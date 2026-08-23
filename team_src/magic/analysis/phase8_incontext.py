#!/usr/bin/env python3
# phase8_incontext.py -- IN-CONTEXT rehearsal: instance chip_top (all masters present)
# at (dx,dy) in a throwaway cell, route the matched quad with the map-derived escapes/
# jogs, match the four to the longest with serpentine in the clear channel. NOT the flow.
#
# Left risers (Q_N/I_N, DIV2 outputs) via M1->M3 AT the tap pin and escape on M3, past
# DIV2's M1 frame (escl=3) -- an M1 escape there hits DIV2's M1 (M1.2a). They rise WEST->EAST
# (Q_N west of I_N) so neither escape sweeps across the other's riser (that overlap is a
# DRC-clean silent short, caught only by the routes-only extraction). Right risers (I_P/Q_P)
# escape east and jog into the x381-404 ibias-CP gap: I_P low-jog+west col, Q_P high-jog+east
# col so no lane crosses a riser (M3.2a). See docs/phase8-padframe-plan.md §3i.
#
# Writes gds/reh_phase8.gds (chip_top + 4 routes), gds/reh_base.gds (blocks only), and
# gds/reh_routes.gds (the 4 routes alone, for a clean routes-only extraction). Gate with
# reh_drc.tcl (==84), klayout_signoff.py (168 waived), reh_extract.tcl (4 distinct nets).
# dy via env PHASE8_DY (default 200); PHASE8_NOSER=1 for base lengths (no serpentine).
import pya, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase5"))
import route_lib as R

DX = 200.0
DY = float(os.environ.get("PHASE8_DY", "200"))
def d(cx, cy): return (cx + DX, cy + DY)
CHIP = "/foss/designs/AUS-NZ-integration/gds/chip_top.gds"

TAP = {"Q_N": d(2.18,51.92), "I_N": d(2.18,140.27), "I_P": d(235.18,140.27), "Q_P": d(235.18,51.92)}
PAD = {"Q_N":167.5, "I_N":267.5, "I_P":367.5, "Q_P":467.5}
PADY = 549.0
# per-net plan: escape dx (M1), optional jog (jog_x, jog_y die), lane_y die
PLAN = {   # escl = escape layer (3 = via at the M1 pin then escape ON M3, past DIV2's M1 frame
           # with no M1 painted near it; 1 = M1 escape then via up). Left risers escape on M3
           # because west of DIV2 (chip x<0) every layer but the M5 ring is empty and M3<->M5
           # has no spacing rule -- the old "2.5um slot" was an artifact of escaping on M1.
 "Q_N": dict(esc=-3.6,  escl=3, jog=None,             lane=d(0,290)[1]),   # M3 esc west, riser die 198.6 (WEST)
 "I_N": dict(esc=-2.3,  escl=3, jog=None,             lane=d(0,300)[1]),   # M3 esc west, riser die 199.9 (EAST)
 # Q_N riser MUST be west of I_N's: I_N's escape (higher y) sweeps west to its riser and would
 # cross-and-SHORT Q_N's riser if Q_N sat east of it (DRC-clean overlap, caught only by extraction).
 "I_P": dict(esc=+11.0, escl=3, novia=True, jog=(385.0, d(0,190)[1]), lane=d(0,308)[1]),  # LOW jog y390, WEST col 385, lane 508 -- pin is a full via stack (land on its M3)
 "Q_P": dict(esc=+17.0, escl=3, jog=(400.0, d(0,198)[1]), lane=d(0,316)[1]),  # HIGH jog y398, EAST col 400, lane 516
 # I_P/Q_P escl=3 (M3 at the pin, no M1 escape hwire): the M1 hwire ran east across the
 # ib_conv_v1_0/_3 a_8764_6964# bias node and SHORTED it to the output -- a tap-to-block short
 # invisible to DRC and to the routes-only extract, caught only by the in-context extraction (§3l).
}

