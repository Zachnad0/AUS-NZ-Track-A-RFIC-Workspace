import gdspy
GDS="/foss/designs/AUS-NZ-integration/gds"
ORIG={"DIV2_QUAD_v1":(65.0,105.0),"vco_v1":(402.0,119.48)}
def bbox(p):
    xs=[q[0] for q in p]; ys=[q[1] for q in p]; return min(xs),min(ys),max(xs),max(ys)
COLS={"vco_v1":[370,380,400,410,420,440,460,470],"DIV2_QUAD_v1":[120,140,160,180,200,220,235]}
for blk in ["vco_v1","DIV2_QUAD_v1"]:
    lib=gdspy.GdsLibrary(infile="%s/%s.gds"%(GDS,blk)); top=lib.top_level()[0]
    ox,oy=ORIG[blk]
    m5=[bbox(p) for p in top.get_polygons(by_spec=True).get((81,0),[])]
    maxx=max(b[2] for b in m5)+ox; minx=min(b[0] for b in m5)+ox
    print("%s: M5 chip x[%.1f,%.1f] (%d shapes)"%(blk,minx,maxx,len(m5)))
    for xc in COLS[blk]:
        xl=xc-ox
        blocked=[b for b in m5 if b[0]-0.3<=xl<=b[2]+0.3]
        if not blocked:
            print("    x=%d: M5 CLEAR"%xc)
        else:
            yr=[(round(b[1]+oy,1),round(b[3]+oy,1)) for b in blocked][:4]
            print("    x=%d: blocked by %d, y-ranges %s"%(xc,len(blocked),yr))
