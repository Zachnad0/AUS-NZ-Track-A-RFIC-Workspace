# strap.tcl -- nf-device strapping generator (Phase 5.1e), poly-gate topology.
# Generate the device with topc=0 botc=0 (NO gate metal1 contacts) so the gate/S-D
# metal1 congestion is empty by construction; strap gates on a POLYSILICON rail
# (one contact at the far end), S/D on metal2 (source top-contacted, drain bottom).
# Reuse across blocks; call with per-device column lists + rail y's.
#
# gf180 minimums (hoisted): via1 52, metal1 encloses via +12, metal2 >=56, riser
# extends >=12 past via (V1.3).
set ::VHW 26   ;# via1 half-width  (52 sq)
set ::M1HW 38  ;# metal1 riser half-width (76 => encloses via +12)
set ::M2HW 28  ;# metal2 rail half-width (56)
set ::EXT 14   ;# riser overshoot past the via at the rail end

proc strap_col {x ytab yrail} {
    set ext $::EXT
    if {$yrail > $ytab} { set lo $ytab ; set hi [expr {$yrail+$::VHW+$ext}] } \
                   else { set lo [expr {$yrail-$::VHW-$ext}] ; set hi $ytab }
    box values [expr {$x-$::M1HW}] $lo [expr {$x+$::M1HW}] $hi ; paint metal1
    box values [expr {$x-$::VHW}] [expr {$yrail-$::VHW}] [expr {$x+$::VHW}] [expr {$yrail+$::VHW}] ; paint m2contact
}
proc rail {x1 x2 yc name} {
    box values $x1 [expr {$yc-$::M2HW}] $x2 [expr {$yc+$::M2HW}] ; paint metal2 ; label $name metal2
}
# poly gate rail: connect gate polys, one polycontact->via1->metal2 at cx (far end, over field).
# py must be ABOVE pdiff top (else poly-over-diff = spurious FET). Rail 80 tall for CO.3 overlap.
proc gate_polyrail {px1 px2 py cx rG} {
    box values $px1 [expr {$py-42}] $px2 [expr {$py+42}] ; paint polysilicon
    box values [expr {$cx-24}] [expr {$py-24}] [expr {$cx+24}] [expr {$py+24}] ; paint polycontact
    box values [expr {$cx-$::M1HW}] [expr {$py-24}] [expr {$cx+$::M1HW}] [expr {$rG+$::VHW+$::EXT}] ; paint metal1
    box values [expr {$cx-$::VHW}] [expr {$rG-$::VHW}] [expr {$cx+$::VHW}] [expr {$rG+$::VHW}] ; paint m2contact
    box values [expr {$cx-$::VHW-$::EXT}] [expr {$rG-$::M2HW}] [expr {$px2+40}] [expr {$rG+$::M2HW}] ; paint metal2 ; label G metal2
}

proc strap_device {cell scol dcol gcol sdt sdb rS rD} {
    load $cell
    foreach x $scol { strap_col $x $sdt $rS }
    foreach x $dcol { strap_col $x $sdb $rD }
    set ss [lsort -integer $scol]; rail [expr {[lindex $ss 0]-40}] [expr {[lindex $ss end]+40}] $rS S
    set ds [lsort -integer $dcol]; rail [expr {[lindex $ds 0]-40}] [expr {[lindex $ds end]+40}] $rD D
}

# ---- verify on pfet nf=10 w=5 L=2 (topc=0 botc=0) ----
drc off
snap internal
set pc [magic::gencell_makecell gf180mcu::pfet_03v3 w 5 l 2 nf 10 m 1 guard 0 topc 0 botc 0]
puts "DEVCELL=$pc"
set scol {-2520 -1512 -504 504 1512 2520}
set dcol {-2016 -1008 0 1008 2016}
strap_device $pc $scol $dcol {} 492 -492 720 -720
gate_polyrail -2900 2468 564 -2800 960
# bulk = shared well node for this single-device verify; guard ring ties it to VDD in the block.
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "STRAP_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i < 6} {incr i} { drc find ; puts "ERRBOX: [box values]" }
}
save cp_pstrapped
extract all
ext2spice lvs
ext2spice -o cp_pstrapped.spice
puts "---BEGIN---"
set fh [open cp_pstrapped.spice r]; puts [read $fh]; close $fh
puts "---END---"
quit -noprompt
