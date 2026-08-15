# ib_block.tcl -- IBIAS block generator (5.2). Composable strapped-leg procs built
# on the ib_n24-validated topology (magic+KLayout DRC 0, netgen combine, per leg).
# Each leg is SELF-CONTAINED (own S/D/G rails, gate contact, substrate taps); shared
# nets (NB gate, VSS, IBIAS cascode gate, cascode nodes) are joined by explicit metal
# routing between the labeled rails -- the layer-per-net-class rule.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl

set ::PITCH 504

# S/D contacted-poly pitch by L (measured from generated devices): L=2->504,
# L=1->304, L=0.3->164. Linear: pitch = 200*L + 104. Vertical strap constants are
# W-dependent (finger width), NOT L-dependent, so they carry across L.
proc pitch_for_L {L} { return [expr {int(round(200*$L + 104))}] }

# place_nfet: place ONE raw nf-finger nfet (W=4) centered at x=xoff, unique name.
# Placement only -- gencell with distinct names, flatten ONCE after all devices are
# placed, THEN strap (mtest pattern). L defaults to 2 (mirror); pass 1 for cascodes.
proc place_nfet {nf xoff name {L 2} {yoff 0}} {
    set maxc [expr {int($nf*[pitch_for_L $L]/2)}]
    box values [expr {$xoff-($maxc+60)}] [expr {$yoff-468}] [expr {$xoff-($maxc+60)}] [expr {$yoff-468}]
    magic::gencell gf180mcu::nfet_03v3 $name w 4 l $L nf $nf m 1 guard 0 topc 0 botc 0
}

# nfet_leg: strap an already-placed+flattened nf-finger nfet centered at x=xoff.
# Paints UNLABELED rails: source(M2 y-600), drain(M2 y600), gate contact+rail(M2
# y960). The driver merges shared rails with continuous bars and labels each NET
# exactly once at its port location -- avoids the duplicate-label port-make failure.
#   gc : 1 = make the poly->M2 gate contact + M2 gate rail; 0 = bare poly gate rail.
# Returns the leg's outer half-extent (maxc+340).
#   yoff : row y-offset (device centered at y=yoff). taps : 1 = paint pwell + a
#   source-tied psubdiff tap row (mirror rows); 0 = skip both -- for cascode rows
#   whose bulk is the SHARED pwell (VSS-tied by the mirror taps) and whose source is
#   NOT VSS. The driver then paints the shared pwell spanning all rows.
proc nfet_leg {nf xoff gc {L 2} {yoff 0} {taps 1}} {
    set P [pitch_for_L $L]
    set maxc [expr {int($nf*$P/2)}]
    set src {} ; set drn {}
    for {set i 0} {$i <= $nf} {incr i} {
        set x [expr {round(($i-$nf/2.0)*$P)+$xoff}]
        if {$i % 2 == 0} { lappend src $x } else { lappend drn $x }
    }
    set gfx {}
    for {set i 0} {$i < $nf} {incr i} { lappend gfx [expr {round(($i-($nf-1)/2.0)*$P)+$xoff}] }
    # S/D straps (rails unlabeled)
    foreach x $src { strap_col $x [expr {$yoff-380}] [expr {$yoff-600}] }
    foreach x $drn { strap_col $x [expr {$yoff+380}] [expr {$yoff+600}] }
    box values [expr {$xoff-($maxc+40)}] [expr {$yoff-628}] [expr {$xoff+$maxc+40}] [expr {$yoff-572}] ; paint metal2
    box values [expr {$xoff-($maxc+40)}] [expr {$yoff+572}] [expr {$xoff+$maxc+40}] [expr {$yoff+628}] ; paint metal2
    # gate: bridges up to a horizontal poly rail. Bridge half-width = gate-poly
    # half-width (100*L units); a wider bridge overhangs toward the S/D contacts and
    # trips PL.5a/CO.7 at the tighter L=1 pitch (304 vs 504).
    set bhw [expr {100*$L}]
    foreach fx $gfx { box values [expr {$fx-$bhw}] [expr {$yoff+400}] [expr {$fx+$bhw}] [expr {$yoff+600}] ; paint polysilicon }
    set lx [expr {$xoff-($maxc+180)}]
    box values $lx [expr {$yoff+556}] [expr {$xoff+$maxc-52}] [expr {$yoff+600}] ; paint polysilicon
    if {$gc} {
        box values $lx [expr {$yoff+556}] [expr {$lx+80}]   [expr {$yoff+720}] ; paint polysilicon
        box values [expr {$lx+17}] [expr {$yoff+620}] [expr {$lx+63}] [expr {$yoff+666}] ; paint polycontact
        box values [expr {$lx+2}]  [expr {$yoff+620}] [expr {$lx+78}] [expr {$yoff+988}] ; paint metal1
        box values [expr {$lx+14}] [expr {$yoff+934}] [expr {$lx+66}] [expr {$yoff+986}] ; paint m2contact
        box values [expr {$lx-30}] [expr {$yoff+932}] [expr {$xoff+$maxc-260}] [expr {$yoff+988}] ; paint metal2
    }
    if {$taps} {
        # bulk: pwell + tap row (<=25um spacing) tied to source rail
        box values [expr {$xoff-($maxc+340)}] [expr {$yoff-820}] [expr {$xoff+$maxc+340}] [expr {$yoff+700}] ; paint pwell
        for {set tx [expr {$xoff-$maxc+252}]} {$tx < [expr {$xoff+$maxc}]} {set tx [expr {$tx+5040}]} {
            welltap $tx [expr {$yoff-760}] [expr {$yoff-580}] [expr {$yoff-600}] psubdiff psubdiffcont
        }
    }
    return [expr {$maxc+340}]
}

