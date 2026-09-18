# vco_varactors.tcl -- rung 3b: differential varactor pair (XC1 cap_bias<->OUT_n m=21,
#   XC4 cap_bias<->OUT_p m=21), 42x cap_nmos_03v3_b (nmoscap_3p3 w5 l5).
# Contact map (proven): a unit placed at box(X,Y) lands its child CENTER at (X+714,Y+676).
#   gate poly contacts -> M1 at (X+714, Y+676 +-556) ; well (nsubdiff) -> M1 at (X+162, Y+676)
#   [and (X+1266,Y+676), same net]. Guard psubdiff auto-ties to substrate (no bus needed).
# Grid 6 cols x 7 rows, pitch X 1548 / Y 1500 (nwell gaps 324 / 268 >= 120 -> no NW.2a).
#   cols 0-2 wells -> OUT_n ; cols 3-5 wells -> OUT_p (mirror-symmetric about centre).
#   all 42 gates -> cap_bias.  Gate col buses (M2) -> cap_bias M3 rail on top; well col
#   buses (M2) -> OUT_n / OUT_p M3 rails on bottom.
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
set CELL vco_varactors
proc via12 {x y} {
  box values [expr {$x-38}] [expr {$y-38}] [expr {$x+38}] [expr {$y+38}] ; paint metal1
  box values [expr {$x-38}] [expr {$y-38}] [expr {$x+38}] [expr {$y+38}] ; paint metal2
  box values [expr {$x-26}] [expr {$y-26}] [expr {$x+26}] [expr {$y+26}] ; paint m2contact
}
proc via23 {x y} {
  box values [expr {$x-42}] [expr {$y-42}] [expr {$x+42}] [expr {$y+42}] ; paint metal2
  box values [expr {$x-42}] [expr {$y-42}] [expr {$x+42}] [expr {$y+42}] ; paint metal3
  box values [expr {$x-28}] [expr {$y-28}] [expr {$x+28}] [expr {$y+28}] ; paint m3contact
}
proc vseg {x y1 y2 hw} { box values [expr {$x-$hw}] $y1 [expr {$x+$hw}] $y2 ; paint metal2 }
proc hseg3 {x1 x2 y hw} { box values $x1 [expr {$y-$hw}] $x2 [expr {$y+$hw}] ; paint metal3 }
# ---- WIDENED TANK PATH, 2026-09-18 ----------------------------------------------------
# Each side of this cell measured 3.550 ohm from the OUT rail to its 21 unit terminals,
# against 0.760 ohm for the whole coil. It is three 0.38 um metal2 well columns 51 um long
# (12.1 ohm each end to end) each hung off a SINGLE via2 cut, plus one via1 per unit.
# The columns go to 2.40 um, the via2 sites become 4x4 arrays and every unit gets two more
# via1. The gate (cap_bias) columns are NOT touched and neither are the nmoscap units.
#
# Clearance: a well column at wx = c*1560+162 widened to +/-120 spans c*1560+42..282; its
# own gate column sits at c*1560+676..752, so 394 iu (1.97 um) clear, and the previous
# column's gate ends at c*1560-808, 850 iu clear. The rails grow UP only -- y -482 is the
# cell's bbox bottom and both OUT port labels live in -482..-398.
set WCHW 120   ;# well column half-width (2.40 um, was 38)
set GCHW 120   ;# gate (cap_bias) column half-width (2.40 um, was 38)
set GRTOP 10398 ;# cap_bias rail top -- held at its original edge, inside the bbox top 10412
set GRBOT 9918  ;# ... and grown DOWN to 2.40 um. metal3 is empty over the array.
set GVY  10161  ;# cap_bias via2 array centre: the +/-237 pad spans 9924..10398, inside the
                ;# widened rail and clear of the well columns' metal2, which tops out at 9840
set RTOP -2    ;# widened OUT rail top; bottom stays at OBOT-42 = -482 (the bbox edge)
set VP 126 ; set VC 56 ; set VE 20
proc varray2 {x y n} {
  set span [expr {($n-1)*$::VP + $::VC}] ; set hf [expr {$span/2}] ; set pd [expr {$hf+$::VE}]
  foreach l {metal2 metal3} { box values [expr {$x-$pd}] [expr {$y-$pd}] [expr {$x+$pd}] [expr {$y+$pd}] ; paint $l }
  for {set i 0} {$i < $n} {incr i} {
    for {set j 0} {$j < $n} {incr j} {
      set cx [expr {$x-$hf+$i*$::VP}] ; set cy [expr {$y-$hf+$j*$::VP}]
      box values $cx $cy [expr {$cx+$::VC}] [expr {$cy+$::VC}] ; paint m3contact
    }
  }
  incr ::VCUTS [expr {$n*$n}]
}
set VCUTS 0

