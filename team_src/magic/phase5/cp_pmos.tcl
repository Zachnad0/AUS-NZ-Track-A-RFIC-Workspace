# cp_pmos.tcl -- interleaved PMOS mirror M_PREF+M_PSRC (nf=20 common-centroid ABBA).
# source(11)=VDD M2 top; gate=VGP poly rail; VGP-drains(5)=M2 bottom; PMID-drains(5)=M3
# bottom; vertical M2 strap unifies VGP (drain rail <-> gate rail). DRC + netgen vs golden.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl
drc off
snap internal
set pc [magic::gencell_makecell gf180mcu::pfet_03v3 w 5 l 2 nf 20 m 1 guard 0 topc 0 botc 0]
load $pc
set scol {-5040 -4032 -3024 -2016 -1008 0 1008 2016 3024 4032 5040}
set vgpd {-4536 -1512 -504 2520 3528}
set pmid {-3528 -2520 504 1512 4536}

# source -> VDD (M2 top y720)
foreach x $scol { strap_col $x 492 720 }
rail -5080 5080 720 VDD
# gate -> VGP (poly rail py564; contact far left cx-5350; gate M2 rail y960)
gate_polyrail -5400 5040 564 -5350 960 VGP
# VGP-drains -> M2 bottom rail (y-720), extend left to meet the vertical strap
foreach x $vgpd { strap_col $x -492 -720 }
rail -5378 3568 -720 VGP
# vertical M2 strap unifying VGP: bottom drain rail (y-720) up to gate rail (y960)
box values -5378 -748 -5322 988 ; paint metal2 ; label VGP metal2
# PMID-drains -> M3 bottom rail (y-960)
foreach x $pmid { strap_col_m3 $x -492 -960 }
rail3 -3568 4576 -960 PMID

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "PMOS_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i < 6} {incr i} { drc find ; puts "ERRBOX: [box values]" }
}
save cp_pmos
extract all
ext2spice lvs
ext2spice -o cp_pmos.spice
puts "NDEV=[exec grep -c {pfet_03v3} cp_pmos.spice]"
quit -noprompt
