# dev_geom.tcl -- report geometry of the CP device building blocks (guard=0),
# so floorplan positions can be computed. bbox + nwell/diff extents per device.
drc off
snap internal

proc gen {cell dev args} {
    cellname create $cell
    load $cell
    box values 0 0 0 0
    eval "magic::gencell gf180mcu::$dev M $args"
    select top cell
    puts "$cell BBOX=[box values]"
    # report the child device cell's layer extents
    set ch [lindex [cellname list children $cell] 0]
    puts "  child=$ch"
}

gen cp_pmir pfet_03v3 w 5 l 2 nf 10 m 1 guard 0
gen cp_psw  pfet_03v3 w 5 l 0.3 nf 10 m 1 guard 0
gen cp_nmir nfet_03v3 w 5 l 2 nf 2 m 1 guard 0
gen cp_nsw  nfet_03v3 w 5 l 0.3 nf 2 m 1 guard 0
gen cp_invp pfet_03v3 w 2 l 0.3 nf 1 m 1 guard 0
gen cp_invn nfet_03v3 w 1 l 0.3 nf 1 m 1 guard 0
gen cp_pdum pfet_03v3 w 5 l 2 nf 1 m 1 guard 0
gen cp_ndum nfet_03v3 w 5 l 2 nf 1 m 1 guard 0
writeall force
quit -noprompt
