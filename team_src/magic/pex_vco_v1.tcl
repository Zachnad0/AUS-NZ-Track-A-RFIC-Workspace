# pex_vco_v1.tcl -- R+C parasitic extraction of vco_v1, leads included.
# Same recipe as pex_vco_core.tcl (extract do resistance + ext2sim/extresist, cthresh 0,
# rthresh 0, scale off, hierarchy off) with ONE deliberate difference: the source is the
# .mag HIERARCHY, not gds/vco_v1.gds. Reading the GDS would traverse the spiral and give a
# DC short between the terminals; loading the hierarchy keeps vco_inductor_v2 as the LEFview
# abstract whose COMMITTED vco_inductor_v2.ext carries the coil model (two tm11k, m4 bridge,
# 7.46 fF per port). ext2spice hierarchy off then inlines that model into one flat netlist.
drc off
load vco_v1
select top cell
extract path [pwd]
extract do resistance
extract all
ext2sim labels on
ext2sim
extresist tolerance 10
extresist all
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice scale off
ext2spice format ngspice
ext2spice hierarchy off
ext2spice extresist on
ext2spice -o vco_v1.pex.spice
puts "PEX_DONE"
quit -noprompt
