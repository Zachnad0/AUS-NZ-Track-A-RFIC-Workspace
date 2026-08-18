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
  vseg $gx [expr {676-556-38}] $GTOP 38          ;# gate col bus -> up to cap_bias rail
  vseg $wx $OBOT [expr {($NR-1)*$PY+676+38}] 38  ;# well col bus -> down to OUT rail
  via23 $gx $GTOP                                 ;# gate col -> M3 cap_bias rail
  via23 $wx $OBOT                                 ;# well col -> M3 OUT rail
}
# ---------- horizontal M3 rails ----------
hseg3 [expr {0*$PX+714-60}] [expr {($NC-1)*$PX+714+60}] $GTOP 42     ;# cap_bias (all gate cols)
hseg3 [expr {0*$PX+162-60}] [expr {2*$PX+162+60}] $OBOT 42            ;# OUT_n (cols 0-2)
hseg3 [expr {3*$PX+162-60}] [expr {5*$PX+162+60}] $OBOT 42            ;# OUT_p (cols 3-5)

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
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
