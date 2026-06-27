v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 -830 -610 -30 -210 {flags=graph
y1=0.00038
y2=0.0088
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-05
x2=0.01
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
color=4
node=gm1
hcursor1_y=0.0065833803}
B 2 -830 -1010 -30 -610 {flags=graph
y1=0.55
y2=2.1
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-05
x2=0.01
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
color=4
node="v(nsource) -1 *"}
B 2 -830 -210 -30 190 {flags=graph
y1=1.3
y2=20
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-05
x2=0.01
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=gmid1
color=4
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 540 -600 1340 -200 {flags=graph
y1=0.00035
y2=0.011
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-05
x2=0.01
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
color=4
node=gm2
hcursor1_y=0.0058291434}
B 2 540 -1000 1340 -600 {flags=graph
y1=0.68
y2=2.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-05
x2=0.01
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=v(psource)
color=4
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 540 -200 1340 200 {flags=graph
y1=0.82
y2=17
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-05
x2=0.01
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=gmid2
color=4
dataset=-1
unitx=1
logx=0
logy=0
}
N 140 -120 150 -120 {lab=nsource}
N 150 -120 150 -90 {lab=nsource}
N 340 -70 340 -40 {lab=psource}
N 340 -40 350 -40 {lab=psource}
N 340 -70 350 -70 {lab=psource}
N 140 -90 150 -90 {lab=nsource}
N 180 -230 280 -230 {lab=GND}
N 180 -290 280 -290 {lab=#net1}
N 50 -180 140 -180 {lab=#net2}
N 140 -180 140 -150 {lab=#net2}
N 50 -120 100 -120 {lab=GND}
N 50 -120 50 -110 {lab=GND}
N 140 0 140 10 {lab=GND}
N 140 -90 140 -60 {lab=nsource}
N 350 -120 350 -100 {lab=psource}
N 350 -100 350 -70 {lab=psource}
N 350 -190 350 -180 {lab=GND}
N 350 -10 350 20 {lab=#net3}
N 350 20 430 20 {lab=#net3}
N 390 -40 430 -40 {lab=GND}
N 430 -40 450 -40 {lab=GND}
C {symbols/nfet_03v3.sym} 120 -120 0 0 {name=M1
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
C {symbols/pfet_03v3.sym} 370 -40 0 1 {name=M2
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
C {vsource.sym} 280 -260 2 1 {name=V0 value=0 savecurrent=false}
C {simulator_commands_shown.sym} 30 -820 0 0 {name=COMMANDS
simulator=ngspice
only_toplevel=false 
value="
.control
* dc I0 10u 10m 10u
* let gm1 = -1/deriv(v(nsource))
* let gmid1 = gm1/i(v0)
* let gm2 = 1/deriv(v(psource))
* let gmid2 = gm2/i(v0)

alter I0 2m
op
echo \\"--- Extracted nMOS and pMOS Internal Capacitances ---\\"
show : cgs cgd cgb cbd cds

save all
write vco_mosfets_test_2.raw
.endc
"}
C {devices/code_shown.sym} 40 -940 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {launcher.sym} 110 -460 0 0 {name=h5
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/vco_mosfets_test_2.raw dc"
}
C {lab_wire.sym} 140 -70 0 1 {name=p1 sig_type=std_logic lab=nsource}
C {lab_wire.sym} 350 -100 2 0 {name=p2 sig_type=std_logic lab=psource}
C {cccs.sym} 140 -30 0 0 {name=F1 vnam=v0 value=1}
C {isource.sym} 180 -260 0 0 {name=I0 value=0}
C {vsource.sym} 50 -150 0 1 {name=V1 value=1 savecurrent=false}
C {gnd.sym} 50 -110 0 1 {name=l1 lab=GND}
C {gnd.sym} 140 10 0 1 {name=l2 lab=GND}
C {cccs.sym} 350 -150 0 0 {name=F2 vnam=v0 value=1}
C {vsource.sym} 430 -10 0 1 {name=V2 value=3.3 savecurrent=false}
C {gnd.sym} 450 -40 0 0 {name=l3 lab=GND}
C {gnd.sym} 350 -190 2 0 {name=l4 lab=GND}
C {gnd.sym} 230 -230 0 0 {name=l5 lab=GND}
