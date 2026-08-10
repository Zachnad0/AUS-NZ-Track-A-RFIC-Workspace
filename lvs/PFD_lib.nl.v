module PFD_lib (DOWN,
    FB,
    REF,
    UP);
 output DOWN;
 input FB;
 input REF;
 output UP;

 wire NANDO;
 wire NDLY;
 wire RSTN;
 wire net1;
 wire net;

 gf180mcu_fd_sc_mcu7t5v0__fillcap_32 FILLER_0_2 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_32 FILLER_0_36 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_16 FILLER_0_70 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_4 FILLER_0_86 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_2 FILLER_0_90 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_1 FILLER_0_92 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_8 FILLER_1_18 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_16 FILLER_1_2 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_1 FILLER_1_26 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_8 FILLER_1_61 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_1 FILLER_1_69 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_16 FILLER_1_72 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_4 FILLER_1_88 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_1 FILLER_1_92 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_2 FILLER_2_18 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_16 FILLER_2_2 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_4 FILLER_2_24 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_2 FILLER_2_28 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_1 FILLER_2_30 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_16 FILLER_2_71 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_4 FILLER_2_87 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_2 FILLER_2_91 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_32 FILLER_3_2 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_8 FILLER_3_36 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_2 FILLER_3_44 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_8 FILLER_3_59 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_1 FILLER_3_67 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_16 FILLER_3_70 ();
 gf180mcu_fd_sc_mcu7t5v0__fillcap_4 FILLER_3_86 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_2 FILLER_3_90 ();
 gf180mcu_fd_sc_mcu7t5v0__fill_1 FILLER_3_92 ();
 gf180mcu_fd_sc_mcu7t5v0__endcap PHY_EDGE_ROW_0_Left_4 ();
 gf180mcu_fd_sc_mcu7t5v0__endcap PHY_EDGE_ROW_0_Right_0 ();
 gf180mcu_fd_sc_mcu7t5v0__endcap PHY_EDGE_ROW_1_Left_5 ();
 gf180mcu_fd_sc_mcu7t5v0__endcap PHY_EDGE_ROW_1_Right_1 ();
 gf180mcu_fd_sc_mcu7t5v0__endcap PHY_EDGE_ROW_2_Left_6 ();
 gf180mcu_fd_sc_mcu7t5v0__endcap PHY_EDGE_ROW_2_Right_2 ();
 gf180mcu_fd_sc_mcu7t5v0__endcap PHY_EDGE_ROW_3_Left_7 ();
 gf180mcu_fd_sc_mcu7t5v0__endcap PHY_EDGE_ROW_3_Right_3 ();
 gf180mcu_fd_sc_mcu7t5v0__filltie TAP_TAPCELL_ROW_0_8 ();
 gf180mcu_fd_sc_mcu7t5v0__filltie TAP_TAPCELL_ROW_0_9 ();
 gf180mcu_fd_sc_mcu7t5v0__filltie TAP_TAPCELL_ROW_1_10 ();
 gf180mcu_fd_sc_mcu7t5v0__filltie TAP_TAPCELL_ROW_2_11 ();
 gf180mcu_fd_sc_mcu7t5v0__filltie TAP_TAPCELL_ROW_3_12 ();
 gf180mcu_fd_sc_mcu7t5v0__filltie TAP_TAPCELL_ROW_3_13 ();
 gf180mcu_fd_sc_mcu7t5v0__dffrnq_1 X1 (.D(net),
    .RN(RSTN),
    .CLK(REF),
    .Q(UP));
 gf180mcu_fd_sc_mcu7t5v0__tieh X1_1 (.Z(net));
 gf180mcu_fd_sc_mcu7t5v0__dffrnq_1 X2 (.D(net1),
    .RN(RSTN),
    .CLK(FB),
    .Q(DOWN));
 gf180mcu_fd_sc_mcu7t5v0__tieh X2_2 (.Z(net1));
 gf180mcu_fd_sc_mcu7t5v0__inv_1 XI1 (.I(NANDO),
    .ZN(NDLY));
 gf180mcu_fd_sc_mcu7t5v0__inv_1 XI2 (.I(NDLY),
    .ZN(RSTN));
 gf180mcu_fd_sc_mcu7t5v0__nand2_1 XN (.A1(UP),
    .A2(DOWN),
    .ZN(NANDO));
endmodule
