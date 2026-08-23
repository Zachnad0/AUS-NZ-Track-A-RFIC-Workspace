#!/usr/bin/env python3
# lane_map.py -- measure every lane the west-strip / south-corridor allocation uses, on the
# SEATED chip_top.gds, on EVERY layer (M1-M5, comp, poly, cont, vias) -- not just M2/M3.
#
# WHY ALL LAYERS: the channel map's "clear vertical columns" were computed as clear of M2 AND
# M3 only. That is how docs/phase8-padframe-plan.md 3m came to treat die x489 as a clear column
# when it has M4 in it. Every lane in the 3o allocation is re-measured here on every layer
# rather than read off that map.
#
# WHY ALL FIVE NETS AT ONCE: VSSA, VDDA, IBIAS, ISS and VTUNE all land on the west edge and all
# want the same free die. Routing them one at a time is how 3m happened -- a lane looks clear
# until the net that needed it is routed third.
#
# Run: klayout -b -r team_src/magic/analysis/lane_map.py
# NOT the flow -- an analysis harness. Writes nothing. Results: plan doc 3o.
import pya, math

REPO = "/foss/designs/AUS-NZ-integration"
ly = pya.Layout(); ly.read(REPO + "/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)

NAME = {33: "cont", 34: "M1", 35: "v1", 36: "M2", 38: "v2", 42: "M3", 40: "v3",
        46: "M4", 41: "v4", 81: "M5", 22: "comp", 30: "poly", 64: "nwell"}
IDX = {}
for li in ly.layer_indices():
    info = ly.get_info(li)
    if info.layer in NAME and info.datatype == 0:
        IDX.setdefault(NAME[info.layer], []).append(li)

def occ(box):
    hit = []
    for nm, lis in IDX.items():
        for li in lis:
            f = False
            for sh in top.shapes(li).each_overlapping(box.to_itype(ly.dbu)):
                if sh.is_box() or sh.is_polygon() or sh.is_path():
                    f = True; break
            if f:
                hit.append(nm); break
    return sorted(hit)

def seg(label, x0, y0, x1, y1, w=3.0, step=6.0):
    L = abs(x1 - x0) + abs(y1 - y0)
    n = max(1, int(math.ceil(L / step)))
    hits = {}
    for i in range(n):
        ax = x0 + (x1 - x0) * i / n; ay = y0 + (y1 - y0) * i / n
        bx = x0 + (x1 - x0) * (i + 1) / n; by = y0 + (y1 - y0) * (i + 1) / n
        if abs(y1 - y0) > abs(x1 - x0):
            b = pya.DBox(min(ax, bx) - w / 2, min(ay, by), max(ax, bx) + w / 2, max(ay, by))
        else:
            b = pya.DBox(min(ax, bx), min(ay, by) - w / 2, max(ax, bx), max(ay, by) + w / 2)
        for o in occ(b):
            hits[o] = hits.get(o, 0) + 1
    print("  %-42s (%7.2f,%7.2f)->(%7.2f,%7.2f) L=%7.2f  %s"
          % (label, x0, y0, x1, y1, L,
             ", ".join("%s x%d" % (k, v) for k, v in sorted(hits.items())) or "CLEAR"))
    return L

print("=== GND ring geometry (M5 shapes touching the core perimeter) ===")
for li in IDX["M5"]:
    for sh in top.shapes(li).each():
        if sh.is_box():
            b = sh.dbbox()
            if b.width() > 100 or b.height() > 100:
                print("   M5 %8.2f,%8.2f - %8.2f,%8.2f   (%.1f x %.1f)"
                      % (b.left, b.bottom, b.right, b.top, b.width(), b.height()))

print()
print("=== WEST STRIP: candidate riser columns, full height, ALL layers ===")
for x in (2.0, 6.0, 10.0, 16.0, 22.0, 28.0, 34.0, 40.0, 46.0, 52.0, 65.0, 90.0, 130.0, 160.0, 175.0, 180.0):
    seg("riser x=%.0f  y40 -> y510" % x, x, 40.0, x, 510.0, 3.0, 20.0)

print()
print("=== WEST STRIP: horizontal pad approaches at each pad y, x60 -> x0.5 ===")
for nm, y in (("VSSA", 82.5), ("VDDA", 182.5), ("IBIAS", 282.5), ("ISS", 382.5), ("VTUNE", 482.5)):
    seg("%-6s approach y=%.1f" % (nm, y), 60.0, y, 0.5, y, 3.0, 6.0)

print()
print("=== SOUTH CORRIDOR: east-west lanes, x470 -> x5 ===")
for y in (40.0, 60.0, 80.0, 100.0, 120.0, 135.0, 150.0, 165.0, 172.0):
    seg("south lane y=%.0f" % y, 470.0, y, 5.0, y, 3.0, 25.0)

print()
print("=== TAP ESCAPES not yet measured ===")
seg("ISS   M2 west from tap", 592.0, 260.33, 470.0, 260.33, 3.0, 6.0)
seg("ISS   descend in gap x=455", 455.0, 260.33, 455.0, 150.0, 3.0, 6.0)
seg("IBIAS M2 west from tap y423.9", 268.0, 423.90, 175.0, 423.90, 3.0, 6.0)
seg("IBIAS descend x=170 to y282.5", 170.0, 423.90, 170.0, 282.5, 3.0, 6.0)
seg("VDDA  M5 bus west end -> x60 @ y399", 397.0, 399.0, 60.0, 399.0, 3.0, 6.0)
seg("VDDA  descend x=46  y399 -> y182.5", 46.0, 399.0, 46.0, 182.5, 3.0, 6.0)
seg("VSSA  ring SW corner west  y190", 182.0, 190.0, 60.0, 190.0, 3.0, 6.0)
seg("VSSA  descend x=65 y190 -> y82.5", 65.0, 190.0, 65.0, 82.5, 3.0, 6.0)

print()
print("=== ibias block west edge: where can IBIAS actually leave? ===")
for y in (410.0, 415.0, 420.0, 423.9, 430.0, 440.0, 450.0, 460.0, 468.0):
    seg("ibias exit y=%.1f  x268 -> x196" % y, 268.0, y, 196.0, y, 2.0, 6.0)
