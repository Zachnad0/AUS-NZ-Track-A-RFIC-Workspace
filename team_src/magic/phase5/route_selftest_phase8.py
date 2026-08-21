#!/usr/bin/env python3
# route_selftest_phase8.py -- build the phase-8 haul primitives (matched quad router,
# def-pin lander, length accounting) in ISOLATION and write test_phase8.gds for DRC.
# Also asserts the length accounting (each matched net == target). NOT wired into the
# tapeout flow. Gate: magic DRC 0 + KLayout signoff clean on test_phase8.gds.
import pya, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_lib as R

ly = pya.Layout()
ly.dbu = 0.005
cell = ly.create_cell("test_phase8")

# --- 1. length-matched QUAD router (M3 signals), 4 nets with different base lengths ---
# endpoints (name, x0,y0 tap, x1,y1 pad); each net gets its own channel lane => no short.
nets = [
    ("A", 0.0,   0.0, 200.0, 120.0),
    ("B", 5.0,   0.0, 180.0, 120.0),
    ("C", 10.0,  0.0, 160.0, 120.0),
    ("D", 0.0,   0.0, 220.0, 120.0),   # longest base -> sets the target
]
lengths, target = R.matched_route(cell, ly, 3, nets, ych_base=40.0, lane_pitch=8.0, w=0.4)
print("matched quad: target=%.3f um" % target)
ok = True
for name in ("A", "B", "C", "D"):
    err = lengths[name] - target
    flag = "OK" if abs(err) < 1e-3 else "MISMATCH"
    if abs(err) >= 1e-3:
        ok = False
    print("  net %s routed=%.3f  (target %.3f, err %+.4f)  %s" % (name, lengths[name], target, err, flag))

# --- 2. def-pin lander: land an M3 haul onto an M2 def pin rectangle (die-edge, 1um deep) ---
# emulate a BH north asig pad rect (translated_user), 44um wide x 1um deep at y=549.
pin = (300.0, 549.0, 344.0, 550.0)
R.land_on_pin(cell, ly, 3, approach=(322.0, 500.0), pin_rect=pin, label="TESTPIN", w=0.4)
# a narrow in_c-style pin (0.2um wide) landed from M2 directly
pin2 = (400.0, 549.0, 400.2, 550.0)
R.land_on_pin(cell, ly, 2, approach=(400.1, 500.0), pin_rect=pin2, label="NARROW", w=0.3)

# --- 3. length accounting standalone: a known path ---
probe = [(0.0, 200.0), (0.0, 210.0), (30.0, 210.0)]   # 10 up + 30 across = 40
plen = R.path_length(probe)
print("path_length probe = %.3f (expect 40.000)  %s" % (plen, "OK" if abs(plen - 40.0) < 1e-6 else "MISMATCH"))
if abs(plen - 40.0) >= 1e-6:
    ok = False

out = "/foss/designs/AUS-NZ-integration/gds/test_phase8.gds"
ly.write(out)
print("wrote", out, "| length-accounting self-check:", "PASS" if ok else "FAIL")
if not ok:
    sys.exit(1)
