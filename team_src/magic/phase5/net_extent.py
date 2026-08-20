#!/usr/bin/env python3
# net_extent.py -- for the "interior" power ports, find the FULL metal shape the port label
# sits on (+ same-layer shapes touching it), its bbox, and where it comes closest to the block
# boundary. Also dump the per-block M5 occupancy map (clear corridors). Coords: chip = local +
# origin.  origin: DIV2(65,105) vco(402,119.48) ibias(7.66,209.10) CP(237.25,228.01) PFD(210,245)
import gdspy
GDS = "/foss/designs/AUS-NZ-integration/gds"
ORIG = {"DIV2_QUAD_v1": (65.0, 105.0), "vco_v1": (402.0, 119.48),
        "ibias_gen_v1": (7.66, 209.10), "CP_v1": (237.25, 228.01), "PFD_lib": (210.0, 245.0)}
LNAME = {34: "M1", 36: "M2", 42: "M3", 46: "M4", 81: "M5"}
LNUM = {v: k for k, v in LNAME.items()}

def bbox(poly):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)

def overlaps(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])

def net_shapes(top, layer, seed_pt, tol=0.05):
    """polygons on `layer` connected (bbox-touching transitive) to the one under seed_pt."""
    polys = [p for p in top.get_polygons(by_spec=True).get((layer, 0), [])]
    bbs = [bbox(p) for p in polys]
    seed = [i for i, bb in enumerate(bbs)
            if bb[0]-tol <= seed_pt[0] <= bb[2]+tol and bb[1]-tol <= seed_pt[1] <= bb[3]+tol]
    if not seed:
        return []
    grp = set(seed); changed = True
    while changed:
        changed = False
        for i, bb in enumerate(bbs):
            if i in grp:
                continue
            gi = [bbs[j] for j in grp]
            if any(overlaps((bb[0]-tol, bb[1]-tol, bb[2]+tol, bb[3]+tol), g) for g in gi):
                grp.add(i); changed = True
    return [bbs[i] for i in grp]

# ---- target "interior" nets: (block, netname, label_layer, label_local_x, label_local_y) ----
TARGETS = [
    ("DIV2_QUAD_v1", "VDD", "M4", 25.0, 19.0),
    ("DIV2_QUAD_v1", "VSS", "M2", 88.0, -26.3),
    ("vco_v1", "VDD", "M2", -4.57, -44.65),
    ("vco_v1", "GND", "M1", -43.50, -69.70),
    ("vco_v1", "ISS", "M2", -6.17, -59.15),
]
for blk, net, lyr, lx, ly_ in TARGETS:
    lib = gdspy.GdsLibrary(infile="%s/%s.gds" % (GDS, blk)); top = lib.top_level()[0]
    ox, oy = ORIG[blk]
    bb = top.get_bounding_box()
    blx, bly, bux, buy = bb[0][0], bb[0][1], bb[1][0], bb[1][1]
    shapes = net_shapes(top, LNUM[lyr], (lx, ly_))
    if not shapes:
        print("%s.%s (%s): NO shape under label -- check coords" % (blk, net, lyr)); continue
    nx0 = min(s[0] for s in shapes); ny0 = min(s[1] for s in shapes)
    nx1 = max(s[2] for s in shapes); ny1 = max(s[3] for s in shapes)
    # closest approach of the net metal to each block edge
    dL = nx0 - blx; dR = bux - nx1; dB = ny0 - bly; dT = buy - ny1
    near = min([("left", dL), ("right", dR), ("bottom", dB), ("top", dT)], key=lambda t: t[1])
    print("%s.%s on %s: %d shape(s), net bbox local x[%.1f,%.1f] y[%.1f,%.1f] "
          "chip x[%.1f,%.1f] y[%.1f,%.1f]" % (blk, net, lyr, len(shapes),
          nx0, nx1, ny0, ny1, nx0+ox, nx1+ox, ny0+oy, ny1+oy))
    print("    closest to block %s edge: %.2f um  (edges L=%.1f R=%.1f B=%.1f T=%.1f)"
          % (near[0], near[1], dL, dR, dB, dT))

print("\n==== M5 (layer 81) occupancy per block (local bboxes) ====")
for blk in ["DIV2_QUAD_v1", "vco_v1", "ibias_gen_v1", "CP_v1", "PFD_lib"]:
    lib = gdspy.GdsLibrary(infile="%s/%s.gds" % (GDS, blk)); top = lib.top_level()[0]
    ox, oy = ORIG[blk]
    m5 = top.get_polygons(by_spec=True).get((81, 0), [])
    bbs = [bbox(p) for p in m5]
    print("%s: %d M5 shapes" % (blk, len(bbs)))
    for b in sorted(bbs, key=lambda t: (t[0], t[1]))[:12]:
        print("    chip x[%.1f,%.1f] y[%.1f,%.1f] (w=%.1f h=%.1f)"
              % (b[0]+ox, b[2]+ox, b[1]+oy, b[3]+oy, b[2]-b[0], b[3]-b[1]))
