#!/usr/bin/env python3
# cell_list.py -- print the cell hierarchy of a GDS (env GDSF). Verifies the abstract
# subcells survive so the abstract-preload extraction can black-box them (rule: check the
# written GDS cell list before trusting any DRC/extract count).
import pya, os
f = os.environ.get("GDSF", "/foss/designs/AUS-NZ-integration/gds/reh_phase8.gds")
ly = pya.Layout(); ly.read(f)
print("cells in", f, ":")
for c in ly.each_cell():
    tag = " [TOP]" if c.is_top() else ""
    print("   %-24s%s" % (c.name, tag))
for want in ("vco_inductor_v2", "vco_varactors", "chip_top", "reh_phase8"):
    print("   has %-16s: %s" % (want, ly.cell(want) is not None))
