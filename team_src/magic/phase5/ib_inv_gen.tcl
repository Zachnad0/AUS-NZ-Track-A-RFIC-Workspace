# ib_inv_gen.tcl -- build the three standalone converter inverters (INV1 10/4, INV2 26/11,
# INV3 44/16) from the SINGLE shared inverter path in ib_inv_lib.tcl (place_inv_dev +
# strap_inv). make_inv just wraps: create -> place -> flatten -> strap -> label ports ->
# save. No inverter geometry lives here anymore -- one path, in ib_inv_lib.tcl.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_inv_lib.tcl
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
set H 28

proc make_inv {cell Wn Wp} {
    global OUT
    drc off ; snap internal
    cellname create $cell ; load $cell
    place_inv_dev 0 $Wn $Wp M
    flatten ${cell}_f ; load ${cell}_f
    strap_inv 0 $Wn $Wp M
    select top cell
    drc on ; drc euclidean on ; drc check ; drc catchup
    puts "${cell}_DRC=[drc list count total]"
    if {[drc list count total] > 0} { puts "WHY: [drc list why]" }
    foreach {ix imy a b} $::CIN(M) break ; box values $ix $imy $ix $imy ; box size 56 56 ; label IN center metal2 ; port make 1
    foreach {ox omy c d} $::COUT(M) break ; box values $ox $omy $ox $omy ; box size 56 56 ; label OUT center metal3 ; port make 2
    foreach {vx vy} $::CVDD(M) break ; box values $vx $vy $vx $vy ; box size 56 56 ; label VDD center metal1 ; port make 3
    foreach {sx sy} $::CVSS(M) break ; box values $sx $sy $sx $sy ; box size 56 56 ; label VSS center metal1 ; port make 4
    select top cell
    save $OUT/$cell
    puts "${cell}_SAVED"
}

make_inv ib_inv1 4  10
make_inv ib_inv2 11 26
make_inv ib_inv3 16 44
quit -noprompt
