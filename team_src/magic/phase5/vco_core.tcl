# vco_core.tcl -- VCO 4-FET complementary cross-coupled core (rung 3a).
# Devices (folds netgen-combine to golden nf=1):
#   nfet W40 L0.28 = nf10 w4 (G=400): S(ISS) y-600, D y+600, gate M2 y+960; bulk->ISS
#   pfet W70 L0.28 = nf5  w14 (PG=1400): VDD yP-1300, D yP+1300, gate M2 yP+1580; bulk->VDD
#     tap via at yP-1500 needs M2 riser up to VDD rail (tapy default was tuned for W16).
# Golden terminals (from vco_v1.sch): XM1 OUT_p OUT_n ISS ISS ; XM4 OUT_n OUT_p ISS ISS ;
#   XM2 OUT_p OUT_n VDD VDD ; XM3 OUT_n OUT_p VDD VDD.  Cross-couple:
#   OUT_p = MN1.D + MP1.D + MN2.G + MP2.G ; OUT_n = MN2.D + MP2.D + MN1.G + MP1.G.
# Routing: OUT_p on far-left M3 bus (x-1300) -> right gates; OUT_n on far-right M4 bus
#   (x+4300) -> left gates. Hauls at y1650(M3)/y1950(M4) in the clear band 988..2272.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
set CELL vco_core
proc hseg {lay x1 x2 y hw} { box values [expr {$x1-$hw}] [expr {$y-$hw}] [expr {$x2+$hw}] [expr {$y+$hw}] ; paint $lay }
# ---- WIDENED TANK BUSES + VIA ARRAYS, 2026-09-18 -------------------------------------
# The tank branches inside this cell measured 4.742 (OUT_p) / 6.530 ohm (OUT_n) from the
# port to the drain terminals, against 0.760 ohm for the whole coil. The loss is single via
# cuts first (4.5 ohm each) and 0.42 um bus metal second. Both are addressed here.
#
# Every tank segment below is an EXPLICIT box rather than hseg/vseg, because those two procs
# extend the run by the half-width at its ends -- harmless at 0.42 um, but at 2.40 um it
# pushes past the cell boundary. Three edges are load-bearing and are held exactly:
#   metal3 x -1342 (bbox left) ; metal4 x 4342 (0.13 um inside bbox right 4368) ;
#   and every riser top stays at 5222, inside bbox top 5230.
# Growth is therefore one-directional and the port labels (-1300, 2480) and (4300, 2480)
# stay inside their widened buses, so no port moves.
#
# The two hauls grow in OPPOSITE directions -- metal3 DOWN, metal4 UP. Grown the same way
# they would overlap ~13.9 um2 of metal3-on-metal4, which is a direct OUT_p-to-OUT_n
# capacitance straight across the tank.
set VP 126 ; set VC 56 ; set VE 20   ;# 4x4 array: cut 56, space 70 (V*.2b wants 0.36 um)
proc varray {kind x y n} {
  set span [expr {($n-1)*$::VP + $::VC}] ; set hf [expr {$span/2}] ; set pd [expr {$hf+$::VE}]
  foreach l [dict get {via2 {metal2 metal3} via3 {metal3 metal4}} $kind] {
    box values [expr {$x-$pd}] [expr {$y-$pd}] [expr {$x+$pd}] [expr {$y+$pd}] ; paint $l
  }
  set ct [dict get {via2 m3contact via3 via3} $kind]
  for {set i 0} {$i < $n} {incr i} {
    for {set j 0} {$j < $n} {incr j} {
      set cx [expr {$x-$hf+$i*$::VP}] ; set cy [expr {$y-$hf+$j*$::VP}]
      box values $cx $cy [expr {$cx+$::VC}] [expr {$cy+$::VC}] ; paint $ct
    }
  }
  incr ::VCUTS [expr {$n*$n}]
}
set VCUTS 0
proc bx {lay x1 y1 x2 y2} { box values $x1 $y1 $x2 $y2 ; paint $lay }
# Four via1 per drain finger instead of one. strap_col drops a SINGLE cut at the drain rail,
# which is a 4.5 ohm series element on every finger -- with only 5 (nfet) or 3 (pfet) fingers
# per side that is a 0.9 / 1.5 ohm floor on the branch, and it is what is left after the buses
# are widened. The finger's own metal1 runs far past the rail in both device families
# (nfet -398..640, pfet 2202..4998 internal units, read off the built gds/vco_core.gds), so
# three more cuts fit at the 126 iu pitch. They need metal2 over them, which is what the
# drain bands below add; the bands sit entirely between the source rail (-628..-572) and the
# gate rail (932..988), and metal2 crossing a source finger's metal1 without a cut is not a
# short. Devices themselves are untouched.
proc stitch {xs y0} {
  foreach fx $xs {
    for {set k 1} {$k < 2} {incr k} {
      set cy [expr {$y0 - $k*$::VP}]
      box values [expr {$fx-$::VHW}] [expr {$cy-$::VHW}] [expr {$fx+$::VHW}] [expr {$cy+$::VHW}]
      paint m2contact
      incr ::VCUTS
    }
  }
}
proc vseg {lay x y1 y2 hw} { box values [expr {$x-$hw}] [expr {$y1-$hw}] [expr {$x+$hw}] [expr {$y2+$hw}] ; paint $lay }

