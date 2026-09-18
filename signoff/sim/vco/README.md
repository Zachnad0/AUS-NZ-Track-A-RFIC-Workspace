# `signoff/sim/vco/` — the VCO bench, and why the extracted startup run is still open

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Recorded 2026-09-18 at commit `6dfb71f`, attempting the tank-level startup check that
`docs/verification.md` §3.2 has been flagged as needing since the tank fix (`6573181`).

**Outcome: no simulation result. Both runs are blocked, for different reasons, and both are
recorded here so the next attempt starts from measured numbers instead of guesses.**

## Files

| File | What it is |
|---|---|
| `vco_tb.spice` | the bench, netlisted headlessly from `team_src/xschem/vco_tb.sch` |
| `mkdeck.py` | builds run decks from it — sets VTUNE and tstop, replaces the committed `.control` (which ends in `plot`, needing a display), and optionally swaps the schematic `vco_v1` for the extracted netlist |

## Netlisting

```
cd team_src/xschem
xschem -n -q -x -s -l <scratch>/xschem.log --netlist_path <scratch> vco_tb.sch
```

Runs headless and exits 0. The deck contains one `vco_v1` instance
(`x1 vdd net1 net2 GND tune vss vco_v1`), `.option method=gear`, and the four PDK includes
`docs/verification.md` §3.2 cites (`design.ngspice` plus `sm141064` typical / res_typical / moscap_typical).

### Three deltas from what `docs/verification.md` §3.2 describes

`docs/verification.md` §3.2 cites `tran 5p 80n`, settled 60–80 ns, at VTUNE 2.15 V. The committed schematic does not
hold that state, so whoever produced those numbers edited the deck before running:

| | committed `vco_tb.sch` | `verification.md` §3.2 |
|---|---|---|
| transient | `tran 5p 1.04u 40n 5p` (the long run for the FFT) | `tran 5p 80n` |
| VTUNE | `V2 tune GND 1.5` | 2.15 V (and the sweep points) |

The third delta is **not** a bench setting and matters more:

| | bench schematic | LVS golden, `vco_tune_r`, and the extracted layout |
|---|---|---|
| tune resistor | `ppolyf_u_3k r_width=1u r_length=5u` | `ppolyf_u_1k r_width=1u r_length=15u` |

Both are ~15 kΩ nominal (3 kΩ/sq × 5 µm vs 1 kΩ/sq × 15 µm) and it is a DC bias feed into a
varactor gate, so it should not move f0 — but **the bench schematic and the signed-off golden
describe different devices**, and that should be reconciled before any number from this bench
is quoted as matching the layout.

## Measured runtimes — the figures that did not exist before

`ngspice-46`, `set num_threads=2`, in-container, `timeout 600`, VTUNE 2.0 V:

| deck | probe `tran 5p 5n` | extrapolated to 80 ns |
|---|--:|--:|
| schematic `vco_v1` | **36.5 s** | **583 s ≈ 9.7 min** |
| extracted `vco_v1` | 0.6 s (aborted, see below) | — |

The deck's own options are what make it expensive: `reltol=1e-5`, `method=gear`, `bypass=0`.
The 5 ns probe took 16 203 internal timepoints for 1 000 requested.

**583 s exceeds the 5-minute budget set for this work, so the full 80 ns schematic control was
not run.** That is a scheduling decision, not a failure: the deck is sound and the run is
simply longer than the window allowed.

## The extracted deck aborts at t = 0

Two problems, one mine and one not:

1. **Mine, fixed.** `ext2spice hierarchy off` leaves the abstract child's substrate node
   floating: **542 parasitic caps hang off `vco_inductor_v2_0/VSUBS` with no DC path**, which
   makes the operating point singular. `mkdeck.py` ties it (VSUBS *is* the substrate) along
   with three vestigial cap-only nodes from the committed inductor `.ext`. With those ties the
   operating point solves.

2. **Not fixed.** The transient then aborts at the *initial timepoint*:

   ```
   doAnalyses: TRAN:  Timestep too small; initial timepoint:
               trouble with node "e.x1.x38.ec_moscap#branch"
   ```

   `ec_moscap` is an internal behavioural source inside the `cap_nmos_03v3_b` model. The
   schematic deck instantiates **2** of them (`m=21` each); the extracted deck instantiates
   **42 individually**, and the combination of 42 behavioural moscap models with
   `method=gear` + `reltol=1e-5` + `bypass=0` will not take a first step.

   **No timepoints are produced, so there is no startup envelope to report.** Getting past it
   means relaxing the solver settings, ramping the supply, or supplying an `.ic` — all of which
   change the numerical experiment, and none of which were in scope here.

## What the next attempt should do

1. Reconcile the `ppolyf_u_3k` / `ppolyf_u_1k` delta above, so the bench and the golden agree.
2. Budget **≥ 10 minutes per 80 ns point** for the schematic control, more for the extracted.
3. For the extracted deck, decide deliberately how to get the first timestep — and record the
   setting alongside the result, because it is part of the measurement.
