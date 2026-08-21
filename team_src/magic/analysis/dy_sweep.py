#!/usr/bin/env python3
# dy_sweep.py -- sweep the core's dy in the BH DIEAREA (dx=200 fixed, proposed pad order
# Q_N,I_N,I_P,Q_P) against the channel_map. Reports matched haul, the clear channel height
# above the core (empty die between the core-north edge and the pad row), and whether the
# horizontal lanes+serpentine fit in it. Analysis only.
import math
DX = 200.0
TAP = {"I_P": (235.18,140.27), "I_N": (2.18,140.27), "Q_P": (235.18,51.92), "Q_N": (2.18,51.92)}
PAD = {"Q_N":167.5, "I_N":267.5, "I_P":367.5, "Q_P":467.5}   # proposed order -> slot x-centre
PADY = 549.0
CORE_TOP = 287.5   # core boundary top in chip frame; DIEAREA core-top = 287.5+dy
def man(t, px, py): return abs(px-t[0]) + abs(py-t[1])
# lane+serpentine budget: 4 M3 lanes @ ~5um pitch (20) + meander amplitude to absorb the
# 58um spread (~2 fingers of ~15um = 30) + pad-drop margin (~10) ~= 60um needed.
NEED = 60.0
print("dx=200, proposed order Q_N,I_N,I_P,Q_P")
print("%-6s %-9s %-9s %-9s %-8s %s" % ("dy","matched","perOut","channel","lanesFit","note"))
for dy in [100,130,160,180,200,220,240,262.5]:
    hauls = {n: man((TAP[n][0]+DX, TAP[n][1]+dy), PAD[n], PADY) for n in TAP}
    mx = max(hauls.values()); matched = 4*mx
    channel = PADY - (CORE_TOP + dy) - 1.0   # empty gap: pad inner edge y549 down to core top, minus pad depth
    fit = "yes" if channel >= NEED else ("TIGHT" if channel >= 40 else "NO")
    note = ""
    if channel < 0: note = "core reaches pad row -- lanes over blocks (last-session problem)"
    elif channel < 40: note = "not enough for lanes+serpentine"
    elif channel < NEED: note = "lanes fit but serpentine cramped"
    print("%-6.1f %-9.1f %-9.1f %-9.1f %-8s %s" % (dy, matched, mx, channel, fit, note))
print("\nrisers (dy-independent): taps at chip x2.18 (Q_N/I_N) and x235.18 (I_P/Q_P).")
print("clear columns of M2&M3 in y[175,287.5]: x181-204, x288-397, x406-472 (chip frame).")
print("x2.18 sits under ibias(x0.7-180) -> riser must jog right to the x181-204 gap before rising.")
print("x235.18 sits under CP(x210-283)  -> riser must jog to x288-397 before rising.")
print("both jogs are horizontal (M2/M3) crossing the block/riser stack on a DIFFERENT layer.")
