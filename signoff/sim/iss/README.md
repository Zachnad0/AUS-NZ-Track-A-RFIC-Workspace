# `signoff/sim/iss/` — ISS node voltage and tail-sink compliance

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Run 2026-11-02 at `8486ed6`, on the landed `vco_v1` extraction (`signoff/sim/vco/pex200.spice`).
ngspice-46, TT, 27 °C, `tran 5p 200n uic`, measured 150–200 ns, 2 threads, one job at a time.

| File | What it is |
|---|---|
| `mk_vco_iss.py` | builds a deck from `pex200.spice`: VTUNE set, tail from the bench mirror (`mirror`) or an ideal sink (`ideal`); measures avg/min/max v(ISS) and the tail current |
| `analyze_iss.py` | differential swing and f0 over 190–200 ns from the `.dat` dump |
| `run_iss.sh` | `node`: mirror at 1 mA / 2 mA reference × VTUNE 0 / 2.0 / 3.3 V. `sweep`: ideal sink 1.0–2.35 mA at VTUNE 2.0 V. Decks, logs and dumps go to `/tmp/iss` |

Run in-container: `bash run_iss.sh node` (~11 min), `bash run_iss.sh sweep` (~10 min).

Results and their interpretation are in `docs/test_plan.md` §5.1. Headline: v(ISS) stays at
1.0–1.42 V in every case, with a minimum of 1.009 V (2 mA reference, VTUNE 3.3 V). The off-chip
sink must regulate with its terminal at 1.0 V or lower. The `node` runs reproduce the
`docs/verification.md` §3.2.1 band to within 0.003 GHz.
