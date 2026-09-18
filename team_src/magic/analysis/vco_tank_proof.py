#!/usr/bin/env python3
"""vco_tank_proof.py -- prove the VCO tank reaches BOTH inductor terminals.

This replaces the old "1a geometry proof" in phase5/vco_v1.tcl, which was run against the
magic ABSTRACT of vco_inductor_v2. The abstract carries no coil, so it could not see that
both output buses had been routed into the SAME terminal pad -- which is what happened: the
abstract's PORT1/PORT2 label rects were at 1/10 of the real coordinates, vco_v1.tcl took its
bus positions from them, and the two 38 um-apart terminals were treated as 3.8 um apart.

This proof reads the STREAMED coil instead, so it cannot be fooled the same way. It asserts:

  1. the coil's metal5 merges into exactly two polygons, one per terminal;
  2. each bus intersects exactly ONE of them;
  3. the two buses intersect DIFFERENT ones;
  4. neither bus touches the other's polygon.

Run:  python3 team_src/magic/analysis/vco_tank_proof.py [vco_v1.gds] [vco_inductor_v2.gds]
Exit 0 on proof, 1 on failure.
"""
import sys
import pya

REPO = "/foss/designs/AUS-NZ-integration"
V1 = sys.argv[1] if len(sys.argv) > 1 else REPO + "/gds/vco_v1.gds"
IND = sys.argv[2] if len(sys.argv) > 2 else REPO + "/gds/vco_inductor_v2.gds"
M5 = (81, 0)

ly = pya.Layout()
ly.read(V1)
v1 = ly.cell("vco_v1")
DBU = ly.dbu
lm5 = ly.layer(*M5)

tr = [i.trans for i in v1.each_inst() if i.cell.name == "vco_inductor_v2"]
if len(tr) != 1:
    print("FAIL: expected exactly one vco_inductor_v2 instance, found %d" % len(tr))
    sys.exit(1)
tr = tr[0]

il = pya.Layout()
il.read(IND)
coil = pya.Region(il.cell("vco_inductor_v2").begin_shapes_rec(il.layer(*M5)))
coil.merge()
coil = coil.transformed(pya.ICplxTrans(il.dbu / DBU) * pya.ICplxTrans(1.0)).transformed(tr) \
    if abs(il.dbu - DBU) > 1e-12 else coil.transformed(tr)
polys = sorted(coil.each(), key=lambda p: p.bbox().left)

print("coil metal5 merges into %d polygon(s)" % len(polys))
if len(polys) != 2:
    print("FAIL: expected 2 terminal polygons")
    sys.exit(1)
for k, p in enumerate(polys):
    b = p.bbox().to_dtype(DBU)
    print("   terminal %s  vco_v1 bbox (%.3f,%.3f)-(%.3f,%.3f)"
          % ("AB"[k], b.left, b.bottom, b.right, b.top))

# vco_v1's OWN metal5, split into connected pieces; the buses are the ones that reach the coil
own = pya.Region(v1.shapes(lm5))
own.merge()
coil_all = pya.Region()
for p in polys:
    coil_all.insert(p)
buses = own.interacting(coil_all)
print("vco_v1 own metal5 shapes reaching the coil: %d" % buses.count())

ok = True
hits = []
for bus in sorted(buses.each(), key=lambda p: p.bbox().left):
    br = pya.Region()
    br.insert(bus)
    bb = bus.bbox().to_dtype(DBU)
    touched = []
    for k, p in enumerate(polys):
        pr = pya.Region()
        pr.insert(p)
        if not (br & pr).is_empty():
            touched.append("AB"[k])
    hits.append((bb, touched))
    verdict = "OK" if len(touched) == 1 else "FAIL"
    if len(touched) != 1:
        ok = False
    print("   bus x %.3f..%.3f  y %.3f..%.3f  touches terminal(s) %s   %s"
          % (bb.left, bb.right, bb.bottom, bb.top, ",".join(touched) or "NONE", verdict))

seen = [t[0] for _, t in hits if len(t) == 1]
if len(hits) != 2:
    print("FAIL: expected exactly 2 buses reaching the coil, found %d" % len(hits))
    ok = False
elif len(set(seen)) != 2:
    print("FAIL: both buses land on terminal %s -- THE TANK IS SHORTED" % seen[0])
    ok = False
else:
    print("both buses land on different terminals (%s and %s)" % (seen[0], seen[1]))

print("RESULT: %s" % ("PASS -- the tank reaches both inductor terminals" if ok else "FAIL"))
sys.exit(0 if ok else 1)
