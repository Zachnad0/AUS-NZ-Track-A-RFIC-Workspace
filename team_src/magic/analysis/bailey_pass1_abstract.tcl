# bailey_pass1_abstract.tcl -- reproduction of extra_be_checks run_extract PASS 1
# (abstract.tcl): for each ABSTRACT_CELL, load it, mark LEFview, and `lef write
# -hide -pinonly` a geometry-free pins-only LEF into $EXT_DIR. magic's -pinonly write
# emits each labelled PORT as its own pin RECT, so DC-continuous internal metal (the
# spiral shorting OUT_p/OUT_n) does NOT merge the pins. Env: LAYOUT_FILE, ABSTRACT_CELLS,
# EXT_DIR. (Bailey adds a grid-delete of child instances for very large cells; for these
# small cells the plain -pinonly write already yields clean separate pins.)
drc off
gds drccheck off
crashbackups stop
undo disable
puts "PASS1: reading $env(LAYOUT_FILE)"
gds read $env(LAYOUT_FILE)
cd $env(EXT_DIR)
foreach cell $env(ABSTRACT_CELLS) {
    load $cell
    property LEFview true
    lef write $cell -hide -pinonly
    puts "PASS1: wrote $env(EXT_DIR)/$cell.lef"
}
quit -noprompt
