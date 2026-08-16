# ib_inv_lib.tcl -- THE single CMOS-inverter construction path (converter INV1/2/3 and
# the standalone/chain cells all source this; no more divergent copies). inv_geom derives
# every y-constant from Wn/Wp; place_inv_dev places the raw devices; strap_inv straps +
# paints wells/taps + local IN/OUT/VDD/VSS routing at an x-offset, ports left UNLABELED,
# coords stashed in ::CIN/::COUT/::CVSS/::CVDD.
# The VDD nsubdiff tap is +/-420 (NOT +/-400): at +/-400 the tap's auto-nplus pinched to a
# sub-0.4um NP.1 tab, but ONLY in the inverter context (its interaction with the pfet/metal1
# below). 0c DISPROVED the "exact-micron-boundary" theory: an isolated +/-400 tap is clean,
# and round vs off-micron isolated taps generate an IDENTICAL nplus (same 0.01um corner grid-
# jog, 4.04um wide). +/-420 works by moving the tap edge clear of the neighbour interaction.
proc hseg {lay x1 x2 y hw} { box values [expr {$x1-$hw}] [expr {$y-$hw}] [expr {$x2+$hw}] [expr {$y+$hw}] ; paint $lay }
proc vseg {lay x y1 y2 hw} { box values [expr {$x-$hw}] [expr {$y1-$hw}] [expr {$x+$hw}] [expr {$y2+$hw}] ; paint $lay }

proc inv_geom {Wn Wp} {
    set Gn [expr {100*$Wn}] ; set PGp [expr {100*$Wp}]
    set gyN [expr {$Gn+532}] ; set YP [expr {$gyN+$PGp+3040}]
    dict create Gn $Gn PGp $PGp gyN $gyN YP $YP dyN [expr {$Gn+200}] syN [expr {-($Gn+200)}] \
        gyP [expr {$YP+$PGp+152}] dyP [expr {$YP+$PGp-100}] syP [expr {$YP-($PGp-100)}] \
        my [expr {(($Gn+200)+($YP+$PGp-100))/2}]
}
proc place_inv_dev {xoff Wn Wp pfx} {
    set g [inv_geom $Wn $Wp]
    place_nfet 1 $xoff N_$pfx 0.3 0 $Wn
    place_pfet 1 $xoff P_$pfx [dict get $g YP] 0.3 $Wp
}
proc strap_inv {xoff Wn Wp pfx} {
    global H
    set g [inv_geom $Wn $Wp]
    foreach k {Gn PGp gyN YP dyN syN gyP dyP syP my} { set $k [dict get $g $k] }
    nfet_leg 1 $xoff 1 0.3 0 0 $Wn
    pfet_leg 1 $xoff 1 0.3 $YP 0 -700 $Wp
    box values [expr {$xoff-400}] [expr {$syN-800}] [expr {$xoff+400}] [expr {$Gn+300}] ; paint pwell
    box values [expr {$xoff-383}] [expr {$syN-690}] [expr {$xoff+383}] [expr {$syN-570}] ; paint psubdiff
    box values [expr {$xoff-366}] [expr {$syN-677}] [expr {$xoff+366}] [expr {$syN-583}] ; paint psubdiffcont
    box values [expr {$xoff-383}] [expr {$syN-690}] [expr {$xoff+383}] [expr {$syN-570}] ; paint metal1
    box values [expr {$xoff-110}] [expr {$syN-600}] [expr {$xoff-54}] [expr {$syN+20}] ; paint metal1
    box values [expr {$xoff-108}] [expr {$syN-26}] [expr {$xoff-56}] [expr {$syN+26}] ; paint m2contact
    box values [expr {$xoff-600}] [expr {$YP-($PGp+340)}] [expr {$xoff+600}] [expr {$gyP+440}] ; paint nwell
    box values [expr {$xoff-420}] [expr {$gyP+140}] [expr {$xoff+420}] [expr {$gyP+380}] ; paint nsubdiff
    box values [expr {$xoff-383}] [expr {$gyP+173}] [expr {$xoff+383}] [expr {$gyP+347}] ; paint nsubdiffcont
    box values [expr {$xoff-400}] [expr {$gyP+160}] [expr {$xoff+400}] [expr {$gyP+400}] ; paint metal1
    vseg metal2 [expr {$xoff-235}] $gyN $gyP $H
    via_m2m3 $xoff $dyN ; via_m2m3 $xoff $dyP ; vseg metal3 $xoff $dyN $dyP $H
    box values [expr {$xoff+122}] [expr {$syP-$H}] [expr {$xoff+428}] [expr {$syP+$H}] ; paint metal2
    via_m2m3 [expr {$xoff+400}] $syP ; vseg metal3 [expr {$xoff+400}] $syP [expr {$gyP+260}] $H ; via_m1m3 [expr {$xoff+400}] [expr {$gyP+260}]
    set ::CIN($pfx) [list [expr {$xoff-235}] $my $gyN $gyP]
    set ::COUT($pfx) [list $xoff $my $dyN $dyP]
    set ::CVSS($pfx) [list $xoff [expr {$syN-630}]]
    set ::CVDD($pfx) [list $xoff [expr {$gyP+280}]]
}