drc off ; snap internal
cellname create $CELL ; load $CELL
set xL 0 ; set xR 3000 ; set yN 0 ; set yP 3600
# ---------- PLACE ----------
place_nfet 10 $xL MN1 0.28 $yN 4
place_nfet 10 $xR MN2 0.28 $yN 4
place_pfet 5  $xL MP1 $yP 0.28 14
place_pfet 5  $xR MP2 $yP 0.28 14
flatten ${CELL}_f ; load ${CELL}_f
# ---------- STRAP ----------  nfets get taps=0 (NO bulk->source tie). We paint the pwell
#   and psub taps ourselves, tied to a SEPARATE GND rail (y-760), so nfet bulk = GND while
#   the source rail stays its own ISS net. This gives a REAL tail node (ISS != GND) -- the
#   B=ISS + no-isolation short is gone. (gf180 nfet_03v3 has no dnwell isolation, so the
#   pwell IS the global psub = GND; the source rail is a distinct M2 net.)
nfet_leg 10 $xL 1 0.28 $yN 0 4
nfet_leg 10 $xR 1 0.28 $yN 0 4
box values -1140 -1080 4140 700 ; paint pwell
foreach tx {-1000 1500 4000} { welltap $tx -1060 -880 -900 psubdiff psubdiffcont }  ;# default offsets (clo=raily-160, chi=raily+20): 180-tall diff, M1/contact enclosure OK
hseg metal2 -1040 4040 -900 28    ;# GND rail (M2) at -900, distinct from ISS @ -600
pfet_leg 5  $xL 1 0.28 $yP 1 -1500 14
pfet_leg 5  $xR 1 0.28 $yP 1 -1500 14
# pfet tap risers: cover the tap via (fix V1.4) + connect nwell tap -> VDD rail (yP-1300)
foreach xo [list $xL $xR] { vseg metal2 [expr {$xo-320}] [expr {$yP-1530}] [expr {$yP-1290}] 32 }
# M2 pads under every via_m2m4 site (that proc paints no M2 -> V2.3 without a pad)
proc m2pad {x y} { box values [expr {$x-42}] [expr {$y-42}] [expr {$x+42}] [expr {$y+42}] ; paint metal2 }

# ---------- ISS rail (nfet sources y-600) + VDD rail (pfet sources yP-1300) ----------
hseg metal2 [expr {$xL-1050}] [expr {$xR+1050}] [expr {$yN-600}] 28
hseg metal2 [expr {$xL-440}] [expr {$xR+440}] [expr {$yP-1300}] 28

# ---------- OUT_p : far-left M3 bus x-1300 ----------
bx metal2 -1328 380 -812 628                             ;# haul MN1.D left, grown DOWN
bx metal2 -1328 4448 -412 4928                           ;# haul MP1.D left, grown DOWN
bx metal2 -678 380 678 628                               ;# drain band over MN1's fingers
bx metal2 -278 4450 438 4928                             ;# drain band over MP1's fingers
stitch {-640 -320 0 320 640} [expr {$yN+600}]            ;# +3 via1 per nfet drain finger
varray via2 -1102 [expr {$yN+600}] 4                     ;# 16 via2, nfet drain -> bus
varray via2 -1102 [expr {$yP+1300}] 4                    ;# 16 via2, pfet drain -> bus
bx metal3 -1342 558 -862 4942                            ;# bus, grown EAST off the bbox edge
bx metal3 -1342 1212 2742 1692                           ;# haul to right gates, grown DOWN
bx metal3 2658 918 3138 5222                             ;# right-gate riser, grown EAST:
                                                         ;# grown WEST it lands on
                                                         ;# route_chip's vco.VDD metal3
                                                         ;# column at core x 404.75-405.25
via_m2m3 2700 [expr {$yN+960}] ; via_m2m3 2700 [expr {$yP+1580}]  ;# gate cuts stay single:
                                                         ;# a 4x4 pad at y5180 would overrun
                                                         ;# the bbox top, and no tank current
                                                         ;# flows into a gate

# ---------- OUT_n : far-right M4 bus x+4300 ----------
bx metal2 3812 380 4368 628                              ;# haul MN2.D right, grown DOWN
bx metal2 3412 4448 4368 4928                            ;# haul MP2.D right, grown DOWN
# OUT_n needs via2 AND via3 at each transition -- vco_core presents it on metal4. Both are
# 4x4; the metal3 landing pad between them comes free with the arrays' own pads.
bx metal2 2322 380 3678 628                              ;# drain band over MN2's fingers
bx metal2 2722 4450 3438 4928                            ;# drain band over MP2's fingers
stitch {2360 2680 3000 3320 3640} [expr {$yN+600}]
varray via2 4102 [expr {$yN+600}] 4 ; varray via3 4102 [expr {$yN+600}] 4
varray via2 4102 [expr {$yP+1300}] 4 ; varray via3 4102 [expr {$yP+1300}] 4
bx metal4 3862 558 4342 4942                             ;# bus, grown WEST
bx metal4 -342 1908 4342 2388                            ;# haul to left gates, grown UP
bx metal4 -342 918 138 5222                              ;# left-gate riser, grown EAST
m2pad -300 [expr {$yN+960}] ; m2pad -300 [expr {$yP+1580}]
via_m2m4 -300 [expr {$yN+960}] ; via_m2m4 -300 [expr {$yP+1580}]

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "VCORE_CUTS=$VCUTS"
puts "VCORE_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<20} {incr i} { drc find ; puts "EB: [box values]" }
}
# ---------- ports ----------
box values 680 [expr {$yN-628}] 720 [expr {$yN-572}] ; label ISS center metal2 ; port make 1
box values 980 [expr {$yP-1328}] 1020 [expr {$yP-1272}] ; label VDD center metal2 ; port make 2
box values -1320 2480 -1280 2520 ; label OUT_p center metal3 ; port make 3
box values 4280 2480 4320 2520 ; label OUT_n center metal4 ; port make 4
box values -520 -928 -480 -872 ; label GND center metal2 ; port make 5    ;# GND rail (nfet bulk)
select top cell
save $OUT/$CELL
puts "VCORE_SAVED bbox=[box values]"
quit -noprompt
