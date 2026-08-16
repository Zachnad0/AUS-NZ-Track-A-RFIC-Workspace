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
proc hseg {lay x1 x2 y hw} { box values [expr {$x1-$hw}] [expr {$y-$hw}] [expr {$x2+$hw}] [expr {$y+$hw}] ; paint $lay }
proc vseg {lay x y1 y2 hw} { box values [expr {$x-$hw}] [expr {$y1-$hw}] [expr {$x+$hw}] [expr {$y2+$hw}] ; paint $lay }

proc inv_geom {Wn Wp} {
    set Gn [expr {100*$Wn}] ; set PGp [expr {100*$Wp}]
    set gyN [expr {$Gn+532}] ; set YP [expr {$gyN+$PGp+3040}]
    dict create Gn $Gn PGp $PGp gyN $gyN YP $YP dyN [expr {$Gn+200}] syN [expr {-($Gn+200)}] \
        gyP [expr {$YP+$PGp+152}] dyP [expr {$YP+$PGp-100}] syP [expr {$YP-($PGp-100)}] \
        my [expr {(($Gn+200)+($YP+$PGp-100))/2}]
}
proc place_inv_dev {xoff Wn Wp pfx} {
    set g [inv_geom $Wn $Wp]
    place_nfet 1 $xoff N_$pfx 0.3 0 $Wn
    place_pfet 1 $xoff P_$pfx [dict get $g YP] 0.3 $Wp
}
proc strap_inv {xoff Wn Wp pfx} {
    global H
    set g [inv_geom $Wn $Wp]
    foreach k {Gn PGp gyN YP dyN syN gyP dyP syP my} { set $k [dict get $g $k] }
    nfet_leg 1 $xoff 1 0.3 0 0 $Wn
    pfet_leg 1 $xoff 1 0.3 $YP 0 -700 $Wp
    box values [expr {$xoff-400}] [expr {$syN-800}] [expr {$xoff+400}] [expr {$Gn+300}] ; paint pwell
    box values [expr {$xoff-383}] [expr {$syN-690}] [expr {$xoff+383}] [expr {$syN-570}] ; paint psubdiff
    box values [expr {$xoff-366}] [expr {$syN-677}] [expr {$xoff+366}] [expr {$syN-583}] ; paint psubdiffcont
    box values [expr {$xoff-383}] [expr {$syN-690}] [expr {$xoff+383}] [expr {$syN-570}] ; paint metal1
    box values [expr {$xoff-110}] [expr {$syN-600}] [expr {$xoff-54}] [expr {$syN+20}] ; paint metal1
    box values [expr {$xoff-108}] [expr {$syN-26}] [expr {$xoff-56}] [expr {$syN+26}] ; paint m2contact
    box values [expr {$xoff-600}] [expr {$YP-($PGp+340)}] [expr {$xoff+600}] [expr {$gyP+400}] ; paint nwell
    box values [expr {$xoff-400}] [expr {$gyP+200}] [expr {$xoff+400}] [expr {$gyP+320}] ; paint nsubdiff
    box values [expr {$xoff-383}] [expr {$gyP+213}] [expr {$xoff+383}] [expr {$gyP+307}] ; paint nsubdiffcont
    box values [expr {$xoff-400}] [expr {$gyP+200}] [expr {$xoff+400}] [expr {$gyP+360}] ; paint metal1
    vseg metal2 [expr {$xoff-235}] $gyN $gyP $H
    via_m2m3 $xoff $dyN ; via_m2m3 $xoff $dyP ; vseg metal3 $xoff $dyN $dyP $H
    box values [expr {$xoff+122}] [expr {$syP-$H}] [expr {$xoff+428}] [expr {$syP+$H}] ; paint metal2
    via_m2m3 [expr {$xoff+400}] $syP ; vseg metal3 [expr {$xoff+400}] $syP [expr {$gyP+260}] $H ; via_m1m3 [expr {$xoff+400}] [expr {$gyP+260}]
    set ::CIN($pfx) [list [expr {$xoff-235}] $my $gyN $gyP]
    set ::COUT($pfx) [list $xoff $my $dyN $dyP]
    set ::CVSS($pfx) [list $xoff [expr {$syN-630}]]
    set ::CVDD($pfx) [list $xoff [expr {$gyP+280}]]
}

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
# passives: RFB (20k w2 l40) left of INV1; R_SER (1k w2 l2) right of INV3; CC (100f w5 l10)
# in the channel above the front-end. gencell draws up/right from the box LL.
box values 3900 3200 3900 3200 ; magic::gencell gf180mcu::ppolyf_u_1k RFB w 2 l 40
box values 9000 200 9000 200 ; magic::gencell gf180mcu::ppolyf_u_1k RSER w 2 l 2
box values 1600 5200 1600 5200 ; magic::gencell gf180mcu::cap_mim_2p0fF CC w 5 l 10
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

