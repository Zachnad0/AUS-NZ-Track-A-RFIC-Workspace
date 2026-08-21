#!/usr/bin/env python3
# phase8_dryrun.py -- rehearse route_lib.matched_route on the REAL phase-8 numbers in a
# throwaway cell. Placement dx=200, dy from argv (default 200), proposed order
# Q_N,I_N,I_P,Q_P, lanes in the clear channel above the core. Reports matched length,
# magic-DRC-ready GDS, the route bbox, and an OVERLAP CHECK of the route's M3 against each
# block's M3/M2 (from the committed GDS, shifted to the DIEAREA frame). NOT the flow.
import pya, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase5"))
import route_lib as R

DX = 200.0
DY = float(os.environ.get("PHASE8_DY", "200"))
def die(cx, cy): return (cx + DX, cy + DY)

TAP = {"I_P": (235.18,140.27), "I_N": (2.18,140.27), "Q_P": (235.18,51.92), "Q_N": (2.18,51.92)}
PADX = {"x145":167.5, "x245":267.5, "x345":367.5, "x445":467.5}
ORDER = [("Q_N","x145"), ("I_N","x245"), ("I_P","x345"), ("Q_P","x445")]
nets = [(n, *die(*TAP[n]), PADX[s], 549.0) for n, s in ORDER]

ly = pya.Layout(); ly.dbu = 0.005
cell = ly.create_cell("test_phase8_dryrun")
core_top = 287.5 + DY
ych = core_top + 3.0    # lanes just above the core, in the clear channel
lengths, target = R.matched_route(cell, ly, 3, nets, ych_base=ych, lane_pitch=8.0, w=0.4)
print("dy=%.1f  matched target=%.3f um  lanes at y~%.1f (channel y[%.1f,549])" % (DY, target, ych, core_top))
ok = True
for n, _ in ORDER:
    e = lengths[n] - target
    if abs(e) >= 1.0: ok = False
    print("  %-4s routed=%.3f err=%+.4f %s" % (n, lengths[n], e, "OK" if abs(e) < 1.0 else "FAIL"))
bb = cell.dbbox(); print("route bbox: (%.1f,%.1f)-(%.1f,%.1f)" % (bb.left, bb.bottom, bb.right, bb.top))

# --- overlap check: route M3 vs each block's M3 and M2, shifted to DIEAREA (dx,dy) ---
route_m3 = pya.Region(cell.begin_shapes_rec(ly.layer(42, 0))); route_m3.merge()
src = pya.Layout(); src.read("/foss/designs/AUS-NZ-integration/gds/chip_top.gds")
stop = src.cell("chip_top")
itr = {}
for it in stop.each_inst(): itr.setdefault(it.cell.name, it.trans)
shift = pya.ICplxTrans(1.0, 0.0, False, int(DX/src.dbu), int(DY/src.dbu))
print("route-M3 vs block metal (DIEAREA frame):")
for b in ["ibias_gen_v1","CP_v1","PFD_lib","DIV2_QUAD_v1","vco_v1"]:
    for lname, lnum in [("M3",42),("M2",36)]:
        br = pya.Region(src.cell(b).begin_shapes_rec(src.layer(lnum,0)))
        br = br.transformed(itr[b]).transformed(shift)
        inter = route_m3 & br
        if not inter.is_empty():
            ib = inter.bbox()
            print("  CONFLICT route-M3 x %s.%s : overlap (%.1f,%.1f)-(%.1f,%.1f) area=%.1f"
                  % (b, lname, ib.left*src.dbu, ib.bottom*src.dbu, ib.right*src.dbu, ib.top*src.dbu, inter.area()*src.dbu*src.dbu))
out = "/foss/designs/AUS-NZ-integration/gds/test_phase8_dryrun.gds"
ly.write(out); print("wrote", out, "| match:", "PASS" if ok else "FAIL")
