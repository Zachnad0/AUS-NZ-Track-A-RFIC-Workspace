v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {PFD_v1.sym} 0 0 0 0 {name=x1}
C {lab_pin.sym} -150 -30 0 0 {name=lREF lab=REF}
C {lab_pin.sym} -150 -10 0 0 {name=lFB lab=FB}
C {lab_pin.sym} 150 -30 0 0 {name=lVDD lab=VDD}
C {lab_pin.sym} 150 -10 0 0 {name=lUP lab=UP}
C {lab_pin.sym} 150 30 0 0 {name=lDOWN lab=DOWN}
C {gnd.sym} 150 10 0 0 {name=lvss lab=0}
C {vsource.sym} 400 -30 0 0 {name=V_VDD value=3.3 savecurrent=false}
C {lab_pin.sym} 400 -60 0 0 {name=lvddsrc lab=VDD}
C {gnd.sym} 400 0 0 0 {name=lgvdd lab=0}
C {vsource.sym} -450 -30 0 0 {name=V_REF value="PULSE(0 3.3 50n 100p 100p 500n 1u)" savecurrent=false}
C {lab_pin.sym} -450 -60 0 0 {name=lrefsrc lab=REF}
C {gnd.sym} -450 0 0 0 {name=lgref lab=0}
C {vsource.sym} -450 120 0 0 {name=V_FB value="PULSE(0 3.3 150n 100p 100p 500n 1u)" savecurrent=false}
C {lab_pin.sym} -450 90 0 0 {name=lfbsrc lab=FB}
C {gnd.sym} -450 150 0 0 {name=lgfb lab=0}
C {code_shown.sym} 0 220 0 0 {name=s1 only_toplevel=false value="
* PFD_tb_lead : phase-LEAD case, REF rising edge 100ns BEFORE FB (same freq).
* Project rail 3.3V. Stimulus first edges at 50ns so edge detectors are armed
* under uic (Rule 7). Expect wide UP pulses, DOWN = reset pulse only.
* DRAFT - not yet netlisted/simulated (container offline 2026-07-30).
.param fnoicor=0
.param sw_stat_global=0
.param sw_stat_mismatch=0
.param sw_mc_global=0
.param sw_mc_mismatch=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.control
tran 100p 5u uic
write PFD_tb_lead.raw
.endc
"}
