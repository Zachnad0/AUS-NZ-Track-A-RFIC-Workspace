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
BUS_X = {"VDDA": (60.0, 405.0), "VDDD": (55.0, 236.0)}  # VDDD extended left to feed the DIV2 comb
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

# DIV2.VDD MULTI-POINT tap (EM, item 2): DIV2's VDD are thin 0.28um M4 collectors; a single via
# funnels all 22.4mA -> 80 mA/um. Instead inject at MANY clear M4 columns (3um pitch) so each
# collector segment carries only its local ~3um-span current (~0.28mA -> ~1 mA/um). Each tap: M4
# riser from the collector up its clear column to the VDDD bus, via4 onto the bus.
DIV2_VDD_TAPS = ([(x, 137.5) for x in range(113, 183, 3)]     # y137.5 collector (x108-183): 24 cols
                 + [(x, 124.0) for x in range(60, 106, 3)])   # y124 collector (x60-108): 16 cols
#                (x108-110 junction taps dropped -- they abut the collector edge = M4.2a)
for tx, ty in DIV2_VDD_TAPS:
    R.vwire(chip, ly, 4, ty, 178.0, float(tx), w=0.4)         # M4 riser collector -> y178 (BELOW the
    R.via1_at(chip, ly, 4, 5, float(tx), 178.0)               #   OUT M4 lanes at y181/184). w0.4: 0.56mA
    R.vwire(chip, ly, 5, 178.0, BUS["VDDD"], float(tx), w=0.44)  # riser = 1.4 mA/um -- a 57x cut vs the
    #  old single 0.28um collector (80 mA/um); widening to 0.6 tripped one M4.2a. M5 up to the bus,
    #  crossing the OUT M4 lanes on a DIFFERENT layer.
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
# GND ring port label. GROUND is ONE electrical net (shared p-substrate), so LVS carries ONE
# ground port = VSSA (bottom ring). The SECOND ground PAD, VSSD (info.yaml pad #11, Bailey's
# power/ground pairing), bonds to the SAME ring at the top edge ~ (200, GY_TOP) -- a second bond
# point, not a second net (separates only bond-wire L). It is not a distinct LVS port; giving it
# its own label would create a netgen port error against the one-net golden. (A1b -> ask Bailey.)
port_label("VSSA", 200.0, GY_BOT, 5, patch=False)   # the ground port (bottom ring)
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
R.via_stack(chip, ly, 2, 3, 232.5, 240.0)          # -> M3 (whole FB run is M3 here, so it crosses
R.hwire(chip, ly, 3, 232.5, 287.0, 240.0, w=0.6)   #   the UP/DOWN M4 verticals @x282/285 and the
R.vwire(chip, ly, 3, 240.0, 140.0, 287.0, w=0.6)   #   VCO_OUT M4 band lanes on a DIFFERENT layer)
R.via_stack(chip, ly, 3, 4, 287.0, 140.0)          # to M4 for the guard crossing
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

# vco.VDD: M2 wire x390-410. Via up at x405 (M3 column clear y76-179; OUT_p/n M5 and the M4 bar
# are on OTHER layers) and rise M3 straight to the VDDA bus at its x405 right end.
R.via_stack(chip, ly, 2, 3, 405.0, 74.85)         # vco.VDD M2 -> M3
R.vwire(chip, ly, 3, 74.85, 199.0, 405.0, w=0.4)  # M3 up the clear column to the VDDA bus y
R.via_stack(chip, ly, 3, 5, 405.0, 199.0)         # to M5 onto the VDDA bus (BUS_X VDDA ends at 405)

# VCO_OUTP/N: the 337um differential pair. OUT_p/n leads at y94.5 escape UP on their M3 columns
# (x401.8 / x398 clear y95-179; spiral is M5, the underpass bar is M4) to the band, M4 across to
# the DIV2 CK/CKB M3 columns (x65 / x130 clear), down onto CK/CKB. Lanes y181 (OUT_p) / y184 (OUT_n).
for outnet, xv, xd, ylane in [("OUT_p", 401.8, 65.0, 181.0), ("OUT_n", 398.0, 130.0, 184.0)]:
    R.via_stack(chip, ly, 3, 5, xv, 94.5)             # tap the OUT lead (M5) -> M3
    R.vwire(chip, ly, 3, 94.5, ylane, xv, w=0.4)      # M3 up the clear vco column into the band
    R.via_stack(chip, ly, 3, 4, xv, ylane)            # -> M4 for the long band crossing
    if outnet == "OUT_n":
        # LENGTH-MATCH (item 3): OUT_n's path is 431.5um vs OUT_p's 494.3um -- 62.8um (12.7%) short.
        # Add a ~64um M4 notch UP into the clear right margin: east of the VDDA bus (ends x405),
        # west of the die edge (x423). All M4, same net; it crosses only the vco.VDD M3 column at
        # x405 and OUT_p's M3 up-column at x401.8, both on a DIFFERENT layer (no short). The down
        # leg at x398 stacks over OUT_n's own M3 column (same net). New OUT_n ~= 495.5um (Delta 0.2%).
        R.hwire(chip, ly, 4, xv, 416.0, ylane, w=0.4)      # east  y184: 398 -> 416  (+18)
        R.vwire(chip, ly, 4, ylane, 198.0, 416.0, w=0.4)   # up    x416: 184 -> 198  (+14, 1um below VDDA)
        R.hwire(chip, ly, 4, 398.0, 416.0, 198.0, w=0.4)   # west  y198: 416 -> 398  (+18)
        R.vwire(chip, ly, 4, 198.0, ylane, 398.0, w=0.4)   # down  x398: 198 -> 184  (+14)
    R.hwire(chip, ly, 4, xd, xv, ylane, w=0.4)        # M4 across the band (below the y188 bus) to DIV2
    R.via_stack(chip, ly, 3, 4, xd, ylane)            # -> M3 at the DIV2 CK/CKB column
    R.vwire(chip, ly, 3, ylane, 110.0, xd, w=0.4)     # M3 down the clear DIV2 column
    R.via_stack(chip, ly, 2, 3, xd, 109.8)            # -> M2 onto DIV2.CK / CKB

# --- PHASE 8 (a): the matched I/Q quad to the north pads -------------------------------------
# Ported from analysis/phase8_incontext.py, whose five-part in-context gate this geometry
# already passed (plan doc 3l). CORE coordinates here: everything below the frame step is
# core-frame, and the seat translates it. die = core + 200 on both axes.
#
# Escapes are NOT arbitrary -- each one fixes a specific silent short that DRC could not see:
#   * all four escape on M3 VIA-AT-THE-PIN (escl 3). An M1 escape hwire out of Q_N/I_N hits
#     DIV2's M1 frame (M1.2a), and out of I_P/Q_P it runs east across the ib_conv_v1
#     a_8764_6964# bias node and SHORTS the output to it -- invisible to DRC (an overlap
#     leaves no spacing gap) and invisible to a routes-only extract (3l).
#   * the left risers run WEST-TO-EAST (Q_N's riser west of I_N's) so neither escape sweeps
#     across the other's riser. That overlap is DRC-clean and merged I_N into Q_N (3i).
#   * I_P carries novia: its pin is already a full M1-via1-M2-via2-M3-via3-M4 stack, so adding
#     our own via1/via2 trips V1.2a/V2.2a against the pin's. The M3 route lands on the pin's
#     existing M3 instead. Q_N/I_N/Q_P pins are M1-only and take the via stack.
#   * I_P low-jog into the west column, Q_P high-jog into the east column, so no lane crosses
#     a riser (M3.2a).
# JOB B: I_P is OFF the pin list (docs/verification.md 8.10 -- its pad's 875 fF through
# XR_SER_IP's 1 kohm collapses the PFD feedback clock to 11 % swing). DIV2.I_P still reaches
# PFD.FB through the dedicated chip-level FB route above, so only the PAD haul goes.
# Q_P moves N05 -> N04, i.e. onto I_P's old pad x. Every other I/Q pad is unchanged.
IQ_TAP  = {"Q_N": (2.18, 51.92), "I_N": (2.18, 140.27), "Q_P": (235.18, 51.92)}
IQ_PAD  = {"Q_N": -32.5, "I_N": 67.5, "Q_P": 167.5}                 # core x of N02..N04 centres
IQ_PADY = 349.0                                                     # core y of the north pin row
IQ_PLAN = {
    "Q_N": dict(esc=-3.6, jog=None,           lane=290.0),
    "I_N": dict(esc=-2.3, jog=None,           lane=300.0),
    # JOB B: Q_P now lands on I_P's old pad (N05 -> N04), so its lane runs x167.5 -> jog_x.
    # With the jog left at 200.0 that lane SPANS core x192, where CP_OUT's M3 riser threads
    # "between I_P's lane and Q_P's" -- and Q_P merged into CP_OUT (LVS: XCP_v1_0 ... Q_P ...,
    # CP_OUT absent from the port list). Q_P inherits I_P's jog x for the same reason it
    # inherited its pad: the column at x185 is exactly the one I_P vacated.
    "Q_P": dict(esc=+17.0, jog=(185.0, 198.0), lane=316.0),
}

def iq_pts(net, ser_extra):
    tx, ty = IQ_TAP[net]; px = IQ_PAD[net]; pl = IQ_PLAN[net]
    ex = tx + pl["esc"]
    pts = [(tx, ty), (ex, ty)]                       # escape on M3, from the via at the pin
    if pl["jog"] is None:
        pts += [(ex, pl["lane"])]
    else:
        jx, jy = pl["jog"]
        pts += [(ex, jy), (jx, jy), (jx, pl["lane"])]
    if ser_extra > 1e-6:
        pts += R.meander_points(pts[-1][0], px, pl["lane"], ser_extra, 0.4, 3, amp=6.0)[1:]
    else:
        pts += [(px, pl["lane"])]
    return pts

def iq_len(net, ser_extra):
    return R.path_length(iq_pts(net, ser_extra)) + abs(IQ_PADY - IQ_PLAN[net]["lane"])

iq_base = {n: iq_len(n, 0.0) for n in IQ_PAD}
IQ_TARGET = max(iq_base.values())
print("IQ base lengths (core frame): %s" % {n: round(iq_base[n], 2) for n in IQ_PAD})
print("IQ matched target %.3f um (set by %s)" % (IQ_TARGET, max(iq_base, key=iq_base.get)))

