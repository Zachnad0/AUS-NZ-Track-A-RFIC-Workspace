# `signoff/pex/ib_conv_v1/resim.md` — PEX re-simulation in the DIV2 bench

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)** · 2026-09-11, at `2df615e`.

Review-condition item 3, second half: re-simulate with the extracted netlist. This is the
`ib_conv_v1` result. `CP_v1`'s is in `../README.md` (49-point DC match, ±0.076 pp).

## Decks and invocation

Generated from `team_src/sim/div2/div2_sb_TT.spice` by replacing the four inline converter
chains with four subckt instances, mapping per the DIV2 instance order
(`IP: INP=OIB INM=OI OUT=I_P`, `IN: OI/OIB/I_N`, `QP: OQB/OQ/Q_P`, `QN: OQ/OQB/Q_N`), and
adding a 0 V ammeter in each converter's VSS return.

| deck | converters | purpose |
|---|---|---|
| `div2_ideal.spice` | 4 × `ib_conv_v1_ideal` | control (a), restructure-only |
| `div2_sch.spice` | 4 × `ib_conv_v1` (golden) | **control (b), the item-3 reference** |
| `div2_mix.spice` | I_P PEX, other three golden | one-converter PEX |
| `div2_all.spice` | 4 × `ib_conv_v1_pex` | all-four PEX |

Decks are committed at `signoff/pex/ib_conv_v1/decks/`. Run in-container from a scratch
copy of that directory (they write .dat files beside themselves):

```
ngspice -b div2_sch.spice      # set num_threads=2 is in-deck
awk -v CORNER=TT -f team_src/sim/div2/analyze.awk sch_quad.dat
```

`set num_threads=2` is set **in the `.control` block**: `OMP_NUM_THREADS` is ignored by this
ngspice build (user time stayed at 3m20s against 25 s wall until the in-deck setting was added).

Three deck fixes were required and are not circuit changes: the golden needs
`.lib … mimcap_typical` and `.lib … res_typical` (absent from the original bench, which used
ideal passives); the internal probe moves from `x1.INVO3_IP` to `x1.x_conv_ip.s3`; and for the
PEX converter it moves again to `x1.x_conv_ip.a_8030_n1600.t1`, the INV3 output net
(magic's name for the golden's `S3`). `meas`'s two-node form `v(a,b)` is not accepted by this
build, so the VSS drop is taken from a second `wrdata` and reduced in post.

## Control (a): the restructure is lossless

| metric | recorded TT | control (a) |
|---|---:|---:|
| I_P swing | 142 mVpp | **142 mVpp** |
| f_out | 2.500 GHz | **2.500 GHz** |
| duty | 48.8 % | **48.8 %** |
| I/Q phase | 270.0° | **270.0°** |
| supply | 22.4 mA | 22.387 mA |

Lifting the inline chain verbatim into a subckt reproduces the recorded baseline exactly. The
restructuring introduces nothing.

## BENCH FIDELITY: the recorded TT baseline was measured with IDEAL passives

The bench's inline chain uses `CC 100f`, `RFB 20k`, `R_SER 1k` as ideal elements. The golden
`ib_conv_v1` uses the modelled devices actually drawn: `cap_mim_2f0_m4m5_noshield`
(`c_width=5u c_length=10u`) and two `ppolyf_u_1k`. Nominal values agree; the models do not.

| metric | (a) ideal | (b) modelled | shift |
|---|---:|---:|---:|
| I_P swing | 142 mVpp | 131 mVpp | **−7.7 %** |
| duty | 48.8 % | 49.5 % | +1.4 % |
| supply | 22.387 mA | 22.118 mA | −1.3 % |
| f_out, I/Q | 2.500 GHz, 270.0° | 2.500 GHz, 270.0° | 0 |

**The headline 142 mVpp in `team_src/sim/div2/README.md` is an ideal-passive number.** With the
drawn passives the same circuit gives 131 mVpp. Control (b) is therefore the reference for the
PEX comparison, not 142.

## PEX result

All three runs are **settled**: the envelope is flat from 12 ns to 20 ns in every case, so these
are steady states, not incomplete settling. (Checked explicitly because
`team_src/sim/div2/README.md` notes some corners settle at 24–28 ns while this deck stops at 20.)

