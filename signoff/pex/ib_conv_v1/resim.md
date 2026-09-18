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
| **PEX rebuilt at `9614947`** | none — real VDD relayout | — | — | **29 mVpp** | **4 of 106 mVpp** |

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

## Re-run 2026-09-17: R+C with the `9614947` VDD fix

Only the **R+C case** was re-run — `div2_mix.spice`, the deck the 25 mVpp and 94 mVpp rows
above were both measured on (`div2_run_vdd` is likewise a mix deck: I_P extracted, the other
three golden). The schematic and C-only cases were not re-run; their numbers stand.

**What changed:** the converter's PEX netlist, rebuilt from `gds/ib_conv_v1.gds` at commit
`9614947` (item 23 VDD fix: M3 plate 2.36 um over the M2 spine, 80 via2 stitch cuts, inverter
bus taps 1 -> 3 via1 cuts). Deck, `.meas` statements, `tran 0.2p 20n uic`, `set num_threads=2`
and the golden converters are all unchanged. Netlist 14 devices / 136 C / **625 R**
(was 14 / 70 / 526); the VDD net goes **17 -> 116** resistors and **0 -> 33** independent
loops, while the **VSS net is byte-identical** at 476 R / 59,903.732 ohm.

| metric | (b) golden ref | old PEX (2026-09-11) | **PEX at `9614947`** | vs golden | vs old PEX |
|---|---:|---:|---:|---:|---:|
| **I_P swing** | 131 mVpp | 25 mVpp | **29 mVpp** | **−77.9 %** | **+4 mVpp** |
| I_N / Q_P / Q_N swing | 131 mVpp | 131 mVpp | 131 mVpp | 0 % | 0 |
| f_out | 2.500 GHz | 2.500 GHz | **2.500 GHz** | 0 | 0 |
| duty | 49.5 % | 63.9 % | **64.5 %** | +30.3 % | +0.6 pp |
| I/Q phase | 270.0° | 290.7° | **289.6°** | +7.3 % | −1.1° |
| INV3 output span | −31…2998 mV | 2079…2677 mV | **1989…2687 mV** | — | span 598 → 698 mV |
| VSS current, I_P | 2.9735 mA | 2.7249 mA | **2.8204 mA** | **−5.15 %** | **+0.0955 mA** |
| VSS current, I_N | 2.9735 mA | 2.9754 mA | 2.9754 mA | +0.06 % | 0 |
| VSS current, Q_P | 2.9732 mA | 2.9732 mA | 2.9732 mA | 0 % | 0 |
| VSS current, Q_N | 2.9735 mA | 2.9747 mA | 2.9747 mA | +0.04 % | 0 |
| supply | 22.118 mA | 22.717 mA | **22.791 mA** | +3.04 % | +0.074 mA |
| runtime | 32.5 s | 52.1 s | **74 s** | — | — |

Settled: the I_P envelope is flat to 0.03 mV from 10 ns to 20 ns (87.09…116.41 mV in every
2 ns bin from 10 ns on), so this is a steady state. The three golden converters reproduce the
2026-09-11 mix run **to the digit** (2.9754 / 2.9732 / 2.9747 mA), which is the bench control.

**The result against the three references: 25 → 29 mVpp, against a 94 mVpp all-VDD-R-zeroed
ceiling and a 131 mVpp schematic.** The fix recovers **4 of the 106 mVpp deficit (3.8 %)**, and
**4 of the 69 mVpp (5.8 %)** that removing the VDD resistance entirely is shown above to buy.
**Item 23 is not closed by this.** The direction is right and nothing regressed, but the
magnitude is what §6 of `docs/layout-review-sep01.md` predicted from the resistance change
alone: cumulative port-to-source R fell only 10.2 / 12.2 / 12.7 % (INV1/INV2/INV3), and a
~13 % cut against a ceiling that needs R → 0 cannot move the swing far.

**The supply current moved much more than the swing.** I_P's VSS return recovers
**38 % of its deficit** (2.7249 → 2.8204 against 2.9735) while the output swing recovers 3.8 %.
The extracted converter still parks its INV3 output mid-rail — the span is 1989…2687 mV, up
from 2079…2677 mV but nowhere near the golden's −31…2998 mV — so rise/fall remain undefined
against 20/80 % thresholds. Whatever holds `S2` low survives a 13 % reduction in VDD
resistance.

*Derived, not measured in this deck:* the INV3-source droop implied by the extracted R and the
measured current is 53.19 Ω × 2.8204 mA = **150.0 mV**, against 60.91 Ω × 2.7249 mA =
**166.0 mV** before. The 2026-09-11 run validated that product against a measured 165.33 mV to
0.4 %, but `div2_mix.spice` writes no VDD-node probe, so 150.0 mV is arithmetic here.

**Two fidelity notes.**

