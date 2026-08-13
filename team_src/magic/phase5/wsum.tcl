drc off
snap internal
proc wsum {args} {
  set c [eval "magic::gencell_makecell gf180mcu::pfet_03v3 $args"]
  load $c
  select top cell
  extract all
  ext2spice lvs
  ext2spice -o /tmp/w.spice
  set fh [open /tmp/w.spice r]; set t [read $fh]; close $fh
  set sum 0; set n 0
  foreach ln [split $t "\n"] { if {[regexp {w=([0-9.]+)u} $ln -> w]} { set sum [expr {$sum+$w}]; incr n } }
  puts "PARAMS=[lrange $args 0 5]  fingers=$n  Wsum=${sum}u"
}
wsum w 5  l 2 nf 10 m 1 guard 0
wsum w 10 l 2 nf 5  m 1 guard 0
wsum w 5  l 2 nf 20 m 1 guard 0
wsum w 5  l 2 nf 2  m 1 guard 0
wsum w 25 l 2 nf 2  m 1 guard 0
quit -noprompt
