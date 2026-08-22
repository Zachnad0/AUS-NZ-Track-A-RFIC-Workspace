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
 "I_P": dict(esc=+11.0, escl=1, jog=(385.0, d(0,190)[1]), lane=d(0,308)[1]),  # LOW jog y390, WEST col 385, lane 508
 "Q_P": dict(esc=+17.0, escl=1, jog=(400.0, d(0,198)[1]), lane=d(0,316)[1]),  # HIGH jog y398, EAST col 400, lane 516
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
    if p["escl"] == 3:
        R.via_stack(top, ly, 1, 3, tx, ty)              # M1 pin -> M3 AT the tap (no M1 near DIV2 frame)
    else:
        R.hwire(top, ly, 1, tx, esc_x, ty, w=0.4)       # M1 escape
        R.via_stack(top, ly, 1, 3, esc_x, ty)
    R.route_path(top, ly, 3, pts, w=0.4)                # M3 path (+serpentine)
    R.via_stack(top, ly, 2, 3, px, p["lane"])
    R.vwire(top, ly, 2, p["lane"], PADY, px, w=0.4)     # M2 drop to pad
    top.shapes(ly.layer(36, 10)).insert(pya.DText(net, pya.DTrans(pya.DVector(px, PADY))))  # M2 port label
    final[net] = (0.0 if p["escl"] == 3 else abs(p["esc"])) + R.path_length(pts) + abs(PADY - p["lane"])

# routes-only cell (top-cell direct shapes = the 4 routes, NO chip_top instance): standalone
# extraction of THIS gives the net count directly -- 4 distinct nets iff no two routes merge.
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
