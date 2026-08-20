#!/usr/bin/env python3
# vss_extent.py -- each block's VSS/GND metal extent + closest block edge, to plan the GND ring.
import gdspy
GDS = "/foss/designs/AUS-NZ-integration/gds"
ORIG = {"DIV2_QUAD_v1": (65.0, 105.0), "vco_v1": (402.0, 119.48),
        "ibias_gen_v1": (7.66, 209.10), "CP_v1": (237.25, 228.01), "PFD_lib": (210.0, 245.0)}
LNUM = {"M1": 34, "M2": 36, "M3": 42, "M4": 46, "M5": 81}
def bb(p):
    xs=[q[0] for q in p]; ys=[q[1] for q in p]; return min(xs),min(ys),max(xs),max(ys)
def ov(a,b,t): return not (a[2]+t<b[0] or b[2]+t<a[0] or a[3]+t<b[1] or b[3]+t<a[1])
def net_shapes(top,layer,seed,tol=0.05):
    bbs=[bb(p) for p in top.get_polygons(by_spec=True).get((layer,0),[])]
    grp=set(i for i,b in enumerate(bbs) if b[0]-tol<=seed[0]<=b[2]+tol and b[1]-tol<=seed[1]<=b[3]+tol)
    ch=True
    while ch:
        ch=False
        for i,b in enumerate(bbs):
            if i in grp: continue
            if any(ov(b,bbs[j],tol) for j in grp): grp.add(i); ch=True
    return [bbs[i] for i in grp]
# block, net, layer, local label
VSS=[("DIV2_QUAD_v1","VSS","M2",88.0,-26.3),("ibias_gen_v1","VSS","M2",81.96,-3.0),
     ("CP_v1","VSS","M2",0.0,-14.4),("PFD_lib","VSS","M4",22.98,11.76),
     ("vco_v1","GND","M1",-43.5,-69.7)]
for blk,net,lyr,lx,ly_ in VSS:
    top=gdspy.GdsLibrary(infile="%s/%s.gds"%(GDS,blk)).top_level()[0]
    ox,oy=ORIG[blk]; b=top.get_bounding_box(); blx,bly,bux,buy=b[0][0],b[0][1],b[1][0],b[1][1]
    sh=net_shapes(top,LNUM[lyr],(lx,ly_))
    if not sh: print(blk,net,"NO shape"); continue
    nx0=min(s[0] for s in sh); ny0=min(s[1] for s in sh); nx1=max(s[2] for s in sh); ny1=max(s[3] for s in sh)
    e={"L":nx0-blx,"R":bux-nx1,"B":ny0-bly,"T":buy-ny1}; near=min(e,key=e.get)
    print("%-13s %s %s: %2d sh chip x[%.1f,%.1f] y[%.1f,%.1f] nearest %s %.1fum  block y[%.1f,%.1f]"
          %(blk,net,lyr,len(sh),nx0+ox,nx1+ox,ny0+oy,ny1+oy,near,e[near],bly+oy,buy+oy))
