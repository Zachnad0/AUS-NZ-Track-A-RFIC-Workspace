#!/usr/bin/env python3
# Generator for DIV2_QUAD_v1.sch (xschem 3.4.8RC) -- CML div-by-2 quadrature cell
# with real NMOS bias mirror off IBIAS and 4x CML->CMOS output converters.
#
# CONVERTER (Phase 3 rework, 2026-08-12): diff-pair front end (unchanged) ->
# AC-couple OC->G1 (CC) -> SELF-BIASED inverter (RFB INVO1->G1, pins G1 at its own
# trip across PVT) -> balanced restore -> 44/16 driver -> R_SER. No absolute
# threshold to match, by construction. Validated at netlist level: TT 142 mVpp /
# 2.500 GHz / 270 deg quadrature; divides at every corner. See docs/div2-debug.md
# (2026-08-12) and team_src/sim/div2/.
#
# Connectivity is by net-name label (lab_pin). Output path is relative to this
# script (portable: runs under container python3 or Windows python).

import io, os
out = io.StringIO()
def emit(s): out.write(s + "\n")

emit("v {xschem version=3.4.8RC file_version=1.3}")
emit("G {}"); emit("K {}"); emit("V {}"); emit("S {}"); emit("F {}"); emit("E {}")

lpn = [0]
def lab(x, y, name):
    lpn[0] += 1
    emit("C {lab_pin.sym} %d %d 0 0 {name=lp%d lab=%s}" % (x, y, lpn[0], name))

# nfet terminal offsets: G(-20,0) D(+20,-30) S(+20,+30) B(+20,0)
# pfet terminal offsets: G(-20,0) D(+20,+30) S(+20,-30) B(+20,0)
def nfet(x, y, name, G, D, S, B, W, L):
    emit("C {symbols/nfet_03v3.sym} %d %d 0 0 {name=%s L=%s W=%s nf=1 model=nfet_03v3 spiceprefix=X}" % (x, y, name, L, W))
    lab(x-20, y, G); lab(x+20, y-30, D); lab(x+20, y+30, S); lab(x+20, y, B)
def pfet(x, y, name, G, D, S, B, W, L):
    emit("C {symbols/pfet_03v3.sym} %d %d 0 0 {name=%s L=%s W=%s nf=1 model=pfet_03v3 spiceprefix=X}" % (x, y, name, L, W))
    lab(x-20, y, G); lab(x+20, y+30, D); lab(x+20, y-30, S); lab(x+20, y, B)
# res.sym / capa.sym share pin geometry: pin1 (A) at (0,-30), pin2 (B) at (0,+30)
def res(x, y, name, A, B, val):
    emit("C {res.sym} %d %d 0 0 {name=%s value=%s footprint=1206 device=resistor m=1}" % (x, y, name, val))
    lab(x, y-30, A); lab(x, y+30, B)
def cap(x, y, name, A, B, val):
    emit("C {capa.sym} %d %d 0 0 {name=%s value=%s m=1}" % (x, y, name, val))
    lab(x, y-30, A); lab(x, y+30, B)

# ================= CML core (12x nfet W=40u L=0.3u), bulk=VSS =================
core = [
 ("MA1","OQ","OIB","nTA"), ("MA2","OQB","OI","nTA"),
 ("MA3","OI","OIB","nLA"), ("MA4","OIB","OI","nLA"),
 ("MA5","CK","nTA","TAILA"), ("MA6","CKB","nLA","TAILA"),
 ("MB1","OIB","OQB","nTB"), ("MB2","OI","OQ","nTB"),
 ("MB3","OQ","OQB","nLB"), ("MB4","OQB","OQ","nLB"),
 ("MB5","CKB","nTB","TAILB"), ("MB6","CK","nLB","TAILB"),
]
x = 0
for nm,G,D,S in core:
    y = 0 if nm.startswith("MA") else 500
    xx = x if nm.startswith("MA") else x-260*6
    nfet(xx, y, nm, G, D, S, "VSS", "40u", "0.3u")
    x += 260

# loads 300R to VDD
res(0,  -400, "RA1", "VDD","OIB","300")
res(260,-400, "RA2", "VDD","OI","300")
res(520,-400, "RB1", "VDD","OQB","300")
res(780,-400, "RB2", "VDD","OQ","300")

