drc off
snap internal
proc geo {tag args} {
  set c [eval "magic::gencell_makecell gf180mcu::$args"]
  load $c
  select top cell
  set bb [box values]
  set hw [expr {([lindex $bb 2]-[lindex $bb 0])/2}]
  puts "$tag  bbox=$bb  hw=$hw"
}
geo PSW  pfet_03v3 w 5 l 0.3 nf 10 m 1 guard 0 topc 0 botc 0
geo INVP pfet_03v3 w 2 l 0.3 nf 1 m 1 guard 1
geo PDUM pfet_03v3 w 5 l 2 nf 1 m 1 guard 0 topc 0 botc 0
geo NSW  nfet_03v3 w 5 l 0.3 nf 2 m 1 guard 0 topc 0 botc 0
geo INVN nfet_03v3 w 1 l 0.3 nf 1 m 1 guard 1
geo NDUM nfet_03v3 w 5 l 2 nf 1 m 1 guard 0 topc 0 botc 0
quit -noprompt
