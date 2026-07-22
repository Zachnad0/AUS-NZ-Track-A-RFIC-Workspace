v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
* ============================================================================
* CP_v1 : single-ended switched current-steering charge pump, GF180 3.3V
* Team A1 AUS/NZ Track A RFIC
*
* Topology:
*   PMOS mirror  M_PREF (diode) -> M_PSRC sources I_CP into CP_OUT when UP=1
*   NMOS mirror  M_NREF (diode) -> M_NSNK sinks   I_CP from CP_OUT when DOWN=1
*   Drain switches M_PSW (pmos, gated by UP_B) and M_NSW (nmos, gated by DOWN)
*     steer the mirror currents to/from CP_OUT; both off => CP_OUT high-Z.
*   Internal inverter M_INVP/M_INVN generates UP_B (active-low for the pmos
*     switch). DOWN drives the nmos switch directly -> ~1 inverter of UP/DOWN
*     drive skew; see report (v1 caveat).
*   Reference current I_CP is set by two IDEAL 50u sources (I_PREF/I_NREF).
*     I_CP = 50u is a PROVISIONAL PLACEHOLDER; final value is a loop-design
*     decision with the loop filter. In silicon these ideal sources become a
*     mirrored bias from the PLL bias generator (no IBIAS pin exists in v1).
* ============================================================================
* --- PMOS mirror: reference (diode) ---
C {symbols/pfet_03v3.sym} 400 -560 0 0 {name=M_PREF
L=1u
W=10u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
* --- PMOS mirror: output source device ---
C {symbols/pfet_03v3.sym} 700 -560 0 0 {name=M_PSRC
L=1u
W=10u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
* --- PMOS drain switch (on when UP=1 -> UP_B=0) ---
C {symbols/pfet_03v3.sym} 700 -460 0 0 {name=M_PSW
L=0.3u
W=10u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
* --- NMOS drain switch (on when DOWN=1) ---
C {symbols/nfet_03v3.sym} 700 -360 0 0 {name=M_NSW
L=0.3u
W=5u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
* --- NMOS mirror: output sink device ---
C {symbols/nfet_03v3.sym} 700 -260 0 0 {name=M_NSNK
L=1u
W=5u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
* --- NMOS mirror: reference (diode) ---
C {symbols/nfet_03v3.sym} 400 -260 0 0 {name=M_NREF
L=1u
W=5u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
* --- Inverter pmos (UP -> UP_B) ---
C {symbols/pfet_03v3.sym} 560 -460 0 0 {name=M_INVP
L=0.3u
W=2u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
* --- Inverter nmos (UP -> UP_B) ---
C {symbols/nfet_03v3.sym} 560 -360 0 0 {name=M_INVN
L=0.3u
W=1u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
* --- Ideal reference current sources (PROVISIONAL I_CP placeholder) ---
C {isource.sym} 400 -460 0 0 {name=I_PREF value=I_CP savecurrent=true}
C {isource.sym} 400 -360 0 0 {name=I_NREF value=I_CP savecurrent=true}
* --- I_CP parameter (subckt-local default; provisional placeholder) ---
C {code_shown.sym} 120 -160 0 0 {name=CP_PARAM only_toplevel=false value=".param I_CP=50u"}
* ============================================================================
* Explicit net labels on EVERY device terminal (rule: zero auto #netN names)
* ----- M_PREF (pmos diode) -----
C {lab_pin.sym} 420 -590 0 0 {name=lPREFs sig_type=std_logic lab=VDD}
C {lab_pin.sym} 380 -560 0 0 {name=lPREFg sig_type=std_logic lab=VGP}
C {lab_pin.sym} 420 -530 0 0 {name=lPREFd sig_type=std_logic lab=VGP}
C {lab_pin.sym} 420 -560 0 0 {name=lPREFb sig_type=std_logic lab=VDD}
* ----- M_PSRC (pmos mirror out) -----
C {lab_pin.sym} 720 -590 0 0 {name=lPSRCs sig_type=std_logic lab=VDD}
C {lab_pin.sym} 680 -560 0 0 {name=lPSRCg sig_type=std_logic lab=VGP}
C {lab_pin.sym} 720 -530 0 0 {name=lPSRCd sig_type=std_logic lab=PMID}
C {lab_pin.sym} 720 -560 0 0 {name=lPSRCb sig_type=std_logic lab=VDD}
* ----- M_PSW (pmos switch) -----
C {lab_pin.sym} 720 -490 0 0 {name=lPSWs sig_type=std_logic lab=PMID}
C {lab_pin.sym} 680 -460 0 0 {name=lPSWg sig_type=std_logic lab=UP_B}
C {lab_pin.sym} 720 -430 0 0 {name=lPSWd sig_type=std_logic lab=CP_OUT}
C {lab_pin.sym} 720 -460 0 0 {name=lPSWb sig_type=std_logic lab=VDD}
* ----- M_NSW (nmos switch) -----
C {lab_pin.sym} 720 -390 0 0 {name=lNSWd sig_type=std_logic lab=CP_OUT}
C {lab_pin.sym} 680 -360 0 0 {name=lNSWg sig_type=std_logic lab=DOWN}
C {lab_pin.sym} 720 -330 0 0 {name=lNSWs sig_type=std_logic lab=NMID}
C {lab_pin.sym} 720 -360 0 0 {name=lNSWb sig_type=std_logic lab=VSS}
* ----- M_NSNK (nmos mirror out) -----
C {lab_pin.sym} 720 -290 0 0 {name=lNSNKd sig_type=std_logic lab=NMID}
C {lab_pin.sym} 680 -260 0 0 {name=lNSNKg sig_type=std_logic lab=VGN}
C {lab_pin.sym} 720 -230 0 0 {name=lNSNKs sig_type=std_logic lab=VSS}
C {lab_pin.sym} 720 -260 0 0 {name=lNSNKb sig_type=std_logic lab=VSS}
* ----- M_NREF (nmos diode) -----
C {lab_pin.sym} 420 -290 0 0 {name=lNREFd sig_type=std_logic lab=VGN}
C {lab_pin.sym} 380 -260 0 0 {name=lNREFg sig_type=std_logic lab=VGN}
C {lab_pin.sym} 420 -230 0 0 {name=lNREFs sig_type=std_logic lab=VSS}
C {lab_pin.sym} 420 -260 0 0 {name=lNREFb sig_type=std_logic lab=VSS}
* ----- M_INVP (pmos) -----
C {lab_pin.sym} 580 -490 0 0 {name=lINVPs sig_type=std_logic lab=VDD}
C {lab_pin.sym} 540 -460 0 0 {name=lINVPg sig_type=std_logic lab=UP}
C {lab_pin.sym} 580 -430 0 0 {name=lINVPd sig_type=std_logic lab=UP_B}
C {lab_pin.sym} 580 -460 0 0 {name=lINVPb sig_type=std_logic lab=VDD}
* ----- M_INVN (nmos) -----
C {lab_pin.sym} 580 -390 0 0 {name=lINVNd sig_type=std_logic lab=UP_B}
C {lab_pin.sym} 540 -360 0 0 {name=lINVNg sig_type=std_logic lab=UP}
C {lab_pin.sym} 580 -330 0 0 {name=lINVNs sig_type=std_logic lab=VSS}
C {lab_pin.sym} 580 -360 0 0 {name=lINVNb sig_type=std_logic lab=VSS}
* ----- Ideal current source terminals -----
C {lab_pin.sym} 400 -490 0 0 {name=lIPREFp sig_type=std_logic lab=VGP}
C {lab_pin.sym} 400 -430 0 0 {name=lIPREFm sig_type=std_logic lab=VSS}
C {lab_pin.sym} 400 -390 0 0 {name=lINREFp sig_type=std_logic lab=VDD}
C {lab_pin.sym} 400 -330 0 0 {name=lINREFm sig_type=std_logic lab=VGN}
* ============================================================================
* Boundary ports (define subckt pin order: UP DOWN CP_OUT VDD VSS)
C {ipin.sym} 120 -640 0 0 {name=p_up lab=UP}
C {ipin.sym} 120 -600 0 0 {name=p_down lab=DOWN}
C {opin.sym} 900 -430 0 0 {name=p_cpout lab=CP_OUT}
C {iopin.sym} 120 -560 0 0 {name=p_vdd lab=VDD}
C {iopin.sym} 120 -520 0 0 {name=p_vss lab=VSS}
C {title.sym} 120 -40 0 0 {name=l1 author="Team A1 AUS/NZ Track A RFIC"}
