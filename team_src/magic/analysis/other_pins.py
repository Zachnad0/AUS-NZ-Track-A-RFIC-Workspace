DX, DY = 200.0, 200.0
def die(c): return (c[0]+DX, c[1]+DY)
def man(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
# block taps (chip coords, port_map primary tap)
SRC = {
 "VSSA":("GND ring west spur", None),           # perimeter -- ring extension = dx-25 = 175um
 "VDDA":("ibias.VDD", (74.16,231.60)),
 "IBIAS":("ibias.IBIAS", (71.30,223.90)),
 "ISS":("vco.ISS", (395.84,60.33)),
 "VTUNE":("vco.TUNE", (358.68,66.70)),
 "CP_OUT":("CP.CP_OUT", (272.25,215.41)),
 "VDDD":("PFD.VDD", (229.68,256.76)),
 "REF_IN":("PFD.REF", (210.28,257.60)),
 "REF_IN_PU":("tie->VSS ring", None),
 "REF_IN_PD":("tie->VDD bus", None),
}
PAD = {  # die frame
 "VSSA":(0.5,82.5),"VDDA":(0.5,182.5),"IBIAS":(0.5,282.5),"ISS":(0.5,382.5),"VTUNE":(0.5,482.5),
 "CP_OUT":(67.5,549),"VDDD":(567.5,549),"REF_IN":(666.5,549),"REF_IN_PU":(699.0,549),"REF_IN_PD":(694.0,549),
}
print("dx=200 dy=200 -- other-ten-pin hauls")
print("%-10s %-16s %-9s %-8s %s" % ("pad","source","edge","haul um","note"))
for p in ["VSSA","VDDA","IBIAS","ISS","VTUNE","CP_OUT","VDDD","REF_IN","REF_IN_PU","REF_IN_PD"]:
    name, tap = SRC[p]
    edge = "west" if PAD[p][0] < 5 else "north"
    if tap is None:
        if p=="VSSA": h="~175 (spur)"
        else: h="short tie"
        print("%-10s %-16s %-9s %-8s %s" % (p,name,edge,h,"rail/ring -- clear"))
        continue
    h = man(die(tap), PAD[p])
    note = ""
    if h > 600: note = "LONG (vco on right -> west pad, crosses full die)"
    elif h > 450: note = "long (up-and-across)"
    print("%-10s %-16s %-9s %-8.1f %s" % (p,name,edge,h,note))
