# Aug-14 Layout Review — Team A01 (AUS/NZ Track A RFIC)

Block under review: **PFD_lib** (library-cell PFD, gf180 5 V std cells, our PFD topology).
All numbers below are read from files in the passing run
`librelane_pfd/runs/RUN_2026-08-05_23-52-38/` unless noted. Image: `docs/img/PFD_lib_white.png`.
Second Aug-14 target CP_v1 is analog full-custom — golden + drawing packet done, **layout
not yet drawn** (see §3).

Ground note (applies throughout): the padframe provides **one chip-wide common ground**
(#143: ground = 0 pins). `VSSA`/`VSSD` are **on-chip routing labels only — not separate
ground pins**. `VDDA`/`VDDD` are the two real power pins.

---

## 1. DRC and LVS correctness — **claimed 3/3**

Evidence (file-read):
- **Magic DRC = 0** — `…/63-magic-drc/reports/drc.magic.rpt` ("COUNT: 0"); `final/metrics.json`
  `"magic__drc_error__count": 0`.
- **KLayout DRC = 0** — `final/metrics.json` `"klayout__drc_error__count": 0`;
  `…/64-klayout-drc/reports/drc.klayout.json`.
- **Routing DRC = 0** — `final/metrics.json` `"route__drc_errors": 0`.
- **netgen LVS = Circuits match uniquely** — `…/69-netgen-lvs/reports/lvs.netgen.rpt`
  ("Netlists match uniquely", 11 devices / 11 nets both sides); `final/metrics.json`
  `"design__lvs_error__count": 0`, `"design__lvs_device_difference__count": 0`.
- Layout also LVS-matches our hand golden (`team_src/magic/PFD_lib_golden.spice`), verified
  separately (`verification.md §2.3`).
- **Cell inventory** (`final/nl/PFD_lib.nl.v`): 2× dffrnq_1, 1× nand2_1, 2× inv_1, 2× tieh;
  everything else physical-only (endcap×8, fill_1×7, fill_2×6, fillcap_16×6, fillcap_32×3,
  fillcap_4×5, fillcap_8×4, filltie×6).
- **Reset delay preserved:** `NAND(UP,DOWN)→NANDO→XI1→NDLY→XI2→RSTN→both DFF.RN` — 2× inv_1
  in series on RSTN, confirmed in the final post-route netlist.

Not verified: nothing outstanding for this row.

---

## 2. Power, ground, current paths — **claimed 3/3**

Evidence (`resolved.json` + reports):
- **PDN layers:** rail = **Metal1** (`PDN_RAIL_WIDTH` 0.6 µm); vertical straps **Metal4**,
  horizontal straps **Metal5** (`PDN_VERTICAL_LAYER`/`PDN_HORIZONTAL_LAYER`); core ring on
  Metal4/5, `PDN_CORE_RING_VWIDTH`/`HWIDTH` 1.6 µm. `PDN_MULTILAYER` false.
- **Strap width / spacing / pitch:** `PDN_VWIDTH`/`HWIDTH` 1.6 µm; spacing 1.7 µm; pitch
  `PDN_VPITCH` 153.6 µm / `PDN_HPITCH` 153.18 µm (pitch ≫ the ~60×24 µm block → effectively
  core ring + Metal1 rails feed the cells).
- **Vias:** `final/metrics.json` `"route__vias": 26` (all single-cut, 0 multicut),
  `"global_route__vias": 30`.
- **Tap:** `FP_TAPCELL_DIST` 20 µm (setting — see §4 caveat); tap/tie cells = **filltie ×6**.
- **IR drop** (`…/55-openroad-irdropreport/irdrop.rpt`, corner nom_tt_025C_5v00):
  **VDD worst-case 9.60 µV** (avg 8.99 µV), **VSS worst-case 18.2 µV** (avg 7.24 µV),
  **0.00 % drop**, all shapes connected. `final/metrics.json`
  `"design__power_grid_violation__count": 0`.

Not verified: power-specific via count is not broken out separately from routing vias in the
metrics (only total route/global-route vias reported).

---

## 3. Analog matching, symmetry, noise isolation — **PFD_lib N/A (no-analog clause); CP_v1 NOT YET**

- **PFD_lib** is all-digital std cells; it qualifies under the rubric's **"no analog
  circuitry" clause** — matching/symmetry/noise-isolation do not apply to this block.
- **CP_v1** is the analog block for this row. Real status, stated plainly:
  - Golden LVS netlist **verified** (`team_src/magic/CP_v1_golden.spice`, 8 devices, parses).
  - Drawing packet **written** (`docs/cp-layout-packet.md`): matched-mirror finger breakdown +
    dummies, guard rings, noise-driven ≥20 µm CP↔PFD separation (not the 0.48 µm DRC floor),
    CP_OUT shielding.
  - **Layout NOT drawn.** No CP `.mag`, no CP DRC/LVS/matching evidence exists yet.

Not verified (CP_v1): entire layout, device matching, guard-ring geometry, CP↔PFD noise
separation, CP_OUT shielding — all pending the GUI draw.

---

## 4. Reliability and physical-design risks — **claimed 2/3**

Evidence (file-read):
- **Antenna: 0 violations, 0 diodes** — `final/metrics.json` `"antenna__violating__nets": 0`,
  `"antenna__violating__pins": 0`, `"antenna_diodes_count": 0`;
  `…/45-openroad-checkantennas-1/reports/antenna_summary.rpt` (empty violation table).
- **Latch-up / tap distance — honest statement:** the enforced rules are **DF.13_MV /
  DF.14_MV = 15 µm** max tap-to-device distance for 5 V devices (confirmed **live executed
  rules** in `…/klayout/tech/drc/rule_decks/comp.drc`: `logger.info('Executing rule …')` +
  `.output(...)`, gated on `.overlapping(dualgate)`). **`FP_TAPCELL_DIST` = 20 µm EXCEEDS the
  15 µm limit.** Compliance here is **incidental to this block's small size** (std cells
  self-tap; filltie taps keep the real distance under 15 µm) and is confirmed **only by
  KLayout DRC = 0**. **20 µm must NOT be treated as compliant — the setting must drop to
  ≤ 15 µm before reuse on any larger 5 V block.**
