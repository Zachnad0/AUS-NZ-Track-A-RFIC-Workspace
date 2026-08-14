# mtest.tcl -- PROOF: m parallel unit devices strapped on all 4 terminals combine in
# netgen. 3 unit nfets (W=4 L=2 nf=1, guard=0 topc=0), drains->D, sources->S, gates->G
# (poly rail), bulk->S via pwell tap. Golden = one nfet m=3. Deferred Phase-1 check.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl
drc off
snap internal
cellname create mtest
load mtest
# place 3 units at cx=0,800,1600 (unit hw=312 hh=468; pitch 800 => 176 gap)
foreach cx {0 800 1600} {
    box values [expr {$cx-312}] -468 [expr {$cx-312}] -468
    magic::gencell gf180mcu::nfet_03v3 M$cx w 4 l 2 nf 1 m 1 guard 0 topc 0 botc 0
}
flatten mtest_f
load mtest_f
# per-unit: drain (right ndiffc cx+252) riser up + via1 to D rail; source (left cx-252)
# riser down + via1 to S rail; gate poly stub up + polycontact + via1 to G rail.
foreach cx {0 800 1600} {
    # drain riser + via1
    box values [expr {$cx+214}] 300 [expr {$cx+290}] 620 ; paint metal1
    box values [expr {$cx+226}] 544 [expr {$cx+278}] 596 ; paint m2contact
    # source riser + via1
    box values [expr {$cx-290}] -620 [expr {$cx-214}] -300 ; paint metal1
    box values [expr {$cx-278}] -596 [expr {$cx-226}] -544 ; paint m2contact
    # gate poly stub up (contact well clear of diffusion, CO.8) + polycontact + via1 to G rail
    box values [expr {$cx-40}] 400 [expr {$cx+40}] 600 ; paint polysilicon
    box values [expr {$cx-23}] 490 [expr {$cx+23}] 536 ; paint polycontact
    box values [expr {$cx-38}] 490 [expr {$cx+38}] 828 ; paint metal1
    box values [expr {$cx-26}] 774 [expr {$cx+26}] 826 ; paint m2contact
}
# rails (extended past the outermost vias)
box values -560 542 1960 598 ; paint metal2 ; label D
box values -680 -598 1960 -542 ; paint metal2 ; label S
box values -560 772 1960 828 ; paint metal2 ; label G
# bulk: pwell band + tap (well clear of unit0 source, DF.3a) tied into the S rail
box values -760 -820 1980 700 ; paint pwell
welltap -620 -760 -580 -570 psubdiff psubdiffcont
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "MTEST_DRC=[drc list count total]"
if {[drc list count total] > 0} { puts "WHY: [drc list why]"; for {set i 0} {$i<6} {incr i} { drc find ; puts "EB: [box values]" } }
# ports
box values 0 542 1852 598 ; port make 1
box values 0 -598 1852 -542 ; port make 2
box values 0 772 1852 828 ; port make 3
select top cell
save /foss/designs/AUS-NZ-integration/team_src/magic/mtest
puts "MTEST_SAVED"
quit -noprompt