*Terminal re-indexing.* The extractor renumbers device terminals when the layout changes. On
the INV3 output net `a_8030_n1600`, the R_SER tap was `.t1` before and is `.t0` now (`.t1` is
now the INV3 nfet drain). The one `wrdata` probe was moved `.t1 → .t0` so the INV3-output-span
metric measures the same physical tap; that is the **only** difference between the deck run
here and the committed `decks/div2_mix.spice`. No `.meas` statement is affected — they read
ammeters in the wrapper — and `v(I_P)` is a port node.

*The VSS port-to-internal-node sub-analysis above was not re-derived.* Its peak reproduces
(~58 mV both runs) but its "average" column does not follow from the deck's `wrdata` output
under any reading tried here, and since the VSS net is byte-identical between the two netlists
there is nothing for the fix to have changed. Rather than publish a number that cannot be
reconciled with the 2026-09-11 definition, it is left as recorded.

## Category bisect 2026-09-17 on the `9614947` netlist

Same zeroing method as the 2026-09-11 bisect: the class's resistors are **deleted** and the
nodes they joined are **merged by union-find**, one class per run, everything else intact.
Deck `div2_mix.spice`, `tran 0.2p 20n uic`, `set num_threads=2`, golden converters untouched.
Runs already on record were not repeated.

### Every R in the netlist, by net prefix

625 resistors, 71,199.788 ohm. Schematic names from `ib_conv_v1_golden.spice`.

| class | net prefix | count | ΣR (ohm) |
|---|---|---:|---:|
| VSS | `VSS` | **476** | **59,903.732** |
| VDD | `VDD` | **116** | **8,477.828** |
| **S2** — INV3 input | `a_6430_n1100` | 5 | 921.570 |
| **S1** — INV2 input | `a_2156_7176` | 6 | 650.054 |
| DN1 — diff-pair mirror | `a_938_3424` | 5 | 353.324 |
| **G1** — INV1 input, RFB node | `a_1676_7176` | 4 | 325.787 |
| INM | `INM` | 1 | 163.077 |
| INP | `INP` | 1 | 163.077 |
| IBIAS | `IBIAS` | 1 | 79.774 |
| S3 — INV3 output | `a_8030_n1600` | 3 | 73.018 |
| NS — tail | `a_100_n800` | 3 | 42.843 |
| OC — diff-pair output | `a_2430_n800` | 3 | 42.079 |
| OUT | `OUT` | 1 | 3.625 |
| **total** | | **625** | **71,199.788** |

The three **inverter input nets** are `G1` + `S1` + `S2` = **15 resistors, 1,897.411 ohm**.

### Runs

| run | collapsed / removed | count | Σ | I_P swing | INV3 (S3) span | S2 span | duty | I/Q | supply | I_P VSS | runtime |
|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| baseline PEX `9614947` | — | — | — | **29 mVpp** | 1989…2687 mV | not probed | 64.5 % | 289.6° | 22.791 mA | 2.8204 mA | 74 s |
| **(a) all R** | every parasitic R | 625 | 71,199.8 Ω | **109 mVpp** | **370…2919 mV** | 676…1793 mV | 59.9 % | 255.4° | 23.043 mA | 3.5362 mA | 40 s |
| **(b) VSS R only** | `VSS` net | 476 | 59,903.7 Ω | **28 mVpp** | 2016…2692 mV | 593…1237 mV | 64.6 % | 290.0° | 22.803 mA | 2.8199 mA | 46 s |
| **(c) inverter-input R only** | `G1`+`S1`+`S2` | 15 | 1,897.4 Ω | **37 mVpp** | 1849…2725 mV | 475…1332 mV | 67.2 % | 297.0° | 22.753 mA | 2.7905 mA | 61 s |
| **(d) all C** | every parasitic C | 136 | 190.5 fF | **61 mVpp** | 1233…2683 mV | 607…1449 mV | 65.0 % | 290.4° | 22.778 mA | 3.0522 mA | 62 s |
| **(e) VDD-metal only** | VDD supply metal | 111 | 309.5 Ω | **70 mVpp** | 1047…2696 mV | 892…1605 mV | 59.3 % | 261.9° | 23.205 mA | 3.5909 mA | 59 s |
| **(f) VDD-tap only** | VDD nwell/bulk taps | 5 | 8,168.3 Ω | **44 mVpp** | 1646…2694 mV | 610…1336 mV | 66.0 % | 273.1° | 22.778 mA | 2.9058 mA | 63 s |
| golden reference | — | — | — | 131 mVpp | −31…2998 mV | — | 49.5 % | 270.0° | 22.118 mA | 2.9735 mA | — |

`I_N` / `Q_P` / `Q_N` are 131 mVpp in every run (golden converters — the bench control).

### What the bisect says

