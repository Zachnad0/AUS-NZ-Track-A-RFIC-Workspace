import pya
ly = pya.Layout(); ly.read("/foss/designs/AUS-NZ-integration/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)
NAME = {34:"M1",35:"via1",36:"M2",38:"via2",42:"M3",40:"via3",46:"M4",41:"via4",81:"M5"}
def occ(reg):
    s=set()
    for li in ly.layer_indices():
        info=ly.get_info(li)
        if info.layer not in NAME: continue
        for sh in top.shapes(li).each():
            if (sh.is_box() or sh.is_polygon()) and sh.dbbox().overlaps(reg):
                s.add(NAME[info.layer]); break
    return s
# vco west edge chip x358.5; DIV2 east edge chip x235.4. Scan WEST from each tap in 4um steps
# in a 3um-tall strip at tap y, to the gap. Report layer occupancy per step.
for net,(cx,cy) in [("VTUNE",(358.68,66.70)),("ISS",(395.84,60.33))]:
    print("==== %s tap chip(%.2f,%.2f) scanning WEST at y=%.2f ====" % (net,cx,cy,cy))
    x=cx
    while x > 233:
        reg=pya.DBox(x-4.0, cy-1.5, x, cy+1.5)
        print("   x[%.1f,%.1f]: %s" % (x-4.0,x, ",".join(sorted(occ(reg))) or "CLEAR"))
        x-=4.0