# ---- PMOS side (pfet_03v3 W=16 L=2). Tall device (nwell 3460 tall, S/D contact
# strip y+/-1587), nwell taps to VDD. Same x-geometry as nfet (pitch 504). ----
# pfet vertical constants (device centered at yoff), measured from a flattened device:
set ::PFHH   1730    ;# half-height (nwell +/-1730)
set ::PFSTR  1587    ;# S/D metal1 strip half-height
set ::PFRAIL 1500    ;# S(bottom)/D(top) rail |y| from center
set ::PFPTOP 1600    ;# pdiff top/bottom |y|
set ::PFGRL  1646    ;# gate poly rail center |y| (above pdiff top, overlaps finger tops)
set ::PFGM2  1780    ;# gate M2 (PB) rail center |y|

proc place_pfet {nf xoff name {yoff 0} {L 2}} {
    set maxc [expr {int($nf*[pitch_for_L $L]/2)}]
    box values [expr {$xoff-($maxc+122)}] [expr {$yoff-1730}] [expr {$xoff-($maxc+122)}] [expr {$yoff-1730}]
    magic::gencell gf180mcu::pfet_03v3 $name w 16 l $L nf $nf m 1 guard 0 topc 0 botc 0
}

# pfet_leg: strap a placed+flattened pfet nf-leg centered at (xoff,yoff). Sources ->
# VDD rail (bottom, yoff-1500), drains -> drain rail (top, yoff+1500), gate poly rail
# (yoff+1646) -> M2 (yoff+1780) at far left. nwell taps -> VDD. Rails UNLABELED.
# tapy : y-offset (from yoff) of the rail the nwell taps land on. Default -1500 =
# the source rail (mirror rows, where source=VDD). Cascode rows pass a dedicated
# VDD-rail offset (e.g. -1700) because their source rail is NOT VDD; the driver then
# paints/labels a VDD rail at yoff+tapy and routes it to the main VDD.
proc pfet_leg {nf xoff gc {L 2} {yoff 0} {taps 1} {tapy -1500}} {
    set P [pitch_for_L $L] ; set maxc [expr {int($nf*$P/2)}]
    set src {} ; set drn {}
    for {set i 0} {$i <= $nf} {incr i} {
        set x [expr {round(($i-$nf/2.0)*$P)+$xoff}]
        if {$i % 2 == 0} { lappend src $x } else { lappend drn $x }
    }
    set gfx {}
    for {set i 0} {$i < $nf} {incr i} { lappend gfx [expr {round(($i-($nf-1)/2.0)*$P)+$xoff}] }
    foreach x $src { strap_col $x [expr {$yoff-1400}] [expr {$yoff-1500}] }
    foreach x $drn { strap_col $x [expr {$yoff+1400}] [expr {$yoff+1500}] }
    box values [expr {$xoff-($maxc+40)}] [expr {$yoff-1528}] [expr {$xoff+$maxc+40}] [expr {$yoff-1472}] ; paint metal2
    box values [expr {$xoff-($maxc+40)}] [expr {$yoff+1472}] [expr {$xoff+$maxc+40}] [expr {$yoff+1528}] ; paint metal2
    # gate poly rail overlaps the finger tops (1600-1644); no bridges needed
    set lx [expr {$xoff-($maxc+180)}]
    box values $lx [expr {$yoff+1624}] [expr {$xoff+$maxc-52}] [expr {$yoff+1668}] ; paint polysilicon
    if {$gc} {
        box values $lx [expr {$yoff+1624}] [expr {$lx+80}] [expr {$yoff+1808}] ; paint polysilicon
        box values [expr {$lx+17}] [expr {$yoff+1712}] [expr {$lx+63}] [expr {$yoff+1758}] ; paint polycontact
        box values [expr {$lx+2}]  [expr {$yoff+1712}] [expr {$lx+78}] [expr {$yoff+1808}] ; paint metal1
        box values [expr {$lx+14}] [expr {$yoff+1754}] [expr {$lx+66}] [expr {$yoff+1806}] ; paint m2contact
        box values [expr {$lx-30}] [expr {$yoff+1752}] [expr {$xoff+$maxc-260}] [expr {$yoff+1808}] ; paint metal2
    }
    if {$taps} {
        # nwell taps (n+ -> VDD) well BELOW the gate-poly bottom extension (which reaches
        # yoff-1644): tap top must clear it by NP.4b=64 -> tap top <= yoff-1708. riser up
        # to the VDD source rail.
        box values [expr {$xoff-($maxc+340)}] [expr {$yoff-1940}] [expr {$xoff+$maxc+340}] [expr {$yoff+1830}] ; paint nwell
        # taps at TRUE column midpoints (P/2 offset, P-multiple spacing). The pfet tap
        # riser sits at the tall pdiffc's y, so an off-midpoint tap (e.g. the L=2 +252 at
        # L=1 pitch 304) abuts the neighbouring S/D contact and shorts VDD to it.
        for {set tx [expr {$xoff-$maxc+$P/2}]} {$tx < [expr {$xoff+$maxc}]} {set tx [expr {$tx+10*$P}]} {
            welltap $tx [expr {$yoff-1900}] [expr {$yoff-1720}] [expr {$yoff+$tapy}] nsubdiff nsubdiffcont
        }
    }
    return [expr {$maxc+340}]
}

# via_m2m3: connect an existing metal2 feature up to metal3 at (x,y).
proc via_m2m3 {x y} {
    box values [expr {$x-$::M3HW}] [expr {$y-$::M3HW}] [expr {$x+$::M3HW}] [expr {$y+$::M3HW}] ; paint metal2
    box values [expr {$x-$::M3HW}] [expr {$y-$::M3HW}] [expr {$x+$::M3HW}] [expr {$y+$::M3HW}] ; paint metal3
    box values [expr {$x-$::VHW2}] [expr {$y-$::VHW2}] [expr {$x+$::VHW2}] [expr {$y+$::VHW2}] ; paint m3contact
}
