v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {chip_top -- PLL die-level integration (Phase 7). Blocks are black-box interface
symbols; definitions come from the signed-off block goldens at netlist time.} -200 -700 0 0 0.4 0.4 {}
C {PFD_lib.sym} 0 0 0 0 {name=x_pfd_lib}
C {lab_pin.sym} -120 -100 0 0 {name=l0 lab=REF_IN}
C {lab_pin.sym} -120 -60 0 0 {name=l1 lab=I_P}
C {lab_pin.sym} -120 -20 0 0 {name=l2 lab=UP}
C {lab_pin.sym} -120 20 0 0 {name=l3 lab=DOWN}
C {lab_pin.sym} -120 60 0 0 {name=l4 lab=VDDD}
C {lab_pin.sym} -120 100 0 0 {name=l5 lab=VSSA}
C {CP_v1.sym} 600 0 0 0 {name=x_cp_v1}
C {lab_pin.sym} 480 -120 0 0 {name=l6 lab=UP}
C {lab_pin.sym} 480 -80 0 0 {name=l7 lab=DOWN}
C {lab_pin.sym} 480 -40 0 0 {name=l8 lab=CP_OUT}
C {lab_pin.sym} 480 0 0 0 {name=l9 lab=VDDA}
C {lab_pin.sym} 480 40 0 0 {name=l10 lab=VSSA}
C {lab_pin.sym} 480 80 0 0 {name=l11 lab=VGP}
C {lab_pin.sym} 480 120 0 0 {name=l12 lab=VGN}
C {ibias_gen_v1.sym} 1200 0 0 0 {name=x_ibias_gen_v1}
C {lab_pin.sym} 1080 -100 0 0 {name=l13 lab=IBIAS_C}
C {lab_pin.sym} 1080 -60 0 0 {name=l14 lab=VGP}
C {lab_pin.sym} 1080 -20 0 0 {name=l15 lab=VGN}
C {lab_pin.sym} 1080 20 0 0 {name=l16 lab=IB_DIV2}
C {lab_pin.sym} 1080 60 0 0 {name=l17 lab=VDDA}
C {lab_pin.sym} 1080 100 0 0 {name=l18 lab=VSSA}
C {DIV2_QUAD_v1.sym} 1800 0 0 0 {name=x_div2_quad_v1}
C {lab_pin.sym} 1680 -160 0 0 {name=l19 lab=VCO_OUTP}
C {lab_pin.sym} 1680 -120 0 0 {name=l20 lab=VCO_OUTN}
C {lab_pin.sym} 1680 -80 0 0 {name=l21 lab=IB_DIV2}
C {lab_pin.sym} 1680 -40 0 0 {name=l22 lab=I_P}
C {lab_pin.sym} 1680 0 0 0 {name=l23 lab=I_N}
C {lab_pin.sym} 1680 40 0 0 {name=l24 lab=Q_P}
C {lab_pin.sym} 1680 80 0 0 {name=l25 lab=Q_N}
C {lab_pin.sym} 1680 120 0 0 {name=l26 lab=VDDD}
C {lab_pin.sym} 1680 160 0 0 {name=l27 lab=VSSA}
C {vco_v1.sym} 2400 0 0 0 {name=x_vco_v1}
C {lab_pin.sym} 2280 -100 0 0 {name=l28 lab=VDDA}
C {lab_pin.sym} 2280 -60 0 0 {name=l29 lab=VCO_OUTP}
C {lab_pin.sym} 2280 -20 0 0 {name=l30 lab=VCO_OUTN}
C {lab_pin.sym} 2280 20 0 0 {name=l31 lab=VSSA}
C {lab_pin.sym} 2280 60 0 0 {name=l32 lab=VTUNE}
C {lab_pin.sym} 2280 100 0 0 {name=l33 lab=ISS}
C {symbols/ppolyf_u.sym} -300 600 0 0 {name=R_ESD_IBIAS model=ppolyf_u spiceprefix=X W=16e-6 L=4e-6 m=1}
C {lab_pin.sym} -300 570 0 0 {name=e0_P lab=IBIAS}
C {lab_pin.sym} -300 630 0 0 {name=e0_M lab=IBIAS_C}
C {lab_pin.sym} -320 600 0 0 {name=e0_B lab=VSSA}
C {symbols/diode_pd2nw_03v3.sym} 0 600 0 0 {name=D_ESD_IBIAS_P model=diode_pd2nw_03v3 r_w=10u r_l=10u m=4}
C {lab_pin.sym} 0 570 0 0 {name=e1_p lab=IBIAS_C}
C {lab_pin.sym} 0 630 0 0 {name=e1_m lab=VDDA}
C {symbols/diode_nd2ps_03v3.sym} 300 600 0 0 {name=D_ESD_IBIAS_N model=diode_nd2ps_03v3 r_w=10u r_l=10u m=4}
C {lab_pin.sym} 300 570 0 0 {name=e2_p lab=VSSA}
C {lab_pin.sym} 300 630 0 0 {name=e2_m lab=IBIAS_C}
C {symbols/diode_pd2nw_03v3.sym} 600 600 0 0 {name=D_ESD_ISS_P model=diode_pd2nw_03v3 r_w=10u r_l=10u m=4}
C {lab_pin.sym} 600 570 0 0 {name=e3_p lab=ISS}
C {lab_pin.sym} 600 630 0 0 {name=e3_m lab=VDDA}
C {symbols/diode_nd2ps_03v3.sym} 900 600 0 0 {name=D_ESD_ISS_N model=diode_nd2ps_03v3 r_w=10u r_l=10u m=4}
C {lab_pin.sym} 900 570 0 0 {name=e4_p lab=VSSA}
C {lab_pin.sym} 900 630 0 0 {name=e4_m lab=ISS}
C {iopin.sym} -200 -500 0 0 {name=P_VSSA lab=VSSA}
C {ipin.sym} -40 -500 0 0 {name=P_VDDA lab=VDDA}
C {ipin.sym} 120 -500 0 0 {name=P_IBIAS lab=IBIAS}
C {ipin.sym} 280 -500 0 0 {name=P_ISS lab=ISS}
C {ipin.sym} 440 -500 0 0 {name=P_VTUNE lab=VTUNE}
C {opin.sym} 600 -500 0 0 {name=P_CP_OUT lab=CP_OUT}
C {opin.sym} 760 -500 0 0 {name=P_I_N lab=I_N}
C {opin.sym} 920 -500 0 0 {name=P_Q_P lab=Q_P}
C {opin.sym} 1080 -500 0 0 {name=P_Q_N lab=Q_N}
C {ipin.sym} 1240 -500 0 0 {name=P_VDDD lab=VDDD}
C {ipin.sym} 1400 -500 0 0 {name=P_REF_IN lab=REF_IN}
