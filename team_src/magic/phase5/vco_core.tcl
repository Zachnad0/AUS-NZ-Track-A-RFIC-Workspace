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
# ---------- STRAP ----------  (nfet taps=0: leg tap offset is tuned for L=2, collides
#   with a source via at L0.28 pitch -> paint shared pwell + psub taps in clean spots)
nfet_leg 10 $xL 1 0.28 $yN 0 4
nfet_leg 10 $xR 1 0.28 $yN 0 4
box values -1140 -820 4140 700 ; paint pwell
foreach tx {-1000 1500 4000} { welltap $tx -760 -580 -600 psubdiff psubdiffcont }
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
hseg metal2 -1300 [expr {$xL-840}] [expr {$yN+600}] 28   ;# haul MN1.D left
hseg metal2 -1300 [expr {$xL-440}] [expr {$yP+1300}] 28  ;# haul MP1.D left
via_m2m3 -1300 [expr {$yN+600}] ; via_m2m3 -1300 [expr {$yP+1300}]
vseg metal3 -1300 [expr {$yN+600}] [expr {$yP+1300}] 42  ;# bus
hseg metal3 -1300 2700 1650 42                           ;# haul to right gates
vseg metal3 2700 [expr {$yN+960}] [expr {$yP+1580}] 42   ;# right-gate riser
via_m2m3 2700 [expr {$yN+960}] ; via_m2m3 2700 [expr {$yP+1580}]

# ---------- OUT_n : far-right M4 bus x+4300 ----------
hseg metal2 [expr {$xR+840}] 4340 [expr {$yN+600}] 28    ;# haul MN2.D right
hseg metal2 [expr {$xR+440}] 4340 [expr {$yP+1300}] 28   ;# haul MP2.D right
m2pad 4300 [expr {$yN+600}] ; m2pad 4300 [expr {$yP+1300}]
via_m2m4 4300 [expr {$yN+600}] ; via_m2m4 4300 [expr {$yP+1300}]
vseg metal4 4300 [expr {$yN+600}] [expr {$yP+1300}] 42   ;# bus
hseg metal4 -300 4300 1950 42                            ;# haul to left gates
vseg metal4 -300 [expr {$yN+960}] [expr {$yP+1580}] 42   ;# left-gate riser
m2pad -300 [expr {$yN+960}] ; m2pad -300 [expr {$yP+1580}]
via_m2m4 -300 [expr {$yN+960}] ; via_m2m4 -300 [expr {$yP+1580}]

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
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
select top cell
save $OUT/$CELL
puts "VCORE_SAVED bbox=[box values]"
quit -noprompt
