#!/usr/bin/env python3
# lane_conflicts.py -- the west-strip / south-corridor allocation as DATA, checked two ways:
#   (1) NET-vs-NET: every pair of segments belonging to different nets, on the SAME layer,
#       tested for rectangle overlap. This is the check that was done by eye in 3o and 3p and
#       that missed a real M5-on-M5 short between VSSA's descent and the ISS south lane.
#   (2) NET-vs-CHIP: every segment tested against the existing chip_top geometry ON ITS OWN
#       LAYER only (a different-layer crossing is benign; a same-layer one is a short).
#
# Same-layer overlap with zero gap is invisible to DRC -- there is no spacing violation when
# two shapes merge -- which is how the I_N/Q_N short in 3i and the I_P/Q_P tap-to-block short
# in 3l both passed a clean DRC. This runs before metal is cut, not after.
#
# Run: klayout -b -r team_src/magic/analysis/lane_conflicts.py
# Exit is advisory (printed); NOT the flow -- an analysis harness. Writes nothing.
import pya

REPO = "/foss/designs/AUS-NZ-integration"
LAYER = {"M1": 34, "M2": 36, "M3": 42, "M4": 46, "M5": 81}

# --- THE ALLOCATION: ALL NETS, not just the west five (Greg 2026-08-23 -- the checker is
# only as good as its coverage, and the quad is the exact net class this bug already bit twice).
# plan doc 3o as revised by 3p/3q. die coords, um. ---
# (net, layer, x0, y0, x1, y1, width)  -- a segment is the swept rectangle of a centreline.
SEG = [
    # ---- VTUNE : route (a), approved ----
    ("VTUNE", "M3", 558.68, 266.70, 465.00, 266.70, 0.4),
    ("VTUNE", "M3", 465.00, 266.70, 465.00, 165.00, 0.4),
    ("VTUNE", "M3", 465.00, 165.00,  10.00, 165.00, 0.4),
    ("VTUNE", "M3",  10.00, 165.00,  10.00, 482.50, 0.4),
    ("VTUNE", "M2",  10.00, 482.50,   0.50, 482.50, 0.4),
    ("VTUNE", "M2",   0.50, 460.34,   0.50, 504.66, 1.0),   # pad stub over the 8 fingers

    # ---- IBIAS ----
    # The escape must CROSS the Q_N (x198.58) and I_N (x199.88) M3 risers -- IBIAS's tap is east
    # of them and its pad is west, so no re-routing avoids it. Found by this checker before any
    # IBIAS metal was cut, as two 0.40 x 0.40 um M3-on-M3 overlaps. M4 is CLEAR at x193-206
    # y422.4-425.4 (measured), so IBIAS hops M3->M4->M3 across the pair: 11 um of M4, 2 vias.
    ("IBIAS", "M3", 271.30, 423.90, 204.00, 423.90, 0.4),
    ("IBIAS", "M4", 204.00, 423.90, 193.00, 423.90, 0.4),
    ("IBIAS", "M3", 193.00, 423.90,  34.00, 423.90, 0.4),
    ("IBIAS", "M3",  34.00, 423.90,  34.00, 282.50, 0.4),
    ("IBIAS", "M2",  34.00, 282.50,   0.50, 282.50, 0.4),
    ("IBIAS", "M2",   0.50, 260.34,   0.50, 304.66, 1.0),

    # ---- VDDA : M4, never M5 (the ring left segment is M5 at x182.5-197.5) ----
    ("VDDA",  "M4", 256.00, 399.00,  46.00, 399.00, 3.0),
    ("VDDA",  "M4",  46.00, 399.00,  46.00, 205.00, 3.0),
    ("VDDA",  "M2",  46.00, 205.00,   0.50, 205.00, 3.0),
    ("VDDA",  "M2",   0.50, 146.36,   0.50, 218.64, 1.0),

    # ---- VSSA : M5 spur off the ring bottom ----
    ("VSSA",  "M5", 175.00, 190.00, 120.00, 190.00, 15.0),
    ("VSSA",  "M5", 120.00, 190.00, 120.00,  82.50, 15.0),
    ("VSSA",  "M5", 120.00,  82.50,  16.00,  82.50, 9.5),
    ("VSSA",  "M2",  16.00,  82.50,   0.50,  82.50, 9.5),
    ("VSSA",  "M2",   0.50,  46.36,   0.50, 118.64, 1.0),

    # ---- ISS : >=10 um M5 bus (option A). M4 wherever it must cross M5. ----
    ("ISS",   "M2", 587.04, 260.33, 490.00, 260.33, 8.0),   # escape west out of the vco
    ("ISS",   "M4", 490.00, 260.33, 455.00, 260.33, 10.0),  # into the gap
    ("ISS",   "M4", 455.00, 260.33, 455.00, 140.00, 10.0),  # gap descent -- M4 THROUGH the ring band
    ("ISS",   "M5", 455.00, 140.00, 130.00, 140.00, 10.0),  # south lane, M5
    ("ISS",   "M4", 130.00, 140.00, 110.00, 140.00, 10.0),  # <-- the ONE deliberate crossing:
                                                            #     hop to M4 across VSSA's M5 descent
    ("ISS",   "M5", 110.00, 140.00,  90.00, 140.00, 10.0),
    ("ISS",   "M5",  90.00, 140.00,  90.00, 382.50, 10.0),  # riser, west of VSSA's descent
    ("ISS",   "M5",  90.00, 382.50,  16.00, 382.50, 10.0),
    ("ISS",   "M2",  16.00, 382.50,   0.50, 382.50, 10.0),
    ("ISS",   "M2",   0.50, 360.34,   0.50, 404.66, 1.0),

    # ---- I/Q matched quad (phase 8 (a), BUILT). die coords = core + 200. ----
    # The lane runs carry the matching serpentine (meander_points amp=6.0), so each is modelled
    # as a BAND of width 2*6.0 + 0.4 = 12.4 um centred on its lane y -- the serpentine's real
    # envelope, not its centreline. The four bands DO overlap in y (490/500/508/516 with +/-6.2)
    # and are kept apart purely by having disjoint x spans, which is what the west-to-east riser
    # ordering buys. Model them honestly so the checker can see that.
    ("Q_N", "M3", 202.18, 251.92, 198.58, 251.92, 0.4),    # escape, M3 at the pin
    ("Q_N", "M3", 198.58, 251.92, 198.58, 490.00, 0.4),    # riser (WEST of I_N's -- 3i)
    ("Q_N", "M3", 198.58, 490.00, 167.50, 490.00, 12.4),   # lane + serpentine envelope
    ("Q_N", "M2", 167.50, 490.00, 167.50, 549.00, 0.4),
    ("Q_N", "M2", 145.34, 549.00, 189.66, 549.00, 1.0),    # N02 finger-row landing bar

    ("I_N", "M3", 202.18, 340.27, 199.88, 340.27, 0.4),
    ("I_N", "M3", 199.88, 340.27, 199.88, 500.00, 0.4),    # riser (EAST of Q_N's)
    ("I_N", "M3", 199.88, 500.00, 267.50, 500.00, 12.4),
    ("I_N", "M2", 267.50, 500.00, 267.50, 549.00, 0.4),
    ("I_N", "M2", 245.34, 549.00, 289.66, 549.00, 1.0),    # N03

    ("I_P", "M3", 435.18, 340.27, 446.18, 340.27, 0.4),    # escape east (novia: lands on the
    ("I_P", "M3", 446.18, 340.27, 446.18, 390.00, 0.4),    #  pin's own M3, no via1/via2 of ours)
    ("I_P", "M3", 446.18, 390.00, 385.00, 390.00, 0.4),    # LOW jog -> west column
    ("I_P", "M3", 385.00, 390.00, 385.00, 508.00, 0.4),
    ("I_P", "M3", 385.00, 508.00, 367.50, 508.00, 12.4),
    ("I_P", "M2", 367.50, 508.00, 367.50, 549.00, 0.4),
    ("I_P", "M2", 345.34, 549.00, 389.66, 549.00, 1.0),    # N04

    ("Q_P", "M3", 435.18, 251.92, 452.18, 251.92, 0.4),
    ("Q_P", "M3", 452.18, 251.92, 452.18, 398.00, 0.4),
    ("Q_P", "M3", 452.18, 398.00, 400.00, 398.00, 0.4),    # HIGH jog -> east column
    ("Q_P", "M3", 400.00, 398.00, 400.00, 516.00, 0.4),
    ("Q_P", "M3", 400.00, 516.00, 467.50, 516.00, 0.4),    # sets the target -> no serpentine
    ("Q_P", "M2", 467.50, 516.00, 467.50, 549.00, 0.4),
    ("Q_P", "M2", 445.34, 549.00, 489.66, 549.00, 1.0),    # N05
]


