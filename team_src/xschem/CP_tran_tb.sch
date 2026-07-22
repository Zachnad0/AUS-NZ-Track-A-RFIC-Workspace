v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
* ============================================================================
* CP_tran_tb : transient characterization of CP_v1
*   UP and DOWN are ~1ns-wide pulses (PFD reset pulse ~0.98ns) at 1 MHz rep
*   rate (1us period). Delays >=50n so nothing switches at t=0 under uic.
*   UP fires at 50n, DOWN at 500n (separated so each steering event is
*   measured cleanly). 10p cap load at CP_OUT (placeholder). A 0V sense
*   source V_SENSE carries the pump current into the load: i(v_sense).
*   CP_OUT pre-charged to mid-rail (1.65V) so it starts inside compliance.
* ============================================================================
C {CP_v1.sym} 400 -300 0 0 {name=x1}
* --- DUT pin labels ---
C {lab_pin.sym} 250 -330 0 0 {name=lp_up sig_type=std_logic lab=UP}
C {lab_pin.sym} 250 -310 0 0 {name=lp_dn sig_type=std_logic lab=DOWN}
C {lab_pin.sym} 550 -310 0 0 {name=lp_out sig_type=std_logic lab=CP_OUT}
C {lab_pin.sym} 550 -330 0 0 {name=lp_vdd sig_type=std_logic lab=VDD}
C {lab_pin.sym} 550 -270 0 0 {name=lp_vss sig_type=std_logic lab=VSS}
* --- VDD supply (3.3V) ---
C {vsource.sym} 120 -460 0 0 {name=V_VDD value=3.3 savecurrent=false}
C {lab_pin.sym} 120 -490 0 0 {name=lp_vdds sig_type=std_logic lab=VDD}
C {gnd.sym} 120 -430 0 0 {name=g_vdd lab=0}
* --- UP pulse (1ns wide, fires at 50n, 1us period) ---
C {vsource.sym} 120 -360 0 0 {name=V_UP value="PULSE(0 3.3 50n 50p 50p 1n 1u)" savecurrent=false}
C {lab_pin.sym} 120 -390 0 0 {name=lp_ups sig_type=std_logic lab=UP}
C {gnd.sym} 120 -330 0 0 {name=g_up lab=0}
* --- DOWN pulse (1ns wide, fires at 500n, 1us period) ---
C {vsource.sym} 120 -260 0 0 {name=V_DOWN value="PULSE(0 3.3 500n 50p 50p 1n 1u)" savecurrent=false}
C {lab_pin.sym} 120 -290 0 0 {name=lp_dns sig_type=std_logic lab=DOWN}
C {gnd.sym} 120 -230 0 0 {name=g_dn lab=0}
* --- CP_OUT current sense (0V) + 10p load ---
C {vsource.sym} 640 -310 0 0 {name=V_SENSE value=0 savecurrent=true}
C {lab_pin.sym} 640 -340 0 0 {name=lp_senp sig_type=std_logic lab=CP_OUT}
C {lab_pin.sym} 640 -280 0 0 {name=lp_senm sig_type=std_logic lab=CAPTOP}
C {capa.sym} 640 -230 0 0 {name=C_L value=10p m=1}
C {lab_pin.sym} 640 -260 0 0 {name=lp_capt sig_type=std_logic lab=CAPTOP}
C {gnd.sym} 640 -200 0 0 {name=g_cl lab=0}
* --- VSS tie to ground (0V source keeps net explicitly named VSS) ---
C {vsource.sym} 700 -160 0 0 {name=V_VSS value=0 savecurrent=false}
C {lab_pin.sym} 700 -190 0 0 {name=lp_vsss sig_type=std_logic lab=VSS}
C {gnd.sym} 700 -130 0 0 {name=g_vss lab=0}
* --- Simulation control ---
C {code_shown.sym} 40 -120 0 0 {name=s1 only_toplevel=false value="
.param fnoicor=0
.param sw_stat_global=0
.param sw_stat_mismatch=0
.param sw_mc_global=0
.param sw_mc_mismatch=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.param I_CP=50u
.options method=gear
.control
save all
tran 10p 600n uic
wrdata CP_tran.txt v(cp_out) i(v_sense) v(x1.up_b)
.endc
.ic v(cp_out)=1.65 v(captop)=1.65
"}
C {title.sym} 40 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