# ---------- CC cap: OC(M5) -> top plate ; bottom plate -> G1(M2 gate tie of INV1) ----------
# cap CC drawn from LL (1600,5200): plates ~ m4 (bottom) / m5 (top). Access both plates.
# top(m5) -> OC(M5) route ; bottom(m4) -> G1.  (approx plate access points; refine on DRC)
set G1x [lindex $::CIN(I1) 0] ; set G1my [lindex $::CIN(I1) 1]
# OC(M5 @ OCx,OCy) up to cap region y, across to cap top plate
via_m2m5 $xN2 [expr {$YP+700}]
hseg metal5 $xN2 2100 5700 44 ;# OC M5 into cap-top area (placeholder plate contact)
# G1 access: gate tie M2 @ (G1x,G1my). bring bottom plate (m4) down to G1 on M4->M2
via_m2m4 $G1x $G1my
hseg metal4 2100 $G1x 5500 $H
# ---------- RFB 20k: S1 -> G1 ----------
set S1x [lindex $::COUT(I1) 0] ; set S1my [lindex $::COUT(I1) 1]
# RFB drawn from (3900,3200) w2 l40 -> vertical strip; ends ~ bottom y3200 / top y11200.
# bottom end -> G1 (M2) ; top end -> S1 (M3). (metal1 over end polycontacts + risers)
box values 3941 3389 4059 3435 ; paint metal1 ; via_m1m3 4000 3410 ; hseg metal3 3800 $G1x 3410 $H ; via_m2m3 $G1x 3410
box values 3941 11189 4059 11235 ; paint metal1 ; via_m1m3 4000 11210
# ---------- R_SER 1k: S3 -> OUT ----------
set S3x [lindex $::COUT(I3) 0] ; set S3my [lindex $::COUT(I3) 1]
# RSER from (9000,200) w2 l2 -> small; bottom end -> S3(M3) ; top end -> OUT port
box values 9041 389 9159 435 ; paint metal1 ; via_m1m3 9100 410 ; hseg metal3 $S3x 9100 $S3my $H
box values 9041 589 9159 635 ; paint metal1 ; via_m1m3 9100 610

# ---------- VDD / VSS unification ----------
# VSS bus: left metal1 vertical tying front-end VSS strip + inverter VSS strips
set xVSSbus -1000
hseg metal1 $xVSSbus -833 -1230 60
foreach pfx {I1 I2 I3} { foreach {sx sy} $::CVSS($pfx) break ; hseg metal1 $xVSSbus $sx $sy 60 }
set vlo [lindex $::CVSS(I3) 1] ; vseg metal1 $xVSSbus $vlo -1230 60
# VDD bus: left metal1 vertical tying front-end VDD strip (y~YP+1240) + inverter VDD strips
set xVDDbus -1300
hseg metal1 $xVDDbus -833 [expr {$YP+1240}] 60
foreach pfx {I1 I2 I3} { foreach {sx sy} $::CVDD($pfx) break ; hseg metal1 $xVDDbus $sx $sy 60 }
set vhi [lindex $::CVDD(I3) 1] ; vseg metal1 $xVDDbus [expr {$YP+1240}] $vhi 60

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
box values 9091 585 9147 641 ; label OUT center metal1 ; port make 4
box values [expr {$xVDDbus-60}] 3000 [expr {$xVDDbus-60}] 3000 ; box size 56 56 ; label VDD center metal1 ; port make 5
box values [expr {$xVSSbus-60}] -1300 [expr {$xVSSbus-60}] -1300 ; box size 56 56 ; label VSS center metal1 ; port make 6
select top cell
save $OUT/$CELL
puts "CONV_SAVED"
quit -noprompt
