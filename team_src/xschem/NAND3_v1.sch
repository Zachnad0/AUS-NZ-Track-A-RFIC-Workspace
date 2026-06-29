v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 300 -540 370 -540 {lab=A}
N 300 -540 300 -440 {lab=A}
N 300 -440 370 -440 {lab=A}
N 300 -360 370 -360 {lab=B}
N 410 -410 410 -390 {lab=#net1}
N 410 -440 420 -440 {lab=#net1}
N 420 -440 420 -410 {lab=#net1}
N 410 -410 420 -410 {lab=#net1}
N 410 -540 420 -540 {lab=VDD}
N 420 -570 420 -540 {lab=VDD}
N 410 -570 420 -570 {lab=VDD}
N 580 -540 590 -540 {lab=VDD}
N 590 -570 590 -540 {lab=VDD}
N 580 -570 590 -570 {lab=VDD}
N 580 -600 580 -570 {lab=VDD}
N 410 -600 580 -600 {lab=VDD}
N 410 -600 410 -570 {lab=VDD}
N 410 -510 410 -490 {lab=Y}
N 410 -480 580 -480 {lab=Y}
N 580 -510 580 -490 {lab=Y}
N 410 -490 410 -480 {lab=Y}
N 410 -480 410 -470 {lab=Y}
N 410 -360 420 -360 {lab=#net2}
N 420 -360 420 -330 {lab=#net2}
N 410 -330 420 -330 {lab=#net2}
N 580 -480 670 -480 {lab=Y}
N 340 -500 340 -360 {lab=B}
N 340 -500 540 -500 {lab=B}
N 540 -540 540 -500 {lab=B}
N 580 -490 580 -480 {lab=Y}
N 740 -600 740 -570 {lab=VDD}
N 580 -600 740 -600 {lab=VDD}
N 670 -480 860 -480 {lab=Y}
N 740 -510 740 -480 {lab=Y}
N 410 -330 410 -300 {lab=#net2}
N 410 -240 410 -220 {lab=VSS}
N 330 -270 370 -270 {lab=C}
N 370 -270 370 -130 {lab=C}
N 370 -130 680 -130 {lab=C}
N 680 -540 680 -130 {lab=C}
N 680 -540 700 -540 {lab=C}
C {title.sym} 160 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
C {symbols/nfet_03v3.sym} 390 -360 0 0 {name=M1
L=0.28u
W=3u
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
C {symbols/nfet_03v3.sym} 390 -440 0 0 {name=M2
L=0.28u
W=3u
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
C {symbols/pfet_03v3.sym} 560 -540 0 0 {name=M3
L=0.28u
W=1u
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
C {symbols/pfet_03v3.sym} 390 -540 0 0 {name=M4
L=0.28u
W=1u
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
C {iopin.sym} 410 -220 1 0 {name=p1 lab=VSS}
C {iopin.sym} 410 -600 3 0 {name=p2 lab=VDD}
C {ipin.sym} 300 -440 0 0 {name=p3 lab=A}
C {opin.sym} 860 -480 0 0 {name=p4 lab=Y}
C {ipin.sym} 300 -360 0 0 {name=p5 lab=B}
C {symbols/pfet_03v3.sym} 720 -540 0 0 {name=M5
L=0.28u
W=1u
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
C {symbols/nfet_03v3.sym} 390 -270 0 0 {name=M6
L=0.28u
W=3u
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
C {ipin.sym} 330 -270 0 0 {name=p6 lab=C}