- **DUALGATE spacing** (cited from `docs/scope.md §4.2`, not re-derived): DV.3 (DUALGATE-to-COMP)
  0.24 µm, DV.2 (DUALGATE space) 0.44 µm → ~0.48 µm PFD-active-to-CP-active DRC floor. That is
  a **DRC floor, not the block gap**; the noise-driven CP↔PFD gap is ≥ 20 µm (§3 / packet §3b).
- **ESD:** this block has **no pads**; secondary ESD sits with the **organizer padframe**
  (`scope.md §7`, `pins.md §2`). ESD is not a block-level artifact here.

Not verified / NOT DONE: **current-density / electromigration** (no check exists in the run —
LibreLane Classic flow does not run it); **ESD quantification**; **PEX** (parasitic extraction).

---

## 5. Top-level integration and connectivity — **claimed 2/3**

Evidence (file-read):
- **Name correspondence — all match `PFD_lib`:** GDS top cell (`final/gds/PFD_lib.gds`),
  `.v` module (`module PFD_lib`), `.def` DESIGN, and golden `.subckt PFD_lib`.
- **Block interface:** ports `REF FB UP DOWN VDD VSS` (`final/nl/PFD_lib.nl.v`; golden matches).
- **Submission pointer repointed:** `lvs/lvs_config.json` `TOP_SOURCE` = `PFD_lib`,
  `LVS_VERILOG_FILES` = `$UPRJ_ROOT/lvs/PFD_lib.nl.v`, `LAYOUT_FILE` =
  `$UPRJ_ROOT/gds/$TOP_LAYOUT.gds` → `gds/PFD_lib.gds` (both committed; no run-tag paths).

Not verified: this is a **single block**, not the integrated RFIC top (which does not exist
yet). Top-level padframe integration, inter-block routing, and the CP/VCO/DIV2 blocks are not
part of this GDS. `lvs_config` TOP must be repointed at the integrated top before the Aug-21
GDS (`tracking.md §4`).

---

### Score summary (self-assessed, conservative)
| Rubric row | Score | Basis |
|---|---|---|
| 1 DRC/LVS correctness | **3/3** | Magic 0, KLayout 0, route 0, LVS match uniquely — all file-read |
| 2 Power/ground/current | **3/3** | PDN + IR drop 9.6/18.2 µV, 0 PG violations |
| 3 Analog matching/isolation | **N/A (PFD) / NOT YET (CP)** | PFD no-analog clause; CP layout not drawn |
| 4 Reliability | **2/3** | antenna 0, latch-up DRC-clean (tap-dist caveat); EM/ESD/PEX NOT DONE |
| 5 Top-level integration | **2/3** | names match, pointer repointed; block ≠ integrated top |
