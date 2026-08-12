drc off
snap internal
cellname create p1_m4b
load p1_m4b
box values 0 0 0 0
magic::gencell gf180mcu::nfet_03v3 MN w 4 l 2 nf 1 m 4
save p1_m4b
load p1_m4b
flatten p1_m4
load p1_m4
drc on
drc euclidean on
drc check
drc catchup
puts "M4_DRC_COUNT=[drc list count total]"
extract all
ext2spice lvs
ext2spice -o p1_m4.spice
puts "---BEGIN p1_m4.spice---"
set fh [open p1_m4.spice r]; puts [read $fh]; close $fh
puts "---END p1_m4.spice---"
puts "CHILDREN_OF_BLD=[cellname list children p1_m4b]"
quit -noprompt
