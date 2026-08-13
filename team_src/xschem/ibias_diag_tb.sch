v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {ibias_gen_v1.sym} 0 0 0 0 {name=X1}
C {lab_pin.sym} -150 0 0 0 {name=lp1 lab=IBIAS}
C {lab_pin.sym} 150 -40 0 0 {name=lp2 lab=VGP}
C {lab_pin.sym} 150 0 0 0 {name=lp3 lab=VGN}
C {lab_pin.sym} 150 40 0 0 {name=lp4 lab=IB_DIV2}
C {lab_pin.sym} 0 -100 0 0 {name=lp5 lab=VDD}
C {lab_pin.sym} 0 100 0 0 {name=lp6 lab=0}
C {vsource.sym} -600 -300 0 0 {name=V_VDD value="3.3" savecurrent=true}
C {lab_pin.sym} -600 -330 0 0 {name=lp7 lab=VDD}
C {lab_pin.sym} -600 -270 0 0 {name=lp8 lab=0}
C {isource.sym} -900 0 0 0 {name=I_BIAS value=240u}
C {lab_pin.sym} -900 -30 0 0 {name=lp9 lab=VDD}
C {lab_pin.sym} -900 30 0 0 {name=lp10 lab=IBIAS}
C {vsource.sym} 700 0 0 0 {name=V_VGPf value="2.066" savecurrent=true}
C {lab_pin.sym} 700 -30 0 0 {name=lp11 lab=VGP}
C {lab_pin.sym} 700 30 0 0 {name=lp12 lab=0}
C {vsource.sym} 1100 0 0 0 {name=V_VGNf value="0.882" savecurrent=true}
C {lab_pin.sym} 1100 -30 0 0 {name=lp13 lab=VGN}
C {lab_pin.sym} 1100 30 0 0 {name=lp14 lab=0}
C {vsource.sym} 1500 0 0 0 {name=V_IBDf value="0.882" savecurrent=true}
C {lab_pin.sym} 1500 -30 0 0 {name=lp15 lab=IB_DIV2}
C {lab_pin.sym} 1500 30 0 0 {name=lp16 lab=0}
C {code_shown.sym} -900 500 0 0 {name=s1 only_toplevel=false value="
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
"}
