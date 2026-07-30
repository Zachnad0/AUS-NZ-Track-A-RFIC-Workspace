v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 -570 -600 230 -200 {flags=graph
y1=1
y2=1000
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=9.6434451
x2=9.8581934
divx=5
subdivx=8
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
unitx=1
logx=1
logy=0
hilight_wave=-1
vlegend=0
rainbow=0
digital=0
dataset=-1
color=4
node=out}
N 600 -720 620 -720 {lab=GND}
N 600 -720 600 -700 {lab=GND}
N 450 -720 520 -720 {lab=out_p}
N 450 -720 450 -600 {lab=out_p}
N 680 -720 740 -720 {lab=out_n}
N 740 -720 740 -600 {lab=out_n}
N 600 -540 600 -520 {lab=GND}
N 450 -600 450 -320 {lab=out_p}
N 740 -600 740 -320 {lab=out_n}
N 740 -600 760 -600 {lab=out_n}
N 430 -600 450 -600 {lab=out_p}
N 600 -840 610 -840 {lab=GND}
N 600 -840 600 -720 {lab=GND}
N 520 -840 530 -840 {lab=out_p}
N 520 -840 520 -720 {lab=out_p}
N 670 -840 680 -840 {lab=out_n}
N 680 -840 680 -720 {lab=out_n}
N 580 -720 600 -720 {lab=GND}
N 590 -840 600 -840 {lab=GND}
N 360 -320 450 -320 {lab=out_p}
N 740 -320 830 -320 {lab=out_n}
N 360 -260 390 -260 {lab=GND}
N 800 -260 830 -260 {lab=GND}
N 360 -260 360 -250 {lab=GND}
N 800 -260 800 -250 {lab=GND}
N 560 -260 560 -240 {lab=out_p}
N 630 -260 630 -240 {lab=out_n}
N 560 -180 630 -180 {lab=GND}
N 510 -180 560 -180 {lab=GND}
N 630 -320 630 -260 {lab=out_n}
N 560 -320 560 -260 {lab=out_p}
N 450 -320 560 -320 {lab=out_p}
N 630 -320 740 -320 {lab=out_n}
C {vco_inductor_v2.sym} 480 -620 0 0 {}
C {gnd.sym} 600 -520 0 0 {name=l1 lab=GND}
C {simulator_commands_shown.sym} 870 -785 0 0 {name=COMMANDS
simulator=ngspice
only_toplevel=false 
value="
.param Cvar = 1400f
.control
  ac dec 1000 1G 100G
  let out = out_p - out_n
  save out
  write vco_tank_tb.raw
.endc
"}
C {launcher.sym} 80 -170 0 0 {name=h5
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/vco_tank_tb.raw ac"
}
C {gnd.sym} 360 -250 0 0 {name=l2 lab=GND}
C {title.sym} 170 -40 0 0 {name=l3 author="Team A1 AUS/NZ Track A RFIC"}
C {capa.sym} 390 -290 0 0 {name=C3
m=1
value=39f
footprint=1206
device="ceramic capacitor"}
C {isource.sym} 650 -720 3 0 {name=Iin0 value="0 AC 0.5"}
C {isource.sym} 550 -720 3 0 {name=Iin1 value="0 AC 0.5"}
C {gnd.sym} 600 -700 0 0 {name=l4 lab=GND}
C {lab_pin.sym} 760 -600 2 0 {name=p1 sig_type=std_logic lab=out_n}
C {lab_pin.sym} 430 -600 0 0 {name=p2 sig_type=std_logic lab=out_p}
C {res.sym} 560 -840 3 0 {name=R1
value=100k
footprint=1206
device=resistor
m=1}
C {res.sym} 640 -840 3 0 {name=R2
value=100k
footprint=1206
device=resistor
m=1}
C {capa.sym} 560 -210 0 0 {name=C1
m=1
value=\{Cvar\}
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 630 -210 0 0 {name=C2
m=1
value=\{Cvar\}
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 360 -290 0 1 {name=C5
m=1
value=97f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 800 -290 0 1 {name=C6
m=1
value=39f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 830 -290 0 0 {name=C7
m=1
value=97f
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 800 -250 0 0 {name=l5 lab=GND}
C {gnd.sym} 510 -180 0 0 {name=l6 lab=GND}
