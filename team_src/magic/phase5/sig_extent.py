#!/usr/bin/env python3
# sig_extent.py -- full metal extent + closest-block-edge for each inter-block SIGNAL terminal,
# so signal routing can tap at an accessible point (same method that de-risked the power nets).
import gdspy
GDS = "/foss/designs/AUS-NZ-integration/gds"
ORIG = {"DIV2_QUAD_v1": (65.0, 105.0), "vco_v1": (402.0, 119.48),
        "ibias_gen_v1": (7.66, 209.10), "CP_v1": (237.25, 228.01), "PFD_lib": (210.0, 245.0)}
LNUM = {"M1": 34, "M2": 36, "M3": 42, "M4": 46, "M5": 81}

def bbox(p):
    xs = [q[0] for q in p]; ys = [q[1] for q in p]; return min(xs), min(ys), max(xs), max(ys)
def overlaps(a, b, t):
    return not (a[2]+t < b[0] or b[2]+t < a[0] or a[3]+t < b[1] or b[3]+t < a[1])
def net_shapes(top, layer, seed, tol=0.05):
    polys = top.get_polygons(by_spec=True).get((layer, 0), [])
    bbs = [bbox(p) for p in polys]
    grp = set(i for i, b in enumerate(bbs)
              if b[0]-tol <= seed[0] <= b[2]+tol and b[1]-tol <= seed[1] <= b[3]+tol)
    ch = True
    while ch:
        ch = False
        for i, b in enumerate(bbs):
            if i in grp: continue
            if any(overlaps(b, bbs[j], tol) for j in grp):
                grp.add(i); ch = True
    return [bbs[i] for i in grp]

# (net, block, layer, local_label_x, local_label_y)
SIG = [
    ("VGP", "ibias_gen_v1", "M2", 41.22, 13.00), ("VGP", "CP_v1", "M2", -26.75, 0.60),
    ("VGN", "ibias_gen_v1", "M2", 74.26, 59.50), ("VGN", "CP_v1", "M2", -6.50, -17.40),
    ("IB_DIV2", "ibias_gen_v1", "M2", 108.62, 59.50), ("IB_DIV2", "DIV2_QUAD_v1", "M2", 77.25, -12.70),
    ("UP", "PFD_lib", "M2", 36.12, 23.72), ("UP", "CP_v1", "M3", 45.00, -7.50),
    ("DOWN", "PFD_lib", "M2", 37.24, 23.72), ("DOWN", "CP_v1", "M2", 34.41, -13.20),
    ("FB", "PFD_lib", "M2", 20.44, 0.28), ("I_P", "DIV2_QUAD_v1", "M1", 170.18, 35.27),
    ("CK", "DIV2_QUAD_v1", "M2", 0.0, 4.80), ("OUT_p", "vco_v1", "M5", -4.0, -25.0),
    ("CKB", "DIV2_QUAD_v1", "M2", 65.0, 4.80), ("OUT_n", "vco_v1", "M5", -0.2, -25.0),
]
cache = {}
for net, blk, lyr, lx, ly_ in SIG:
    if blk not in cache:
        cache[blk] = gdspy.GdsLibrary(infile="%s/%s.gds" % (GDS, blk)).top_level()[0]
    top = cache[blk]; ox, oy = ORIG[blk]
    bb = top.get_bounding_box(); blx, bly, bux, buy = bb[0][0], bb[0][1], bb[1][0], bb[1][1]
    sh = net_shapes(top, LNUM[lyr], (lx, ly_))
    if not sh:
        print("%-8s %-13s %s: NO shape under label" % (net, blk, lyr)); continue
    nx0 = min(s[0] for s in sh); ny0 = min(s[1] for s in sh)
    nx1 = max(s[2] for s in sh); ny1 = max(s[3] for s in sh)
    edges = {"L": nx0-blx, "R": bux-nx1, "B": ny0-bly, "T": buy-ny1}
    near = min(edges, key=edges.get)
    print("%-8s %-13s %s: %2d sh  chip x[%.1f,%.1f] y[%.1f,%.1f]  nearest %s edge %.1fum"
          % (net, blk, lyr, len(sh), nx0+ox, nx1+ox, ny0+oy, ny1+oy, near, edges[near]))