| metric | (b) golden ref | I_P PEX only | all-four PEX | Δ mix | Δ all |
|---|---:|---:|---:|---:|---:|
| **I_P swing** | 131 mVpp | **25 mVpp** | **25 mVpp** | **−80.9 %** | **−80.9 %** |
| I_N / Q_P / Q_N swing | 131 mVpp | 131 mVpp | **25 mVpp** | 0 % | **−80.9 %** |
| f_out | 2.500 GHz | 2.500 GHz | 2.500 GHz | 0 | 0 |
| duty | 49.5 % | **63.9 %** | **63.8 %** | **+29.1 %** | **+28.9 %** |
| I/Q phase | 270.0° | **290.7°** | 270.0° | **+7.7 %** | 0 |
| INV3 output span | −31…2998 mV | 2079…2677 mV | 2088…2677 mV | — | — |
| rise / fall (INV3, 20–80 %) | 40.69 / 35.19 ps | **undefined** | **undefined** | — | — |
| VSS current, I_P | 2.9735 mA | **2.7249 mA** | **2.7212 mA** | **−8.36 %** | **−8.48 %** |
| VSS current, I_N | 2.9735 mA | 2.9754 mA | **2.7212 mA** | +0.06 % | **−8.48 %** |
| VSS current, Q_P | 2.9732 mA | 2.9732 mA | **2.7212 mA** | 0 % | **−8.47 %** |
| VSS current, Q_N | 2.9735 mA | 2.9747 mA | **2.7212 mA** | +0.04 % | **−8.48 %** |
| supply | 22.118 mA | 22.717 mA | **24.496 mA** | +2.71 % | **+10.75 %** |
| runtime | 32.5 s | 52.1 s | 2 m 04 s | — | — |

**Flagged, >5 %:** I_P swing (−80.9 %), duty (+29.1 %), I/Q phase in the mixed run (+7.7 %),
per-converter VSS current (−8.4 %), and total supply in the all-four run (+10.75 %).

Rise and fall are **undefined** in both PEX runs, not slow: the INV3 output no longer crosses
the 20 % and 80 % thresholds of a 0–3.3 V swing. It sits between 2079 mV and 2677 mV.

In the mixed run only the PEX converter degrades; the three golden converters are unchanged to
within 0.06 %. In the all-four run all four degrade identically and the I/Q phase returns to
270.0°, symmetry being restored because every chain is affected the same way.

### VSS port-to-internal-node voltage, PEX converter

Across the 12 device-terminal nodes of the extracted VSS net, over 16–20 ns:

| | worst node | average | peak |
|---|---|---:|---:|
| I_P PEX only | `VSS.t3` | 33.68 mV | 58.50 mV |
| all-four PEX | `VSS.t3` | 33.51 mV | 58.19 mV |

The 12 nodes span 0.87 mV to 33.68 mV average. They are **not** tied together in the wrapper;
tying them would remove exactly this drop.

## Diagnosis, 2026-09-11

Three checks, in order. The first two came back clean, which rules out whole classes of cause.

**1. Topology and connectivity are correct.** Collapsing all 526 parasitic resistors by
union-find (keeping the 14 devices, dropping the 70 parasitic caps) leaves **13 distinct nodes**
— the same count as the golden — and netgen reports **"Circuits match uniquely"** against
`ib_conv_v1_golden.spice`. The only device-terminal nodes with exactly one connection are
`IBIAS`, `INP`, `INM` and `OUT`, which are the four signal ports and are supposed to have one
internal connection each. **No dangling terminal, no mis-extraction.**

**2. Every device and passive parameter is identical to the golden.**

| device | golden | extracted |
|---|---|---|
| 11 MOSFETs | W8/L1; W8, W8, W8, W8 at L0.3; W10, W4, W26, W11, W44, W16 | **all match** |
| `cap_mim_2f0_m4m5_noshield` | `c_width=5u c_length=10u` = 2 fF/µm² × 50 µm² = **100 fF** | **identical** |
| `ppolyf_u_1k` (RFB) | `r_width=2u r_length=40.04u` | **identical** |
| `ppolyf_u_1k` (RSER) | `r_width=2u r_length=2u` | **identical** |

The earlier spot-check covered MOSFETs only; this covers the passives too. Nothing is mis-sized.