**The VSS mesh still buys nothing, on the rebuilt netlist too.** 476 resistors and 59.9 kΩ —
84 % of all the parasitic resistance in the cell — move I_P from 29 to **28 mVpp**, i.e. not at
all. This reproduces the 2026-09-11 result on a netlist whose VSS section is byte-identical, so
it is a repeat measurement, not an independent one; it is recorded because it rules the VSS
network out for the *post-fix* netlist as well.

**Fifteen resistors on the inverter input nets buy more than 476 on VSS.** `G1`+`S1`+`S2`,
1.9 kΩ total, are worth **+8 mVpp** against VSS's +0 (in fact −1). Per resistor that is roughly
250× the leverage, and it is the same group the 2026-09-11 "signal only" run (33 R, 38 mVpp)
was pointing at.

**Capacitance is worth 32 mVpp, and this is the first time the whole set has been removed.**
The 2026-09-11 run A removed only the 12 caps on `G1`+`S1` and bought 14 mVpp; removing all
136 buys **32 mVpp** (29 → 61). Capacitance is therefore a larger share of the remaining
deficit than that run implied.

**The all-R ceiling did NOT move.** Collapsing every resistor gives **109 mVpp**, the same
number the 2026-09-11 netlist gave. The `9614947` VDD fix moved the *baseline* (25 → 29) but
left the ceiling where it was, so it removed some of the resistive deficit without changing
what resistance can account for at all. The residual 109 → 131 remains the capacitance, and
runs (a) and (d) are **not additive**: +80 mVpp (R) and +32 mVpp (C) against a 102 mVpp
deficit. The non-additivity first recorded on 2026-09-11 persists.

**`S2` moves with the swing, as expected, and only run (a) lifts it.** Its 16–20 ns average is
911 mV in (b) and 903 mV in (c) — both still parked low, near the 863 mV of the unmodified
2026-09-11 run — against 1235 mV in (a). Nothing short of removing all resistance gets `S2`
back toward a trip point.

**Consequence for the PFD feedback clock.** `I_P` is not a monitor pad: it is an internal net
feeding `PFD_lib`'s FB pin, i.e. the CLK input of a
`gf180mcu_fd_sc_mcu7t5v0__dffrnq_1`, an ordinary CMOS std-cell input tripping near VDD/2
≈ 1.65 V. The INV3 output minimum is **1989 mV** at baseline, **2016 mV** in (b) and
**1849 mV** in (c) — all *above* the trip point, so in those cases the extracted feedback clock
**never toggles at all**. Only (d) at 1233 mV and (a) at 370 mV bring it below. (`I_N`, `Q_P`,
`Q_N` have no such constraint — `docs/pins.md` §1: they are single-ended monitor outputs into a
1 kΩ → 50 Ω instrument, with no on-chip load and no trip point.)

**Capacitance accounting, for the record.** Total parasitic C is **186.34 fF before the fix and
190.51 fF after** — the 70 → 136 element count is the same charge redistributed over the VDD
net's 18 → 121 nodes, not new coupling. The whole +4.17 fF is the **VDD–VSS element**
(115.9 → 120.1 fF), i.e. the M3 plate acting as a little extra decoupling. Every signal net's
parasitic C is unchanged to the digit (`S1` 3.26, `S2` 5.28, `S3` 4.71 fF in both).

### VDD-class split 2026-09-17: supply metal vs nwell taps

The VDD class was split by the **pfet bulk terminal** (PDK order `d g s b`). Bulks are
`VDD.t0/t2/t4/t6/t8` (X11/X1/X2/X10/X4), sources are `VDD.t1/t3/t5/t7/t9`. A resistor is
**VDD-tap** if it lies on a branch that serves only a bulk node — found by iteratively peeling
degree-1 nodes that are neither the VDD port nor a pfet source contact — and **VDD-metal**
otherwise. After the peel no bulk node remains in the metal graph and all five source contacts
are still reachable from the port.

| class | count | ΣR (ohm) | share of ohms | I_P gain when collapsed | share of the gain |
|---|---:|---:|---:|---:|---:|
| **VDD-tap** (nwell/bulk) | **5** | **8,168.327** | **96.3 %** | **+15 mVpp** | 27 % |
| **VDD-metal** (supply) | **111** | **309.501** | **3.7 %** | **+41 mVpp** | 73 % |
| total | 116 | 8,477.828 | 100 % | — | — |

The tap resistors are `R4` 4,010.79 (X2 W44), `R5` 2,510.79 (X4 W26), `R6` 1,177.45 (X10 W10),
`R7` 468.75 (X1↔X11 shared well) and `R51` 0.547.

