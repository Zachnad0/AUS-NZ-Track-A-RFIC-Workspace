#!/usr/bin/env python3
# chip_sch_gen.py -- generate chip_top.sch + 5 BLACK-BOX block interface symbols.
#
# WHY black boxes and not the committed block symbols:
#   * CP_v1.sym is STALE -- it has 5 pins (UP DOWN CP_OUT VDD VSS) but CP_v1's own signed-off
#     golden + layout have 7 (adds VGP VGN). Instancing it would drop the bias nets.
#   * There is NO PFD_lib.sym at all -- only PFD_v1.sym (right ports, wrong cell name for LVS).
#   * Editing a block .sch is forbidden (rule 12); editing block .sym would mutate a committed
#     block interface. So chip_top instances fresh black-box symbols whose port lists come
#     VERBATIM from each block's signed-off golden .subckt line, and the chip golden pulls the
#     block DEFINITIONS by .include-ing those same signed-off goldens. No block file is touched.
#
# Ports per block, IN GOLDEN ORDER (so @pinlist matches the .subckt port order):
#   PFD_lib      REF FB UP DOWN VDD VSS
#   CP_v1        UP DOWN CP_OUT VDD VSS VGP VGN
#   ibias_gen_v1 IBIAS VGP VGN IB_DIV2 VDD VSS
#   DIV2_QUAD_v1 CK CKB IBIAS I_P I_N Q_P Q_N VDD VSS
#   vco_v1       VDD OUT_p OUT_n GND TUNE ISS
#
# Connectivity is by NET LABEL (xschem connects same-named lab_pin/ipin/opin): a lab_pin is
# dropped exactly on every block pin (connection point = pin-box center = instance_pos+center),
# and the 10 pads are ipin/opin with the pad net name. Ground is the internal common net GND
# (no pad, per info.yaml). vco ISS ties to GND (see NOTE below).

import os

HERE = os.path.dirname(os.path.abspath(__file__))

# block -> [pins in golden order]
BLOCKS = {
    "PFD_lib":      ["REF", "FB", "UP", "DOWN", "VDD", "VSS"],
    "CP_v1":        ["UP", "DOWN", "CP_OUT", "VDD", "VSS", "VGP", "VGN"],
    "ibias_gen_v1": ["IBIAS", "VGP", "VGN", "IB_DIV2", "VDD", "VSS"],
    "DIV2_QUAD_v1": ["CK", "CKB", "IBIAS", "I_P", "I_N", "Q_P", "Q_N", "VDD", "VSS"],
    "vco_v1":       ["VDD", "OUT_p", "OUT_n", "GND", "TUNE", "ISS"],
}
DIRS = {  # pin directions (cosmetic in a black box, but set them sensibly)
    "PFD_lib":      {"REF": "in", "FB": "in", "UP": "out", "DOWN": "out", "VDD": "inout", "VSS": "inout"},
    "CP_v1":        {"UP": "in", "DOWN": "in", "CP_OUT": "out", "VDD": "inout", "VSS": "inout", "VGP": "in", "VGN": "in"},
    "ibias_gen_v1": {"IBIAS": "in", "VGP": "out", "VGN": "out", "IB_DIV2": "out", "VDD": "inout", "VSS": "inout"},
    "DIV2_QUAD_v1": {"CK": "in", "CKB": "in", "IBIAS": "in", "I_P": "out", "I_N": "out", "Q_P": "out", "Q_N": "out", "VDD": "inout", "VSS": "inout"},
    "vco_v1":       {"VDD": "inout", "OUT_p": "out", "OUT_n": "out", "GND": "inout", "TUNE": "in", "ISS": "inout"},
}

# block pin -> chip net.  I_P is shared: DIV2.I_P == I_P pad == PFD.FB (loop feedback).
# vco ISS -> GND: no on-chip VCO tail-current source exists, and info.yaml is "common ground
# everywhere"; the LC-VCO runs sources-to-ground on-chip (5.4 record: ISS is electrically gnd).
NETMAP = {
    "PFD_lib":      {"REF": "REF_IN", "FB": "I_P", "UP": "UP", "DOWN": "DOWN", "VDD": "VDDD", "VSS": "GND"},
    "CP_v1":        {"UP": "UP", "DOWN": "DOWN", "CP_OUT": "CP_OUT", "VDD": "VDDA", "VSS": "GND", "VGP": "VGP", "VGN": "VGN"},
    "ibias_gen_v1": {"IBIAS": "IBIAS", "VGP": "VGP", "VGN": "VGN", "IB_DIV2": "IB_DIV2", "VDD": "VDDA", "VSS": "GND"},
    "DIV2_QUAD_v1": {"CK": "VCO_OUTP", "CKB": "VCO_OUTN", "IBIAS": "IB_DIV2", "I_P": "I_P", "I_N": "I_N", "Q_P": "Q_P", "Q_N": "Q_N", "VDD": "VDDD", "VSS": "GND"},
    "vco_v1":       {"VDD": "VDDA", "OUT_p": "VCO_OUTP", "OUT_n": "VCO_OUTN", "GND": "GND", "TUNE": "VTUNE", "ISS": "GND"},
}

