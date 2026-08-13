# strap.tcl -- parameterized nf-device strapping generator (Phase 5.1e).
# Straps a raw gencell nf device (shared-diffusion contact tabs) into a parallel
# device: source cols -> metal2 rail_S, drain cols -> rail_D, gates -> rail_G,
# via metal1 risers + m2contact. Device-local frame (no flatten shift). Adds a bulk
# tie + S/D/G/B port labels. Verify: extract -> netgen combines fingers to one W=total.

# strap_device: cell = device cell (loaded); scol/dcol/gcol = x-lists (device-local);
#   sdt = S/D top-tab y, sdb = S/D bottom-tab y, gt = gate top-tab y;
#   rS/rD/rG = rail y-centers; welllayer = nwell tie layer (nsubdiff/psubdiff); btie_x = bulk tie x
# gf180: via1 52x52, metal1 encloses via >=12 (=>76 wide), metal2 >=56 wide, encloses via >=2
set ::VHW 26 ; set ::M1HW 38 ; set ::M2HW 28
proc strap_col {x ytab yrail} {
    # metal1 riser spans from the tab to PAST the via at the rail end (enclose via >=12)
    set ext [expr {$::VHW + 14}]
    if {$yrail > $ytab} { set lo $ytab ; set hi [expr {$yrail+$ext}] } \
                   else { set lo [expr {$yrail-$ext}] ; set hi $ytab }
    box values [expr {$x-$::M1HW}] $lo [expr {$x+$::M1HW}] $hi ; paint metal1
    box values [expr {$x-$::VHW}] [expr {$yrail-$::VHW}] [expr {$x+$::VHW}] [expr {$yrail+$::VHW}] ; paint m2contact
}
proc rail {x1 x2 yc name} {
    box values $x1 [expr {$yc-$::M2HW}] $x2 [expr {$yc+$::M2HW}] ; paint metal2 ; label $name metal2
}
proc strap_device {cell scol dcol gcol sdt sdb gt rS rD rG welltie btie} {
    load $cell
    foreach x $scol { strap_col $x $sdt $rS }
    foreach x $dcol { strap_col $x $sdb $rD }
    foreach x $gcol { strap_col $x $gt  $rG }
    set ss [lsort -integer $scol]; rail [expr {[lindex $ss 0]-40}] [expr {[lindex $ss end]+40}] $rS S
    set ds [lsort -integer $dcol]; rail [expr {[lindex $ds 0]-40}] [expr {[lindex $ds end]+40}] $rD D
    set gs [lsort -integer $gcol]; rail [expr {[lindex $gs 0]-40}] [expr {[lindex $gs end]+40}] $rG G
    # bulk = shared well node (auto); guard ring ties it to VDD in the real block (stage d).
}

# ---- verify on pfet nf=10 w=5 L=2 ----
drc off
snap internal
set pc [magic::gencell_makecell gf180mcu::pfet_03v3 w 5 l 2 nf 10 m 1 guard 0]
puts "DEVCELL=$pc"
set scol {-2520 -1512 -504 504 1512 2520}
set dcol {-2016 -1008 0 1008 2016}
set gcol {-2268 -1764 -1260 -756 -252 252 756 1260 1764 2268}
strap_device $pc $scol $dcol $gcol 492 -492 556 720 -720 960 nsubdiff 2900
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "STRAP_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i < 6} {incr i} { drc find ; puts "ERRBOX: [box values]" }
}
save cp_pstrapped
# extract
extract all
ext2spice lvs
ext2spice -o cp_pstrapped.spice
puts "---BEGIN---"
set fh [open cp_pstrapped.spice r]; puts [read $fh]; close $fh
puts "---END---"
quit -noprompt
