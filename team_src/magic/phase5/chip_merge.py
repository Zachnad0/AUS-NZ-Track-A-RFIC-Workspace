#!/usr/bin/env python3
# chip_merge.py -- assemble chip_top.gds by streaming each block's SIGNED-OFF golden GDS
# verbatim (via KLayout copy_tree), placed at the docs/phase7-floorplan.md offsets. This
# avoids re-rendering foundry geometry through magic, which perturbs sub-grid features
# (a magic gds-read->gds-write roundtrip of PFD_lib's foundry dualgate created a 0.68um
# DV.5 sliver; streaming the golden bytes keeps every block exactly as it signed off).
#
# Placement: getcell/floorplan targets are block BBOX-LL in um. KLayout inserts a cell at
# its ORIGIN, so origin = target_LL - block_bbox_LL.  (block_bbox_LL from gds/<blk>.gds)
import pya

GDS = "/foss/designs/AUS-NZ-integration/gds"
# (file, topcell, target_LL_x, target_LL_y, block_bbox_LL_x, block_bbox_LL_y)
BLOCKS = [
    ("DIV2_QUAD_v1", 0.0,   0.0,   -65.000, -105.000),  # bottom-left
    ("vco_v1",       290.0, 0.0,   -112.000, -119.480), # bottom-right, 53um gap from DIV2
    ("ibias_gen_v1", 0.0,   205.0, -7.660,  -4.100),    # mid-left, above DIV2
    ("CP_v1",        210.0, 205.0, -27.250, -23.010),   # mid, right of ibias
    ("PFD_lib",      210.0, 245.0, 0.000,   0.000),     # top-mid, far from vco
]

# Cells to ORIGIN-NORMALIZE inside chip_top: shift the cell's own frame so its bbox-LL
# is (0,0), and place it directly at the floorplan target. The ABSOLUTE geometry is
# byte-identical (the +(-blx,-bly) content shift and the (tx,ty) placement cancel to the
# original (tx-blx, ty-bly) offset -- verified by a flat XOR before/after). Reason: Bailey's
# extra_be_checks EXTRACT_ABSTRACT path `lef write`s a cell whose native LL != (0,0) with a
# non-zero LEF ORIGIN, and `lef read` then mis-places the abstract by -ORIGIN so its pins
# miss the chip metal. Normalizing the frame makes ORIGIN 0 so the abstract aligns. Only
# vco_v1 needs abstracting (nmoscap varactor + spiral); gds/vco_v1.gds is left untouched,
# so block-level verify_cp vco_v1 is unaffected. See docs/gf180-flat-gds-gencell-lvs.md.
NORMALIZE = {"vco_v1"}

master = pya.Layout()
master.dbu = 0.005
chip = master.create_cell("chip_top")

for name, tx, ty, blx, bly in BLOCKS:
    ly = pya.Layout()
    ly.read("%s/%s.gds" % (GDS, name))
    src = ly.cell(name)
    if src is None:
        raise RuntimeError("top cell %s not found in %s.gds" % (name, name))
    tgt = master.create_cell(name)
    tgt.copy_tree(src)                      # deep copy of the golden hierarchy, verbatim
    if name in NORMALIZE:
        tgt.transform(pya.DTrans(-blx, -bly))  # shift frame so bbox-LL -> (0,0)
        dx, dy = tx, ty                        # place the normalized cell directly at target
    else:
        dx, dy = tx - blx, ty - bly            # origin so bbox-LL lands on the floorplan target
    trans = pya.DCplxTrans(1.0, 0.0, False, dx, dy)
    chip.insert(pya.DCellInstArray(tgt.cell_index(), trans))
    print("placed %-16s origin=(%.3f,%.3f) -> LL=(%.1f,%.1f)%s"
          % (name, dx, dy, tx, ty, "  [origin-normalized]" if name in NORMALIZE else ""))

bb = chip.dbbox()
print("CHIP_BBOX_um=(%.3f,%.3f)-(%.3f,%.3f)  size=%.2f x %.2f"
      % (bb.left, bb.bottom, bb.right, bb.top, bb.width(), bb.height()))
print("CELL_COUNT=%d" % master.cells())
master.write("%s/chip_top.gds" % GDS)
print("WROTE %s/chip_top.gds" % GDS)
