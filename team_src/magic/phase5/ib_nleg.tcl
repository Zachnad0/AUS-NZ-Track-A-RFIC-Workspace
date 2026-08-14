# ib_nleg.tcl -- parameterized strapped nfet mirror leg generator (5.2).
# Generalizes ib_ntest (nf=5) to arbitrary nf. One multi-finger nfet W=4 L=2,
# gate on a poly rail, sources->S rail (bottom), drains->D rail (top), bulk->S
# via a ROW of pwell taps (DF.14_LV: every nfet within 20um of a tap -> a wide
# device needs several taps, KLayout-only rule). Netgen combines to m=nf.
# Usage: magic ... ib_nleg.tcl  with  $env(NF) set (default 24), $env(CELL).
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/strap.tcl

set NF   [expr {[info exists env(NF)]   ? $env(NF)   : 24}]
set CELL [expr {[info exists env(CELL)] ? $env(CELL) : "ib_nleg"}]
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic

# ---- geometry from nf (device centered on x=0), 200 units/um, W=4 L=2 ----
set P     504                      ;# contacted S/D column pitch
set maxc  [expr {$NF*$P/2}]         ;# outermost S/D column |x|  (nf even here)
# S/D columns i=0..nf at x=(i-nf/2)*P ; sources = even i, drains = odd i
set src {} ; set drn {}
for {set i 0} {$i <= $NF} {incr i} {
    set x [expr {($i - $NF/2.0)*$P}]
    set x [expr {round($x)}]
    if {$i % 2 == 0} { lappend src $x } else { lappend drn $x }
}
# gate fingers i=0..nf-1 at x=(i-(nf-1)/2)*P
set gfx {}
for {set i 0} {$i < $NF} {incr i} { lappend gfx [expr {round(($i-($NF-1)/2.0)*$P)}] }

drc off
snap internal
cellname create $CELL
load $CELL
box values [expr {-($maxc+60)}] -468 [expr {-($maxc+60)}] -468
magic::gencell gf180mcu::nfet_03v3 M w 4 l 2 nf $NF m 1 guard 0 topc 0 botc 0
flatten ${CELL}_f
load ${CELL}_f

# ---- strap S/D (vertical geometry is nf-invariant, from ib_ntest) ----
foreach x $src { strap_col $x -380 -600 }
foreach x $drn { strap_col $x  380  600 }
rail [expr {-($maxc+40)}] [expr {$maxc+40}] -600 S
rail [expr {-($maxc+40)}] [expr {$maxc+40}]  600 D

# ---- gate: poly bridges up from each finger to a horizontal poly rail; one
#      polycontact->via1->metal2 at the far left over field ----
foreach fx $gfx { box values [expr {$fx-200}] 400 [expr {$fx+200}] 600 ; paint polysilicon }
set lx [expr {-($maxc+180)}]                 ;# poly rail / gate-contact far-left x
box values $lx 556 [expr {$maxc-52}] 600 ; paint polysilicon          ;# horiz poly rail
box values $lx 556 [expr {$lx+80}]   720 ; paint polysilicon          ;# vert poly up
box values [expr {$lx+17}] 620 [expr {$lx+63}] 666 ; paint polycontact
box values [expr {$lx+2}]  620 [expr {$lx+78}] 988 ; paint metal1
box values [expr {$lx+14}] 934 [expr {$lx+66}] 986 ; paint m2contact
box values [expr {$lx-30}] 932 [expr {$maxc-260}] 988 ; paint metal2 ; label G

# ---- bulk: pwell band + a ROW of taps (<=30um spacing) tied to the S rail ----
box values [expr {-($maxc+340)}] -820 [expr {$maxc+340}] 700 ; paint pwell
# taps at S/D column MIDPOINTS (offset +252), 5040=10-pitch spacing (25.2um <=
# 40um so every finger is within 20um of a tap), never sharing x with a strap riser.
set taps {}
for {set tx [expr {-$maxc+252}]} {$tx < $maxc} {set tx [expr {$tx+5040}]} { lappend taps $tx }
foreach cx $taps { welltap $cx -760 -580 -600 psubdiff psubdiffcont }
box values [expr {-($maxc+300)}] -628 [expr {-($maxc+40)}] -572 ; paint metal2 ; label S

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "IBN_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<8} {incr i} { drc find ; puts "EB: [box values]" }
}

# ---- ports ----
box values [expr {-($maxc-40)}] -628 [expr {$maxc-40}] -572 ; port make 1   ;# S
box values [expr {-($maxc-40)}]  572 [expr {$maxc-40}]  628 ; port make 2   ;# D
box values [expr {$lx}]          932 [expr {$maxc-300}]  988 ; port make 3   ;# G
select top cell
save $OUT/$CELL
puts "IBN_SAVED $CELL nf=$NF maxc=$maxc taps=[llength $taps]"
quit -noprompt
