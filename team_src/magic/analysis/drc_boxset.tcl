# drc_boxset.tcl -- dump the magic DRC violation BOX SET for a GDS, not just the count.
#
# WHY THIS EXISTS: `drc list count total` is FRAME-DEPENDENT. Seating chip_top inside the
# A01_BH DIEAREA (a pure +200/+200 translation, 2026-08-22) moved the reported total 84 -> 106
# while the violations themselves were bit-identical -- 252 boxes, same places, same
# multiplicities. Magic's per-cell attribution shifts when the parent frame moves. So a phase-8
# "zero added violations" gate must compare the BOX SET, not the total.
#
# Env:
#   GDSF   absolute path to the GDS to check      (required)
#   CELL   top cell name                          (default chip_top)
#   NOPRE  if set, do NOT preload the abstracts   (default: no preload -- full geometry)
# Emits:
#   TOTAL <n>
#   CELLCOUNT <cell> <n>          (one per cell magic attributes errors to)
#   B <x0> <y0> <x1> <y1>         (one per violation box, magic internal units)
#
# Pair with drc_delta.py, which compares two dumps as MULTISETS with an optional frame shift.
# NOTE: this is the full-geometry rule set (84 pre-seat / 106 seated, all PL.5a in
# vco_varactors). `verify_cp.sh` reports 0 for the same GDS because it preloads the
# vco_varactors abstract. Two different rule sets -- never compare across them.
drc off
snap internal
gds noduplicates true
set cell chip_top
if {[info exists env(CELL)]} { set cell $env(CELL) }
gds read $env(GDSF)
load $cell
select top cell
drc euclidean on
drc check
drc catchup
puts "TOTAL [drc list count total]"
foreach pair [drc listall count] {
    # magic returns {cellname count} pairs. analysis/reh_drc.tcl has these two indices
    # swapped and therefore prints the count where the cell name belongs -- do not copy it.
    puts "CELLCOUNT [lindex $pair 0] [lindex $pair 1]"
}
set all [drc listall why]
# `drc listall why` alternates: {rule text} {box box box ...}
for {set i 0} {$i < [llength $all]} {incr i 2} {
    set why [lindex $all $i]
    set boxes [lindex $all [expr {$i + 1}]]
    puts "RULE [llength $boxes] $why"
    foreach b $boxes { puts "B $b" }
}
quit -noprompt
