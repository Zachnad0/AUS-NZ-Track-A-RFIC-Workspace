v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 480 -300 480 -280 {lab=Y}
N 480 -380 480 -360 {lab=VDD}
N 410 -330 440 -330 {lab=A}
N 440 -330 440 -250 {lab=A}
N 480 -290 560 -290 {lab=Y}
N 480 -220 480 -200 {lab=VSS}
C {title.sym} 170 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
C {symbols/nfet_03v3.sym} 460 -250 0 0 {name=M2
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
C {symbols/pfet_03v3.sym} 460 -330 0 0 {name=M4
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
C {iopin.sym} 480 -200 1 0 {name=p1 lab=VSS}
C {iopin.sym} 480 -380 3 0 {name=p2 lab=VDD}
C {ipin.sym} 410 -330 0 0 {name=p3 lab=A}
C {opin.sym} 560 -290 0 0 {name=p4 lab=Y}
