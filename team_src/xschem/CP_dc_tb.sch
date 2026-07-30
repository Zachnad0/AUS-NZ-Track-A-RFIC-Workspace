v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
* ============================================================================
* CP_dc_tb : DC characterization of CP_v1
*   Sweeps a voltage source V_OUT at CP_OUT over 0..VDD and records the
*   charge-pump current i(v_out) under three static conditions:
*     source-only (UP=1,DOWN=0), sink-only (UP=0,DOWN=1), leakage (0,0).
*   Sign: i(v_out) > 0 => current delivered INTO CP_OUT (sourcing).
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
* --- UP level source (altered in .control) ---
C {vsource.sym} 120 -360 0 0 {name=V_UP value=0 savecurrent=false}
C {lab_pin.sym} 120 -390 0 0 {name=lp_ups sig_type=std_logic lab=UP}
C {gnd.sym} 120 -330 0 0 {name=g_up lab=0}
* --- DOWN level source (altered in .control) ---
C {vsource.sym} 120 -260 0 0 {name=V_DOWN value=0 savecurrent=false}
C {lab_pin.sym} 120 -290 0 0 {name=lp_dns sig_type=std_logic lab=DOWN}
C {gnd.sym} 120 -230 0 0 {name=g_dn lab=0}
* --- CP_OUT sweep source ---
C {vsource.sym} 760 -300 0 0 {name=V_OUT value=0 savecurrent=true}
C {lab_pin.sym} 760 -330 0 0 {name=lp_outs sig_type=std_logic lab=CP_OUT}
C {gnd.sym} 760 -270 0 0 {name=g_out lab=0}
* --- VSS tie to ground (0V source keeps net explicitly named VSS) ---
C {vsource.sym} 700 -180 0 0 {name=V_VSS value=0 savecurrent=false}
C {lab_pin.sym} 700 -210 0 0 {name=lp_vsss sig_type=std_logic lab=VSS}
C {gnd.sym} 700 -150 0 0 {name=g_vss lab=0}
* --- Simulation control ---
C {code_shown.sym} 40 -120 0 0 {name=s1 only_toplevel=false value="
.param fnoicor=0
.param sw_stat_global=0
.param sw_stat_mismatch=0
.param sw_mc_global=0
.param sw_mc_mismatch=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.param I_CP=50u
.control
* source-only: UP=1 DOWN=0
alter v_up = 3.3
alter v_down = 0
dc V_OUT 0 3.3 0.02
wrdata CP_dc_source.txt i(v_out)
* sink-only: UP=0 DOWN=1
alter v_up = 0
alter v_down = 3.3
dc V_OUT 0 3.3 0.02
wrdata CP_dc_sink.txt i(v_out)
* leakage: UP=0 DOWN=0
alter v_up = 0
alter v_down = 0
dc V_OUT 0 3.3 0.02
wrdata CP_dc_leak.txt i(v_out)
.endc
"}
C {title.sym} 40 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
