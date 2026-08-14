# ib_pl1test.tcl -- validate pfet_leg at L=1 (pitch 304). pfet nf=12 W=16 L=1.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_pl1test
drc off ; snap internal
cellname create $CELL ; load $CELL
place_pfet 12 0 M 0 1
flatten ${CELL}_f ; load ${CELL}_f
pfet_leg 12 0 1 1
set maxc [expr {int(12*304/2)}]
box values -40 -1520 40 -1480 ; label VDD center metal2 ; port make 1
box values -40  1480 40  1520 ; label D center metal2 ; port make 2
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "PL1_DRC=[drc list count total]"
if {[drc list count total] > 0} { puts "WHY: [drc list why]"; for {set i 0} {$i<8} {incr i} { drc find ; puts "EB: [box values]" } }
box values -40 1760 40 1800 ; label G center metal2 ; port make 3
select top cell
save $OUT/$CELL
puts "PL1_SAVED"
quit -noprompt
