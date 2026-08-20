# EM sizing: 1 mA/um for M2-M4, 2 mA/um for M5. width, current, mA/um, verdict.
RULE={"M4":1.0,"M5":2.0}
# per-block supply currents (mA): DIV2 on record (240uA*10:1*... + output buffers, 22.4mA);
# others estimated -- vco ~2 (LC tank + xcoupled, 1mA tail), CP ~0.5 (I_CP 50uA + switching),
# ibias ~1 (240uA ref + mirror branches), PFD ~0.5 (digital switching avg).
I={"DIV2":22.4,"PFD":0.5,"vco":2.0,"CP":0.5,"ibias":1.0}
VDDA=I["vco"]+I["CP"]+I["ibias"]; VDDD=I["DIV2"]+I["PFD"]; GND=sum(I.values()); ISS=1.0
segs=[
 ("GND","M5 bus","M5",15.0,GND),("VDDD","M5 bus","M5",12.0,VDDD),("VDDA","M5 bus","M5",3.0,VDDA),
 ("VDDD","DIV2.VDD riser","M4",23.0,I["DIV2"]),("GND","DIV2.VSS riser","M4",23.0,I["DIV2"]),
 ("VDDD","PFD.VDD riser","M4",1.0,I["PFD"]),("GND","PFD.VSS riser","M4",1.0,I["PFD"]),
 ("VDDA","vco.VDD riser","M4",2.0,I["vco"]),("GND","vco.GND riser","M4",2.0,I["vco"]),
 ("VDDA","CP.VDD riser","M4",2.0,I["CP"]),("GND","CP.VSS riser","M4",2.0,I["CP"]),
 ("VDDA","ibias.VDD riser","M4",2.0,I["ibias"]),("GND","ibias.VSS riser","M4",2.0,I["ibias"]),
 ("ISS","vco.ISS riser","M4",2.0,ISS),
]
print("%-6s %-16s %6s %7s %8s  %s"%("net","segment","width","I(mA)","mA/um","verdict"))
for net,seg,layer,w,i in segs:
    dens=i/w; ok=dens<=RULE[layer]
    print("%-6s %-16s %5.1fu %6.1f %7.2f  %s"%(net,seg,w,i,dens,"OK" if ok else "*** OVER ***"))
print()
print("Net currents (mA): VDDA=%.1f  VDDD=%.1f  GND=%.1f  ISS=%.1f"%(VDDA,VDDD,GND,ISS))
print("Band-fit: GND15 + VDDD12 + VDDA3 + 2x1 spacing = %d um vs the 25 um band"%(15+12+3+2))
print("  -> does NOT fit stacked; put the 15um GND strap in a grown BOTTOM margin")
print("     (DIV2.VSS reaches y6.4, 6.4um from the die bottom -> taps straight down).")
