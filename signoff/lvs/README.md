# `signoff/lvs/` — LVS artifacts, tracked and readable without running anything

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Generated 2026-09-01 from commit `52a783a`, layout `gds/chip_top.gds`.

These files exist because the flow's own working directory,
`team_src/magic/verify_work/`, is **gitignored** (see `.gitignore`) — it is regenerable
build output, so nothing in it was ever visible in the repository. This directory is a
committed copy of the artifacts a reviewer or an aggregation script needs.

**Nothing here is hand-edited.** Every file is byte-for-byte tool output, copied verbatim.
The `lvs.report` files begin with a blank line and end with a `.` because that is exactly
what netgen emits; that was left alone on purpose rather than tidied.

## What is here

| File | What it is |
|---|---|
| `lvs.report` | **The top-level LVS report — `chip_top`.** netgen comparison output, layout vs the hand-written golden. Named `lvs.report` so it is findable without knowing our cell names. |
| `chip_top.lvs.spice` | Extracted netlist of the whole chip (Magic `ext2spice`). Every device instance on the die, with its PDK model name and geometry. |
| `chip_top.drc.log` | Magic DRC log for the same layout (`VERIFY_DRC_COUNT=0`). |
| `blocks/<CELL>.lvs.report` | Per-block netgen comparison output. |
| `blocks/<CELL>.lvs.spice` | Per-block extracted netlist. |

Blocks: `PFD_lib`, `CP_v1`, `ibias_gen_v1`, `DIV2_QUAD_v1`, `vco_v1`.

## Results, as of this capture

Every cell: Magic DRC **0**, netgen **"Circuits match uniquely"**, **0 property errors**
(`verify_cp.sh` hard-fails on a W/L property error, not only on a topology mismatch).

| Cell | netgen devices | nets | ports | Verdict |
|---|---:|---:|---:|---|
| `chip_top` | 10 | 20 | 11 | match uniquely |
| `PFD_lib` | 7 | 11 | 6 | match uniquely |
| `CP_v1` | 8 | 10 | 7 | match uniquely |
| `ibias_gen_v1` | 17 | 15 | 6 | match uniquely |
| `DIV2_QUAD_v1` | 75 | 47 | 9 | match uniquely |
| `vco_v1` | 7 | 7 | 6 | match uniquely |

`chip_top`'s 10 devices are the **top-level** instances: the five blocks, the ESD ballast
resistor, and the two ESD diode groups (`diode_nd2ps_03v3 (8->2)`,
`diode_pd2nw_03v3 (8->2)`). Device counts *inside* the blocks are in
`../devices.md`.

> **Three different device counts exist for this design and they are not interchangeable.**
> Read `../devices.md` §"Counting conventions" before quoting any number. In short:
> netgen's merged count (above) ≠ the raw instance count in the extracted netlist ≠ the
> summary line `verify_cp.sh` prints. All three are correct for what they measure.

## Two accepted LVS waivers, both in `chip_top` and both narrow

1. **`vco_inductor_v2` is an `ignore class`.** The custom spiral is a physical inductor with
   no foundry device model; netgen black-boxes it. It still appears in the extracted netlist
   as two `tm11k` top-metal resistors (its M5 leads) — see `../devices.md`.
2. **`PFD_lib` fill/decap cells are ignored** (18 instances of `gf180mcu_fd_sc_mcu7t5v0__fillcap_*`)
   using only the PDK-provided `ignore class`. This is the same waiver LibreLane's own run
   applies via `LVS_IGNORE`. The devices inside those cells are real and **are** counted in
   `../devices.md`.

There is **one DRC waiver**, unrelated to LVS: 168 KLayout `PL.5a_LV`/`PL.5b_LV` items
internal to the PDK's `nmoscap_3p3` gencell. See `../../docs/layout-review-sep01.md` §2.5.

## Regenerating

Inside the `iic-osic-tools` container, from the repo root:

```
export PDK=gf180mcuD PDK_ROOT=/foss/pdks
for c in PFD_lib CP_v1 ibias_gen_v1 DIV2_QUAD_v1 vco_v1 chip_top; do
  bash team_src/magic/verify_cp.sh $c
done
```

~28 s for all six. Output lands in `team_src/magic/verify_work/`; this directory is a copy.
`verify_cp.sh` exits 0 only on DRC 0 + match uniquely + zero property errors.

**The extracted netlist is not byte-reproducible run to run** in the same way the GDS is not
(`docs/verification.md` §8.11): node auto-names such as `IBIAS_uq0` and `m4_n14800_800#` are
generated during extraction. The device set, counts and geometry are stable; incidental node
names may differ. Compare device tables, not file hashes.
