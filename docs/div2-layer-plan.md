# DIV2_QUAD_v1 — layer / track allocation (1f)

Written before Stage B so the inter-band routing has an explicit per-net-class layer plan.
Six same-layer-crossing shorts have each cost a full LVS run; the rule is: **any horizontal
hop crosses vertical risers on a DIFFERENT layer**, and a resistor's metal1 GUARD RING and a
MIM cap's metal4/metal5 PLATES are OCCUPIED layers. Coordinates in internal units (200/µm).

## Floorplan
- Latch A row @ yA=0, latch B row @ yB=−7000 (both [MA5 MA1 MA3 MA4 MA2 MA6] W40, pitch P=2600).
- Bias row (M_BREF/M_TAILA/M_TAILB) @ x=6P.., ybias=−3500.
- 4 converters (IP/IN/QP/QN) BELOW latch B (each ib_conv_v1 = 54.9×85.8 µm). See Stage B/C.

## Net-class → layer (CML core, PROVEN in Stage A — do not disturb)
| Net class | Layer | Band |
|---|---|---|
| latch outB/out (OI/OIB/OQ/OQB local) | **M3** | y+600 |
| latch nT (M5.d+M1.s+M2.s) | **M4** | y−900 |
| latch nL (M6.d+M3.s+M4.s) | **M5** | y+1150 (hseg 5600..12600; risers 5600/8200/12600) |
| latch TAIL | **M3** | y−750 |
| cross-gate M3.g→out | M3 | y+960 |
| cross-gate M4.g→outB | M4 | y+960 |
| load→out/outB riser | M3 @ x2600/8700 | up to y+2610 |
| load→VDD riser + VDD rail | M4 | y+3384..+3800 |

