v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {symbols/nfet_03v3.sym} 0 0 0 0 {name=MN0 L=2u W=4u nf=1 m=24 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} -20 0 0 0 {name=lp1 lab=NB}
C {lab_pin.sym} 20 -30 0 0 {name=lp2 lab=NB}
C {lab_pin.sym} 20 30 0 0 {name=lp3 lab=VSS}
C {lab_pin.sym} 20 0 0 0 {name=lp4 lab=VSS}
C {symbols/nfet_03v3.sym} 200 0 0 0 {name=MNC0 L=1u W=4u nf=1 m=24 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} 180 0 0 0 {name=lp5 lab=IBIAS}
C {lab_pin.sym} 220 -30 0 0 {name=lp6 lab=IBIAS}
C {lab_pin.sym} 220 30 0 0 {name=lp7 lab=NB}
C {lab_pin.sym} 220 0 0 0 {name=lp8 lab=VSS}
C {symbols/nfet_03v3.sym} 400 0 0 0 {name=MN1 L=4u W=4u nf=1 m=10 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} 380 0 0 0 {name=lp9 lab=NB}
C {lab_pin.sym} 420 -30 0 0 {name=lp10 lab=n1}
C {lab_pin.sym} 420 30 0 0 {name=lp11 lab=VSS}
C {lab_pin.sym} 420 0 0 0 {name=lp12 lab=VSS}
C {symbols/nfet_03v3.sym} 600 0 0 0 {name=MNC1 L=1u W=4u nf=1 m=5 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} 580 0 0 0 {name=lp13 lab=IBIAS}
C {lab_pin.sym} 620 -30 0 0 {name=lp14 lab=VGP}
C {lab_pin.sym} 620 30 0 0 {name=lp15 lab=n1}
C {lab_pin.sym} 620 0 0 0 {name=lp16 lab=VSS}
C {symbols/nfet_03v3.sym} 800 0 0 0 {name=MN2 L=2u W=4u nf=1 m=24 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} 780 0 0 0 {name=lp17 lab=NB}
C {lab_pin.sym} 820 -30 0 0 {name=lp18 lab=n2}
C {lab_pin.sym} 820 30 0 0 {name=lp19 lab=VSS}
C {lab_pin.sym} 820 0 0 0 {name=lp20 lab=VSS}
C {symbols/nfet_03v3.sym} 1000 0 0 0 {name=MNC2 L=1u W=4u nf=1 m=24 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} 980 0 0 0 {name=lp21 lab=IBIAS}
C {lab_pin.sym} 1020 -30 0 0 {name=lp22 lab=PA}
C {lab_pin.sym} 1020 30 0 0 {name=lp23 lab=n2}
C {lab_pin.sym} 1020 0 0 0 {name=lp24 lab=VSS}
C {symbols/nfet_03v3.sym} 1200 0 0 0 {name=MNB L=2u W=4u nf=1 m=2 model=nfet_03v3 spiceprefix=X}
C {lab_pin.sym} 1180 0 0 0 {name=lp25 lab=NB}
C {lab_pin.sym} 1220 -30 0 0 {name=lp26 lab=VBCPD}
C {lab_pin.sym} 1220 30 0 0 {name=lp27 lab=VSS}
C {lab_pin.sym} 1220 0 0 0 {name=lp28 lab=VSS}
C {symbols/pfet_03v3.sym} 1400 0 0 0 {name=MP0 L=2u W=16u nf=1 m=24 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 1380 0 0 0 {name=lp29 lab=PB}
C {lab_pin.sym} 1420 30 0 0 {name=lp30 lab=PB}
C {lab_pin.sym} 1420 -30 0 0 {name=lp31 lab=VDD}
C {lab_pin.sym} 1420 0 0 0 {name=lp32 lab=VDD}
C {symbols/pfet_03v3.sym} 1600 0 0 0 {name=MP0c L=1u W=16u nf=1 m=24 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 1580 0 0 0 {name=lp33 lab=PA}
C {lab_pin.sym} 1620 30 0 0 {name=lp34 lab=PA}
C {lab_pin.sym} 1620 -30 0 0 {name=lp35 lab=PB}
C {lab_pin.sym} 1620 0 0 0 {name=lp36 lab=VDD}
C {symbols/pfet_03v3.sym} 1800 0 0 0 {name=MP1 L=4u W=16u nf=1 m=10 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 1780 0 0 0 {name=lp37 lab=PB}
C {lab_pin.sym} 1820 30 0 0 {name=lp38 lab=p1}
C {lab_pin.sym} 1820 -30 0 0 {name=lp39 lab=VDD}
C {lab_pin.sym} 1820 0 0 0 {name=lp40 lab=VDD}
C {symbols/pfet_03v3.sym} 2000 0 0 0 {name=MP1c L=1u W=16u nf=1 m=5 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 1980 0 0 0 {name=lp41 lab=PA}
C {lab_pin.sym} 2020 30 0 0 {name=lp42 lab=VGN}
C {lab_pin.sym} 2020 -30 0 0 {name=lp43 lab=p1}
C {lab_pin.sym} 2020 0 0 0 {name=lp44 lab=VDD}
C {symbols/pfet_03v3.sym} 2200 0 0 0 {name=MP2 L=2u W=16u nf=1 m=24 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 2180 0 0 0 {name=lp45 lab=PB}
C {lab_pin.sym} 2220 30 0 0 {name=lp46 lab=p2}
C {lab_pin.sym} 2220 -30 0 0 {name=lp47 lab=VDD}
C {lab_pin.sym} 2220 0 0 0 {name=lp48 lab=VDD}
C {symbols/pfet_03v3.sym} 2400 0 0 0 {name=MP2c L=1u W=16u nf=1 m=24 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 2380 0 0 0 {name=lp49 lab=VBCPD}
C {lab_pin.sym} 2420 30 0 0 {name=lp50 lab=IB_DIV2}
C {lab_pin.sym} 2420 -30 0 0 {name=lp51 lab=p2}
C {lab_pin.sym} 2420 0 0 0 {name=lp52 lab=VDD}
C {symbols/pfet_03v3.sym} 2600 0 0 0 {name=MPB L=2u W=16u nf=1 m=2 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 2580 0 0 0 {name=lp53 lab=pb2}
C {lab_pin.sym} 2620 30 0 0 {name=lp54 lab=pb2}
C {lab_pin.sym} 2620 -30 0 0 {name=lp55 lab=VDD}
C {lab_pin.sym} 2620 0 0 0 {name=lp56 lab=VDD}
C {symbols/pfet_03v3.sym} 2800 0 0 0 {name=MPBc L=1u W=16u nf=1 m=2 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 2780 0 0 0 {name=lp57 lab=VBCPD}
C {lab_pin.sym} 2820 30 0 0 {name=lp58 lab=VBCPD}
C {lab_pin.sym} 2820 -30 0 0 {name=lp59 lab=pb2}
C {lab_pin.sym} 2820 0 0 0 {name=lp60 lab=VDD}
C {symbols/pfet_03v3.sym} 3000 0 0 0 {name=CDEC L=2u W=16u nf=1 m=6 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 2980 0 0 0 {name=lp61 lab=PB}
C {lab_pin.sym} 3020 30 0 0 {name=lp62 lab=VDD}
C {lab_pin.sym} 3020 -30 0 0 {name=lp63 lab=VDD}
C {lab_pin.sym} 3020 0 0 0 {name=lp64 lab=VDD}
C {ipin.sym} 0 -400 0 0 {name=port_IBIAS lab=IBIAS}
C {iopin.sym} 0 -360 0 0 {name=port_VGP lab=VGP}
C {iopin.sym} 0 -320 0 0 {name=port_VGN lab=VGN}
C {iopin.sym} 0 -280 0 0 {name=port_IB_DIV2 lab=IB_DIV2}
C {iopin.sym} 0 -240 0 0 {name=port_VDD lab=VDD}
C {iopin.sym} 0 -200 0 0 {name=port_VSS lab=VSS}
