import gdspy
lib=gdspy.GdsLibrary(infile="/foss/designs/AUS-NZ-integration/gds/vco_v1.gds"); top=lib.top_level()[0]
ox,oy=402.0,119.48
LN={34:"M1",36:"M2",42:"M3",46:"M4",81:"M5"}
def bb(p):
    xs=[q[0] for q in p]; ys=[q[1] for q in p]; return min(xs),min(ys),max(xs),max(ys)
def ov(a,b,t): return not (a[2]+t<b[0] or b[2]+t<a[0] or a[3]+t<b[1] or b[3]+t<a[1])
def net_shapes(layer,seed,tol=0.05):
    bbs=[bb(p) for p in top.get_polygons(by_spec=True).get((layer,0),[])]
    grp=set(i for i,b in enumerate(bbs) if b[0]-tol<=seed[0]<=b[2]+tol and b[1]-tol<=seed[1]<=b[3]+tol)
    ch=True
    while ch:
        ch=False
        for i,b in enumerate(bbs):
            if i in grp: continue
            if any(ov(b,bbs[j],tol) for j in grp): grp.add(i); ch=True
    return [bbs[i] for i in grp]
# vco.VDD M2 net extent (label local -4.57,-44.65)
vdd=net_shapes(36,(-4.57,-44.65))
print("vco.VDD M2: chip x[%.1f,%.1f] y[%.1f,%.1f]"%(min(s[0] for s in vdd)+ox,max(s[2] for s in vdd)+ox,min(s[1] for s in vdd)+oy,max(s[3] for s in vdd)+oy))
# OUT_p M5 (local -0.2,-25) and OUT_n M5 (local -4,-25)
for nm,seed in [("OUT_p",(-0.2,-25.0)),("OUT_n",(-4.0,-25.0))]:
    sh=net_shapes(81,seed)
    if sh:
        print("%s M5: chip x[%.1f,%.1f] y[%.1f,%.1f] (%d sh)"%(nm,min(s[0] for s in sh)+ox,max(s[2] for s in sh)+ox,min(s[1] for s in sh)+oy,max(s[3] for s in sh)+oy,len(sh)))
# what layers occupy the far-end column x[405,412] over y[74,199]?
print("--- obstacles in far-end riser column x[405,412] y[74,199] ---")
seen=set()
for (lyr,dt),polys in top.get_polygons(by_spec=True).items():
    if lyr not in LN or dt!=0: continue
    for p in polys:
        x0,y0,x1,y1=bb(p); X0,X1,Y0,Y1=x0+ox,x1+ox,y0+oy,y1+oy
        if X0<412 and X1>405 and Y0<199 and Y1>74:
            key=(LN[lyr],round(Y0),round(Y1));
            if key not in seen: seen.add(key); print("  %s y[%.1f,%.1f] x[%.1f,%.1f]"%(LN[lyr],Y0,Y1,X0,X1))
