# varactor_comp_gate.py -- GDS-level gate for the 42 cap_nmos_03v3_b varactors in vco_varactors.
#
#   klayout -b -r varactor_comp_gate.py [-rd gds=<file.gds>[,<file.gds>...]]
#   default: gds/vco_varactors.gds, gds/vco_v1.gds, gds/chip_top.gds of this repo
#
# Why it exists (2026-11-02): magic's stock gf180mcuD tech does not write COMP (22/0) under a
# 3.3 V `nvaractor` -- the gdsii cifoutput DIFF layer takes `alldiff`, and `alldifflv` leaves
# the LV varactors out. Every vco_varactors.gds written before 2026-11-02 therefore had POLY,
# NWELL, NPLUS and MOS_CAP_MK over the 42 gates but NO COMP, i.e. poly over field oxide, and the
# PDK's own LVS derivation found 0 varactors. See signoff/lvs/tech_patches/README.md.
#
# Two checks per file, both on the flattened top cell. Exit 0 iff every file passes:
#   1. COMP (22/0) & MOS_CAP_MK (166/5) == 1050 um^2  (42 gates x 5 um x 5 um)
#   2. the PDK KLayout LVS derivation of cap_nmos_03v3_b finds 42 devices -- mirrored from
#      gf180mcuD libs.tech/klayout/tech/lvs/rule_decks general_derivations.lvs:23,25,56 and
#      moscap_derivations.lvs:23,55 (layer numbers from layers_definitions.lvs).
import os, sys
import pya

EXPECT_AREA, EXPECT_N = 1050.0, 42
here = os.path.dirname(os.path.abspath(__file__))
repo = os.path.dirname(os.path.dirname(os.path.dirname(here)))
try:
    files = gds.split(",")
except NameError:
    files = ["%s/gds/%s.gds" % (repo, c) for c in ("vco_varactors", "vco_v1", "chip_top")]

ok = True
for path in files:
    ly = pya.Layout(); ly.read(path)
    top = ly.top_cells()[0]; u = ly.dbu
    G = lambda l, d: pya.Region(top.begin_shapes_rec(ly.layer(l, d))).merged()
    comp, nwell, dualgate, poly2, nplus = G(22, 0), G(21, 0), G(55, 0), G(30, 0), G(32, 0)
    res_mk, v5_xtor, mos_cap_mk = G(110, 5), G(112, 1), G(166, 5)
    moscap_exclude = G(62, 0) + G(24, 0) + G(49, 0)          # resistor + esd + sab
    tgate = (poly2 & comp) - res_mk
    ngate_lv_base = ((nplus & tgate) - v5_xtor) - dualgate
    cap = (ngate_lv_base & nwell).interacting(mos_cap_mk) - moscap_exclude
    area = (comp & mos_cap_mk).area() * u * u
    n = cap.count()
    good = abs(area - EXPECT_AREA) < 1e-6 and n == EXPECT_N
    ok &= good
    print("%-4s %-30s top=%-14s COMP&MOS_CAP_MK %8.3f um2 (want %.0f) | cap_nmos_03v3_b %2d (want %d)"
          % ("PASS" if good else "FAIL", os.path.basename(path), top.name, area, EXPECT_AREA, n, EXPECT_N))
print("VARACTOR_COMP_GATE", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
