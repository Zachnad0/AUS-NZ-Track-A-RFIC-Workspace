# derisk_pfetw.tcl -- isolate: do the converter pfet widths (W10/W26/W44) DRC-clean
# with taps=0 + a clean shared nwell + nwell tap strip (the W8-pfet-validated recipe)?
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set CELL derisk_pfetw
drc off ; snap internal
cellname create $CELL ; load $CELL
set YP 6000
set xa 0 ; set xb 3000 ; set xc 6000
place_pfet 1 $xa PA $YP 0.3 10
place_pfet 1 $xb PB $YP 0.3 26
place_pfet 1 $xc PC $YP 0.3 44
flatten ${CELL}_f ; load ${CELL}_f
pfet_leg 1 $xa 1 0.3 $YP 0 -700 10
pfet_leg 1 $xb 1 0.3 $YP 0 -700 26
pfet_leg 1 $xc 1 0.3 $YP 0 -700 44
# clean shared nwell spanning all three, + an nwell tap strip well ABOVE the tallest
# pfet gate stuff (W44 gate M2 reaches YP+(PG+208)=YP+4608; strip at YP+4800).
box values -1000 [expr {$YP-4600}] 7000 [expr {$YP+4900}] ; paint nwell
box values -900 [expr {$YP+4700}] 6900 [expr {$YP+4820}] ; paint nsubdiff
box values -883 [expr {$YP+4713}] 6883 [expr {$YP+4807}] ; paint nsubdiffcont
box values -900 [expr {$YP+4700}] 6900 [expr {$YP+4820}] ; paint metal1
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "PFETW_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<16} {incr i} { drc find ; puts "EB: [box values]" }
}
quit -noprompt
