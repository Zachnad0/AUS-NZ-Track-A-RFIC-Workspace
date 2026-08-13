# guard_test.tcl -- Phase 5.1 opener: does per-device guard ring block the
# common-centroid interdigitation? Compare guard=1 (per-device ring) vs guard=0
# (bare active, group ring drawn separately). pfet_03v3 5u/2u = one mirror finger.
drc off
snap internal

proc devbbox {cell} {
    load $cell
    select top cell
    return [box values]
}

# --- A: single finger, guard=1 (default per-device ring) ---
cellname create gt_g1
load gt_g1
box values 0 0 0 0
magic::gencell gf180mcu::pfet_03v3 M w 5 l 2 nf 1 m 1 guard 1
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "G1_DRC=[drc list count total]  G1_BBOX=[box values]"
drc off

# --- B: single finger, guard=0 (bare active, no ring) ---
cellname create gt_g0
load gt_g0
box values 0 0 0 0
magic::gencell gf180mcu::pfet_03v3 M w 5 l 2 nf 1 m 1 guard 0
select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "G0_DRC=[drc list count total]  G0_BBOX=[box values]"
drc off

writeall force
quit -noprompt
