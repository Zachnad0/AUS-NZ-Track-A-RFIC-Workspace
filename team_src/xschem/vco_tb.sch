v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 10 -1080 810 -680 {flags=graph
y1=-0.31963704
y2=0.32836296
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1.013867e-06
x2=1.0144515e-06
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
y1=-0.86527627
y2=4.0649703
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1.013867e-06
x2=1.0144515e-06
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
x1=1.013867e-06
x2=1.0144515e-06
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
B 2 890 -1080 1690 -680 {flags=graph
y1=1.0186855
y2=3.5530856
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1.013867e-06
x2=1.0144515e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="out_p
out_n
net1
net2"
color="4 5 18 6"
dataset=-1
unitx=1
logx=0
logy=0
}
N 490 -460 490 -440 {lab=#net1}
N 490 -480 600 -480 {lab=#net1}
N 490 -420 490 -400 {lab=#net2}
N 400 -500 400 -490 {lab=vdd}
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
N 470 -220 470 -200 {lab=#net3}
N 220 -160 220 -150 {lab=GND}
N 220 -230 220 -220 {lab=vsg}
N 470 -230 470 -220 {lab=#net3}
N 490 -480 490 -460 {lab=#net1}
N 390 -550 400 -550 {lab=vdd}
N 310 -550 330 -550 {lab=GND}
N 310 -550 310 -530 {lab=GND}
N 490 -400 490 -310 {lab=#net2}
N 490 -310 600 -310 {lab=#net2}
N 560 -230 600 -230 {lab=vsg}
N 640 -280 640 -260 {lab=out_n}
N 640 -200 640 -190 {lab=GND}
N 400 -550 400 -500 {lab=vdd}
N 640 -350 640 -340 {lab=vdd}
N 670 -450 670 -430 {lab=out_p}
N 670 -370 670 -360 {lab=GND}
N 670 -520 670 -510 {lab=vdd}
N 590 -400 630 -400 {lab=vsg}
N 600 -480 630 -480 {lab=#net1}
N 640 -270 810 -270 {lab=out_n}
N 810 -300 810 -270 {lab=out_n}
N 810 -440 810 -360 {lab=out_p}
N 670 -440 810 -440 {lab=out_p}
N 670 -480 680 -480 {lab=out_p}
N 680 -480 680 -440 {lab=out_p}
N 640 -310 650 -310 {lab=out_n}
N 650 -310 650 -270 {lab=out_n}
N 640 -230 650 -230 {lab=GND}
N 650 -230 650 -200 {lab=GND}
N 640 -200 650 -200 {lab=GND}
N 670 -400 680 -400 {lab=GND}
N 680 -400 680 -370 {lab=GND}
N 670 -370 680 -370 {lab=GND}
C {title.sym} 160 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
C {gnd.sym} 260 -330 0 0 {name=l2 lab=GND}
C {res.sym} 810 -330 0 0 {name=R1
value=50
footprint=1206
device=resistor
m=1}
C {vsource.sym} 360 -550 1 0 {name=V1 value=3.3 savecurrent=true}
C {vco_v1.sym} 340 -410 0 0 {name=x1}
C {gnd.sym} 310 -530 0 0 {name=l3 lab=GND}
C {vsource.sym} 260 -390 0 0 {name=V2 value=1.5 savecurrent=true}
C {lab_wire.sym} 810 -440 0 0 {name=p1 sig_type=std_logic lab=out_p}
C {lab_wire.sym} 790 -270 0 0 {name=p2 sig_type=std_logic lab=out_n}
C {code_shown.sym} 950 -650 0 0 {name=NGSPICE only_toplevel=true
value="
*.option keepopinfo
.option reltol=1e-5
.option method=gear
.option numparam jobs=4
.option bypass=0

.control
  save all
  op
  let bias = v(x1.cap_bias) - v(out_p)
  print out_p bias vss

  echo \\"===============================================================\\"
  *tran 5p 100n 40n 10p
  tran 5p 1.04u 40n 5p
  let out = v(out_p) - v(out_n)
  let pow_out = out*out / 50
  print mean(pow_out)
  write vco_tb.raw

  linearize v(out)
  let out_fft = mag(fft(v(out)))
  let pow_fft = 10*log10(out_fft*out_fft / 50 * 1e3)
  *plot out_fft vs fft_scale xlimit 3G 7G
  plot pow_fft vs fft_scale
.endc
"}
C {lab_wire.sym} 290 -430 0 0 {name=p3 sig_type=std_logic lab=tune}
C {netlist.sym} 870 -180 0 0 {name=s1 value="
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
C {symbols/nfet_03v3.sym} 620 -310 0 0 {name=M3
L=0.28u
W=50u
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
C {lab_wire.sym} 560 -230 0 1 {name=p6 sig_type=std_logic lab=vsg
}
C {symbols/nfet_03v3.sym} 620 -230 0 0 {name=M4
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
C {gnd.sym} 640 -190 0 0 {name=l5 lab=GND}
C {lab_wire.sym} 400 -550 2 0 {name=p7 sig_type=std_logic lab=vdd}
C {lab_wire.sym} 640 -350 0 0 {name=p8 sig_type=std_logic lab=vdd}
C {symbols/nfet_03v3.sym} 650 -480 0 0 {name=M5
L=0.28u
W=50u
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
C {symbols/nfet_03v3.sym} 650 -400 0 0 {name=M6
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
C {gnd.sym} 670 -360 0 0 {name=l6 lab=GND}
C {lab_wire.sym} 670 -520 0 0 {name=p9 sig_type=std_logic lab=vdd}
C {lab_wire.sym} 590 -400 0 1 {name=p10 sig_type=std_logic lab=vsg
}
