# vco_tune_r.tcl -- rung 3d: VCO tune resistor. ppolyf_u_1k w1 l15 = 15 squares
#   = 15 kOhm on the 1k sheet variant (Greg's decision to design to 1k).
# Terminals (query the ACTUAL polycontact M1, not the extracted node-name coords):
#   top poly-contact (189..363, 3361..3407) = TUNE ; bottom (189..363, 189..235) =
#   cap_bias ; the full-width metal1 guard ring = GND (body).
# NOTE: vco_v1.sch still says XR2 ... ppolyf_u_3k r_width=1u r_length=5u. Design-to-1k
#   means 15 squares not 5 -> this cell is w1 l15. The .sch change (device + tune-range
#   re-sim) is Greg's (rule 13); the golden here matches the LAYOUT (ppolyf_u_1k l15).
# Run from team_src/magic so the save/cellname resolves as `vco_tune_r` (a full-path
#   save renames the cell and breaks netgen's cell lookup).
set OUT /foss/designs/AUS-NZ-integration/team_src/magic
drc off ; snap internal
box values 0 0 0 0
magic::gencell gf180mcu::ppolyf_u_1k RT w 1 l 15
flatten vco_tune_r ; load vco_tune_r
box values 240 3372 312 3396 ; label TUNE center metal1 ; port make 1
box values 240 200 312 224 ; label cap_bias center metal1 ; port make 2
box values 40 -20 120 12 ; label GND center metal1 ; port make 3
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "RDRC=[drc list count total]"
save vco_tune_r
gds write /foss/designs/AUS-NZ-integration/gds/vco_tune_r.gds
puts "RT_SAVED bbox=[box values]"
quit -noprompt
