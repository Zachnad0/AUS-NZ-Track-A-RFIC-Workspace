v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {D_FF_RST_v1.sym} 0 0 0 0 {name=x1}
C {lab_pin.sym} -70 -20 0 0 {name=lD lab=DFB}
C {lab_pin.sym} 60 20 0 0 {name=lQb lab=DFB}
C {lab_pin.sym} 60 -20 0 0 {name=lQ lab=QOUT}
C {lab_pin.sym} -70 0 0 0 {name=lclk lab=CLK}
C {lab_pin.sym} -70 20 0 0 {name=lrst lab=RST}
C {lab_pin.sym} 0 -60 0 0 {name=lvdd lab=VDD}
C {gnd.sym} 0 60 0 0 {name=lvss lab=0}
C {vsource.sym} -400 0 0 0 {name=V_CLK value="PULSE(0 3.3 1500p 10p 10p 480p 1000p)" savecurrent=false}
C {lab_pin.sym} -400 -30 0 0 {name=lclks lab=CLK}
C {gnd.sym} -400 30 0 0 {name=lgclk lab=0}
C {vsource.sym} -400 150 0 0 {name=V_RST value="PULSE(0 3.3 1000p 10p 10p 100n 200n)" savecurrent=false}
C {lab_pin.sym} -400 120 0 0 {name=lrsts lab=RST}
C {gnd.sym} -400 180 0 0 {name=lgrst lab=0}
C {vsource.sym} -400 -150 0 0 {name=V_VDD value=3.3 savecurrent=false}
C {lab_pin.sym} -400 -180 0 0 {name=lvdds lab=VDD}
C {gnd.sym} -400 -120 0 0 {name=lgvdd lab=0}
C {code_shown.sym} -150 240 0 0 {name=s1 only_toplevel=false value="
* DIV2 feasibility probe: D_FF_RST_v1 as toggle FF (D tied to !Q) -> Q = CLK/2.
* RST asserted high 0-1ns to break latch symmetry; clock starts at 1.5ns.
* Sweep CLK to find static-CMOS max toggle rate vs 6.37 GHz worst case. 3.3V.
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
"}
