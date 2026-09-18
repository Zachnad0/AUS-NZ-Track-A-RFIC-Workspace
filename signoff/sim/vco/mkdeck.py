"""Build run decks from the xschem-netlisted vco_tb.spice.

Usage: mkdeck.py <out.spice> <vtune> <tstop> <datfile> [pexfile]
Keeps the bench as netlisted; replaces only the .control block (the committed one ends in
`plot`, which needs a display) and the VTUNE source. With <pexfile> the schematic vco_v1
subckt is swapped for the extracted one.
"""
import io
import re
import sys

SRC = "/foss/designs/_lvs_check/vco/sim/vco_tb.spice"
out, vtune, tstop, dat = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
pex = sys.argv[5] if len(sys.argv) > 5 else None

s = io.open(SRC, encoding="utf-8").read()

# 1. VTUNE
s = re.sub(r"^V2 tune GND [0-9.]+", "V2 tune GND %s" % vtune, s, count=1, flags=re.M)

# 2. control block -> batch-safe measurement
CTRL = """.control
save all
set num_threads=2
op
tran 5p %s
wrdata %s v(net1) v(net2) v(out_p) v(out_n) i(v1) i(viss_meas)
.endc
""" % (tstop, dat)
s = re.sub(r"^\.control\n.*?^\.endc\n", CTRL, s, count=1, flags=re.M | re.S)

# 3. optional: swap the schematic vco_v1 for the extracted netlist
if pex:
    body = io.open(pex, encoding="utf-8").read()
    # the PEX netlist is a flat deck of the cell's contents with no .subckt wrapper;
    # wrap it with the schematic's port order so x1's connection by position still holds.
    lines = [l for l in body.split("\n")
             if l.strip() and not l.strip().startswith("*")
             and not l.strip().lower().startswith(".option")
             and not l.strip().lower().startswith(".include")
             and not l.strip().lower().startswith(".end")]
    TIES = ("V_vsubs vco_inductor_v2_0/VSUBS GND 0\n"
            "V_indgnd vco_inductor_v2_0/GND GND 0\n"
            "R_dangle1 vco_inductor_v2_0/m5_n22400_10400# GND 1e12\n"
            "R_dangle2 vco_inductor_v2_0/m5_n1200_10400# GND 1e12\n")
    wrapped = (".subckt vco_v1 VDD OUT_p OUT_n GND TUNE ISS\n" + TIES +
               "* --- extracted (R+C) body, magic ext2spice, from gds/vco_v1.gds via the .mag\n"
               "* --- hierarchy so the coil comes from the committed vco_inductor_v2.ext model\n"
               + "\n".join(lines) + "\n.ends\n")
    s = re.sub(r"^\.subckt vco_v1 .*?^\.ends\n", wrapped, s, count=1, flags=re.M | re.S)

io.open(out, "w", encoding="utf-8", newline="\n").write(s)
print("wrote %s  (VTUNE=%s, tstop=%s, pex=%s)" % (out, vtune, tstop, bool(pex)))
