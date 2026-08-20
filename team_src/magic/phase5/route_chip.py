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
# VSSA/VSSD ground pads on the GND ring (M5, already metal). Two PADS, ONE net (shared
# p-substrate; separates bond-wire L, not the net). Bailey 2026-08-20: pair power with ground.
port_label("VSSA", 200.0, GY_BOT, 5, patch=False)   # quiet analog ground (bottom ring)
port_label("VSSD", 200.0, GY_TOP, 5, patch=False)   # digital ground (top ring)
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

# --- signals (rung 4b). SAME-LAYER ESCAPE: extend a pin along its OWN axis out of the block
#     (min width, no via pad, so neighbour spacing stays as-drawn), then via up in open space.
#     Signals M2/M3, power M4/M5, never crossing a same-layer power riser. ---
# UP: PFD.UP M2 pin x[245.4,247.5] (vertical) -> escape UP into the y270.3-272.5 gap (above PFD,
#     below the GND ring); CP.UP M3 pin x282 -> escape UP into the y233-245 CP/PFD gap.
UPX = 246.12                                       # PFD.UP label x (DOWN is at 247.24)
R.vwire(chip, ly, 2, 268.0, 271.0, UPX, w=0.3)     # narrow M2 stub up out of PFD (clear of DOWN)
R.via_stack(chip, ly, 2, 4, UPX, 271.0)            # via up in the open gap (no neighbour here)
R.hwire(chip, ly, 4, UPX, 282.25, 271.0, w=0.6)    # M4 across to x282.25 (right of PFD, clear of risers)
R.vwire(chip, ly, 4, 271.0, 238.0, 282.25, w=0.6)  # M4 down (same net -> its own L corner)
R.via_stack(chip, ly, 3, 4, 282.25, 238.0)         # to M3 at the CP.UP escape (above CP, open)
R.vwire(chip, ly, 3, 238.0, 228.0, 282.25, w=0.28) # extend CP.UP M3 (x282.11-282.39 pin) down onto it

# DOWN: PFD.DOWN M2 pin (label x247.24) up-escape; CP.DOWN M2 (x270-273 @ y214.8) extend RIGHT
# along its own axis into the CP<->vco gap (x283.5-290, free), then rise. M4 riser at x285.
DNX = 247.24
R.vwire(chip, ly, 2, 268.0, 272.0, DNX, w=0.3)     # PFD.DOWN M2 stub up out of PFD (clear of UP)
R.via_stack(chip, ly, 2, 4, DNX, 272.0)
R.hwire(chip, ly, 4, DNX, 285.0, 272.0, w=0.6)     # M4 across at y272 (0.4um clear of UP's y271 M4)
R.vwire(chip, ly, 4, 272.0, 214.8, 285.0, w=0.6)   # M4 down in the CP<->vco gap
R.via_stack(chip, ly, 2, 4, 285.0, 214.8)          # to M2 at the CP.DOWN escape (open gap)
R.hwire(chip, ly, 2, 273.3, 285.0, 214.8, w=0.28)  # extend CP.DOWN M2 right onto the escape

# FB: PFD.FB M2 (230.44,245, PFD bottom edge) -> DIV2.I_P M1 (235.18,140, DIV2 right edge) =
# the I_P net (I_P pad is labelled there). Down the x287 column (right of CP) into the DIV2/vco
# channel. M4 for the long vertical run (power-free column).
R.vwire(chip, ly, 2, 245.3, 240.0, 230.44, w=0.3)  # PFD.FB M2 down out of PFD into the gap
R.hwire(chip, ly, 2, 230.44, 232.5, 240.0, w=0.3)  # jog right in the gap, clear of PFD.VDD's M4 riser@229.68
R.via_stack(chip, ly, 2, 4, 232.5, 240.0)
R.hwire(chip, ly, 4, 232.5, 287.0, 240.0, w=0.6)   # M4 across (above CP) to x287
R.vwire(chip, ly, 4, 240.0, 140.0, 287.0, w=0.6)   # M4 down the CP-right / DIV2-vco channel
R.hwire(chip, ly, 4, 287.0, 235.5, 140.27, w=0.6)  # M4 left, OVER the DIV2 x237 VDD guard (M4 vs M1)
R.via_stack(chip, ly, 1, 4, 235.5, 140.27)         # down onto DIV2.I_P M1 (x235.5, before the guard)

