# ib_nmir.tcl -- NMOS mirror row of ibias_gen_v1: MN0/MN1/MN2/MNB (m=24/5/24/2).
# MATCHING (run #3): the ratio-critical MN0(24):MN1(5) pair is COMMON-CENTROID --
# MN0 is split into two nf=12 halves (MN0a|MN0b) flanking MN1 (A-B-A), so MN1 sits at
# MN0's centroid and linear gradients across it cancel. Both halves are drain=gate=NB
# so netgen merges them to m=24 -> the golden is unchanged. End dummies (nf=2) at each
# array end; dummy gate -> NB (uniform gate-field at the edge beats a VSS potential step;
# the small cap sits on the low-Z diode node NB). All gate=NB, all source=VSS.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_nmir4

drc off ; snap internal
cellname create $CELL ; load $CELL

# A-B-A interdigitation: DL | MN0a(12) | MN1(5) | MN0b(12) | MN2(24) | MNB(2) | DR
set cMN0a 3400
set cMN1  [expr {$cMN0a + 3024 + 1260 + 560}]   ;# 8244
set cMN0b [expr {$cMN1  + 1260 + 3024 + 560}]   ;# 13088
set cMN2  [expr {$cMN0b + 3024 + 6048 + 560}]   ;# 22720
set cMNB  [expr {$cMN2  + 6048 +  504 + 560}]   ;# 29832
set cDL   [expr {$cMN0a - 3024 -  504 - 560}]   ;# -688
set cDR   [expr {$cMNB  +  504 +  504 + 560}]   ;# 31400

# place all -> flatten once -> strap
place_nfet  2 $cDL   DL
place_nfet 12 $cMN0a MN0a
place_nfet  5 $cMN1  MN1
place_nfet 12 $cMN0b MN0b
place_nfet 24 $cMN2  MN2
place_nfet  2 $cMNB  MNB
place_nfet  2 $cDR   DR
flatten ${CELL}_f ; load ${CELL}_f
foreach {nf cx} [list 2 $cDL 12 $cMN0a 5 $cMN1 12 $cMN0b 24 $cMN2 2 $cMNB 2 $cDR] { nfet_leg $nf $cx 1 }

# shared NB gate bar (y960) + VSS source bar (y-600) spanning the whole row
set xL [expr {$cDL - 504 - 210}]
set xR [expr {$cDR + 504 + 40}]
box values $xL 932 $xR 988   ; paint metal2   ;# NB bar (merges all gate rails, incl dummies)
box values $xL -628 $xR -572 ; paint metal2   ;# VSS bar (merges all source rails)
# MN0a + MN0b diodes: drain(y600) -> NB bar(960)
foreach cx [list $cMN0a $cMN0b] { box values [expr {$cx-28}] 572 [expr {$cx+28}] 988 ; paint metal2 }
# dummies: tie drain rail (y600) DOWN to the VSS bar (y-600) so S=D=VSS
foreach cx [list $cDL $cDR] { box values [expr {$cx-28}] -628 [expr {$cx+28}] 628 ; paint metal2 }

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "NMIR_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<12} {incr i} { drc find ; puts "EB: [box values]" }
}

# label each net ONCE at a clean spot (gap between MN0b and MN2) with the explicit-layer form
set xNB [expr {($cMN0b+3024+$cMN2-6048)/2}]
box values [expr {$xNB-28}] 940 [expr {$xNB+28}] 980 ; label NB center metal2   ; port make 1
box values [expr {$xNB-28}] -620 [expr {$xNB+28}] -580 ; label VSS center metal2 ; port make 2
box values [expr {$cMN1-40}] 574 [expr {$cMN1+40}] 626 ; label n1 center metal2    ; port make 3
box values [expr {$cMN2-40}] 574 [expr {$cMN2+40}] 626 ; label n2 center metal2    ; port make 4
box values [expr {$cMNB-40}] 574 [expr {$cMNB+40}] 626 ; label VBCPD center metal2 ; port make 5
select top cell
save $OUT/$CELL
puts "NMIR_SAVED"
quit -noprompt
