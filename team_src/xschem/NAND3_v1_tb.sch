v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 0 -910 800 -510 {flags=graph
y1=0
y2=3.3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-08
x2=8
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
color="4 5 1"
node="a
b
c"}
B 2 0 -1310 800 -910 {flags=graph
y1=-0.00014
y2=3.3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-08
x2=8
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=y
color=1
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 800 -910 1600 -510 {flags=graph
y1=-0.00016
y2=5e-08
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1e-08
x2=8
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=i(vdd)
color=1
dataset=-1
unitx=1
logx=0
logy=0
}
N 80 -180 80 -130 {lab=GND}
N 80 -130 220 -130 {lab=GND}
N 160 -140 160 -130 {lab=GND}
N 120 -160 120 -130 {lab=GND}
N 160 -200 180 -200 {lab=C}
N 120 -220 180 -220 {lab=B}
N 80 -240 180 -240 {lab=A}
N 220 -160 220 -130 {lab=GND}
N 40 -280 220 -280 {lab=#net1}
N 40 -220 40 -130 {lab=GND}
N 40 -130 80 -130 {lab=GND}
N 270 -220 320 -220 {lab=Y}
N 220 -130 320 -130 {lab=GND}
N 320 -140 320 -130 {lab=GND}
N 320 -220 320 -200 {lab=Y}
C {NAND3_v1.sym} 200 -220 0 0 {name=x1}
C {gnd.sym} 220 -130 0 0 {name=l1 lab=GND}
C {vsource.sym} 40 -250 0 0 {name=VDD value=3.3 savecurrent=false}
C {res.sym} 320 -170 0 0 {name=R1
value=100k
footprint=1206
device=resistor
m=1}
C {devices/code_shown.sym} 400 -100 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/code_shown.sym} 390 -420 0 0 {name=NGSPICE only_toplevel=true
value="
VA A GND PULSE(0 3.3 0 1u 1u 1 2)
VB B GND PULSE(0 3.3 0 1u 1u 2 4)
VC C GND PULSE(0 3.3 0 1u 1u 4 8)

.control
  save all
  tran 1m 8 uic
  write NAND3_v1_tb.raw
.endc
"}
C {lab_wire.sym} 320 -220 0 0 {name=p1 sig_type=std_logic lab=Y}
C {launcher.sym} 190 -430 0 0 {name=h5
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/NAND3_v1_tb.raw tran"
}
C {lab_wire.sym} 130 -240 0 0 {name=p2 sig_type=std_logic lab=A}
C {lab_wire.sym} 140 -220 0 0 {name=p3 sig_type=std_logic lab=B}
C {lab_wire.sym} 160 -200 0 0 {name=p4 sig_type=std_logic lab=C}
