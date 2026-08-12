# nf_test.tcl -- Phase 1 addendum: is generator `w` per-finger or total?
# Build nf=10 w=5, nf=10 w=50, and m=4 w=5; flatten; extract; dump device lines.
drc off
snap internal

proc build {cellname args} {
    cellname create ${cellname}_bld
    load ${cellname}_bld
    box values 0 0 0 0
    eval "magic::gencell gf180mcu::nfet_03v3 MN $args"
    save ${cellname}_bld
    load ${cellname}_bld
    flatten $cellname
    load $cellname
    drc on ; drc euclidean on ; drc check ; drc catchup
    puts "DRC_${cellname}=[drc list count total]"
    extract all
    ext2spice lvs
    ext2spice -o ${cellname}.spice
    puts "---BEGIN ${cellname}.spice---"
    set fh [open ${cellname}.spice r]; puts [read $fh]; close $fh
    puts "---END ${cellname}.spice---"
    drc off
}

build nf10_w5  w 5  l 2 nf 10 m 1
build nf10_w50 w 50 l 2 nf 10 m 1
build m4_w5    w 5  l 2 nf 1  m 4
quit -noprompt
