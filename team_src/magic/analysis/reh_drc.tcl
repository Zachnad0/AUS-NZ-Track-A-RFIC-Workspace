# _reh_drc.tcl -- DRC a reh_* gds and dump per-rule counts + violation boxes.
# arg: cellname (reh_phase8 | reh_base). Coords printed in um.
drc off ; snap internal
gds noduplicates true
set CELL $env(REH_CELL)
gds read /foss/designs/AUS-NZ-integration/gds/$CELL.gds
load $CELL
select top cell
drc euclidean on
drc check
drc catchup
puts "==== $CELL  TOTAL [drc list count total] ===="
# PER-CELL counts -- NOT per-rule. `drc listall count` returns {cellname count} pairs, so this
# is the error count magic attributes to each cell in the hierarchy. The two indices used to be
# swapped here, which printed the count where the cell name belongs; fixed 2026-08-23.
# NOTE the per-cell TOTAL is FRAME-DEPENDENT (84 pre-seat vs 106 seated for identical geometry
# -- docs/verification.md 8). For a gate, dump the BOX SET with analysis/drc_boxset.tcl and
# compare with drc_delta.py; use these numbers for orientation only.
foreach pair [drc listall count] {
    puts "  CELL [lindex $pair 0]  x[lindex $pair 1]"
}
puts "---- violation boxes (um) ----"
# `drc listall why` alternates {rule text} {box box ...} -- it is NOT a list of pairs. Iterating
# it as pairs (as this loop did) feeds the rule string to the box parser and aborts on the first
# non-numeric word. Step by 2 instead.
set why [drc listall why]
for {set i 0} {$i < [llength $why]} {incr i 2} {
    set msg [lindex $why $i]
    puts "  RULE [llength [lindex $why [expr {$i+1}]]] boxes: $msg"
    foreach b [lindex $why [expr {$i+1}]] {
        # b is {llx lly urx ury} in internal units (200/um)
        set llx [expr {[lindex $b 0]/200.0}]
        set lly [expr {[lindex $b 1]/200.0}]
        set urx [expr {[lindex $b 2]/200.0}]
        set ury [expr {[lindex $b 3]/200.0}]
        puts [format "  %-40s (%.3f,%.3f)-(%.3f,%.3f)" $msg $llx $lly $urx $ury]
    }
}
puts "==== END $CELL ===="