# 10 pads: (net, kind)  kind: ipin (input/supply) or opin (output)
PADS = [
    ("VDDA", "ipin"), ("IBIAS", "ipin"), ("VTUNE", "ipin"), ("CP_OUT", "opin"),
    ("I_P", "opin"), ("I_N", "opin"), ("Q_P", "opin"), ("Q_N", "opin"),
    ("VDDD", "ipin"), ("REF_IN", "ipin"),
]

PITCH = 40  # vertical pin pitch (grid-aligned)

def pin_center(idx, n):
    """left-side stacked pin center for pin idx of n, symbol-local coords."""
    y = (idx - (n - 1) / 2.0) * PITCH
    return (-120.0, y)

def write_symbol(name):
    pins = BLOCKS[name]
    n = len(pins)
    half = (n - 1) / 2.0 * PITCH
    top = -half - 40
    bot = half + 40
    lines = []
    lines.append("v {xschem version=3.4.8RC file_version=1.3}")
    lines.append("K {type=subcircuit")
    lines.append('format="@name @pinlist @symname"')
    lines.append('spectre_format="@name ( @pinlist ) @symname"')
    lines.append("template=\"name=x1\"")
    lines.append("}")
    lines.append("T {@symname} -60 %g 0 0 0.3 0.3 {}" % (top - 10))
    lines.append("T {@name} 40 %g 0 0 0.2 0.2 {}" % (bot + 4))
    # body rectangle
    lines.append("P 4 5 -100 %g 100 %g 100 %g -100 %g -100 %g {}" % (top, top, bot, bot, top))
    for i, p in enumerate(pins):
        cx, cy = pin_center(i, n)
        d = DIRS[name][p]
        lines.append("B 5 %g %g %g %g {name=%s dir=%s}" % (cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5, p, d))
        lines.append("L 4 %g %g %g %g {}" % (cx, cy, -100.0, cy))   # leader to body
        lines.append("T {%s} %g %g 0 0 0.2 0.2 {}" % (p, -95.0, cy - 6))
    with open(os.path.join(HERE, name + ".sym"), "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

def main():
    for b in BLOCKS:
        write_symbol(b)

    sch = []
    sch.append("v {xschem version=3.4.8RC file_version=1.3}")
    sch.append("G {}")
    sch.append("K {}")
    sch.append("V {}")
    sch.append("S {}")
    sch.append("E {}")
    sch.append("T {chip_top -- PLL die-level integration (Phase 7). Blocks are black-box interface")
    sch.append("symbols; definitions come from the signed-off block goldens at netlist time.} -200 -700 0 0 0.4 0.4 {}")

    # place blocks in a row, spaced so no pin coords coincide
    order = ["PFD_lib", "CP_v1", "ibias_gen_v1", "DIV2_QUAD_v1", "vco_v1"]
    lab_id = 0
    for k, name in enumerate(order):
        X = k * 600
        Y = 0
        sch.append("C {%s.sym} %g %g 0 0 {name=x_%s}" % (name, X, Y, name.lower()))
        pins = BLOCKS[name]
        n = len(pins)
        for i, p in enumerate(pins):
            cx, cy = pin_center(i, n)
            ax, ay = X + cx, Y + cy
            net = NETMAP[name][p]
            sch.append("C {lab_pin.sym} %g %g 0 0 {name=l%d lab=%s}" % (ax, ay, lab_id, net))
            lab_id += 1

    # 10 pads across the top, as ports (ipin/opin)
    for j, (net, kind) in enumerate(PADS):
        px = j * 160 - 200
        py = -500
        rot = 0
        sch.append("C {%s.sym} %g %g %d 0 {name=P_%s lab=%s}" % (kind, px, py, rot, net, net))

    with open(os.path.join(HERE, "chip_top.sch"), "w", newline="\n") as f:
        f.write("\n".join(sch) + "\n")
    print("wrote 5 black-box .sym + chip_top.sch in", HERE)
    print("nets:", sorted({v for m in NETMAP.values() for v in m.values()} | {p for p, _ in PADS}))

if __name__ == "__main__":
    main()