def m3_pts(net, ser_extra):
    tx, ty = TAP[net]; px = PAD[net]; p = PLAN[net]
    esc_x = tx + p["esc"]
    pts = [(tx, ty), (esc_x, ty)] if p["escl"] == 3 else [(esc_x, ty)]
    if p["jog"] is None:
        pts += [(esc_x, p["lane"])]
    else:
        jx, jy = p["jog"]
        pts += [(esc_x, jy), (jx, jy), (jx, p["lane"])]
    lane_x0 = pts[-1][0]
    if ser_extra > 1e-6:
        pts += R.meander_points(lane_x0, px, p["lane"], ser_extra, 0.4, 3, amp=6.0)[1:]
    else:
        pts += [(px, p["lane"])]
    return pts, esc_x

def net_len(net, ser_extra):
    p = PLAN[net]
    pts, esc_x = m3_pts(net, ser_extra)
    m1 = 0.0 if p["escl"] == 3 else abs(p["esc"])   # escl 3: escape is on M3, already in path_length
    return m1 + R.path_length(pts) + abs(PADY - p["lane"])

NOSER = os.environ.get("PHASE8_NOSER", "") != ""   # base routes only (no matching serpentine)
base = {n: net_len(n, 0.0) for n in PAD}
target = max(base.values()) if not NOSER else None
print("dy=%.1f  base lengths: %s  -> target %.3f (pad %s to it)"
      % (DY, {n: round(base[n],1) for n in PAD}, target, max(base, key=base.get)))

ly = pya.Layout(); ly.read(CHIP)
src = ly.cell("chip_top"); top = ly.create_cell("reh_phase8")
top.insert(pya.DCellInstArray(src.cell_index(), pya.DCplxTrans(1.0,0.0,False,DX,DY)))
final = {}
for net in PAD:
    tx, ty = TAP[net]; px = PAD[net]; p = PLAN[net]
    ser = 0.0 if NOSER else (target - base[net])
    pts, esc_x = m3_pts(net, ser)
    if p.get("novia"):
        pass  # tap pin already reaches M3 (full via stack): land the M3 route on it, add NO
              # via1/via2 of our own -- a duplicate via stack trips V1.2a/V2.2a against the pin's.
    elif p["escl"] == 3:
        R.via_stack(top, ly, 1, 3, tx, ty)              # M1-only pin -> M3 AT the tap
    else:
        R.hwire(top, ly, 1, tx, esc_x, ty, w=0.4)       # M1 escape
        R.via_stack(top, ly, 1, 3, esc_x, ty)
    R.route_path(top, ly, 3, pts, w=0.4)                # M3 path (+serpentine)
    R.via_stack(top, ly, 2, 3, px, p["lane"])
    R.vwire(top, ly, 2, p["lane"], PADY, px, w=0.4)     # M2 drop to pad
    top.shapes(ly.layer(36, 10)).insert(pya.DText(net, pya.DTrans(pya.DVector(px, PADY))))  # M2 port label
    final[net] = (0.0 if p["escl"] == 3 else abs(p["esc"])) + R.path_length(pts) + abs(PADY - p["lane"])

