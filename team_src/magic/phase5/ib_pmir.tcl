# ib_pmir.tcl -- PMOS mirror row of ibias_gen_v1 (L=2). Source=VDD; gates PB
# (MP0/MP1/MP2/XCDEC) or pb2 (MPB). Wide m=24 legs split 2x nf=12 (200um bin).
#  MP0 (diode, PB) | MP1 (p1) | MP2 (p2) | XCDEC (decap, gate PB, D=S=VDD) | MPB (pb2 diode)
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_pmir

drc off ; snap internal
cellname create $CELL ; load $CELL

# x-centers (spacing = maxc_l+maxc_r+560; nf12 maxc=3024, nf5=1260, nf6=1512, nf2=504)
set c0a 3400
set c0b [expr {$c0a + 3024 + 3024 + 560}]   ;# 10008  MP0 halves
set c1  [expr {$c0b + 3024 + 1260 + 560}]   ;# 14852  MP1
set c2a [expr {$c1  + 1260 + 3024 + 560}]   ;# 19696  MP2 halves
set c2b [expr {$c2a + 3024 + 3024 + 560}]   ;# 26304
set cCD [expr {$c2b + 3024 + 1512 + 560}]   ;# 31400  XCDEC
set cPB [expr {$cCD + 1512 +  504 + 560}]   ;# 33976  MPB (pb2)

place_pfet 12 $c0a MP0a
place_pfet 12 $c0b MP0b
place_pfet  5 $c1  MP1
place_pfet 12 $c2a MP2a
place_pfet 12 $c2b MP2b
place_pfet  6 $cCD MPCD
place_pfet  2 $cPB MPB
flatten ${CELL}_f ; load ${CELL}_f
foreach {nf cx} [list 12 $c0a 12 $c0b 5 $c1 12 $c2a 12 $c2b 6 $cCD 2 $cPB] { pfet_leg $nf $cx 1 }

# ---- VDD source bar (y-1500) spanning the whole row ----
set xL [expr {$c0a - 3024 - 210}]
set xR [expr {$cPB +  504 + 40}]
box values $xL -1528 $xR -1472 ; paint metal2   ;# VDD bar
# ---- PB gate bar (y+1780) over MP0a..XCDEC (all gate=PB); MPB gate (pb2) is separate ----
box values $xL 1752 [expr {$cCD+1512-260}] 1808 ; paint metal2
# MP0 diode halves: drain(+1500) -> PB bar(+1780)
foreach cx [list $c0a $c0b] { box values [expr {$cx-28}] 1472 [expr {$cx+28}] 1808 ; paint metal2 }
# p2: merge MP2a + MP2b drain rails (adjacent) at y+1500
box values [expr {$c2a+3024}] 1472 [expr {$c2b-3024}] 1528 ; paint metal2
# XCDEC decap: drain(+1500) -> VDD bar(-1500) (D=S=VDD)
box values [expr {$cCD-28}] -1528 [expr {$cCD+28}] 1528 ; paint metal2
# MPB diode (pb2): gate rail(+1780) + drain rail(+1500) risered together
box values [expr {$cPB-28}] 1472 [expr {$cPB+28}] 1808 ; paint metal2

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "PMIR_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<14} {incr i} { drc find ; puts "EB: [box values]" }
}

# ---- ports (5) ----
set xVDD [expr {($c0b+3024+$c1-1260)/2}]   ;# gap over VDD bar only
box values [expr {$xVDD-28}] -1520 [expr {$xVDD+28}] -1480 ; label VDD center metal2 ; port make 1
box values [expr {$c0b+3024+120}] 1760 [expr {$c0b+3024+176}] 1800 ; label PB center metal2 ; port make 2
box values [expr {$c1-40}] 1474 [expr {$c1+40}] 1526 ; label p1 center metal2 ; port make 3
box values [expr {$c2a+3200}] 1474 [expr {$c2a+3256}] 1526 ; label p2 center metal2 ; port make 4
box values [expr {$cPB-40}] 1474 [expr {$cPB+40}] 1526 ; label pb2 center metal2 ; port make 5
select top cell
save $OUT/$CELL
puts "PMIR_SAVED"
quit -noprompt
