# ibias_gen_v1.tcl -- FULL 16-device IBIAS block. Four-row stack:
#   NMOS mirror (y=0) | NMOS cascode (y=2000) | PMOS mirror (y=YP) | PMOS cascode (y=YP+4400)
# NMOS side = ib_nmos, PMOS side = ib_pmos (+YP). Cross-routes on M5: PA (NMOS MNC2 drain
# <-> PMOS MP0c gate/drain) and VBCPD (NMOS MNB drain <-> PMOS MP2c gate + MPBc).
# Ports: IBIAS VGP VGN IB_DIV2 VDD VSS. (NB, PB, PA, VBCPD are internal.)
source /foss/designs/AUS-NZ-integration/team_src/magic/phase5/ib_block.tcl
set OUT  /foss/designs/AUS-NZ-integration/team_src/magic
set CELL ibias_gen_v1
set YC 2000 ; set YP 6000 ; set YCP 4400

drc off ; snap internal
cellname create $CELL ; load $CELL

# ---- NMOS x-centers (ib_nmos) ----
set cMN0 6400
set cMN1 [expr {$cMN0 + 6048 + 1260 + 560}]
set cMN2 [expr {$cMN1 + 1260 + 6048 + 560}]
set cMNB [expr {$cMN2 + 6048 +  504 + 560}]
set cDL  [expr {$cMN0 - 6048 -  504 - 560}]
set cDR  [expr {$cMNB +  504 +  504 + 560}]
# ---- PMOS x-centers (ib_pmos) ----
set c0a 3400
set c0b [expr {$c0a + 3024 + 3024 + 560}]
set p1c [expr {$c0b + 3024 + 1260 + 560}]
set c2a [expr {$p1c + 1260 + 3024 + 560}]
set c2b [expr {$c2a + 3024 + 3024 + 560}]
set cCD [expr {$c2b + 3024 + 1512 + 560}]
set cPB [expr {$cCD + 1512 +  504 + 560}]

# ===== place all devices =====
place_nfet  2 $cDL DL ; place_nfet 24 $cMN0 MN0 ; place_nfet 5 $cMN1 MN1
place_nfet 24 $cMN2 MN2 ; place_nfet 2 $cMNB MNB ; place_nfet 2 $cDR DR
place_nfet 24 $cMN0 MNC0 1 $YC ; place_nfet 5 $cMN1 MNC1 1 $YC ; place_nfet 24 $cMN2 MNC2 1 $YC
place_pfet 12 $c0a MP0a $YP ; place_pfet 12 $c0b MP0b $YP ; place_pfet 5 $p1c MP1 $YP
place_pfet 12 $c2a MP2a $YP ; place_pfet 12 $c2b MP2b $YP ; place_pfet 6 $cCD MPCD $YP ; place_pfet 2 $cPB MPB $YP
set YPC [expr {$YP+$YCP}]
place_pfet 12 $c0a MP0ca $YPC 1 ; place_pfet 12 $c0b MP0cb $YPC 1 ; place_pfet 5 $p1c MP1c $YPC 1
place_pfet 12 $c2a MP2ca $YPC 1 ; place_pfet 12 $c2b MP2cb $YPC 1 ; place_pfet 2 $cPB MPBc $YPC 1
flatten ${CELL}_f ; load ${CELL}_f

# ===== strap =====
foreach {nf cx} [list 2 $cDL 24 $cMN0 5 $cMN1 24 $cMN2 2 $cMNB 2 $cDR] { nfet_leg $nf $cx 1 }
nfet_leg 24 $cMN0 1 1 $YC 0 ; nfet_leg 5 $cMN1 1 1 $YC 0 ; nfet_leg 24 $cMN2 1 1 $YC 0
foreach {nf cx} [list 12 $c0a 12 $c0b 5 $p1c 12 $c2a 12 $c2b 6 $cCD 2 $cPB] { pfet_leg $nf $cx 1 2 $YP }
foreach {nf cx} [list 12 $c0a 12 $c0b 5 $p1c 12 $c2a 12 $c2b 2 $cPB] { pfet_leg $nf $cx 1 1 $YPC 1 -1700 }

