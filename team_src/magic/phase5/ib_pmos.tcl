# ib_pmos.tcl -- full PMOS side of ibias_gen_v1 (9 devices).
# Bottom row (L=2, y=0): mirror MP0/MP1/MP2 + XCDEC decap + MPB (pb2 diode). Wide m=24
# legs split 2x nf=12. Top row (L=1, y=YCP): cascodes MP0c/MP1c/MP2c/MPBc.
# Two cascode gate bars: PA over MP0c/MP1c, VBCPD over MP2c/MPBc. Cascode nwell taps ->
# VDD (tapy=-1700 rail, routed up on M4). Inter-row sources PB/p1/p2/pb2 on M3.
# Ports: VDD PB PA VGN IB_DIV2 VBCPD.
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ib_pmos
set YCP 4400

drc off ; snap internal
cellname create $CELL ; load $CELL

# --- bottom (mirror) x-centers, as ib_pmir ---
set c0a 3400
set c0b [expr {$c0a + 3024 + 3024 + 560}]
set c1  [expr {$c0b + 3024 + 1260 + 560}]
set c2a [expr {$c1  + 1260 + 3024 + 560}]
set c2b [expr {$c2a + 3024 + 3024 + 560}]
set cCD [expr {$c2b + 3024 + 1512 + 560}]
set cPB [expr {$cCD + 1512 +  504 + 560}]
# --- cascode (L=1) centers, above the corresponding mirror halves ---
set d0a $c0a ; set d0b $c0b ; set d1 $c1 ; set d2a $c2a ; set d2b $c2b ; set dBc $cPB

# place all -> flatten -> strap
place_pfet 12 $c0a MP0a ; place_pfet 12 $c0b MP0b ; place_pfet 5 $c1 MP1
place_pfet 12 $c2a MP2a ; place_pfet 12 $c2b MP2b ; place_pfet 6 $cCD MPCD ; place_pfet 2 $cPB MPB
place_pfet 12 $d0a MP0ca 4400 1 ; place_pfet 12 $d0b MP0cb 4400 1 ; place_pfet 5 $d1 MP1c 4400 1
place_pfet 12 $d2a MP2ca 4400 1 ; place_pfet 12 $d2b MP2cb 4400 1 ; place_pfet 2 $dBc MPBc 4400 1
flatten ${CELL}_f ; load ${CELL}_f
foreach {nf cx} [list 12 $c0a 12 $c0b 5 $c1 12 $c2a 12 $c2b 6 $cCD 2 $cPB] { pfet_leg $nf $cx 1 }
# cascodes: L=1, yoff=YCP, taps=1 tied to a dedicated VDD rail at YCP-1700 (tapy=-1700)
foreach {nf cx} [list 12 $d0a 12 $d0b 5 $d1 12 $d2a 12 $d2b 2 $dBc] { pfet_leg $nf $cx 1 1 $YCP 1 -1700 }

# ===== bottom-row nets (mirror), as ib_pmir =====
set xL [expr {$c0a - 3024 - 210}]
set xR [expr {$cPB +  504 + 40}]
box values $xL -1528 $xR -1472 ; paint metal2   ;# VDD bar
box values $xL 1752 [expr {$cCD+1512-260}] 1808 ; paint metal2   ;# PB gate bar
foreach cx [list $c0a $c0b] { box values [expr {$cx-28}] 1472 [expr {$cx+28}] 1808 ; paint metal2 }  ;# MP0 diode
box values [expr {$c2a+3024}] 1472 [expr {$c2b-3024}] 1528 ; paint metal2  ;# p2 merge
box values [expr {$cCD-28}] -1528 [expr {$cCD+28}] 1528 ; paint metal2      ;# XCDEC D=S=VDD
box values [expr {$cPB-28}] 1472 [expr {$cPB+28}] 1808 ; paint metal2       ;# MPB pb2 diode

