import pya
ly = pya.Layout(); ly.read("/foss/designs/AUS-NZ-integration/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)
NAME = {33:"contact",34:"M1",35:"via1",36:"M2",38:"via2",42:"M3",40:"via3",46:"M4",41:"via4",81:"M5"}
for net,(cx,cy) in [("I_P",(235.18,140.27)),("Q_P",(235.18,51.92)),
                    ("Q_N",(2.18,51.92)),("I_N",(2.18,140.27))]:
    print("==== %s tap chip(%.2f,%.2f) die(%.2f,%.2f) ====" % (net,cx,cy,cx+200,cy+200))
    reg = pya.DBox(cx-0.6, cy-0.6, cx+0.6, cy+0.6)
    for li in ly.layer_indices():
        info = ly.get_info(li)
        if info.layer not in NAME: continue
        hits=[sh.dbbox() for sh in top.shapes(li).each() if (sh.is_box() or sh.is_polygon()) and sh.dbbox().overlaps(reg)]
        if hits:
            b=pya.DBox()
            for h in hits: b+=h
            print("   %-8s %d  union(%.2f,%.2f)-(%.2f,%.2f)"%(NAME[info.layer],len(hits),b.left,b.bottom,b.right,b.top))
