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
