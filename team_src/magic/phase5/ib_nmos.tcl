# ib_nmos.tcl -- full NMOS side of ibias_gen_v1 (7 devices + 2 end dummies).
# Bottom row (L=2, y=0): mirror, COMMON-CENTROID on the 24:5 pair -- MN0 split into
# MN0a|MN0b (nf=12 each) flanking MN1 (A-B-A), + end dummies DL/DR. Top row (L=1,
# y=YC): cascodes MNC0/MNC1/MNC2, bulk = shared pwell. Inter-row: NB/n1/n2. Cascodes
# align cC1 over MN1 and cC2 over MN2; MNC0 connects to NB via the bar. Ports: NB
# IBIAS VGP PA VBCPD VSS.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_nmos
set YC 2000

drc off ; snap internal
cellname create $CELL ; load $CELL

# A-B-A mirror: DL | MN0a(12) | MN1(5) | MN0b(12) | MN2(24) | MNB(2) | DR
set cMN0a 3400
set cMN1  [expr {$cMN0a + 3024 + 1260 + 560}]   ;# 8244
set cMN0b [expr {$cMN1  + 1260 + 3024 + 560}]   ;# 13088
set cMN2  [expr {$cMN0b + 3024 + 6048 + 560}]   ;# 22720
set cMNB  [expr {$cMN2  + 6048 +  504 + 560}]   ;# 29832
set cDL   [expr {$cMN0a - 3024 -  504 - 560}]   ;# -688
set cDR   [expr {$cMNB  +  504 +  504 + 560}]   ;# 31400
# cascodes: MNC0 over the MN0a region (source->NB via bar), MNC1 over MN1, MNC2 over MN2
set cC0 $cMN0a ; set cC1 $cMN1 ; set cC2 $cMN2

place_nfet  2 $cDL   DL
place_nfet 12 $cMN0a MN0a
place_nfet  5 $cMN1  MN1
place_nfet 12 $cMN0b MN0b
place_nfet 24 $cMN2  MN2
place_nfet  2 $cMNB  MNB
place_nfet  2 $cDR   DR
place_nfet 24 $cC0 MNC0 1 $YC ; place_nfet 5 $cC1 MNC1 1 $YC ; place_nfet 24 $cC2 MNC2 1 $YC
flatten ${CELL}_f ; load ${CELL}_f
foreach {nf cx} [list 2 $cDL 12 $cMN0a 5 $cMN1 12 $cMN0b 24 $cMN2 2 $cMNB 2 $cDR] { nfet_leg $nf $cx 1 }
nfet_leg 24 $cC0 1 1 $YC 0 ; nfet_leg 5 $cC1 1 1 $YC 0 ; nfet_leg 24 $cC2 1 1 $YC 0

# ---- shared pwell over BOTH rows ----
box values [expr {$cDL-844}] -820 [expr {$cDR+844}] [expr {$YC+700}] ; paint pwell
# ---- bottom-row bars ----
set xL [expr {$cDL - 504 - 210}] ; set xR [expr {$cDR + 504 + 40}]
box values $xL 932 $xR 988   ; paint metal2
box values $xL -628 $xR -572 ; paint metal2
# MN0a diode + NB inter-row riser (MN0a drain -> NB bar -> MNC0 source); MN0b diode -> NB bar
box values [expr {$cMN0a-28}] 572 [expr {$cMN0a+28}] [expr {$YC-572}] ; paint metal2
box values [expr {$cMN0b-28}] 572 [expr {$cMN0b+28}] 988 ; paint metal2
foreach cx [list $cDL $cDR] { box values [expr {$cx-28}] -628 [expr {$cx+28}] 628 ; paint metal2 }
# ---- cascode gate bar = IBIAS + MNC0 diode ----
box values [expr {$cC0-3648-210}] [expr {$YC+932}] [expr {$cC2+3648+40}] [expr {$YC+988}] ; paint metal2
box values [expr {$cC0-28}] [expr {$YC+572}] [expr {$cC0+28}] [expr {$YC+988}] ; paint metal2
# ---- inter-row n1/n2 on M3 (cC1 over MN1, cC2 over MN2 -> vertical risers) ----
foreach cx [list $cMN1 $cMN2] {
    via_m2m3 $cx 600 ; via_m2m3 $cx [expr {$YC-600}]
    box values [expr {$cx-$::M2HW}] 600 [expr {$cx+$::M2HW}] [expr {$YC-600}] ; paint metal3
}

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "NMOS_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<14} {incr i} { drc find ; puts "EB: [box values]" }
}

# ---- ports (6) ----
set xg [expr {($cMN0b+3024+$cMN2-6048)/2}]
box values [expr {$xg-28}] 940 [expr {$xg+28}] 980 ; label NB center metal2 ; port make 1
box values [expr {$xg-28}] -620 [expr {$xg+28}] -580 ; label VSS center metal2 ; port make 2
box values [expr {$cMNB-40}] 574 [expr {$cMNB+40}] 626 ; label VBCPD center metal2 ; port make 3
box values 7002 [expr {$YC+940}] 7058 [expr {$YC+980}] ; label IBIAS center metal2 ; port make 4
box values [expr {$cC1-40}] [expr {$YC+574}] [expr {$cC1+40}] [expr {$YC+626}] ; label VGP center metal2 ; port make 5
box values [expr {$cC2-40}] [expr {$YC+574}] [expr {$cC2+40}] [expr {$YC+626}] ; label PA center metal2 ; port make 6
select top cell
save $OUT/$CELL
puts "NMOS_SAVED"
quit -noprompt
