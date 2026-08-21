# bailey_pass2_extract.tcl -- reproduction of extra_be_checks run_extract PASS 2
# (extract.tcl): read the pin-only LEFs generated in PASS 1, then `gds noduplicates yes`
# + `gds read` so magic KEEPS the geometry-free abstract and SKIPS the cell's real
# geometry from the stream (this is what prevents the spiral from shorting OUT_p/OUT_n).
# Then set LEFview again, extract analog-style, ext2spice. NO chip_top.abstract, NO
# device-aware .mag preload -- only the LEFs and lvs_config's EXTRACT_ABSTRACT list.
# Env: LAYOUT_FILE, TOP, ABSTRACT_CELLS, FLATGLOB_CELLS, EXT_DIR, OUTSP, DRCOUT.
drc off
gds drccheck off
crashbackups stop
undo disable
cd $env(EXT_DIR)
foreach cell $env(ABSTRACT_CELLS) {
    if { [file exists $env(EXT_DIR)/$cell.lef] } {
        puts "PASS2: using abstracted $cell"
        lef read $env(EXT_DIR)/$cell.lef
    }
}
foreach cell $env(FLATGLOB_CELLS) { gds flatglob $cell }
gds flatten yes
gds noduplicates yes
puts "PASS2: reading $env(LAYOUT_FILE)"
gds read $env(LAYOUT_FILE)
foreach cell $env(ABSTRACT_CELLS) { load $cell; property LEFview true }
load $env(TOP)
select top cell

# ---- DRC (should drop the varactor PL.5a now the varactor is abstracted away) ----
drc on
drc euclidean on
drc check
drc catchup
set drccount [drc list count total]
puts "BAILEY_DRC_COUNT=$drccount"
if {[info exists env(DRCOUT)] && $env(DRCOUT) ne ""} {
    set fp [open $env(DRCOUT) w]; puts $fp "DRC_TOTAL=$drccount"
    foreach {rule coords} [drc listall why] { puts $fp "RULE\t[llength $coords]\t$rule" }
    close $fp
}

# ---- analog extraction mirroring extract.tcl ----
drc off
extract no all
extract do aliases
extract do local
extract unique notopports
extract
ext2spice lvs
ext2spice merge conservative
ext2spice short resistor
ext2spice -o $env(OUTSP) $env(TOP).ext
puts "BAILEY_EXTRACT_DONE=$env(OUTSP)"
quit -noprompt
