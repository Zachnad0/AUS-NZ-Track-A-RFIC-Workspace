# cp_finalize.tcl -- load the DRC-0 layout, promote the 7 signal labels to ports,
# save as team_src/magic/CP_v1.mag (the name/location verify_cp.sh extracts).
drc off
snap internal
addpath /foss/designs/AUS-NZ-integration/team_src/magic/phase5
load CP_v1_layout
set YN -3600
proc yn {y} { return [expr {$y + $::YN}] }
# 7 ports: box over a segment of each labeled net, then port make <index>
box values 5080 692 5340 748    ; port make 1   ;# VDD (metal2 tap extension)
box values 1008 [yn 692] 1340 [yn 748] ; port make 2   ;# VSS (metal2 tap extension)
box values 0 932 2000 988       ; port make 3   ;# VGP (mirror gate rail, clean segment right of connector)
box values -1340 [yn 932] 1048 [yn 988] ; port make 4  ;# VGN (nmos mirror gate rail)
box values 6520 [yn 932] 7204 [yn 988] ; port make 5   ;# DOWN (nsw gate rail)
box values 6304 -748 7696 -692  ; port make 6   ;# CP_OUT (psw drain rail)
box values 8972 -1600 9028 -1400 ; port make 7  ;# UP (M3 route)
select top cell
save /foss/designs/AUS-NZ-integration/team_src/magic/CP_v1
puts "FINALIZE_DONE cell=[cellname list self]"
quit -noprompt
