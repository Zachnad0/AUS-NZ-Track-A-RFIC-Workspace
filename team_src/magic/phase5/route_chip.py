#!/usr/bin/env python3
# route_chip.py -- add top-level power/signal metal to the PLACED chip_top.gds, write it back.
# Run AFTER chip_merge.py. Iterate: chip_merge -> route_chip -> run_drc / verify_cp / chip_conn.
#
# GND needs NO routing: every block's VSS and vco.GND already extract as VSUBS (substrate) --
# a chip-wide common with no pad. So power routing is just VDDA and VDDD.
#
# LAYER DISCIPLINE (silent-short fix): horizontal buses on M5; vertical risers on M4; a riser
# vias to M5 ONLY at its own target bus. An M5 riser is allowed ONLY inside a verified M5-clear
# corridor AND only where no other M5 bus shares its x (so it crosses only its target bus).
import pya, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_lib as R

GDS = "/foss/designs/AUS-NZ-integration/gds/chip_top.gds"
ly = pya.Layout(); ly.read(GDS)
chip = ly.cell("chip_top")
if chip is None:
    raise SystemExit("chip_top not found")

# --- GND ring (M5, 15um) in a 20um margin around the die. Electrically GND is already the
#     substrate common (VSUBS), but that is a HIGH-impedance return for ~26mA across 472um;
#     the ring is a low-Z metal backbone. Channel-budget: the band cannot hold GND15+VDDD12+
#     VDDA3, so GND rides the perimeter margin (top blocks tap up, DIV2 taps down, ibias left).
GY_BOT, GY_TOP, GX_L, GX_R, RW = -10.0, 280.0, -10.0, 482.0, 15.0
R.hwire(chip, ly, 5, GX_L - RW/2, GX_R + RW/2, GY_BOT, w=RW)   # bottom
R.hwire(chip, ly, 5, GX_L - RW/2, GX_R + RW/2, GY_TOP, w=RW)   # top
R.vwire(chip, ly, 5, GY_BOT, GY_TOP, GX_L, w=RW)              # left
R.vwire(chip, ly, 5, GY_BOT, GY_TOP, GX_R, w=RW)              # right

def gnd_tap(tx, ty, tm, direction, w):
    """tap a VSS extent point, escape to M4, run to the M5 GND ring, via4 up onto it."""
    R.via_stack(chip, ly, tm, 4, tx, ty)
    if direction == "down":
        R.vwire(chip, ly, 4, ty, GY_BOT, tx, w=w); R.via1_at(chip, ly, 4, 5, tx, GY_BOT)
    elif direction == "up":
        R.vwire(chip, ly, 4, ty, GY_TOP, tx, w=w); R.via1_at(chip, ly, 4, 5, tx, GY_TOP)
    elif direction == "left":
        R.hwire(chip, ly, 4, tx, GX_L, ty, w=w); R.via1_at(chip, ly, 4, 5, GX_L, ty)
    elif direction == "right":
        R.hwire(chip, ly, 4, tx, GX_R, ty, w=w); R.via1_at(chip, ly, 4, 5, GX_R, ty)

# accessible taps (VSS extents from vss_extent.py), strap sized ~1mA/um for the block's share:
gnd_tap(120.0, 8.0, 2, "down", 23.0)    # DIV2.VSS (22.4 mA) -> bottom ring
gnd_tap(2.0, 209.5, 2, "left", 2.0)     # ibias.VSS (1 mA) reaches x0.7 -> left ring
gnd_tap(233.0, 262.0, 4, "up", 2.0)     # PFD.VSS (0.5 mA) -> top ring

# --- buses in the clear y[180,205] band (M5), EM-sized ---
BUS = {"VDDA": 199.0, "VDDD": 188.0}
BUS_W = {"VDDA": 3.0, "VDDD": 12.0}
BUS_X = {"VDDA": (60.0, 405.0), "VDDD": (150.0, 236.0)}
for net, y in BUS.items():
    x1, x2 = BUS_X[net]
    R.hwire(chip, ly, 5, x1, x2, y, w=BUS_W[net])

# --- ABOVE-band drops: port -> via stack to M4 -> M4 riser DOWN to bus -> via4 to M5 bus ---
DROPS = [
    ("VDDA", 219.48, 231.61, 2, 2.0),   # CP.VDD  M2
    ("VDDA", 74.16, 231.60, 2, 2.0),    # ibias.VDD M2
    ("VDDD", 229.68, 256.76, 4, 2.0),   # PFD.VDD  M4
]
for net, x, y, m, w in DROPS:
    yb = BUS[net]
    R.via_stack(chip, ly, m, 4, x, y)
    R.vwire(chip, ly, 4, y, yb, x, w=w)
    R.via1_at(chip, ly, 4, 5, x, yb)