## Inter-band (Stage A, PROVEN)
| Net | Layer plan |
|---|---|
| OIB (A→MB1.g) | M5 vertical @ x2400 |
| OI (A→MB2.g) | M5 down @ x10400, **JOG to M4** through B-nL M5 hseg (yB+1150), M4 to gate |
| OQ (B→MA1.g) | M5 @ x8700 up, **JOG to M4** through B-nL, M5 gap-hop g1, M5 up @ x2800 |
| OQB (B→MA2.g) | M5 @ x4800 up, **M4 gap-hop g2**, M5 up @ x10600 (crosses OQ's M5 inter-layer) |
| CK (MA5@x0 + MB6@x12500) | M3 stub @ x0, **M3 gap-hop g3=−2400**, M4 stub @ x12500 |
| CKB (MA6@x12300 + MB5@x0) | M4 stub @ x12300, **M4 gap-hop g4=−4600**, M3 stub @ x0 |
| IBIAS (M_BREF.g/d + TAILA/B.g) | **M3 rail** @ gy=ybias+960 (tail M4 risers cross inter-layer) |
| TAILA (M_TAILA.d→A.TAIL) | M4 riser+hseg @ yA−750, x-connect @ 13000 |
| TAILB (M_TAILB.d→B.TAIL) | M4 riser+hseg @ yB−750 |
| VDD | M4 load rails (yA/yB+3800) tied by a left M4 vertical @ x−1000 |
| VSS | **M2 collector plate** over bias (7.5µm, →17µm w/ converters) + M3 bulk spine @ x−1150 + pwell |

## Converter band (Stage B/C — the plan to route against)
Each converter (`place_conv {cx cy tag}`) placed at its own (cx,cy) below latch B. Internal
converter layers are FIXED by ib_conv_v1 (OC=M5, G1=M4, S1=M3, VDD bus M2, RFB guard = M1
guard ring OCCUPIED, CC cap = M4/M5 plates OCCUPIED). Inter-converter → core:
| Net | Source (core) | Layer to the converter INP/INM |
|---|---|---|
| IP.INP=OIB, IP.INM=OI | OIB/OI M3 @ latch A y+600 | drop on **M4** (core outputs are M3; M4 clear below A) to the converter, via to the conv's M2 input gate tie |
| IN.INP=OI, IN.INM=OIB | same, swapped | M4 |
| QP.INP=OQB, QP.INM=OQ | OQB/OQ M3 @ latch B y+600 | M4 |
| QN.INP=OQ, QN.INM=OQB | same, swapped | M4 |
| IBIAS → each conv M_NT.g | IBIAS M3 rail | extend M3 rail down to the converter band |
| VDD → each conv | M4 VDD | extend VDD M4 to a converter VDD spine |
| VSS → each conv | M2 plate | extend the M2 collector plate under the converters (EM: →17µm) |
| OUT (I_P/I_N/Q_P/Q_N) | conv R_SER top | to top-level output ports |

Rule reminders: via stubs sit INSIDE a gate rail (not the edge, or V2.3); use `via_m4m5` at
M4/M5 hops; M5 jog pad needs 92 clearance from a neighbouring M5 hseg (MT.2a); QUERY a rail's
actual extent (leg procs offset gate rails, e.g. M_BREF gate @ x15268..15492, not xbr).

## Stage B/C mechanism — PROVEN (getcell + flatten, not place_conv reparam)
Reparameterising ib_conv_v1's ~100 hardcoded coords by (cx,cy) is too short-error-prone. The
converter is a proven 14-device flat cell (bbox −1360,−2600 .. 9612,14564 = 10972×17164 iu =
54.9×85.8 µm). REUSE IT VERBATIM:
```
box values $bx $by $bx $by ; getcell ib_conv_v1     ;# NO "child" arg (breaks it)
flatten ${CELL}_g ; load ${CELL}_g                  ;# converter geometry pulled in flat
```
Verified in isolation: flatten → DRC 0, extract all → exactly 14 devices. getcell aligns the
cell's bbox-LL (native −1360,−2600) to the box point, so the **effective offset is
(bx+1360, by+2600)**. Native port (px,py) lands at parent (bx+1360+px, by+2600+py). With
OX=bx+1360, OY=by+2600:
| Port | native (px,py,layer) | parent (OX+px, OY+py) |
|---|---|---|
| IBIAS | (−235, 1330, M2) | front-end left |
| INP | (965, 1330, M2) | → OIB |
| INM | (2165, 1330, M2) | → OI |
| VDD | (−1272, 4128, M2) | bus vertical @ OX−1300 |
| VSS | (−1032, −1272, M1) | bus @ OX−1000 |
| OUT | (9176, 7784, M1) | → I_P/I_N/Q_P/Q_N port |
Getcell/flatten must happen in ib_div2_f AFTER CML straps; flatten to ib_div2_g; save writes
ib_div2_g → ib_div2.mag. Routing (in ib_div2_g): the whole band y>3900 over the core+bias
(x −1000..22000) is CLEAR on every layer (core tops at VDD y3800; cross-couple/CK/bias all at
NEGATIVE y) — route the long INP/INM/IBIAS/VDD hauls "up-over-down" on M5 at spaced y-tracks
(≥300 iu apart), tap OIB at its M3 west via x2200 and OI at its east via x10000 (both y600,
clear of the x2600/8700 load risers). VSS: extend the M2 collector plate east to the conv VSS
pin, via_m1m2. Partial golden gains 10th port I_P; conv nets → NS_IP/DN1_IP.. internal,
INP=OIB INM=OI IBIAS=IBIAS VDD=VDD VSS=VSS OUT=I_P.

## Stage B ACTUAL (IP, CLOSED) — corrections to the mechanism above
- Converter is a **hierarchical child**, NOT flattened. A 2nd `flatten` shatters the CML folded
  W40 fets into 147 unmergeable fingers → LVS device-count blows up. `getcell ib_conv_v1`
  (no flatten); netgen auto-flattens the child to compare against the flat golden. Golden built
  by grepping the IP section out of the full `DIV2_QUAD_v1_golden.spice` (`^X\S*_IP `).
- getcell aligns bbox-LL to the box → effective offset (bx+1360, by+2600). IP at bx23500,
  by−3330 (OX24860, OY−730) → front-end pins land at y600, level with latch-A outputs.
- INM pin (native x2165) sits UNDER the CC MiM cap AND the converter's DN1 gate net runs on M4
  right over the pin. Route INM: OI tap M4 → haul → via_m4m5 in the clear gap → M5 down at
  native x1340 (LEFT of cap) → M3 east UNDER the cap to the pin. A straight M4 riser shorts DN1.
- I_P port: PAINT a top-level M1 patch over the child OUT port before `label`+`port make`; a bare
  label lands on empty top metal and reads as a floating net.
- Gate MUST run `PDK=gf180mcuD PDK_ROOT=/foss/pdks verify_cp.sh` (ambient PDK=ihp-sg13g2 breaks
  the netgen setup). NO ext2spice merge needed — netgen combines the folds itself.

## Stage C FLOORPLAN (the gating decision — resolve BEFORE routing)
IP works because it sits BESIDE the core with its front-end (INP/INM/IBIAS + VDD/VSS bus) facing
the core, so all 6 nets are SHORT lateral hops. The other three cannot all do that:
- Tiled same-side (all east): far converters' hauls cross near converters' bodies → the cap
  M4/M5 plates guarantee MIMTM shorts. REJECTED.
- Vertical stacking: no body-crossing, but VSS/VDD/IBIAS then run the full ~17k-iu core height
  across every core net. REJECTED (worse).
- Mirrored side-placement: front-ends face the core → short hauls like IP. Needs mirror for the
  non-east converters.

## ORIENTATION DECISION (item 2, chosen) — option (c): P-east-unmirrored, N-west-mirrored
`sideways` PROVEN (getcell after loading master to warm the tech; mirror-x about bbox centre →
native (px,py) → parent (bx+9612−px, by+2600+py); flatten+extract = 14 clean devices).
**Chosen: I_P & Q_P east UNMIRRORED; I_N & Q_N west MIRRORED (`sideways`).** IP east (done), IN
mirror-west (latch A, by−3330, pins y600), QP east-lower + QN mirror-west-lower (latch B, taps
OQ/OQB at yB+600=−6400, placed low with down-hauls, gapped clear of the upper pair).
**Matching argument:** the four converters are threshold slicers; mirroring shifts a slicer's
input-referred offset systematically (STI stress / well proximity, a few mV) → a phase skew =
offset/slew. The binding spec is I-to-Q quadrature. Option (c) makes the I and Q paths
STRUCTURALLY IDENTICAL (both have P-unmirrored + N-mirrored), so the mirror-induced offset is
common to I and Q and cancels in the I-vs-Q comparison — quadrature is preserved to first order.
It leaves only a small P/N (duty) offset shared by both paths, which is second-order (the
master-slave latch sets ~50% duty) and correctable. Option (d) (east/west split by I-vs-Q) would
put the offset directly on the quadrature axis — rejected. Option (a) (all-unmirrored row below
core) is matching-optimal (zero relative mirror) BUT discards the closed/verified IP Stage B and
needs an unproven down-channel routing scheme; (c) preserves IP, gives every converter a clean
core-facing placement, and preserves the binding quadrature spec — chosen for that balance.
Golden: grep `_IN`/`_QP`/`_QN` from `DIV2_QUAD_v1_golden.spice`, ports I_N/Q_P/Q_N (47→61→75).
Stage D renames cell → DIV2_QUAD_v1, DROPS OI/OIB/OQ/OQB as ports (internal once all 4 tap them);
final 9 ports CK CKB IBIAS I_P I_N Q_P Q_N VDD VSS.
