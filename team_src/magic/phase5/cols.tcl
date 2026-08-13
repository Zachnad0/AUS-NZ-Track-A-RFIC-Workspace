drc off
snap internal
proc cols {tag args} {
  set c [eval "magic::gencell_makecell gf180mcu::$args"]
  load $c
  set r ""
  foreach lyr {pdiffc ndiffc} {
    set b [what -list]
  }
  puts "$tag CELL=$c"
}
cols PSW  pfet_03v3 w 5 l 0.3 nf 10 m 1 guard 0 topc 0 botc 0
cols NSW  nfet_03v3 w 5 l 0.3 nf 2 m 1 guard 0 topc 0 botc 0
writeall force
quit -noprompt
