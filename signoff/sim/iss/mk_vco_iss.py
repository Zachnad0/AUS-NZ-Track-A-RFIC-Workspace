"""Build ISS-node decks from signoff/sim/vco/pex200.spice (landed vco_v1 extraction).

usage: mk_vco_iss.py OUTDIR NAME MODE AMPS VTUNE
  MODE mirror : the bench's 1:1 NMOS tail mirror, reference I0 = AMPS (1m = "1.0x")
  MODE ideal  : the tail mirror (XM1) replaced by an ideal current sink of AMPS from the
                ISS node to GND -- no compliance limit, so v(ISS) is what the die needs
Measures over 150-200 ns: avg/min/max v(ISS) (the bench's `vss` net = the vco_v1 ISS
port) and avg tail current; dumps v(net1) v(net2) v(vss) for swing and f0.
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
out, name, mode, amps, vtune = sys.argv[1:6]
s = open(os.path.join(REPO, "signoff/sim/vco/pex200.spice"), encoding="utf-8").read()

s = s.replace("V2 tune GND 2.0", f"V2 tune GND {vtune}", 1)
if mode == "mirror":
    s = s.replace("I0 GND vsg 1m", f"I0 GND vsg {amps}", 1)
elif mode == "ideal":
    s, n = re.subn(r"^XM1 net3 vsg GND GND .*\n\+ .*\n", f"I_SINK net3 GND {amps}\n", s, count=1, flags=re.M)
    assert n == 1, "XM1 not found"
else:
    raise SystemExit("MODE must be mirror or ideal")
s = s.replace(".option numparam jobs=4", ".option numparam jobs=2", 1)
s = s.replace("wrdata r_final.dat v(net1) v(net2) v(out_p) v(out_n) i(v1) i(viss_meas)",
              "meas tran viss_avg AVG v(vss) from=150n to=200n\n"
              "meas tran viss_min MIN v(vss) from=150n to=200n\n"
              "meas tran viss_max MAX v(vss) from=150n to=200n\n"
              "meas tran iss_avg AVG i(viss_meas) from=150n to=200n\n"
              f"wrdata {out}/{name}.dat v(net1) v(net2) v(vss)", 1)
for must in (f"V2 tune GND {vtune}", "jobs=2", "viss_min", "set num_threads=2"):
    assert must in s, must
open(os.path.join(out, f"{name}.spice"), "w", newline="\n").write(s)
