# cp_full.tcl -- CP_v1 assembly, stage 1: both interleaved mirrors in the two-band
# floorplan (PMOS y=0, NMOS y=-3600), placed + strapped, DRC. Placement math:
# device at box(FX-hw, FY-hh) => CP = local + (FX,FY). Straps use offset coords.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl
drc off
snap internal
set YN -3600

cellname create CP_v1
load CP_v1

# --- place PMOS mirror (nf=20, hw=5162 hh=630) center (0,0) ---
box values -5162 -630 -5162 -630
magic::gencell gf180mcu::pfet_03v3 MPMIR w 5 l 2 nf 20 m 1 guard 0 topc 0 botc 0
# --- place NMOS mirror (nf=4, hw=1068 hh=568) center (0,YN) ---
box values -1068 [expr {$YN-568}] -1068 [expr {$YN-568}]
magic::gencell gf180mcu::nfet_03v3 MNMIR w 5 l 2 nf 4 m 1 guard 0 topc 0 botc 0
# --- place M_PSW (pfet nf=10 L=0.3, hw=942) center (7000,0) ---
box values [expr {7000-942}] -630 [expr {7000-942}] -630
magic::gencell gf180mcu::pfet_03v3 MPSW w 5 l 0.3 nf 10 m 1 guard 0 topc 0 botc 0
# --- place M_NSW (nfet nf=2 L=0.3, hw=224) center (7000,YN) ---
box values [expr {7000-224}] [expr {$YN-568}] [expr {7000-224}] [expr {$YN-568}]
magic::gencell gf180mcu::nfet_03v3 MNSW w 5 l 0.3 nf 2 m 1 guard 0 topc 0 botc 0

flatten CP_flat
load CP_flat

# --- strap PMOS mirror (FX=0 FY=0, same as cp_pmos.tcl) ---
set pscol {-5040 -4032 -3024 -2016 -1008 0 1008 2016 3024 4032 5040}
set pvgpd {-4536 -1512 -504 2520 3528}
set ppmid {-3528 -2520 504 1512 4536}
foreach x $pscol { strap_col $x 492 720 }
rail -5080 5080 720 VDD
gate_polyrail -5400 5040 564 -5350 960 VGP
foreach x $pvgpd { strap_col $x -492 -720 }
rail -5378 3568 -720 VGP
box values -5378 -748 -5322 988 ; paint metal2 ; label VGP metal2
foreach x $ppmid { strap_col_m3 $x -492 -960 }
rail3 -3568 4576 -960 PMID

# --- strap NMOS mirror (FX=0 FY=YN); add YN to all y-coords ---
set nscol {-1008 0 1008}
proc yn {y} { return [expr {$y + $::YN}] }
foreach x $nscol { strap_col $x [yn 492] [yn 720] }
rail -1048 1048 [yn 720] VSS
gate_polyrail -1350 1008 [yn 564] -1300 [yn 960] VGN
strap_col -504 [yn -492] [yn -720]
rail -1328 -464 [yn -720] VGN
box values -1328 [yn -748] -1272 [yn 988] ; paint metal2 ; label VGN metal2
strap_col_m3 504 [yn -492] [yn -960]
rail3 464 544 [yn -960] NMID

# --- strap M_PSW (FX=7000): source->PMID (top), drain->CP_OUT (bottom), gate->UP_B ---
set psw_s {6180 6508 6836 7164 7492 7820}
set psw_d {6344 6672 7000 7328 7656}
foreach x $psw_s { strap_col $x 492 720 }
rail 6140 7860 720 PMID
foreach x $psw_d { strap_col $x -492 -720 }
rail 6304 7696 -720 CP_OUT
gate_polyrail 5950 7820 564 6000 960 UPB

# --- strap M_NSW (FX=7000 FY=YN): source->NMID, drain->CP_OUT, gate->DOWN ---
foreach x {6836 7164} { strap_col $x [yn 492] [yn 720] }
rail 6796 7204 [yn 720] NMID
strap_col 7000 [yn -492] [yn -720]
rail 6900 7100 [yn -720] CP_OUT
gate_polyrail 6550 7164 [yn 564] 6600 [yn 960] DOWN

# ===== inter-device routing (layer per net; crossings are inter-layer, not shorts) =====
# CP_OUT (M4): PSW drain rail (y-720) <-> NSW drain rail (yn-720), vertical bridge at x7000
via_m2m4 7000 -720
via_m2m4 7000 [yn -720]
m4route 7000 -720 7000 [yn -720] CP_OUT
# PMID (M4): mirror PMID M3 drain (4576,-960) <-> PSW source rail (6508,720)
via_m3m4 4576 -960
via_m2m4 6508 720
m4route 4576 720 6508 720 PMID
m4route 4576 -960 4576 720 PMID
# NMID (M4): mirror NMID M3 drain (504,yn-960) <-> NSW source rail (6836,yn720)
via_m3m4 504 [yn -960]
via_m2m4 6836 [yn 720]
m4route 504 [yn -960] 6836 [yn -960] NMID
m4route 6836 [yn -960] 6836 [yn 720] NMID

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "CPFULL_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i < 6} {incr i} { drc find ; puts "ERRBOX: [box values]" }
}
save CP_v1_layout
quit -noprompt
