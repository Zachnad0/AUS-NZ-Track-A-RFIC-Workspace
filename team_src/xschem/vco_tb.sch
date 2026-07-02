v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 0 -1020 800 -620 {flags=graph
y1=-3
y2=3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=4.0005074e-08
x2=1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=out
color=4
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 0 -1580 800 -1180 {flags=graph
y1=2.0711775
y2=2.7878136
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=4.0005074e-08
x2=1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=x1.cap_bias
color=4
unitx=1
logx=0
logy=0
dataset=-1}
B 2 880 -1580 1680 -1180 {flags=graph
y1=-0.00036
y2=0.0022
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=4.0005074e-08
x2=1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node=i(v2)
color=4
dataset=-1
unitx=1
logx=0
logy=0
}
B 2 880 -1020 1680 -620 {flags=graph
y1=-0.059
y2=3.7
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=4.0005074e-08
x2=1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="out_p
out_n"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
}
N 490 -460 490 -440 {lab=out_p}
N 490 -460 600 -460 {lab=out_p}
N 490 -420 490 -400 {lab=out_n}
N 490 -400 600 -400 {lab=out_n}
N 400 -500 400 -490 {lab=#net1}
N 400 -570 400 -560 {lab=GND}
N 260 -430 260 -420 {lab=tune}
N 260 -430 320 -430 {lab=tune}
N 380 -210 380 -200 {lab=vsg}
N 380 -200 420 -200 {lab=vsg}
N 420 -200 420 -170 {lab=vsg}
N 420 -170 430 -170 {lab=vsg}
N 220 -130 380 -130 {lab=GND}
N 380 -140 380 -130 {lab=GND}
N 380 -130 470 -130 {lab=GND}
N 470 -140 470 -130 {lab=GND}
N 430 -330 470 -330 {lab=vss}
N 260 -360 260 -330 {lab=GND}
N 260 -330 370 -330 {lab=GND}
N 370 -170 380 -170 {lab=GND}
N 370 -170 370 -140 {lab=GND}
N 370 -140 380 -140 {lab=GND}
N 470 -140 480 -140 {lab=GND}
N 480 -170 480 -140 {lab=GND}
N 470 -170 480 -170 {lab=GND}
N 470 -330 470 -290 {lab=vss}
N 220 -130 220 -120 {lab=GND}
N 220 -150 220 -130 {lab=GND}
N 220 -230 380 -230 {lab=vsg}
N 380 -230 380 -210 {lab=vsg}
N 470 -220 470 -200 {lab=#net2}
N 220 -160 220 -150 {lab=GND}
N 220 -230 220 -220 {lab=vsg}
N 470 -230 470 -220 {lab=#net2}
C {title.sym} 160 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
C {gnd.sym} 260 -330 0 0 {name=l2 lab=GND}
C {res.sym} 600 -430 0 0 {name=R1
value=100k
footprint=1206
device=resistor
m=1}
C {vsource.sym} 400 -530 2 0 {name=V1 value=3.3 savecurrent=true}
C {vco_v1.sym} 340 -410 0 0 {name=x1}
C {gnd.sym} 400 -570 2 0 {name=l3 lab=GND}
C {vsource.sym} 260 -390 0 0 {name=V2 value=2.5 savecurrent=true}
C {lab_wire.sym} 560 -460 0 0 {name=p1 sig_type=std_logic lab=out_p}
C {lab_wire.sym} 560 -400 0 0 {name=p2 sig_type=std_logic lab=out_n}
C {code_shown.sym} 750 -570 0 0 {name=NGSPICE only_toplevel=true
value="
*.option keepopinfo

.control
  save all
  op
  let bias = v(x1.cap_bias) - v(out_p)
  print out_p bias x1.n_sources

  echo \\"===============================================================\\"
  tran 5p 100n 40n 10p
  let out = v(out_p) - v(out_n)
  write vco_tb.raw

  linearize v(out)
  let resulting_fft = mag(fft(v(out)))
  plot mag(resulting_fft) vs fft_scale xlimit 3G 7G
.endc
"}
C {lab_wire.sym} 290 -430 0 0 {name=p3 sig_type=std_logic lab=tune}
C {netlist.sym} 650 -200 0 0 {name=s1 value="
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice res_typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice moscap_typical
"}
C {launcher.sym} 100 -570 0 0 {name=h5
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/vco_tb.raw tran"
}
C {gnd.sym} 220 -120 0 0 {name=l4 lab=GND}
C {symbols/nfet_03v3.sym} 400 -170 0 1 {name=M2
L=0.28u
W=100u
nf=1
m=4
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 450 -170 0 0 {name=M1
L=0.28u
W=100u
nf=1
m=4
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {lab_wire.sym} 470 -330 0 0 {name=p4 sig_type=std_logic lab=vss}
C {ammeter.sym} 470 -260 0 0 {name=Viss_meas savecurrent=true spice_ignore=0}
C {lab_wire.sym} 400 -200 0 1 {name=p5 sig_type=std_logic lab=vsg
}
C {isource.sym} 220 -190 2 0 {name=I0 value=1m}
