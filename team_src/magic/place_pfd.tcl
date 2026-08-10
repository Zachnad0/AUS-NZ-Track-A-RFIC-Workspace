# Scripted placement of the library-cell PFD (abutted std-cell row).
# Cells abut on shared VDD(top)/VSS(bottom) rails at y=0..3.92; power connects by abutment.
drc off
snap internal
load PFD_lib -quiet
# add the std-cell mag dir to the search path
path search +/foss/designs/AUS-NZ-integration/gf180mcu/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/mag
# place instances left-to-right, lower-left at cumulative x
box position 0um 0um 0um 0um
getcell gf180mcu_fd_sc_mcu7t5v0__dffrnq_1
box position 19.04um 0um 19.04um 0um
getcell gf180mcu_fd_sc_mcu7t5v0__dffrnq_1
box position 38.08um 0um 38.08um 0um
getcell gf180mcu_fd_sc_mcu7t5v0__nand2_1
box position 40.88um 0um 40.88um 0um
getcell gf180mcu_fd_sc_mcu7t5v0__inv_1
box position 43.12um 0um 43.12um 0um
getcell gf180mcu_fd_sc_mcu7t5v0__inv_1
# report the assembled bbox and instance list
select top cell
box
puts "INSTANCES:"
foreach i [cellname list children PFD_lib] { puts "  $i" }
save PFD_lib
drc on
drc euclidean on
drc check
puts "DRC_COUNT [drc list count total]"
quit -noprompt
