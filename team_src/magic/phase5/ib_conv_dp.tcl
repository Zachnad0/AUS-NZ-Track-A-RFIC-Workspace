# ib_conv_dp.tcl -- diff-pair front-end of the DIV2 converter (part of 1e). NMOS-input
# diff pair (M_BN1/M_BN2, W8 L0.3) on a tail (M_NT, W8 L1), PMOS current-mirror load
# (M_BP1 diode/M_BP2, W8 L0.3). Single-ended output OC. Nets: NS(=M_NT.d+BN1.s+BN2.s)
# DN1(=BN1.d+BP1.d/g+BP2.g) OC(=BN2.d+BP2.d). Ports IBIAS INP INM OC VDD VSS.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_conv_dp
set YP 2600
drc off ; snap internal
cellname create $CELL ; load $CELL

set xNT 0 ; set xN1 1200 ; set xN2 2400
# place: nfets y=0 (W8), pfets y=YP (W8). M_NT L=1, rest L=0.3.
place_nfet 1 $xNT MNT 1   0 8
place_nfet 1 $xN1 MBN1 0.3 0 8
place_nfet 1 $xN2 MBN2 0.3 0 8
place_pfet 1 $xN1 MBP1 $YP 0.3 8
place_pfet 1 $xN2 MBP2 $YP 0.3 8
flatten ${CELL}_f ; load ${CELL}_f
nfet_leg 1 $xNT 1 1   0 0 8
nfet_leg 1 $xN1 1 0.3 0 0 8
nfet_leg 1 $xN2 1 0.3 0 0 8
pfet_leg 1 $xN1 1 0.3 $YP 0 -700 8
pfet_leg 1 $xN2 1 0.3 $YP 0 -700 8

# shared pwell (nfets, VSS) + nwell (pfets, VDD), each with a tap strip. Tap diffs are
# 13 wider than their contacts (CO.4); the nwell tap sits ABOVE the pfet gate stuff
# (gate M2 reaches YP+1008) so it does not overlap the device (PL.6/CO.7/DF.1c).
box values -900 -1320 3300 [expr {$YP+1360}] ; paint pwell
box values -833 -1290 3233 -1170 ; paint psubdiff
box values -816 -1277 3216 -1183 ; paint psubdiffcont
box values -833 -1290 3233 -1130 ; paint metal1
box values -900 [expr {$YP-1200}] 3300 [expr {$YP+1360}] ; paint nwell
box values -833 [expr {$YP+1160}] 3233 [expr {$YP+1280}] ; paint nsubdiff
box values -816 [expr {$YP+1173}] 3216 [expr {$YP+1267}] ; paint nsubdiffcont
box values -833 [expr {$YP+1160}] 3233 [expr {$YP+1320}] ; paint metal1

proc hseg {lay x1 x2 y hw} { box values [expr {$x1-$hw}] [expr {$y-$hw}] [expr {$x2+$hw}] [expr {$y+$hw}] ; paint $lay }
proc vseg {lay x y1 y2 hw} { box values [expr {$x-$hw}] [expr {$y1-$hw}] [expr {$x+$hw}] [expr {$y2+$hw}] ; paint $lay }
set H 28

# nfet source rail y-1000, drain rail y+1000, gate M2 y+1332 (G=800). VSS = nfet sources
# + pwell (tap strip). MNT.source=VSS.
# --- VSS: MNT source(M2, y-1000) -> tap strip metal1 (y-1130..-1290): metal1 riser + via1 ---
box values [expr {$xNT-40}] -1290 [expr {$xNT+40}] -972 ; paint metal1
box values [expr {$xNT-26}] -1026 [expr {$xNT+26}] -974 ; paint m2contact
# --- NS (M3): MNT.drain(+1000) + MBN1.s(-1000) + MBN2.s(-1000) ---
via_m2m3 $xNT 1000 ; via_m2m3 $xN1 -1000 ; via_m2m3 $xN2 -1000
vseg metal3 $xNT -1300 1000 $H
hseg metal3 $xNT $xN2 -1300 $H
vseg metal3 $xN1 -1300 -1000 $H
vseg metal3 $xN2 -1300 -1000 $H
# --- DN1 (M4): MBN1.drain(+1000) + MBP1.drain(YP+700)+MBP1.gate+MBP2.gate ---
via_m2m4 $xN1 1000 ; via_m2m4 $xN1 [expr {$YP+700}]
vseg metal4 $xN1 1000 [expr {$YP+700}] $H
# pfet gate M2 rails at far-left (lx). MBP1/MBP2 gates -> DN1. Route gate rails to DN1.
# MBP1 gate rail near xN1-262; MBP2 near xN2-262. Tie both to DN1 (M4 at xN1).
via_m2m4 [expr {$xN1-235}] [expr {$YP+980}] ; via_m2m4 [expr {$xN2-235}] [expr {$YP+980}]
hseg metal4 [expr {$xN1-235}] [expr {$xN2-235}] [expr {$YP+980}] $H
vseg metal4 [expr {$xN1-235}] [expr {$YP+700}] [expr {$YP+980}] $H
hseg metal4 [expr {$xN1-235}] $xN1 [expr {$YP+700}] $H   ;# bridge gate M4 -> DN1 M4 at YP+700
# --- VDD: pfet source rails(YP-700) -> nwell tap strip(YP+1160) on M3 ---
foreach x [list $xN1 $xN2] {
    via_m2m3 $x [expr {$YP-700}] ; vseg metal3 $x [expr {$YP-700}] [expr {$YP+1220}] $H
    via_m1m3 $x [expr {$YP+1220}]
}
# --- OC (M5): MBN2.drain(+1000) + MBP2.drain(YP+700) ---
via_m2m5 $xN2 1000 ; via_m2m5 $xN2 [expr {$YP+700}]
vseg metal5 $xN2 1000 [expr {$YP+700}] 44

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "DP_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<12} {incr i} { drc find ; puts "EB: [box values]" }
}
box values [expr {$xNT-260}] 1300 [expr {$xNT-210}] 1360 ; label IBIAS center metal2 ; port make 1
box values [expr {$xN1-260}] 1300 [expr {$xN1-210}] 1360 ; label INP center metal2 ; port make 2
box values [expr {$xN2-260}] 1300 [expr {$xN2-210}] 1360 ; label INM center metal2 ; port make 3
box values [expr {$xN2-$H}] 1500 [expr {$xN2+$H}] 1560 ; label OC center metal5 ; port make 4
box values -800 -1250 -680 -1170 ; label VSS center metal1 ; port make 5
box values -800 [expr {$YP+1200}] -680 [expr {$YP+1280}] ; label VDD center metal1 ; port make 6
select top cell
save $OUT/$CELL
puts "DP_SAVED"
quit -noprompt
