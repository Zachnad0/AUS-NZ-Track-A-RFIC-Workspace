# extract the routes-only cell -> net/node count + per-label node (distinct-net proof).
drc off ; snap internal
gds read /foss/designs/AUS-NZ-integration/gds/reh_routes.gds
load reh_routes
select top cell
extract all
ext2spice lvs
ext2spice -o /tmp/reh_routes.spice
# count nodes from the .ext
set fp [open reh_routes.ext r]
set nodes 0
while {[gets $fp line] >= 0} { if {[string match "node *" $line]} { incr nodes } }
close $fp
puts "EXT_NODES $nodes"
