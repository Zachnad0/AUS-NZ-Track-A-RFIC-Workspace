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
# 300ohm ppolyf_u_1k loads (w10 l3) above the OIB / OI regions. box LL -> device drawn
# from LL-60; terminals (polycontact) at LL+189..235 (bottom=OIB/OI) and LL+961..1007
# (top=VDD), x = LL+189..2163.
set rLLy 2400
box values 2264 $rLLy 2264 $rLLy ; magic::gencell gf180mcu::ppolyf_u_1k RA1 w 10 l 3
box values 7464 $rLLy 7464 $rLLy ; magic::gencell gf180mcu::ppolyf_u_1k RA2 w 10 l 3
flatten ${CELL}_f ; load ${CELL}_f
foreach x [list $xMA5 $xMA1 $xMA3 $xMA4 $xMA2 $xMA6] { nfet_leg 10 $x 1 0.3 0 0 }

# shared pwell over the whole row + a VSS psubdiff tap strip below (DF.14, clear of
# the source-rail vias at y-600 so no V1.2a)
box values -1200 -1200 [expr {$xMA6+1200}] 1100 ; paint pwell
box values -833 -1120 [expr {$xMA6+833}] -1000 ; paint psubdiff
box values -816 -1107 [expr {$xMA6+816}] -1013 ; paint psubdiffcont
box values -833 -1120 [expr {$xMA6+833}] -960 ; paint metal1

# ================= ROUTING =================
# offset access within each ±860 rail: drain via at x-400, source via at x+400, so a
# device's own source and drain routes never share an x.
# segments extend hw past each endpoint so L-corners fully overlap (no sub-width notch)
proc hseg {lay x1 x2 y hw} { box values [expr {$x1-$hw}] [expr {$y-$hw}] [expr {$x2+$hw}] [expr {$y+$hw}] ; paint $lay }
proc vseg {lay x y1 y2 hw} { box values [expr {$x-$hw}] [expr {$y1-$hw}] [expr {$x+$hw}] [expr {$y2+$hw}] ; paint $lay }
set H 28 ; set H5 44

# --- OIB (M3, y600): MA1.d(-400) + MA3.d(-400) ---
via_m2m3 [expr {$xMA1-400}] 600 ; via_m2m3 [expr {$xMA3-400}] 600
hseg metal3 [expr {$xMA1-400}] [expr {$xMA3-400}] 600 $H
# --- OI (M3, y600): MA2.d(-400) + MA4.d(-400) ---
via_m2m3 [expr {$xMA2-400}] 600 ; via_m2m3 [expr {$xMA4-400}] 600
hseg metal3 [expr {$xMA4-400}] [expr {$xMA2-400}] 600 $H
# --- nTA (M4, horiz y-900): MA5.d(-400,+600) + MA1.s(+400) + MA2.s(+400) ---
via_m2m4 [expr {$xMA5-400}] 600 ; via_m2m4 [expr {$xMA1+400}] -600 ; via_m2m4 [expr {$xMA2+400}] -600
vseg metal4 [expr {$xMA5-400}] -900 600 $H
hseg metal4 [expr {$xMA5-400}] [expr {$xMA2+400}] -900 $H
vseg metal4 [expr {$xMA1+400}] -900 -600 $H
vseg metal4 [expr {$xMA2+400}] -900 -600 $H
# --- nLA (M5, horiz y+1150): MA6.d(-400,+600) + MA3.s(+400) + MA4.s(+400) ---
via_m2m5 [expr {$xMA6-400}] 600 ; via_m2m5 [expr {$xMA3+400}] -600 ; via_m2m5 [expr {$xMA4+400}] -600
vseg metal5 [expr {$xMA6-400}] 600 1150 $H5
hseg metal5 [expr {$xMA3+400}] [expr {$xMA6-400}] 1150 $H5
vseg metal5 [expr {$xMA3+400}] -600 1150 $H5
vseg metal5 [expr {$xMA4+400}] -600 1150 $H5
# --- TAILA (M3, horiz y-750): MA5.s(+400) + MA6.s(+400). On M3 so it crosses nTA(M4)
#     and nLA(M5) verticals inter-layer, not on M4 where nTA's risers would short it. ---
via_m2m3 [expr {$xMA5+400}] -600 ; via_m2m3 [expr {$xMA6+400}] -600
vseg metal3 [expr {$xMA5+400}] -750 -600 $H
hseg metal3 [expr {$xMA5+400}] [expr {$xMA6+400}] -750 $H
vseg metal3 [expr {$xMA6+400}] -750 -600 $H
# --- cross-coupled gates: MA3.g=OI (M3), MA4.g=OIB (M4, different layer so they cross) ---
# MA3.gate(5200,960) -> OI drain node (MA4.d at xMA4-400,600) on M3
via_m2m3 $xMA3 960 ; via_m2m3 [expr {$xMA4-400}] 600
hseg metal3 $xMA3 [expr {$xMA4-400}] 960 $H
vseg metal3 [expr {$xMA4-400}] 600 960 $H
# MA4.gate(7800,960) -> OIB drain node (MA3.d at xMA3-400,600) on M4
via_m2m4 $xMA4 960 ; via_m2m4 [expr {$xMA3-400}] 600
hseg metal4 [expr {$xMA3-400}] $xMA4 960 $H
vseg metal4 [expr {$xMA3-400}] 600 960 $H

# --- resistor loads: bottom terminal -> OIB/OI (M3 down over the gate rails), top -> VDD ---
# RA1 (OIB): bottom polycontact x2453..4427 y2589..2635 ; top y3361..3407
box values 2453 2589 4427 2635 ; paint metal1
via_m1m3 2600 2610 ; vseg metal3 2600 600 2610 $H
box values 2453 3361 4427 3407 ; paint metal1
via_m1m4 2600 3384 ; vseg metal4 2600 3384 3800 $H
# RA2 (OI): bottom x7653..9627 y2589..2635 ; top y3361..3407
box values 7653 2589 9627 2635 ; paint metal1
via_m1m3 8700 2610 ; vseg metal3 8700 600 2610 $H
box values 7653 3361 9627 3407 ; paint metal1
via_m1m4 8700 3384 ; vseg metal4 8700 3384 3800 $H
# VDD rail (M4, y3800) joining both resistor tops
hseg metal4 2600 8700 3800 $H

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "CML_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<12} {incr i} { drc find ; puts "EB: [box values]" }
}

# ports: label each net once
box values [expr {$xMA5-40}] 940 [expr {$xMA5+40}] 980 ; label CK center metal2 ; port make 1
box values [expr {$xMA6-40}] 940 [expr {$xMA6+40}] 980 ; label CKB center metal2 ; port make 2
box values [expr {$xMA1-40}] 940 [expr {$xMA1+40}] 980 ; label OQ center metal2 ; port make 3
box values [expr {$xMA2-40}] 940 [expr {$xMA2+40}] 980 ; label OQB center metal2 ; port make 4
box values [expr {($xMA1+$xMA3)/2-28}] 572 [expr {($xMA1+$xMA3)/2+28}] 628 ; label OIB center metal3 ; port make 5
box values [expr {($xMA4+$xMA2)/2-28}] 572 [expr {($xMA4+$xMA2)/2+28}] 628 ; label OI center metal3 ; port make 6
box values 1972 -762 2028 -738 ; label TAILA center metal3 ; port make 7
box values -833 -1100 -700 -1020 ; label VSS center metal1 ; port make 8
box values 5622 3772 5678 3828 ; label VDD center metal4 ; port make 9
select top cell
save $OUT/$CELL
puts "CML_SAVED"
quit -noprompt
