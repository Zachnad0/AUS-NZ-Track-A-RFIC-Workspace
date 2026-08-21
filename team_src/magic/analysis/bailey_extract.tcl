# bailey_extract.tcl -- faithful LOCAL reproduction of the extraction half of
# d-m-bailey/extra_be_checks scripts/gds.analog.spice.tcl. NO device-aware
# preload, NO chip_top.abstract; the only special handling is LEFview on the
# cells named in $ABSTRACT_CELLS -- exactly what EXTRACT_ABSTRACT does upstream.
# Env: LAYOUT_FILE, TOP, ABSTRACT_CELLS (space list, may be empty),
#      FLATGLOB_CELLS (space list, may be empty), OUTSP, DRCOUT.
# CIFIN_STYLE / EXTRACT_STYLE are blanked upstream (run_full_lvs) -> we defer to
# the PDK magicrc defaults, which is the faithful behaviour.
drc off
gds drccheck off
foreach cell $env(FLATGLOB_CELLS) { gds flatglob $cell }
gds flatten yes
puts "BAILEY: reading $env(LAYOUT_FILE)"
gds read $env(LAYOUT_FILE)
foreach cell $env(ABSTRACT_CELLS) {
    puts "BAILEY: LEFview (abstract) on $cell"
    load $cell
    property LEFview true
}
load $env(TOP)
select top cell

# ---- DRC, reported the same way Bailey's magic DRC would count it ----
drc on
drc euclidean on
drc check
drc catchup
set drccount [drc list count total]
puts "BAILEY_DRC_COUNT=$drccount"
if {[info exists env(DRCOUT)] && $env(DRCOUT) ne ""} {
    set fp [open $env(DRCOUT) w]
    puts $fp "DRC_TOTAL=$drccount"
    # per-rule breakdown
    set why [drc listall why]
    foreach {rule coords} $why {
        puts $fp "RULE\t[llength $coords]\t$rule"
    }
    close $fp
}

# ---- analog extraction, mirroring gds.analog.spice.tcl ----
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
