"""Build the VCO VDDA-current decks from signoff/sim/vco/pex200.spice (landed extraction).

vco_v1 gets its own 3.3 V source (V1v) so the bench output buffer, which stays on V1, is not
counted. ISS reference 1 mA (1.0x) and 2 mA (2.0x), VTUNE 2.0 V, 200 ns, 2 threads.
Writes vco_vdda_1x.spice / vco_vdda_2x.spice into the directory given as argv[1].
"""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
out = sys.argv[1]
src = open(os.path.join(REPO, "signoff/sim/vco/pex200.spice"), encoding="utf-8").read()
for mult, iref in (("1x", "1m"), ("2x", "2m")):
    s = src
    s = s.replace("x1 vdd net1 net2 GND tune vss vco_v1",
                  "V1v vddv GND 3.3\n.save i(v1v)\nx1 vddv net1 net2 GND tune vss vco_v1", 1)
    s = s.replace("I0 GND vsg 1m", f"I0 GND vsg {iref}", 1)
    s = s.replace(".option numparam jobs=4", ".option numparam jobs=2", 1)
    s = s.replace("wrdata r_final.dat v(net1) v(net2) v(out_p) v(out_n) i(v1) i(viss_meas)",
                  "meas tran ivco_avg AVG i(v1v) from=150n to=200n\n"
                  "meas tran iss_avg AVG i(viss_meas) from=150n to=200n\n"
                  "meas tran ibench_avg AVG i(v1) from=150n to=200n\n"
                  f"wrdata {out}/vco_{mult}.dat v(net1) v(net2) i(v1v) i(viss_meas)", 1)
    for must in ("V1v vddv", f"I0 GND vsg {iref}", "jobs=2", "ivco_avg", "set num_threads=2"):
        assert must in s, must
    open(os.path.join(out, f"vco_vdda_{mult}.spice"), "w", newline="\n").write(s)
