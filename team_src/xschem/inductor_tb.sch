v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 -130 -790 670 -390 {flags=graph
y1=0.15
y2=6.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-13
x2=1e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1
vlegend=0
color=4
node=out}
B 2 670 -790 1470 -390 {flags=graph
y1=-0.43
y2=0.033
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-13
x2=1e-08
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
node=i(v1)}
T {Step response looks fine} 370 -340 0 0 0.4 0.4 {}
N 70 -90 70 -80 {lab=GND}
N 70 -80 360 -80 {lab=GND}
N 360 -120 360 -80 {lab=GND}
N 70 -180 70 -150 {lab=#net1}
N 70 -180 110 -180 {lab=#net1}
N 170 -180 210 -180 {lab=#net1}
N 500 -180 540 -180 {lab=OUT}
N 110 -180 170 -180 {lab=#net1}
N 540 -180 540 -150 {lab=OUT}
N 540 -90 540 -80 {lab=GND}
N 360 -80 540 -80 {lab=GND}
N 360 -80 360 -70 {lab=GND}
N 540 -190 540 -180 {lab=OUT}
C {vco_inductor_v2.sym} 240 -200 0 0 {}
C {gnd.sym} 360 -70 0 0 {name=l1 lab=GND}
C {vsource.sym} 70 -120 0 0 {name=V1 value=0 savecurrent=false}
C {simulator_commands_shown.sym} 720 -250 0 0 {name=COMMANDS
simulator=ngspice
only_toplevel=false 
value="
.control
save all
* dc V1 0 3.3 0.01
alter V1 = 3.3
tran 10p 10n uic
write inductor_tb.raw
.endc
"}
C {launcher.sym} 80 -350 0 0 {name=h5
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/inductor_tb.raw tran"
}
C {lab_wire.sym} 540 -190 0 0 {name=p1 sig_type=std_logic lab=OUT}
C {symbols/ppolyf_u_2k.sym} 540 -120 0 0 {name=R1
W=1u
L=10u
model=ppolyf_u_2k
spiceprefix=X
m=1}
