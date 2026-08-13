# place_cp.tcl -- Phase 5.1(b,c): place all 8 CP devices + 4 dummies, two-band
# floorplan, spaced (gap G) so no inter-device DRC. Flatten, DRC.
drc off
snap internal
set G 400          ;# inter-device gap (2 um) -- clears nwell/diff spacing
set YN -2600       ;# NMOS band y

cellname create cp_bld
load cp_bld

# place a device at running x on band y; returns advanced x. widths passed in.
proc dev {dev name x y w args} {
    box values $x $y $x $y
    eval "magic::gencell gf180mcu::$dev $name $args"
    return [expr {$x + $w}]
}

# --- PMOS band (y=0): PDUM1 MPREF MPSRC PDUM2 MPSW MINVP ---
set x 0
set x [expr {[dev pfet_03v3 PDUM1 $x 0 748  w 5 l 2   nf 1  m 1 guard 0] + $G}]
set x [expr {[dev pfet_03v3 MPREF $x 0 5284 w 5 l 2   nf 10 m 1 guard 0] + $G}]
set x [expr {[dev pfet_03v3 MPSRC $x 0 5284 w 5 l 2   nf 10 m 1 guard 0] + $G}]
set x [expr {[dev pfet_03v3 PDUM2 $x 0 748  w 5 l 2   nf 1  m 1 guard 0] + $G}]
set x [expr {[dev pfet_03v3 MPSW  $x 0 1884 w 5 l 0.3 nf 10 m 1 guard 1] + $G}]
set x [expr {[dev pfet_03v3 MINVP $x 0 408  w 2 l 0.3 nf 1  m 1 guard 1] + $G}]

# --- NMOS band (y=YN): NDUM1 MNREF MNSNK NDUM2 MNSW MINVN ---
set x 0
set x [expr {[dev nfet_03v3 NDUM1 $x $YN 624  w 5 l 2   nf 1 m 1 guard 0] + $G}]
set x [expr {[dev nfet_03v3 MNREF $x $YN 1128 w 5 l 2   nf 2 m 1 guard 0] + $G}]
set x [expr {[dev nfet_03v3 MNSNK $x $YN 1128 w 5 l 2   nf 2 m 1 guard 0] + $G}]
set x [expr {[dev nfet_03v3 NDUM2 $x $YN 624  w 5 l 2   nf 1 m 1 guard 0] + $G}]
set x [expr {[dev nfet_03v3 MNSW  $x $YN 448  w 5 l 0.3 nf 2 m 1 guard 1] + $G}]
set x [expr {[dev nfet_03v3 MINVN $x $YN 284  w 1 l 0.3 nf 1 m 1 guard 1] + $G}]

select top cell
save cp_bld
load cp_bld
flatten cp_place
load cp_place
select top cell
puts "PLACE_BBOX=[box values]"
drc on ; drc euclidean on ; drc check ; drc catchup
puts "PLACE_DRC=[drc list count total]"
if {[drc list count total] > 0} { puts "WHY: [drc list why]" }
save cp_place
quit -noprompt
