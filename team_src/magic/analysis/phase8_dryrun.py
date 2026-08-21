#!/usr/bin/env python3
# phase8_dryrun.py -- rehearse route_lib.matched_route on the REAL phase-8 numbers in a
# throwaway cell (gds/test_phase8_dryrun.gds). NOT the flow. Reports routed length per net,
# whether they match to <1um, and the serpentine bbox for collision assessment vs the
# y[180,205] power band (DIEAREA y421.5-446.5) and the GND perimeter ring.
import pya, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase5"))
import route_lib as R

DX, DY = 200.0, 262.5   # chosen placement: core at top, boundary x[175,697] y[241,550]
def tap(cx, cy): return (cx + DX, cy + DY)   # chip coord -> DIEAREA coord

# real taps (chip coords, M1) and the PROPOSED ordering Q_N,I_N,I_P,Q_P -> slots x145/245/345/445
TAP = {"I_P": (235.18,140.27), "I_N": (2.18,140.27), "Q_P": (235.18,51.92), "Q_N": (2.18,51.92)}
# BH north pad rects (translated_user, DIEAREA) centre x, inner edge y=549
PADX = {"x145": 167.5, "x245": 267.5, "x345": 367.5, "x445": 467.5}
ORDER = [("Q_N","x145"), ("I_N","x245"), ("I_P","x345"), ("Q_P","x445")]  # proposed

nets = []
for name, slot in ORDER:
    tx, ty = tap(*TAP[name])
    nets.append((name, tx, ty, PADX[slot], 549.0))

ly = pya.Layout(); ly.dbu = 0.005
cell = ly.create_cell("test_phase8_dryrun")
# lanes between the taps (y<=403) and the pads (y549): 4 lanes at 470..500
lengths, target = R.matched_route(cell, ly, 3, nets, ych_base=470.0, lane_pitch=10.0, w=0.4)
print("matched quad @ real coords (order %s), target=%.3f um" % ([n for n,_ in ORDER], target))
ok = True
for name, _ in ORDER:
    err = lengths[name] - target
    if abs(err) >= 1.0: ok = False
    print("  %-4s routed=%.3f  err=%+.4f  %s" % (name, lengths[name], err, "OK(<1um)" if abs(err)<1.0 else "FAIL"))

# serpentine / route bbox for collision assessment
bb = cell.dbbox()
print("route bbox (DIEAREA um): (%.1f,%.1f)-(%.1f,%.1f)" % (bb.left,bb.bottom,bb.right,bb.top))
BAND = (0.0, 421.5, 1110.0, 446.5)     # y[180,205] band in DIEAREA frame (core-y+259)
TOPBLK = (175.0, 466.5, 697.0, 534.5)  # ibias/CP/PFD top blocks (core-y205-273 + dy)
def overlaps(b, r): return not (b.right<r[0] or b.left>r[2] or b.top<r[1] or b.bottom>r[3])
print("  vs power band  y[421.5,446.5]: %s" % ("OVERLAP" if overlaps(bb,BAND) else "clear"))
print("  vs top blocks  y[466.5,534.5]: %s" % ("OVERLAP" if overlaps(bb,TOPBLK) else "clear"))

out = "/foss/designs/AUS-NZ-integration/gds/test_phase8_dryrun.gds"
ly.write(out); print("wrote", out, "| match:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