# --- BELOW-band corridor taps: tap net at an accessible extent point, ride an M5-CLEAR column
#     up to the bus. (tap_x,tap_y,tap_metal, corridor_x, jog_metal, bus, riser_w) ---
def corridor_tap(tx, ty, tm, cx, jm, net, w):
    yb = BUS[net]
    R.via_stack(chip, ly, tm, jm, tx, ty)          # escape to jog layer
    if abs(cx - tx) > 0.01:
        R.hwire(chip, ly, jm, tx, cx, ty, w=w)     # jog to the corridor x on jog layer
    R.via_stack(chip, ly, jm, 5, cx, ty)           # up to M5 in the corridor
    R.vwire(chip, ly, 5, ty, yb, cx, w=w)          # M5 riser up the clear column to the bus

# DIV2.VDD: tap ON its M4 collector wire (x108-183 @ y137.5); x160 is an M5-clear column.
# CLEAN: extraction shows DIV2.VDD merges into VDDD (PFD+DIV2), no side effects.
corridor_tap(160.0, 137.5, 4, 160.0, 4, "VDDD", 2.0)
# vco.VDD: DEFERRED. The ONLY M5-riser-able column over vco is x[388,394] (OUT_p/OUT_n M5 fill
# x[396,472]; spiral fills x<=366). But vco.VDD's M2 there is a 1.5um wire interleaved with
# other-net active M2 at ~0.14um, so a via pad lands 0.14um off it (M2.2a) and does not merge --
# no clean tap without reopening vco (its VDD has no wider/edge-accessible reach). vco.VDD ISS
# ride to VDDA needs a vco-internal supply pin. Flag for Greg. VDDA stays CP+ibias (2/3).
# R.via_stack(chip, ly, 2, 5, 392.5, 74.3); R.vwire(chip, ly, 5, 74.3, 199.0, 392.5, w=2.0)

# --- die-edge port labels (rung 4c). A top-level label needs top-level metal to land on:
#     paint a small patch on the port's centerline (overlaps the block port -> connects) and
#     drop a text on the metal LABEL datatype (10) so magic reads it as a chip_top port. ---
def port_label(name, x, y, m, patch=True):
    if patch:
        p = 0.30
        R.box(chip, ly, R.METAL[m], x - p, y - p, x + p, y + p)
    lyr = ly.layer(R.METAL[m][0], 10)
    chip.shapes(lyr).insert(pya.DText(name, pya.DTrans(pya.DVector(x, y))))

# VDDA/VDDD land on their own M5 buses (already top-level metal -> no patch).
port_label("VDDA", 200.0, BUS["VDDA"], 5, patch=False)
port_label("VDDD", 180.0, BUS["VDDD"], 5, patch=False)
# block ports: patch on the port centerline (chip coords, port_map.py) + label.
PORT_LABELS = [
    ("IBIAS",  71.30, 223.90, 2),   # ibias.IBIAS
    ("VTUNE",  358.68, 66.70, 1),   # vco.TUNE
    ("ISS",    395.84, 60.33, 2),   # vco.ISS
    ("CP_OUT", 272.25, 215.41, 4),  # CP.CP_OUT
    ("I_P",    235.18, 140.27, 1),  # DIV2.I_P
    ("I_N",    2.18, 140.27, 1),    # DIV2.I_N
    ("Q_P",    235.18, 51.92, 1),   # DIV2.Q_P
    ("Q_N",    2.18, 51.92, 1),     # DIV2.Q_N
    ("REF_IN", 210.28, 257.60, 3),  # PFD.REF
]
for name, x, y, m in PORT_LABELS:
    port_label(name, x, y, m)

# --- signals (rung 4b). H hops on M4, V risers on M3 (crossing-safe). ---
# UP (PFD.UP<->CP.UP): CONNECTS (extracted PFD.UP=CP.UP at tap (246,268), OUT distinct), but
# PFD's UP/DOWN are 0.28um std-cell pins at 0.28um PITCH; the minimum via pad is 0.26+2*0.06 =
# 0.38um (V1.3d enclosure floor), leaving only 0.23um to the neighbour DOWN pin < the 0.28um
# M2.2a limit. A top-down via cannot be DRC-clean on these pins without reopening PFD -- same for
# DOWN and FB (all PFD digital pins). Flag for Greg: PFD needs chip-level pin escapes, or a
# waivered 0.23um spacing on these taps. Analog signals (VGP/VGN/IB_DIV2) are the tractable next.
#   Verified route shape: via(2,4)@(246,268); M4 -> x282.25; via(3,4); M3 -> CP.UP.

ly.write(GDS)
print("routed power + GND ring + 11 labels (UP defeated by 0.28um PFD pin pitch); wrote %s" % GDS)
