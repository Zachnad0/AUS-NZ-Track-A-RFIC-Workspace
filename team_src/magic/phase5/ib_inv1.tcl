# ib_inv1.tcl -- ONE CMOS inverter (converter INV1: pfet W10 / nfet W4, L=0.3), the
# reusable topology for INV2 (26/11) and INV3 (44/16). nfet bottom (taps=1, VSS), pfet
# top (taps=0 + shared nwell, VDD). Gate tie (IN) = vertical M2 at far-left joining the
# two gate M2 rails; drain tie (OUT) = vertical M3 at x0 joining the two drain rails
# (M3 so it crosses the gate M2 inter-layer). VDD riser on the RIGHT (clear of the IN
# tie on the left). Ports IN OUT VDD VSS.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_inv1
set YP 3000
drc off ; snap internal
cellname create $CELL ; load $CELL

place_nfet 1 0 MIN1 0.3 0 4
place_pfet 1 0 MIP1 $YP 0.3 10
flatten ${CELL}_f ; load ${CELL}_f
nfet_leg 1 0 1 0.3 0 0 4
pfet_leg 1 0 1 0.3 $YP 0 -700 10

# nfet pwell + VSS psubdiff tap strip below (taps=0: welltap's loop skips single-finger
# devices, so tie the pwell explicitly -- diff-pair/CML pattern). Riser at the source
# column x=-82 up to the M2 source rail (y-600) via via1.
box values -400 -1400 400 700 ; paint pwell
box values -383 -1290 383 -1170 ; paint psubdiff
box values -366 -1277 366 -1183 ; paint psubdiffcont
box values -383 -1290 383 -1170 ; paint metal1
box values -110 -1200 -54 -580 ; paint metal1
box values -108 -626 -56 -574 ; paint m2contact
# shared nwell over the pfet (taps=0) + nwell tap strip ABOVE the gate M2 (YP+1152)
box values -600 [expr {$YP-1340}] 600 [expr {$YP+1540}] ; paint nwell
box values -400 [expr {$YP+1360}] 400 [expr {$YP+1480}] ; paint nsubdiff
box values -383 [expr {$YP+1373}] 383 [expr {$YP+1467}] ; paint nsubdiffcont
box values -400 [expr {$YP+1360}] 400 [expr {$YP+1500}] ; paint metal1

proc hseg {lay x1 x2 y hw} { box values [expr {$x1-$hw}] [expr {$y-$hw}] [expr {$x2+$hw}] [expr {$y+$hw}] ; paint $lay }
proc vseg {lay x y1 y2 hw} { box values [expr {$x-$hw}] [expr {$y1-$hw}] [expr {$x+$hw}] [expr {$y2+$hw}] ; paint $lay }
set H 28

# gate y: nfet gate M2 rail center = G+532 = 932 ; pfet = PG+152 = 1152 above YP -> 4152
set gyN 932 ; set gyP [expr {$YP+1152}]
# drain y: nfet +600 ; pfet YP+900
set dyN 600 ; set dyP [expr {$YP+900}]
# source y: nfet -600 (VSS) ; pfet YP-900 (VDD)
set syP [expr {$YP-900}]

# --- IN (gate tie, M2 vertical at far-left x=-235, joining both gate M2 rails) ---
vseg metal2 -235 $gyN $gyP $H
# --- OUT (drain tie, M3 vertical at x0, over the gate M2 inter-layer) ---
via_m2m3 0 $dyN ; via_m2m3 0 $dyP
vseg metal3 0 $dyN $dyP $H
# --- VDD: extend pfet source rail RIGHT to x+400, M3 riser up to the nwell tap strip ---
box values 122 [expr {$syP-$H}] 428 [expr {$syP+$H}] ; paint metal2
via_m2m3 400 $syP ; vseg metal3 400 $syP [expr {$YP+1420}] $H ; via_m1m3 400 [expr {$YP+1420}]

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "INV1_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<14} {incr i} { drc find ; puts "EB: [box values]" }
}
box values -235 2400 -235 2400 ; box size 56 56 ; label IN center metal2 ; port make 1
box values 0 1900 0 1900 ; box size 56 56 ; label OUT center metal3 ; port make 2
box values 275 [expr {$syP-28}] 331 [expr {$syP+28}] ; label VDD center metal2 ; port make 3
box values -28 -628 28 -572 ; label VSS center metal2 ; port make 4
select top cell
save $OUT/$CELL
puts "INV1_SAVED"
quit -noprompt
