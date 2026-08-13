# cp_nmos.tcl -- interleaved NMOS mirror M_NREF+M_NSNK (nf=4). source=VSS M2 top;
# gate=VGN poly rail; VGN-drain M2 bottom; NMID-drain M3 bottom; vertical M2 unifies VGN.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl
drc off
snap internal
set nc [magic::gencell_makecell gf180mcu::nfet_03v3 w 5 l 2 nf 4 m 1 guard 0 topc 0 botc 0]
load $nc
set scol {-1008 0 1008}
set vgnd {-504}
set nmid {504}

foreach x $scol { strap_col $x 492 720 }
rail -1048 1048 720 VSS
gate_polyrail -1350 1008 564 -1300 960 VGN
foreach x $vgnd { strap_col $x -492 -720 }
rail -1328 -464 -720 VGN
box values -1328 -748 -1272 988 ; paint metal2 ; label VGN metal2
foreach x $nmid { strap_col_m3 $x -492 -960 }
rail3 464 544 -960 NMID

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "NMOS_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i < 6} {incr i} { drc find ; puts "ERRBOX: [box values]" }
}
save cp_nmos
extract all
ext2spice lvs
ext2spice -o cp_nmos.spice
quit -noprompt
