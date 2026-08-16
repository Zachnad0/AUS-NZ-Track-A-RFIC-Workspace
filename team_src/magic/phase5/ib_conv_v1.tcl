# ib_conv_v1.tcl -- FULL DIV2 converter (1e), 14 devices, one flat cell.
# Front-end (diff pair, native coords 0..3300) + 3-inverter chain (shifted right) +
# CC MIM cap (OC->G1) + RFB 20k (S1->G1) + R_SER 1k (S3->OUT).
# Nets: NS DN1 OC G1 S1 S2 S3 ; ports IBIAS INP INM OUT VDD VSS.
# Layer-per-net around the caps: OC=M5 (front-end) reaches the cap m5 top plate; the
# cap m4 bottom plate -> G1; inverter chain hops on M4 but in the inverter band (x>=4800),
# clear of the cap which sits in the channel above the front-end.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_conv_v1
set H 28
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_inv_lib.tcl

drc off ; snap internal
cellname create $CELL ; load $CELL

# ---------- PLACE ----------
set xNT 0 ; set xN1 1200 ; set xN2 2400 ; set YP 2600
place_nfet 1 $xNT MNT 1   0 8
place_nfet 1 $xN1 MBN1 0.3 0 8
place_nfet 1 $xN2 MBN2 0.3 0 8
place_pfet 1 $xN1 MBP1 $YP 0.3 8
place_pfet 1 $xN2 MBP2 $YP 0.3 8
set xI1 4800 ; set xI2 6400 ; set xI3 8000
place_inv_dev $xI1 4  10 I1
place_inv_dev $xI2 11 26 I2
place_inv_dev $xI3 16 44 I3
# passives (measured). RFB = SERPENTINE nx2 l20.6 (r_length 40.04u = 20k, DRC-clean
# both terminals at bottom: term-A=G1 @ LL+(376,212), term-B=S1 @ LL+(856,212));
# CC cap w5 l10 (m4 bottom plate / m5 top plate, full bbox); R_SER w2 l2 (bot LL+(376,212)
# top LL+(376,784)). All placed in the clear channel above the front-end / by INV3.
set rfx 1500 ; set rfy 7000   ;# RFB snake LL
set ccx 1500 ; set ccy 4200   ;# CC cap LL (bbox +1480 x +2240)
set rsx 8800 ; set rsy 7000   ;# R_SER LL
box values $rfx $rfy $rfx $rfy ; magic::gencell gf180mcu::ppolyf_u_1k RFB w 2 l 20.6 nx 2 snake 1
box values $rsx $rsy $rsx $rsy ; magic::gencell gf180mcu::ppolyf_u_1k RSER w 2 l 2
box values $ccx $ccy $ccx $ccy ; magic::gencell gf180mcu::cap_mim_2p0fF CC w 5 l 10
flatten ${CELL}_f ; load ${CELL}_f

