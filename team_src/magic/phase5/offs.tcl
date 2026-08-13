drc off
snap internal
cellname create cp
load cp
box values 8000 3000 8000 3000
magic::gencell gf180mcu::pfet_03v3 M w 5 l 2 nf 10 m 1 guard 0 topc 0 botc 0
puts "CHILDREN=[cellname list children cp]"
flatten cpf
load cpf
select top cell
puts "BBOX=[box values]"
extract all
ext2spice lvs
ext2spice -o /tmp/o.spice
set fh [open /tmp/o.spice r]; foreach ln [split [read $fh] "\n"] { if {[string match {X0 *} $ln]} { puts "X0nets: [lrange $ln 0 4]" } }; close $fh
quit -noprompt
