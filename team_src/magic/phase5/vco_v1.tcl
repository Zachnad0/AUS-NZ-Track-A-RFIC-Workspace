# vco_v1.tcl -- VCO assembly. Inductor + core + varactor placed; FULL TANK routed.
#
# FIXED 2026-09-18. The tank was SHORTED. The two M5 buses were placed at x-40 and x-800,
# taken from the abstract .mag's PORT1/PORT2 label rects -- and those label rects were at
# 1/10 of the real coordinates. The streamed coil's two metal5 terminals are 38.000 um
# apart, not 3.800, so BOTH buses landed inside the SAME terminal pad (the east one) and
# the west terminal was left unconnected: OUT_p and OUT_n were one node and the inductor
# was a stub. The old header's "1a geometry proof" was run against the abstract, which
# carries no coil, so it could not see this. The abstract's labels are corrected in the
# same change (team_src/magic/vco_inductor_v2/vco_inductor_v2.mag).
#
# The proof now runs against the STREAM, not the abstract:
#   team_src/magic/analysis/vco_tank_proof.py
# It reads gds/vco_inductor_v2.gds and gds/vco_v1.gds and asserts that each bus intersects
# exactly ONE terminal polygon, that the two buses touch different polygons, and that
# neither bus touches the other's polygon. Run it after any change to this file.
#
# vco_inductor_v2 is an ABSTRACT cell (LEFview + GDS_FILE=gds/vco_inductor_v2.gds,
# GDS_START/END, FIXED_BBOX) so magic's extractor does NOT traverse the DC-continuous coil
# -> PORT1/PORT2 come out as DISTINCT pins and OUT_p/OUT_n stay separate. That is true of
# the .mag flow only; a GDS-only flow DOES traverse the coil and will see the two terminals
# as one net through the winding, which is correct and expected for an inductor.
# Cross-taps kept on M3/M4 UNDER the M5 buses so the two nets never share a layer at a
# crossing.
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
# ---- multi-cut via arrays. Same large-array pitch as the phase C chip work: the DRM's
# V*.2b rules fix "via space in a 4x4 or larger array" at 0.36 um. Magic models a via3/via4
# CONTACT at 0.28 um, not the DRM's 0.26 (V3.1 fires at < 56 internal units), so the cut is
# 56 and the pitch is 56 + 72 = 128 = 0.64 um, with a 0.10 um enclosure. n x n cuts give
# 4.5/n^2 ohm; 4 x 4 = 16 cuts = 0.281 ohm per transition, inside the 0.3 ohm budget.
set VP 128 ; set VC 56 ; set VE 20
set LEADHW 240   ;# 2.4 um core leads. The BUSES stay at BUSHW (2.0 um); the leads are
                 ;# sized for <= 2.5 ohm per side, and 2.4 um also makes the 4x4 array
                 ;# pad (2*(3*128+56)/2 + 2*20 = 480 = 2.4 um) exactly the lead width.
proc varray {lo hi x y n} {
  set span [expr {($n-1)*$::VP + $::VC}]
  set hf [expr {$span/2}]
  set pd [expr {$hf + $::VE}]
  for {set m $lo} {$m < $hi} {incr m} {
    foreach l [list metal$m metal[expr {$m+1}]] {
      box values [expr {$x-$pd}] [expr {$y-$pd}] [expr {$x+$pd}] [expr {$y+$pd}] ; paint $l
    }
    for {set i 0} {$i < $n} {incr i} {
      for {set j 0} {$j < $n} {incr j} {
        set cx [expr {$x - $hf + $i*$::VP}]
        set cy [expr {$y - $hf + $j*$::VP}]
        box values $cx $cy [expr {$cx+$::VC}] [expr {$cy+$::VC}] ; paint via$m
      }
    }
  }
  incr ::VCUTS [expr {($hi-$lo)*$n*$n}]
}
set VCUTS 0
proc via_m3m4 {x y} {
  foreach l {metal3 metal4} { box values [expr {$x-44}] [expr {$y-44}] [expr {$x+44}] [expr {$y+44}] ; paint $l }
  box values [expr {$x-28}] [expr {$y-28}] [expr {$x+28}] [expr {$y+28}] ; paint via3
}
proc h {lay x1 x2 y hw} { box values $x1 [expr {$y-$hw}] $x2 [expr {$y+$hw}] ; paint $lay }
proc v {lay x y1 y2 hw} { box values [expr {$x-$hw}] $y1 [expr {$x+$hw}] $y2 ; paint $lay }

drc off ; snap internal
load vco_inductor_v2/vco_inductor_v2   ;# warm all masters before getcell
load vco_core
load vco_varactors
load vco_tune_r
cellname create $CELL ; load $CELL
box values -22400 -4800 -22400 -4800 ; getcell vco_inductor_v2
box values -3255 -12310 -3255 -12310 ; getcell vco_core   ;# core grew 260 taller (GND taps); place 260 lower so ISS/VDD/OUT ports realign, top stays at y-6000
box values -5074 -23894 -5074 -23894 ; getcell vco_varactors
box values -9000 -14000 -9000 -14000 ; getcell vco_tune_r

# ---- net coords ----
# Inductor terminals, DERIVED from gds/vco_inductor_v2.gds (not from the abstract's
# labels, which were wrong by 10x). getcell places the abstract at its FIXED_BBOX LL, so
# the cell's own coordinates ARE vco_v1's here. The coil's metal5 merges into exactly two
# polygons; each meets the cell's bottom edge (y -24.000 um) in one 8.000 um pad:
#   west pad  x -44.000 .. -36.000 um -> internal -8800 .. -7200, centre -8000
#   east pad  x  -6.000 ..  +2.000 um -> internal -1200 ..   400, centre  -400
#   pad edge  y -24.000 um            -> internal -4800
# Terminal pitch is therefore 38.000 um. The old constants (-800, -40, -480) are those
# three numbers divided by ten.
set Ax -8000 ; set Bx -400 ; set Py -4800     ;# inductor terminals (M5), west and east
set BUSHW 200                                  ;# 2.0 um buses, identical widths
set BUSTOP [expr {$Py+400}]                    ;# rise 2 um into the pad; the lead runs
                                               ;# straight from y-24.0 to y-16.5 um, so the
                                               ;# bus stops well short of the first turn
