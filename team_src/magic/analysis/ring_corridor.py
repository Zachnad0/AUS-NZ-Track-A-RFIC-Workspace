import pya
ly = pya.Layout(); ly.read("/foss/designs/AUS-NZ-integration/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)
NAME = {33:"contact",34:"M1",35:"via1",36:"M2",38:"via2",42:"M3",40:"via3",46:"M4",41:"via4",81:"M5"}
# corridors are in CHIP coords (chip_top gds, no +200 offset). Q_N tap chip (2.18,51.92),
# I_N tap chip (2.18,140.27). Ring left seg chip x[-17.5,-2.5]. DIV2 starts chip x0.
# escape band: chip x[-18,4] around each tap y, to see DIV2 (x>0) vs ring(x<-2.5) vs slot.
for label,(x0,y0,x1,y1) in [("Q_N escape band chip x[-18,4] y[48,56]",(-18,48,4,56)),
                            ("I_N escape band chip x[-18,4] y[136,144]",(-18,136,4,144))]:
    print("===", label, "===")
    reg = pya.DBox(x0,y0,x1,y1)
    for li in ly.layer_indices():
        info = ly.get_info(li)
        if info.layer not in NAME: continue
        hits=[]
        for sh in top.shapes(li).each():
            if (sh.is_box() or sh.is_polygon()) and sh.dbbox().overlaps(reg):
                hits.append(sh.dbbox())
        if hits:
            allb=pya.DBox()
            for h in hits: allb+=h
            print("  %-8s %d shapes union(%.2f,%.2f)-(%.2f,%.2f)"%(NAME[info.layer],len(hits),allb.left,allb.bottom,allb.right,allb.top))
            for h in sorted(hits,key=lambda b:b.left)[:6]:
                print("      (%.2f,%.2f)-(%.2f,%.2f)"%(h.left,h.bottom,h.right,h.top))