iq_final = {}
for net in IQ_PAD:
    tx, ty = IQ_TAP[net]; px = IQ_PAD[net]; pl = IQ_PLAN[net]
    pts = iq_pts(net, IQ_TARGET - iq_base[net])
    if not pl.get("novia"):
        R.via_stack(chip, ly, 1, 3, tx, ty)          # M1-only pin -> M3 AT the tap
    R.route_path(chip, ly, 3, pts, w=0.4)            # M3 haul + matching serpentine
    R.via_stack(chip, ly, 2, 3, px, pl["lane"])      # down to M2 for the pad drop
    R.vwire(chip, ly, 2, pl["lane"], IQ_PADY, px, w=0.4)
    # Land on the DEF pin FINGERS, not on the slot centre. Each asig_5p0 pin is 8 separate
    # 2.54 um Metal2 fingers spanning +/-22.16 um about the slot centre (plan doc 1e); the
    # centre itself falls in a GAP between fingers, so a bare 0.4 um drop would touch nothing.
    # One M2 bar across the whole finger row ties all 8 -- they are the same pin.
    R.box(chip, ly, (36, 0), px - 22.16, IQ_PADY, px + 22.16, IQ_PADY + 1.0)
    chip.shapes(ly.layer(36, 10)).insert(pya.DText(net, pya.DTrans(pya.DVector(px, IQ_PADY + 0.5))))
    iq_final[net] = R.path_length(pts) + abs(IQ_PADY - pl["lane"])
    print("  %-4s core tap (%7.2f,%7.2f) -> pad x%7.2f  lane %5.1f  len %8.3f um"
          % (net, tx, ty, px, pl["lane"], iq_final[net]))
err = max(iq_final.values()) - min(iq_final.values())
print("IQ matched: all four %.3f um, spread %.4f um" % (IQ_TARGET, err))
assert err < 1e-3, "I/Q length matching broke: spread %.4f um" % err

# --- PHASE 8 (b): VSSA -- extend the GND ring west to the W18 pad ----------------------------
# CORE coords (die = core + 200). The ring's own bottom segment already reaches core x-25, so
# the spur starts there and is the SAME net -- the one intended same-layer touch in the
# allocation. M5 the whole way (40 mohm/sq, the chip's entire ~26 mA ground returns here),
# dropping to M2 only for the pad itself, because the pin rectangles are Metal2.
# The pad landing is a BAR across the whole finger column, not a drop at the slot centre:
# W18 is 6 dvss fingers x 9.5 um spanning die y46.36-118.64, and the centre y82.500 sits in a
# 3.28 um GAP between fingers 3 and 4 (plan doc 3s). A centre drop touches nothing, DRC-clean
# and LVS-clean.
VSSA_Y   = -10.0        # core y of the ring bottom centreline (die 190)
VSSA_XW  = -80.0        # core x where the spur turns south (die 120)
VSSA_YP  = -117.5       # core y of the pad approach (die 82.5)
VSSA_XV  = -184.0       # core x of the M5->M2 via (die 16)
R.hwire(chip, ly, 5, -25.0, VSSA_XW, VSSA_Y,  w=15.0)          # ring bottom -> west
R.vwire(chip, ly, 5, VSSA_YP, VSSA_Y, VSSA_XW, w=15.0)         # south to the pad row
R.hwire(chip, ly, 5, VSSA_XV, VSSA_XW, VSSA_YP, w=9.5)         # west to the via column
# One M2 PLATE from the via column out to the die edge, covering the whole finger column.
# NOT an hwire + a separate bar: R.hwire extends half its width past each endpoint, so an
# hwire ending at core x-199.5 (die 0.5) reached die -4.25 -- outside the DIEAREA.
R.via_stack(chip, ly, 2, 5, VSSA_XV - 2.0, VSSA_YP)            # via INSIDE the plate (x<XV)
R.box(chip, ly, (36, 0), -200.0, -153.64, VSSA_XV, -81.36)     # die x0-16, y46.36-118.64
chip.shapes(ly.layer(36, 10)).insert(pya.DText("VSSA", pya.DTrans(pya.DVector(-199.5, VSSA_YP))))
print("(b) VSSA: ring spur %.1f um M5 + %.1f um M2 to the W18 finger bar (die y46.36-118.64)"
      % (abs(-25.0 - VSSA_XW) + abs(VSSA_Y - VSSA_YP) + abs(VSSA_XW - VSSA_XV), abs(VSSA_XV + 199.5)))

# --- PHASE 8 (c): VTUNE -- route (a), out of the core SOUTH and round through free die -------
# CORE coords. Plan doc 3n: 3m called this "boxed", which was true only while chip_top was
# 522 x 309. Seated, the DIV2<->vco gap (die x437.36-490, 52.6 um) is open all the way down and
# the die south of y178.5 and west of x175 is empty. The route crosses NOTHING but the GND ring
# on M5, and M3-vs-M5 has no spacing rule.
# The tap sits INSIDE the varactor comp ring, so it escapes by via UP at the gate pad, never
# laterally on M1 -- a lateral M1 escape shorts the ring to VSSA.
# The riser is held at core x-190 (die 10), NOT at the pad column: the west pin rectangles all
# sit at die x[0,1], so a riser run up the pad column would short VTUNE to IBIAS, ISS, VDDA and
# VSSA on the way past (plan doc 3o).
VT_TAP  = (358.68, 66.70)      # die (558.68, 266.70), M1
VT_PTS  = [VT_TAP, (265.0, 66.70), (265.0, -35.0), (-190.0, -35.0), (-190.0, 282.5)]
R.via_stack(chip, ly, 1, 3, VT_TAP[0], VT_TAP[1])              # M1 -> M3 AT the gate pad
R.route_path(chip, ly, 3, VT_PTS, w=0.4)
R.via_stack(chip, ly, 2, 3, -190.0, 282.5)
R.box(chip, ly, (36, 0), -200.0, 260.34, -186.0, 304.66)       # W22 finger-column plate
chip.shapes(ly.layer(36, 10)).insert(pya.DText("VTUNE", pya.DTrans(pya.DVector(-199.5, 282.5))))
print("(c) VTUNE: %.2f um M3, crossings = GND ring M5 only" % R.path_length(VT_PTS))

# --- PHASE 8 (d): VDDA on M4, IBIAS on M3 with an M4 hop -------------------------------------
# VDDA leaves its own M5 bus and goes west on M4, NOT M5: the GND ring's left segment is M5 at
# die x182.50-197.50 spanning the full height, so an M5 run west at die y399 would short VDDA to
# GND. Measured, not assumed (plan doc 3o).
# The VDDA M5 bus spans die x258.5-606.5 (core 58.5-406.5). 3o said to tap it at die x256 --
# which is 2.5 um WEST of the bus end, so the via landed on nothing and the whole VDDA haul
# extracted as a disconnected node (VDDA_uq0). Tap at core x60 (die 260), inside the bus.
R.via_stack(chip, ly, 4, 5, 60.0, 199.0)                       # onto the VDDA M5 bus, die (260,399)
R.hwire(chip, ly, 4, -154.0, 60.0, 199.0, w=3.0)               # west across the ring on M4
R.vwire(chip, ly, 4, 5.0, 199.0, -154.0, w=3.0)                # south to the pad row
# MSLOT.1 caps metal at 30 um wide without slotting, and it is measured in BOTH axes. A plate
# spanning the 72.28 um finger column AND reaching the via at core x-154 would be 48 x 72.28
# and violates. KLayout signoff caught it; magic did not. Plate stays 18 um wide and a 3 um
# feeder reaches the via.
R.via_stack(chip, ly, 2, 4, -154.0, 5.0)
R.hwire(chip, ly, 2, -184.0, -154.0, 5.0, w=3.0)               # feeder, plate -> via
R.box(chip, ly, (36, 0), -200.0, -53.64, -182.0, 18.64)        # W19 finger-column plate, 18 um
chip.shapes(ly.layer(36, 10)).insert(pya.DText("VDDA", pya.DTrans(pya.DVector(-199.5, 5.0))))
print("(d) VDDA: %.2f um M4 west+down, crosses the GND ring left segment on M4" % (210.0 + 194.0))

# IBIAS escapes on M3 at its OWN tap y (die 423.90): that line carries M2 x11, M1 x2, M4 x1,
# M5 x3 westward but NO M3, so an M3 escape crosses only other layers. The cleaner-looking
# die y450 line is NOT M3-clear -- layer-specific clearance decides, not total clutter.
# The escape must then cross the Q_N (die x198.58) and I_N (die x199.88) M3 risers: IBIAS's tap
# is east of them and its pad is west, so no re-route avoids it. M4 is clear at die x193-206,
# so it hops M3 -> M4 -> M3 across that span. Found by analysis/lane_conflicts.py BEFORE this
# metal existed, as two 0.40 x 0.40 um M3-on-M3 overlaps.
IB_TAP = (71.30, 223.90)       # die (271.30, 423.90), M2
R.via_stack(chip, ly, 2, 3, IB_TAP[0], IB_TAP[1])              # M2 pin -> M3 at the tap
R.hwire(chip, ly, 3, 4.0, IB_TAP[0], IB_TAP[1], w=0.4)         # M3 west to die x204
R.via_stack(chip, ly, 3, 4, 4.0, IB_TAP[1])
R.hwire(chip, ly, 4, -7.0, 4.0, IB_TAP[1], w=0.4)              # M4 hop over the two quad risers
R.via_stack(chip, ly, 3, 4, -7.0, IB_TAP[1])
# RUNG 3 CUT: this M3 used to run unbroken from the block tap to the pad riser. The secondary
# ESD ballast resistor goes IN SERIES in it, so the run is split into a TAP-side piece and a
# PAD-side piece and the gap (die x40.0-58.5, under esd_rpoly) is bridged through the resistor.
# Leaving it unbroken would short the ballast out. DRC-clean -- but NOT LVS-clean: TESTED
# 2026-08-25 by re-painting the bridge and re-running the gate. The resistor extracts as
# `Xesd_rpoly_0 IBIAS IBIAS VSSA` (both terminals on one node), the chip net count drops
# 20 -> 19, and netgen reports "Final result: Top level cell failed pin matching". So gate 4
# DOES see a shorted-out ballast. An earlier version of this comment claimed otherwise; it was
# wrong and is retracted. This is an ordinary visible defect, not a docs 8.8/8.9 blindness.
# RUNG 3 (IBIAS RELOCATION): THE SERIES CUT MOVED TO THE PAD END. It used to sit here, a gap
# at die x40.0-58.5 in this haul, because the clamp was up at y440-464 -- which left 141 um of
# 0.4 um M3 riser BETWEEN the pad and the ballast, carrying the full pre-ballast current. With
# the clamp relocated into the W20 pin band the ballast belongs between the PAD PLATE and the
# clamp, so this haul runs UNBROKEN from the block tap down to the riser bottom again.
#
# The break is now the ABSENCE of the old M2 feeder: the pad plate no longer touches the riser
# at all. Its only path to the core is through esd_rpoly and the clamp node, painted after the
# seat. Re-adding a feeder here would short the ballast out -- and gate 4 DOES catch that
# (tested 2026-08-25: resistor extracts with both terminals on IBIAS, net count 20 -> 19,
# "Top level cell failed pin matching").
R.route_path(chip, ly, 3, [(-7.0, IB_TAP[1]), (-166.0, IB_TAP[1]), (-166.0, 82.5)], w=0.4)
R.box(chip, ly, (36, 0), -200.0, 60.34, -182.0, 104.66)        # W20 finger-column plate, 18 um
chip.shapes(ly.layer(36, 10)).insert(pya.DText("IBIAS", pya.DTrans(pya.DVector(-199.5, 82.5))))
print("(d) IBIAS: %.2f um, M4 hop x193-204 over the Q_N/I_N risers"
      % (IB_TAP[0] - 4.0 + 11.0 + (4.0 + 166.0 - 7.0) + (IB_TAP[1] - 82.5)))

