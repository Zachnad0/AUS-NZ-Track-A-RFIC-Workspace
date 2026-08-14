# ib_nmir.tcl -- NMOS mirror row of ibias_gen_v1: MN0/MN1/MN2/MNB (m=24/5/24/2),
# all gate=NB, all source=VSS; drains NB(diode)/n1/n2/VBCPD. Plus an END DUMMY nfet
# (nf=2) at each end of the ratio-critical array: gate->NB, S+D->VSS (tied off) for a
# matched edge environment. Shared NB and VSS are continuous M2 bars; each net labeled
# ONCE at its port with the explicit-layer form `label X center metal2`.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_nmir4

drc off ; snap internal
cellname create $CELL ; load $CELL

set cMN0 6400
set cMN1 [expr {$cMN0 + 6048 + 1260 + 560}]   ;# 14268
set cMN2 [expr {$cMN1 + 1260 + 6048 + 560}]   ;# 22136
set cMNB [expr {$cMN2 + 6048 +  504 + 560}]   ;# 29248
set cDL  [expr {$cMN0 - 6048 -  504 - 560}]   ;# -712  left end dummy (nf=2)
set cDR  [expr {$cMNB +  504 +  504 + 560}]   ;# 30816 right end dummy (nf=2)

# place all -> flatten once -> strap
place_nfet  2 $cDL  DL
place_nfet 24 $cMN0 MN0
place_nfet  5 $cMN1 MN1
place_nfet 24 $cMN2 MN2
place_nfet  2 $cMNB MNB
place_nfet  2 $cDR  DR
flatten ${CELL}_f ; load ${CELL}_f
foreach {nf cx} [list 2 $cDL 24 $cMN0 5 $cMN1 24 $cMN2 2 $cMNB 2 $cDR] { nfet_leg $nf $cx 1 }

# shared NB gate bar (y960) + VSS source bar (y-600) spanning the whole row
set xL [expr {$cDL - 504 - 210}]
set xR [expr {$cDR + 504 + 40}]
box values $xL 932 $xR 988   ; paint metal2   ;# NB bar (merges all gate rails, incl dummies)
box values $xL -628 $xR -572 ; paint metal2   ;# VSS bar (merges all source rails)
box values [expr {$cMN0-28}] 572 [expr {$cMN0+28}] 988 ; paint metal2  ;# MN0 diode: drain->NB
# dummies: tie drain rail (y600) DOWN to the VSS bar (y-600) so S=D=VSS
foreach cx [list $cDL $cDR] {
    box values [expr {$cx-28}] -628 [expr {$cx+28}] 628 ; paint metal2
}

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "NMIR_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<12} {incr i} { drc find ; puts "EB: [box values]" }
}

# label each net ONCE at a clean spot with the explicit-layer form, then port make
set xNB [expr {($cMN0+6048+$cMN1-1260)/2}]  ;# gap between MN0 and MN1, over NB bar only
box values [expr {$xNB-28}] 940 [expr {$xNB+28}] 980 ; label NB center metal2   ; port make 1
box values [expr {$xNB-28}] -620 [expr {$xNB+28}] -580 ; label VSS center metal2 ; port make 2
box values [expr {$cMN1-40}] 574 [expr {$cMN1+40}] 626 ; label n1 center metal2    ; port make 3
box values [expr {$cMN2-40}] 574 [expr {$cMN2+40}] 626 ; label n2 center metal2    ; port make 4
box values [expr {$cMNB-40}] 574 [expr {$cMNB+40}] 626 ; label VBCPD center metal2 ; port make 5
select top cell
save $OUT/$CELL
puts "NMIR_SAVED"
quit -noprompt
