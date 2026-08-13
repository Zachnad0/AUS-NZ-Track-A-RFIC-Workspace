# cp_b_pair.tcl -- Phase 5.1(b): M_PREF + M_PSRC matched pair (pfet 10x5u L=2, guard=0),
# placed adjacent sharing nwell. Flatten -> DRC. Extract to recover terminal coords.
drc off
snap internal
cellname create cp_bld
load cp_bld
# M_PREF at x=0, M_PSRC abutted to its right (nwells merge)
box values 0 0 0 0
magic::gencell gf180mcu::pfet_03v3 MPREF w 5 l 2 nf 10 m 1 guard 0
box values 5284 0 5284 0
magic::gencell gf180mcu::pfet_03v3 MPSRC w 5 l 2 nf 10 m 1 guard 0
select top cell
save cp_bld
load cp_bld
flatten cp_pair
load cp_pair
select top cell
puts "PAIR_BBOX=[box values]"
drc on ; drc euclidean on ; drc check ; drc catchup
puts "PAIR_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "--- first violations ---"
    puts [drc list why]
}
save cp_pair
quit -noprompt
