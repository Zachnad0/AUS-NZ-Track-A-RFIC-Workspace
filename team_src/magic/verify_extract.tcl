# verify_extract.tcl -- DRC + LVS-netlist extraction, driven by verify_cp.sh.
# Reads environment variables (set by the driver):
#   VERIFY_CELL     top cell name
#   VERIFY_SRC      absolute path to layout source (.gds or .mag)
#   VERIFY_SRCTYPE  "gds" or "mag"
#   VERIFY_OUT      absolute path for the extracted LVS spice
# Emits machine-parseable markers on stdout:
#   VERIFY_DRC_COUNT=<n>
#   VERIFY_EXTRACT_DONE=<path>
set cell  $env(VERIFY_CELL)
set src   $env(VERIFY_SRC)
set stype $env(VERIFY_SRCTYPE)
set outsp $env(VERIFY_OUT)

drc off
if {$stype eq "gds"} {
    gds read $src
    load $cell
} else {
    addpath [file dirname $src]
    load $cell
}
select top cell

# ---- DRC (full hierarchy) ----
drc on
drc euclidean on
drc check
drc catchup
set drccount [drc list count total]
puts "VERIFY_DRC_COUNT=$drccount"

# ---- Extract device-level netlist for LVS (no parasitics) ----
# merge aggressive: collapse truly-parallel identical fingers (same 4 nodes/L/W) into one
# device with an M= multiplier. Folded CML/mirror devices (W40 -> w4 nf10, mirror m24) draw
# as N fingers; without this they extract as N separate devices and never match the goldens,
# which are written in the merged form (m=24, or W40 nf=1 = the summed-width equivalent that
# netgen accepts since nfet/pfet_03v3 are pin-only black boxes). Only identical same-net
# devices merge, so distinct/common-centroid devices on different nets are untouched.
extract all
ext2spice lvs
ext2spice merge aggressive
ext2spice -o $outsp
puts "VERIFY_EXTRACT_DONE=$outsp"
quit -noprompt
