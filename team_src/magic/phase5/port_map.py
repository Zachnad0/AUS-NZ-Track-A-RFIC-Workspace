#!/usr/bin/env python3
# port_map.py -- every block port in CHIP coordinates, grouped by chip net (per the
# chip_top.sch net map). chip_coord = block_local_label_coord + block_origin(dx,dy),
# where the origins are chip_merge.py's (target_LL - block_bbox_LL). Prints, per net,
# the (block, pin, layer, chip_x, chip_y) terminals a router must tie together.
import gdspy, sys
GDS = "/foss/designs/AUS-NZ-integration/gds"
LAYER = {34: "M1", 36: "M2", 42: "M3", 46: "M4", 81: "M5"}

# block -> chip-merge origin (um): where the block's (0,0) maps in chip coords
ORIGIN = {
    "DIV2_QUAD_v1": (65.0, 105.0), "vco_v1": (402.0, 119.48),
    "ibias_gen_v1": (7.66, 209.10), "CP_v1": (237.25, 228.01), "PFD_lib": (210.0, 245.0),
}
# block pin -> chip net (mirror of chip_sch_gen.py NETMAP)
NETMAP = {
    "PFD_lib": {"REF": "REF_IN", "FB": "I_P", "UP": "UP", "DOWN": "DOWN", "VDD": "VDDD", "VSS": "GND"},
    "CP_v1": {"UP": "UP", "DOWN": "DOWN", "CP_OUT": "CP_OUT", "VDD": "VDDA", "VSS": "GND", "VGP": "VGP", "VGN": "VGN"},
    "ibias_gen_v1": {"IBIAS": "IBIAS", "VGP": "VGP", "VGN": "VGN", "IB_DIV2": "IB_DIV2", "VDD": "VDDA", "VSS": "GND"},
    "DIV2_QUAD_v1": {"CK": "VCO_OUTP", "CKB": "VCO_OUTN", "IBIAS": "IB_DIV2", "I_P": "I_P", "I_N": "I_N", "Q_P": "Q_P", "Q_N": "Q_N", "VDD": "VDDD", "VSS": "GND"},
    "vco_v1": {"VDD": "VDDA", "OUT_p": "VCO_OUTP", "OUT_n": "VCO_OUTN", "GND": "GND", "TUNE": "VTUNE", "ISS": "GND"},
}
# only these labels are real block ports (skip internal ones like NMID/PMID/UPB/OI...)
PORTS = {b: set(m) for b, m in NETMAP.items()}

nets = {}
for blk, (ox, oy) in ORIGIN.items():
    lib = gdspy.GdsLibrary(infile="%s/%s.gds" % (GDS, blk))
    top = lib.top_level()[0]
    for L in top.get_labels(depth=0):
        if L.text not in PORTS[blk]:
            continue
        net = NETMAP[blk][L.text]
        cx, cy = L.position[0] + ox, L.position[1] + oy
        nets.setdefault(net, []).append((blk, L.text, LAYER.get(L.layer, str(L.layer)), round(cx, 2), round(cy, 2)))

for net in sorted(nets):
    print("NET %-9s (%d terminals):" % (net, len(nets[net])))
    for t in sorted(nets[net]):
        print("    %-13s.%-7s %-3s (%7.2f, %7.2f)" % t)
