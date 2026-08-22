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
# per-rule counts
foreach pair [drc listall count] {
    puts "  RULE [lindex $pair 1]  x[lindex $pair 0]"
}
puts "---- violation boxes (um) ----"
foreach pair [drc listall why] {
    set msg [lindex $pair 0]
    foreach b [lrange $pair 1 end] {
        # b is {llx lly urx ury} in internal units (200/um)
        set llx [expr {[lindex $b 0]/200.0}]
        set lly [expr {[lindex $b 1]/200.0}]
        set urx [expr {[lindex $b 2]/200.0}]
        set ury [expr {[lindex $b 3]/200.0}]
        puts [format "  %-40s (%.3f,%.3f)-(%.3f,%.3f)" $msg $llx $lly $urx $ury]
    }
}
puts "==== END $CELL ===="
