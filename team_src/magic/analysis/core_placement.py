import math
SRC = {"VSSA":(89.62,206.10),"VDDA":(74.16,231.60),"IBIAS":(71.30,223.90),"ISS":(395.84,60.33),
 "VTUNE":(358.68,66.70),"CP_OUT":(272.25,215.41),"I_P":(235.18,140.27),"I_N":(2.18,140.27),
 "Q_P":(235.18,51.92),"Q_N":(2.18,51.92),"VDDD":(229.68,256.76),"REF_IN":(210.28,257.60)}
PAD = {"VSSA":(0.5,82.5),"VDDA":(0.5,182.5),"IBIAS":(0.5,282.5),"ISS":(0.5,382.5),"VTUNE":(0.5,482.5),
 "CP_OUT":(67.5,549),"I_P":(167.5,549),"I_N":(267.5,549),"Q_P":(367.5,549),"Q_N":(467.5,549),
 "VDDD":(567.5,549),"REF_IN":(666.5,549)}
IQ=["I_P","I_N","Q_P","Q_N"]
def man(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
def det(dx,dy,name):
    h={n:man((SRC[n][0]+dx,SRC[n][1]+dy),PAD[n]) for n in SRC}
    iq={n:h[n] for n in IQ}
    mx=max(iq.values()); mn=min(iq.values())
    matched=4*mx  # all padded up to the longest
    print("%-14s dx=%5.1f dy=%5.1f | IQ: "%(name,dx,dy)
          + " ".join("%s=%.0f"%(n,iq[n]) for n in IQ)
          + " | max=%.0f spread=%.0f matched4x=%.0f pad+=%.0f | ISS=%.0f VTUNE=%.0f VDDA=%.0f | allTot=%.0f"
          %(mx,mx-mn,matched,4*mx-sum(iq.values()),h["ISS"],h["VTUNE"],h["VDDA"],sum(h.values())))
print("dy=262.5 (core at top of DIEAREA), sweep dx:")
for dx in [25,100,150,200,243,300]:
    # fit check: boundary left=-25+dx>=0, right=497+dx<=1110 -> dx in [25,613]
    det(dx,262.5,"top dx%d"%dx)
print()
print("core boundary at dx=200,dy=262.5: x[%.0f,%.0f] y[%.0f,%.0f] in DIEAREA(1110x550)"
      %(-25+200,497+200,-21.5+262.5,287.5+262.5))