# VGP/VGN/IB_DIV2 (analog signals): DEFERRED. The pins are wide (tappable), but ibias.VGP/VGN
# sit INTERIOR to ibias (x48.9 / x82, ~140um from the right edge), so any run to CP crosses
# ibias's dense internal metal (M2 92 / M3 30 / M4 7). Signal H-hops also must avoid the power
# M4 risers and M5 buses (a first VGP cut on M4 shorted to VDDA by crossing ibias.VDD's riser).
# That leaves only M3 over ibias, which its own M3 defeats. Needs channel-only routing with the
# ibias pins escaped to an edge, or block pin escapes -- a dedicated pass. (LAYER PLAN for it:
# power M4/M5, signals M2/M3, route in Band C x189-210 / the y180-205 band, never over a block.)

# VGP: ibias.VGP M2 (x44.9-52.9 @ y222) via up the CLEAR M4 column at x48 to the top margin,
# across, down Band C (x189-210, free) to CP.VGP (x210-262 @ y224-233). No block edit -- the
# M3/M4 column above VGP is clear to the ibias top edge.
R.via_stack(chip, ly, 2, 4, 48.9, 222.1)          # VGP tap up to M4 (no M2 neighbour within 1um)
R.vwire(chip, ly, 4, 222.1, 271.0, 48.9, w=0.6)   # M4 up the clear column, out the ibias top
R.hwire(chip, ly, 4, 48.9, 200.0, 271.0, w=0.6)   # M4 across the top margin to Band C
R.vwire(chip, ly, 4, 271.0, 228.0, 200.0, w=0.6)  # M4 down Band C to CP.VGP's vertical-wire y
R.hwire(chip, ly, 4, 200.0, 205.0, 228.0, w=0.6)  # M4 right into Band C, clear of CP
R.via_stack(chip, ly, 2, 4, 205.0, 228.0)         # down to M2 in Band C (open)
R.hwire(chip, ly, 2, 205.0, 210.5, 228.0, w=0.28)  # extend CP.VGP left-edge vertical (x210.5) left,
#                                                     y228 clear of the CP.VDD M2 rail @ y231.6

# VGN: ibias.VGN M2 (x77.9-85.9 @ y268.6, top edge) via up, DOWN the CLEAR M4 column at x81.92
# into the band, across the band (y200, clear full width), up to CP.VGN bottom (x230.6-234.9 @ y206.3).
R.via_stack(chip, ly, 2, 4, 81.92, 268.6)         # ibias.VGN up to M4 (8um pin, no M2 neighbour)
R.vwire(chip, ly, 4, 268.6, 183.0, 81.92, w=0.6)  # M4 down the clear column to y183 (BELOW the
#                                                    y188 VDDD / y199 VDDA buses + their M4 risers)
R.hwire(chip, ly, 4, 81.92, 232.0, 183.0, w=0.6)  # M4 across at y183, clear of the power risers
R.via_stack(chip, ly, 2, 4, 232.0, 183.0)         # down to M2 (x232 is right of the risers)
R.vwire(chip, ly, 2, 183.0, 206.5, 232.0, w=0.28) # M2 up (crosses the M5 buses on a diff layer) to CP.VGN

# IB_DIV2: DIV2.IBIAS M3 (x142.2, reaches y142.78; column clear above) extend UP out of DIV2 to
# the band; ibias.IB_DIV2 (x96.8-148.5 @ y268.5 top edge) down the clear M4 column; join at y183.
R.vwire(chip, ly, 3, 142.78, 186.0, 142.2, w=0.28)  # extend DIV2.IBIAS M3 up the clear column into band
R.via_stack(chip, ly, 3, 4, 142.2, 186.0)           # to M4 in the band
R.via_stack(chip, ly, 2, 4, 120.0, 268.5)           # ibias.IB_DIV2 up to M4 (wide pin)
R.vwire(chip, ly, 4, 268.5, 186.0, 120.0, w=0.6)    # M4 down the clear column into the band
R.hwire(chip, ly, 4, 120.0, 142.2, 186.0, w=0.6)    # M4 across at y186 (clear of VGN's y183, below y188 bus)

# --- 0/0 boundary at the true die extent (Bailey: determines size + available-block budget) ---
bb = chip.dbbox()
chip.shapes(ly.layer(0, 0)).insert(pya.DBox(bb.left, bb.bottom, bb.right, bb.top))
print("die boundary (0/0): (%.2f,%.2f)-(%.2f,%.2f)  %.1f x %.1f um"
      % (bb.left, bb.bottom, bb.right, bb.top, bb.width(), bb.height()))

ly.write(GDS)
print("routed power + GND ring + 13 labels + boundary; wrote %s" % GDS)
