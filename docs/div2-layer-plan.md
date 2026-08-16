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
