# ib_l1test.tcl -- validate the parameterized generator at L=1 (pitch 304).
# One strapped nfet nf=5 W=4 L=1, S->bottom rail, D->top rail, gate poly rail.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_l1test
drc off ; snap internal
cellname create $CELL ; load $CELL
place_nfet 5 0 M 1
flatten ${CELL}_f ; load ${CELL}_f
nfet_leg 5 0 1 1
# label S/D/G once (explicit-layer form)
set maxc [expr {int(5*304/2)}]
box values [expr {-$maxc-40}] -628 [expr {$maxc+40}] -572 ; paint metal2
box values [expr {-$maxc-40}]  572 [expr {$maxc+40}]  628 ; paint metal2
box values -40 -620 40 -580 ; label S center metal2 ; port make 1
box values -40 574 40 626   ; label D center metal2 ; port make 2
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "L1_DRC=[drc list count total]"
if {[drc list count total] > 0} { puts "WHY: [drc list why]"; for {set i 0} {$i<6} {incr i} { drc find ; puts "EB: [box values]" } }
# gate port: on the NB-style M2 gate rail at y960
box values -40 940 40 980 ; label G center metal2 ; port make 3
select top cell
save $OUT/$CELL
puts "L1_SAVED"
quit -noprompt