# --- PHASE 8 (e): ISS -- the VCO TAIL RETURN, so a bus, not a signal thread ------------------
# ISS is the common source of the cross-coupled nfet pair (golden: XM1/XM4 "OUT_p OUT_n ISS
# GND"), i.e. the tail node, carrying 1.24-1.57 mA DC plus the 2f0 component -- NOT a bias
# reference. At 0.4 um the ~876 um haul would be 191 ohm and drop 300 mV. Built per Greg's
# option A: >=10 um M5, ~3.4 ohm, ~5 mV. The ~876 pH of added tail inductance is recorded as a
# characterized limitation whose SIGN IS UNESTABLISHED -- there is no PSS/HB in the open flow.
# M4 wherever it must cross M5: the gap descent crosses the GND ring band, and the west run
# crosses VSSA's own M5 descent. VSSA goes left-and-down while ISS goes left-and-up, so on one
# layer they must cross exactly once; no spatial separation avoids it (plan doc 3q).
# The escape is 5.0 um centred core y61.8 (die 261.8), NOT 8.0 um centred on the strap. There
# is an OTHER-NET M2 rail 1.16 um below the strap -- die y258.69-258.97, x587.10-612.77 -- and
# an 8 um bus centred on the strap spans die y256.33-264.33, straight through it. That merged
# ISS into the chip ground: LVS went 21 nets -> 20 and netgen showed the layout's ISS net
# carrying PFD_lib/VSS, vco_v1/GND, ibias/VSS, DIV2/VSS and CP/VSS. DRC-clean, because a merge
# leaves no gap to space against. The 5 um bus sits between that rail (0.33 um clearance) and
# the next M2 north at die y266.12 (1.79 um), still overlaps the strap at y260.13-260.53, and
# at 0.314 mA/um is two decades inside the EM limit.
# EM WIDEN of the vco_v1 ISS strap, done at TOP LEVEL rather than by editing vco_v1.
# The strap is 0.40 um M2 carrying up to 1.57 mA = 3.93 mA/um, against a DRM 14.2
# unidirectional limit of 2.09 / 1.00 / 0.67 mA/um at 85 / 110 / 125 C -- over at every
# temperature. Painting M2 over it at chip level merges with it on the same layer and widens
# the same conductor, which is electrically identical to editing the cell but does NOT touch
# gds/vco_v1.gds, so vco_v1 keeps its sign-off and chip_top.drcbase needs no re-baseline.
# Window measured first: nearest other-net M2 is y258.97 below and y266.12 above, and there
# are ZERO via2 in the window; the 12 via1 at y260.20-260.46 are ISS's own and stay covered.
# 3.0 um -> 0.523 mA/um: 4.0x margin at 85 C, 1.91x at 110 C, 1.28x at 125 C.
R.box(chip, ly, (36, 0), 387.04, 59.9, 412.83, 62.9)           # die x587.04-612.83, 3.0 um
R.hwire(chip, ly, 2, 290.0, 387.04, 61.8, w=5.0)               # M2 escape west out of the vco
R.via_stack(chip, ly, 2, 4, 290.0, 61.8)
R.hwire(chip, ly, 4, 255.0, 290.0, 61.8, w=10.0)               # into the DIV2<->vco gap
R.vwire(chip, ly, 4, -60.0, 61.8, 255.0, w=10.0)               # descent -- M4 THROUGH the ring
R.via_stack(chip, ly, 4, 5, 255.0, -60.0)
# R.hwire EXTENDS HALF ITS WIDTH past each endpoint. At w=10 that is 5 um, so an M5 lane
# nominally ending at die x130 actually reaches x125 -- inside VSSA's M5 descent at die
# x112.5-127.5 -- and merges ISS into the whole ground ring. DRC-clean (a merge leaves no gap
# to space against); caught by the LVS port/net count, 21 nets -> 20. The M5 ends are pulled
# back so the EXTENDED ends clear VSSA's descent by >=0.3 um on both sides: east M5 stops at
# die x135 (reaches 130), west M5 starts at die x105 (reaches 110), M4 spans 135 -> 105.
R.hwire(chip, ly, 5, -65.0, 255.0, -60.0, w=10.0)              # south lane, die y135-145
R.via_stack(chip, ly, 4, 5, -65.0, -60.0)
R.hwire(chip, ly, 4, -95.0, -65.0, -60.0, w=10.0)              # hop over VSSA's M5 descent
R.via_stack(chip, ly, 4, 5, -95.0, -60.0)
R.hwire(chip, ly, 5, -110.0, -95.0, -60.0, w=10.0)
R.vwire(chip, ly, 5, -60.0, 182.5, -110.0, w=10.0)             # riser, die x85-95
R.hwire(chip, ly, 5, -186.0, -110.0, 182.5, w=10.0)
R.via_stack(chip, ly, 2, 5, -186.0, 182.5)
R.box(chip, ly, (36, 0), -200.0, 160.34, -182.0, 204.66)       # W21 finger-column plate
chip.shapes(ly.layer(36, 10)).insert(pya.DText("ISS", pya.DTrans(pya.DVector(-199.5, 182.5))))
print("(e) ISS: %.2f um bus (M2 8um / M4 10um / M5 10um), one M4 hop over VSSA's descent"
      % (97.04 + 35.0 + 120.33 + 325.0 + 20.0 + 20.0 + 242.5 + 76.0))

# --- PHASE 8 (f): VSSD, VDDD, REF_IN and the PU/PD ties -------------------------------------
# Built against the 13-PIN DEF (padframe/A01/project_defs_13pin/), whose slot map was verified
# first: VSSD N06, VDDD N07, REF_IN N08, and BRK_BEFORE_N06 reason additional_power_ground_set
# firing before VSSD's slot -- not VDDD's. All coordinates measured off that DEF.
# CORE coords throughout (die = core + 200).

# VSSD -- N06, die x531.36-603.64. Taken from the GND ring TOP segment (M5, die y472.5-487.5)
# directly beneath the pad. That ring top is where PFD.VSS already lands via route_chip's own
# gnd_tap(233,262,4,"up"), so this IS the digital VSS, reached by the shortest path; it is not
# a spur off the analog VSSA side of the ring. On-chip VSSA and VSSD are one node (shared
# p-substrate, no deep nwell); the padring break isolates the RAILS, so what VSSD buys is a
# local bond for the digital island's return, which is exactly what a short vertical gives.
R.via_stack(chip, ly, 4, 5, 267.5, 280.0)                      # onto the ring top, die (567.5,480)
R.vwire(chip, ly, 4, 280.0, 347.0, 267.5, w=3.0)               # M4 riser, die y480 -> 547
R.via_stack(chip, ly, 2, 4, 267.5, 347.0)
R.vwire(chip, ly, 2, 347.0, 348.0, 267.5, w=3.0)   # w=3 extends 1.5: must not pass die y550
R.box(chip, ly, (36, 0), 231.36, 349.0, 303.64, 350.0)         # N06 finger-row bar, 72.28 x 1.0
# VSSD text on 36/0, NOT 36/10. The magic tech maps `calma 36 10 -> labels allm2 port` and
# `calma 36 0 -> labels allm2 noport`, so a text on /0 is a label magic never promotes to a
# port. VSSA and VSSD are ONE electrical net, magic emits ONE name for it, and on /10 it was
# picking VSSD -- which broke pin matching against a golden whose ground port is VSSA. On /0
# the VSSD text is still in the GDS (Bailey's top_cell_text scrape reports each text with its
# layer and datatype) but never competes for the port name.
chip.shapes(ly.layer(36, 0)).insert(pya.DText("VSSD", pya.DTrans(pya.DVector(267.5, 349.5))))

# VDDD -- N07, die x631.36-703.64, off the M5 VDDD bus (die x249-442, y382-394).
# Tapped at die x408, INSIDE the bus -- 3o's "tap at x256" for VDDA was 2.5 um outside its bus
# and produced a floating node, so every bus tap here is measured against the bus extent.
# The rise column die x408 is the ibias(<=381.76) / CP(>=410) gap and carries NO M4 (measured).
# The east lane at die y505 must cross VSSD's M4 riser at die x567.5 -- same layer, different
# net -- so it hops to M5 for 30 um. M5 is free there, above the ring top at die y487.5.
R.via_stack(chip, ly, 4, 5, 208.0, 188.0)                      # onto the VDDD bus, die (408,388)
R.vwire(chip, ly, 4, 188.0, 305.0, 208.0, w=3.0)               # M4 riser, die y388 -> 505
R.hwire(chip, ly, 4, 208.0, 260.0, 305.0, w=3.0)
R.via_stack(chip, ly, 4, 5, 260.0, 305.0)
R.hwire(chip, ly, 5, 260.0, 275.0, 305.0, w=3.0)               # M5 hop over VSSD's M4 riser
R.via_stack(chip, ly, 4, 5, 275.0, 305.0)
R.hwire(chip, ly, 4, 275.0, 367.0, 305.0, w=3.0)
R.vwire(chip, ly, 4, 305.0, 347.0, 367.0, w=3.0)               # M4 riser, die x667
R.via_stack(chip, ly, 2, 4, 367.0, 347.0)
R.vwire(chip, ly, 2, 347.0, 348.0, 367.0, w=3.0)   # ditto
R.box(chip, ly, (36, 0), 331.36, 349.0, 403.64, 350.0)         # N07 finger-row bar
chip.shapes(ly.layer(36, 10)).insert(pya.DText("VDDD", pya.DTrans(pya.DVector(367.0, 349.5))))

# REF_IN -- N08 in_c. THREE separate pins in one slot, ONE 0.38 um finger each, no row to bar
# across (plan doc 3s): Y die x733.76-734.14, PD x794.29-794.67, PU x798.655-799.035. Each is
# landed on its OWN measured finger; a 0.4 um wire centred 0.2 um off misses entirely while
# looking perfectly routed.
# Y comes from PFD.REF, die (410.28,457.60) on M3, which sits on PFD's west edge (x410), so it
# escapes WEST into the ibias/PFD gap rather than crossing the block.
R.hwire(chip, ly, 3, 205.0, 210.28, 257.6, w=0.4)              # escape west out of PFD
R.vwire(chip, ly, 3, 257.6, 305.0, 205.0, w=0.4)               # north, crossing the ring on M3
R.hwire(chip, ly, 3, 205.0, 434.0, 305.0, w=0.4)               # east at die y505 (measured clear)
R.vwire(chip, ly, 3, 305.0, 348.5, 434.0, w=0.4)
R.via_stack(chip, ly, 2, 3, 434.0, 348.5)
# The box must reach DOWN to the via2 M2 pad (die y548.25-548.75), not start at the finger
# edge: at y349.0 (die 549.0) it cleared the pad by 0.25 um and REF_IN extracted as two
# disconnected labels (REF_IN + REF_IN_uq0). Same landing-miss family as VSSA_uq0/VDDA_uq0.
R.box(chip, ly, (36, 0), 433.5, 348.3, 434.4, 350.0)           # lands ON the Y finger
chip.shapes(ly.layer(36, 10)).insert(pya.DText("REF_IN", pya.DTrans(pya.DVector(433.95, 349.5))))

