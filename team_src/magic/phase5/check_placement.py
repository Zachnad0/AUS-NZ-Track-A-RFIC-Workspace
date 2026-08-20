#!/usr/bin/env python3
# check_placement.py -- guard against drift between the two chip_top placement artifacts:
#   * chip_merge.py  (KLayout) -- builds the DELIVERABLE gds/chip_top.gds; its BLOCKS table
#     gives each block's target BBOX-LL in um.
#   * chip_top.tcl   (magic)   -- the placement RECORD + magic-DRC gate; its `box values X Y`
#     getcell lines place each block's MAG-bbox-LL at (X/200, Y/200) um.
# For DIV2/ibias/CP/PFD the .mag bbox == the golden GDS bbox, so box-position == real LL.
# vco_v1 is placed in magic via its ABSTRACT .mag (bbox 66x125) whose LL sits +67um (13400iu)
# right of the real 182x179.5 footprint LL, so chip_top.tcl deliberately offsets vco's box by
# +13400iu. The checker subtracts that KNOWN offset and then every block's reconciled real LL
# must equal chip_merge.py's target. Any other divergence -> FAIL LOUDLY (exit 1).
import re, sys

HERE = "/foss/designs/AUS-NZ-integration/team_src/magic/phase5"
TOL = 0.01  # um

# Known mag-abstract -> real-footprint LL offset (um), applied to the chip_top.tcl box position.
MAG_REAL_OFFSET = {"vco_v1": (67.0, 0.0)}  # 13400 iu / 200 = 67 um in x; documented in chip_top.tcl

# --- parse chip_merge.py BLOCKS: ("name", tx, ty, blx, bly) -> target LL (tx,ty) ---
merge = {}
with open("%s/chip_merge.py" % HERE) as f:
    src = f.read()
for m in re.finditer(r'\(\s*"(\w+)"\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)', src):
    name, tx, ty = m.group(1), float(m.group(2)), float(m.group(3))
    merge[name] = (tx, ty)

# --- parse chip_top.tcl getcell lines: box values X Y X Y ; getcell NAME ---
mag = {}
with open("%s/chip_top.tcl" % HERE) as f:
    for line in f:
        m = re.search(r'box values\s+(-?\d+)\s+(-?\d+)\s+-?\d+\s+-?\d+\s*;\s*getcell\s+(\w+)', line)
        if m:
            x_iu, y_iu, name = int(m.group(1)), int(m.group(2)), m.group(3)
            mag[name] = (x_iu / 200.0, y_iu / 200.0)

blocks = sorted(set(merge) | set(mag))
fail = False
print("%-16s %-18s %-18s %-18s %s" % ("block", "merge_target_LL", "mag_box_pos", "mag_real_LL", "status"))
for b in blocks:
    if b not in merge or b not in mag:
        print("%-16s MISSING in %s" % (b, "chip_top.tcl" if b not in mag else "chip_merge.py")); fail = True; continue
    tx, ty = merge[b]
    mx, my = mag[b]
    ox, oy = MAG_REAL_OFFSET.get(b, (0.0, 0.0))
    rx, ry = mx - ox, my - oy
    ok = abs(rx - tx) <= TOL and abs(ry - ty) <= TOL
    fail = fail or not ok
    print("%-16s (%7.2f,%7.2f)   (%7.2f,%7.2f)   (%7.2f,%7.2f)   %s"
          % (b, tx, ty, mx, my, rx, ry, "OK" if ok else "*** DRIFT ***"))

if fail:
    print("\nPLACEMENT DRIFT DETECTED -- chip_top.mag and chip_merge.py disagree. FIX before trusting the GDS.")
    sys.exit(1)
print("\nPLACEMENT CONSISTENT -- chip_top.mag placement record matches chip_merge.py deliverable.")
