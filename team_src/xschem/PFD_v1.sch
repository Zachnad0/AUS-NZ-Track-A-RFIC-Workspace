v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 170 70 170 90 {lab=VSS}
N 300 -0 300 20 {lab=VSS}
N 300 -140 300 -120 {lab=VDD}
N 170 -270 170 -230 {lab=VDD}
N 170 -170 170 -140 {lab=VSS}
N 170 -210 260 -80 {lab=UP}
N 170 -30 170 10 {lab=VDD}
N 170 30 260 -40 {lab=DOWN}
N 350 -60 410 -60 {lab=#net1}
N 410 -60 410 140 {lab=#net1}
N -130 140 410 140 {lab=#net1}
N -130 50 -130 140 {lab=#net1}
N -220 -190 -130 -190 {lab=#net1}
N -220 -300 -220 -190 {lab=#net1}
N -220 -300 420 -300 {lab=#net1}
N 410 -60 420 -300 {lab=#net1}
N 170 -210 260 -210 {lab=UP}
N 170 30 200 50 {lab=DOWN}
C {ipin.sym} -130 -210 0 0 {name=p2 lab=REF}
C {iopin.sym} 170 -170 0 0 {name=p3 lab=VSS}
C {iopin.sym} 170 -230 0 0 {name=p4 lab=VDD}
C {opin.sym} 260 -210 0 0 {name=p5 lab=UP}
C {ipin.sym} -130 30 0 0 {name=p8 lab=FB}
C {opin.sym} 200 50 0 0 {name=p11 lab=DOWN}
C {NAND_v1.sym} 280 20 0 0 {name=x3}
C {lab_pin.sym} 170 -270 0 0 {name=p1 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 170 -140 0 0 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 170 -30 0 0 {name=p7 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 300 20 0 0 {name=p9 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 300 -140 0 0 {name=p10 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 170 90 0 0 {name=p12 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -130 -230 0 0 {name=p13 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -130 10 0 0 {name=p14 sig_type=std_logic lab=VDD}
C {D_FF_RST_v1.sym} 20 -200 0 0 {name=x1}
C {D_FF_RST_v1.sym} 20 40 0 0 {name=x2}
