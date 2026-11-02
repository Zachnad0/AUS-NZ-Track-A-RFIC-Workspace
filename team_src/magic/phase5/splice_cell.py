# splice_cell.py -- replace the contents of ONE leaf cell inside a GDS with the same-named
# cell from another GDS; nothing else in the layout is touched. Handles a dbu difference
# (chip_top.gds is written at 0.005 by chip_merge.py, the block GDS at 0.001).
#   klayout -b -r splice_cell.py -rd src=IN.gds -rd new=CELL_SOURCE.gds -rd cellname=NAME -rd out=OUT.gds
import pya
L = pya.Layout(); L.read(src)
N = pya.Layout(); N.read(new)
tgt, nc = L.cell(cellname), N.cell(cellname)
assert tgt is not None and nc is not None, "cell %s missing" % cellname
assert tgt.child_instances() == 0 and nc.child_instances() == 0, "leaf cells only"
mag = N.dbu / L.dbu
before = tgt.dbbox()
tgt.clear_shapes()
for i in N.layer_indexes():
    info = N.get_info(i)
    tgt.shapes(L.layer(info.layer, info.datatype)).insert(nc.shapes(i), pya.ICplxTrans(mag))
print("spliced %s: %s -> %s" % (cellname, before, tgt.dbbox()))
L.write(out)
print("wrote", out)