# PU/PD: decided 2026-08-21 and confirmed against the PDK truth table -- PU=0, PD=1 = weak
# pull-down, so REF_IN parks at a clean logic 0 when the bench clock is disconnected. Both
# terminals MUST be driven; a floating CMOS control gate is not acceptable.
#   PD -> VDDD   PU -> VSSD (the DIGITAL island's ground, NOT VSSA)
# Both ties run on M2 so they cross REF_IN's M3 riser and each other's risers on other layers.
R.box(chip, ly, (36, 0), 494.0, 349.0, 494.96, 350.0)          # lands ON the PD finger
R.vwire(chip, ly, 2, 340.0, 349.0, 494.48, w=1.0)
R.hwire(chip, ly, 2, 367.0, 494.48, 340.0, w=1.0)              # west to VDDD's riser
R.via_stack(chip, ly, 2, 4, 367.0, 340.0)                      # joins VDDD -- same net
chip.shapes(ly.layer(36, 10)).insert(pya.DText("REF_IN_PD", pya.DTrans(pya.DVector(494.48, 349.5))))

R.box(chip, ly, (36, 0), 498.4, 349.0, 499.3, 350.0)           # lands ON the PU finger
R.vwire(chip, ly, 2, 328.0, 349.0, 498.845, w=1.0)
R.hwire(chip, ly, 2, 267.5, 498.845, 328.0, w=1.0)             # west to VSSD's riser
R.via_stack(chip, ly, 2, 4, 267.5, 328.0)                      # joins VSSD -- same net
chip.shapes(ly.layer(36, 10)).insert(pya.DText("REF_IN_PU", pya.DTrans(pya.DVector(498.845, 349.5))))
print("(f) VSSD/VDDD/REF_IN + PU->VSSD, PD->VDDD landed on the 13-pin DEF fingers")

# --- PHASE 8 (g): CP_OUT to N01 ---------------------------------------------------------------
# The last declared pin. Found MISSING by analysis/landing_check.py: CP_OUT was declared in
# info.yaml as pin 6 / slot N01 and had NO metal, which a port count can never catch because an
# unrouted net has no label to be missing from a list.
# Route derived on the SEATED frame, not from 3g. Layer per segment is forced by what is already
# built: BOTH M3 and M4 are taken at die y505 -- REF_IN's M3 lane (x405-734) and VDDD's M4 lane
# (x408-667) -- so the haul goes WEST of x405 before it rises. It leaves M4 at die y460 because
# the M4 horizontals at y470.7-472.3, x445-485 are gnd_tap's escape to the ring, and it crosses
# y495 on M2 because Q_P's riser (x400) and REF_IN's riser (x405) both sit on M3 there.
CPO_X = 272.25          # die 472.25 -- the tap's own 0.6 um M4 stub, die y406.20-424.62
R.vwire(chip, ly, 4, 215.41, 260.0, CPO_X, w=0.6)              # up the stub to die y460
R.via_stack(chip, ly, 3, 4, CPO_X, 260.0)
R.vwire(chip, ly, 3, 260.0, 295.0, CPO_X, w=0.4)               # above the M3 horizontal at y440
R.via_stack(chip, ly, 2, 3, CPO_X, 295.0)
R.hwire(chip, ly, 2, 192.0, CPO_X, 295.0, w=0.4)               # M2 west across x405 and x400
R.via_stack(chip, ly, 2, 3, 192.0, 295.0)
R.vwire(chip, ly, 3, 295.0, 330.0, 192.0, w=0.4)               # between I_P's lane and Q_P's
R.hwire(chip, ly, 3, -132.5, 192.0, 330.0, w=0.4)              # die y530, above every quad lane
R.via_stack(chip, ly, 2, 3, -132.5, 330.0)
R.vwire(chip, ly, 2, 330.0, 349.5, -132.5, w=0.4)              # drops INTO the bar, not up to it
R.box(chip, ly, (36, 0), -154.66, 349.0, -110.34, 350.0)       # N01 finger-row bar
chip.shapes(ly.layer(36, 10)).insert(pya.DText("CP_OUT", pya.DTrans(pya.DVector(-132.5, 349.5))))
print("(g) CP_OUT: %.2f um to N01 (die x45.34-89.66)"
      % (44.59 + 35.0 + 80.25 + 35.0 + 324.5 + 19.5))

# --- PHASE 8 FRAME: seat the core in the padframe DIEAREA and draw the 0/0 boundary AT it ---
# Bailey, 2026-08-21: "the width and the height should be the exact size of the block size
# specified for the pad frame blocks." A01_BH.def (padframe/A01/project_defs/BH/) says
#   DIEAREA ( 0 0 ) ( 222000 110000 ) ;   UNITS DISTANCE MICRONS 200 ;
# = 1110.000 x 550.000 um. This layout is also 200 dbu/um (master.dbu = 0.005 in
# chip_merge.py), so seating the core in the die frame is a PURE TRANSLATION -- no scaling.
#
# The 0/0 boundary REPLACES the old core-extent rectangle; the two do not coexist. There is
# exactly one 0/0 shape in the deliverable and it IS the DIEAREA. (The old rectangle tracked
# chip.dbbox(), i.e. the metal extent -25,-21.5 .. 497,287.5 = 522 x 309 -- chip_top's
# STANDALONE die outline, which the padframe supersedes.)
#
# Everything above is written in the CORE frame; this final step shifts the whole cell into
# the die frame. Doing it here rather than offsetting chip_merge.py's BLOCKS table keeps every
# routing coordinate above unchanged, and keeps check_placement.py's core-frame comparison
# (chip_merge BLOCKS vs chip_top.tcl getcell boxes) valid without a re-baseline -- the
# block-relative placement does not move, only the whole core does.
DX, DY = 200.0, 200.0            # core offset inside the die (docs/phase8-padframe-plan.md 3f)
DIE_W, DIE_H = 1110.0, 550.0     # A01_BH DIEAREA, exact

core = chip.dbbox()
# The core frame reaches negative x (the GND ring sits at -17.5); the die frame never does.
# If this is already non-negative the cell has been seated once -- running route_chip.py twice
# would double-shift it and silently move every block 200 um.
if core.left >= 0.0:
    raise SystemExit("route_chip: chip_top already looks seated in the DIE frame (bbox LL "
                     "x=%.2f >= 0). Re-run chip_merge.py first; routing twice double-shifts."
                     % core.left)
chip.transform(pya.DTrans(DX, DY))
ly.clear_layer(ly.layer(0, 0))   # exactly one boundary, whatever was there before
chip.shapes(ly.layer(0, 0)).insert(pya.DBox(0.0, 0.0, DIE_W, DIE_H))

seated = chip.dbbox()
print("core frame  : (%.2f,%.2f)-(%.2f,%.2f)  %.1f x %.1f um"
      % (core.left, core.bottom, core.right, core.top, core.width(), core.height()))
print("seated at dx=%.1f dy=%.1f -> core occupies (%.2f,%.2f)-(%.2f,%.2f)"
      % (DX, DY, core.left + DX, core.bottom + DY, core.right + DX, core.top + DY))
print("die boundary (0/0): (0.00,0.00)-(%.2f,%.2f)  %.1f x %.1f um  [= A01_BH DIEAREA]"
      % (DIE_W, DIE_H, DIE_W, DIE_H))
print("DIEAREA_dbu=(0,0)-(%d,%d)" % (round(DIE_W / ly.dbu), round(DIE_H / ly.dbu)))
assert abs(seated.left) < 1e-9 and abs(seated.bottom) < 1e-9, seated
assert abs(seated.width() - DIE_W) < 1e-9 and abs(seated.height() - DIE_H) < 1e-9, seated

# --- DENSITY KEEP-OUT MARKERS (die frame, painted AFTER the seat) -------------------------
# Fill has not been inserted yet -- by us or by the organizer -- and whoever inserts it will
# drop dummy metal on the spiral and the varactor array unless these markers are present.
# Supplied unconditionally: they are ours to supply either way.
#
# WHICH LAYER STOPS WHAT. Read out of the PDK's own fill generators, which are the authority
# on what actually gets dropped (drc/filler_generation/*.rb), and cross-checked against the
# DRC rules, which agree exactly:
#
#   marker            dummy COMP        dummy POLY2       dummy METAL
#   NDMY   111/5      3.5 um DCF.11a    29.7 um DPF.11    -- NONE --
#   PMNDMY 152/5      -- none --        8 um DPF.19       6.0 um DM1.8-DM5.8
#   IND_MK 151/5      3.0 um DCF.12     3.0 um DPF.14     -- NONE --
#
# NDMY DOES NOT STOP METAL FILL. fill_metal.rb subtracts PMNDMY, MTPMK, OTP_MK, the fuse
# layers and the scribe ring; NDMY and IND_MK appear nowhere in it. PMNDMY is the metal
# keep-out. NDMY and IND_MK are the COMP/poly2 keep-outs.
#
# NO TILING IS NEEDED. DE.3's 15,000 um2 area cap and DE.4's 20 um merge distance bind
# `ndmy` ONLY (dummy_exclude.drc). PMNDMY and IND_MK carry neither, so the 15,288 um2 spiral
# is ONE rectangle on each. The only NDMY here is the varactor rect at 2,545.9 um2 -- 17% of
# the cap -- and it is the sole NDMY polygon in the design, so DE.4 has no pair to check.
# NDMY is deliberately kept OFF the spiral: covering it would force a tiling with a 20 um
# unprotected gap straight across the coil, to buy only a wider poly2 halo outside it.
#
# COORDINATES ARE MEASURED off gds/chip_top.gds (each instance's cell bbox in the die frame),
# not taken from a plan doc. The recorded plan figures were rounded, and the spiral's would
# have UNDER-covered the coil by 0.020 um at its bottom edge.
NDMY, PMNDMY, IND_MK = (111, 5), (152, 5), (151, 5)

SPIRAL = pya.DBox(490.000, 295.480, 672.000, 379.480)   # vco_v1/vco_inductor_v2, 182.000 x 84.000
VARACT = pya.DBox(576.630, 200.010, 623.370, 254.480)   # vco_v1/vco_varactors,    46.740 x 54.470

