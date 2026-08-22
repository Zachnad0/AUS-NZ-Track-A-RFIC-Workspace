# dump reh added violations: why-list alternates {msg} {boxlist}. um coords.
drc off ; snap internal
gds noduplicates true
set CELL $env(REH_CELL)
gds read /foss/designs/AUS-NZ-integration/gds/$CELL.gds
load $CELL
select top cell
drc euclidean on
drc check
drc catchup
puts "TOTAL [drc list count total]"
set w [drc listall why]
set n [llength $w]
for {set i 0} {$i < $n} {incr i 2} {
    set msg [lindex $w $i]
    set boxes [lindex $w [expr {$i+1}]]
    puts "== RULE: $msg   nboxes=[llength $boxes]"
    # print up to 8 boxes in um (skip the huge PL.5a hierarchical dump)
    set k 0
    foreach b $boxes {
        if {$k >= 8} { puts "   ... (+[expr {[llength $boxes]-8}] more)"; break }
        set llx [expr {[lindex $b 0]/200.0}]
        set lly [expr {[lindex $b 1]/200.0}]
        set urx [expr {[lindex $b 2]/200.0}]
        set ury [expr {[lindex $b 3]/200.0}]
        puts [format "     (%.3f,%.3f)-(%.3f,%.3f)  w=%.3f h=%.3f" $llx $lly $urx $ury [expr {$urx-$llx}] [expr {$ury-$lly}]]
        incr k
    }
}
