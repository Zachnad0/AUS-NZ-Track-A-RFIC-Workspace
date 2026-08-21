#!/usr/bin/env python3
# channel_map.py -- phase-8 occupancy map for chip_top.gds (chip frame, 522x309).
# (a) per-block per-layer shape count + union extent (real geometry, not bbox);
# (b) CLEAR VERTICAL COLUMNS through the top-block row (clear of M2 AND M3);
# (c) CLEAR HORIZONTAL BANDS across the full core width, per layer.
# Analysis only -- reads the committed GDS, writes nothing into the flow.
import pya, sys

GDS = "/foss/designs/AUS-NZ-integration/gds/chip_top.gds"
LAYERS = {"M2": (36, 0), "M3": (42, 0), "M4": (46, 0), "M5": (81, 0)}
BLOCKS = ["DIV2_QUAD_v1", "vco_v1", "ibias_gen_v1", "CP_v1", "PFD_lib"]

ly = pya.Layout(); ly.read(GDS)
top = ly.cell("chip_top")

def reg(cellname, lnum, ldt):
    li = ly.layer(lnum, ldt)
    c = ly.cell(cellname)
    return pya.Region(c.begin_shapes_rec(li))

# --- (a) per-block per-layer, transformed into chip coords via the instance trans ---
inst_trans = {}
for it in top.each_inst():
    inst_trans.setdefault(it.cell.name, it.trans)   # integer (DBU) transform
print("=== (a) per-block per-layer occupancy (chip coords) ===")
print("%-14s %-3s %5s  %-32s" % ("block", "lyr", "cnt", "union extent x0,y0 - x1,y1 um"))
for b in BLOCKS:
    t = inst_trans.get(b)
    for lname, (lnum, ldt) in LAYERS.items():
        r = reg(b, lnum, ldt)
        cnt = r.size()
        if t is not None:
            r = r.transformed(t)
        if cnt:
            bb = r.bbox()
            print("%-14s %-3s %5d  (%.1f,%.1f)-(%.1f,%.1f)"
                  % (b, lname, cnt, bb.left*ly.dbu, bb.bottom*ly.dbu, bb.right*ly.dbu, bb.top*ly.dbu))
        else:
            print("%-14s %-3s %5d  --" % (b, lname, 0))

# --- flattened chip_top per-layer regions (all metal: blocks + chip routing + buses) ---
FLAT = {ln: pya.Region(top.begin_shapes_rec(ly.layer(l, d))) for ln, (l, d) in LAYERS.items()}
for r in FLAT.values(): r.merge()
DBU = ly.dbu

def clear_columns(ystrip, layers, xmin, xmax, step=1.0, wcol=0.5):
    """x ranges where NONE of `layers` occupy the vertical strip [x, y in ystrip]."""
    occ = pya.Region()
    for ln in layers: occ += FLAT[ln]
    occ.merge()
    clear = []
    x = xmin; run0 = None
    while x <= xmax:
        strip = pya.Region(pya.Box(int((x-wcol/2)/DBU), int(ystrip[0]/DBU),
                                   int((x+wcol/2)/DBU), int(ystrip[1]/DBU)))
        empty = (strip & occ).is_empty()
        if empty and run0 is None: run0 = x
        if (not empty) and run0 is not None:
            if x-step-run0 >= wcol: clear.append((run0, x-step)); run0 = None
            else: run0 = None
        x += step
    if run0 is not None and xmax-run0 >= wcol: clear.append((run0, xmax))
    return clear

def clear_bands(xspan, layer, ymin, ymax, step=1.0, wband=0.5):
    """y ranges where `layer` does not occupy the horizontal strip across xspan."""
    occ = FLAT[layer]
    clear = []
    y = ymin; run0 = None
    while y <= ymax:
        strip = pya.Region(pya.Box(int(xspan[0]/DBU), int((y-wband/2)/DBU),
                                   int(xspan[1]/DBU), int((y+wband/2)/DBU)))
        empty = (strip & occ).is_empty()
        if empty and run0 is None: run0 = y
        if (not empty) and run0 is not None:
            clear.append((run0, y-step)); run0 = None
        y += step
    if run0 is not None: clear.append((run0, ymax))
    return clear

# --- (b) clear vertical columns through the top-block row + band (y 175..287.5) ---
print("\n=== (b) clear vertical columns (clear of M2 AND M3), y[175,287.5], x[0,472] ===")
cols = clear_columns((175.0, 287.5), ["M2", "M3"], 0.0, 472.0, step=1.0, wcol=0.6)
for x0, x1 in cols:
    print("   x[%.1f, %.1f]  width %.1f um" % (x0, x1, x1-x0))
if not cols: print("   (none >= 0.6 um)")

# --- (c) clear horizontal bands across full width, per layer ---
print("\n=== (c) clear horizontal bands across x[0,472], per layer (y[0,300]) ===")
for lname in ["M2", "M3", "M4", "M5"]:
    bands = clear_bands((0.0, 472.0), lname, 0.0, 300.0, step=1.0, wband=0.6)
    wide = [(y0, y1) for y0, y1 in bands if y1-y0 >= 3.0]
    print("  %s clear bands (>=3um tall):" % lname)
    for y0, y1 in wide:
        print("     y[%.1f, %.1f]  height %.1f" % (y0, y1, y1-y0))
    if not wide: print("     (none >= 3um)")