# ---------- STRAP: front-end (native diff-pair) ----------
nfet_leg 1 $xNT 1 1   0 0 8
nfet_leg 1 $xN1 1 0.3 0 0 8
nfet_leg 1 $xN2 1 0.3 0 0 8
pfet_leg 1 $xN1 1 0.3 $YP 0 -700 8
pfet_leg 1 $xN2 1 0.3 $YP 0 -700 8
box values -900 -1320 3300 [expr {$YP+1360}] ; paint pwell
box values -833 -1290 3233 -1170 ; paint psubdiff
box values -816 -1277 3216 -1183 ; paint psubdiffcont
box values -833 -1290 3233 -1130 ; paint metal1
box values -900 [expr {$YP-1200}] 3300 [expr {$YP+1360}] ; paint nwell
box values -833 [expr {$YP+1160}] 3233 [expr {$YP+1280}] ; paint nsubdiff
box values -816 [expr {$YP+1173}] 3216 [expr {$YP+1267}] ; paint nsubdiffcont
box values -833 [expr {$YP+1160}] 3233 [expr {$YP+1320}] ; paint metal1
# VSS riser (MNT source) ; NS (M3) ; DN1 (M4) ; VDD bridge+riser ; OC (M5)
box values [expr {$xNT-40}] -1290 [expr {$xNT+40}] -972 ; paint metal1
box values [expr {$xNT-26}] -1026 [expr {$xNT+26}] -974 ; paint m2contact
via_m2m3 $xNT 1000 ; via_m2m3 $xN1 -1000 ; via_m2m3 $xN2 -1000
vseg metal3 $xNT -1300 1000 $H ; hseg metal3 $xNT $xN2 -1300 $H
vseg metal3 $xN1 -1300 -1000 $H ; vseg metal3 $xN2 -1300 -1000 $H
via_m2m4 $xN1 1000 ; via_m2m4 $xN1 [expr {$YP+700}] ; vseg metal4 $xN1 1000 [expr {$YP+700}] $H
via_m2m4 [expr {$xN1-235}] [expr {$YP+980}] ; via_m2m4 [expr {$xN2-235}] [expr {$YP+980}]
hseg metal4 [expr {$xN1-235}] [expr {$xN2-235}] [expr {$YP+980}] $H
vseg metal4 [expr {$xN1-235}] [expr {$YP+700}] [expr {$YP+980}] $H
hseg metal4 [expr {$xN1-235}] $xN1 [expr {$YP+700}] $H
set xNL [expr {$xN1-450}]
box values [expr {$xNL-$H}] [expr {$YP-728}] [expr {$xN2+$H}] [expr {$YP-672}] ; paint metal2
via_m2m3 $xNL [expr {$YP-700}] ; vseg metal3 $xNL [expr {$YP-700}] [expr {$YP+1220}] $H ; via_m1m3 $xNL [expr {$YP+1220}]
via_m2m5 $xN2 1000 ; via_m2m5 $xN2 [expr {$YP+700}] ; vseg metal5 $xN2 1000 [expr {$YP+700}] 44
# OC node access point (M5) at the top of the front-end
set OCx $xN2 ; set OCy [expr {$YP+700}]

# ---------- STRAP: inverters ----------
strap_inv $xI1 4  10 I1
strap_inv $xI2 11 26 I2
strap_inv $xI3 16 44 I3

# ---------- chain S-nets (M4 hop, from ib_inv_chain) ----------
proc chain {src dst} {
    global H
    foreach {ox omy a b} $::COUT($src) break ; foreach {ix imy c d} $::CIN($dst) break
    via_m3m4 $ox $omy ; hseg metal4 $ox $ix $omy $H ; via_m2m4 $ix $omy
}
chain I1 I2
chain I2 I3

# ---------- layer-per-net around the caps: OC=M5, G1=M4, S1=M3 (so the G1/S1 routes
#            cross inter-layer, never short). Cap M4=bottom(G1) / M5=top(OC), full bbox. ----------
set G1x [lindex $::CIN(I1) 0]      ;# INV1 gate tie M2 x (=4565)
set S1x [lindex $::COUT(I1) 0] ; set S1my [lindex $::COUT(I1) 1]
set S3x [lindex $::COUT(I3) 0]
# OC: extend front-end OC M5 up into the cap M5 (top plate)
vseg metal5 $xN2 [expr {$YP+700}] [expr {$ccy+400}] 44
# G1: cap M4 (bottom) -> INV1 gate tie (M4 across, via down to M2)
hseg metal4 [expr {$ccx+200}] $G1x [expr {$ccy+200}] $H
via_m2m4 $G1x [expr {$ccy+200}]
# RFB serpentine terminals (both at bottom): term-A=G1 @ +376, term-B=S1 @ +1816
set tAx [expr {$rfx+376}] ; set tBx [expr {$rfx+856}] ; set tY [expr {$rfy+212}]
box values [expr {$rfx+189}] [expr {$rfy+189}] [expr {$rfx+563}] [expr {$rfy+235}] ; paint metal1
box values [expr {$rfx+1629}] [expr {$rfy+189}] [expr {$rfx+2003}] [expr {$rfy+235}] ; paint metal1
# term-A -> G1 on M4 down into the cap M4
via_m1m4 $tAx $tY ; vseg metal4 $tAx [expr {$ccy+200}] $tY $H
# term-B -> S1 on M3: jog RIGHT to x3200 (clear of the cap x1500..2980) BEFORE descending,
# so the S1 vertical never runs under the cap OC/M5 plate. Then down and to INV1 drain.
via_m1m3 $tBx $tY ; hseg metal3 $tBx 3200 $tY $H
vseg metal3 3200 $S1my $tY $H ; hseg metal3 3200 $S1x $S1my $H
# ---------- R_SER: bot=S3 @ +(376,212), top=OUT @ +(376,784) ----------
box values [expr {$rsx+189}] [expr {$rsy+189}] [expr {$rsx+563}] [expr {$rsy+235}] ; paint metal1
box values [expr {$rsx+189}] [expr {$rsy+761}] [expr {$rsx+563}] [expr {$rsy+807}] ; paint metal1
# bottom term -> S3 (INV3 drain tie M3 @ x8000) on M4 (crosses the M3 VDD riser inter-layer)
via_m1m4 [expr {$rsx+376}] [expr {$rsy+212}]
hseg metal4 $S3x [expr {$rsx+376}] [expr {$rsy+212}] $H
via_m3m4 $S3x [expr {$rsy+212}]

