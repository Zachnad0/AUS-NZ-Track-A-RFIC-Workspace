v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 0 -950 800 -550 {flags=graph
y1=360
y2=1300
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1
divx=5
subdivx=4
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
rainbow=0
vlegend=0
color=4
node=vec_c}
N 430 -340 430 -330 {lab=GND}
N 430 -330 430 -310 {lab=GND}
N 430 -420 430 -400 {lab=cap_v}
N 280 -420 280 -400 {lab=cap_v}
N 280 -420 310 -420 {lab=cap_v}
N 370 -420 430 -420 {lab=cap_v}
N 280 -340 280 -330 {lab=GND}
N 280 -330 430 -330 {lab=GND}
N 310 -420 370 -420 {lab=cap_v}
C {devices/code_shown.sym} 640 -220 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/sm141064.ngspice res_typical
.lib $::180MCU_MODELS/sm141064.ngspice moscap_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {title.sym} 160 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
C {symbols/cap_nmos_03v3_b.sym} 430 -370 2 1 {name=C1
W=30u
L=1.3u
model=cap_nmos_03v3_b
spiceprefix=X
m=10}
C {gnd.sym} 430 -310 0 0 {name=l2 lab=GND}
C {lab_wire.sym} 380 -420 0 0 {name=p1 sig_type=std_logic lab=cap_v}
C {code_shown.sym} 860 -950 0 0 {name=NGSPICE only_toplevel=true
value="
*.option keepopinfo

*.control
*  save all
*  AC dec 1k 0.1G 100G
*  let capacitance = -i(v1) / (2*pi*frequency*(0, 1))
*  write vco_varactor_tb.raw
*.endc

.control
  save all
  let v_start = 0
  let v_stop = 3.3
  let v_n = 100
  let v_act = v_start

  let vec_v = vector(v_n)
  let vec_c = vector(v_n)
  let iN = 0

  while v_act <= v_stop
    alter V1 = v_act
    AC lin 1 10Meg 10Meg

    let cap_step = imag(-i(V1)) / (2 * pi * frequency) * 1e15
*    print v_act cap_step
*    print ph(-i(V1))*180/pi

    let vec_v[iN] = v_act
    let vec_c[iN] = re(cap_step)
    let iN = iN + 1
    let v_act = v_act + ((v_stop - v_start) / v_n)
  end
  setplot const
*  write vco_varactor_tb.raw vec_c vec_v
  plot vec_c vs vec_v
.endc
"}
C {launcher.sym} 70 -520 0 0 {name=h5
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/vco_varactor_tb.raw ac"
}
C {vsource.sym} 280 -370 0 0 {name=V1 value="1.5 AC 1" savecurrent=true}
