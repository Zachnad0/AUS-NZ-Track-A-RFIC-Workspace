# ib_nmir.tcl -- NMOS mirror row of ibias_gen_v1: MN0/MN1/MN2/MNB (m=24/5/24/2),
# all gate=NB, all source=VSS; drains NB(diode)/n1/n2/VBCPD. Shared NB and VSS are
# continuous M2 bars bridging the per-leg rails; each net labeled ONCE at its port.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_nmir4

drc off ; snap internal
cellname create $CELL ; load $CELL

set cMN0 6400
set cMN1 [expr {$cMN0 + 6048 + 1260 + 560}]   ;# 14268
set cMN2 [expr {$cMN1 + 1260 + 6048 + 560}]   ;# 22136
set cMNB [expr {$cMN2 + 6048 +  504 + 560}]   ;# 29248

# place all -> flatten once -> strap
place_nfet 24 $cMN0 MN0
place_nfet  5 $cMN1 MN1
place_nfet 24 $cMN2 MN2
place_nfet  2 $cMNB MNB
flatten ${CELL}_f ; load ${CELL}_f
nfet_leg 24 $cMN0 1
nfet_leg  5 $cMN1 1
nfet_leg 24 $cMN2 1
nfet_leg  2 $cMNB 1

# shared NB gate bar (y960) + VSS source bar (y-600) spanning the row
set xL [expr {$cMN0 - 6048 - 210}]
set xR [expr {$cMNB +  504 + 40}]
box values $xL 932 $xR 988   ; paint metal2   ;# NB bar (merges all gate rails)
box values $xL -628 $xR -572 ; paint metal2   ;# VSS bar (merges all source rails)
box values [expr {$cMN0-28}] 572 [expr {$cMN0+28}] 988 ; paint metal2  ;# MN0 diode riser drain->NB

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "NMIR_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<10} {incr i} { drc find ; puts "EB: [box values]" }
}

# label each net ONCE at a clean single-label spot (paint metal2 first so the
# label sticks to metal2, not the underlying pwell), then port make
set xNB [expr {($cMN0+6048+$cMN1-1260)/2}]  ;# gap between MN0 and MN1, over NB bar only
box values [expr {$xNB-28}] 940 [expr {$xNB+28}] 980 ; paint metal2 ; label NB   ; port make 1
box values [expr {$xNB-28}] -620 [expr {$xNB+28}] -580 ; paint metal2 ; label VSS ; port make 2
box values [expr {$cMN1-40}] 574 [expr {$cMN1+40}] 626 ; paint metal2 ; label n1    ; port make 3
box values [expr {$cMN2-40}] 574 [expr {$cMN2+40}] 626 ; paint metal2 ; label n2    ; port make 4
# VBCPD: riser from MNB drain rail up to a metal2 pad in CLEAR FIELD (y720-860,
# above pwell top y700, below the NB bar y932) so the label sticks to metal2.
box values [expr {$cMNB-28}] 600 [expr {$cMNB+28}] 860 ; paint metal2
box values [expr {$cMNB-40}] 760 [expr {$cMNB+40}] 860 ; paint metal2 ; label VBCPD ; port make 5
select top cell
save $OUT/$CELL
puts "NMIR_SAVED"
quit -noprompt
