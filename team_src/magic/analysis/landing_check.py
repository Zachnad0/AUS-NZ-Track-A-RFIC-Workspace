#!/usr/bin/env python3
# landing_check.py -- assert that every haul actually REACHES its target, with a measured margin.
#
# WHY THIS IS A SEPARATE TOOL FROM lane_conflicts.py
# ---------------------------------------------------
# lane_conflicts detects nets that DO touch and should not. This detects nets that do NOT touch
# and should. They are opposite defects and no single check finds both.
#
# Five landing defects have now been found, every one DRC-clean and every one caught only after
# the fact by an LVS port count:
#   1. Q_N/I_N/I_P/Q_P drops aimed at the slot CENTRE, which is an inter-finger gap on all
#      twelve multi-finger pins -- a bare drop touches nothing (plan doc 3s);
#   2. VSSA_uq0  -- the pad-plate via placed 2.0 um OUTSIDE the plate (sign error);
#   3. VDDA_uq0  -- the via4 placed 2.5 um short of the M5 bus, which starts at die x258.5
#      and not the x256 the plan said;
#   4. REF_IN_uq0 -- the Y landing box starting at die y549.0 while its via2 M2 pad ended at
#      y548.75: a 0.25 um gap;
#   5. the w=3 M2 drops overshooting the DIEAREA by 1.0 um at the other end.
# DRC cannot see any of these: not touching is not a rule violation.
#
# HOW IT WORKS
# ------------
# For each net, flood-fill the connected metal from a seed on the net's BLOCK-SIDE source, then
# assert the flood covers every target shape -- the DEF pin fingers, taken from the committed
# DEF, not from a plan. Seeding at the block side means the flood has to traverse the whole haul
# to reach the pad, so a break anywhere along it shows up as an uncovered target.
#
# Run: klayout -b -r team_src/magic/analysis/landing_check.py
# Exit status is printed, not returned (klayout -b swallows it). Writes nothing.
import pya
import os

REPO = "/foss/designs/AUS-NZ-integration"
DEF_ROOT = os.environ.get("PADFRAME_ROOT", REPO + "/padframe/A01/project_defs_12pin")
MIN_MARGIN = 0.28          # um -- one minimum feature; anything less is not a connection

MET = {"M1": 34, "M2": 36, "M3": 42, "M4": 46, "M5": 81}
VIA = {"v1": 35, "v2": 38, "v3": 40, "v4": 41}
STACK = ["M1", "v1", "M2", "v2", "M3", "v3", "M4", "v4", "M5"]

# net -> (seed x, seed y, seed layer, what the seed is)
# Seeds are on the BLOCK side so the flood must traverse the haul to reach the pad.
#
# !! THE SEED IS FRAGILE. RE-CHECK IT AFTER ANY CHANGE TO A NET'S DEVICE ORDER. !!
# This check floods METAL. It cannot cross a device. So a seed is only valid while it sits on
# the same metal island as the pad fingers, and inserting or moving a series device on a net
# silently invalidates it -- the tool then reports 0/8 fingers, which reads as a landing defect
# when it is actually a stale seed. It is a LOUD failure, not a silent one, but it costs a gate
# cycle to diagnose every time.
#
# IBIAS's seed has moved TWICE in three commits and both times the tool was right and the seed
# was wrong:
#   7391653  ballast inserted between pad and block tap -> block-side seed could no longer
#            reach the pad. Moved to the pad side of the ballast, at the haul (40.00,423.90).
#   5eda5b6  clamp relocated into the W20 pin band, so the ballast became the FIRST element on
#            the net -- (40.00,423.90) was then on the CORE side of it. Moved again, to the
#            resistor's pad-side terminal.
# The rule that would have caught both without a gate cycle: after changing a net, ask which
# metal island the pad fingers are on, and seed at the far end of THAT island.
SEED = {
    "Q_N":       (202.18, 251.92, "M1", "DIV2 Q_N output tap"),
    "I_N":       (202.18, 340.27, "M1", "DIV2 I_N output tap"),
    "I_P":       (435.18, 340.27, "M1", "DIV2 I_P output tap"),
    "Q_P":       (435.18, 251.92, "M1", "DIV2 Q_P output tap"),
    "VTUNE":     (558.68, 266.70, "M1", "vco TUNE gate pad"),
    "ISS":       (595.84, 260.33, "M2", "vco ISS tail strap"),
    # RUNG 3: IBIAS now has a SERIES ballast resistor between the pad and the block tap, so
    # the net is two metal islands and a metal flood from the block tap cannot reach the pad
    # (it read 0/8 fingers). The question this tool exists to answer -- "does the haul REACH
    # its pin" -- is about the PAD-side island, so seed there: the M3 at the pad side of the
    # series cut (route_chip.py IB_CUT_W, IB_HAUL_Y). That the block-side island reaches the
    # clamp node is a connectivity question, and LVS answers it -- verified: the shorted and
    # the disconnected variants both FAIL gate 4.
    #
    # UPDATED when the clamp moved into the W20 pin band: the ballast is now the FIRST element
    # on the net, so the pad-side island is just the plate plus the short M2 run to the
    # resistor. Seed at the resistor's bottom terminal -- the far end of that island -- so the
    # flood still has to traverse the whole run and the plate to reach all eight fingers.
    "IBIAS":     (28.30, 268.25, "M2", "IBIAS pad side of the series ballast"),
    "VDDA":      (400.00, 399.00, "M5", "VDDA M5 bus"),
    "VDDD":      (380.00, 388.00, "M5", "VDDD M5 bus"),
    "VSSA":      (400.00, 190.00, "M5", "GND ring, bottom segment"),
    "REF_IN":    (410.28, 457.60, "M3", "PFD REF pin"),
    "CP_OUT":    (472.25, 415.41, "M4", "CP_v1 CP_OUT M4 stub"),
}
# Nets that share another net's flood (same electrical node) -- checked against that flood.
ALIAS = {"VSSD": "VSSA", "REF_IN_PU": "VSSA", "REF_IN_PD": "VDDD"}
# NO "unrouted, excused" set. The pin list comes from the DEF -- the CONTRACT -- and every pin
# in it must have a seed and must be covered. An earlier version carried CP_OUT in an UNROUTED
# escape hatch, which meant the tool kept reporting PASS after CP_OUT had actually been built:
# it counted the work, not the contract. A pin with no seed is a FAIL, not a note.


