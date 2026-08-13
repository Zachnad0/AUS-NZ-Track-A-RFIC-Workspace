drc off
snap internal
load cp_pmos
# make ports on the rails: select each labeled net, port make
box values -5080 692 5080 748
port make 1
box values -5378 932 5000 988
port make 2
select top cell
extract all
ext2spice lvs
ext2spice -o /tmp/pt.spice
set fh [open /tmp/pt.spice r]; foreach ln [split [read $fh] "\n"] { if {[string match {.subckt*} $ln]} { puts "PORTS: $ln" } }; close $fh
quit -noprompt
