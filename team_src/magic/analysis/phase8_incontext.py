#!/usr/bin/env python3
# phase8_incontext.py -- IN-CONTEXT rehearsal: instance chip_top (all masters present)
# at (dx,dy) in a throwaway cell, route the matched quad with the map-derived escapes/
# jogs (right risers jogged into the x381-404 ibias-CP gap above the vco), match the four
# to the longest with serpentine in the clear channel. Writes gds/reh_phase8.gds (routes)
# and gds/reh_base.gds (blocks only) for DRC + an extraction diff. NOT the flow.
# dy via env PHASE8_DY (default 200).
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
PLAN = {   # escapes/jogs validated DRC-clean (base, no serpentine): riser cols per the map
 "Q_N": dict(esc=-2.3,  jog=None,          lane=d(0,290)[1]),          # riser die 199.9 (E of ring x197.5, W of DIV2 x200)
 "I_N": dict(esc=-3.6,  jog=None,          lane=d(0,300)[1]),          # riser die 198.6
 "I_P": dict(esc=+11.0, jog=(392.0, d(0,198)[1]), lane=d(0,308)[1]),   # east->gap x392 above vco, lane die 508
 "Q_P": dict(esc=+17.0, jog=(388.0, d(0,193)[1]), lane=d(0,316)[1]),   # east->gap x388 above vco, lane die 516
}

def m3_pts(net, ser_extra):
    tx, ty = TAP[net]; px = PAD[net]; p = PLAN[net]
    esc_x = tx + p["esc"]
    pts = [(esc_x, ty)]
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
    tx, ty = TAP[net]; px = PAD[net]; p = PLAN[net]
    pts, esc_x = m3_pts(net, ser_extra)
    return abs(p["esc"]) + R.path_length(pts) + abs(PADY - p["lane"])   # M1 esc + M3 + M2 drop

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
    R.hwire(top, ly, 1, tx, esc_x, ty, w=0.4)           # M1 escape
    R.via_stack(top, ly, 1, 3, esc_x, ty)
    R.route_path(top, ly, 3, pts, w=0.4)                # M3 path (+serpentine)
    R.via_stack(top, ly, 2, 3, px, p["lane"])
    R.vwire(top, ly, 2, p["lane"], PADY, px, w=0.4)     # M2 drop to pad
    final[net] = abs(p["esc"]) + R.path_length(pts) + abs(PADY - p["lane"])
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
