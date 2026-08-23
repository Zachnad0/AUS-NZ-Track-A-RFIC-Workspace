import pya
ly = pya.Layout(); ly.read("/foss/designs/AUS-NZ-integration/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)
NAME = {33:"contact",34:"M1",35:"via1",36:"M2",38:"via2",42:"M3",40:"via3",46:"M4",41:"via4",81:"M5",
        64:"nwell",22:"comp",30:"poly"}
# TUNE label maps to chip(358.68,66.70); GND ~ chip(358.50,49.78). Dump all shapes in a window
# spanning both + the westward escape, with per-shape extents, to see TUNE vs GND M1 layout.
reg = pya.DBox(344.0, 44.0, 372.0, 74.0)
for li in ly.layer_indices():
    info = ly.get_info(li)
    if info.layer not in NAME: continue
    hits=[sh.dbbox() for sh in top.shapes(li).each() if (sh.is_box() or sh.is_polygon()) and sh.dbbox().overlaps(reg)]
    if hits:
        print("== %s (%d shapes) ==" % (NAME[info.layer], len(hits)))
        for h in sorted(hits, key=lambda b:(round(b.bottom,1),b.left))[:12]:
            print("     (%.2f,%.2f)-(%.2f,%.2f)" % (h.left,h.bottom,h.right,h.top))
