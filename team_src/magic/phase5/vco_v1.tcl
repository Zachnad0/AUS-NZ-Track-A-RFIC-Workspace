# vco_v1.tcl -- VCO assembly. Inductor + core + varactor placed; FULL TANK routed.
#   Tank on two M5 buses UP the clear centre channel to the inductor ports: OUT_p @
#   x-40 -> PORT2, OUT_n @ x-800 -> PORT1 (1a geometry proof: each bus intersects ONLY
#   its own port lead, no coil turn). vco_inductor_v2 is an ABSTRACT cell (LEFview +
#   GDS_FILE=gds/vco_inductor_v2.gds, GDS_START/END, FIXED_BBOX) so magic's extractor
#   does NOT traverse the DC-continuous coil -> PORT1/PORT2 come out as DISTINCT pins
#   and OUT_p/OUT_n stay separate. The full spiral (271 shapes) is streamed into the
#   final GDS from GDS_FILE. Cross-taps kept on M3/M4 UNDER the M5 buses so the two nets
#   never share a layer at a crossing.
# PRE-LOAD masters (incl the abstract inductor) before getcell AND before gds write.
# Port coords after getcell (LL placement): shifts core (-1913,-11230), var (-5014,-23412).
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
set CELL vco_v1
proc via_m4m5 {x y} {
  box values [expr {$x-44}] [expr {$y-44}] [expr {$x+44}] [expr {$y+44}] ; paint metal4
  box values [expr {$x-44}] [expr {$y-44}] [expr {$x+44}] [expr {$y+44}] ; paint metal5
  box values [expr {$x-28}] [expr {$y-28}] [expr {$x+28}] [expr {$y+28}] ; paint via4
}
proc via_m3m5 {x y} {
  foreach l {metal3 metal4 metal5} { box values [expr {$x-44}] [expr {$y-44}] [expr {$x+44}] [expr {$y+44}] ; paint $l }
  foreach v {via3 via4} { box values [expr {$x-28}] [expr {$y-28}] [expr {$x+28}] [expr {$y+28}] ; paint $v }
}
proc h {lay x1 x2 y hw} { box values $x1 [expr {$y-$hw}] $x2 [expr {$y+$hw}] ; paint $lay }
proc v {lay x y1 y2 hw} { box values [expr {$x-$hw}] $y1 [expr {$x+$hw}] $y2 ; paint $lay }

drc off ; snap internal
load vco_inductor_v2/vco_inductor_v2   ;# warm all three masters before getcell
load vco_core
load vco_varactors
cellname create $CELL ; load $CELL
box values -22400 -4800 -22400 -4800 ; getcell vco_inductor_v2
box values -3255 -12050 -3255 -12050 ; getcell vco_core
box values -5074 -23894 -5074 -23894 ; getcell vco_varactors

# ---- net coords ----
set P1x -800 ; set P2x -40 ; set Py -480       ;# inductor ports (M5)
set cOP_x -3213 ; set cON_x 2387 ; set cOy -8730  ;# core OUT_p(M3)/OUT_n(M4)
set vOP_x -172 ; set vON_x -4852 ; set vOy -23852 ;# var OUT_p/OUT_n (M3)

# channel between core-top (-6000) and inductor-bottom (-4800): OUT_p @ -5400, OUT_n @ -5700
# ---- OUT_p : M5 bus @ x-40 ; core exits LEFT of its edge, up, right to bus ----
v metal5 $P2x $vOy 100 44
h metal3 -3500 $cOP_x $cOy 30                           ;# core OUT_p out past left edge
v metal3 -3450 $cOy -5370 30                            ;# up (outside core)
h metal3 -3490 $P2x -5400 30 ; via_m3m5 $P2x -5400     ;# right to bus @ -5400 (overlaps v)
h metal3 $vOP_x $P2x $vOy 30 ; via_m3m5 $P2x $vOy       ;# var OUT_p M3 -> bus
# ---- OUT_n : M5 bus @ x-800 ; core exits RIGHT of its edge, up, left to bus ----
v metal5 $P1x $vOy 100 44
h metal4 $cON_x 2650 $cOy 30                            ;# core OUT_n out past right edge
v metal4 2600 $cOy -5670 30                             ;# up (outside core)
h metal4 $P1x 2650 -5700 30 ; via_m4m5 $P1x -5700     ;# left to bus @ -5700 (overlaps v; clears OUT_p via)
h metal3 $vON_x $P1x $vOy 30 ; via_m3m5 $P1x $vOy       ;# var OUT_n M3 -> bus

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "V1DRC=[drc list count total]"
if {[drc list count total] > 0} {
  puts "WHY: [drc list why]"
  for {set i 0} {$i<20} {incr i} { drc find ; puts "EB: [box values]" }
}
# ---- ports (VDD/ISS/cap_bias exposed; GND/TUNE arrive with 3d resistor) ----
box values [expr {-913-28}] [expr {-8930-28}] [expr {-913+28}] [expr {-8930+28}] ; label VDD center metal2 ; port make 1
box values [expr {-1233-28}] [expr {-11830-28}] [expr {-1233+28}] [expr {-11830+28}] ; label ISS center metal2 ; port make 2
box values [expr {$P2x-44}] -5044 [expr {$P2x+44}] -4956 ; label OUT_p center metal5 ; port make 3
box values [expr {$P1x-44}] -5044 [expr {$P1x+44}] -4956 ; label OUT_n center metal5 ; port make 4
box values [expr {-4300-28}] [expr {-13056-28}] [expr {-4300+28}] [expr {-13056+28}] ; label cap_bias center metal3 ; port make 5
select top cell
save $OUT/$CELL
puts "V1_SAVED bbox=[box values]"
quit -noprompt
