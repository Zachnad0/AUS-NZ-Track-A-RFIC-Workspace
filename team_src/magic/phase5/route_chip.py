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
IQ_TAP  = {"Q_N": (2.18, 51.92), "I_N": (2.18, 140.27),
           "I_P": (235.18, 140.27), "Q_P": (235.18, 51.92)}
IQ_PAD  = {"Q_N": -32.5, "I_N": 67.5, "I_P": 167.5, "Q_P": 267.5}   # core x of N02..N05 centres
IQ_PADY = 349.0                                                     # core y of the north pin row
IQ_PLAN = {
    "Q_N": dict(esc=-3.6, jog=None,           lane=290.0),
    "I_N": dict(esc=-2.3, jog=None,           lane=300.0),
    "I_P": dict(esc=+11.0, jog=(185.0, 190.0), lane=308.0, novia=True),
    "Q_P": dict(esc=+17.0, jog=(200.0, 198.0), lane=316.0),
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
R.route_path(chip, ly, 3, [(-7.0, IB_TAP[1]), (-166.0, IB_TAP[1]), (-166.0, 82.5)], w=0.4)
R.via_stack(chip, ly, 2, 3, -166.0, 82.5)
R.hwire(chip, ly, 2, -184.0, -166.0, 82.5, w=2.0)              # feeder, plate -> via (MSLOT.1)
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
R.via_stack(chip, ly, 4, 5, 367.5, 280.0)                      # onto the ring top, die (567.5,480)
R.vwire(chip, ly, 4, 280.0, 347.0, 367.5, w=3.0)               # M4 riser, die y480 -> 547
R.via_stack(chip, ly, 2, 4, 367.5, 347.0)
R.vwire(chip, ly, 2, 347.0, 348.0, 367.5, w=3.0)   # w=3 extends 1.5: must not pass die y550
R.box(chip, ly, (36, 0), 331.36, 349.0, 403.64, 350.0)         # N06 finger-row bar, 72.28 x 1.0
# VSSD text on 36/0, NOT 36/10. The magic tech maps `calma 36 10 -> labels allm2 port` and
# `calma 36 0 -> labels allm2 noport`, so a text on /0 is a label magic never promotes to a
# port. VSSA and VSSD are ONE electrical net, magic emits ONE name for it, and on /10 it was
# picking VSSD -- which broke pin matching against a golden whose ground port is VSSA. On /0
# the VSSD text is still in the GDS (Bailey's top_cell_text scrape reports each text with its
# layer and datatype) but never competes for the port name.
chip.shapes(ly.layer(36, 0)).insert(pya.DText("VSSD", pya.DTrans(pya.DVector(367.5, 349.5))))

# VDDD -- N07, die x631.36-703.64, off the M5 VDDD bus (die x249-442, y382-394).
# Tapped at die x408, INSIDE the bus -- 3o's "tap at x256" for VDDA was 2.5 um outside its bus
# and produced a floating node, so every bus tap here is measured against the bus extent.
# The rise column die x408 is the ibias(<=381.76) / CP(>=410) gap and carries NO M4 (measured).
# The east lane at die y505 must cross VSSD's M4 riser at die x567.5 -- same layer, different
# net -- so it hops to M5 for 30 um. M5 is free there, above the ring top at die y487.5.
R.via_stack(chip, ly, 4, 5, 208.0, 188.0)                      # onto the VDDD bus, die (408,388)
R.vwire(chip, ly, 4, 188.0, 305.0, 208.0, w=3.0)               # M4 riser, die y388 -> 505
R.hwire(chip, ly, 4, 208.0, 360.0, 305.0, w=3.0)
R.via_stack(chip, ly, 4, 5, 360.0, 305.0)
R.hwire(chip, ly, 5, 360.0, 375.0, 305.0, w=3.0)               # M5 hop over VSSD's M4 riser
R.via_stack(chip, ly, 4, 5, 375.0, 305.0)
R.hwire(chip, ly, 4, 375.0, 467.0, 305.0, w=3.0)
R.vwire(chip, ly, 4, 305.0, 347.0, 467.0, w=3.0)               # M4 riser, die x667
R.via_stack(chip, ly, 2, 4, 467.0, 347.0)
R.vwire(chip, ly, 2, 347.0, 348.0, 467.0, w=3.0)   # ditto
R.box(chip, ly, (36, 0), 431.36, 349.0, 503.64, 350.0)         # N07 finger-row bar
chip.shapes(ly.layer(36, 10)).insert(pya.DText("VDDD", pya.DTrans(pya.DVector(467.0, 349.5))))

# REF_IN -- N08 in_c. THREE separate pins in one slot, ONE 0.38 um finger each, no row to bar
# across (plan doc 3s): Y die x733.76-734.14, PD x794.29-794.67, PU x798.655-799.035. Each is
# landed on its OWN measured finger; a 0.4 um wire centred 0.2 um off misses entirely while
# looking perfectly routed.
# Y comes from PFD.REF, die (410.28,457.60) on M3, which sits on PFD's west edge (x410), so it
# escapes WEST into the ibias/PFD gap rather than crossing the block.
R.hwire(chip, ly, 3, 205.0, 210.28, 257.6, w=0.4)              # escape west out of PFD
R.vwire(chip, ly, 3, 257.6, 305.0, 205.0, w=0.4)               # north, crossing the ring on M3
R.hwire(chip, ly, 3, 205.0, 534.0, 305.0, w=0.4)               # east at die y505 (measured clear)
R.vwire(chip, ly, 3, 305.0, 348.5, 534.0, w=0.4)
R.via_stack(chip, ly, 2, 3, 534.0, 348.5)
# The box must reach DOWN to the via2 M2 pad (die y548.25-548.75), not start at the finger
# edge: at y349.0 (die 549.0) it cleared the pad by 0.25 um and REF_IN extracted as two
# disconnected labels (REF_IN + REF_IN_uq0). Same landing-miss family as VSSA_uq0/VDDA_uq0.
R.box(chip, ly, (36, 0), 533.5, 348.3, 534.4, 350.0)           # lands ON the Y finger
chip.shapes(ly.layer(36, 10)).insert(pya.DText("REF_IN", pya.DTrans(pya.DVector(533.95, 349.5))))

# PU/PD: decided 2026-08-21 and confirmed against the PDK truth table -- PU=0, PD=1 = weak
# pull-down, so REF_IN parks at a clean logic 0 when the bench clock is disconnected. Both
# terminals MUST be driven; a floating CMOS control gate is not acceptable.
#   PD -> VDDD   PU -> VSSD (the DIGITAL island's ground, NOT VSSA)
# Both ties run on M2 so they cross REF_IN's M3 riser and each other's risers on other layers.
R.box(chip, ly, (36, 0), 594.0, 349.0, 594.96, 350.0)          # lands ON the PD finger
R.vwire(chip, ly, 2, 340.0, 349.0, 594.48, w=1.0)
R.hwire(chip, ly, 2, 467.0, 594.48, 340.0, w=1.0)              # west to VDDD's riser
R.via_stack(chip, ly, 2, 4, 467.0, 340.0)                      # joins VDDD -- same net
chip.shapes(ly.layer(36, 10)).insert(pya.DText("REF_IN_PD", pya.DTrans(pya.DVector(594.48, 349.5))))

R.box(chip, ly, (36, 0), 598.4, 349.0, 599.3, 350.0)           # lands ON the PU finger
R.vwire(chip, ly, 2, 328.0, 349.0, 598.845, w=1.0)
R.hwire(chip, ly, 2, 367.5, 598.845, 328.0, w=1.0)             # west to VSSD's riser
R.via_stack(chip, ly, 2, 4, 367.5, 328.0)                      # joins VSSD -- same net
chip.shapes(ly.layer(36, 10)).insert(pya.DText("REF_IN_PU", pya.DTrans(pya.DVector(598.845, 349.5))))
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

ly.write(GDS)
print("routed power + GND ring + labels + DIEAREA boundary; wrote %s" % GDS)
