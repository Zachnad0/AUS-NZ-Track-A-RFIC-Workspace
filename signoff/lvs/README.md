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

## The organizer flow (`mpw_precheck run_full_lvs`) — recipe and result

Run 2026-09-18 at `aa470c3`. **This is a different check from `verify_cp.sh` above and it does
not pass yet.** `verify_cp.sh` compares `chip_top` against `chip_top_golden.spice` alone, with
every block a black box; the organizer flow additionally reads the PDK standard-cell netlist and
so compares the inside of `PFD_lib` too.

### Runner

`efabless/mpw_precheck` at commit `0941bdc1b62b5c3f99c8683bd11199d330af2ef3`. The scripts are
under `checks/be_checks/`, not `checks/lvs_check/`; `LVS_ROOT` is that directory.

**Caveat, and it is not ours: **set_lvs_env.py**, under the runner's `checks/be_checks/`, cannot be obtained.** It is
listed in mpw_precheck's own `.gitignore`, has never been committed to any branch or tag
(checked `gfmpw-1a`…`1d` and `2024.09.*`), and nothing in the repo or its `dependencies/Dockerfile`
generates or fetches it. Every `run_*` entry point sources it, so the config path
(`run_full_lvs <config>`) is unusable as shipped.

The workaround uses `run_full_lvs`'s own documented alternative — *"if config file not specified,
skip and use current environment"* — so the runner script itself is unmodified:

```bash
export PDK=gf180mcuD PDK_ROOT=/foss/pdks
export UPRJ_ROOT=<repo root>
export LVS_ROOT=<clone>/checks/be_checks
source <(python3 mk_lvs_env.py $UPRJ_ROOT/lvs/lvs_config.json)   # see note below
export WORK_ROOT=<scratch> LOG_ROOT=$WORK_ROOT SIGNOFF_ROOT=$WORK_ROOT
$LVS_ROOT/run_full_lvs            # no arguments
```

**mk_lvs_env.py** is the one reconstructed piece: it reads `lvs/lvs_config.json` and the
`INCLUDE_CONFIGS` base, and emits the `export` lines **set_lvs_env.py** would have. Merge rule:
scalars override, list variables are a **union**, and `[""]` means "adds nothing" — which is the
only reading under which efabless's own reference configs work, since
`caravel_user_project_analog` sets `EXTRACT_FLATGLOB` to `[""]` while depending on the base
config to supply the real patterns. It lives in scratch, not in this repo, because it is a
stand-in for a file the organizers are expected to have.

Runtime is **8–10 s** per run on this host.

### Result

| run | change | devices (layout/source) | nets | ports | verdict |
|---|---|---|---|---|---|
| 0 | none (`152f812`) | 79 / 84 | 52 / 53 | **13 / 11** | fail, 2 pin shorts |
| 1 | `REF_IN_PD/PU` → 36/0 | 79 / 84 | 52 / 53 | **11 / 11** | fail, **no pin shorts** |
| 2 | `LVS_IGNORE += vco_inductor_v2` | 79 / **83** | 52 / 53 | 11 / 11 | fail |

Runs 3 and 4 tried `EXTRACT_ABSTRACT` for `vco_inductor_v2` and then `vco_varactors`; neither
changed the verdict and both were reverted (see the `lvs_config` commit message).

**The identical run on `c7eb341`, the commit `item23` branched from, fails the same way** — 79/84,
52/53, both pin shorts. None of this was introduced by item 23.

### What is still mismatched, and why

Two causes remain. Neither is expressible in the organizer config schema.

**1. `OUT_p` and `OUT_n` are one net when the GDS is read as geometry.** The extracted
`vco_v1` is

```
.subckt vco_v1 TUNE GND VDD ISS OUT_p          <- 5 ports; the golden has 6
Xvco_core_0 ISS VDD GND OUT_p OUT_p vco_core   <- OUT_n merged into OUT_p
```

`verify_cp.sh` does not see this because `team_src/magic/chip_top.abstract` says
`PRELOAD=vco_varactors vco_inductor_v2`, and `verify_extract.tcl` implements that as `load` of
those `.mag` masters plus `gds noduplicates true`, so the GDS read keeps the abstract and never
traverses the spiral. **The organizer schema has no PRELOAD equivalent**: `EXTRACT_ABSTRACT`
black-boxes a cell that is already in the stream, it does not substitute a `.mag` master for it.
Tried directly — abstracting `vco_inductor_v2` produced the abstract but left `OUT_n` merged and
added a dangling `vco_inductor_v2_0/PORT1`; abstracting `vco_varactors` as well changed nothing.

**2. The standard cells extract as `*_06v0` and the PDK models them as `*_05v0`.** 34 `nfet` and
34 `pfet` on each side, same devices, different class name. They are the standard cells inside
`PFD_lib` — `gf180mcu_fd_sc_mcu7t5v0__dffrnq_1` (28), `__nand2_1` (4), `__inv_1` (2), `__tieh`
(2). `PFD_lib` itself compares **68 / 68 devices, 38 / 38 nets and matches**; only the flattened
chip-level tally splits.

This one is entirely inside the PDK. Both `gf180mcuD` spice views of the library —
`libs.ref/gf180mcu_fd_sc_mcu7t5v0/spice/*.spice` and `.../cdl/*.cdl` — use `nfet_05v0` /
`pfet_05v0`, while magic's extraction of those same cells yields `nfet_06v0` / `pfet_06v0` and
the PDK's netgen setup declares **only** the `*_06v0` classes (`05v0` appears zero times in it).
The fix is a netgen `equate classes nfet_05v0 nfet_06v0`, which belongs in the setup `.tcl` the
runner copies from the PDK — **the config schema does not expose it**, and there is no alternate
PDK file that would make the two agree.

`verify_cp.sh` never hits this because it feeds netgen only `chip_top_golden.spice`, with no
standard-cell netlist at all, so `PFD_lib`'s 68 devices are never compared.

### Reading this honestly

The port fix in `aa470c3` is a real correction to the deliverable and is gated on its own merits.
The two remaining causes are a tool-flow gap and a PDK naming inconsistency; neither indicates a
defect in `gds/chip_top.gds`. Whether the organizer flow passes for anyone on gf180mcuD with a
standard-cell block is worth asking the organizers before treating cause 2 as ours.

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
