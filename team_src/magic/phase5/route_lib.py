#!/usr/bin/env python3
# route_lib.py -- DRC-correct KLayout routing primitives for gf180mcuD (5LM, variant D).
# Coordinates in um. Layers (GDS): M1 34, via1 35, M2 36, via2 38, M3 42, via3 40,
# M4 46, via4 41, M5 81. All vias are EXACTLY 0.26um (V*.1 min/max). Metal min width
# M1 0.23, M2-M4 0.28, M5 0.44; M5 min area 0.5625 um2. Via metal-overlap >= 0.06 (V*.3d/4c),
# and metal landing >= 0.34 wide to dodge the <0.34um end-of-line via rules.
import pya

DB = 1000  # KLayout DBU per um is set on the layout; we pass um via DVector/DBox helpers.

METAL = {1: (34, 0), 2: (36, 0), 3: (42, 0), 4: (46, 0), 5: (81, 0)}
VIA = {12: (35, 0), 23: (38, 0), 34: (42 if False else 40, 0), 45: (41, 0)}  # via1,2,3,4
# via between metal n and n+1:
VIA_BETWEEN = {1: (35, 0), 2: (38, 0), 3: (40, 0), 4: (41, 0)}
VIA_SIZE = 0.26
PAD = {1: 0.50, 2: 0.50, 3: 0.50, 4: 0.50, 5: 0.80}  # square via-landing pad side per metal
MINW = {1: 0.30, 2: 0.30, 3: 0.30, 4: 0.30, 5: 0.44}


def _layer(ly, spec):
    return ly.layer(spec[0], spec[1])


def box(cell, ly, spec, x1, y1, x2, y2):
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    cell.shapes(_layer(ly, spec)).insert(pya.DBox(x1, y1, x2, y2))


def hwire(cell, ly, m, x1, x2, y, w=None):
    """horizontal wire on metal m, centerline y, from x1 to x2, width w."""
    w = w or MINW[m]
    h = w / 2.0
    xa, xb = (x1, x2) if x1 <= x2 else (x2, x1)
    box(cell, ly, METAL[m], xa - h, y - h, xb + h, y + h)  # extend by half-width at ends


def vwire(cell, ly, m, y1, y2, x, w=None):
    """vertical wire on metal m, centerline x, from y1 to y2, width w."""
    w = w or MINW[m]
    h = w / 2.0
    ya, yb = (y1, y2) if y1 <= y2 else (y2, y1)
    box(cell, ly, METAL[m], x - h, ya - h, x + h, y + h if False else yb + h)


def via1_at(cell, ly, m_lo, m_hi, x, y):
    """single via between adjacent metals m_lo,m_hi (=m_lo+1) at (x,y) with landing pads."""
    assert m_hi == m_lo + 1
    v = VIA_SIZE / 2.0
    box(cell, ly, VIA_BETWEEN[m_lo], x - v, y - v, x + v, y + v)
    for m in (m_lo, m_hi):
        p = PAD[m] / 2.0
        box(cell, ly, METAL[m], x - p, y - p, x + p, y + p)


def via_stack(cell, ly, m_from, m_to, x, y):
    """stack vias from metal m_from up/down to m_to at (x,y), all landing pads painted."""
    lo, hi = (m_from, m_to) if m_from <= m_to else (m_to, m_from)
    for m in range(lo, hi):
        via1_at(cell, ly, m, m + 1, x, y)
