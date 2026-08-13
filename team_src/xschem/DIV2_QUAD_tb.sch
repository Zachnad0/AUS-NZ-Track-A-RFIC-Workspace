v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {DIV2_QUAD_v1.sym} 0 0 0 0 {name=X1}
C {lab_pin.sym} -150 -60 0 0 {name=lp1 lab=CK}
C {lab_pin.sym} -150 -20 0 0 {name=lp2 lab=CKB}
C {lab_pin.sym} -150 20 0 0 {name=lp3 lab=IBIAS}
C {lab_pin.sym} 150 -60 0 0 {name=lp4 lab=I_P}
C {lab_pin.sym} 150 -20 0 0 {name=lp5 lab=I_N}
C {lab_pin.sym} 150 20 0 0 {name=lp6 lab=Q_P}
C {lab_pin.sym} 150 60 0 0 {name=lp7 lab=Q_N}
C {lab_pin.sym} 0 -100 0 0 {name=lp8 lab=VDD}
C {lab_pin.sym} 0 100 0 0 {name=lp9 lab=0}
C {vsource.sym} -600 -300 0 0 {name=V_VDD value="3.3" savecurrent=true}
C {lab_pin.sym} -600 -330 0 0 {name=lp10 lab=VDD}
C {lab_pin.sym} -600 -270 0 0 {name=lp11 lab=0}
C {vsource.sym} -600 0 0 0 {name=V_CK value="PULSE(0 3.3 0 5p 5p 95p 200p)" savecurrent=false}
C {lab_pin.sym} -600 -30 0 0 {name=lp12 lab=CK}
C {lab_pin.sym} -600 30 0 0 {name=lp13 lab=0}
C {vsource.sym} -600 300 0 0 {name=V_CKB value="PULSE(3.3 0 0 5p 5p 95p 200p)" savecurrent=false}
C {lab_pin.sym} -600 270 0 0 {name=lp14 lab=CKB}
C {lab_pin.sym} -600 330 0 0 {name=lp15 lab=0}
C {isource.sym} -900 20 0 0 {name=I_BIAS value=240u}
C {lab_pin.sym} -900 -10 0 0 {name=lp16 lab=VDD}
C {lab_pin.sym} -900 50 0 0 {name=lp17 lab=IBIAS}
C {capa.sym} 600 200 0 0 {name=Cpad_I_P value=300f}
C {lab_pin.sym} 600 170 0 0 {name=lp18 lab=I_P}
C {lab_pin.sym} 600 230 0 0 {name=lp19 lab=0}
C {res.sym} 600 400 0 0 {name=Rterm_I_P value=50 footprint=1206 device=resistor m=1}
C {lab_pin.sym} 600 370 0 0 {name=lp20 lab=I_P}
C {lab_pin.sym} 600 430 0 0 {name=lp21 lab=0}
C {capa.sym} 900 200 0 0 {name=Cpad_I_N value=300f}
C {lab_pin.sym} 900 170 0 0 {name=lp22 lab=I_N}
C {lab_pin.sym} 900 230 0 0 {name=lp23 lab=0}
C {res.sym} 900 400 0 0 {name=Rterm_I_N value=50 footprint=1206 device=resistor m=1}
C {lab_pin.sym} 900 370 0 0 {name=lp24 lab=I_N}
C {lab_pin.sym} 900 430 0 0 {name=lp25 lab=0}
C {capa.sym} 1200 200 0 0 {name=Cpad_Q_P value=300f}
C {lab_pin.sym} 1200 170 0 0 {name=lp26 lab=Q_P}
C {lab_pin.sym} 1200 230 0 0 {name=lp27 lab=0}
C {res.sym} 1200 400 0 0 {name=Rterm_Q_P value=50 footprint=1206 device=resistor m=1}
C {lab_pin.sym} 1200 370 0 0 {name=lp28 lab=Q_P}
C {lab_pin.sym} 1200 430 0 0 {name=lp29 lab=0}
C {capa.sym} 1500 200 0 0 {name=Cpad_Q_N value=300f}
C {lab_pin.sym} 1500 170 0 0 {name=lp30 lab=Q_N}
C {lab_pin.sym} 1500 230 0 0 {name=lp31 lab=0}
C {res.sym} 1500 400 0 0 {name=Rterm_Q_N value=50 footprint=1206 device=resistor m=1}
C {lab_pin.sym} 1500 370 0 0 {name=lp32 lab=Q_N}
C {lab_pin.sym} 1500 430 0 0 {name=lp33 lab=0}
C {code_shown.sym} -900 700 0 0 {name=s1 only_toplevel=false value="
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.save all i(V_VDD)
.ic v(x1.OI)=3.2 v(x1.OIB)=2.5 v(x1.OQ)=2.9 v(x1.OQB)=2.8 v(x1.G1_IP)=1.5 v(x1.G1_IN)=1.5 v(x1.G1_QP)=1.5 v(x1.G1_QN)=1.5
.tran 0.2p 20n uic
"}
