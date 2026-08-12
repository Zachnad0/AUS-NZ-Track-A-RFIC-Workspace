# p1_dev1.tcl -- generate a single nfet_03v3, save ALL cells, report its ports.
drc off
snap internal
cellname create p1_dev1
load p1_dev1
box values 0 0 0 0
magic::gencell gf180mcu::nfet_03v3 MN w 10 l 2 nf 1 m 1
set devcell [lindex [cellname list children p1_dev1] 0]
puts "DEVCELL=$devcell"
load $devcell
puts "PORTS_OF_DEVCELL:"
foreach p [port list] { puts "  port= $p index=[port $p index] class=[port $p class] use=[port $p use]" }
load p1_dev1
writeall force
quit -noprompt
