#!/usr/bin/env python3
# route_chip.py -- add top-level metal routing to the PLACED chip_top.gds and write it back.
# Run AFTER chip_merge.py (which places the 5 blocks verbatim). Iterate:
#   chip_merge.py  ->  route_chip.py  ->  run_drc.py / verify_cp.sh chip_top
#
# Strategy (see docs/phase7-routing-plan.md): the band y in [180,205] is clear of ALL block
# geometry across the full die width -> put M5 power buses there. Blocks above the band
# (ibias/CP/PFD: y>=205) expose power on M2/M4 and use M5 sparsely (0-4 polys), so a short
# M5 drop from the port down to the bus is reachable. Blocks below the band (DIV2/vco:
# y<179.5) bury their power/clock ports in dense metal -> handled separately / flagged.
import pya, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_lib as R

GDS = "/foss/designs/AUS-NZ-integration/gds/chip_top.gds"

ly = pya.Layout()
ly.read(GDS)
chip = ly.cell("chip_top")
if chip is None:
    raise SystemExit("chip_top not found in %s" % GDS)

# --- power buses in the clear band (M5), full needed width ---
BUS = {"VDDA": 184.0, "GND": 191.0, "VDDD": 198.0}
BUS_W = {"VDDA": 2.0, "GND": 3.0, "VDDD": 2.0}
BUS_X = {"VDDA": (60.0, 405.0), "GND": (60.0, 245.0), "VDDD": (95.0, 235.0)}
for net, y in BUS.items():
    x1, x2 = BUS_X[net]
    R.hwire(chip, ly, 5, x1, x2, y, w=BUS_W[net])

# --- reachable terminals: (net, chip_x, chip_y, term_metal) ; all ABOVE the band ---
# drop = via stack term_metal->M5 at the port, then vertical M5 down to the bus, joined by
# the bus itself. Each drop crosses its own block on M5 only (sparse) between y_bus and y_port.
DROPS = [
    ("VDDA", 219.48, 231.61, 2),   # CP.VDD  M2
    ("VDDA", 74.16, 231.60, 2),    # ibias.VDD M2
    ("VDDD", 229.68, 256.76, 4),   # PFD.VDD  M4
    ("GND",  237.25, 213.61, 2),   # CP.VSS  M2
    ("GND",  89.62, 206.10, 2),    # ibias.VSS M2
    ("GND",  232.98, 256.76, 4),   # PFD.VSS  M4
]
# LAYER DISCIPLINE (silent-short fix): buses are M5 (horizontal), risers are M4 (vertical).
# An M4 riser crossing a NON-target M5 bus does not short (different layer); it vias up to M5
# ONLY at its own target bus. (A previous cut ran risers on M5 and silently merged GND into
# VDDD where a riser crossed a bus -- DRC-legal, LVS-fatal.)
for net, x, y, m in DROPS:
    ybus = BUS[net]
    R.via_stack(chip, ly, m, 4, x, y)          # escape port up to M4
    R.vwire(chip, ly, 4, y, ybus, x, w=1.0)    # M4 riser down to the bus level
    R.via1_at(chip, ly, 4, 5, x, ybus)         # via4 up to the M5 bus ONLY here
    x1, x2 = BUS_X[net]
    if not (x1 <= x <= x2):
        R.hwire(chip, ly, 5, min(x, x1), max(x, x2), ybus, w=BUS_W[net])

ly.write(GDS)
print("routed power (buses + %d drops); wrote %s" % (len(DROPS), GDS))
