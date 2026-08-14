# ib_block.tcl -- IBIAS block generator (5.2). Composable strapped-leg procs built
# on the ib_n24-validated topology (magic+KLayout DRC 0, netgen combine, per leg).
# Each leg is SELF-CONTAINED (own S/D/G rails, gate contact, substrate taps); shared
# nets (NB gate, VSS, IBIAS cascode gate, cascode nodes) are joined by explicit metal
# routing between the labeled rails -- the layer-per-net-class rule.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl

set ::PITCH 504

# S/D contacted-poly pitch by L (measured from generated devices, W=4 nfet):
# L=2 -> 504, L=1 -> 304. Vertical strap constants are W-dependent (same for both).
proc pitch_for_L {L} { return [expr {$L == 1 ? 304 : 504}] }

# place_nfet: place ONE raw nf-finger nfet (W=4) centered at x=xoff, unique name.
# Placement only -- gencell with distinct names, flatten ONCE after all devices are
# placed, THEN strap (mtest pattern). L defaults to 2 (mirror); pass 1 for cascodes.
proc place_nfet {nf xoff name {L 2}} {
    set maxc [expr {int($nf*[pitch_for_L $L]/2)}]
    box values [expr {$xoff-($maxc+60)}] -468 [expr {$xoff-($maxc+60)}] -468
    magic::gencell gf180mcu::nfet_03v3 $name w 4 l $L nf $nf m 1 guard 0 topc 0 botc 0
}

# nfet_leg: strap an already-placed+flattened nf-finger nfet centered at x=xoff.
# Paints UNLABELED rails: source(M2 y-600), drain(M2 y600), gate contact+rail(M2
# y960). The driver merges shared rails with continuous bars and labels each NET
# exactly once at its port location -- avoids the duplicate-label port-make failure.
#   gc : 1 = make the poly->M2 gate contact + M2 gate rail; 0 = bare poly gate rail.
# Returns the leg's outer half-extent (maxc+340).
proc nfet_leg {nf xoff gc {L 2}} {
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
    foreach x $src { strap_col $x -380 -600 }
    foreach x $drn { strap_col $x  380  600 }
    box values [expr {$xoff-($maxc+40)}] -628 [expr {$xoff+$maxc+40}] -572 ; paint metal2
    box values [expr {$xoff-($maxc+40)}]  572 [expr {$xoff+$maxc+40}]  628 ; paint metal2
    # gate: bridges up to a horizontal poly rail. Bridge half-width = gate-poly
    # half-width (100*L units); a wider bridge overhangs toward the S/D contacts and
    # trips PL.5a/CO.7 at the tighter L=1 pitch (304 vs 504).
    set bhw [expr {100*$L}]
    foreach fx $gfx { box values [expr {$fx-$bhw}] 400 [expr {$fx+$bhw}] 600 ; paint polysilicon }
    set lx [expr {$xoff-($maxc+180)}]
    box values $lx 556 [expr {$xoff+$maxc-52}] 600 ; paint polysilicon
    if {$gc} {
        box values $lx 556 [expr {$lx+80}]   720 ; paint polysilicon
        box values [expr {$lx+17}] 620 [expr {$lx+63}] 666 ; paint polycontact
        box values [expr {$lx+2}]  620 [expr {$lx+78}] 988 ; paint metal1
        box values [expr {$lx+14}] 934 [expr {$lx+66}] 986 ; paint m2contact
        box values [expr {$lx-30}] 932 [expr {$xoff+$maxc-260}] 988 ; paint metal2
    }
    # bulk: pwell + tap row (<=25um spacing) tied to source rail
    box values [expr {$xoff-($maxc+340)}] -820 [expr {$xoff+$maxc+340}] 700 ; paint pwell
    for {set tx [expr {$xoff-$maxc+252}]} {$tx < [expr {$xoff+$maxc}]} {set tx [expr {$tx+5040}]} {
        welltap $tx -760 -580 -600 psubdiff psubdiffcont
    }
    return [expr {$maxc+340}]
}

# via_m2m3: connect an existing metal2 feature up to metal3 at (x,y).
proc via_m2m3 {x y} {
    box values [expr {$x-$::M3HW}] [expr {$y-$::M3HW}] [expr {$x+$::M3HW}] [expr {$y+$::M3HW}] ; paint metal2
    box values [expr {$x-$::M3HW}] [expr {$y-$::M3HW}] [expr {$x+$::M3HW}] [expr {$y+$::M3HW}] ; paint metal3
    box values [expr {$x-$::VHW2}] [expr {$y-$::VHW2}] [expr {$x+$::VHW2}] [expr {$y+$::VHW2}] ; paint m3contact
}
