# chip_top.tcl -- Phase 7 rung 2a: place the 5 closed blocks (placement only, no routing).
# getcell is LOWER-LEFT aligned; box(X,Y) puts the block's bbox LL at (X,Y). Coords in iu
# (200/um). Floorplan per docs/phase7-floorplan.md. PRE-LOAD every master (incl vco_v1's
# abstract-inductor + gencell children and DIV2's ib_conv_v1) or getcell drops the instance.
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
drc off ; snap internal
# ---- pre-load masters ----
load vco_inductor_v2/vco_inductor_v2
load vco_core
load vco_varactors
load vco_tune_r
load vco_v1
load ib_conv_v1
load DIV2_QUAD_v1
load ibias_gen_v1
load CP_v1
load PFD_lib
# ---- place ----
cellname create chip_top ; load chip_top
box values 0 0 0 0         ; getcell DIV2_QUAD_v1     ;# bottom-left  (0,0)-(237.4,174.2)
# vco_v1 .mag bbox (66x125, abstract inductor) != real GDS footprint (182x179.5): the full
# spiral extends 13400iu LEFT of the .mag LL. Offset the box by +13400 so the REAL vco_v1
# left edge lands at x58000 (290um), 53um clear of DIV2's right edge (47480).
box values 71400 0 71400 0 ; getcell vco_v1           ;# real footprint (290,0)-(472,179.5)
box values 0 41000 0 41000 ; getcell ibias_gen_v1     ;# mid-left     (0,205)-(181.8,270.3)
box values 42000 41000 42000 41000 ; getcell CP_v1    ;# mid          (210,205)-(283.5,233)
box values 42000 49000 42000 49000 ; getcell PFD_lib  ;# top-mid      (210,245)-(270,269)
select top cell
puts "CHIP_BBOX=[box values]"
drc on ; drc euclidean on ; drc check ; drc catchup
puts "CHIP_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<16} {incr i} { drc find ; puts "EB: [box values]" }
}
save $OUT/chip_top
puts "CHIP_SAVED"
quit -noprompt
