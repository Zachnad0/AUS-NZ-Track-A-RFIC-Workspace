v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -20 -150 -0 -150 {lab=REF}
N -20 80 -0 80 {lab=FB}
N 130 -190 160 -190 {lab=UP}
N 130 40 160 40 {lab=DOWN}
N 130 -190 260 -80 {lab=UP}
N 130 40 260 -40 {lab=DOWN}
N 70 120 70 140 {lab=VSS}
N 70 -20 70 -0 {lab=VDD}
N 300 -0 300 20 {lab=VSS}
N 300 -140 300 -120 {lab=VDD}
N 70 -110 70 -90 {lab=VSS}
N 70 -250 70 -230 {lab=VDD}
N -30 -190 -0 -190 {lab=VDD}
N -30 40 -0 40 {lab=VDD}
C {D_FF_v1.sym} 150 -170 0 0 {name=x1}
C {ipin.sym} -20 -150 0 0 {name=p2 lab=REF}
C {iopin.sym} 70 -110 0 0 {name=p3 lab=VSS}
C {iopin.sym} 70 -230 0 0 {name=p4 lab=VDD}
C {opin.sym} 160 -190 0 0 {name=p5 lab=UP}
C {D_FF_v1.sym} 150 60 0 0 {name=x2}
C {ipin.sym} -20 80 0 0 {name=p8 lab=FB}
C {opin.sym} 160 40 0 0 {name=p11 lab=DOWN}
C {NAND_v1.sym} 280 20 0 0 {name=x3}
C {lab_pin.sym} 70 -250 0 0 {name=p1 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 70 -90 0 0 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 70 -20 0 0 {name=p7 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 300 20 0 0 {name=p9 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 300 -140 0 0 {name=p10 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 70 140 0 0 {name=p12 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -30 -190 0 0 {name=p13 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -30 40 0 0 {name=p14 sig_type=std_logic lab=VDD}