def rect(x0, y0, x1, y1, w):
    if abs(y1 - y0) > abs(x1 - x0):          # vertical
        return pya.DBox(min(x0, x1) - w / 2, min(y0, y1), max(x0, x1) + w / 2, max(y0, y1))
    return pya.DBox(min(x0, x1), min(y0, y1) - w / 2, max(x0, x1), max(y0, y1) + w / 2)


print("=== (1) NET vs NET, same layer ===")
bad = 0
for i in range(len(SEG)):
    for j in range(i + 1, len(SEG)):
        na, la, *ga = SEG[i]
        nb, lb, *gb = SEG[j]
        if na == nb or la != lb:
            continue
        ra, rb = rect(*ga), rect(*gb)
        ov = ra & rb
        if not ov.empty() and ov.width() > 1e-9 and ov.height() > 1e-9:
            bad += 1
            print("  *** SHORT  %-6s / %-6s on %s   overlap (%.2f,%.2f)-(%.2f,%.2f)  %.2f x %.2f um"
                  % (na, nb, la, ov.left, ov.bottom, ov.right, ov.top, ov.width(), ov.height()))
print("  %d net-vs-net same-layer overlaps" % bad)

print()
print("=== (2) NET vs EXISTING CHIP GEOMETRY, same layer only ===")
ly = pya.Layout(); ly.read(REPO + "/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)
REG = {}
for nm, num in LAYER.items():
    REG[nm] = pya.Region(top.begin_shapes_rec(ly.layer(num, 0)))

# Nets already cut into gds/chip_top.gds. Check (2) would just re-detect their own metal, so it
# is skipped for them -- their real gate is drc_delta + verify_cp, both of which they passed.
BUILT = {"Q_N", "I_N", "I_P", "Q_P"}

hits = 0
for net, lay, *g in SEG:
    if net in BUILT:
        print("  %-6s %s (%7.2f,%7.2f)-(%7.2f,%7.2f) w%.1f : BUILT -- skipped (would self-detect)"
              % (net, lay, g[0], g[1], g[2], g[3], g[4]))
        continue
    r = rect(*g)
    clash = REG[lay].interacting(pya.Region(r.to_itype(ly.dbu)))
    n = clash.count()
    if n:
        hits += 1
        bb = clash.bbox()
        print("  %-6s %s (%7.2f,%7.2f)-(%7.2f,%7.2f) w%.1f : %3d same-layer shapes, bbox (%.2f,%.2f)-(%.2f,%.2f)"
              % (net, lay, g[0], g[1], g[2], g[3], g[4], n,
                 bb.left * ly.dbu, bb.bottom * ly.dbu, bb.right * ly.dbu, bb.top * ly.dbu))
    else:
        print("  %-6s %s (%7.2f,%7.2f)-(%7.2f,%7.2f) w%.1f : clear on %s"
              % (net, lay, g[0], g[1], g[2], g[3], g[4], lay))
print("  %d segments touch existing geometry on their own layer" % hits)
