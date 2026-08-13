drc off
snap internal
# 10-finger shared-diffusion array, guard=0 (the M_PREF interdigitation geometry)
cellname create gt_arr
load gt_arr
box values 0 0 0 0
magic::gencell gf180mcu::pfet_03v3 M w 5 l 2 nf 10 m 1 guard 0
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "ARR_G0_nf10_DRC=[drc list count total]  BBOX=[box values]"
drc off
# same but guard=1 for comparison
cellname create gt_arr1
load gt_arr1
box values 0 0 0 0
magic::gencell gf180mcu::pfet_03v3 M w 5 l 2 nf 10 m 1 guard 1
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "ARR_G1_nf10_DRC=[drc list count total]  BBOX=[box values]"
quit -noprompt
