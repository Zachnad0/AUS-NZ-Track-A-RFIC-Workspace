# enumerate every DRC error in the top cell via `drc find` (prints rule text + position),
# to catch magic-only rules that `drc listall why` under-reports. Env REH_CELL.
drc off ; snap internal
cd /tmp
gds noduplicates true
addpath /foss/designs/AUS-NZ-integration/team_src/magic
addpath /foss/designs/AUS-NZ-integration/team_src/magic/vco_inductor_v2
load vco_varactors
load vco_inductor_v2
gds read /foss/designs/AUS-NZ-integration/gds/$env(REH_CELL).gds
load $env(REH_CELL)
select top cell
drc euclidean on
drc check
drc catchup
set n [drc list count total]
puts "TOTAL $n"
box 0 0 0 0
for {set i 0} {$i < $n} {incr i} {
    set r [drc find]
    puts "FIND[$i]: $r"
}
