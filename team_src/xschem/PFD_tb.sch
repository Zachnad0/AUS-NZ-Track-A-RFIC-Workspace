v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 300 -430 1100 -30 {flags=graph
y1=0.44000714
y2=2.0400075
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-2.6345904e-08
x2=3.3775968e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
sim_type=tran
autoload=1
rawfile=/headless/.xschem/simulations/PFD_tb.raw
digital=1
color="21 4 7 7"
node="net5
x1.net1
x1.net3
x1.net2"}
N -320 -110 -160 -40 {lab=#net1}
N -320 -0 -160 -20 {lab=#net2}
N 140 -40 210 -40 {lab=#net3}
C {PFD_v1.sym} -10 -10 0 0 {name=x1}
C {vsource.sym} -320 -80 0 0 {name=V1 value="PULSE(0 1.8 0 100p 100p 500n 1u)" savecurrent=false}
C {vsource.sym} -320 30 0 0 {name=V2 value="PULSE(0 1.8 100n 100p 100p 500n 1u)" savecurrent=false}
C {vsource.sym} 210 -10 0 0 {name=V3 value=1.8 savecurrent=false}
C {gnd.sym} -320 -50 0 0 {name=l1 lab=0}
C {gnd.sym} -320 60 0 0 {name=l2 lab=0}
C {gnd.sym} 210 20 0 0 {name=l3 lab=0}
C {gnd.sym} 140 0 3 0 {name=l4 lab=0}
C {code_shown.sym} -70 150 0 0 {name=s1 only_toplevel=false value="
.param fnoicor=0
.param sw_stat_global=0
.param sw_stat_mismatch=0
.param sw_mc_global=0
.param sw_mc_mismatch=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.control
tran 100p 5u
write PFD_tb.raw
.endc
"}
C {lab_pin.sym} 140 -20 2 0 {name=p1 sig_type=std_logic lab=UP}
C {lab_pin.sym} 140 20 2 0 {name=p2 sig_type=std_logic lab=DOWN}
