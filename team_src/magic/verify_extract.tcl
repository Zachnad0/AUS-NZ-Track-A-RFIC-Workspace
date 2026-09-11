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
    # env-gated abstract preload: for cells that instance a magic ABSTRACT (LEFview +
    # GDS_FILE) whose coil/black-box geometry must NOT be traversed for LVS. Pre-loading
    # the abstract + `gds noduplicates true` makes `gds read` keep the abstract instead of
    # reading the full geometry from the stream. Untouched for cells with no VERIFY_PRELOAD.
    if {[info exists env(VERIFY_PRELOAD)] && $env(VERIFY_PRELOAD) ne ""} {
        gds noduplicates true
        if {[info exists env(VERIFY_PRELOAD_PATH)] && $env(VERIFY_PRELOAD_PATH) ne ""} {
            foreach p $env(VERIFY_PRELOAD_PATH) { addpath $p }
        }
        foreach c $env(VERIFY_PRELOAD) { load $c }
    }
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
# magic writes each cell's .ext BESIDE the file that cell was loaded from -- not to the
# current directory. So an abstract preload that `addpath`s into the source tree makes
# `extract all` overwrite TRACKED .ext files there, and it overwrites them with the
# geometry-free abstract: the device (rsubckt tm11k) is dropped and a GND port appears.
# That corrupts the baseline in the direction that HIDES shorts. Pin the output directory
# instead; `cd` alone does not do it.
extract path [pwd]
# `extract all` ALONE merges two electrically-separate pieces of metal that carry the same
# label into ONE node, so a net cut in half would still LVS "match uniquely" provided both
# halves kept the label (layout-review-sep01.md 6 item 22). `unique noports` gives duplicate
# NON-port labels distinct names for the extraction; ports are left alone, so subckt port
# matching against the golden is unaffected. Verified 2026-09-11 to be a no-op on all five
# blocks + chip_top: identical device/port/net counts and all six still match uniquely.
# It does NOT cover splits between two PORT-labelled pieces -- only the metal-only
# connectivity extraction does. Nothing is persisted: this script never saves.
extract unique noports
extract all
ext2spice lvs
ext2spice -o $outsp
puts "VERIFY_EXTRACT_DONE=$outsp"
quit -noprompt
