import yaml, sys, os

DBU = 200.0  # padframe dbu per micron (5 nm)

def edge_of(slot):
    return {"W": "west", "N": "north", "E": "east", "S": "south"}.get(slot[0], "?")

def load(variant):
    # The package is committed at padframe/A01/project_defs/ (2026-08-22). It used to be
    # read from a /tmp working dir, which is why it was lost once. PADFRAME_ROOT overrides.
    root = os.environ.get("PADFRAME_ROOT",
                          os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "..", "..", "..", "padframe", "A01", "project_defs_13pin"))
    p = os.path.join(root, variant, "A01_%s_interface.yaml" % variant)
    with open(p) as f:
        return yaml.safe_load(f)

for variant in ("BV", "BH"):
    d = load(variant)
    print("=" * 100)
    print("VARIANT %s  size=%sx%s um  origin_um=%s  diearea_dbu=%s  vss_fixed=%s  usable_area=%s"
          % (variant, d["size_microns"][0], d["size_microns"][1], d["origin_microns"],
             d["diearea_dbu"], d["vss_fixed"], d.get("usable_area")))
    print("%-8s %-10s %-4s %-6s %-26s %-7s %-7s %-6s  %s"
          % ("pin", "proj_pin", "slot", "term", "cell", "dir", "use", "edge", "translated_user bbox (um): x0,y0 - x1,y1"))
    allx0 = allx1 = ally0 = ally1 = None
    edgexy = {}  # edge -> list of (x0,y0,x1,y1) um
    for pin in d["pins"]:
        rects = pin["rectangles"]
        xs0 = min(r["translated_user"][0] for r in rects) / DBU
        ys0 = min(r["translated_user"][1] for r in rects) / DBU
        xs1 = max(r["translated_user"][2] for r in rects) / DBU
        ys1 = max(r["translated_user"][3] for r in rects) / DBU
        e = edge_of(pin["padring_instance"])
        print("%-8s %-10s %-4s %-6s %-26s %-7s %-7s %-6s  %8.2f,%8.2f - %8.2f,%8.2f"
              % (pin["user_pin_name"], pin["project_pin"], pin["padring_instance"],
                 pin["cell_terminal"], pin["cell"], pin["direction"], pin["use"], e,
                 xs0, ys0, xs1, ys1))
        allx0 = xs0 if allx0 is None else min(allx0, xs0)
        ally0 = ys0 if ally0 is None else min(ally0, ys0)
        allx1 = xs1 if allx1 is None else max(allx1, xs1)
        ally1 = ys1 if ally1 is None else max(ally1, ys1)
        edgexy.setdefault(e, []).append((xs0, ys0, xs1, ys1))
    print("  ALL-PIN bbox (um): x[%.2f, %.2f]  y[%.2f, %.2f]" % (allx0, allx1, ally0, ally1))
    for e, lst in edgexy.items():
        ex0 = min(r[0] for r in lst); ex1 = max(r[2] for r in lst)
        ey0 = min(r[1] for r in lst); ey1 = max(r[3] for r in lst)
        print("    edge %-6s: %d pins, x[%.2f, %.2f] y[%.2f, %.2f]" % (e, len(lst), ex0, ex1, ey0, ey1))
    # shortfall vs chip_top 522 x 309 (placed at project LL 0,0)
    if variant == "BV":
        print("  chip_top height 309 um; most distant pin top y=%.2f um -> reach shortfall = %.2f um" % (ally1, ally1 - 309.0))
        print("  lowest pin bottom y=%.2f um (chip_top top edge at 309)" % ally0)
    else:
        print("  chip_top width 522 um; most distant pin right x=%.2f um -> reach shortfall = %.2f um" % (allx1, allx1 - 522.0))
        print("  leftmost pin left x=%.2f um" % allx0)
