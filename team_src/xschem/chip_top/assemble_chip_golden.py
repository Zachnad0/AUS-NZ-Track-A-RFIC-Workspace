#!/usr/bin/env python3
# assemble_chip_golden.py -- build team_src/magic/chip_top_golden.spice, the chip LVS golden.
#
# NOT typed: the TOP subckt (chip_top + its 5 block instances) is taken verbatim from
# xschem's netlist of chip_top.sch (chip_top.spice); the block DEFINITIONS are the five
# SIGNED-OFF block goldens, inlined verbatim. So the golden = generated top connectivity +
# the exact per-block goldens that each block's layout already LVS-matched.
#
# From chip_top.spice we KEEP the top subckt (uncommenting xschem's `**.subckt`/`**.ends`)
# and its x_ instance lines, and DROP the empty black-box `.subckt <block> ... .ends` stubs
# (they would collide with the real block goldens we inline).

import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NETLIST = os.path.join(HERE, "chip_top.spice")
MAGIC = os.path.join(REPO, "team_src", "magic")
OUT = os.path.join(MAGIC, "chip_top_golden.spice")
BLOCKS = ["PFD_lib", "CP_v1", "ibias_gen_v1", "DIV2_QUAD_v1", "vco_v1"]

# --- extract the chip_top top subckt from the xschem netlist ---
top = []
in_top = False
with open(NETLIST) as f:
    for line in f:
        s = line.rstrip("\n")
        if s.startswith("**.subckt chip_top"):
            in_top = True
            top.append(s[2:])          # strip '**' -> real .subckt
            continue
        if in_top and s.startswith("**.ends"):
            top.append(s[2:])          # strip '**' -> real .ends
            in_top = False
            break
        if in_top:
            top.append(s)              # x_ instance lines and *.ipin/*.opin comments

if not top or not top[0].startswith(".subckt chip_top"):
    raise SystemExit("could not extract chip_top subckt from %s" % NETLIST)
# sanity: exactly 5 BLOCK instances. Rung 3 adds secondary-ESD devices to the same subckt
# (XR_ESD_* resistors and D_ESD_* diodes), so the count must look at the x_<block> prefix the
# generator uses and not at "starts with x" -- otherwise a resistor reads as a sixth block.
xlines = [l for l in top if l.lower().startswith("x_")]
esdlines = [l for l in top if "_ESD_" in l.upper()]
if len(xlines) != 5:
    raise SystemExit("expected 5 block instances in chip_top, found %d" % len(xlines))

with open(OUT, "w", newline="\n") as o:
    o.write("* chip_top_golden.spice -- PLL die-level LVS golden.\n")
    o.write("* TOP: netlisted from team_src/xschem/chip_top/chip_top.sch (never typed).\n")
    o.write("* BLOCKS: the five SIGNED-OFF block goldens, inlined verbatim below.\n")
    o.write("* GND is the chip-wide common (internal net, no pad). vco ISS tied to GND.\n")
    o.write("*\n")
    o.write("\n".join(top) + "\n\n")
    for b in BLOCKS:
        gp = os.path.join(MAGIC, b + "_golden.spice")
        with open(gp) as gf:
            body = gf.read().rstrip("\n")
        o.write("* ---- inlined: %s_golden.spice ----\n" % b)
        o.write(body + "\n\n")

print("wrote", OUT)
print("top subckt line:", top[0])
for l in xlines:
    print("  ", l)
print("secondary-ESD devices:", len(esdlines))
for l in esdlines:
    print("  ", l)
