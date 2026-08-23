#!/usr/bin/env python3
# vtune_routes.py -- occupancy-scan candidate VTUNE hauls on the SEATED chip_top.gds and
# report, per segment, exactly which layers each candidate crosses plus its Manhattan length.
#
# WHY: docs/phase8-padframe-plan.md 3m recorded VTUNE as "BOXED" -- the tap reachable but the
# rise to the west pad having no clean column. That was established while chip_top was
# 522 x 309 and every route had to fight for an internal column. Since 2026-08-22 the core is
# SEATED at (175.00,178.50)-(697.00,487.50) inside a 1110 x 550 die, so there is free die south
# of y178.5, west of x175, east of x697 and north of y487.5 that did not exist when 3m was
# written. This script re-tests the premise against the real geometry instead of the memory.
#
# Run: klayout -b -r team_src/magic/analysis/vtune_routes.py
# NOT the flow -- an analysis harness. Writes nothing.
import pya, math

REPO = "/foss/designs/AUS-NZ-integration"
ly = pya.Layout(); ly.read(REPO + "/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)

NAME = {33: "cont", 34: "M1", 35: "v1", 36: "M2", 38: "v2", 42: "M3", 40: "v3",
        46: "M4", 41: "v4", 81: "M5", 22: "comp", 30: "poly"}
IDX = {}
for li in ly.layer_indices():
    info = ly.get_info(li)
    if info.layer in NAME and info.datatype == 0:
        IDX.setdefault(NAME[info.layer], []).append(li)


def occ(box):
    """layers with real (non-text) geometry overlapping box"""
    hit = []
    for nm, lis in IDX.items():
        for li in lis:
            found = False
            for sh in top.shapes(li).each_overlapping(box.to_itype(ly.dbu)):
                if sh.is_box() or sh.is_polygon() or sh.is_path():
                    found = True; break
            if found:
                hit.append(nm); break
    return sorted(hit)


def walk(name, pts, w=3.0, step=6.0):
    print("=== %s ===" % name)
    total = 0.0
    allhits = {}
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = abs(x1 - x0) + abs(y1 - y0)
        total += L
        n = max(1, int(math.ceil(L / step)))
        seg = {}
        for i in range(n):
            ax = x0 + (x1 - x0) * i / n; ay = y0 + (y1 - y0) * i / n
            bx = x0 + (x1 - x0) * (i + 1) / n; by = y0 + (y1 - y0) * (i + 1) / n
            if abs(y1 - y0) > abs(x1 - x0):
                box = pya.DBox(min(ax, bx) - w / 2, min(ay, by), max(ax, bx) + w / 2, max(ay, by))
            else:
                box = pya.DBox(min(ax, bx), min(ay, by) - w / 2, max(ax, bx), max(ay, by) + w / 2)
            for o in occ(box):
                seg[o] = seg.get(o, 0) + 1
                allhits[o] = allhits.get(o, 0) + 1
        print("  (%7.2f,%7.2f)->(%7.2f,%7.2f)  L=%7.2f  %s"
              % (x0, y0, x1, y1, L,
                 ("crosses " + ", ".join("%s x%d" % (k, v) for k, v in sorted(seg.items())))
                 if seg else "CLEAR"))
    print("  TOTAL %.2f um   crossings: %s"
          % (total, ", ".join("%s x%d" % (k, v) for k, v in sorted(allhits.items())) or "none"))
    print()
    return total


TAP = (558.68, 266.70)     # VTUNE tap, M1, die coords (= core 358.68, 66.70)
PAD = (0.5, 482.5)         # W22 VTUNE pin rects: Metal2, x[0,1], y[460.34,504.66]

# (a) west into the DIV2<->vco gap (die x437.36-490.00), SOUTH out of the core, west through
#     free die, north up the free west strip, jog onto the pad fingers.
#     The riser is held at x=10, NOT x=0.5: the west pin rectangles all sit at x[0,1]
#     (VSSA y46-119, VDDA y146-219, IBIAS y260-305, ISS y360-405), so a riser at the pad
#     column would short VTUNE to every one of them on the way up.
A = [TAP, (465.0, 266.70), (465.0, 165.0), (10.0, 165.0), (10.0, 482.5), PAD]

# (d) the "x288-290" column of 3m = die x489: west a little, then NORTH past the spiral.
D = [TAP, (489.0, 266.70), (489.0, 495.0), (10.0, 495.0), (10.0, 482.5), PAD]

# (a-north) exit NORTH through the gap instead of south, for comparison.
AN = [TAP, (486.0, 266.70), (486.0, 495.0), (10.0, 495.0), (10.0, 482.5), PAD]

la = walk("(a) SOUTH exit via the DIV2<->vco gap -> free die -> west strip", A)
ld = walk("(d) die x489 column, NORTH past the spiral (3m's option)", D)
ln = walk("(a-north) NORTH exit via the gap at die x486", AN)
print("summary: (a) south %.1f | (d) spiral column %.1f | (a-north) %.1f um" % (la, ld, ln))

print()
print("=== how clear is the 'x288-290' column really? (die x486-491, y290-386) ===")
for x in (486.0, 487.0, 488.0, 489.0, 490.0, 491.0):
    print("   x=%.1f : %s" % (x, ", ".join(occ(pya.DBox(x - 0.2, 290.0, x + 0.2, 386.0))) or "CLEAR"))

print()
print("=== does the tap face EAST? (inside the vco) ===")
walk("east from the tap", [TAP, (700.0, 266.70)])
