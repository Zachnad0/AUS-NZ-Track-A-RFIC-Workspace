# p1_pair.tcl -- Phase 1.1 throwaway (flatten + label-on-diffusion).
# Place nfet+pfet via generators, FLATTEN into p1_pair so device geometry is at
# top level, then label S/D/gate/bulk on the large diffusion/poly/guard regions.
drc off
snap internal
cellname create p1_bld
load p1_bld
box values 0 0 0 0
magic::gencell gf180mcu::nfet_03v3 MN w 10 l 2 nf 1 m 1
box values 2000 0 2000 0
magic::gencell gf180mcu::pfet_03v3 MP w 10 l 2 nf 1 m 1
select top cell
save p1_bld

# flatten hierarchy into a fresh flat cell
load p1_bld
flatten p1_pair
load p1_pair

# --- labels on flat geometry ---
box values -260 -20 -240 20   ; label S_N ndiff
box values  240 -20  260 20   ; label D_N ndiff
box values  -20 1082 20 1090  ; label G_N polysilicon
box values -422 -20 -416 20   ; label B_N psubdiff
box values 1740 -20 1760 20   ; label S_P pdiff
box values 2240 -20 2260 20   ; label D_P pdiff
box values 1980 1082 2020 1090; label G_P polysilicon
box values 1578 -20 1584 20   ; label B_P nsubdiff

select top cell
save p1_pair

drc on
drc euclidean on
drc check
drc catchup
puts "PAIR_DRC_COUNT=[drc list count total]"

extract all
ext2spice lvs
ext2spice -o p1_pair.spice
puts "---BEGIN p1_pair.spice---"
set fh [open p1_pair.spice r]; puts [read $fh]; close $fh
puts "---END p1_pair.spice---"
quit -noprompt
