# ib_cml.tcl -- ONE CML latch of DIV2_QUAD_v1 (1d). Six W=40 nfets (w4 nf10 L=0.3,
# taps=0) + two 300ohm ppolyf_u_1k loads. Symmetric row [MA5 MA1 MA3 | MA4 MA2 MA6]:
# MA1<->MA2 (input pair), MA3<->MA4 (cross pair), MA5<->MA6 (tail) each mirror about
# the center -> matched OI/OIB paths for I/Q accuracy. Standalone; ports CK CKB OQ OQB
# TAILA OI OIB VDD VSS. Nets: TAILA(=MA5.s+MA6.s) nTA(=MA5.d+MA1.s+MA2.s)
# nLA(=MA6.d+MA3.s+MA4.s) OI(=MA2.d+MA4.d+RA2) OIB(=MA1.d+MA3.d+RA1).
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_cml

drc off ; snap internal
cellname create $CELL ; load $CELL

set P 2600
set xMA5 0 ; set xMA1 $P ; set xMA3 [expr {2*$P}]
set xMA4 [expr {3*$P}] ; set xMA2 [expr {4*$P}] ; set xMA6 [expr {5*$P}]

# place 6 W=40 nfets (distinct names) -> flatten once -> strap (taps=0)
foreach {nm x} [list MA5 $xMA5 MA1 $xMA1 MA3 $xMA3 MA4 $xMA4 MA2 $xMA2 MA6 $xMA6] {
    place_nfet 10 $x $nm 0.3
}
flatten ${CELL}_f ; load ${CELL}_f
foreach x [list $xMA5 $xMA1 $xMA3 $xMA4 $xMA2 $xMA6] { nfet_leg 10 $x 1 0.3 0 0 }

# shared pwell over the whole row + a VSS psubdiff tap strip below (DF.14, clear of
# the source-rail vias at y-600 so no V1.2a)
box values -1200 -1200 [expr {$xMA6+1200}] 1100 ; paint pwell
box values -833 -1120 [expr {$xMA6+833}] -1000 ; paint psubdiff
box values -816 -1107 [expr {$xMA6+816}] -1013 ; paint psubdiffcont
box values -833 -1120 [expr {$xMA6+833}] -960 ; paint metal1

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "CML_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<10} {incr i} { drc find ; puts "EB: [box values]" }
}
save $OUT/$CELL
puts "CML_SAVED"
quit -noprompt
