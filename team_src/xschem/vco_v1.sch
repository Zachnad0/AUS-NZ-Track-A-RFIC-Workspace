v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 320 -500 320 -350 {lab=OUT_n}
N 610 -500 610 -350 {lab=OUT_p}
N 470 -610 470 -600 {lab=GND}
N 320 -770 320 -640 {lab=OUT_n}
N 610 -770 610 -640 {lab=OUT_p}
N 320 -850 320 -830 {lab=VDD}
N 320 -870 320 -850 {lab=VDD}
N 320 -870 610 -870 {lab=VDD}
N 610 -870 610 -830 {lab=VDD}
N 300 -870 320 -870 {lab=VDD}
N 320 -290 320 -250 {lab=ISS}
N 440 -160 460 -160 {lab=ISS}
N 610 -290 610 -250 {lab=ISS}
N 360 -800 440 -800 {lab=OUT_p}
N 490 -800 570 -800 {lab=OUT_n}
N 440 -800 480 -760 {lab=OUT_p}
N 440 -750 490 -800 {lab=OUT_n}
N 480 -760 490 -750 {lab=OUT_p}
N 490 -750 610 -750 {lab=OUT_p}
N 320 -750 440 -750 {lab=OUT_n}
N 360 -320 440 -320 {lab=OUT_p}
N 490 -320 570 -320 {lab=OUT_n}
N 440 -320 490 -370 {lab=OUT_p}
N 440 -370 490 -320 {lab=OUT_n}
N 320 -370 440 -370 {lab=OUT_n}
N 490 -370 610 -370 {lab=OUT_p}
N 280 -750 320 -750 {lab=OUT_n}
N 610 -750 650 -750 {lab=OUT_p}
N 320 -640 320 -500 {lab=OUT_n}
N 610 -640 610 -500 {lab=OUT_p}
N 320 -250 610 -250 {lab=ISS}
N 460 -250 460 -220 {lab=ISS}
N 310 -800 320 -800 {lab=VDD}
N 310 -830 310 -800 {lab=VDD}
N 310 -830 320 -830 {lab=VDD}
N 610 -800 620 -800 {lab=VDD}
N 620 -830 620 -800 {lab=VDD}
N 610 -830 620 -830 {lab=VDD}
N 310 -320 320 -320 {lab=ISS}
N 310 -320 310 -290 {lab=ISS}
N 310 -290 320 -290 {lab=ISS}
N 610 -320 620 -320 {lab=ISS}
N 620 -320 620 -290 {lab=ISS}
N 610 -290 620 -290 {lab=ISS}
N 580 -580 580 -560 {lab=OUT_p}
N 580 -580 610 -580 {lab=OUT_p}
N 320 -580 350 -580 {lab=OUT_n}
N 350 -520 350 -500 {lab=cap_bias}
N 580 -500 580 -490 {lab=cap_bias}
N 350 -490 580 -490 {lab=cap_bias}
N 350 -500 350 -490 {lab=cap_bias}
N 440 -420 460 -420 {lab=TUNE}
N 460 -430 460 -420 {lab=TUNE}
N 460 -220 460 -160 {lab=ISS}
C {title.sym} 160 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
C {symbols/nfet_03v3.sym} 590 -320 0 0 {name=M1
L=0.28u
W=40u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {symbols/pfet_03v3.sym} 590 -800 0 0 {name=M2
L=0.28u
W=70u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
C {vco_inductor_v2.sym} 350 -690 0 0 {name=X1
}
C {iopin.sym} 300 -870 2 0 {name=p1 lab=VDD}
C {iopin.sym} 440 -160 2 0 {name=p2 lab=ISS}
C {iopin.sym} 470 -600 2 0 {name=p3 lab=GND}
C {ipin.sym} 440 -420 0 0 {name=p4 lab=TUNE}
C {opin.sym} 650 -750 0 0 {name=p5 lab=OUT_p}
C {opin.sym} 280 -750 2 0 {name=p6 lab=OUT_n}
C {symbols/pfet_03v3.sym} 340 -800 0 1 {name=M3
L=0.28u
W=70u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 340 -320 0 1 {name=M4
L=0.28u
W=40u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {res.sym} 460 -460 0 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {capa.sym} 110 -490 0 0 {name=C2
m=1
value=1.7p
footprint=1206
device="ceramic capacitor"
spice_ignore=true}
C {capa.sym} 190 -490 0 0 {name=C3
m=1
value=1.7p
footprint=1206
device="ceramic capacitor"
spice_ignore=true}
C {symbols/cap_nmos_03v3_b.sym} 350 -550 2 1 {name=C1
W=5u
L=5u
model=cap_nmos_03v3_b
spiceprefix=X
m=20}
C {symbols/cap_nmos_03v3_b.sym} 580 -530 2 0 {name=C4
W=5u
L=5u
model=cap_nmos_03v3_b
spiceprefix=X
m=20}
C {lab_wire.sym} 420 -490 0 0 {name=p8 sig_type=std_logic lab=cap_bias}
