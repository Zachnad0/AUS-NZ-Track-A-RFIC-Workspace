#!/usr/bin/env python3
# route_lib.py -- DRC-correct KLayout routing primitives for gf180mcuD (5LM, variant D).
# Coordinates in um. Layers (GDS): M1 34, via1 35, M2 36, via2 38, M3 42, via3 40,
# M4 46, via4 41, M5 81. All vias are EXACTLY 0.26um (V*.1 min/max). Metal min width
# M1 0.23, M2-M4 0.28, M5 0.44; M5 min area 0.5625 um2. Via metal-overlap >= 0.06 (V*.3d/4c),
# and metal landing >= 0.34 wide to dodge the <0.34um end-of-line via rules.
import pya
import math

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


def via1_small(cell, ly, m_lo, m_hi, x, y, pad=0.38):
    """single via between adjacent metals with a MINIMAL landing pad (for tight std-cell pins:
    0.26 via + 0.06 enclosure/side = 0.38um). Use where a 0.5um pad would hit a neighbour."""
    v = VIA_SIZE / 2.0
    box(cell, ly, VIA_BETWEEN[m_lo], x - v, y - v, x + v, y + v)
    p = pad / 2.0
    for m in (m_lo, m_hi):
        box(cell, ly, METAL[m], x - p, y - p, x + p, y + p)


def via_stack_small(cell, ly, m_from, m_to, x, y, pad=0.38):
    lo, hi = (m_from, m_to) if m_from <= m_to else (m_to, m_from)
    for m in range(lo, hi):
        via1_small(cell, ly, m, m + 1, x, y, pad)


# ---------------------------------------------------------------------------
# Phase-8 haul infrastructure: length accounting, serpentine matching, def-pin
# landing. Parameterized primitives -- built & DRC-gated in isolation
# (route_selftest_phase8.py), NOT wired into chip_merge.py / route_chip.py.
# ---------------------------------------------------------------------------
MINSP = {1: 0.23, 2: 0.28, 3: 0.28, 4: 0.28, 5: 0.28}  # min same-layer spacing (gf180 M*.2)
LABEL_DT = 10                                            # port labels on datatype 10


def path_length(pts):
    """Manhattan length of an orthogonal polyline (== true length when axis-aligned)."""
    return sum(abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1])
               for i in range(len(pts) - 1))


def route_path(cell, ly, m, pts, w=None):
    """Draw an orthogonal polyline on metal m; return its routed length (length
    accounting). Each consecutive pair must be axis-aligned."""
    w = w or MINW[m]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if abs(ya - yb) < 1e-9 and abs(xa - xb) > 1e-9:
            hwire(cell, ly, m, xa, xb, ya, w)
        elif abs(xa - xb) < 1e-9 and abs(ya - yb) > 1e-9:
            vwire(cell, ly, m, ya, yb, xa, w)
        elif abs(xa - xb) < 1e-9 and abs(ya - yb) < 1e-9:
            continue  # zero-length hop
        else:
            raise ValueError("route_path: non-axis-aligned segment %r->%r" % ((xa, ya), (xb, yb)))
    return path_length(pts)


