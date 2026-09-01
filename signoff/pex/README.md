# `signoff/pex/` — parasitic extraction of `CP_v1`, and the extracted UP/DOWN current match

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Generated 2026-09-01 from `gds/CP_v1.gds` at commit `67cdf72`.

This exists because every charge-pump matching claim in the project was **schematic-level**
until now (`docs/layout-review-sep01.md` §6 item 8). The charge pump's current match is its
headline spec, so it is the one block where an extracted number is worth having.

## Files

| File | What it is |
|---|---|
| `CP_v1.pex.spice` | **R+C extracted netlist** of the signed-off layout — 38 devices, 265 parasitic caps, 269 parasitic resistors. Magic `ext2spice`, `cthresh 0 rthresh 0`, flattened. |
| `cpmatch_sch.spice` | DC testbench on the **schematic golden** (`team_src/magic/CP_v1_golden.spice`). |
| `cpmatch_pex.spice` | The **same** testbench on `CP_v1.pex.spice`. Identical stimulus and bias. |
| `cp_v1_match.csv` | The 49-point comparison, 0.4–2.8 V in 50 mV steps. |

Recipe: `team_src/magic/pex_cp_v1.tcl` (committed). Regenerate in-container from
`team_src/magic/pex_work`:

```
magic -dnull -noconsole -rcfile $PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc ../pex_cp_v1.tcl
ngspice -b cpmatch_sch.spice ; ngspice -b cpmatch_pex.spice
```

## Method

Bias follows the `CP_v1_golden.spice` header: the external generator **sinks** I_CP from `VGP`
and **sources** I_CP into `VGN`. Both decks use **ideal 50 µA** sources for that, so the
comparison isolates the *layout* contribution and nothing else. `I_CP = 50 µA` is the measured
value (`docs/verification.md` §2.1 — 10.19 µA at φ = 200 ns against 10.00 µA ideal).

Source-only is `UP = 3.3 V, DOWN = 0` (the `M_INVP`/`M_INVN` inverter takes `UP` to `UP_B`, so
the PMOS switch turns on); sink-only is `UP = 0, DOWN = 3.3 V`. `CP_OUT` is swept 0.4–2.8 V,
which is the compliance window used in `docs/verification.md` §2.6 S5.

Mismatch is `(|I_src| − |I_sink|) / mean × 100 %`.

## Result — the layout does not degrade the current match

| CP_OUT | schematic mismatch | **extracted mismatch** | delta |
|---:|---:|---:|---:|
| 0.50 V | +1.675 % | +1.721 % | +0.047 pp |
| 1.00 V | +0.717 % | +0.736 % | +0.019 pp |
| **1.50 V** | −0.001 % | **+0.007 %** | +0.008 pp |
| 2.00 V | −0.849 % | −0.848 % | +0.001 pp |
| 2.50 V | −1.635 % | −1.638 % | −0.004 pp |

Across all 49 points of the 0.4–2.8 V window:

| | min | max | mean |
|---|---:|---:|---:|
| schematic mismatch | −2.274 % | +2.246 % | −0.193 % |
| **extracted mismatch** | −2.283 % | +2.321 % | −0.182 % |
| **extracted − schematic** | **−0.008 pp** | **+0.076 pp** | **+0.012 pp** |

**The headline number: R+C parasitics shift the UP/DOWN match by at most 0.076 percentage
points, mean +0.012 pp.** The charge pump's matching survives its layout.

**At the zero-crossing the extracted match is +0.007 %** (schematic −0.001 %). The historical
"0.001 %" figure was a schematic single-point zero-crossing with ideal, perfectly equal sources;
the extracted layout equivalent is **0.007 %** — still excellent, and now measured on the drawn
cell rather than asserted from a schematic.

**The ±2.3 % swing across the window is not a layout defect.** It is the CP's intrinsic
output-impedance mismatch and it is present in *both* columns, which independently reproduces
the finding in `docs/verification.md` §2.6 S5 that the ±2 % variation is intrinsic and appears
identically with ideal sources.

## What this does NOT cover — read before quoting the number

- **Ideal bias, not the real generator.** These decks drive `VGP`/`VGN` from ideal 50 µA
  sources. `docs/verification.md` §2.6 S5 measured that the real `ibias_gen_v1` adds a **uniform
  +0.18 %** to the CP mismatch at TT. That term is **additive to the numbers above and remains
  schematic-level** — it has not been re-measured against the extracted CP.
- **TT only.** No corners. `verification.md` §2.6 S6 gives the process spread as FF 0.004 % /
  TT 0.18 % / SS 0.94 % for the generator-driven case.
- **No Monte Carlo.** Random device mismatch is still not captured anywhere in this project;
  everything here is systematic.
- **DC only.** This is a static current-match measurement. It says nothing about the known
  **+110 fC/cycle charge injection** (`verification.md` §2.1), which is a dynamic,
  schematic-level flaw that layout does not fix.
- **`CP_v1` only.** No other block has PEX except `PFD_lib` (capacitance-only,
  `verification.md` §2.3.3). Full-chip PEX was not attempted.

## One flow note worth keeping

`ext2spice rthresh 0` **on its own emits zero resistors** — it only sets a reporting threshold.
Getting parasitic R needs a real extraction pass: `extract do resistance` → `ext2sim` →
`extresist all` → `ext2spice extresist on`. Measured on this cell, the difference is **27 caps /
0 R** versus **265 caps / 269 R**. The earlier `PFD_lib` PEX (`pex_work/pex_pfd.tcl`,
`verification.md` §2.3.3) used the short form and is therefore **capacitance-only** — which is
adequate for the REF/FB coupling question it was asked, but is not a full PEX.
