#!/usr/bin/env python3
# pin_landings.py -- the landing geometry of EVERY pin, from the organizer's DEF, plus the
# gap test that says whether a drop at the nominal slot centre would touch metal.
#
# WHY THIS EXISTS. Building the I/Q quad turned up that a 0.4 um drop at the N02 slot CENTRE
# (x167.50) lands between the 4th and 5th pin finger and touches NOTHING. That is DRC-clean
# (nothing to space against), LVS-clean (the net still reaches its label), and dead on silicon.
# Same failure family as the silent short: the check that would catch it is not the one being
# run. It is not a quad problem -- it applies to every pin not yet landed.
#
# Reads padframe/A01/project_defs/BH/A01_BH_interface.yaml (committed). Writes nothing.
# Run in-container:  python3 team_src/magic/analysis/pin_landings.py
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml -- run this in the container, not on the Windows host")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("PADFRAME_ROOT",
                      os.path.join(HERE, "..", "..", "..", "padframe", "A01", "project_defs_13pin"))
DBU = 200.0
SLOT_PITCH = 100.0          # um, north slots


def load(variant="BH"):
    with open(os.path.join(ROOT, variant, "A01_%s_interface.yaml" % variant)) as f:
        return yaml.safe_load(f)


def main():
    d = load()
    print("=== A01_BH pin landing geometry (from the committed DEF, 12-pin issue) ===")
    print("%-12s %-5s %-10s %3s  %-17s %-9s %s"
          % ("pin", "slot", "cell", "n", "finger w x h (um)", "pitch", "row extent (um)"))
    rows = []
    for p in d["pins"]:
        r = [q["translated_user"] for q in p["rectangles"]]
        xs = sorted((q[0] / DBU, q[2] / DBU) for q in r)
        ys = sorted((q[1] / DBU, q[3] / DBU) for q in r)
        w = (r[0][2] - r[0][0]) / DBU
        h = (r[0][3] - r[0][1]) / DBU
        north = p["padring_instance"].startswith("N")
        spans = xs if north else ys
        pitch = (spans[1][0] - spans[0][0]) if len(spans) > 1 else 0.0
        lo, hi = spans[0][0], spans[-1][1]
        cell = p["cell"].split("__")[1]
        rows.append((p["user_pin_name"], p["project_pin"], p["padring_instance"], cell,
                     len(r), w, h, pitch, lo, hi, north, spans))
        print("%-12s %-5s %-10s %3d  %6.3f x %6.3f    %6.3f    %s %.2f-%.2f"
              % (p["project_pin"], p["padring_instance"], cell, len(r), w, h, pitch,
                 "x" if north else "y", lo, hi))

    print()
    print("=== THE GAP TEST: does a drop at the nominal slot centre touch a finger? ===")
    for (name, proj, slot, cell, n, w, h, pitch, lo, hi, north, spans) in rows:
        centre = (lo + hi) / 2.0
        on = any(a - 1e-9 <= centre <= b + 1e-9 for a, b in spans)
        if on:
            print("  %-12s centre %s=%8.3f  ON a finger" % (proj, "x" if north else "y", centre))
        else:
            g = [(b, a2) for (a, b), (a2, b2) in zip(spans, spans[1:]) if b < centre < a2]
            gap = (g[0][1] - g[0][0]) if g else 0.0
            print("  %-12s centre %s=%8.3f  *** IN A GAP *** (%.3f um wide, %.3f-%.3f) -- a bare "
                  "drop here touches NOTHING"
                  % (proj, "x" if north else "y", centre, gap, g[0][0], g[0][1]))

    print()
    print("=== LANDING RULE PER CELL TYPE ===")
    print("  asig_5p0  8 fingers x 2.54 um, pitch 5.68 (one 5.16 um gap dead centre)")
    print("            -> ONE BAR across the whole row, centre +/- 22.16 um. 10 pins.")
    print("  dvss/dvdd 6 fingers x 9.50 um (one 3.28 um gap dead centre)")
    print("            -> ONE BAR across the whole row, centre +/- 36.14 um. 3 pins.")
    print("  in_c      1 finger x 0.38 um, THREE separate pins (Y, PU, PD) in one slot")
    print("            -> NO row to bar across. Precision landing on a single 0.38 um shape,")
    print("               and a 0.4 um wire centred 0.2 um off misses it entirely.")

    print()
    print("=== 13-PIN REGENERATION: predicted, NOT from a DEF (VSSD not yet issued) ===")
    print("  N01-N05 (CP_OUT + the four I/Q) and W18-W22 do NOT move.")
    print("  VSSD  -> N06  dvss  6 x 9.50   x531.36-603.64  (takes VDDD's present slot geometry)")
    print("  VDDD  -> N07  dvdd  6 x 9.50   x631.36-703.64  (+%.0f um)" % SLOT_PITCH)
    print("  REF_IN-> N08  in_c  Y x733.76-734.14 | PD x794.29-794.67 | PU x798.65-799.03 (+%.0f)"
          % SLOT_PITCH)
    print("  Verify all six numbers against the regenerated DEF before landing any of them.")


if __name__ == "__main__":
    main()