**3. The self-bias holds; the node that leaves its trip point is `S2`, the INV3 input.**
Averages over 16–20 ns, against a ~1650 mV trip point (VDD/2):

| node | role | average | vs trip |
|---|---|---:|---:|
| `G1` (`a_1676_7176`) | INV1 input, RFB self-bias node | 1577.9 mV | −72 mV |
| `S1` (`a_2156_7176`) | INV1 out / INV2 in | 1577.9 mV | −72 mV |
| **`S2`** (`a_6430_n1100`) | **INV2 out / INV3 in** | **862.9 mV** | **−787 mV** |
| `S3` (`a_8030_n1600`) | INV3 out | 2440.6 mV | +791 mV |

`G1` and `S1` are equal to the digit, which is the `RFB` self-bias doing its job — it ties
`G1` to `S1`, and it holds. The chain departs at **`S2`**. Per-nanosecond bins show `S2`
oscillating for the first 2 ns and then settling to 840–880 mV from 3 ns onward, flat thereafter.

**`uic` is not the cause.** Re-running the identical deck with `uic` removed gives results
identical to the digit: I_P 25 mVpp, duty 63.9 %, I/Q 290.7°, `G1` 1577.9, `S1` 1577.9,
`S2` 862.9, `S3` 2440.6 mV, I_P VSS current 2.72489 mA. The 20 ns stop is likewise excluded, the
envelope being flat from 12 ns.

The no-`uic` run also emits `Warning: singular matrix: check node
x1.x_conv_ip.m1_3129_7189#` — a metal1 island connected only through a 0.00196 fF parasitic cap,
so it has no DC path. That is ordinary for an extracted view and is not the collapse.

### Cause test 2026-09-11: parasitic C on the self-bias chain is NOT the cause

**Parasitic capacitance per node**, summed after collapsing the R network, against the gate
capacitance on the same node. Cox is computed from the PDK's own `nfet_03v3_tox = 8e-009` and
`pfet_03v3_tox = 7.9e-009` (4.31 and 4.37 fF/µm²).

| node | parasitic C | gate C on that node | parasitic as % of gate | top three contributors |
|---|---:|---:|---:|---|
| `INP` | 0.960 fF | 10.3 fF (W8 nfet) | 9.3 % | C8 0.724→VSS, C68 0.160→VSS, C1 0.039→VDD |
| `G1` | 3.870 fF | 18.3 fF (W10 p + W4 n) | 21.1 % | C20 2.600→VSS, C23 0.842→VSS, C21 0.209→VSS |
| `S1` | 6.516 fF | 48.3 fF (W26 p + W11 n) | 13.5 % | C28 1.983→VSS, C25 1.829→VSS, C29 0.835→VSS |
| `S2` | 10.568 fF | 78.4 fF (W44 p + W16 n) | 13.5 % | C17 3.234→VSS, C18 2.470→VSS, C14 1.680→VSS |
| `S3` | 9.422 fF | none (drives RSER) | — | C32 4.681→VSS, C34 2.558→VSS, C33 1.930→VSS |

Every parasitic total is a small fraction of the gate load already present, and essentially all
of it is to VSS.

**Two runs, and both refute the capacitive-loading hypothesis.**

| run | change | I_P swing | duty | I/Q | INV3 span | I_P VSS |
|---|---|---:|---:|---:|---|---:|
| golden reference | — | 131 mVpp | 49.5 % | 270.0° | −31…2998 mV | 2.9735 mA |
| PEX (unmodified) | — | 25 mVpp | 63.9 % | 290.7° | 2079…2677 mV | 2.7249 mA |
| **A** | PEX, all 12 parasitic caps on `G1`+`S1` removed (10.39 fF) | **39 mVpp** | 66.1 % | 292.3° | 1757…2675 mV | 2.8435 mA |
| **B** | golden + one lumped **6.516 fF** at `S1` | **130 mVpp** | 50.3 % | 267.8° | −19…2990 mV | 3.0283 mA |

**A does not recover and B does not collapse.** Removing the entire parasitic capacitance from
both self-bias nodes buys **14 mVpp of a 106 mVpp deficit (13 %)**; the output is still 70 %
down. Adding the full extracted `S1` capacitance to the golden costs **1 mVpp (0.8 %)**.

