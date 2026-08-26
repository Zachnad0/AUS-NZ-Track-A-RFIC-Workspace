# drc_boxset.tcl -- dump the magic DRC violation BOX SET for a GDS, not just the count.
#
# WHY THIS EXISTS: `drc list count total` is FRAME-DEPENDENT. Seating chip_top inside the
# A01_BH DIEAREA (a pure +200/+200 translation, 2026-08-22) moved the reported total 84 -> 106
# while the violations themselves were bit-identical -- 252 boxes, same places, same
# multiplicities. Magic's per-cell attribution shifts when the parent frame moves. So a phase-8
# "zero added violations" gate must compare the BOX SET, not the total.
#
# THE THREE FIGURES ARE THREE DIFFERENT THINGS (measured 2026-08-25, do not conflate):
#   252  emitted B lines  -- MAXIMAL HORIZONTAL STRIPS of DRC error paint. What this file
#                            dumps. Invariant across hierarchy level, frame and layout edits.
#    84  connected regions -- the PHYSICAL violation count, obtained by merging the 252 strips
#                            (252 = 84 x 3). Cross-confirmed by KLayout's 84 PL.5a_LV waivers.
#   TOTAL                  -- magic's frame-dependent re-tiling: reads 84 from vco_varactors or
#                            vco_v1 and 108 from chip_top for the SAME geometry. NOT an
#                            invariant. NEVER gate on it. It is emitted for reporting only.
#
# PROVENANCE: a .drcbase is only meaningful against the GDS it was dumped from. This dump
# therefore records GDSBLOB (git blob sha of the GDS) and SRCCOMMIT (repo HEAD at dump time),
# and drc_delta.py reports a GDSBLOB mismatch out loud instead of leaving the difference to
# surface as a TOTAL nobody reads. The 2026-08-22 baseline's stale "TOTAL 106" cost a full
# investigation cycle for exactly that reason: it had been dumped from a pre-routing GDS.
#
# Env:
#   GDSF   absolute path to the GDS to check      (required)
#   CELL   top cell name                          (default chip_top)
#   NOPRE  if set, do NOT preload the abstracts   (default: no preload -- full geometry)
# Emits:
#   GDSF <path> / GDSBLOB <sha> / SRCCOMMIT <sha>   (provenance header)
#   TOTAL <n>                     (reporting only -- see above, never a gate)
#   CELLCOUNT <cell> <n>          (one per cell magic attributes errors to)
#   RULE <n> <text>               (one per violated rule, n = boxes for that rule)
#   B <x0> <y0> <x1> <y1>         (one per violation box, magic internal units)
#   SELFCHECK OK|FAIL ...         (see below; FAIL also exits non-zero)
#
# Pair with drc_delta.py, which compares two dumps as MULTISETS with an optional frame shift.
# NOTE: this is the full-geometry rule set (all PL.5a in vco_varactors). `verify_cp.sh` reports
# 0 for the same GDS because it preloads the vco_varactors abstract. Never compare across them.
drc off
snap internal
gds noduplicates true
set cell chip_top
if {[info exists env(CELL)]} { set cell $env(CELL) }
set gdsf $env(GDSF)

# --- provenance header -------------------------------------------------------------------
# git is anchored at the GDS's own directory, which is inside the repo. Any of these may be
# unavailable (GDS outside a checkout, no git); record "unknown" rather than failing the dump.
set gdir [file dirname $gdsf]
if {[catch {exec git -c safe.directory=* -C $gdir rev-parse HEAD} srccommit]}     { set srccommit "unknown" }
if {[catch {exec git -c safe.directory=* -C $gdir hash-object $gdsf} gdsblob]}    { set gdsblob   "unknown" }
puts "GDSF $gdsf"
puts "GDSBLOB $gdsblob"
puts "SRCCOMMIT $srccommit"

gds read $gdsf
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

# INDEPENDENT expected count, walked with a SEPARATE traversal of the whole list before the
# emit loop runs. This is the point of the check: comparing the emit loop against a count it
# accumulated itself would be circular and would not catch a truncated walk -- which is the
# exact defect reh_drc.tcl shipped. `foreach {a b}` consumes the list two elements at a time
# and so covers every pair regardless of what the emit loop below does.
set expect 0
foreach {why boxes} $all { incr expect [llength $boxes] }
set npairs [expr {[llength $all] / 2}]
if {[llength $all] % 2 != 0} {
    puts stderr "FATAL: `drc listall why` returned an ODD list ([llength $all] elements)."
    puts stderr "       It is documented to alternate {rule}{boxes}; the parse below is unsafe."
    puts "SELFCHECK FAIL odd-list len=[llength $all]"
    flush stdout
    exit 1
}

set emitted 0
set rulesseen 0
for {set i 0} {$i < [llength $all]} {incr i 2} {
    set why [lindex $all $i]
    set boxes [lindex $all [expr {$i + 1}]]
    incr rulesseen
    puts "RULE [llength $boxes] $why"
    foreach b $boxes { puts "B $b" ; incr emitted }
}

# --- SELF-CHECK: the dump must be COMPLETE ------------------------------------------------
# The box multiset is the gate for every rung, so a silently truncated dump would read as
# "no violations added" -- a false PASS, the worst possible failure mode here. Verified
# 2026-08-25 on a single-rule population (1 rule / 252 boxes); the ESD rung may be the first
# multi-rule dump, which is why this is wired in before it rather than after.
if {$emitted != $expect || $rulesseen != $npairs} {
    puts stderr "========================================================================"
    puts stderr "FATAL: drc_boxset.tcl EMITTED AN INCOMPLETE DUMP -- DO NOT GATE ON IT."
    puts stderr "  rules: walked $rulesseen of $npairs pairs"
    puts stderr "  boxes: emitted $emitted of $expect"
    puts stderr "A short dump reads downstream as 'no violations added' -- a false PASS."
    puts stderr "========================================================================"
    puts "SELFCHECK FAIL rules=$rulesseen/$npairs boxes=$emitted/$expect"
    flush stdout
    exit 1
}
puts "SELFCHECK OK rules=$rulesseen/$npairs boxes=$emitted/$expect"
quit -noprompt
