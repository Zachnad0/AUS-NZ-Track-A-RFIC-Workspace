"""Build the startup decks: vco_tb's stimulus and options around a chosen vco_v1 netlist.

Usage: mkdeck2.py <out.spice> <dut: golden|pex> <vtune> <tstop> <datfile> [gmin]

The DUT replaces the xschem-netlisted vco_v1 subckt. `golden` is
team_src/magic/vco_v1_golden.spice -- the netlist the LAYOUT is checked against -- so the
control measures the same circuit the layout implements, not the bench schematic (which
carries ppolyf_u_3k r_length=5u where the golden has ppolyf_u_1k r_length=15u).
"""
import io
import os
import re
import sys

REPO = "/foss/designs/AUS-NZ-integration"
SRC = "/foss/designs/_lvs_check/vco/sim/vco_tb.spice"
GOLDEN = REPO + "/team_src/magic/vco_v1_golden.spice"
PEX = REPO + "/signoff/pex/vco_v1/vco_v1.pex.spice"

out, dut, vtune, tstop, dat = sys.argv[1:6]
gmin = sys.argv[6] if len(sys.argv) > 6 else None

s = io.open(SRC, encoding="utf-8").read()
s = re.sub(r"^V2 tune GND [0-9.]+", "V2 tune GND %s" % vtune, s, count=1, flags=re.M)

# --- the DUT ---
if dut == "golden":
    body = io.open(GOLDEN, encoding="utf-8").read()
    m = re.search(r"^\.subckt vco_v1 .*?^\.ends\s*$", body, flags=re.M | re.S)
    new = ("* ---- DUT: team_src/magic/vco_v1_golden.spice (the netlist the layout is LVS'd to)\n"
           + m.group(0).rstrip() + "\n")
else:
    b = io.open(PEX, encoding="utf-8").read()
    # The extraction carries NO inductance -- magic extracts R and C only, and the committed
    # vco_inductor_v2.ext models the coil as two tm11k resistors plus caps. Left as-is the tank
    # has no resonator at all and sits flat at 0 Vpp. So the coil's R/C-only representation is
    # replaced by the lumped model that does carry the 1.2 nH (xschem vco_inductor_v2.subckt,
    # L0/L1 = 0.60 n) -- the same model plus the inductance. Everything else, every lead, bus,
    # via array and all 42 varactors, stays extracted.
    COIL = ("m4_n14800_800#", "m5_n1200_10400#", "m5_n22400_10400#")
    keep, dropped = [], 0
    for l in b.split("\n"):
        t = l.strip()
        if not t or t.startswith("*"):
            continue
        if t.lower().startswith((".option", ".include", ".end")):
            continue
        if "tm11k" in t or any(c in t for c in COIL):
            dropped += 1
            continue
        keep.append(l)
    print("  coil R/C elements removed from the PEX body: %d" % dropped)
    # VSUBS carries the whole cell's 542 substrate caps and IS the substrate, so it is tied.
    TIES = "V_vsubs vco_inductor_v2_0/VSUBS GND 0\n"
    # the coil as the lumped model. PORT1 is the WEST terminal, which 6573181 put on OUT_p.
    COILINST = "X_ind OUT_p OUT_n GND vco_inductor_v2\n"
    new = ("* ---- DUT: signoff/pex/vco_v1/vco_v1.pex.spice (R+C extracted) with the coil's\n"
           "* ---- R/C-only representation swapped for the lumped model that carries the L.\n"
           ".subckt vco_v1 VDD OUT_p OUT_n GND TUNE ISS\n" + TIES + COILINST
           + "\n".join(keep) + "\n.ends\n")
s = re.sub(r"^\.subckt vco_v1 .*?^\.ends\n", new, s, count=1, flags=re.M | re.S)

# --- options: keep the bench's, optionally add gmin ---
if gmin:
    s = s.replace(".option bypass=0", ".option bypass=0\n.option gmin=%s" % gmin, 1)

# --- startup kick + uic transient ---
IC = ".ic v(net1)=0.01 v(net2)=-0.01\n"
s = re.sub(r"^\*\*\*\* begin user architecture code", IC + "**** begin user architecture code",
           s, count=1, flags=re.M)

CTRL = """.control
save all
set num_threads=2
tran 5p %s uic
wrdata %s v(net1) v(net2) v(out_p) v(out_n) i(v1) i(viss_meas)
.endc
""" % (tstop, dat)
s = re.sub(r"^\.control\n.*?^\.endc\n", CTRL, s, count=1, flags=re.M | re.S)

io.open(out, "w", encoding="utf-8", newline="\n").write(s)
print("wrote %s  dut=%s vtune=%s tstop=%s gmin=%s" % (os.path.basename(out), dut, vtune, tstop, gmin))
