drc off
snap internal
set c [magic::gencell_makecell gf180mcu::nfet_03v3 w 5 l 2 nf 4 m 1 guard 0 topc 0 botc 0]
puts "CELL=$c"
writeall force
quit -noprompt
