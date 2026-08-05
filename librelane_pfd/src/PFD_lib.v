// Structural library-cell PFD. 2-inverter RSTN delay (dead-zone fix) marked keep.
module PFD_lib (REF, FB, UP, DOWN);
  input  REF, FB;
  output UP, DOWN;
  wire   NANDO, NDLY, RSTN;
  gf180mcu_fd_sc_mcu7t5v0__dffrnq_1 X1 (.CLK(REF), .D(1'b1), .RN(RSTN), .Q(UP));
  gf180mcu_fd_sc_mcu7t5v0__dffrnq_1 X2 (.CLK(FB),  .D(1'b1), .RN(RSTN), .Q(DOWN));
  gf180mcu_fd_sc_mcu7t5v0__nand2_1  XN (.A1(UP), .A2(DOWN), .ZN(NANDO));
  (* keep *) gf180mcu_fd_sc_mcu7t5v0__inv_1 XI1 (.I(NANDO), .ZN(NDLY));
  (* keep *) gf180mcu_fd_sc_mcu7t5v0__inv_1 XI2 (.I(NDLY),  .ZN(RSTN));
endmodule
