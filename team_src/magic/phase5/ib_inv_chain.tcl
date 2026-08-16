# ib_inv_chain.tcl -- the converter's 3-inverter output buffer as a FLAT cell (rung
# toward the full converter 1e). Refactors make_inv into place_inv_dev (placement only)
# + strap_inv (strap + wells + local IN/OUT/VDD/VSS routing at an x-offset, ports left
# UNLABELED, coords stashed in globals). Chain: G1->INV1->S1->INV2->S2->INV3->S3.
# VSS: per-inverter bottom psubdiff strips tied by a left metal1 bus. VDD: per-inverter
# top nsubdiff strips tied by a second left metal1 bus. Ports G1 S1 S2 S3 VDD VSS.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_inv_lib.tcl
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_inv_chain
set H 28

drc off ; snap internal
cellname create $CELL ; load $CELL
# columns spaced 1600 apart (nwell +/-600 -> 400 gap)
set xI1 0 ; set xI2 1600 ; set xI3 3200
place_inv_dev $xI1 4  10 I1
place_inv_dev $xI2 11 26 I2
place_inv_dev $xI3 16 44 I3
flatten ${CELL}_f ; load ${CELL}_f
strap_inv $xI1 4  10 I1
strap_inv $xI2 11 26 I2
strap_inv $xI3 16 44 I3

# --- chain: COUT(I1)->CIN(I2), COUT(I2)->CIN(I3). OUT is M3 @ (x,my); IN is M2 gate
#     tie @ (x-235, spanning gyN..gyP). Route M3 horiz from OUT to dest gate-tie x,
#     via down to M2 onto the gate tie (my_dest lies within [gyN,gyP] of dest). ---
# OUT(M3 @ ox,omy) -> IN(M2 gate tie @ ix). Hop on M4 so it crosses the intermediate
# inverters' VDD risers (M3 @ xoff+400) inter-layer instead of shorting to them.
proc chain {src dst} {
    global H
    foreach {ox omy odyN odyP} $::COUT($src) break
    foreach {ix imy igyN igyP} $::CIN($dst) break
    via_m3m4 $ox $omy
    hseg metal4 $ox $ix $omy $H
    via_m2m4 $ix $omy
}
chain I1 I2
chain I2 I3

# --- VSS bus: left vertical metal1 tying the three bottom strips ---
set xVSS -700
set y1 [lindex $::CVSS(I1) 1] ; set y3 [lindex $::CVSS(I3) 1]
foreach pfx {I1 I2 I3} { foreach {sx sy} $::CVSS($pfx) break ; hseg metal1 $xVSS $sx $sy 60 }
vseg metal1 $xVSS $y3 $y1 60
# --- VDD bus: left vertical metal1 tying the three top strips ---
set xVDD -1000
set v1 [lindex $::CVDD(I1) 1] ; set v3 [lindex $::CVDD(I3) 1]
foreach pfx {I1 I2 I3} { foreach {sx sy} $::CVDD($pfx) break ; hseg metal1 $xVDD $sx $sy 60 }
vseg metal1 $xVDD $v1 $v3 60

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "CHAIN_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<16} {incr i} { drc find ; puts "EB: [box values]" }
}
# ports: label each net once
foreach {pfx net} {I1 G1} { foreach {x y g0 g1} $::CIN($pfx) break ; box values $x $y $x $y ; box size 56 56 ; label $net center metal2 ; port make 1 }
foreach {pfx net idx} {I1 S1 2 I2 S2 3 I3 S3 4} { foreach {x y d0 d1} $::COUT($pfx) break ; box values $x $y $x $y ; box size 56 56 ; label $net center metal3 ; port make $idx }
box values [expr {$xVDD-60}] [expr {($v1+$v3)/2-28}] [expr {$xVDD-60}] [expr {($v1+$v3)/2+28}] ; box size 56 56 ; label VDD center metal1 ; port make 5
box values [expr {$xVSS-60}] [expr {($y1+$y3)/2-28}] [expr {$xVSS-60}] [expr {($y1+$y3)/2+28}] ; box size 56 56 ; label VSS center metal1 ; port make 6
select top cell
save $OUT/$CELL
puts "CHAIN_SAVED"
quit -noprompt
