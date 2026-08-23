# reh_ctx_extract.tcl -- FULL in-context extraction of a reh_* cell using the SAME
# abstract preload verify_cp uses for chip_top (chip_top.abstract): preload the
# vco_varactors + vco_inductor_v2 abstracts with `gds noduplicates true` so `gds read`
# keeps them instead of traversing the spiral geometry (which would short OUT_p/OUT_n).
# This is what a routes-only extract could never do -- it sees the haul nets AND the block
# nets, so it catches a haul shorting to a block. Env REH_CELL (reh_phase8|reh_base),
# CTX_OUT (spice path). NOT the flow -- an analysis harness.
drc off
cd /tmp
set cell $env(REH_CELL)
set outsp $env(CTX_OUT)
gds noduplicates true
addpath /foss/designs/AUS-NZ-integration/team_src/magic
addpath /foss/designs/AUS-NZ-integration/team_src/magic/vco_inductor_v2
load vco_varactors
load vco_inductor_v2
gds read /foss/designs/AUS-NZ-integration/gds/$cell.gds
load $cell
select top cell
# magic writes each cell's .ext BESIDE the file that cell was loaded from -- not to the
# current directory. So an abstract preload that `addpath`s into the source tree makes
# `extract all` overwrite TRACKED .ext files there, and it overwrites them with the
# geometry-free abstract: the device (rsubckt tm11k) is dropped and a GND port appears.
# That corrupts the baseline in the direction that HIDES shorts. Pin the output directory
# instead; `cd` alone does not do it.
extract path [pwd]
extract all
ext2spice lvs
ext2spice -o $outsp
puts "CTX_EXTRACT_DONE=$outsp"
quit -noprompt
