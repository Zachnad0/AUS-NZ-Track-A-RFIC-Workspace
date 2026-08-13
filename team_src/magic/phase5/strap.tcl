# strap.tcl -- nf-device strapping generator LIBRARY (Phase 5.1e). Procs only, no
# side effects on source. Topology: device generated with topc=0 botc=0 (no gate
# metal1), gates on a POLYSILICON rail (one contact past the array), S/D on metal2
# (source top-contacted, drain bottom-contacted). metal1(S/D)-vs-poly(gate) inter-layer
# => the congested band is empty by construction. See phase5/README.md.
#
# gf180 minimums (hoisted): via1 52, metal1 encloses via +12, metal2 >=56, riser
# extends >=12 past via (V1.3). Multi-layer split-drain adds m3contact/metal3.
set ::VHW 26   ;# via1 half-width (52 sq)
set ::VHW2 28  ;# via2 half-width (56 sq -- gf180 via2 min 56)
set ::M1HW 38  ;# metal1 riser half-width (76 => encloses via +12)
set ::M3HW 42  ;# metal3 pad half-width (84 => encloses via2 56 by 14)
set ::M2HW 28  ;# metal2 rail half-width (56)
set ::EXT 14   ;# riser overshoot past the via at the rail end

# strap_col: via1 + metal1 riser tab<->rail + m2contact (S/D or VGP-drains on metal2)
proc strap_col {x ytab yrail} {
    if {$yrail > $ytab} { set lo $ytab ; set hi [expr {$yrail+$::VHW+$::EXT}] } \
                   else { set lo [expr {$yrail-$::VHW-$::EXT}] ; set hi $ytab }
    box values [expr {$x-$::M1HW}] $lo [expr {$x+$::M1HW}] $hi ; paint metal1
    box values [expr {$x-$::VHW}] [expr {$yrail-$::VHW}] [expr {$x+$::VHW}] [expr {$yrail+$::VHW}] ; paint m2contact
}
# strap_col_m3: via1+via2 STACK AT THE TAB (so no M2 riser to cross other M2 rails);
# only metal3 rises to the rail. metal1+metal2 pads at the tab enclose the vias.
proc strap_col_m3 {x ytab yrail} {
    box values [expr {$x-$::M3HW}] [expr {$ytab-$::M3HW}] [expr {$x+$::M3HW}] [expr {$ytab+$::M3HW}] ; paint metal1
    box values [expr {$x-$::M3HW}] [expr {$ytab-$::M3HW}] [expr {$x+$::M3HW}] [expr {$ytab+$::M3HW}] ; paint metal2
    box values [expr {$x-$::VHW}]  [expr {$ytab-$::VHW}]  [expr {$x+$::VHW}]  [expr {$ytab+$::VHW}]  ; paint m2contact
    box values [expr {$x-$::VHW2}] [expr {$ytab-$::VHW2}] [expr {$x+$::VHW2}] [expr {$ytab+$::VHW2}] ; paint m3contact
    # metal3 riser (M3HW wide, encloses via2) from PAST the tab to the rail
    if {$yrail > $ytab} { set lo [expr {$ytab-$::M3HW}] ; set hi [expr {$yrail+$::VHW2+$::EXT}] } \
                   else { set lo [expr {$yrail-$::VHW2-$::EXT}] ; set hi [expr {$ytab+$::M3HW}] }
    box values [expr {$x-$::M3HW}] $lo [expr {$x+$::M3HW}] $hi ; paint metal3
}
proc rail  {x1 x2 yc name} { box values $x1 [expr {$yc-$::M2HW}] $x2 [expr {$yc+$::M2HW}] ; paint metal2 ; label $name metal2 }
proc rail3 {x1 x2 yc name} { box values $x1 [expr {$yc-$::M2HW}] $x2 [expr {$yc+$::M2HW}] ; paint metal3 ; label $name metal3 }

