#!/usr/bin/env python3
# iss_net.py -- flood-fill the ISS net inside vco_v1.gds from its port label and report the
# net's real geometry, its distance to each block edge, and its widest conductors.
#
# WHY: 3o called the ISS escape "blocked at every y". That sweep probed 2 um wide starting at
# x592 -- INSIDE the ISS net's own strap and source fingers -- so it counted ISS's own metal as
# an obstacle. 3g had warned about exactly this: an escape from a block-interior tap needs the
# block's port/net context to tell a same-net touch from a cross-net short. This gets the
# context without re-opening the block.
#
# Result (plan doc 3p): ISS is a single 25.78 x 0.40 um M2 strap at die y260.13-260.53 plus 12
# M1 source fingers -- the common-source TAIL node of the cross-coupled pair, carrying
# 1.24-1.57 mA DC plus 2f0. It reaches no block edge (nearest 59.17 um, east).
#
# Run: klayout -b -r team_src/magic/analysis/iss_net.py
# NOT the flow -- an analysis harness. Writes nothing.
import pya

REPO = "/foss/designs/AUS-NZ-integration"
ly = pya.Layout(); ly.read(REPO + "/gds/vco_v1.gds")
top = ly.cell("vco_v1")
top.flatten(-1, True)
DBU = ly.dbu

# vco_v1 own frame -> die frame
OX, OY = 602.0, 319.48

MET = {"M1": 34, "M2": 36, "M3": 42, "M4": 46, "M5": 81}
VIA = {"v1": 35, "v2": 38, "v3": 40, "v4": 41}
STACK = ["M1", "v1", "M2", "v2", "M3", "v3", "M4", "v4", "M5"]

def region(layer):
    li = ly.layer(layer, 0)
    return pya.Region(top.begin_shapes_rec(li))

R = {}
for nm, l in list(MET.items()) + list(VIA.items()):
    R[nm] = region(l)

print("vco_v1 bbox (own frame): %s" % top.dbbox())
print("die frame offset: +(%.2f, %.2f)" % (OX, OY))
print()

# seed: the ISS label sits on M2 at own (-6.17, -59.15)
seed_pt = pya.DPoint(-6.17, -59.15)
seed_box = pya.DBox(seed_pt.x - 0.05, seed_pt.y - 0.05, seed_pt.x + 0.05, seed_pt.y + 0.05)
seed = R["M2"].interacting(pya.Region(seed_box.to_itype(DBU)))
print("seed M2 shapes under the ISS label: %d" % seed.count())

net = {k: pya.Region() for k in R}
net["M2"] = seed

for it in range(12):
    grew = False
    for i, nm in enumerate(STACK):
        neigh = []
        if i > 0: neigh.append(STACK[i - 1])
        if i < len(STACK) - 1: neigh.append(STACK[i + 1])
        acc = pya.Region()
        for nb in neigh:
            if net[nb].count():
                acc = acc + R[nm].interacting(net[nb])
        acc = acc + R[nm].interacting(net[nm]) if net[nm].count() else acc
        acc.merge()
        before = net[nm].count()
        net[nm] = (net[nm] + acc)
        net[nm].merge()
        if net[nm].count() != before:
            grew = True
    if not grew:
        print("converged after %d passes" % (it + 1))
        break

print()
print("=== ISS net geometry inside vco_v1 ===")
allbb = pya.Box()
for nm in STACK:
    n = net[nm].count()
    if not n:
        continue
    bb = net[nm].bbox()
    allbb += bb
    print("  %-3s %3d shapes  own (%7.2f,%7.2f)-(%7.2f,%7.2f)   die (%7.2f,%7.2f)-(%7.2f,%7.2f)"
          % (nm, n, bb.left * DBU, bb.bottom * DBU, bb.right * DBU, bb.top * DBU,
             bb.left * DBU + OX, bb.bottom * DBU + OY, bb.right * DBU + OX, bb.top * DBU + OY))

b = allbb
print()
print("ISS net TOTAL bbox own (%7.2f,%7.2f)-(%7.2f,%7.2f)" % (b.left*DBU, b.bottom*DBU, b.right*DBU, b.top*DBU))
print("ISS net TOTAL bbox die (%7.2f,%7.2f)-(%7.2f,%7.2f)" % (b.left*DBU+OX, b.bottom*DBU+OY, b.right*DBU+OX, b.top*DBU+OY))

vb = top.dbbox()
print()
print("=== how close does the ISS net get to each vco_v1 edge? ===")
print("  vco west  edge own x=%7.2f (die %7.2f) : ISS net reaches x=%7.2f -> gap %7.2f um"
      % (vb.left, vb.left + OX, b.left * DBU, b.left * DBU - vb.left))
print("  vco east  edge own x=%7.2f (die %7.2f) : ISS net reaches x=%7.2f -> gap %7.2f um"
      % (vb.right, vb.right + OX, b.right * DBU, vb.right - b.right * DBU))
print("  vco south edge own y=%7.2f (die %7.2f) : ISS net reaches y=%7.2f -> gap %7.2f um"
      % (vb.bottom, vb.bottom + OY, b.bottom * DBU, b.bottom * DBU - vb.bottom))
print("  vco north edge own y=%7.2f (die %7.2f) : ISS net reaches y=%7.2f -> gap %7.2f um"
      % (vb.top, vb.top + OY, b.top * DBU, vb.top - b.top * DBU))

print()
print("=== widest ISS conductors (top 12 shapes by area, die coords) ===")
shapes = []
for nm in STACK:
    for p in net[nm].each():
        bb = p.bbox()
        shapes.append((p.area() * DBU * DBU, nm, bb))
shapes.sort(reverse=True, key=lambda s: s[0])
for a, nm, bb in shapes[:12]:
    print("  %-3s area %8.2f um2  die (%7.2f,%7.2f)-(%7.2f,%7.2f)  %6.2f x %6.2f"
          % (nm, a, bb.left*DBU+OX, bb.bottom*DBU+OY, bb.right*DBU+OX, bb.top*DBU+OY,
             (bb.right-bb.left)*DBU, (bb.top-bb.bottom)*DBU))