drc off ; snap internal
set NC 6 ; set NR 7 ; set PX 1560 ; set PY 1500 ;# PX guard gap 60, PY 76 (>=56 DF.3a)
# ---------- PLACE 42 units ----------
for {set c 0} {$c < $NC} {incr c} {
  for {set r 0} {$r < $NR} {incr r} {
    set X [expr {$c*$PX}] ; set Y [expr {$r*$PY}]
    box values $X $Y $X $Y
    magic::gencell gf180mcu::nmoscap_3p3 U${c}_${r} w 5 l 5 m 1 nf 1
  }
}
flatten ${CELL}_f ; load ${CELL}_f
set GTOP [expr {($NR-1)*$PY+676+556+124}] ;# cap_bias rail y (above top gate via)
set OBOT -440                              ;# OUT rails y (below array)
# ---------- per-unit vias + column buses ----------
for {set c 0} {$c < $NC} {incr c} {
  set gx [expr {$c*$PX+714}] ; set wx [expr {$c*$PX+162}]
  for {set r 0} {$r < $NR} {incr r} {
    set cY [expr {$r*$PY+676}]
    via12 $gx [expr {$cY-556}] ; via12 $gx [expr {$cY+556}]  ;# gate
    via12 $wx $cY                                            ;# well
  }
  vseg $gx [expr {676-556-38}] $GTOP $GCHW       ;# gate col bus, 2.40 um, up to cap_bias rail
  vseg $wx -482 [expr {($NR-1)*$PY+676+126+38}] $WCHW ;# well col bus, 2.40 um, down to the rail
  varray2 $gx $GVY 4                              ;# 16 via2, gate col -> M3 cap_bias rail
  # well col -> M3 OUT rail as a 4x4 array. Centred at -245 so its 474 iu pad spans
  # -482..-8: bottom exactly on the bbox edge, top inside the widened rail.
  varray2 [expr {$wx+120}] -245 4
  # two more via1 per unit. The gencell's well-tap metal1 runs 178..1174 about each row's
  # centre, so cuts at +/-126 from the existing one sit well inside it, and the widened
  # column already provides the metal2 over them.
  for {set r 0} {$r < $NR} {incr r} {
    set cY [expr {$r*$PY+676}]
    foreach dy {-126 126} { via12 $wx [expr {$cY+$dy}] ; incr ::VCUTS }
  }
}
# ---------- horizontal M3 rails ----------
box values [expr {0*$PX+714-60}] $GRBOT [expr {($NC-1)*$PX+714+60}] $GRTOP ; paint metal3  ;# cap_bias
box values [expr {0*$PX+162-60}] -482 [expr {2*$PX+162+60}] $RTOP ; paint metal3  ;# OUT_n
box values [expr {3*$PX+162-60}] -482 [expr {5*$PX+162+60}] $RTOP ; paint metal3  ;# OUT_p

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "VAR_CUTS=$VCUTS"
puts "VARDRC=[drc list count total]"
if {[drc list count total] > 0} {
  puts "WHY: [drc list why]"
  for {set i 0} {$i<16} {incr i} { drc find ; puts "EB: [box values]" }
}
# ---------- ports ----------
box values [expr {714-42}] [expr {$GTOP-42}] [expr {714+42}] [expr {$GTOP+42}] ; label cap_bias center metal3 ; port make 1
box values [expr {162-42}] [expr {$OBOT-42}] [expr {162+42}] [expr {$OBOT+42}] ; label OUT_n center metal3 ; port make 2
box values [expr {3*$PX+162-42}] [expr {$OBOT-42}] [expr {3*$PX+162+42}] [expr {$OBOT+42}] ; label OUT_p center metal3 ; port make 3
select top cell
save $OUT/$CELL
puts "VAR_SAVED bbox=[box values]"
quit -noprompt