def meander_points(x0, x1, y, extra, w, m, amp=3.0):
    """Orthogonal polyline from (x0,y) to (x1,y) whose length exceeds the straight span
    by `extra` um, via upward fingers of target height ~`amp`. n fingers = extra/(4*amp);
    if the span cannot hold that many at min pitch, n is capped to the span and the finger
    height grows to still hit `extra` (a taller meander for a short lane). The caller must
    ensure the finger height fits the available channel. Returns the point list.
    Raises only if a single finger at min pitch already overshoots `extra`."""
    span = abs(x1 - x0)
    d = 1.0 if x1 >= x0 else -1.0
    if extra <= 1e-6 or span <= 1e-6:
        return [(x0, y), (x1, y)]
    sp = MINSP[m]
    half_pitch_min = w + sp + 0.10          # min leg-to-leg pitch (up-leg to down-leg)
    amp_min = (w + sp + 0.10) / 2.0         # min finger height so top/bottom legs clear
    amp = max(amp, amp_min)
    if extra < 4.0 * amp_min:               # even one minimum finger overshoots
        raise ValueError("meander: extra %.2fum below one min finger (%.2fum); set "
                         "target >= max_base + %.2f" % (extra, 4.0 * amp_min, 4.0 * amp_min))
    n_fit = max(1, int(span / (2.0 * half_pitch_min)))   # max fingers the span allows
    n = max(1, int(round(extra / (4.0 * amp))))          # from target amplitude
    if n > n_fit:
        n = n_fit                                        # span-limited: fewer, taller fingers
    amp = extra / (4.0 * n)                               # exact; height grows if n capped
    p = span / (2.0 * n)                    # half-pitch
    pts = [(x0, y)]
    cx = x0
    for _ in range(n):
        pts.append((cx, y + 2 * amp))       # up
        cx += d * p
        pts.append((cx, y + 2 * amp))       # across top
        pts.append((cx, y))                 # down
        cx += d * p
        pts.append((cx, y))                 # across bottom to next finger
    if abs(cx - x1) > 1e-6:
        pts.append((x1, y))
    return pts


def matched_route(cell, ly, m, nets, ych_base, lane_pitch, target=None, w=None):
    """Length-matched N-net (pair/quad) router. `nets` = list of (name, x0,y0, x1,y1)
    endpoints (tap -> pad). Net i routes: vertical tap->its own channel lane
    (ych_base + i*lane_pitch), horizontal across (serpentine-padded to `target`),
    vertical lane->pad. Own lane per net => no self-short. If `target` is None it is
    the max base length. Returns (lengths dict, target)."""
    w = w or MINW[m]
    base = {}
    lanes = {}
    for i, (name, x0, y0, x1, y1) in enumerate(nets):
        ych = ych_base + i * lane_pitch
        lanes[name] = ych
        base[name] = abs(ych - y0) + abs(x1 - x0) + abs(ych - y1)
    if target is None:
        target = max(base.values())
    out = {}
    for (name, x0, y0, x1, y1) in nets:
        ych = lanes[name]
        extra = target - base[name]
        pts = [(x0, y0), (x0, ych)]                       # tap up to lane
        pts += meander_points(x0, x1, ych, extra, w, m)[1:]  # meandered horizontal
        pts += [(x1, ych), (x1, y1)]                      # lane down to pad
        out[name] = route_path(cell, ly, m, pts, w)
    return out, target


def land_on_pin(cell, ly, m, approach, pin_rect, label=None, w=None):
    """Land a haul arriving at `approach`=(x,y) on metal m onto a DEF pin rectangle
    `pin_rect`=(x0,y0,x1,y1) um (Metal2, at the die edge). Fills the pin rect on M2,
    stacks m<->M2 at the pin centre if m!=2, L-routes `approach`->pin on m, and drops
    a port `label` on M2 datatype 10. Returns the pin centre."""
    w = w or MINW[m]
    x0, y0, x1, y1 = pin_rect
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    # fill the def pin rect on M2, padded to >= M2 min width in each axis (centred) so a
    # sub-min-width DEF pin (e.g. the ~0.38um in_c pins) still lands DRC-clean.
    mw = MINW[2]
    fx0, fx1 = (x0, x1) if (x1 - x0) >= mw else (cx - mw / 2.0, cx + mw / 2.0)
    fy0, fy1 = (y0, y1) if (y1 - y0) >= mw else (cy - mw / 2.0, cy + mw / 2.0)
    box(cell, ly, METAL[2], fx0, fy0, fx1, fy1)           # fill the def pin rect (M2)
    if m != 2:
        via_stack(cell, ly, 2, m, cx, cy)                 # tie haul layer to the M2 pin
    ax, ay = approach
    route_path(cell, ly, m, [(ax, ay), (ax, cy), (cx, cy)], w)  # L: vert then horiz
    if label:
        cell.shapes(ly.layer(METAL[2][0], LABEL_DT)).insert(
            pya.DText(label, pya.DTrans(pya.DVector(cx, cy))))
    return (cx, cy)