for _name, _box, _layers in [
    ("spiral",    SPIRAL, [PMNDMY, IND_MK]),   # metal fill; comp/poly2 fill (eddy loss -> Q)
    ("varactors", VARACT, [PMNDMY, NDMY]),     # metal fill; comp/poly2 fill (tuning match)
]:
    # geom.drc runs ongrid(0.005) on all three layers -- assert rather than hope.
    for _v in (_box.left, _box.bottom, _box.right, _box.top):
        assert abs(round(_v / ly.dbu) * ly.dbu - _v) < 1e-9, ("off-grid marker edge", _name, _v)
    # DE.2: minimum NDMY or PMNDMY size (x or y) is 0.8 um.
    assert min(_box.width(), _box.height()) >= 0.8, ("DE.2 min size", _name)
    for _lay, _dt in _layers:
        chip.shapes(ly.layer(_lay, _dt)).insert(_box)
    print("keep-out %-10s (%.3f,%.3f)-(%.3f,%.3f)  %.3f x %.3f um  %.1f um2  -> %s"
          % (_name, _box.left, _box.bottom, _box.right, _box.top, _box.width(), _box.height(),
             _box.width() * _box.height(), " ".join("%d/%d" % _l for _l in _layers)))

# DE.3 is an NDMY-only area cap; assert the one NDMY shape stays clear of it.
assert VARACT.width() * VARACT.height() < 15000.0, "DE.3: NDMY area cap"


# =========================================================================================
# RUNG 3 (B2): SECONDARY ESD -- IBIAS and ISS only. Die frame, painted AFTER the seat.
# =========================================================================================
# TOPOLOGY IS THE ORGANIZERS', NOT THE PLAN OF RECORD'S. examples/pads_simulation/symbols/
# io_secondary_3p3/io_secondary_3p3.sch puts BOTH clamp diodes on `to_gate` -- the CORE side
# of the ballast resistor -- not the pad side. That is correct for a SECONDARY network: the
# PRIMARY already exists inside the pad cell (gf180mcu_fd_io__asig_5p0 carries D2/D3,
# diode_*_06v0 m=4 pj=106e-6) and clamps to DVDD/DVSS, the PADRING rails. Our job is to bound
# the CORE-side node against VDDA/VSSA, which the primary structurally cannot do.
#
# ORDER ALONG THE NET: pad -> existing haul -> R (IBIAS only) -> clamp node -> block tap.
# ISS gets NO series R by design: 50 ohm there costs 78.5 mV, ~15x the engineered strap budget.
#
# WHY THE VSSA STRAP EXISTS. The gencell guard ring is metallised but has NO PORT -- the cell
# extracts with ZERO ports and its anode is emitted as `substrate`, because magic globalises
# the p-substrate to $SUB. LVS reports `match uniquely` with or without any ground metal:
# gate 4 is STRUCTURALLY BLIND here (docs/verification.md 8.9). Measured, the return was
# 96.47 um (IBIAS) / 49.85 um (ISS) of bare bulk silicon at 3250 ohm/sq -- of order 12.5 kohm
# and 6.5 kohm. The 10 um straps replace that with ~2-4 ohm.
for _n in ("esd_pd2nw", "esd_nd2ps", "esd_rpoly"):
    _src = pya.Layout(); _src.read("/foss/designs/AUS-NZ-integration/gds/%s.gds" % _n)
    ly.create_cell(_n).copy_tree(_src.cell(_n))

EM1, EVIA1, EM2 = (34, 0), (35, 0), (36, 0)
VIA1_SZ  = 0.26     # V1.1: via1 size is min AND max 0.26 um -- a fixed size, not a floor
M1_SPACE = 0.23     # M1.2a

# ---- VIA1 ARRAY (2026-08-29) ------------------------------------------------------------
# READ OUT OF THE DECK, NOT ASSUMED -- libs.tech/klayout/tech/drc/rule_decks/via1.drc:
#   V1.2a  via1.space(0.26.um, euclidian)                       -- min spacing 0.26
#   V1.2b  selected_via1.space(0.36.um, projecting >= 0.26.um)  -- 0.36 inside an ARRAY,
#          where "array" = a group that merges under sized(+-0.2) (any spacing < 0.40), has
#          a merged bbox min side >= 0.26*3 + 3*0.36 = 1.86 um, AND holds >= 16 cuts.
# A 9x9 plate grid is all three, so the naive 0.52 pitch (0.26 + 0.26) FIRES V1.2b. The
# floor is 0.62; 0.63 is used because it costs ZERO cuts (9 fit either way) and leaves 2 dbu
# of margin on a rule family this design had never stressed before this change.
#
# A SINGLE ROW escapes V1.2b -- with_bbox_min sees 0.26 um, under the 1.86 threshold -- so
# the ring arms could legally run at 0.52 and gain 5 cuts/arm. DELIBERATELY NOT TAKEN (Greg,
# 2026-08-29): it is rule-lawyering the deck's grouping semantics and breaks silently if a
# deck update changes how with_bbox_min merges. One uniform pitch keeps the assert honest.
VIA1_PITCH = 0.63   # 0.26 cut + 0.37 space; 126 dbu, exact on the 0.005 um grid
# Enclosure. V1.3a (metal1 overlap >= 0) and V1.4a (metal2 overlap >= 0.01) alone would allow
# ~0, but V1.3d and V1.4c impose a 0.06 um ADJACENT-EDGE condition on any via enclosed by
# < 0.04 um on one side. Staying >= 0.04 everywhere sidesteps both; 0.10 is 2.5x that and
# absorbs the half-dbu a centring snap can move a row.
VIA1_ENC     = 0.10
VIA1_ENC_MIN = 0.04   # what V1.3d / V1.4c actually key on -- asserted against, never drawn to
# Which pins have had the array applied. Rung 3 lands ONE PIN PER COMMIT with a full gate on
# each, so this tuple grows by one entry per commit rather than the whole clamp set moving at
# once (Greg, 2026-08-29). A pin not listed keeps the original single-cut geometry EXACTLY.
ESD_VIA_ARRAY = ("IBIAS",)


def _snap(v):
    return round(v / ly.dbu) * ly.dbu


def via1_grid(x0, y0, x1, y1, tag):
    """Fill an ALREADY-ENCLOSURE-REDUCED window with a centred via1 array at VIA1_PITCH.

    The caller passes the window it MEASURED -- M1 and M2 intersected, minus VIA1_ENC on
    every side -- so every cut placed here is enclosure-correct by construction rather than
    by a number in a comment. Counting is integer dbu: a float floor() on a 0.63 pitch lands
    one cut short about half the time, and the array comes out silently smaller, not wrong.

    Returns (ncols, nrows, [centres])."""
    sz = int(round(VIA1_SZ / ly.dbu))
    pt = int(round(VIA1_PITCH / ly.dbu))
    n, first = [], []
    for lo, hi in ((x0, x1), (y0, y1)):
        span = int(round((hi - lo) / ly.dbu))
        assert span >= sz, ("ESD %s: via1 window %.4f um cannot hold one %.2f um cut"
                            % (tag, hi - lo, VIA1_SZ))
        k = (span - sz) // pt + 1
        n.append(k)
        first.append(_snap(lo + (span - (sz + (k - 1) * pt)) * ly.dbu / 2.0 + VIA1_SZ / 2.0))
    nx, ny = n
    if nx > 1 or ny > 1:
        assert VIA1_PITCH - VIA1_SZ >= 0.36 - 1e-9, (
            "ESD %s: pitch %.3f gives %.3f um spacing, under V1.2b's 0.36"
            % (tag, VIA1_PITCH, VIA1_PITCH - VIA1_SZ))
    cuts = []
    for i in range(nx):
        for j in range(ny):
            vx, vy = first[0] + i * VIA1_PITCH, first[1] + j * VIA1_PITCH
            # Re-assert AFTER the centring snap. The snap can move a row half a dbu, and a
            # window that fitted BEFORE the snap is not proof it fits after.
            assert (x0 - 1e-9 <= vx - VIA1_SZ / 2 and vx + VIA1_SZ / 2 <= x1 + 1e-9
                    and y0 - 1e-9 <= vy - VIA1_SZ / 2 and vy + VIA1_SZ / 2 <= y1 + 1e-9), (
                "ESD %s: cut (%.4f,%.4f) escapes its enclosure window (%.4f,%.4f)-(%.4f,%.4f)"
                % (tag, vx, vy, x0, y0, x1, y1))
            R.box(chip, ly, EVIA1, vx - VIA1_SZ / 2, vy - VIA1_SZ / 2,
                                   vx + VIA1_SZ / 2, vy + VIA1_SZ / 2)
            cuts.append((vx, vy))
    return nx, ny, cuts

def _rings_plates(cellname):
    c = ly.cell(cellname)
    r = pya.Region(c.begin_shapes_rec(ly.layer(*EM1))); r.merge()
    rings  = sorted([p for p in r.each_merged() if p.holes() > 0], key=lambda q: q.bbox().width())
    plates = [p for p in r.each_merged() if p.holes() == 0]
    return rings, plates

def _outer(p):
    b = p.bbox().to_dtype(ly.dbu)
    return max(abs(b.left), abs(b.right), abs(b.bottom), abs(b.top))

def _inner(p):
    best = 0.0
    for h in range(p.holes()):
        for pt in p.each_point_hole(h):
            best = max(best, abs(pt.x * ly.dbu), abs(pt.y * ly.dbu))
    return best

