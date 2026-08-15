# derisk_nfetw.tcl -- isolate: do the converter nfet widths (W4/W11/W16) DRC-clean as
# SELF-CONTAINED legs (taps=1, own pwell+tap)? No shared-well artifacts. Device-only.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set CELL derisk_nfetw
drc off ; snap internal
cellname create $CELL ; load $CELL
set xa 0 ; set xb 3000 ; set xc 6000
place_nfet 1 $xa NA 0.3 0 4
place_nfet 1 $xb NB 0.3 0 11
place_nfet 1 $xc NC 0.3 0 16
flatten ${CELL}_f ; load ${CELL}_f
nfet_leg 1 $xa 1 0.3 0 1 4
nfet_leg 1 $xb 1 0.3 0 1 11
nfet_leg 1 $xc 1 0.3 0 1 16
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "NFETW_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<16} {incr i} { drc find ; puts "EB: [box values]" }
}
quit -noprompt
