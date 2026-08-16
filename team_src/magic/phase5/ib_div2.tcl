# ib_div2.tcl -- FULL DIV2_QUAD_v1 (1f), flat. Built in stages:
#   A: 2 CML latches (12 W40 nfets + 4x300R) + 3 NMOS bias, cross-coupled + biased.
#   B..C: 4 converters (ib_conv_v1 recipe). D: ports + top routing + gate.
# Latches A and B are IDENTICAL topology ([MA5 MA1 MA3 MA4 MA2 MA6] arrangement); one
# routing proc does each at its yoff. A at yA=0, B at yB below. Cross-couple: A.OI/OIB ->
# B input gates, B.OQ/OQB -> A input gates; CK/CKB swapped between the two tail pairs.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_div2
set H 28 ; set H5 44
proc hseg {lay x1 x2 y hw} { box values [expr {$x1-$hw}] [expr {$y-$hw}] [expr {$x2+$hw}] [expr {$y+$hw}] ; paint $lay }
proc vseg {lay x y1 y2 hw} { box values [expr {$x-$hw}] [expr {$y1-$hw}] [expr {$x+$hw}] [expr {$y2+$hw}] ; paint $lay }

set P 2600
# device x-columns (same for both latch rows): row order [5 1 3 4 2 6]
set x5 0 ; set x1 $P ; set x3 [expr {2*$P}] ; set x4 [expr {3*$P}] ; set x2 [expr {4*$P}] ; set x6 [expr {5*$P}]
set yA 0 ; set yB -7000
# bias row to the right of the latches
set xbias [expr {6*$P}] ; set ybias -3500

drc off ; snap internal
cellname create $CELL ; load $CELL

# ---------- PLACE (distinct names) ----------
foreach {nm x} [list MA5 $x5 MA1 $x1 MA3 $x3 MA4 $x4 MA2 $x2 MA6 $x6] { place_nfet 10 $x $nm 0.3 $yA }
foreach {nm x} [list MB5 $x5 MB1 $x1 MB3 $x3 MB4 $x4 MB2 $x2 MB6 $x6] { place_nfet 10 $x $nm 0.3 $yB }
# 300R loads (w10 l3) above each latch row: A at yA+2400, B at yB+2400. LL x = out-col-2136ish
box values [expr {$x1+64}] [expr {$yA+2400}] [expr {$x1+64}] [expr {$yA+2400}] ; magic::gencell gf180mcu::ppolyf_u_1k RA1 w 10 l 3
box values [expr {$x2+64}] [expr {$yA+2400}] [expr {$x2+64}] [expr {$yA+2400}] ; magic::gencell gf180mcu::ppolyf_u_1k RA2 w 10 l 3
box values [expr {$x1+64}] [expr {$yB+2400}] [expr {$x1+64}] [expr {$yB+2400}] ; magic::gencell gf180mcu::ppolyf_u_1k RB1 w 10 l 3
box values [expr {$x2+64}] [expr {$yB+2400}] [expr {$x2+64}] [expr {$yB+2400}] ; magic::gencell gf180mcu::ppolyf_u_1k RB2 w 10 l 3
# 3 NMOS bias: M_BREF W4 L1 diode, M_TAILA/B W40 L1 (nf=10)
# M_TAILA/B are nf=10 L=1 (maxc=1520, ~3.2um wide) -> space ~3600
place_nfet 1  $xbias              M_BREF  1 $ybias 4
place_nfet 10 [expr {$xbias+2100}] M_TAILA 1 $ybias 4
place_nfet 10 [expr {$xbias+5700}] M_TAILB 1 $ybias 4
flatten ${CELL}_f ; load ${CELL}_f

# ---------- STRAP ----------
foreach x [list $x5 $x1 $x3 $x4 $x2 $x6] { nfet_leg 10 $x 1 0.3 $yA 0 ; nfet_leg 10 $x 1 0.3 $yB 0 }
nfet_leg 1  $xbias           1 1 $ybias 0 4
nfet_leg 10 [expr {$xbias+2100}] 1 1 $ybias 0 4
nfet_leg 10 [expr {$xbias+5700}] 1 1 $ybias 0 4

# shared pwell + VSS psubdiff tap strip, per latch row + bias row
proc pwell_row {x0 x1 yoff} {
    box values [expr {$x0-1200}] [expr {$yoff-1200}] [expr {$x1+1200}] [expr {$yoff+1100}] ; paint pwell
    box values [expr {$x0-833}] [expr {$yoff-1120}] [expr {$x1+833}] [expr {$yoff-1000}] ; paint psubdiff
    box values [expr {$x0-816}] [expr {$yoff-1107}] [expr {$x1+816}] [expr {$yoff-1013}] ; paint psubdiffcont
    box values [expr {$x0-833}] [expr {$yoff-1120}] [expr {$x1+833}] [expr {$yoff-960}] ; paint metal1
}
pwell_row $x5 $x6 $yA
pwell_row $x5 $x6 $yB
pwell_row $xbias [expr {$xbias+5700}] $ybias

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "DIV2_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<16} {incr i} { drc find ; puts "EB: [box values]" }
}
save $OUT/$CELL
puts "DIV2_SAVED"
quit -noprompt
