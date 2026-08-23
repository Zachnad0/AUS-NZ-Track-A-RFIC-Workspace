import pya
ly = pya.Layout(); ly.read("/foss/designs/AUS-NZ-integration/gds/vco_v1.gds")
top = ly.cell("vco_v1")
# labels/texts live on datatype 10 of each metal; dump all text with layer+position (chip coords
# of vco_v1's own frame). Find TUNE / ISS / GND / VDD port label locations -- the REAL net access
# points, not the port_map guess.
print("=== text labels in vco_v1 (layer/dt : text @ (x,y)) ===")
for li in ly.layer_indices():
    info = ly.get_info(li)
    for sh in top.shapes(li).each():
        if sh.is_text():
            t = sh.text
            print("  L%d/%d  %-8s @ (%.2f, %.2f)" % (info.layer, info.datatype, t.string, t.x/1000.0, t.y/1000.0))