# ===== NMOS routing (ib_nmos) =====
box values -1560 -820 31660 [expr {$YC+700}] ; paint pwell
set nxL [expr {$cDL - 504 - 210}] ; set nxR [expr {$cDR + 504 + 40}]
box values $nxL 932 $nxR 988   ; paint metal2
box values $nxL -628 $nxR -572 ; paint metal2
box values [expr {$cMN0-28}] 572 [expr {$cMN0+28}] [expr {$YC-572}] ; paint metal2
foreach cx [list $cDL $cDR] { box values [expr {$cx-28}] -628 [expr {$cx+28}] 628 ; paint metal2 }
box values [expr {$cMN0-3648-210}] [expr {$YC+932}] [expr {$cMN2+3648+40}] [expr {$YC+988}] ; paint metal2
box values [expr {$cMN0-28}] [expr {$YC+572}] [expr {$cMN0+28}] [expr {$YC+988}] ; paint metal2
foreach cx [list $cMN1 $cMN2] {
    via_m2m3 $cx 600 ; via_m2m3 $cx [expr {$YC-600}]
    box values [expr {$cx-$::M2HW}] 600 [expr {$cx+$::M2HW}] [expr {$YC-600}] ; paint metal3
}

# ===== PMOS routing (ib_pmos, +YP) =====
set pxL [expr {$c0a - 3024 - 210}] ; set pxR [expr {$cPB + 504 + 40}]
box values $pxL [expr {$YP-1528}] $pxR [expr {$YP-1472}] ; paint metal2
box values $pxL [expr {$YP+1752}] [expr {$cCD+1512-260}] [expr {$YP+1808}] ; paint metal2
foreach cx [list $c0a $c0b] { box values [expr {$cx-28}] [expr {$YP+1472}] [expr {$cx+28}] [expr {$YP+1808}] ; paint metal2 }
box values [expr {$c2a+3024}] [expr {$YP+1472}] [expr {$c2b-3024}] [expr {$YP+1528}] ; paint metal2
box values [expr {$cCD-28}] [expr {$YP-1528}] [expr {$cCD+28}] [expr {$YP+1528}] ; paint metal2
box values [expr {$cPB-28}] [expr {$YP+1472}] [expr {$cPB+28}] [expr {$YP+1808}] ; paint metal2
# cascode gate bars PA / VBCPD
box values [expr {$c0a-1824-210}] [expr {$YPC+1752}] [expr {$p1c+1260-260}] [expr {$YPC+1808}] ; paint metal2
box values [expr {$c2a-1824-210}] [expr {$YPC+1752}] [expr {$cPB+504-260}] [expr {$YPC+1808}] ; paint metal2
foreach cx [list $c0a $c0b] { box values [expr {$cx-28}] [expr {$YPC+1472}] [expr {$cx+28}] [expr {$YPC+1808}] ; paint metal2 }
box values [expr {$c2a+1824}] [expr {$YPC+1472}] [expr {$c2b-1824}] [expr {$YPC+1528}] ; paint metal2
box values [expr {$cPB-28}] [expr {$YPC+1472}] [expr {$cPB+28}] [expr {$YPC+1808}] ; paint metal2
# PMOS VDD tap rail (YPC-1700) + M4 riser to PMOS VDD bar (YP-1500)
box values [expr {$c0a-1824-210}] [expr {$YPC-1728}] [expr {$cPB+504+40}] [expr {$YPC-1672}] ; paint metal2
via_m2m4 [expr {$c0a-1824-100}] [expr {$YPC-1700}] ; via_m2m4 [expr {$c0a-1824-100}] [expr {$YP-1500}]
box values [expr {$c0a-1824-128}] [expr {$YP-1500}] [expr {$c0a-1824-72}] [expr {$YPC-1700}] ; paint metal4
# inter-row PB/p1/p2/pb2 on M3
foreach cx [list $c0a $c0b] {
    via_m2m3 $cx [expr {$YP+1780}] ; via_m2m3 $cx [expr {$YPC-1500}]
    box values [expr {$cx-$::M2HW}] [expr {$YP+1780}] [expr {$cx+$::M2HW}] [expr {$YPC-1500}] ; paint metal3
}
foreach cx [list $c2a $c2b] {
    via_m2m3 $cx [expr {$YP+1500}] ; via_m2m3 $cx [expr {$YPC-1500}]
    box values [expr {$cx-$::M2HW}] [expr {$YP+1500}] [expr {$cx+$::M2HW}] [expr {$YPC-1500}] ; paint metal3
}
foreach {cxm cxc} [list $p1c $p1c $cPB $cPB] {
    via_m2m3 $cxm [expr {$YP+1500}] ; via_m2m3 $cxc [expr {$YPC-1500}]
    box values [expr {$cxc-$::M2HW}] [expr {$YP+1500}] [expr {$cxc+$::M2HW}] [expr {$YPC-1500}] ; paint metal3
}

