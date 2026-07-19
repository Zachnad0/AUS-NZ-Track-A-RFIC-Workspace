v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -30 -30 -0 -30 {lab=VDD}
N -30 -10 -0 -10 {lab=CLK}
N -30 10 -0 10 {lab=RST}
N 70 -110 70 -70 {lab=VDD}
N 70 50 70 80 {lab=VSS}
N 130 -30 180 -30 {lab=Q}
N 130 10 180 10 {lab=QB}
N 130 -30 160 -80 {lab=Q}
N 220 -80 240 -80 {lab=VSS}
N 130 10 160 70 {lab=QB}
N 220 70 240 70 {lab=VSS}
C {D_FF_RST_v1.sym} 70 -10 0 0 {name=x1}
C {lab_pin.sym} -30 -30 0 0 {name=p1 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -30 -10 0 0 {name=p2 sig_type=std_logic lab=CLK}
C {lab_pin.sym} -30 10 0 0 {name=p3 sig_type=std_logic lab=RST}
C {lab_pin.sym} 70 -110 0 0 {name=p4 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 70 80 0 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 180 -30 2 0 {name=p7 sig_type=std_logic lab=Q}
C {lab_pin.sym} 180 10 2 0 {name=p8 sig_type=std_logic lab=QB}
C {res.sym} 190 -80 3 0 {name=R1
value=100k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 240 -80 2 0 {name=p6 sig_type=std_logic lab=VSS}
C {res.sym} 190 70 3 0 {name=R2
value=100k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 240 70 2 0 {name=p9 sig_type=std_logic lab=VSS}
C {code_shown.sym} -90 100 0 0 {name=s1 only_toplevel=false value="
VDD VDD 0 1.8
VSS VSS 0 0
VCLK CLK 0 PULSE(0 1.8 0 1n 1n 500n 1u)
VRST RST 0 PULSE(0 1.8 200n 1n 1n 10 20)

.control
  tran 10p 5u
  write DFF_tb.raw
.endc
"}
C {code_shown.sym} -120 -220 0 0 {name=s2 only_toplevel=false value="
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
"}