# ================= NMOS bias mirror off IBIAS (L=1u), bulk=VSS =================
nfet(0,   1100, "M_BREF",  "IBIAS","IBIAS","VSS","VSS", "4u",  "1u")
nfet(260, 1100, "M_TAILA", "IBIAS","TAILA","VSS","VSS", "40u", "1u")
nfet(520, 1100, "M_TAILB", "IBIAS","TAILB","VSS","VSS", "40u", "1u")

# ================= 4x CML->CMOS self-biased converters =================
# diff-pair front end (NMOS-input, handles CML CM ~2.9V near VDD; move-b: 8u pair)
# -> OC (single-ended, with gain) -> CC ac-couple -> G1 -> self-biased INV1 (RFB)
# -> INV2 balanced -> INV3 44/16 driver -> R_SER 1k. Sizing locked Phase 3.
def buffer(x0, tag, INP, INM, OUT):
    NS="NS_%s"%tag; DN1="DN1_%s"%tag; OC="OC_%s"%tag; G1="G1_%s"%tag
    S1="INVO1_%s"%tag; S2="INVO2_%s"%tag; S3="INVO3_%s"%tag
    # diff pair + current-mirror load
    nfet(x0,    1600, "M_NT_%s"%tag,  "IBIAS", NS,  "VSS", "VSS", "8u", "1u")
    nfet(x0+260,1600, "M_BN1_%s"%tag, INP,     DN1, NS,    "VSS", "8u", "0.3u")
    nfet(x0+520,1600, "M_BN2_%s"%tag, INM,     OC,  NS,    "VSS", "8u", "0.3u")
    pfet(x0+260,1200, "M_BP1_%s"%tag, DN1,     DN1, "VDD", "VDD", "8u", "0.3u")
    pfet(x0+520,1200, "M_BP2_%s"%tag, DN1,     OC,  "VDD", "VDD", "8u", "0.3u")
    # AC coupling + self-bias: CC OC->G1, RFB INVO1->G1 (RFB*CC=2ns, corner 80MHz)
    cap(x0+650, 1400, "CC_%s"%tag,  OC, G1, "100f")
    res(x0+900, 1400, "RFB_%s"%tag, S1, G1, "20k")
    # stage 1: SELF-BIASED inverter, input G1 (10u/4u)
    pfet(x0+780, 1600, "M_IP1_%s"%tag, G1, S1, "VDD","VDD", "10u","0.3u")
    nfet(x0+780, 2000, "M_IN1_%s"%tag, G1, S1, "VSS","VSS", "4u", "0.3u")
    # stage 2: balanced restoring inverter (26u/11u)
    pfet(x0+1040,1600, "M_IP2_%s"%tag, S1, S2, "VDD","VDD", "26u","0.3u")
    nfet(x0+1040,2000, "M_IN2_%s"%tag, S1, S2, "VSS","VSS", "11u","0.3u")
    # stage 3: output driver 44u/16u (pinned Ron), R_SER 1k into pad
    pfet(x0+1300,1600, "M_IP3_%s"%tag, S2, S3, "VDD","VDD", "44u","0.3u")
    nfet(x0+1300,2000, "M_IN3_%s"%tag, S2, S3, "VSS","VSS", "16u","0.3u")
    res(x0+1560, 1800, "R_SER_%s"%tag, S3, OUT, "1k")

buffer(-100,  "IP", "OIB","OI",  "I_P")   # I_P tracks OI
buffer(1400,  "IN", "OI","OIB",  "I_N")
buffer(2900,  "QP", "OQB","OQ",  "Q_P")   # Q_P tracks OQ
buffer(4400,  "QN", "OQ","OQB",  "Q_N")

# ================= ports =================
py = -800
for p in ["CK","CKB","IBIAS"]:
    emit("C {ipin.sym} %d %d 0 0 {name=port_%s lab=%s}" % (2000, py, p, p)); py += 40
for p in ["VDD","VSS"]:
    emit("C {iopin.sym} %d %d 0 0 {name=port_%s lab=%s}" % (2000, py, p, p)); py += 40
for p in ["I_P","I_N","Q_P","Q_N"]:
    emit("C {opin.sym} %d %d 0 0 {name=port_%s lab=%s}" % (2000, py, p, p)); py += 40

dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DIV2_QUAD_v1.sch")
open(dst, "w").write(out.getvalue())
print("wrote", dst, out.getvalue().count("\n"), "lines")
