# ib_ptest.tcl -- validate pfet_leg on one strapped pfet nf=12 W=16 L=2 (192um,
# under the 200um model bin). source->VDD (+nwell tap), drain->D, gate->G.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_ptest
drc off ; snap internal
cellname create $CELL ; load $CELL
place_pfet 12 0 M
flatten ${CELL}_f ; load ${CELL}_f
pfet_leg 12 0 1
set maxc [expr {int(12*504/2)}]
box values -40 -1520 40 -1480 ; label VDD center metal2 ; port make 1
box values -40  1480 40  1520 ; label D center metal2 ; port make 2
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "PT_DRC=[drc list count total]"
if {[drc list count total] > 0} { puts "WHY: [drc list why]"; for {set i 0} {$i<8} {incr i} { drc find ; puts "EB: [box values]" } }
box values -40 1760 40 1800 ; label G center metal2 ; port make 3
select top cell
save $OUT/$CELL
puts "PT_SAVED"
quit -noprompt