# ===== cross-routes on M5 (L-shaped): PA and VBCPD, NMOS <-> PMOS =====
# PA: NMOS MNC2 drain (cMN2, YC+600) -> PMOS PA bar (c0b, YPC+1780). Verticals run to
# the TOP of the horizontal (+M5HW) so the L-corner has no sub-88 M5 notch (MT.1).
via_m2m5 $cMN2 [expr {$YC+600}] ; via_m2m5 $c0b [expr {$YPC+1780}]
box values [expr {$cMN2-$::M5HW}] [expr {$YC+600-$::M5HW}] [expr {$cMN2+$::M5HW}] [expr {$YPC+1780+$::M5HW}] ; paint metal5
box values [expr {$c0b-$::M5HW}] [expr {$YPC+1780-$::M5HW}] [expr {$cMN2+$::M5HW}] [expr {$YPC+1780+$::M5HW}] ; paint metal5
# VBCPD: NMOS MNB drain (cMNB, y600) -> PMOS VBCPD bar (cPB, YPC+1780)
via_m2m5 $cMNB 600 ; via_m2m5 $cPB [expr {$YPC+1780}]
box values [expr {$cMNB-$::M5HW}] [expr {600-$::M5HW}] [expr {$cMNB+$::M5HW}] [expr {$YPC+1780+$::M5HW}] ; paint metal5
box values [expr {$cPB-$::M5HW}] [expr {$YPC+1780-$::M5HW}] [expr {$cMNB+$::M5HW}] [expr {$YPC+1780+$::M5HW}] ; paint metal5

select top cell
drc on ; drc euclidean on ; drc check ; drc catchup
puts "IB_DRC=[drc list count total]"
if {[drc list count total] > 0} {
    puts "WHY: [drc list why]"
    for {set i 0} {$i<20} {incr i} { drc find ; puts "EB: [box values]" }
}

# ===== ports (6) =====
box values 12700 [expr {$YC+940}] 12756 [expr {$YC+980}] ; label IBIAS center metal2 ; port make 1
box values [expr {$cMN1-40}] [expr {$YC+574}] [expr {$cMN1+40}] [expr {$YC+626}] ; label VGP center metal2 ; port make 2
box values [expr {$p1c-40}] [expr {$YPC+1474}] [expr {$p1c+40}] [expr {$YPC+1526}] ; label VGN center metal2 ; port make 3
box values [expr {$c2a+2000}] [expr {$YPC+1474}] [expr {$c2a+2056}] [expr {$YPC+1526}] ; label IB_DIV2 center metal2 ; port make 4
box values 13272 [expr {$YP-1520}] 13328 [expr {$YP-1480}] ; label VDD center metal2 ; port make 5
box values 12700 -620 12756 -580 ; label VSS center metal2 ; port make 6
select top cell
save $OUT/$CELL
puts "IB_SAVED"
quit -noprompt
