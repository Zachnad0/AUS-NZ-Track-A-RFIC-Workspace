# esd_cells.tcl -- generate the rung-3 secondary-ESD devices from the PDK MAGIC GENCELLS and
# write them to gds/esd_<cell>.gds for route_chip.py (KLayout) to place.
#
# WHY A SEPARATE STEP: the devices are magic gencells (Tcl); the chip flow is KLayout. Rather
# than hand-draw the devices in KLayout -- which would put device geometry under our authorship
# instead of the PDK's -- we generate them here, once, and stream the result.
#
# SIZING IS THE ORGANIZERS', NOT OURS. From examples/pads_simulation/symbols/io_secondary_3p3/
# io_secondary_3p3.sch (Juan, merged 2026-08-25):
#     D1 diode_pd2nw_03v3  r_w=10u r_l=10u m=4
#     D2 diode_nd2ps_03v3  r_w=10u r_l=10u m=4
#     R1 ppolyf_u          W=16e-6 L=4e-6
# m=4 is realised as nx=2 ny=2. Verified by extraction: 4 devices, each pj=40u area=100p,
# i.e. 160 um perimeter / 400 um2 per clamp diode.
#
# doverlap 1 IS DELIBERATE. Without it each of the four units gets its OWN 0.25 um M1 guard
# ring and the four are NOT connected to each other in metal. doverlap merges them into ONE
# ring polygon (still 0.25 um arms) while leaving the device sizing bit-identical.
drc off
snap internal

set GDSDIR /foss/designs/AUS-NZ-integration/gds

# One GDS per cell. A single-library wrapper was tried first and abandoned: `getcell` resolves
# against .mag files on disk and does not populate a wrapper reliably in batch, which produced
# a silently EMPTY library file. Three explicit files cannot fail that way.
proc mk {cellname procname params} {
    global GDSDIR
    load $cellname -silent
    gf180mcu::${procname}_draw $params
    select top cell
    puts "ESDCELL $cellname bbox_iu [box values]"
    gds write $GDSDIR/$cellname.gds
}

# --- pad -> VDDA clamp diode -------------------------------------------------------------
set p [gf180mcu::diode_pd2nw_03v3_defaults]
dict set p w 10 ; dict set p l 10 ; dict set p area 100 ; dict set p peri 40
dict set p nx 2 ; dict set p ny 2 ; dict set p doverlap 1
mk esd_pd2nw diode_pd2nw_03v3 $p

# --- VSSA -> pad clamp diode -------------------------------------------------------------
set q [gf180mcu::diode_nd2ps_03v3_defaults]
dict set q w 10 ; dict set q l 10 ; dict set q area 100 ; dict set q peri 40
dict set q nx 2 ; dict set q ny 2 ; dict set q doverlap 1
mk esd_nd2ps diode_nd2ps_03v3 $q

# --- series ballast resistor (IBIAS only; ISS deliberately has none) ----------------------
# GUARD RING OFF. ppolyf_u_defaults sets glc/grc = 1, which draws an N-WELL guard ring
# (130.389 um2 of nwell) with N+ taps around the resistor. Nothing ties that well, so it
# extracts as an isolated `w_...#` node -- the resistor's bulk pin lands on a FLOATING WELL.
# That is a real defect, not just an LVS artifact: a floating n-well accumulates charge.
#
# Every signed-off resistor in this design is built without it and extracts with bulk = VSS
# (DIV2's XR_SER_*/XRFB_*/XRA*/XRB* all read `... VSS ppolyf_u_1k ...`), and the organizers'
# io_secondary_3p3.sch specifies only W and L -- the guard is a gencell default, not design
# intent. Turning it off makes the golden's `VSSA` bulk TRUE rather than making LVS agree.
set r [gf180mcu::ppolyf_u_defaults]
dict set r w 16 ; dict set r l 4
dict set r guard 0        ;# res_draw's own flag -- glc/grc are the CONTACT flags
mk esd_rpoly ppolyf_u $r

puts "WROTE $GDSDIR/esd_{pd2nw,nd2ps,rpoly}.gds"
quit -noprompt