# ---------- VDD / VSS unification ----------
# VSS bus: left metal1 vertical tying front-end VSS strip + inverter VSS strips
set xVSSbus -1000
hseg metal1 $xVSSbus -833 -1230 60
foreach pfx {I1 I2 I3} { foreach {sx sy} $::CVSS($pfx) break ; hseg metal1 $xVSSbus $sx $sy 60 }
set vlo [lindex $::CVSS(I3) 1] ; vseg metal1 $xVSSbus $vlo -1230 60
# VDD bus on METAL2 (its high-y hseg's cross the RFB, whose guard-ring metal1 is VSS
# bulk -- a metal1 VDD bus shorted VDD to VSS there; M2 crosses the RFB metal1 and the
# cap M4/M5 inter-layer). m2contact ties the M2 bus to each metal1 CVDD strip.
set xVDDbus -1300
hseg metal2 $xVDDbus -800 [expr {$YP+1240}] 60
box values -826 [expr {$YP+1214}] -774 [expr {$YP+1266}] ; paint m2contact
foreach pfx {I1 I2 I3} {
    foreach {sx sy} $::CVDD($pfx) break
    hseg metal2 $xVDDbus $sx $sy 60
    box values [expr {$sx-26}] [expr {$sy-26}] [expr {$sx+26}] [expr {$sy+26}] ; paint m2contact
}
set vhi [lindex $::CVDD(I3) 1] ; vseg metal2 $xVDDbus [expr {$YP+1240}] $vhi 60

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "CONV_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<20} {incr i} { drc find ; puts "EB: [box values]" }
}
# ---------- ports ----------
box values [expr {$xNT-260}] 1300 [expr {$xNT-210}] 1360 ; label IBIAS center metal2 ; port make 1
box values [expr {$xN1-260}] 1300 [expr {$xN1-210}] 1360 ; label INP center metal2 ; port make 2
box values [expr {$xN2-260}] 1300 [expr {$xN2-210}] 1360 ; label INM center metal2 ; port make 3
box values [expr {$rsx+348}] [expr {$rsy+761}] [expr {$rsx+404}] [expr {$rsy+807}] ; label OUT center metal1 ; port make 4
box values $xVDDbus [expr {$YP+1500}] $xVDDbus [expr {$YP+1500}] ; box size 56 56 ; label VDD center metal2 ; port make 5
box values [expr {$xVSSbus-60}] -1300 [expr {$xVSSbus-60}] -1300 ; box size 56 56 ; label VSS center metal1 ; port make 6
select top cell
save $OUT/$CELL
puts "CONV_SAVED"
quit -noprompt
