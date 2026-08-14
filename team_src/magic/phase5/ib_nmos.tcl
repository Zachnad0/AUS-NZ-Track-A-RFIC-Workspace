# ib_nmos.tcl -- full NMOS side of ibias_gen_v1 (7 devices + 2 end dummies).
# Bottom row (L=2, y=0): mirror MN0/MN1/MN2/MNB (24:5:24:2) + end dummies DL/DR.
# Top row (L=1, y=YC): cascodes MNC0/MNC1/MNC2 (24:5:24), bulk = shared pwell (no
# own taps; VSS-tied by the mirror taps). Inter-row: NB on M2 (no crossing), n1/n2
# on M3 to jump the NB M2 bar (layer-per-net-class). Ports: NB IBIAS VGP PA VBCPD VSS.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_nmos
set YC 2000

drc off ; snap internal
cellname create $CELL ; load $CELL

# bottom-row x-centers (as ib_nmir4)
set cMN0 6400
set cMN1 [expr {$cMN0 + 6048 + 1260 + 560}]   ;# 14268
set cMN2 [expr {$cMN1 + 1260 + 6048 + 560}]   ;# 22136
set cMNB [expr {$cMN2 + 6048 +  504 + 560}]   ;# 29248
set cDL  [expr {$cMN0 - 6048 -  504 - 560}]   ;# -712
set cDR  [expr {$cMNB +  504 +  504 + 560}]   ;# 30816
# cascodes centered above their mirrors
set cC0 $cMN0 ; set cC1 $cMN1 ; set cC2 $cMN2

# place all devices (distinct names) -> flatten once -> strap
place_nfet  2 $cDL  DL
place_nfet 24 $cMN0 MN0
place_nfet  5 $cMN1 MN1
place_nfet 24 $cMN2 MN2
place_nfet  2 $cMNB MNB
place_nfet  2 $cDR  DR
place_nfet 24 $cC0  MNC0 1 $YC
place_nfet  5 $cC1  MNC1 1 $YC
place_nfet 24 $cC2  MNC2 1 $YC
flatten ${CELL}_f ; load ${CELL}_f
foreach {nf cx} [list 2 $cDL 24 $cMN0 5 $cMN1 24 $cMN2 2 $cMNB 2 $cDR] { nfet_leg $nf $cx 1 }
# cascodes: L=1, yoff=YC, taps=0 (shared pwell)
nfet_leg 24 $cC0 1 1 $YC 0
nfet_leg  5 $cC1 1 1 $YC 0
nfet_leg 24 $cC2 1 1 $YC 0

# ---- shared pwell over BOTH rows (cascodes have no own pwell) ----
box values -1560 -820 31660 [expr {$YC+700}] ; paint pwell

# ---- bottom-row bars ----
set xL [expr {$cDL - 504 - 210}]
set xR [expr {$cDR + 504 + 40}]
box values $xL 932 $xR 988   ; paint metal2   ;# NB bar (mirror gates)
box values $xL -628 $xR -572 ; paint metal2   ;# VSS bar (mirror sources)
# MN0 diode + NB inter-row riser: MN0 drain(y600) -> NB bar(960) -> MNC0 source(YC-600)
box values [expr {$cMN0-28}] 572 [expr {$cMN0+28}] [expr {$YC-572}] ; paint metal2
# dummies: drain -> VSS
foreach cx [list $cDL $cDR] { box values [expr {$cx-28}] -628 [expr {$cx+28}] 628 ; paint metal2 }

# ---- top-row cascode gate bar = IBIAS (YC+960), + MNC0 diode riser drain->gate ----
set xCL [expr {$cC0 - 3648 - 210}]
set xCR [expr {$cC2 + 3648 + 40}]
box values $xCL [expr {$YC+932}] $xCR [expr {$YC+988}] ; paint metal2   ;# IBIAS gate bar
box values [expr {$cC0-28}] [expr {$YC+572}] [expr {$cC0+28}] [expr {$YC+988}] ; paint metal2  ;# MNC0 diode

# ---- inter-row n1/n2 on M3 (jump the NB M2 bar) ----
foreach cx [list $cMN1 $cMN2] {
    via_m2m3 $cx 600
    via_m2m3 $cx [expr {$YC-600}]
    box values [expr {$cx-$::M2HW}] 600 [expr {$cx+$::M2HW}] [expr {$YC-600}] ; paint metal3
}

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "NMOS_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<14} {incr i} { drc find ; puts "EB: [box values]" }
}

# ---- ports (6), explicit-layer labels ----
box values 12700 940 12756 980 ; label NB center metal2 ; port make 1
box values 12700 -620 12756 -580 ; label VSS center metal2 ; port make 2
box values [expr {$cMNB-40}] 574 [expr {$cMNB+40}] 626 ; label VBCPD center metal2 ; port make 3
box values 12700 [expr {$YC+940}] 12756 [expr {$YC+980}] ; label IBIAS center metal2 ; port make 4
box values [expr {$cC1-40}] [expr {$YC+574}] [expr {$cC1+40}] [expr {$YC+626}] ; label VGP center metal2 ; port make 5
box values [expr {$cC2-40}] [expr {$YC+574}] [expr {$cC2+40}] [expr {$YC+626}] ; label PA center metal2 ; port make 6
select top cell
save $OUT/$CELL
puts "NMOS_SAVED YC=$YC"
quit -noprompt