def load_targets():
    """pin -> list of Metal2 target rects (um), straight from the committed DEF."""
    import yaml
    with open(os.path.join(DEF_ROOT, "BH", "A01_BH_interface.yaml")) as f:
        d = yaml.safe_load(f)
    out = {}
    for p in d["pins"]:
        rs = [pya.DBox(q["translated_user"][0] / 200.0, q["translated_user"][1] / 200.0,
                       q["translated_user"][2] / 200.0, q["translated_user"][3] / 200.0)
              for q in p["rectangles"]]
        out.setdefault(p["project_pin"], []).extend(rs)
    return out


def main():
    ly = pya.Layout(); ly.read(REPO + "/gds/chip_top.gds")
    top = ly.cell("chip_top"); top.flatten(-1, True)
    R = {}
    for nm, l in list(MET.items()) + list(VIA.items()):
        R[nm] = pya.Region(top.begin_shapes_rec(ly.layer(l, 0)))

    targets = load_targets()
    print("=== landing_check: does every haul REACH its pin? ===")
    print("targets from %s" % DEF_ROOT)
    print("minimum acceptable overlap on a finger: %.2f um in both axes\n" % MIN_MARGIN)

    floods = {}
    fails = 0
    # Iterate the DEF's pin list, not the seed table: count from the contract.
    for net in sorted(targets):
        if net not in SEED and net not in ALIAS:
            print("%-10s *** NO SEED DEFINED *** %d target finger(s) unverifiable"
                  % (net, len(targets[net]))); fails += 1; continue
        src = ALIAS.get(net, net)
        if src not in floods:
            sx, sy, sl, what = SEED[src]
            seed = pya.Region(pya.DBox(sx - 0.05, sy - 0.05, sx + 0.05, sy + 0.05).to_itype(ly.dbu))
            cur = {k: pya.Region() for k in R}
            cur[sl] = R[sl].interacting(seed)
            if cur[sl].count() == 0:
                print("%-10s *** SEED MISSES *** no %s under the %s at (%.2f,%.2f)"
                      % (src, sl, what, sx, sy)); fails += 1; floods[src] = cur; continue
            for _ in range(40):
                grew = False
                for i, nm in enumerate(STACK):
                    acc = pya.Region()
                    for nb in ([STACK[i - 1]] if i else []) + ([STACK[i + 1]] if i < len(STACK) - 1 else []):
                        if cur[nb].count():
                            acc += R[nm].interacting(cur[nb])
                    before = cur[nm].count()
                    cur[nm] = (cur[nm] + acc); cur[nm].merge()
                    if cur[nm].count() != before:
                        grew = True
                if not grew:
                    break
            floods[src] = cur
        m2 = floods[src]["M2"]
        tg = targets.get(net, [])
        if not tg:
            print("%-10s no target rects in the DEF" % net); continue
        covered, worst = 0, None
        for t in tg:
            ov = m2 & pya.Region(t.to_itype(ly.dbu))
            if ov.is_empty():
                worst = (0.0, 0.0); continue
            b = ov.bbox()
            w, h = b.width() * ly.dbu, b.height() * ly.dbu
            if min(w, h) >= MIN_MARGIN:
                covered += 1
            if worst is None or min(w, h) < min(worst):
                worst = (w, h)
        ok = covered == len(tg)
        if not ok:
            fails += 1
        print("%-10s %s  %d/%d fingers covered   worst overlap %.3f x %.3f um   [flood seeded at %s]"
              % (net, "OK  " if ok else "FAIL", covered, len(tg), worst[0], worst[1],
                 ALIAS.get(net, net)))

    print("\n%d net(s) failed to reach every target finger." % fails)
    print("RESULT: %s" % ("PASS" if fails == 0 else "FAIL"))


main()
