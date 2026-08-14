# ib_ntest.tcl -- checkpoint 1+3 (nfet): one strapped multi-finger nfet (nf=5 W=4 L=2)
# = one IBIAS mirror leg. gate poly rail, sources->S rail (bottom), drains->D rail (top),
# bulk->S via pwell tap. Verify DRC 0 and netgen combine to m=5. Uses CP strap procs.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl
drc off
snap internal
cellname create ib_ntest
load ib_ntest
box values -1320 -468 -1320 -468
magic::gencell gf180mcu::nfet_03v3 M w 4 l 2 nf 5 m 1 guard 0 topc 0 botc 0
flatten ib_ntest_f
load ib_ntest_f
# strap: sources (cols -1260,-252,756) down to S rail y-600; drains (cols -756,252,1260) up to D rail y600
foreach x {-1260 -252 756} { strap_col $x -380 -600 }
foreach x {-756 252 1260} { strap_col $x 380 600 }
rail -1300 1300 -600 S
rail -1300 1300 600 D
# gate: poly bridge at the gate-arm y (400..444, 13u from diffusion like the arms),
# extended up at the far left and contacted above the array (clear of diffusion).
foreach fx {-1008 -504 0 504 1008} { box values [expr {$fx-200}] 400 [expr {$fx+200}] 600 ; paint polysilicon }
box values -1440 556 1208 600 ; paint polysilicon
box values -1440 556 -1360 720 ; paint polysilicon
box values -1423 620 -1377 666 ; paint polycontact
box values -1438 620 -1362 988 ; paint metal1
box values -1426 934 -1374 986 ; paint m2contact
box values -1470 932 1000 988 ; paint metal2 ; label G
# bulk: pwell band + tap to the S rail
box values -1600 -820 1600 700 ; paint pwell
welltap -1450 -760 -580 -600 psubdiff psubdiffcont
box values -1600 -628 -1300 -572 ; paint metal2 ; label S
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "IBN_DRC=[drc list count total]"
if {[drc list count total] > 0} { puts "WHY: [drc list why]"; for {set i 0} {$i<6} {incr i} { drc find ; puts "EB: [box values]" } }
box values -1200 -628 1200 -572 ; port make 1
box values -1200 572 1200 628 ; port make 2
box values -1300 932 1200 988 ; port make 3
select top cell
save /foss/designs/AUS-NZ-integration/team_src/magic/ib_ntest
puts "IBN_SAVED"
quit -noprompt
