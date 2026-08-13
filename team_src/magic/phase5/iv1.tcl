drc off
snap internal
cellname create ivp
load ivp
box values 0 0 0 0
magic::gencell gf180mcu::pfet_03v3 M w 2 l 0.3 nf 1 m 1 guard 1
select top cell
drc on; drc euclidean on; drc check; drc catchup
puts "INVP_standalone_DRC=[drc list count total]"
save ivp
quit -noprompt
