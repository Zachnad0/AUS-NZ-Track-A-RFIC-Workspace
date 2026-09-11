# pex_vco_core.tcl -- R+C parasitic extraction of vco_core from the COMMITTED GDS.
# Adapted verbatim from pex_cp_v1.tcl; only the cell name and the GDS path differ.
# capacitance-only; this one also extracts parasitic resistance.
#
# Run in-container from team_src/magic/pex_work:
#   magic -dnull -noconsole -rcfile $PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc \
#         ../pex_cp_v1.tcl
#
# READ-ONLY on every tracked file: reads gds/vco_core.gds, writes only into pex_work/ (gitignored).
# It NEVER writes a GDS -- standing rule adopted 2026-09-01 after a `gds write` briefly
# clobbered gds/DIV2_QUAD_v1.gds.
#
# WHY `extract do resistance` AND the ext2sim/extresist pair: `ext2spice rthresh 0` on its own
# emits ZERO resistors -- it only sets a reporting threshold. Magic needs a real resistance
# extraction pass (extresist), which in turn needs the .sim view. Without these four lines the
# netlist is capacitance-only, which cannot move a DC operating point. Measured on this cell:
# full pass on this cell: see signoff/pex/vco_core/README.md for the measured counts.
#
# `extract path` is pinned to the CWD: magic writes each cell's .ext BESIDE the file that cell
# was loaded from, so without it the run drops .ext files onto tracked cells in team_src/magic/
# (same hazard documented in verify_extract.tcl).
drc off
gds read /foss/designs/AUS-NZ-integration/gds/vco_core.gds
load vco_core
select top cell
# Flatten so every device, coupling cap and parasitic R lands in one netlist.
flatten vco_core_flat
load vco_core_flat
select top cell
extract path [pwd]
extract do resistance
extract all
ext2sim labels on
ext2sim
extresist tolerance 10
extresist all
# Retain everything: cthresh 0 keeps all coupling caps, rthresh 0 all parasitic R.
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice format ngspice
ext2spice hierarchy off
ext2spice extresist on
ext2spice -o vco_core.pex.spice
puts "PEX_DONE"
quit -noprompt