**Ohms are a bad predictor here, and that is the point.** 96 % of the VDD resistance sits in the
well taps and delivers 27 % of the recovery; the 3.7 % that is supply metal delivers 73 %. That
is consistent with the geometry finding already recorded above — a bulk path carries no DC
current — but it **refines** the earlier wording "those three kilo-ohm elements are not the
mechanism". They are not the *main* mechanism, yet they are worth **+15 mVpp**, roughly a third
again of what the whole `9614947` fix bought (+4 mVpp). The taps pass displacement current
through the well junction and modulate the pfet body, and that is not nothing.

**(f) does NOT carry most of the recovery, so the trigger for a tap-strip block is not met on
these numbers.** (e) at +41 mVpp is the larger share. Both are recorded because 15 mVpp is
still worth more than the VDD fix itself delivered.

**For the PFD feedback clock** (see the trip-point note above, ≈1.65 V): (e) brings the INV3
output minimum to **1047 mV**, comfortably across the trip point, so the extracted feedback
clock would toggle. (f) reaches **1646 mV** — within 4 mV of the trip point, i.e. marginal at
best. Supply metal is what decides whether the PFD clocks at all.

### Where the nwell taps sit, from `team_src/magic/ib_conv_v1.mag` (read-only)

Every pfet is drawn `nf = 1`, one tall finger, and **each nwell has exactly one tap strip, at
one end of the finger**. There are no taps along the length.

| device | nwell island | source `pdiffc` column | finger length | tap strip | tap width | gap, source end → tap | ΣR (PEX) |
|---|---|---|---:|---|---:|---:|---:|
| X2 INV3 W44 | (7400,4832)-(8600,14564), 6.00 × 48.66 µm | (7895,5185)-(7941,13959) | **43.87 µm** | (7617,14297)-(8383,14471) | 3.83 µm | 1.69 µm | **4,010.79 Ω** |
| X4 INV2 W26 | (5800,4332)-(7000,10464), 6.00 × 30.66 µm | (6295,4685)-(6341,9859) | **25.87 µm** | (6017,10197)-(6783,10371) | 3.83 µm | 1.69 µm | **2,510.79 Ω** |
| X10 INV1 W10 | (4200,3632)-(5400,6564), 6.00 × 14.66 µm | (4695,3985)-(4741,5959) | **9.87 µm** | (4417,6297)-(5183,6471) | 3.83 µm | 1.69 µm | **1,177.45 Ω** |
| X1/X11 difpair W8 | (-900,1400)-(3300,3960), 21.00 × 12.80 µm | (1095,1813)-(1141,3387) | 7.87 µm | (-816,3773)-(3216,3867) | **20.16 µm** | 1.93 µm | 468.75 Ω (shared) |

**The pattern is legible in one line: tap resistance tracks finger length.** 43.87 µm → 4,011 Ω,
25.87 → 2,511, 9.87 → 1,177. The three inverter wells each get a single **3.83 µm** strip at the
top while the well runs up to **48.66 µm**, so well current from the far end of the finger
crosses the whole island to reach one contact. The diff-pair well is the counter-example that
proves it: its tap strip is **20.16 µm**, five times wider, running the length of a 21 µm well —
and its tap resistance is the lowest of the four despite serving two devices.

**M1 path to VDD.** Each tap strip carries M1 (the `nsubdiffcont` tile implies it), and that M1
reaches the VDD bus through the inverter bus tap via1 — which `9614947` widened from 1 cut to
**3 cuts** at each of the three inverter taps (at x 4566/4670/4774, 6166/6270/6374,
7766/7870/7974). The tap-to-bus connection is therefore no longer the narrow point; the well
crossing is.

**What a next block would do, if it takes this up:** add nwell tap strips along the length of
the three inverter wells rather than one strip at the end. Taps at both ends alone should
quarter the well resistance; strips at intervals would do better. This is a **layout change and
is not proposed here** — the measurement says it is worth at most the 15 mVpp of run (f), and
run (e) says the supply metal is the larger prize.

### Method notes

Runs (a) and (b) collapse the `VSS.tN` nodes, so the `mixvss.dat` `wrdata` line — which probes
exactly those nodes — was dropped from all four decks. `S2` was added as the **last** `wrdata`
variable so `analyze.awk`, which reads columns 1–12, is unaffected. The union-find
representative was chosen to keep the two probe node names (`a_8030_n1600.t0`,
`a_6430_n1100.t3`) alive in every variant, which is free — any member of a merged group names
the same node. Device count is 14 in all four variants and every device keeps its model and
W/L.

## What is reported and what is not

These are measurements. No cause is asserted here beyond what was measured: the extracted
converter settles to a state in which its INV3 output does not reach the rails, its output swing
is 25 mVpp against the schematic's 131 mVpp, and it draws 8.4 % less VSS current. Whether that
originates in the extracted VSS network, the self-bias path through the extracted `RFB`, the
20 ns stop, or the `uic` start has **not** been isolated, and no such claim is made.

The DIV2 core remains schematic in every run; only the converters change.
