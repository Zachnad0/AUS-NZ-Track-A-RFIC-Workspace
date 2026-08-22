import pya
ly = pya.Layout(); ly.read("/foss/designs/AUS-NZ-integration/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)
NAME = {34:"M1",35:"via1",36:"M2",38:"via2",42:"M3",40:"via3",46:"M4",41:"via4",81:"M5"}
# For each vco tap, scan upward in a narrow x-strip and find the first y where a clear
# window (no M2/M3/M4/M5) opens up -- the escape height. Also scan west/east strips.
def occ_at(reg):
    hits=set()
    for li in ly.layer_indices():
        info=ly.get_info(li)
        if info.layer not in NAME: continue
        for sh in top.shapes(li).each():
            if (sh.is_box() or sh.is_polygon()) and sh.dbbox().overlaps(reg):
                hits.add(NAME[info.layer]); break
    return hits
for net,(cx,cy) in [("VTUNE",(358.68,66.70)),("ISS",(395.84,60.33))]:
    print("==== %s tap chip(%.2f,%.2f) ====" % (net,cx,cy))
    # vertical escape: scan y from tap up to 290 in 5um bands, 3um-wide strip at tap x
    for y in range(int(cy), 292, 8):
        reg=pya.DBox(cx-1.5, y, cx+1.5, y+8)
        print("   up y[%d,%d]: %s" % (y,y+8, ",".join(sorted(occ_at(reg))) or "CLEAR"))
