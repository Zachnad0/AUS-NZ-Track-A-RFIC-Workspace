import pya, math

ly = pya.Layout(); ly.read("/foss/designs/AUS-NZ-integration/gds/chip_top.gds")
top = ly.cell("chip_top")
M1 = ly.layer(34, 0)

# DIV2 output taps in CURRENT chip coords (from port_map.py, on the net metal at the label)
taps = {"I_P": (235.18, 140.27), "I_N": (2.18, 140.27),
        "Q_P": (235.18, 51.92),  "Q_N": (2.18, 51.92)}

# measure the M1 metal shape covering each tap (tap-the-extent)
print("=== M1 net-metal extent at each tap (current chip frame) ===")
for n, (x, y) in taps.items():
    reg = pya.DBox(x-1.0, y-1.0, x+1.0, y+1.0)
    best = None
    for sh in top.shapes(M1).each():
        if (sh.is_box() or sh.is_polygon()) and sh.dbbox().overlaps(reg):
            b = sh.dbbox()
            if best is None or b.area() > best.area(): best = b
    if best:
        print("  %-4s tap(%.2f,%.2f)  M1 shape (%.2f,%.2f)-(%.2f,%.2f)  w=%.2f h=%.2f"
              % (n, x, y, best.left, best.bottom, best.right, best.top, best.width(), best.height()))
    else:
        print("  %-4s tap(%.2f,%.2f)  no M1 shape within 1um" % (n, x, y))

# BH pad rect CENTERS at the north inner edge (y=549), from the def translated_user
pads = {"I_P": (167.5, 549.0), "I_N": (267.5, 549.0), "Q_P": (367.5, 549.0), "Q_N": (467.5, 549.0)}

def hauls(dx, dy, label):
    print("\n=== placement '%s': core offset (dx=%.1f, dy=%.1f) -> boundary LL at (%.1f,%.1f) ==="
          % (label, dx, dy, -25+dx, -21.5+dy))
    res = {}
    for n, (tx, ty) in taps.items():
        ax, ay = tx+dx, ty+dy           # tap in DIEAREA frame
        px, py = pads[n]
        man = abs(px-ax) + abs(py-ay)
        stl = math.hypot(px-ax, py-ay)
        res[n] = man
        print("  %-4s tap_die(%.1f,%.1f) -> pad(%.1f,%.1f)  Manhattan=%.1f  straight=%.1f"
              % (n, ax, ay, px, py, man, stl))
    longest = max(res.values()); mn = min(res.values())
    print("  spread: longest=%.1f (%s)  shortest=%.1f (%s)  Delta=%.1f um"
          % (longest, max(res, key=res.get), mn, min(res, key=res.get), longest-mn))
    print("  padding to match longest: " + ", ".join("%s +%.1f" % (n, longest-res[n]) for n in ["I_P","I_N","Q_P","Q_N"]))
    return res

# Item 2: bottom-left (boundary LL at DIEAREA (0,0))
hauls(25.0, 21.5, "bottom-left")