**The hypothesis that the cause is INV1's drive against the extracted load on `S1` is therefore
refuted.** Capacitive loading of the self-bias chain accounts for at most an eighth of the
degradation, and the single node it would act through is demonstrably insensitive.

### Resistive test 2026-09-11: the cause is resistive, and it is the VDD network

**Parasitic R inventory.** 526 resistors, 71,065.522263 Ω total, largest single element
22,187.7 Ω. Identical count, sum and maximum in the `.option scale=5n` and `scale off`
netlists, confirming `scale` does not touch resistor values.

| net class | count | ΣR |
|---|---:|---:|
| VSS | 476 | 59,903.732 Ω |
| VDD | 17 | 8,343.562 Ω |
| signal (S2, S1, DN1, G1, INM, INP, S3, NS, OC, OUT) | 32 | 1,838.399 Ω |
| IBIAS | 1 | 79.774 Ω |

Largest five: R21 22,187.7 Ω (VSS.t4–VSS.n166), R22 18,727.5 (VSS.n165–VSS.n164),
R23 7,638.22 (VSS.n164–VSS.t8), R24 4,092.47 (VSS.n169–VSS.n166), R4 4,010.79
(VDD.n0–VDD.t4).

**Run C and the bisect.** One run each, all parasitic C kept throughout.

| run | R collapsed | count | ΣR collapsed | I_P swing | recovered |
|---|---|---:|---:|---:|---:|
| PEX, unmodified | none | 0 | — | 25 mVpp | — |
| **VDD only** | VDD net | **17** | 8,344 Ω | **94 mVpp** | **69 of 106 mVpp** |
| signal only | signal + IBIAS | 33 | 1,918 Ω | 38 mVpp | 13 mVpp |
| **VSS only** | VSS net | **476** | **59,904 Ω** | **25 mVpp** | **0** |
| all | everything | 526 | 71,066 Ω | 109 mVpp | 84 mVpp |
| golden reference | — | — | — | 131 mVpp | — |

**The VDD network carries it.** Seventeen resistors totalling 8.3 kΩ recover 65 % of the
deficit. The 476-resistor, 59.9 kΩ VSS mesh recovers **nothing at all** — its total resistance
is seven times VDD's, but it is a mesh with parallel paths, so its series contribution is small.
Collapsing everything reaches 109 mVpp; the residual 22 mVpp to 131 is the parasitic
capacitance, consistent with the 14 mVpp measured in run A.

### VDD port-to-internal-node drop, which had never been measured

Over 16–20 ns, against the VDD port:

| node | average | peak |
|---|---:|---:|
| `VDD.t5` | **165.33 mV** | 182.78 mV |
| `VDD.t4` | 80.72 mV | **200.17 mV** |
| `VDD.t2` | 73.69 mV | 130.86 mV |
| `VDD.t3` | 71.84 mV | 88.92 mV |
| `VDD.t9` | 24.53 mV | 30.72 mV |
| `VDD.t8` | 22.05 mV | 48.04 mV |
| `VDD.t7` | 13.02 mV | 18.26 mV |
| `VDD.t1` | 12.58 mV | 17.63 mV |
| `VDD.t6` | 8.18 mV | 17.11 mV |
| `VDD.t0` | 2.83 mV | 4.10 mV |

For comparison the worst VSS node is `VSS.t3` at 33.68 mV average, 58.50 mV peak.

**`VDD.t4` and `VDD.t5` are the two supply terminals of `X2`** —
`X2 a_8030_n1600.t0 a_6430_n1100.t3 VDD.t5 VDD.t4 pfet_03v3 w=44u l=0.3u`, the **W44 INV3
pfet**, the widest device in the cell. Its source sees 165 mV of average droop and its bulk
200 mV of peak droop on a 3.3 V supply.

### Geometry 2026-09-11: what the VDD resistance physically is

Node coordinates from `ib_conv_v1_flat.res.ext` (cell internal units, 200 iu/um; `VDD.n2` sits
at x -1300, which is `xVDDbus`), read back against `gds/ib_conv_v1.gds`.

**The 17 VDD resistors are two populations.**