set cOP_x -3213 ; set cON_x 2387 ; set cOy -8730  ;# core OUT_p(M3)/OUT_n(M4)
set vOP_x -172 ; set vON_x -4852 ; set vOy -23852 ;# var OUT_p/OUT_n (M3)

# channel between core-top (-6000) and inductor-bottom (-4800): OUT_p @ -5400, OUT_n @ -5700
# ---- OUT_p : M5 bus @ Ax (WEST terminal) ----
v metal5 $Ax $vOy $BUSTOP $BUSHW
# The core-pin lead is widened from 0.30 um to the bus width (2.0 um) and its M3->M5
# transition is a 4x4 array instead of a single cut. The riser is centred at -3590 so its
# 2.4 um body clears vco_core's west edge (-3255) by 0.475 um; only the 0.30 um stub off the
# pin itself stays narrow, because the pin is 0.20 um.
h metal3 -3590 $cOP_x $cOy 30                           ;# core OUT_p out past left edge, onto the riser
v metal3 -3590 $cOy -5300 $LEADHW                       ;# 2.4 um riser, clears the core by 0.475 um
h metal3 $Ax -3350 -5300 $LEADHW                        ;# WEST to bus A at 2.4 um
varray 3 5 $Ax -5300 4                                  ;# 16 via3 + 16 via4 onto bus A
# The varactor's OUT_p pin is on its EAST side while OUT_p's bus is now the WEST terminal,
# so this tap has to cross under the OUT_n bus. It crosses on metal4, one micron ABOVE the
# OUT_n tap's metal3 lane: the OUT_n via pad spans y -23896..-23808 and this lane spans
# -23682..-23622, a 0.63 um gap, so the two nets never share a layer at the crossing.
set vOPy [expr {$vOy+200}]
via_m3m4 $vOP_x $vOy                                    ;# varactor OUT_p pin M3 -> M4
v metal4 $vOP_x $vOy [expr {$vOPy+30}] 30               ;# jog north out of the M3 lane
h metal4 $Ax $vOP_x $vOPy 30 ; via_m4m5 $Ax $vOPy       ;# west, under the OUT_n bus, to bus A
# ---- OUT_n : M5 bus @ Bx (EAST terminal) ----
v metal5 $Bx $vOy $BUSTOP $BUSHW
# Same treatment on OUT_n. Its riser sits at 2790 so the 2.4 um body clears vco_core's east
# edge (2455) by 0.475 um. OUT_n needs ONE transition where OUT_p needs two, because
# vco_core presents OUT_n on metal4 and OUT_p on metal3 -- a property of vco_core, which is
# not touched here; the 0.281 ohm difference is in the imbalance table.
h metal4 $cON_x 2790 $cOy 30                            ;# core OUT_n out past right edge, onto the riser
v metal4 2790 $cOy -5750 $LEADHW                        ;# 2.4 um riser, clears the core by 0.475 um
h metal4 $Bx 2790 -5750 $LEADHW                         ;# west to bus B at 2.4 um
varray 4 5 $Bx -5750 4                                  ;# 16 via4 onto bus B
h metal3 $vON_x $Bx $vOy 30 ; via_m3m5 $Bx $vOy         ;# var OUT_n M3 -> bus B

# ---- tune resistor (3d): cap_bias(res,-8664,-13728) -> varactor cap_bias(-4300,-13056);
#      TUNE(-8664,-10556) and GND(-8860,-13944) become top ports ----
set rCB_x -8664 ; set rCB_y -13728 ; set vCB_x -4300 ; set vCB_y -13056
via_m1m3 $rCB_x $rCB_y
v metal3 $rCB_x $rCB_y [expr {$vCB_y+30}] 30      ;# up to cap_bias rail y
h metal3 $rCB_x [expr {$vCB_x+30}] $vCB_y 30      ;# over to varactor cap_bias M3 rail

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "V1_LEADCUTS=$VCUTS"
puts "V1DRC=[drc list count total]"
if {[drc list count total] > 0} {
  puts "WHY: [drc list why]"
  for {set i 0} {$i<20} {incr i} { drc find ; puts "EB: [box values]" }
}
# ---- ports (VDD/ISS/cap_bias exposed; GND/TUNE arrive with 3d resistor) ----
# top-level metal painted OVER each child port so the label lands on a real net
box values -953 -8970 -873 -8890 ; paint metal2 ; label VDD center metal2 ; port make 1
box values -1273 -11870 -1193 -11790 ; paint metal2 ; label ISS center metal2 ; port make 2
box values [expr {$Ax-$BUSHW}] -5044 [expr {$Ax+$BUSHW}] -4956 ; label OUT_p center metal5 ; port make 3
box values [expr {$Bx-$BUSHW}] -5044 [expr {$Bx+$BUSHW}] -4956 ; label OUT_n center metal5 ; port make 4
box values -8704 -10596 -8624 -10516 ; paint metal1 ; label TUNE center metal1 ; port make 5   ;# resistor TUNE
box values -8740 -13958 -8660 -13922 ; paint metal1 ; label GND center metal1 ; port make 6    ;# resistor GND (on guard-ring bottom strip)
select top cell
save $OUT/$CELL
puts "V1_SAVED bbox=[box values]"
quit -noprompt
