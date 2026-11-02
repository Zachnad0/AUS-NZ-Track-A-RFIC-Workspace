# `signoff/sim/cp_out/` — CP_OUT DC current at the pad

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Run 2026-11-02 at `5defbaf`. ngspice-46, TT, 27 °C, 3.3 V, DC operating points.

| File | What it is |
|---|---|
| `cp_out_op.spice` | extracted `CP_v1` (`signoff/pex/CP_v1.pex.spice`) biased by `ibias_gen_v1` (schematic, `team_src/sim/ibias/ibias_sub.spice`) at a 240 µA reference; `CP_OUT` forced to 0.32 / 1.65 / 3.00 V in the idle, UP-only and DOWN-only states |
| `run_cp_out.sh` | runs it in-container (one job, 2 threads, ~0.3 s); log in `/tmp/cp_out` |

Results (positive = the CP sources current out of `CP_OUT`):

| `CP_OUT` | idle | UP only | DOWN only |
|---|---|---|---|
| 0.32 V | +29.8 pA | +50.34 µA | −48.08 µA |
| 1.65 V | +12.2 pA | +50.21 µA | −50.24 µA |
| 3.00 V | −5.6 pA | +48.12 µA | −50.54 µA |

The 1.65 V UP/DOWN values match the `signoff/sim/vdda/` run (+50.21 / −50.24 µA). Used in
`docs/test_plan.md` §5.3.