def esd_tabs(cellname, cx, cy, ring_idx, tab_out, dirs, tag,
             array=False, half=0.6, m2ri=None, m2ro=None):
    """Outward M1 widening tabs on a gencell tie ring, + via1 up to M2.

    The gencell ring arms are 0.25 um. V1.1 fixes via1 at 0.26 um, so a via CANNOT be
    covered by the ring as generated -- no enclosure rule rescues a via wider than its
    metal. Same-layer M1 paint MERGES with the ring and widens the same conductor (the
    technique already used for the ISS EM widen). Widening goes OUTWARD: inward is blocked
    by the diode plate, and bridging that gap would short the diode to its own guard.
    """
    rings, plates = _rings_plates(cellname)
    ring = rings[ring_idx]
    r_out, r_in = _outer(ring), _inner(ring)
    tab_far = r_out + tab_out

    # ---- BUILD-TIME ASSERTS, recomputed from the GENERATED geometry on every run ---------
    # A gencell regeneration, a parameter change or a grid snap can silently eat these
    # margins. A number in a report cannot catch that; an assert that fires at build can.
    if len(rings) > ring_idx + 1:                   # an OUTER ring exists (pd2nw RING B)
        outer_in = _inner(rings[ring_idx + 1])
        gap = outer_in - tab_far
        assert gap >= M1_SPACE, (
            "ESD %s: tab-to-outer-ring gap %.4f um < M1.2a %.2f um "
            "(ring_out %.4f tab_far %.4f outer_in %.4f)"
            % (tag, gap, M1_SPACE, r_out, tab_far, outer_in))
    plate_far = max(_outer(p) for p in plates)      # inward: never approach the diode plate
    assert r_in - plate_far >= M1_SPACE, (
        "ESD %s: ring-inner-to-plate gap %.4f um < M1.2a %.2f um (r_in %.4f plate %.4f)"
        % (tag, r_in - plate_far, M1_SPACE, r_in, plate_far))
    assert (tab_far - r_in) >= VIA1_SZ, (
        "ESD %s: widened M1 %.4f um cannot hold a %.2f um via1"
        % (tag, tab_far - r_in, VIA1_SZ))

    # `half` is the tab half-length ALONG the ring. 0.6 (one cut) is the original tab and is
    # what pd2nw RING A keeps: it has only 0.285 um of outward room and 0.295 um to RING B, so
    # running the widening the full arm would hold that margin over 16 um instead of 1.2 um.
    # nd2ps has NO outer ring and 1.00 um of free outward room, so it takes the full row.
    assert half + M1_SPACE <= r_out, (
        "ESD %s: tab half-length %.3f um reaches the ring corner (r_out %.3f) -- the "
        "perpendicular arm's tab would merge into it" % (tag, half, r_out))
    # SNAP the via radius to the dbu grid. (r_in + tab_far)/2 is 11.1325 for pd2nw, which is
    # half a dbu off grid; a caller that re-derived it as 11.133 produced a second via1
    # rectangle snapping one dbu differently, and the 0.005 um sliver between them fired
    # V1.1 (via1 width) three times. The radius is now on-grid and RETURNED, so no caller
    # ever has to re-derive it.
    vr   = round((r_in + tab_far) / 2.0 / ly.dbu) * ly.dbu
    assert abs(round(vr / ly.dbu) * ly.dbu - vr) < 1e-12, "ESD %s: via radius off grid" % tag
    # RADIAL enclosure, against the MEASURED ring and the M2 frame the caller is about to
    # paint. One cut centred in a 1.25 um widening is obviously enclosed; a 25-cut row is not
    # obviously anything, so both directions are now checked rather than reasoned about.
    assert ((vr - VIA1_SZ / 2) - r_in >= VIA1_ENC_MIN
            and tab_far - (vr + VIA1_SZ / 2) >= VIA1_ENC_MIN), (
        "ESD %s: via1 radius %.4f not enclosed by M1 %.4f..%.4f by V1.3d's %.2f um"
        % (tag, vr, r_in, tab_far, VIA1_ENC_MIN))
    if m2ri is not None:
        assert ((vr - VIA1_SZ / 2) - m2ri >= VIA1_ENC_MIN
                and m2ro - (vr + VIA1_SZ / 2) >= VIA1_ENC_MIN), (
            "ESD %s: via1 radius %.4f not enclosed by the M2 frame %.4f..%.4f by V1.4c's "
            "%.2f um" % (tag, vr, m2ri, m2ro, VIA1_ENC_MIN))
        assert half - VIA1_ENC + VIA1_SZ / 2 <= m2ro - VIA1_ENC_MIN, (
            "ESD %s: via1 row (half %.3f) runs past the M2 frame end %.3f" % (tag, half, m2ro))
    vias, ncut = [], 0
    for d in dirs:
        if d in ("E", "W"):
            sgn = 1.0 if d == "E" else -1.0
            x0, x1 = (cx + r_out, cx + tab_far) if sgn > 0 else (cx - tab_far, cx - r_out)
            R.box(chip, ly, EM1, x0, cy - half, x1, cy + half)
            vx, vy = cx + sgn * vr, cy
            # x window is exactly one cut wide -- the RADIAL enclosure is asserted above,
            # against the real ring and frame radii, not re-derived from a box here.
            win = (vx - VIA1_SZ / 2, cy - half + VIA1_ENC, vx + VIA1_SZ / 2, cy + half - VIA1_ENC)
        else:
            sgn = 1.0 if d == "N" else -1.0
            y0, y1 = (cy + r_out, cy + tab_far) if sgn > 0 else (cy - tab_far, cy - r_out)
            R.box(chip, ly, EM1, cx - half, y0, cx + half, y1)
            vx, vy = cx, cy + sgn * vr
            win = (cx - half + VIA1_ENC, vy - VIA1_SZ / 2, cx + half - VIA1_ENC, vy + VIA1_SZ / 2)
        if array:
            ncut += len(via1_grid(win[0], win[1], win[2], win[3], "%s.%s" % (tag, d))[2])
        else:
            R.box(chip, ly, EVIA1, vx - VIA1_SZ / 2, vy - VIA1_SZ / 2,
                                   vx + VIA1_SZ / 2, vy + VIA1_SZ / 2)
            ncut += 1
        vias.append((vx, vy))
    print("   %-16s ring %.3f/%.3f -> tab %.3f  %d tab(s) %-4s  via r=%.3f  half %.2f  "
          "%d cut(s) = %d/arm" % (tag, r_in, r_out, tab_far, len(dirs), "".join(dirs), vr,
                                  half, ncut, ncut // max(1, len(dirs))))
    return vias, r_out, tab_far, ncut


def esd_res_tabs(cellname, cx, cy, tag):
    """The ppolyf_u terminals are 0.23 um M1 strips -- the SAME via-can't-land problem as the
    diode tie rings, found the same way (measured, not assumed). Widen each terminal OUTWARD
    in y, away from the poly body, and via up. Returns (bottom_via, top_via)."""
    c = ly.cell(cellname)
    r = pya.Region(c.begin_shapes_rec(ly.layer(*EM1))); r.merge()
    strips = sorted([p for p in r.each_merged() if p.holes() == 0],
                    key=lambda q: q.bbox().to_dtype(ly.dbu).bottom)
    frames = [p for p in r.each_merged() if p.holes() > 0]
    assert len(strips) == 2, "ESD %s: expected 2 terminal strips, got %d" % (tag, len(strips))
    frame_in = _inner(frames[0]) if frames else 1e9
    vias = []
    for i, p in enumerate(strips):
        b = p.bbox().to_dtype(ly.dbu)
        s = -1.0 if i == 0 else 1.0                    # bottom strip grows down, top grows up
        far = (b.bottom - 0.455) if s < 0 else (b.top + 0.455)
        gap = frame_in - abs(far)
        assert gap >= M1_SPACE, (
            "ESD %s: terminal tab to guard frame %.4f um < M1.2a %.2f um (far %.4f frame %.4f)"
            % (tag, gap, M1_SPACE, far, frame_in))
        inner_edge = b.top if s < 0 else b.bottom
        assert abs(far - inner_edge) >= VIA1_SZ, (
            "ESD %s: widened terminal %.4f um cannot hold a %.2f um via1"
            % (tag, abs(far - inner_edge), VIA1_SZ))
        y0, y1 = (far, b.top) if s < 0 else (b.bottom, far)
        R.box(chip, ly, EM1, cx + b.left, cy + y0, cx + b.right, cy + y1)
        vy = (far + inner_edge) / 2.0
        R.box(chip, ly, EVIA1, cx - VIA1_SZ / 2, cy + vy - VIA1_SZ / 2,
                               cx + VIA1_SZ / 2, cy + vy + VIA1_SZ / 2)
        vias.append((cx, cy + vy))
    print("   %-16s terminals widened to +-%.3f, frame_in %.3f" % (tag, 0.455, frame_in))
    return vias[0], vias[1]

def esd_m2_frame(cx, cy, ri, ro):
    """Square M2 annulus collecting the tab via1s of one device."""
    R.box(chip, ly, EM2, cx - ro, cy + ri, cx + ro, cy + ro)     # N
    R.box(chip, ly, EM2, cx - ro, cy - ro, cx + ro, cy - ri)     # S
    R.box(chip, ly, EM2, cx + ri, cy - ro, cx + ro, cy + ro)     # E
    R.box(chip, ly, EM2, cx - ro, cy - ro, cx - ri, cy + ro)     # W

ESD_BRIDGE = 6.5   # M2 plate-bridge half-extent. NOT a free parameter: it has to clear the
                   # tie-ring M2 frame's inner radius (11.00 nd2ps / 10.80 pd2nw).

def esd_plate_bridge(cx, cy, cellname, tag, array=False):
    """Tie the FOUR diode plates together and take them up to M2.

    Each doverlap cell has four SEPARATE M1 plates (the diode terminals), one per unit. A via
    on one plate leaves the other three FLOATING -- netgen sees it as 4 devices reducing to 2
    instead of 1, plus extra nets. They cannot be bridged on M1: the tie ring's own central
    cross occupies |x|,|y| < 0.135, exactly the gap between the plates, so an M1 bridge would
    short every diode to its own guard. So bridge on M2, inside the tie-ring M2 frame's inner
    radius (11.00 / 10.80) with clearance to spare.

    VIA ARRAY (2026-08-29). Each plate used to carry ONE 0.26 um cut on 98.50 um2 of solid
    M1 -- four cuts for an entire diode, against 1040 in the organizers' io_secondary_5p0
    (resources/Integration/Chipathon2025_pads/magic/secondary_ESD.gds). On an ESD path the
    CUT, not the diode, was the current limit.

    THE M2 BRIDGE CAPS THE ARRAY, NOT THE M1 PLATE. The plates reach +-10.49 but the bridge
    stops at +-6.5, so each plate's usable window is the M1/M2 INTERSECTION -- 5.990 x 5.935
    um, a CORNER of the plate, not its centre. Measured per plate and re-derived every run:
    a gencell change moves the plates, and an array centred on the plate would then drift off
    the bridge silently. (Widening the bridge to ~+-10 would allow ~16x16; deliberately NOT
    done -- it would eat the clearance to the M2 frame, and 752 cuts/clamp already matches
    the reference's order of magnitude. Greg, 2026-08-29.)"""
    if not array:
        for sx in (-5.5, 5.5):
            for sy in (-5.5, 5.5):
                R.box(chip, ly, EVIA1, cx + sx - VIA1_SZ / 2, cy + sy - VIA1_SZ / 2,
                                       cx + sx + VIA1_SZ / 2, cy + sy + VIA1_SZ / 2)
        R.box(chip, ly, EM2, cx - ESD_BRIDGE, cy - ESD_BRIDGE, cx + ESD_BRIDGE, cy + ESD_BRIDGE)
        return (cx + 5.5, cy + 5.5), 4
    _, plates = _rings_plates(cellname)
    assert len(plates) == 4, "ESD %s: expected 4 diode plates, got %d" % (tag, len(plates))
    tot, shape = 0, None
    for pl in sorted(plates, key=lambda q: (q.bbox().bottom, q.bbox().left)):
        b = pl.bbox().to_dtype(ly.dbu)
        wx0 = max(b.left,   -ESD_BRIDGE) + VIA1_ENC
        wx1 = min(b.right,   ESD_BRIDGE) - VIA1_ENC
        wy0 = max(b.bottom, -ESD_BRIDGE) + VIA1_ENC
        wy1 = min(b.top,     ESD_BRIDGE) - VIA1_ENC
        nx, ny, cuts = via1_grid(cx + wx0, cy + wy0, cx + wx1, cy + wy1, "%s plate" % tag)
        tot += len(cuts); shape = (nx, ny)
    R.box(chip, ly, EM2, cx - ESD_BRIDGE, cy - ESD_BRIDGE, cx + ESD_BRIDGE, cy + ESD_BRIDGE)
    print("   %-16s 4 plates x %dx%d = %d via1 cuts (was 4)  pitch %.2f  enc %.2f"
          % (tag, shape[0], shape[1], tot, VIA1_PITCH, VIA1_ENC))
    return (cx + 5.5, cy + 5.5), tot

print("phase 8 rung 3: secondary ESD, IBIAS + ISS")
# ---- PLACEMENT IS DERIVED, NOT TRANSCRIBED -----------------------------------------------
# Each device is anchored by its intended LOWER-LEFT corner in the die frame; the instance
# origin is computed from the cell's MEASURED bbox at build time. Transcribed centres would
# silently drift the moment a gencell parameter changed -- and they already did once this
# rung: magic's `box values` reported the resistor as 18.16 x 7.18 while the written GDS is
# 18.24 x 7.26. Deriving means the 0.08 um can never become a landing defect.
ESD_PLACE = {                       # tag: (cell, lower-left x, lower-left y)
    "IB_D1": ("esd_pd2nw",  38.00, 268.00),
    "IB_D2": ("esd_nd2ps",  66.00, 268.00),
    "IB_R":  ("esd_rpoly",  20.00, 268.00),
    "IS_D1": ("esd_pd2nw",  20.00, 368.00),
    "IS_D2": ("esd_nd2ps",  50.00, 368.00),
}
# the measured free blocks these must stay inside (docs: rung-3 stage B1 occupancy scans)
ESD_BLOCK = {"IB": (18.0, 255.0, 100.0, 312.0), "IS": (18.0, 355.0, 100.0, 412.0)}
ESD_POS, ESD_BOX = {}, {}
for _tag, (_cell, _llx, _lly) in ESD_PLACE.items():
    _bb = ly.cell(_cell).dbbox()
    _cx, _cy = _llx - _bb.left, _lly - _bb.bottom          # origin s.t. bbox LL lands on (llx,lly)
    ESD_POS[_tag] = (_cx, _cy)
    ESD_BOX[_tag] = (_llx, _lly, _llx + _bb.width(), _lly + _bb.height())
    chip.insert(pya.DCellInstArray(ly.cell(_cell).cell_index(),
                                   pya.DTrans(pya.DVector(_cx, _cy))))
    _bx = ESD_BLOCK[_tag[:2]]
    assert (_bx[0] <= _llx and _bx[1] <= _lly
            and ESD_BOX[_tag][2] <= _bx[2] and ESD_BOX[_tag][3] <= _bx[3]), (
        "ESD %s box (%.3f,%.3f)-(%.3f,%.3f) escapes its measured free block %s"
        % ((_tag,) + ESD_BOX[_tag] + (_bx,)))
    print("   %-6s %-11s (%8.3f,%8.3f)-(%8.3f,%8.3f)  %6.3f x %6.3f"
          % (_tag, _cell, ESD_BOX[_tag][0], ESD_BOX[_tag][1], ESD_BOX[_tag][2],
             ESD_BOX[_tag][3], _bb.width(), _bb.height()))
# no two ESD devices may overlap
for _a in ESD_BOX:
    for _b in ESD_BOX:
        if _a >= _b: continue
        ax0, ay0, ax1, ay1 = ESD_BOX[_a]; bx0, by0, bx1, by1 = ESD_BOX[_b]
        assert not (ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1),             "ESD %s and %s overlap" % (_a, _b)
IB_D1, IB_D2, IB_R = ESD_POS["IB_D1"], ESD_POS["IB_D2"], ESD_POS["IB_R"]
IS_D1, IS_D2       = ESD_POS["IS_D1"], ESD_POS["IS_D2"]

# ---- tie-ring tabs. nd2ps gets 4 (outward is free); pd2nw RING A gets 2 (it is boxed in by
# RING B with only 0.58 um, so each tab is a thin-margin structure -- fewer is safer).
# The pd2nw RING B "bonus" VSSA tab from the approved plan is DROPPED: it would put a third
# net on M2 around one cell with a measured 0.2 um gap to the VDDA frame, under the 0.28 um
# M2 spacing. The nd2ps beside it provides the substrate strap and they share one substrate.
ESD_TABVIA = {}
ESD_CUTS = {}      # tag -> via1 cuts drawn, for the attribution report
for _tag, _c, _p in (("IBIAS.nd2ps", "esd_nd2ps", IB_D2), ("ISS.nd2ps", "esd_nd2ps", IS_D2)):
    # nd2ps ONLY. The arm widening grows from 1.2 um to 16 um, which is real new M1; pd2nw
    # RING A is deliberately left alone (0.295 um to RING B -- holding that over 16 um is a
    # bad trade for a return path). Greg, 2026-08-29.
    _a = _tag.split(".")[0] in ESD_VIA_ARRAY
    _v, _ro, _tf, _n = esd_tabs(_c, _p[0], _p[1], 0, 1.00, ("N", "S", "E", "W"), _tag,
                                array=_a, half=(8.0 if _a else 0.6),
                                m2ri=11.00, m2ro=12.70)
    ESD_TABVIA[_tag] = dict(zip(("N", "S", "E", "W"), _v))
    ESD_CUTS[_tag + ".ring"] = _n
    esd_m2_frame(_p[0], _p[1], 11.00, 12.70)
for _tag, _c, _p in (("IBIAS.pd2nw", "esd_pd2nw", IB_D1), ("ISS.pd2nw", "esd_pd2nw", IS_D1)):
    _v, _ro, _tf, _n = esd_tabs(_c, _p[0], _p[1], 0, 0.285, ("E", "W"), _tag)
    ESD_TABVIA[_tag] = dict(zip(("E", "W"), _v))
    ESD_CUTS[_tag + ".ring"] = _n
    esd_m2_frame(_p[0], _p[1], 10.80, 11.50)


# ---- IBIAS: resistor terminals, series insertion, clamp node ----------------------------
# NOTE ON FRAME: everything below this point paints in the DIE frame -- the +200/+200 seat has
# already happened. An earlier revision of this block used core coordinates (die-200) and every
# connecting wire landed 200 um from its device, leaving all five ESD devices on isolated m1_*
# nodes. Caught by the extraction port/net count, not by DRC: unconnected is not a rule
# violation. Same failure class as the five landing defects in analysis/landing_check.py.
# --- STRUCTURAL GUARD FOR THE R.hwire HALF-WIDTH OVERRUN ---------------------------------
# R.hwire/R.vwire extend HALF THEIR WIDTH past each endpoint. That overrun has now silently
# merged a net THREE times in this file (the ISS south lane, the ISS bus, and the rung-3 VSSA
# strap reaching into the ESD plate bridge). It is documented twice already, so documenting it
# again is not a fix. Every ESD segment is recorded here with its GROWN extent and checked
# pairwise against the other nets' segments and against every device footprint, at BUILD time.
# A new segment can no longer reach a foreign net without the build failing loudly.
ESD_SEGS = []      # (net, metal, grown DBox)

def eseg(net, m, x0, y0, x1, y1, w, horiz=None):
    """Paint an ESD wire AND record the grown extent the checker must use."""
    if horiz is None:
        horiz = abs(y1 - y0) < 1e-9
    if horiz:
        R.hwire(chip, ly, m, x0, x1, y0, w=w)
    else:
        R.vwire(chip, ly, m, y0, y1, x0, w=w)
    h = w / 2.0
    ESD_SEGS.append((net, m, pya.DBox(min(x0, x1) - h, min(y0, y1) - h,
                                      max(x0, x1) + h, max(y0, y1) + h)))

M4_SPACE = 0.28    # M4.2a

def evia(net, x, y, m_lo, m_hi, pad=0.5):
    """Record a via stack's INTERMEDIATE metal pads. A via stack from M2 to M5 paints M3 and
    M4 on the way through, and those pads are invisible to a segment checker that only knows
    about declared wires -- which is exactly how the ISS clamp via landed 0.14 um from the
    VDDA M4 feed and fired M4.2a four times. Registered here, grown by the spacing rule, so a
    near-miss on an intermediate layer fails the build instead of the gate."""
    R.via_stack(chip, ly, m_lo, m_hi, x, y)
    h = pad / 2.0 + M4_SPACE
    for m in range(m_lo, m_hi + 1):
        ESD_SEGS.append((net, m, pya.DBox(x - h, y - h, x + h, y + h)))

def esd_check_segments(devboxes):
    bad = []
    for i in range(len(ESD_SEGS)):
        for j in range(i + 1, len(ESD_SEGS)):
            (na, ma, ba), (nb, mb, bb) = ESD_SEGS[i], ESD_SEGS[j]
            if na != nb and ma == mb and ba.overlaps(bb):
                bad.append("%s/%s on M%d: %s vs %s" % (na, nb, ma, ba, bb))
    for (net, m, b) in ESD_SEGS:
        for tag, (x0, y0, x1, y1) in devboxes.items():
            if net == "VSSA" and b.overlaps(pya.DBox(x0, y0, x1, y1)) and m == 2:
                # the VSSA strap MAY overlap its own nd2ps frame, nothing else
                if not tag.endswith("D2"):
                    bad.append("VSSA M2 grown extent reaches device %s" % tag)
    assert not bad, "ESD segment overrun reaches a foreign net: " + "; ".join(bad)
    print("   ESD segment check: %d segments, 0 cross-net overruns" % len(ESD_SEGS))

_rb, _rt = esd_res_tabs("esd_rpoly", IB_R[0], IB_R[1], "IBIAS.rpoly")
IB_RISER = (34.0, 282.5)      # die: bottom end of the M3 riser that carries on to the block tap
# PAD PLATE -> resistor BOTTOM terminal. This M2 run is now the ONLY thing the pad touches.
eseg("IBIAS", 2, 18.0, _rb[1], _rb[0], _rb[1], 1.0)
# CORE side: resistor TOP -> clamp node -> both diodes -> up onto the riser bottom
ESD_CUTS["IBIAS.pd2nw.plates"] = esd_plate_bridge(
    IB_D1[0], IB_D1[1], "esd_pd2nw", "IBIAS.pd2nw", "IBIAS" in ESD_VIA_ARRAY)[1]
ESD_CUTS["IBIAS.nd2ps.plates"] = esd_plate_bridge(
    IB_D2[0], IB_D2[1], "esd_nd2ps", "IBIAS.nd2ps", "IBIAS" in ESD_VIA_ARRAY)[1]
IB_CY = IB_D2[1]                              # clamp-node y, inside BOTH plate bridges
for _c in (IB_D1, IB_D2):
    assert abs(IB_CY - _c[1]) <= 6.5 - 0.5, "IBIAS clamp-node y outside the plate bridge of %r" % (_c,)
evia("IBIAS", _rt[0], _rt[1], 2, 3)           # resistor top -> M3
for _c in (IB_D1, IB_D2):
    evia("IBIAS", _c[0], IB_CY, 2, 3)         # each plate bridge -> M3
R.route_path(chip, ly, 3, [(_rt[0], _rt[1]), (_rt[0], IB_CY), (IB_D2[0], IB_CY)], w=0.4)
R.route_path(chip, ly, 3, [(IB_RISER[0], IB_CY), (IB_RISER[0], IB_RISER[1])], w=0.4)
assert min(_rt[0], IB_D2[0]) < IB_RISER[0] < max(_rt[0], IB_D2[0]),     "the riser stub does not meet the clamp node"
print("   IBIAS clamp node: R %.3f/%.3f -> D1 %.2f -> D2 %.2f at y%.2f -> riser (%.1f,%.1f)"
      % (_rb[1], _rt[1], IB_D1[0], IB_D2[0], IB_CY, IB_RISER[0], IB_RISER[1]))

# ---- VDDA feed onto the pd2nw RING A frame ----------------------------------------------
# The VDDA M4 riser (die x44.5-47.5, y205-399) now passes straight through D1's footprint, so
# the feed is a short hop west onto the W tab instead of a 120 um vertical from y400.
_ibv = ESD_TABVIA["IBIAS.pd2nw"]["W"]
eseg("VDDA", 4, 47.5, _ibv[1], _ibv[0], _ibv[1], 3.0)
evia("VDDA", _ibv[0], _ibv[1], 2, 4)

# ---- VSSA strap: nd2ps M2 frame -> GND ring, 10 um, via stack INTO the ring --------------
# R.hwire EXTENDS HALF ITS WIDTH past each endpoint. At w=10 that is 5 um, so a strap
# nominally starting at the M2 frame's inner edge (cx+11.00 = 82.30) actually reaches 77.30 --
# INSIDE the plate bridge, which ends at cx+6.5 = 77.80. That shorted the clamp node to VSSA
# and every ESD node extracted as VSSA. Start at cx+13.0 so the EXTENDED end lands at 79.30,
# still covering the frame (82.30-84.00) with 1.5 um clear of the bridge. Third time this
# overrun has cost a net in this file; the strap start is now derived from it, not eyeballed.
assert (IB_D2[0] + 13.0) - 5.0 > IB_D2[0] + 6.5 + 1.0, "VSSA strap would reach the plate bridge"
eseg("VSSA", 2, IB_D2[0] + 13.0, IB_D2[1], 190.0, IB_D2[1], 10.0)
R.via_stack(chip, ly, 2, 5, 190.0, IB_D2[1])
print("   IBIAS VSSA strap: M2 10 um (%.2f,%.2f) -> GND ring die x190.00  [extends to %.2f]"
      % (IB_D2[0] + 13.0, IB_D2[1], IB_D2[0] + 13.0 - 5.0))

# ---- DEMOTE the block's own IBIAS port label -------------------------------------------
# ibias_gen_v1's GDS carries an `IBIAS` text on 36/10 at its tap (die 271.30,423.90), streamed
# in verbatim by chip_merge. Our pad plate carries a second `IBIAS` on 36/10 at (0.50,282.50).
# Before the series cut those two texts sat on ONE net, so magic emitted one port. The ballast
# splits that net in two, and magic then has one name for two electrically distinct nodes --
# it emits `IBIAS` and `IBIAS_uq0`, a 13th port, and LVS fails on port count.
#
# The chip's port list is a CHIP-level decision; a block's internal port label should not get a
# vote. Demote the tap label to 36/10 -> 36/0, which the magic tech maps to `labels allm2
# noport`: it stays in the GDS and stays visible to a text scrape, it simply stops competing
# for a port name. Exactly the mechanism used for VSSD in f31d594, applied one level down.
# ---- ISS: NO series ballast, by design ---------------------------------------------------
# 50 ohm on ISS would cost 78.5 mV at the 1.24-1.57 mA tail current -- about 15x the whole
# engineered strap budget -- and ISS is the VCO TAIL RETURN, not a signal. So pad node and
# clamp node are ONE low-impedance M5/M4 bus and the clamp taps it directly. Nothing splits
# the ISS net, so unlike IBIAS there is no duplicate-port-label to resolve and landing_check
# keeps its BLOCK-side seed: the flood has no series device to cross.
# RELOCATED into the W21 pin band (DEF pin y360.340-404.660). The clamp node routing is
# GONE: the ISS M5 bus (die y377.5-387.5, x14-90) passes directly OVER both plate bridges, so
# the node is two via stacks straight down instead of an M5 tap plus ~45 um of 0.4 um M3.
# Verified M5 is present at both via points before this was written.
ESD_CUTS["ISS.pd2nw.plates"] = esd_plate_bridge(
    IS_D1[0], IS_D1[1], "esd_pd2nw", "ISS.pd2nw", "ISS" in ESD_VIA_ARRAY)[1]
ESD_CUTS["ISS.nd2ps.plates"] = esd_plate_bridge(
    IS_D2[0], IS_D2[1], "esd_nd2ps", "ISS.nd2ps", "ISS" in ESD_VIA_ARRAY)[1]
# IS_VY was 382.0 first: that put the via stack's M4 pad 0.14 um from the VDDA M4 feed
# (y378.61-381.61) and fired M4.2a x4. Raised clear of it, still inside both plate bridges
# and still under the ISS M5 bus (y377.5-387.5).
IS_VY = 384.0
for _c in (IS_D1, IS_D2):
    assert abs(IS_VY - _c[1]) <= 6.5 - 0.5, "ISS via y is outside the plate bridge of %r" % (_c,)
assert 377.5 < IS_VY < 387.5, "ISS clamp via is not under the ISS M5 bus"
assert (IS_VY - 0.25) - 381.61 >= M4_SPACE, "ISS clamp via M4 pad violates M4.2a to the VDDA feed"
for _c in (IS_D1, IS_D2):
    evia("ISS", _c[0], IS_VY, 2, 5)
print("   ISS clamp node:   2 via stacks M2->M5 at (%.2f,%.1f) and (%.2f,%.1f) under the ISS bus"
      % (IS_D1[0], IS_VY, IS_D2[0], IS_VY))

# VDDA feed onto the ISS pd2nw RING A W tab, held 5.5 um clear of the ISS M4 tap above it --
# a first draft put both on M4 at the same y, which would have shorted ISS to VDDA.
_isv = ESD_TABVIA["ISS.pd2nw"]["W"]
eseg("VDDA", 4, 47.5, _isv[1], _isv[0], _isv[1], 3.0)
R.via_stack(chip, ly, 2, 4, _isv[0], _isv[1])

# VSSA strap, same overrun-aware start as IBIAS
assert (IS_D2[0] + 13.0) - 5.0 > IS_D2[0] + 6.5 + 1.0, "ISS VSSA strap would reach the plate bridge"
eseg("VSSA", 2, IS_D2[0] + 13.0, IS_D2[1], 190.0, IS_D2[1], 10.0)
R.via_stack(chip, ly, 2, 5, 190.0, IS_D2[1])
print("   ISS   VSSA strap: M2 10 um (%.2f,%.2f) -> GND ring die x190.00  [extends to %.2f]"
      % (IS_D2[0] + 13.0, IS_D2[1], IS_D2[0] + 13.0 - 5.0))

# DELETING WHILE ITERATING shapes(...).each() CORRUPTS THE TRAVERSAL. A first version of this
# deleted inside the loop; with one shape it happened to work, with several it removed EVERY
# 36/10 text in the cell and the extraction came back with 0 ports and 5 devices. Collect the
# targets first, then delete. Never fold these two passes together.
_l1010, _l360 = ly.layer(36, 10), ly.layer(36, 0)

def demote_labels(name, keep_at=None, lay=36):
    """Move <lay>/10 (port) texts to <lay>/0 (plain label). keep_at=(x,y) spares one instance.
    Block-tap labels streamed in from a block GDS sit on the tap's OWN metal: the I/Q taps are
    M1, so theirs are on 34/10, not 36/10."""
    _p10, _p0 = ly.layer(lay, 10), ly.layer(lay, 0)
    hits = []
    for _sh in chip.shapes(_p10).each():                   # pass 1: collect only
        if _sh.is_text() and _sh.text.string == name:
            _t = _sh.text
            xy = (_t.x * ly.dbu, _t.y * ly.dbu)
            if keep_at is not None and abs(xy[0] - keep_at[0]) < 1e-6 and abs(xy[1] - keep_at[1]) < 1e-6:
                continue
            hits.append((_sh, pya.DText(name, pya.DTrans(pya.DVector(xy[0], xy[1])))))
    for _sh, _ in hits:                                    # pass 2: delete
        _sh.delete()
    for _, _t in hits:                                     # pass 3: re-insert on <lay>/0
        chip.shapes(_p0).insert(_t)
    return len(hits)

# ibias_gen_v1's GDS carries its own IBIAS text on 36/10 at its tap; our pad plate carries one
# at (0.50,282.50). The ballast splits that net in two, so magic would emit IBIAS + IBIAS_uq0 --
# a 13th port. Keep the pad one, demote the block's.
_n = demote_labels("IBIAS", keep_at=(0.5, 282.5))
assert _n == 1, "expected exactly 1 non-pad IBIAS 36/10 label to demote, found %d" % _n
print("   IBIAS: demoted %d block-tap label 36/10 -> 36/0 (pad label at 0.50,282.50 kept)" % _n)

# JOB B: I_P is no longer a PAD, so nothing should carry it as a chip PORT. DIV2_QUAD_v1's GDS
# still has its own I_P text on 36/10 at its output tap. Demote ALL of them -- I_P stays an
# internal net (DIV2.I_P -> PFD.FB) and keeps its text in the GDS, it just stops being a port.
_m = demote_labels("I_P", lay=34) + demote_labels("I_P", lay=36)
assert _m >= 1, "expected at least one I_P 36/10 label to demote, found none"
print("   I_P: demoted %d label(s) 36/10 -> 36/0 (no longer a pad)" % _m)
esd_check_segments(ESD_BOX)
# ---- VIA1 CUT INVENTORY -- the attribution source for the DRC box-set delta --------------
# Every via1 cut this script adds is attributable to exactly one structure below. If the box
# set moves and a box cannot be tied back to one of these extents, that is a STOP, not a
# rounding difference (Greg, 2026-08-29).
print("   via1 cut inventory (arrayed pins: %s)" % (", ".join(ESD_VIA_ARRAY) or "none"))
for _k in sorted(ESD_CUTS):
    print("      %-24s %4d cut(s)" % (_k, ESD_CUTS[_k]))
print("      %-24s %4d cut(s)  TOTAL (was 30 across both clamps)"
      % ("all ESD via1", sum(ESD_CUTS.values())))
print("   IBIAS: demoted %d block-tap label 36/10 -> 36/0 (pad label at 0.50,282.50 kept)" % _n)

ly.write(GDS)
print("routed power + GND ring + labels + DIEAREA boundary; wrote %s" % GDS)
