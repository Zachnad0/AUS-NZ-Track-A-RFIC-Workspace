# p1_probe.tcl -- Phase 1 representation probe (fixed cell creation).
drc off
snap internal
cellname create p1_probe
load p1_probe

# one nfet_03v3: W=10 L=2
box values 0 0 0 0
magic::gencell gf180mcu::nfet_03v3 MN w 10 l 2 nf 1 m 1

# one pfet_03v3: W=10 L=2, placed clear to the right
box values 400 0 400 0
magic::gencell gf180mcu::pfet_03v3 MP w 10 l 2 nf 1 m 1

select top cell
save p1_probe
puts "CHILDREN:"
foreach c [cellname list children p1_probe] { puts "  child= $c" }
puts "BBOX_MN=[instance list bbox MN]"
puts "BBOX_MP=[instance list bbox MP]"

drc on
drc euclidean on
drc check
drc catchup
puts "PROBE_DRC_COUNT=[drc list count total]"

extract all
ext2spice lvs
ext2spice -o p1_probe.spice
puts "---BEGIN p1_probe.spice---"
set fh [open p1_probe.spice r]
puts [read $fh]
close $fh
puts "---END p1_probe.spice---"
quit -noprompt