# gate_polyrail: poly rail connecting gate polys (py must be ABOVE pdiff top), one
# polycontact->via1->metal2 at cx (far end, over field). rail 80 tall for CO.3 overlap.
proc gate_polyrail {px1 px2 py cx rG name} {
    # ASSERT: contact cx must be LEFT of px2, else the metal2 rail (cx..px2+40) runs
    # backwards and silently makes malformed/undersized metal2. Fail loudly instead.
    if {$cx >= $px2} { error "gate_polyrail: cx ($cx) must be < px2 ($px2) -- place the gate contact LEFT of the array" }
    box values $px1 [expr {$py-42}] $px2 [expr {$py+42}] ; paint polysilicon
    box values [expr {$cx-24}] [expr {$py-24}] [expr {$cx+24}] [expr {$py+24}] ; paint polycontact
    box values [expr {$cx-$::M1HW}] [expr {$py-24}] [expr {$cx+$::M1HW}] [expr {$rG+$::VHW+$::EXT}] ; paint metal1
    box values [expr {$cx-$::VHW}] [expr {$rG-$::VHW}] [expr {$cx+$::VHW}] [expr {$rG+$::VHW}] ; paint m2contact
    box values [expr {$cx-$::VHW-$::EXT}] [expr {$rG-$::M2HW}] [expr {$px2+40}] [expr {$rG+$::M2HW}] ; paint metal2 ; label $name metal2
}
# via stack M2<->M4 at (x,y): via2 (m3contact 56) + via3 (m4contact 52), metal3/4 pads.
# Connects an existing metal2 rail up to metal4 (for inter-band M4 routing).
proc via_m2m4 {x y} {
    box values [expr {$x-$::M3HW}] [expr {$y-$::M3HW}] [expr {$x+$::M3HW}] [expr {$y+$::M3HW}] ; paint metal3
    box values [expr {$x-$::VHW2}] [expr {$y-$::VHW2}] [expr {$x+$::VHW2}] [expr {$y+$::VHW2}] ; paint m3contact
    box values [expr {$x-$::M3HW}] [expr {$y-$::M3HW}] [expr {$x+$::M3HW}] [expr {$y+$::M3HW}] ; paint metal4
    box values [expr {$x-$::VHW}]  [expr {$y-$::VHW}]  [expr {$x+$::VHW}]  [expr {$y+$::VHW}]  ; paint m4contact
}
proc via_m3m4 {x y} {
    box values [expr {$x-$::M3HW}] [expr {$y-$::M3HW}] [expr {$x+$::M3HW}] [expr {$y+$::M3HW}] ; paint metal3
    box values [expr {$x-$::M3HW}] [expr {$y-$::M3HW}] [expr {$x+$::M3HW}] [expr {$y+$::M3HW}] ; paint metal4
    box values [expr {$x-$::VHW}]  [expr {$y-$::VHW}]  [expr {$x+$::VHW}]  [expr {$y+$::VHW}]  ; paint m4contact
}
proc m4route {x1 y1 x2 y2 name} {
    box values [expr {$x1<$x2?$x1-$::M2HW:$x2-$::M2HW}] [expr {$y1<$y2?$y1-$::M2HW:$y2-$::M2HW}] \
               [expr {$x1<$x2?$x2+$::M2HW:$x1+$::M2HW}] [expr {$y1<$y2?$y2+$::M2HW:$y1+$::M2HW}] ; paint metal4 ; label $name metal4
}
# simple single-device strap (source top, drain bottom) -- for switches/inverter/dummies
proc strap_device {scol dcol sdt sdb rS rD sname dname} {
    foreach x $scol { strap_col $x $sdt $rS }
    foreach x $dcol { strap_col $x $sdb $rD }
    set ss [lsort -integer $scol]; rail [expr {[lindex $ss 0]-40}] [expr {[lindex $ss end]+40}] $rS $sname
    set ds [lsort -integer $dcol]; rail [expr {[lindex $ds 0]-40}] [expr {[lindex $ds end]+40}] $rD $dname
}
