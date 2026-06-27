v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 -830 -610 -30 -210 {flags=graph
y1=1.1e-10
y2=0.0011
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3.3
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
node=i(gm1)
}
B 2 -830 -1010 -30 -610 {flags=graph
y1=7.4e-12
y2=0.0026
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3.3
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=i(vmeas)
color=4
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 -830 -210 -30 190 {flags=graph
y1=0.4
y2=28
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3.3
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
y1=3.8e-13
y2=0.0013
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3.3
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
node=i(gm2)
}
B 2 540 -1000 1340 -600 {flags=graph
y1=3.9e-12
y2=0.0025
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3.3
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=i(vmeas1)
color=4
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 540 -200 1340 200 {flags=graph
y1=0.096
y2=27
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3.3
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
N 300 -130 300 -110 {lab=gp}
N 150 -160 150 -130 {lab=gn}
N 300 -160 310 -160 {lab=gp}
N 300 -130 310 -130 {lab=gp}
N 310 -160 310 -130 {lab=gp}
N 140 -130 150 -130 {lab=gn}
N 140 -130 140 -100 {lab=gn}
N 140 -100 150 -100 {lab=gn}
N 190 -100 210 -100 {lab=gp}
N 240 -160 250 -160 {lab=gn}
N 250 -160 260 -160 {lab=gn}
N 300 -200 300 -190 {lab=#net1}
N 210 -100 240 -100 {lab=gp}
N 150 -160 240 -160 {lab=gn}
N 240 -100 300 -100 {lab=gp}
N 300 -110 300 -100 {lab=gp}
N 300 -100 390 -100 {lab=gp}
N 390 -200 390 -100 {lab=gp}
N 300 -260 390 -260 {lab=#net2}
N 50 0 150 0 {lab=#net3}
N 50 -160 50 -60 {lab=gn}
N 50 -160 150 -160 {lab=gn}
N 150 -70 150 -60 {lab=#net4}
C {symbols/nfet_03v3.sym} 280 -160 0 0 {name=M1
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
C {symbols/pfet_03v3.sym} 170 -100 0 1 {name=M2
L=0.28u
W=50u
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
C {vsource.sym} 240 -130 0 1 {name=V1 value=3.3 savecurrent=false}
C {simulator_commands_shown.sym} 30 -640 0 0 {name=COMMANDS
simulator=ngspice
only_toplevel=false 
value="
.control
dc V1 0 3.3 0.01

let gm1 = deriv(i(vmeas))
let gmid1 = gm1/i(vmeas)
let gm2 = deriv(i(vmeas1))
let gmid2 = gm2/i(vmeas1)

save all
write vco_mosfets_test.raw
.endc
"}
C {vsource.sym} 390 -230 0 0 {name=V3 value=3.3 savecurrent=false}
C {devices/code_shown.sym} 40 -760 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {launcher.sym} 120 -350 0 0 {name=h5
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/vco_mosfets_test.raw dc"
}
C {ammeter.sym} 300 -230 0 0 {name=Vmeas savecurrent=true spice_ignore=0}
C {ammeter.sym} 150 -30 0 0 {name=Vmeas1 savecurrent=true spice_ignore=0}
C {vsource.sym} 50 -30 0 0 {name=V2 value=3.3 savecurrent=false}
C {lab_wire.sym} 120 -160 0 0 {name=p1 sig_type=std_logic lab=gn}
C {lab_wire.sym} 340 -100 2 0 {name=p2 sig_type=std_logic lab=gp}
