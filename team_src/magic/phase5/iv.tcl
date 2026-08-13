drc off
snap internal
set p [magic::gencell_makecell gf180mcu::pfet_03v3 w 2 l 0.3 nf 1 m 1 guard 0 topc 0 botc 0]
set n [magic::gencell_makecell gf180mcu::nfet_03v3 w 1 l 0.3 nf 1 m 1 guard 0 topc 0 botc 0]
puts "INVP=$p INVN=$n"
writeall force
quit -noprompt
