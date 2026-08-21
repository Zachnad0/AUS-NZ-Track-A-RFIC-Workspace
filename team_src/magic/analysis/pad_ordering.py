import itertools, math
# taps (chip coords) and placement dx=200 dy=262.5
DX, DY = 200.0, 262.5
TAP = {"I_P": (235.18,140.27), "I_N": (2.18,140.27), "Q_P": (235.18,51.92), "Q_N": (2.18,51.92)}
TAPD = {k: (v[0]+DX, v[1]+DY) for k,v in TAP.items()}   # tap in DIEAREA frame
# the four north analog pad slots (x centre, y549) between CP_OUT(x45) and VDDD(x531)
SLOT = [167.5, 267.5, 367.5, 467.5]   # slot centres for x145/245/345/445 rects
def man(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
outs = ["I_P","I_N","Q_P","Q_N"]
rows=[]
for perm in itertools.permutations(outs):     # perm[i] -> SLOT[i]
    h={perm[i]: man(TAPD[perm[i]], (SLOT[i],549.0)) for i in range(4)}
    mx=max(h.values()); mn=min(h.values())
    # crossing count: taps I_N/Q_N are LEFT (x2), I_P/Q_P RIGHT (x235). A crossing when a
    # left-tap net sits at a slot to the RIGHT of a right-tap net (their wires cross).
    xtap={n:TAP[n][0] for n in outs}; xslot={perm[i]:SLOT[i] for i in range(4)}
    cross=0
    for a in outs:
        for b in outs:
            if xtap[a]<xtap[b] and xslot[a]>xslot[b]: cross+=1
    cross//=1
    rows.append((mx-mn, 4*mx, sum(h.values()), cross, perm, tuple(round(h[n]) for n in outs)))
rows.sort(key=lambda r:(r[0], r[1]))
print("ordering sweep @ dx200,dy262.5  (perm = net at slot x145/245/345/445)")
print("%-28s %-7s %-8s %-7s %-6s %s"%("perm (x145,245,345,445)","spread","matched","total","cross","hauls IP/IN/QP/QN"))
seen=set()
for sp,matched,tot,cross,perm,hauls in rows:
    key=(round(sp),round(matched))
    print("%-28s %6.1f %8.1f %7.1f %5d   %s"%(",".join(perm),sp,matched,tot,cross,hauls))
print("\ncurrent (info.yaml) order I_P,I_N,Q_P,Q_N -> slots x145,245,345,445:")
cur=("I_P","I_N","Q_P","Q_N")
h={cur[i]: man(TAPD[cur[i]],(SLOT[i],549.0)) for i in range(4)}
print("  spread=%.1f matched=%.1f total=%.1f"%(max(h.values())-min(h.values()),4*max(h.values()),sum(h.values())))
