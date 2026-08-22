import pya
ly = pya.Layout(); ly.read("/foss/designs/AUS-NZ-integration/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)
NAME = {33:"contact",34:"M1",35:"via1",36:"M2",38:"via2",42:"M3",40:"via3",46:"M4",41:"via4",81:"M5"}
# CHIP coords of the block taps (from other_pins.py SRC)
TAP = {
 "VDDA":(74.16,231.60), "IBIAS":(71.30,223.90), "ISS":(395.84,60.33), "VTUNE":(358.68,66.70),
 "CP_OUT":(272.25,215.41), "VDDD":(229.68,256.76), "REF_IN":(210.28,257.60),
}
for net,(cx,cy) in TAP.items():
    reg = pya.DBox(cx-1.0, cy-1.0, cx+1.0, cy+1.0)   # 2um window around the tap
    present=[]
    for li in ly.layer_indices():
        info = ly.get_info(li)
        if info.layer not in NAME: continue
        for sh in top.shapes(li).each():
            if (sh.is_box() or sh.is_polygon()) and sh.dbbox().overlaps(reg):
                present.append(NAME[info.layer]); break
    print("%-8s chip(%.2f,%.2f) die(%.2f,%.2f)  layers: %s"
          % (net, cx, cy, cx+200, cy+200, ",".join(present)))