# ===== top-row cascode gate bars + VDD tap rail =====
# PA bar over MP0ca/MP0cb/MP1c ; VBCPD bar over MP2ca/MP2cb/MPBc
box values [expr {$d0a-1824-210}] [expr {$YCP+1752}] [expr {$d1+1260-260}] [expr {$YCP+1808}] ; paint metal2  ;# PA bar
box values [expr {$d2a-1824-210}] [expr {$YCP+1752}] [expr {$dBc+504-260}] [expr {$YCP+1808}] ; paint metal2  ;# VBCPD bar
# MP0c diode halves: drain(YCP+1500) -> PA bar
foreach cx [list $d0a $d0b] { box values [expr {$cx-28}] [expr {$YCP+1472}] [expr {$cx+28}] [expr {$YCP+1808}] ; paint metal2 }
# MP2c drain merge (IB_DIV2)
box values [expr {$d2a+1824}] [expr {$YCP+1472}] [expr {$d2b-1824}] [expr {$YCP+1528}] ; paint metal2
# MPBc diode: drain -> VBCPD bar
box values [expr {$dBc-28}] [expr {$YCP+1472}] [expr {$dBc+28}] [expr {$YCP+1808}] ; paint metal2
# VDD tap rail (YCP-1700) across the cascode row + M4 riser to the mirror VDD bar
box values [expr {$d0a-1824-210}] [expr {$YCP-1728}] [expr {$dBc+504+40}] [expr {$YCP-1672}] ; paint metal2
via_m2m4 [expr {$d0a-1824-100}] [expr {$YCP-1700}] ; via_m2m4 [expr {$d0a-1824-100}] -1500
box values [expr {$d0a-1824-128}] -1500 [expr {$d0a-1824-72}] [expr {$YCP-1700}] ; paint metal4

# ===== inter-row sources on M3: PB/p1/p2/pb2 (mirror drain -> cascode source) =====
# PB: PB bar(y+1780) -> MP0ca/MP0cb source(YCP-1500)
foreach cx [list $d0a $d0b] {
    via_m2m3 $cx 1780 ; via_m2m3 $cx [expr {$YCP-1500}]
    box values [expr {$cx-$::M2HW}] 1780 [expr {$cx+$::M2HW}] [expr {$YCP-1500}] ; paint metal3
}
# p2 (split): MP2a/MP2b drains -> MP2ca/MP2cb sources, TWO risers (a single riser
# at the midpoint lands in the gap between the split halves and connects neither).
foreach cx [list $d2a $d2b] {
    via_m2m3 $cx 1500 ; via_m2m3 $cx [expr {$YCP-1500}]
    box values [expr {$cx-$::M2HW}] 1500 [expr {$cx+$::M2HW}] [expr {$YCP-1500}] ; paint metal3
}
# p1/pb2 (single legs): mirror drain(y+1500) -> cascode source(YCP-1500)
foreach {cxm cxc} [list $c1 $d1 $cPB $dBc] {
    via_m2m3 $cxm 1500 ; via_m2m3 $cxc [expr {$YCP-1500}]
    box values [expr {$cxc-$::M2HW}] 1500 [expr {$cxc+$::M2HW}] [expr {$YCP-1500}] ; paint metal3
}

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "PMOS_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<16} {incr i} { drc find ; puts "EB: [box values]" }
}

# ===== ports (6). PB on the PB gate bar (NOT MP1's drain = p1); VDD on the VDD bar
# in a clean gap (avoid the M4-via-stack spot where the label snaps to via2). =====
box values 13072 1760 13128 1800 ; label PB center metal2 ; port make 1
box values 13272 -1520 13328 -1480 ; label VDD center metal2 ; port make 2
box values [expr {$d0b+120}] [expr {$YCP+1760}] [expr {$d0b+176}] [expr {$YCP+1800}] ; label PA center metal2 ; port make 3
box values [expr {$d1-40}] [expr {$YCP+1474}] [expr {$d1+40}] [expr {$YCP+1526}] ; label VGN center metal2 ; port make 4
box values [expr {$d2a+2000}] [expr {$YCP+1474}] [expr {$d2a+2056}] [expr {$YCP+1526}] ; label IB_DIV2 center metal2 ; port make 5
box values [expr {$dBc-40}] [expr {$YCP+1474}] [expr {$dBc+40}] [expr {$YCP+1526}] ; label VBCPD center metal2 ; port make 6
select top cell
save $OUT/$CELL
puts "PMOS_SAVED YCP=$YCP"
quit -noprompt