| | resistors | sum | what they are |
|---|---|---:|---|
| **bulk / nwell** | R4 4,010.79, R5 2,510.79, R6 1,177.45 | 7,699 ohm | nwell tap to pfet **body** |
| **supply metal** | R19 1.68, R18 2.84, R12 14.46, R8 41.94 and the rest | 645 ohm | M2 bus to M1 strap to source |

**R4 is a well resistance, not a routing resistance.** `X2` is
`a_8030_n1600.t0 a_6430_n1100.t3 VDD.t5 VDD.t4 pfet_03v3 w=44u` - drain, gate, **source**,
**bulk** - so `VDD.t4` is the pfet body. The magic tech gives
`resist (nwell,dnwell)/well 1000000` **milliohms** per square = **1000 ohm/sq**, and
4,010.79 ohm is **4.01 squares of nwell** between the tap (`VDD.n0`, a COMP 4.200 x 1.200 um
patch at y 71.32-72.52 with one Via1 up to the M2 bus) and the device body. R5 (W26) and R6
(W10) are the same structure on INV2 and INV1 and scale with device length.
**Consistent with the tech: real, and it is the `nwell` class.**

**A bulk path carries no DC current**, so those three kilo-ohm elements are not the mechanism.

**The mechanism is the supply metal, and it reconciles exactly.** The INV3 source path
`VDD -> n4 -> n2 -> n0 -> t5` is R19 + R18 + R12 + R8 = **60.92 ohm**. At the measured converter
current of 2.7249 mA that is **166.0 mV**, against a measured `VDD.t5` droop of **165.33 mV**:
agreement to **0.4 %**. The droop is I x R of the extracted supply metal.

**The geometry that produces it**, all four devices measured:

| device | nf | COMP | contacts | contact span | M1 strap |
|---|---:|---|---:|---:|---|
| INV3 pfet W44 | **1** | 1.180 x 44.000 um | 186 | 98.8 % | **0.230 um** wide, 97.7 % of finger |
| INV3 nfet W16 | **1** | 1.180 x 16.000 | 68 | 98.3 % | 0.230 um, 99.3 % |
| INV2 pfet W26 | **1** | 1.180 x 26.000 | 110 | 98.5 % | 0.230 um, 96.1 % |
| INV2 nfet W11 | **1** | 1.180 x 11.000 | 46 | 96.0 % | 0.230 um, 99.0 % |

**Contacting is not the problem**: every device is contacted over 96-99 % of its finger, 186
contacts on the W44. **Every device is `nf = 1`**, the INV3 pfet drawn as a single 44 um finger,
and each source strap is **0.230 um of metal1** over the full length. At the tech's
`resist (allm1)/metal1 90` milliohms/sq that strap alone is 43 um / 0.23 um = 187 squares =
**16.8 ohm**, fed by a 0.600 um M2 bus running 47.1 um.

**Consistent, therefore real, not an extraction artifact.** Both populations reproduce from the
tech sheet values on the drawn geometry: the kilo-ohm elements from `nwell` at 1000 ohm/sq, the
tens-of-ohms elements from `metal1`/`metal2` at 90 milliohms/sq over narrow straps. No layer
class produces a number the geometry does not support.

**What this establishes and what it does not.** The degradation is resistive, and the VDD
network is the group that carries it; the VSS mesh contributes none of it. That the largest
drops land on the W44 INV3 pfet's supply terminals is measured, not inferred. No claim is made
here about what in the layout produces that VDD resistance, and no design change is proposed.

**What remains.** Topology, parameters, `uic`, the run length, and capacitive loading of the
self-bias chain are all excluded. What has not
been separated is whether the extracted parasitics themselves (the 526 R and 70 C, in particular
around INV2 and its supply returns) are enough to park `S2` low, or whether something in the
bench's treatment of the extracted converter is at fault. No claim either way.

## What is reported and what is not

These are measurements. No cause is asserted here beyond what was measured: the extracted
converter settles to a state in which its INV3 output does not reach the rails, its output swing
is 25 mVpp against the schematic's 131 mVpp, and it draws 8.4 % less VSS current. Whether that
originates in the extracted VSS network, the self-bias path through the extracted `RFB`, the
20 ns stop, or the `uic` start has **not** been isolated, and no such claim is made.

The DIV2 core remains schematic in every run; only the converters change.
