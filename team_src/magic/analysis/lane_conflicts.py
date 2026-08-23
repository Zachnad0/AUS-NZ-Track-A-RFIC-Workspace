#!/usr/bin/env python3
# lane_conflicts.py -- the west-strip / south-corridor allocation as DATA, checked two ways:
#   (1) NET-vs-NET: every pair of segments belonging to different nets, on the SAME layer,
#       tested for rectangle overlap. This is the check that was done by eye in 3o and 3p and
#       that missed a real M5-on-M5 short between VSSA's descent and the ISS south lane.
#   (2) NET-vs-CHIP: every segment tested against the existing chip_top geometry ON ITS OWN
#       LAYER only (a different-layer crossing is benign; a same-layer one is a short).
#
# Same-layer overlap with zero gap is invisible to DRC -- there is no spacing violation when
# two shapes merge -- which is how the I_N/Q_N short in 3i and the I_P/Q_P tap-to-block short
# in 3l both passed a clean DRC. This runs before metal is cut, not after.
#
# Run: klayout -b -r team_src/magic/analysis/lane_conflicts.py
# Exit is advisory (printed); NOT the flow -- an analysis harness. Writes nothing.
import pya

REPO = "/foss/designs/AUS-NZ-integration"
LAYER = {"M1": 34, "M2": 36, "M3": 42, "M4": 46, "M5": 81}

# --- THE ALLOCATION (plan doc 3o as revised by 3p). die coords, um. ---
# (net, layer, x0, y0, x1, y1, width)  -- a segment is the swept rectangle of a centreline.
SEG = [
    # ---- VTUNE : route (a), approved ----
    ("VTUNE", "M3", 558.68, 266.70, 465.00, 266.70, 0.4),
    ("VTUNE", "M3", 465.00, 266.70, 465.00, 165.00, 0.4),
    ("VTUNE", "M3", 465.00, 165.00,  10.00, 165.00, 0.4),
    ("VTUNE", "M3",  10.00, 165.00,  10.00, 482.50, 0.4),
    ("VTUNE", "M2",  10.00, 482.50,   0.50, 482.50, 0.4),
    ("VTUNE", "M2",   0.50, 460.34,   0.50, 504.66, 1.0),   # pad stub over the 8 fingers

    # ---- IBIAS ----
    ("IBIAS", "M3", 271.30, 423.90,  34.00, 423.90, 0.4),
    ("IBIAS", "M3",  34.00, 423.90,  34.00, 282.50, 0.4),
    ("IBIAS", "M2",  34.00, 282.50,   0.50, 282.50, 0.4),
    ("IBIAS", "M2",   0.50, 260.34,   0.50, 304.66, 1.0),

    # ---- VDDA : M4, never M5 (the ring left segment is M5 at x182.5-197.5) ----
    ("VDDA",  "M4", 256.00, 399.00,  46.00, 399.00, 3.0),
    ("VDDA",  "M4",  46.00, 399.00,  46.00, 205.00, 3.0),
    ("VDDA",  "M2",  46.00, 205.00,   0.50, 205.00, 3.0),
    ("VDDA",  "M2",   0.50, 146.36,   0.50, 218.64, 1.0),

    # ---- VSSA : M5 spur off the ring bottom ----
    ("VSSA",  "M5", 175.00, 190.00, 120.00, 190.00, 15.0),
    ("VSSA",  "M5", 120.00, 190.00, 120.00,  82.50, 15.0),
    ("VSSA",  "M5", 120.00,  82.50,  16.00,  82.50, 9.5),
    ("VSSA",  "M2",  16.00,  82.50,   0.50,  82.50, 9.5),
    ("VSSA",  "M2",   0.50,  46.36,   0.50, 118.64, 1.0),

    # ---- ISS : >=10 um M5 bus (option A). M4 wherever it must cross M5. ----
    ("ISS",   "M2", 587.04, 260.33, 490.00, 260.33, 8.0),   # escape west out of the vco
    ("ISS",   "M4", 490.00, 260.33, 455.00, 260.33, 10.0),  # into the gap
    ("ISS",   "M4", 455.00, 260.33, 455.00, 140.00, 10.0),  # gap descent -- M4 THROUGH the ring band
    ("ISS",   "M5", 455.00, 140.00, 130.00, 140.00, 10.0),  # south lane, M5
    ("ISS",   "M4", 130.00, 140.00, 110.00, 140.00, 10.0),  # <-- the ONE deliberate crossing:
                                                            #     hop to M4 across VSSA's M5 descent
    ("ISS",   "M5", 110.00, 140.00,  90.00, 140.00, 10.0),
    ("ISS",   "M5",  90.00, 140.00,  90.00, 382.50, 10.0),  # riser, west of VSSA's descent
    ("ISS",   "M5",  90.00, 382.50,  16.00, 382.50, 10.0),
    ("ISS",   "M2",  16.00, 382.50,   0.50, 382.50, 10.0),
    ("ISS",   "M2",   0.50, 360.34,   0.50, 404.66, 1.0),
]


def rect(x0, y0, x1, y1, w):
    if abs(y1 - y0) > abs(x1 - x0):          # vertical
        return pya.DBox(min(x0, x1) - w / 2, min(y0, y1), max(x0, x1) + w / 2, max(y0, y1))
    return pya.DBox(min(x0, x1), min(y0, y1) - w / 2, max(x0, x1), max(y0, y1) + w / 2)


print("=== (1) NET vs NET, same layer ===")
bad = 0
for i in range(len(SEG)):
    for j in range(i + 1, len(SEG)):
        na, la, *ga = SEG[i]
        nb, lb, *gb = SEG[j]
        if na == nb or la != lb:
            continue
        ra, rb = rect(*ga), rect(*gb)
        ov = ra & rb
        if not ov.empty() and ov.width() > 1e-9 and ov.height() > 1e-9:
            bad += 1
            print("  *** SHORT  %-6s / %-6s on %s   overlap (%.2f,%.2f)-(%.2f,%.2f)  %.2f x %.2f um"
                  % (na, nb, la, ov.left, ov.bottom, ov.right, ov.top, ov.width(), ov.height()))
print("  %d net-vs-net same-layer overlaps" % bad)

print()
print("=== (2) NET vs EXISTING CHIP GEOMETRY, same layer only ===")
ly = pya.Layout(); ly.read(REPO + "/gds/chip_top.gds")
top = ly.cell("chip_top"); top.flatten(-1, True)
REG = {}
for nm, num in LAYER.items():
    REG[nm] = pya.Region(top.begin_shapes_rec(ly.layer(num, 0)))

hits = 0
for net, lay, *g in SEG:
    r = rect(*g)
    clash = REG[lay].interacting(pya.Region(r.to_itype(ly.dbu)))
    n = clash.count()
    if n:
        hits += 1
        bb = clash.bbox()
        print("  %-6s %s (%7.2f,%7.2f)-(%7.2f,%7.2f) w%.1f : %3d same-layer shapes, bbox (%.2f,%.2f)-(%.2f,%.2f)"
              % (net, lay, g[0], g[1], g[2], g[3], g[4], n,
                 bb.left * ly.dbu, bb.bottom * ly.dbu, bb.right * ly.dbu, bb.top * ly.dbu))
    else:
        print("  %-6s %s (%7.2f,%7.2f)-(%7.2f,%7.2f) w%.1f : clear on %s"
              % (net, lay, g[0], g[1], g[2], g[3], g[4], lay))
print("  %d segments touch existing geometry on their own layer" % hits)
