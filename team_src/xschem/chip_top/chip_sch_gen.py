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
# vco ISS -> its OWN pad (NOT GND): ISS is the LC-VCO tail node; the characterized band
# (4.13-6.35 GHz) was simulated with a 1 mA tail mirror driving ISS. Grounding it on-chip
# changes the operating point, so ISS is brought out as a separate analog pad and the tail
# current stays controllable off-chip. (vco.GND -- the nfet-bulk/substrate return -- stays GND.)
NETMAP = {
    "PFD_lib":      {"REF": "REF_IN", "FB": "I_P", "UP": "UP", "DOWN": "DOWN", "VDD": "VDDD", "VSS": "VSSA"},
    "CP_v1":        {"UP": "UP", "DOWN": "DOWN", "CP_OUT": "CP_OUT", "VDD": "VDDA", "VSS": "VSSA", "VGP": "VGP", "VGN": "VGN"},
    "ibias_gen_v1": {"IBIAS": "IBIAS_C", "VGP": "VGP", "VGN": "VGN", "IB_DIV2": "IB_DIV2", "VDD": "VDDA", "VSS": "VSSA"},
    "DIV2_QUAD_v1": {"CK": "VCO_OUTP", "CKB": "VCO_OUTN", "IBIAS": "IB_DIV2", "I_P": "I_P", "I_N": "I_N", "Q_P": "Q_P", "Q_N": "Q_N", "VDD": "VDDD", "VSS": "VSSA"},
    "vco_v1":       {"VDD": "VDDA", "OUT_p": "VCO_OUTP", "OUT_n": "VCO_OUTN", "GND": "VSSA", "TUNE": "VTUNE", "ISS": "ISS"},
}

# LVS pads: kind ipin (supply/in) / opin (out) / iopin (ground).
# GROUND is ONE electrical net (all VSS ties to the shared p-substrate; no deep-nwell), so the
# golden + layout carry ONE ground port, VSSA. info.yaml still lists TWO ground PADS (VSSA index0
# + VSSD) per Bailey -- the second pad bonds to the same ground ring at a different point (marked
# in route_chip.py), separating only bond-wire L. netgen sees one net; that is the A1b question
# for Bailey. So VSSD is NOT a separate LVS port here.
PADS = [
    ("VSSA", "iopin"), ("VDDA", "ipin"), ("IBIAS", "ipin"), ("ISS", "ipin"), ("VTUNE", "ipin"),
    # JOB B: I_P is no longer a PAD. It stays an internal net (DIV2.I_P -> PFD.FB) and so
    # stops being a chip_top PORT -- the port list goes 12 -> 11.
    ("CP_OUT", "opin"), ("I_N", "opin"), ("Q_P", "opin"), ("Q_N", "opin"),
    ("VDDD", "ipin"), ("REF_IN", "ipin"),
]

# --- RUNG 3: secondary ESD (Bailey: "add it yourself and update the schematics accordingly").
# Sizing and topology are the ORGANIZERS', from examples/pads_simulation/symbols/
# io_secondary_3p3/io_secondary_3p3.sch: diodes r_w=10u r_l=10u m=4, ppolyf_u W=16u L=4u, and
# BOTH diodes on the CORE side of the ballast -- so the block instance moves to the clamp node
# (<PAD>_C) and the pad net feeds only the resistor.
#
# POLARITY IS PHYSICS, NOT THE SYMBOL PIN NAMES. pd2nw is P+ in N-well: the P+ is the ANODE, so
# it takes the clamp node and the N-well cathode goes to VDDA. nd2ps is N+ in p-well: the p-well
# is the ANODE, so it takes VSSA and the N+ cathode takes the clamp node. That ordering is what
# magic emits too -- the extracted nd2ps puts its SUBSTRATE node first.
# Pin coords come from the PDK symbols: diodes p(0,-30) m(0,+30); ppolyf_u P(0,-30) M(0,+30) B(-20,0).
ESD_PINS = {"diode": {"p": (0.0, -30.0), "m": (0.0, 30.0)},
            "res":   {"P": (0.0, -30.0), "M": (0.0, 30.0), "B": (-20.0, 0.0)}}
ESD = [   # (inst, symbol, kind, {pin: net}, params)
    ("R_ESD_IBIAS", "symbols/ppolyf_u.sym", "res",
     {"P": "IBIAS", "M": "IBIAS_C", "B": "VSSA"},
     "model=ppolyf_u spiceprefix=X W=16e-6 L=4e-6 m=1"),
    ("D_ESD_IBIAS_P", "symbols/diode_pd2nw_03v3.sym", "diode",
     {"p": "IBIAS_C", "m": "VDDA"},
     "model=diode_pd2nw_03v3 r_w=10u r_l=10u m=4"),
    ("D_ESD_IBIAS_N", "symbols/diode_nd2ps_03v3.sym", "diode",
     {"p": "VSSA", "m": "IBIAS_C"},
     "model=diode_nd2ps_03v3 r_w=10u r_l=10u m=4"),
    # ISS has NO ballast (50 ohm would cost 78.5 mV on the VCO tail), so there is no clamp
    # node distinct from the pad: the diodes hang directly on ISS and vco_v1 keeps its ISS pin.
    ("D_ESD_ISS_P", "symbols/diode_pd2nw_03v3.sym", "diode",
     {"p": "ISS", "m": "VDDA"},
     "model=diode_pd2nw_03v3 r_w=10u r_l=10u m=4"),
    ("D_ESD_ISS_N", "symbols/diode_nd2ps_03v3.sym", "diode",
     {"p": "VSSA", "m": "ISS"},
     "model=diode_nd2ps_03v3 r_w=10u r_l=10u m=4"),
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

    # --- secondary ESD devices, one column per pin, below the block row ---
    for e, (inst, sym, kind, netmap, params) in enumerate(ESD):
        X, Y = e * 300 - 300, 600
        sch.append("C {%s} %g %g 0 0 {name=%s %s}" % (sym, X, Y, inst, params))
        for pin, (dx, dy) in ESD_PINS[kind].items():
            sch.append("C {lab_pin.sym} %g %g 0 0 {name=e%d_%s lab=%s}"
                       % (X + dx, Y + dy, e, pin, netmap[pin]))

    # 13 pads across the top, as ports (ipin/opin/iopin)
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
