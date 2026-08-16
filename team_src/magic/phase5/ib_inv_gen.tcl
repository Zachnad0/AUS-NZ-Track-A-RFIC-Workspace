# ib_inv_gen.tcl -- parameterized CMOS inverter proc (converter INV1/2/3). Validates
# the topology at the largest, tallest instance (INV3 = pfet W44 / nfet W16). Same
# construction as ib_inv1 but every y-constant derived from Wn/Wp so one proc covers
# all three. nfet bottom (taps=0 + explicit pwell+VSS tap strip -- welltap skips
# single-finger devices), pfet top (taps=0 + shared nwell). IN=gate tie (M2 far-left),
# OUT=drain tie (M3 x0), VDD riser on the right. Ports IN OUT VDD VSS.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT /foss/designs/AUS-NZ-integration/team_src/magic

proc hseg {lay x1 x2 y hw} { box values [expr {$x1-$hw}] [expr {$y-$hw}] [expr {$x2+$hw}] [expr {$y+$hw}] ; paint $lay }
proc vseg {lay x y1 y2 hw} { box values [expr {$x-$hw}] [expr {$y1-$hw}] [expr {$x+$hw}] [expr {$y2+$hw}] ; paint $lay }

# make_inv: build a standalone inverter cell named $cell with pfet width Wp, nfet Wn.
proc make_inv {cell Wn Wp} {
    global OUT
    set H 28
    set Gn  [expr {100*$Wn}]
    set PGp [expr {100*$Wp}]
    # place YP so the pfet's nwell bottom clears the nfet gate top by >300
    set gyN [expr {$Gn+532}]
    set YP  [expr {$gyN + $PGp + 3040}]     ;# nwell bottom (YP-(PGp+340)) = gyN+2700
    set dyN [expr {$Gn+200}]
    set syN [expr {-($Gn+200)}]
    set gyP [expr {$YP+$PGp+152}]
    set dyP [expr {$YP+$PGp-100}]
    set syP [expr {$YP-($PGp-100)}]

    drc off ; snap internal
    cellname create $cell ; load $cell
    place_nfet 1 0 M_N 0.3 0 $Wn
    place_pfet 1 0 M_P $YP 0.3 $Wp
    flatten ${cell}_f ; load ${cell}_f
    nfet_leg 1 0 1 0.3 0  0 $Wn
    pfet_leg 1 0 1 0.3 $YP 0 -700 $Wp

    # nfet pwell + VSS psubdiff tap strip below, riser at source col x=-82 to source rail
    box values -400 [expr {$syN-800}] 400 [expr {$Gn+300}] ; paint pwell
    box values -383 [expr {$syN-690}] 383 [expr {$syN-570}] ; paint psubdiff
    box values -366 [expr {$syN-677}] 366 [expr {$syN-583}] ; paint psubdiffcont
    box values -383 [expr {$syN-690}] 383 [expr {$syN-570}] ; paint metal1
    box values -110 [expr {$syN-600}] -54 [expr {$syN+20}] ; paint metal1
    box values -108 [expr {$syN-26}] -56 [expr {$syN+26}] ; paint m2contact
    # shared nwell over pfet + nwell tap strip above the gate M2 (gyP)
    box values -600 [expr {$YP-($PGp+340)}] 600 [expr {$gyP+400}] ; paint nwell
    box values -400 [expr {$gyP+200}] 400 [expr {$gyP+320}] ; paint nsubdiff
    box values -383 [expr {$gyP+213}] 383 [expr {$gyP+307}] ; paint nsubdiffcont
    box values -400 [expr {$gyP+200}] 400 [expr {$gyP+360}] ; paint metal1

    # IN gate tie (M2 far-left) ; OUT drain tie (M3 x0) ; VDD riser (right, to nwell tap)
    vseg metal2 -235 $gyN $gyP $H
    via_m2m3 0 $dyN ; via_m2m3 0 $dyP ; vseg metal3 0 $dyN $dyP $H
    box values 122 [expr {$syP-$H}] 428 [expr {$syP+$H}] ; paint metal2
    via_m2m3 400 $syP ; vseg metal3 400 $syP [expr {$gyP+260}] $H ; via_m1m3 400 [expr {$gyP+260}]

    select top cell
    drc on ; drc euclidean on ; drc check ; drc catchup
    puts "${cell}_DRC=[drc list count total]"
    if {[drc list count total] > 0} {
        puts "WHY: [drc list why]"
        for {set i 0} {$i<14} {incr i} { drc find ; puts "EB: [box values]" }
    }
    set my [expr {($dyN+$dyP)/2}]
    box values -235 $my -235 $my ; box size 56 56 ; label IN center metal2 ; port make 1
    box values 0 $my 0 $my ; box size 56 56 ; label OUT center metal3 ; port make 2
    box values 275 [expr {$syP-28}] 331 [expr {$syP+28}] ; label VDD center metal2 ; port make 3
    box values -28 [expr {$syN-28}] 28 [expr {$syN+28}] ; label VSS center metal2 ; port make 4
    select top cell
    save $OUT/$cell
    puts "${cell}_SAVED"
}

# All three converter inverters share this ONE construction path (make_inv). ib_inv1 was
# formerly a hand-built one-off (ib_inv1.tcl, now retired) -- regenerated here so the
# assembly carries a single path per cell type.
make_inv ib_inv1 4  10
make_inv ib_inv2 11 26
make_inv ib_inv3 16 44
quit -noprompt
