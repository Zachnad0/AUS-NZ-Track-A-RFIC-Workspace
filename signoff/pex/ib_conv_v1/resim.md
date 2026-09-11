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

## What is reported and what is not

These are measurements. No cause is asserted here beyond what was measured: the extracted
converter settles to a state in which its INV3 output does not reach the rails, its output swing
is 25 mVpp against the schematic's 131 mVpp, and it draws 8.4 % less VSS current. Whether that
originates in the extracted VSS network, the self-bias path through the extracted `RFB`, the
20 ns stop, or the `uic` start has **not** been isolated, and no such claim is made.

The DIV2 core remains schematic in every run; only the converters change.
