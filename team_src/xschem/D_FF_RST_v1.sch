v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Edge Detector} 180 -540 0 0 0.4 0.4 {}
T {NOTE: CLK is positive edge triggered, RST is active high} 430 0 0 0 0.4 0.4 {}
N 1070 -530 1100 -530 {lab=Q}
N 620 -610 690 -610 {lab=VDD}
N 690 -610 900 -610 {lab=VDD}
N 560 -610 620 -610 {lab=VDD}
N 520 -570 520 -330 {lab=D}
N 520 -570 650 -570 {lab=D}
N 600 -330 650 -330 {lab=#net1}
N 630 -290 650 -290 {lab=#net2}
N 630 -440 630 -290 {lab=#net2}
N 630 -530 650 -530 {lab=#net2}
N 630 -530 630 -440 {lab=#net2}
N 550 -280 550 -250 {lab=VSS}
N 550 -610 550 -380 {lab=VDD}
N 400 -570 520 -570 {lab=D}
N 400 -610 560 -610 {lab=VDD}
N 410 -250 560 -250 {lab=VSS}
N 500 -440 630 -440 {lab=#net2}
N 450 -390 450 -250 {lab=VSS}
N 400 -440 420 -440 {lab=#net3}
N 230 -370 450 -370 {lab=VSS}
N 350 -380 350 -370 {lab=VSS}
N 230 -510 450 -510 {lab=VDD}
N 450 -510 550 -510 {lab=VDD}
N 230 -510 230 -470 {lab=VDD}
N 350 -510 350 -500 {lab=VDD}
N 450 -510 450 -490 {lab=VDD}
N 180 -490 180 -420 {lab=CLK}
N 180 -420 200 -420 {lab=CLK}
N 180 -490 310 -490 {lab=CLK}
N 310 -490 310 -460 {lab=CLK}
N 980 -420 980 -370 {lab=Q}
N 1080 -530 1080 -470 {lab=Q}
N 980 -470 1080 -420 {lab=!Q}
N 980 -420 1080 -470 {lab=Q}
N 1080 -420 1080 -350 {lab=!Q}
N 1070 -350 1080 -350 {lab=!Q}
N 1080 -350 1100 -350 {lab=!Q}
N 980 -510 980 -470 {lab=!Q}
N 950 -550 950 -530 {lab=#net4}
N 950 -550 980 -550 {lab=#net4}
N 740 -350 740 -310 {lab=#net5}
N 740 -350 980 -350 {lab=#net5}
N 960 -330 980 -330 {lab=RST}
N 740 -550 760 -550 {lab=#net6}
N 840 -550 860 -550 {lab=#net7}
N 840 -330 860 -330 {lab=RST}
N 860 -510 860 -330 {lab=RST}
N 860 -330 960 -330 {lab=RST}
N 790 -610 790 -600 {lab=VDD}
N 900 -610 900 -590 {lab=VDD}
N 900 -610 1020 -610 {lab=VDD}
N 1020 -610 1020 -590 {lab=VDD}
N 1020 -290 1020 -250 {lab=VSS}
N 560 -250 1020 -250 {lab=VSS}
N 690 -410 690 -370 {lab=VDD}
N 690 -410 1020 -410 {lab=VDD}
N 550 -410 690 -410 {lab=VDD}
N 1020 -470 1020 -460 {lab=VSS}
N 690 -460 1020 -460 {lab=VSS}
N 690 -490 690 -460 {lab=VSS}
N 790 -500 790 -460 {lab=VSS}
N 900 -470 900 -460 {lab=VSS}
N 760 -460 760 -250 {lab=VSS}
N 410 -860 450 -860 {lab=#net8}
N 530 -860 570 -860 {lab=#net9}
N 650 -860 690 -860 {lab=#net10}
N 770 -860 810 -860 {lab=#net11}
N 890 -860 930 -860 {lab=#net12}
C {ipin.sym} 180 -490 0 0 {name=p1 lab=CLK}
C {ipin.sym} 400 -570 0 0 {name=p2 lab=D}
C {iopin.sym} 400 -610 2 0 {name=p3 lab=VDD}
C {opin.sym} 1100 -530 0 0 {name=p4 lab=Q}
C {title.sym} 160 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
C {NAND_v1.sym} 1000 -450 0 0 {name=x1}
C {opin.sym} 1100 -350 0 0 {name=p5 lab=!Q}
C {NAND_v1.sym} 670 -470 0 0 {name=x3}
C {NAND_v1.sym} 670 -230 0 0 {name=x4}
C {iopin.sym} 410 -250 2 0 {name=p6 lab=VSS}
C {NOT_v1.sym} 540 -300 0 0 {name=x5}
C {NOT_v1.sym} 440 -410 0 0 {name=x6}
C {NOT_v1.sym} 220 -390 0 0 {name=x7}
C {NAND_v1.sym} 330 -360 0 0 {name=x8}
C {ipin.sym} 840 -330 0 0 {name=p7 lab=RST}
C {NAND3_v1.sym} 1000 -350 0 0 {name=x2}
C {NOT_v1.sym} 780 -520 0 0 {name=x9}
C {NAND_v1.sym} 880 -450 0 0 {name=x10}
C {NOT_v1.sym} 350 -830 0 0 {name=x11}
C {NOT_v1.sym} 950 -830 0 0 {name=x12}
C {lab_pin.sym} 280 -420 3 0 {name=p8 sig_type=std_logic lab=CLKB}
C {lab_pin.sym} 330 -860 3 0 {name=p9 sig_type=std_logic lab=CLKB}
C {lab_pin.sym} 1010 -860 3 0 {name=p10 sig_type=std_logic lab=CLKB_DLY}
C {lab_pin.sym} 310 -420 3 0 {name=p11 sig_type=std_logic lab=CLKB_DLY}
C {lab_pin.sym} 360 -910 2 0 {name=p12 lab=VDD}
C {lab_pin.sym} 960 -910 2 0 {name=p13 lab=VDD}
C {lab_pin.sym} 960 -810 2 0 {name=p14 lab=VSS}
C {lab_pin.sym} 360 -810 0 0 {name=p15 lab=VSS}
C {NOT_v1.sym} 470 -830 0 0 {name=x13}
C {NOT_v1.sym} 590 -830 0 0 {name=x14}
C {NOT_v1.sym} 710 -830 0 0 {name=x15}
C {NOT_v1.sym} 830 -830 0 0 {name=x16}
C {lab_pin.sym} 480 -910 2 0 {name=p16 lab=VDD}
C {lab_pin.sym} 600 -910 2 0 {name=p17 lab=VDD}
C {lab_pin.sym} 720 -910 2 0 {name=p18 lab=VDD}
C {lab_pin.sym} 840 -910 2 0 {name=p19 lab=VDD}
C {lab_pin.sym} 480 -810 0 0 {name=p20 lab=VSS}
C {lab_pin.sym} 600 -810 0 0 {name=p21 lab=VSS}
C {lab_pin.sym} 720 -810 0 0 {name=p22 lab=VSS}
C {lab_pin.sym} 840 -810 0 0 {name=p23 lab=VSS}
