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
C {symbols/pfet_03v3.sym} 600 0 0 0 {name=M_PREF_rep L=2u W=50u nf=1 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 580 0 0 0 {name=lp11 lab=VGP}
C {lab_pin.sym} 620 30 0 0 {name=lp12 lab=VGP}
C {lab_pin.sym} 620 -30 0 0 {name=lp13 lab=vgp_s}
C {lab_pin.sym} 620 0 0 0 {name=lp14 lab=VDD}
C {vsource.sym} 820 0 0 0 {name=V_VGP value="0" savecurrent=true}
C {lab_pin.sym} 820 -30 0 0 {name=lp15 lab=VDD}
C {lab_pin.sym} 820 30 0 0 {name=lp16 lab=vgp_s}
C {symbols/nfet_03v3.sym} 1100 0 0 0 {name=M_NREF_rep L=2u W=10u nf=1 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} 1080 0 0 0 {name=lp17 lab=VGN}
C {lab_pin.sym} 1120 -30 0 0 {name=lp18 lab=VGN}
C {lab_pin.sym} 1120 30 0 0 {name=lp19 lab=vgn_s}
C {lab_pin.sym} 1120 0 0 0 {name=lp20 lab=0}
C {vsource.sym} 1320 0 0 0 {name=V_VGN value="0" savecurrent=true}
C {lab_pin.sym} 1320 -30 0 0 {name=lp21 lab=vgn_s}
C {lab_pin.sym} 1320 30 0 0 {name=lp22 lab=0}
C {symbols/nfet_03v3.sym} 1600 0 0 0 {name=M_BREF_rep L=1u W=4u nf=1 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} 1580 0 0 0 {name=lp23 lab=IB_DIV2}
C {lab_pin.sym} 1620 -30 0 0 {name=lp24 lab=IB_DIV2}
C {lab_pin.sym} 1620 30 0 0 {name=lp25 lab=ibd_s}
C {lab_pin.sym} 1620 0 0 0 {name=lp26 lab=0}
C {vsource.sym} 1820 0 0 0 {name=V_IBD value="0" savecurrent=true}
C {lab_pin.sym} 1820 -30 0 0 {name=lp27 lab=ibd_s}
C {lab_pin.sym} 1820 30 0 0 {name=lp28 lab=0}
C {code_shown.sym} -900 500 0 0 {name=s1 only_toplevel=false value="
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
"}