# --- single-net hauls (Item 2/3): explicit LAYERED polylines in DIE coords. Each waypoint is
# (metal, x, y); a wire is drawn between consecutive same-layer points, a via_stack where the
# layer changes at a fixed (x,y). Selected via env PHASE8_HAULS=comma,list (default none, so the
# quad-only gate is unchanged). Gated with reh_ctx_extract.tcl like the quad. ---
HAUL = {
 # VTUNE: vco.TUNE tap (M1) escapes WEST on M1 into the fully-clear DIV2<->vco gap, vias up to
 # M3 in the clear column (chip 348), rises to the top band (crossing only vco M5 leads --
 # perpendicular, benign; the 15k tune R low-passes it), then M2 WEST across the top band (clear
 # of M2/M3 full width) to the west empty die, down to the pad. No parallel run past aggressors.
 # VTUNE: BOXED (Item 2d, §3m). The TUNE tap IS accessible -- via UP (M1->M3) at the gate pad
 # (which sits INSIDE the varactor comp ring; a lateral M1 escape shorts the ring -> VSSA, caught
 # by the in-context extract) then M3 west over the ring into the gap. But the RISE to the west
 # pad is boxed: the only M2/M3-clear rise columns are x181-204 (unreachable at low y -- DIV2
 # blocks x<235.4) and x288-397 (under the inductor spiral x290-472); the sole column clear of
 # BOTH is x288-290 (~2um, 1um off the spiral) => a ~96um M3 run beside the live inductor, which
 # Item 2b forbids for the tune node. This entry documents the clean tap access only.
 "VTUNE_tap": dict(label_xy=(548.68, 266.70), pts=[
     (1, 558.68, 266.70), (3, 558.68, 266.70),         # via M1->M3 at the TUNE gate pad
     (3, 548.68, 266.70)],                             # M3 west over the comp ring into the gap
 ),
 # ISS attempt: DC tail node (coupling-tolerant, so rising under the spiral is OK). Tap is a
 # vco-INTERIOR M2 pin (chip x395.84, center of the spiral footprint). Best-effort: M2 west out
 # of the vco into the gap, via up, M3 rise (under spiral, fine for ISS), M2 west band to pad.
 "ISS": dict(label_xy=(0.5, 382.5), pts=[
     (2, 595.84, 260.33), (2, 548.0, 260.33),          # M2 west out of the vco into the gap
     (3, 548.0, 260.33), (3, 548.0, 380.0),            # via up, M3 riser (under spiral, ok for ISS)
     (2, 548.0, 380.0), (2, 0.5, 380.0), (2, 0.5, 382.5)],  # via to M2, west band, to pad
 ),
}

def route_haul(name, spec):
    pts = spec["pts"]; L = 0.0
    for (m0,x0,y0),(m1,x1,y1) in zip(pts, pts[1:]):
        if m0 == m1:                                   # same layer -> wire
            if abs(x0-x1) > 1e-9 or abs(y0-y1) > 1e-9:
                R.route_path(top, ly, m0, [(x0,y0),(x1,y1)], w=0.4); L += abs(x1-x0)+abs(y1-y0)
        else:                                          # layer change at fixed point -> via stack
            R.via_stack(top, ly, m0, m1, x0, y0)
    lx, lyy = spec["label_xy"]; mlast = pts[-1][0]
    top.shapes(ly.layer(METAL_DT.get(mlast,36), 10)).insert(pya.DText(name, pya.DTrans(pya.DVector(lx, lyy))))
    return L

METAL_DT = {1:34, 2:36, 3:42, 4:46, 5:81}
HAULS = [h for h in os.environ.get("PHASE8_HAULS","").split(",") if h in HAUL]
for h in HAULS:
    Lh = route_haul(h, HAUL[h]); print("HAUL %s routed len=%.1f um" % (h, Lh))

# routes-only cell (top-cell direct shapes = the routes, NO chip_top instance): standalone
# extraction of THIS gives the net count directly -- distinct nets iff no two routes merge.
rl = pya.Layout(); rl.dbu = ly.dbu
rc = rl.create_cell("reh_routes")
for li in ly.layer_indices():
    info = ly.get_info(li); tl = rl.layer(info)
    for sh in top.shapes(li).each():
        rc.shapes(tl).insert(sh)
rl.write("/foss/designs/AUS-NZ-integration/gds/reh_routes.gds")
if NOSER:
    print("BASE routes (no serpentine) lengths:", {n: round(final[n],3) for n in PAD})
else:
    print("matched lengths:", {n: round(final[n],3) for n in PAD})
    err = max(abs(final[n]-target) for n in PAD)
    print("max match error: %.4f um  %s" % (err, "OK(<1um)" if err < 1.0 else "FAIL"))

lb = pya.Layout(); lb.read(CHIP)
bsrc = lb.cell("chip_top"); btop = lb.create_cell("reh_base")
btop.insert(pya.DCellInstArray(bsrc.cell_index(), pya.DCplxTrans(1.0,0.0,False,DX,DY)))
ly.write("/foss/designs/AUS-NZ-integration/gds/reh_phase8.gds")
lb.write("/foss/designs/AUS-NZ-integration/gds/reh_base.gds")
print("wrote reh_phase8.gds + reh_base.gds")
