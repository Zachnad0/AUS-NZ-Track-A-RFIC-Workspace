v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 300 -430 370 -430 {lab=A}
N 300 -430 300 -330 {lab=A}
N 300 -330 370 -330 {lab=A}
N 300 -250 370 -250 {lab=B}
N 410 -220 410 -200 {lab=VSS}
N 410 -300 410 -280 {lab=#net1}
N 410 -330 420 -330 {lab=#net1}
N 420 -330 420 -300 {lab=#net1}
N 410 -300 420 -300 {lab=#net1}
N 410 -430 420 -430 {lab=VDD}
N 420 -460 420 -430 {lab=VDD}
N 410 -460 420 -460 {lab=VDD}
N 580 -430 590 -430 {lab=VDD}
N 590 -460 590 -430 {lab=VDD}
N 580 -460 590 -460 {lab=VDD}
N 580 -490 580 -460 {lab=VDD}
N 410 -490 580 -490 {lab=VDD}
N 410 -490 410 -460 {lab=VDD}
N 410 -400 410 -380 {lab=Y}
N 410 -370 580 -370 {lab=Y}
N 580 -400 580 -380 {lab=Y}
N 410 -380 410 -370 {lab=Y}
N 410 -370 410 -360 {lab=Y}
N 410 -250 420 -250 {lab=VSS}
N 420 -250 420 -220 {lab=VSS}
N 410 -220 420 -220 {lab=VSS}
N 580 -370 670 -370 {lab=Y}
N 340 -390 340 -250 {lab=B}
N 340 -390 540 -390 {lab=B}
N 540 -430 540 -390 {lab=B}
N 580 -380 580 -370 {lab=Y}
C {title.sym} 160 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
C {symbols/nfet_03v3.sym} 390 -250 0 0 {name=M1
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
model=nfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 390 -330 0 0 {name=M2
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
model=nfet_03v3
spiceprefix=X
}
C {symbols/pfet_03v3.sym} 560 -430 0 0 {name=M3
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
C {symbols/pfet_03v3.sym} 390 -430 0 0 {name=M4
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
C {iopin.sym} 410 -200 1 0 {name=p1 lab=VSS}
C {iopin.sym} 410 -490 3 0 {name=p2 lab=VDD}
C {ipin.sym} 300 -330 0 0 {name=p3 lab=A}
C {opin.sym} 670 -370 0 0 {name=p4 lab=Y}
C {ipin.sym} 300 -250 0 0 {name=p5 lab=B}
