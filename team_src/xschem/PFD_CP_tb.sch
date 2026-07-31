v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {PFD_v1.sym} 0 0 0 0 {name=x1}
C {CP_v1.sym} 600 0 0 0 {name=x2}
C {lab_pin.sym} -150 -30 0 0 {name=lref lab=REF}
C {lab_pin.sym} -150 -10 0 0 {name=lfb lab=FB}
C {lab_pin.sym} 150 -30 0 0 {name=lvdd1 lab=VDD}
C {lab_pin.sym} 150 -10 0 0 {name=lup1 lab=UP}
C {lab_pin.sym} 150 30 0 0 {name=ldn1 lab=DOWN}
C {lab_pin.sym} 450 -30 0 0 {name=lup2 lab=UP}
C {lab_pin.sym} 450 -10 0 0 {name=ldn2 lab=DOWN}
C {lab_pin.sym} 750 -30 0 0 {name=lvdd2 lab=VDD}
C {lab_pin.sym} 750 -10 0 0 {name=lcpout lab=CP_OUT}
C {gnd.sym} 150 10 0 0 {name=lvss1 lab=0}
C {gnd.sym} 750 30 0 0 {name=lvss2 lab=0}
C {vsource.sym} 300 -200 0 0 {name=V_VDD value=3.3 savecurrent=false}
C {lab_pin.sym} 300 -230 0 0 {name=lvdds lab=VDD}
C {gnd.sym} 300 -170 0 0 {name=lgvdd lab=0}
C {vsource.sym} -450 -30 0 0 {name=V_REF value="PULSE(0 3.3 300n 100p 100p 500n 1u)" savecurrent=false}
C {lab_pin.sym} -450 -60 0 0 {name=lrefs lab=REF}
C {gnd.sym} -450 0 0 0 {name=lgref lab=0}
C {vsource.sym} -450 120 0 0 {name=V_FB value="PULSE(0 3.3 300n 100p 100p 500n 1u)" savecurrent=false}
C {lab_pin.sym} -450 90 0 0 {name=lfbs lab=FB}
C {gnd.sym} -450 150 0 0 {name=lgfb lab=0}
C {vsource.sym} 900 -10 0 0 {name=V_meas value=1.65 savecurrent=true}
C {lab_pin.sym} 900 -40 0 0 {name=lcps lab=CP_OUT}
C {gnd.sym} 900 20 0 0 {name=lgm lab=0}
C {code_shown.sym} -200 320 0 0 {name=s1 only_toplevel=false value="
* PFD_v1 + CP_v1 integration tb. REF fixed at 300ns delay; FB delay = fbdel
* (swept). phase error phi = fbdel - 300n: phi>0 -> REF leads -> UP -> CP sources.
* CP_OUT held at 1.65V (mid-compliance); i(V_meas) = CP output current.
* Project rail 3.3V. Sweep + measurement injected at run time.
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
"}
