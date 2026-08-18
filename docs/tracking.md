# Tracking & Milestones — AUS/NZ Track A RFIC

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU**
Last updated: 2026-07-30.

Companion to the team **Progress Tracker** spreadsheet:
<https://docs.google.com/spreadsheets/d/1ioGDfle-Np0gdS-PER5QJmRa5nnGZcALtzJDiHwNKBI/edit>
This file is the git-tracked, dated view; the sheet is the live shared view.

Owners: **Zach** (@Zachnad0, team lead — VCO, inductor), **Greg**
(@gregorydaley1209 — PFD, CP, digital, divider, integration, layout, docs),
**xyfy3** (member — support). "Team" = shared.

---

## 1. Schedule vs. organizer deadlines

| Date | Gate | What we deliver | Status | Owner |
|------|------|-----------------|--------|-------|
| **Jul 31** | Weekly form closes | Area Estimate + Pin count lines in issue #143; on-track claim for Aug 6 | 🟡 In progress (this update) | Greg |
| **Aug 6** | DRC dry-run | Sample GDS + DRC — **toolchain/sample-GDS proof only** (workshop-slot LibreLane) | 🟢 **Done: full GDS (chip_top.gds 27 MB) + Magic DRC = 0** (read from drc.magic.rpt); KLayout DRC still running/inconclusive | Greg |
| **Aug 7** | Sample layout review | Present sample-cell layout | ⬜ Not started | Greg |
| **Aug 10** | Layout review docs due | Per-cell DRC/LVS table, PNGs, area vs estimate | ⬜ Not started | Greg |
| **Aug 14** | Block layout reviews | **CP_v1 + PFD digital chain** (VCO + DIV2 cut — see §5) | ⬜ Not started | Greg (solo; Zach out ~2 wks) |
| **Aug 21** | Dry-run block GDS | **Block-footprint GDS with specified pad types** (fixed placement; organizer-scripted padframe integration) → channel partner | ⬜ Not started | Greg |
| **Aug 28** | Verification + final review | Full-chip DRC/LVS/antenna clean, final GDS | ⬜ Not started | Team |

---

## 2. Reviewer conditions → status (schematic-review Conditional-Go)

Addresses review condition 8 (milestones + fallback reflecting unstarted blocks).

| # | Condition (Caglar) | Action | Status | Owner |
|---|--------------------|--------|--------|-------|
| 1 | Freeze reduced minimum scope | `scope.md` tiers frozen | 🟢 Done (this update) | Greg |
| 2 | Consistent frequency plan + feasible divider | Plan B (VCO band **4.05–6.38 GHz** corrected ÷2, `verification.md §3.2`). **`DIV2_QUAD_v1` NOW DIVIDES** — Phase-3 self-biased AC-coupled converter removed the threshold-match failure class; every corner 2.500 GHz + exact 270° quadrature; schematic regenerated from `gen_div2_quad.py`. See `div2-debug.md` (2026-08-12) | 🟢 Done | Greg/CC |
| 3 | PLL diagram must include CP + loop filter | Corrected chain in `scope.md` §2 | 🟢 Done | Greg |
| 4 | Verify PFD for lead / lag / equal-freq | 3-case PFD sim; min reset pulse re-confirmed **0.500 ns** (`verification.md §3.2` container check) | 🟢 Done | Greg |
| 5 | Full VCO characterization | swing/startup/power/PVT done (`verification.md §3.2`); f-VTUNE corrected (7/30 mid-curve was an error, container proven stable); **KVCO −1.1 GHz/V near ISM**; phase noise NOT measurable with open-source toolchain (no PSS/HB) | 🟢 Done (phase-noise gap documented) | CC |
| 6 | Inductor model is preliminary | Mohan cross-check (6.1) done — **CONFIRMS 1.2 nH** (turns read from `.mag`: two 3-turn D_out=76µm halves in series ⇒ ~1.08 nH vs 1.2, within ~10%). Plan B band stands, ISM reachable. EM (6.2) = Q/SRF refinement, not critical-path; openEMS install QUEUED | 🟡 6.1 done, 6.2 queued | Zach/CC |
| 7 | On/off-chip partition + test approach | `pins.md` partition + per-pad test notes | 🟢 Done (v1) | Greg |
| 8 | Milestones + fallback scope | This file + `scope.md` §6 | 🟢 Done | Greg |

---

## 3. Near-term task backlog

| Task | Blocks | Owner | Target |
|------|--------|-------|--------|
| Post area + pin data to issue #143 | Jul 31 form | Greg | Jul 31 |
| VCO f–VTUNE sweep → finalize freq plan | cond. 2, `scope.md` §3 | Zach/Greg | pre-Aug 6 |
| Resolve `PFD_v1` / `D_FF_RST_v1` / `NAND3_v1` symbol↔schematic pin mismatch | cond. 4 | Greg | pre-PFD sim |
| Project rail decision (1.8 V tb sources vs 3.3 V cells vs CP at 3.3 V) | Phase-3 sims | Greg + team | pre-mass-sim |
| PFD 3-case + PFD+CP integration sim | cond. 4 | Greg | pre-Aug 6 |
| VCO characterization suite | cond. 5 | Zach | pre-Aug 6 |
| Inductor re-extraction | cond. 6 | Zach | pre-Aug 6 |
| librelane workshop-slot flow → sample GDS + DRC | Aug 6 gate | Greg | Aug 6 |
| Cell layouts (NOT→NAND3→DFF→D_FF_RST→PFD→CP) | Aug 14 | Greg | Aug 7–14 |
| VCO/tank layout around inductor | Aug 14 | Zach/Greg | Aug 14 |
| Top-level place in slot + padframe → GDS | Aug 21 | Greg | Aug 21 |

---

## 4. Consolidation status (repo)

- **`lvs/lvs_config.json` `TOP_SOURCE = chip_top` is an Aug-6 dry-run placeholder**
  (workshop-slot sample GDS, the only cell with a real layout). **Must be repointed
  at the integrated RFIC top before the Aug 21 block GDS.**
- Working integration branch: `integration` = `reset-dff-wip` + `main` (VCO) +
  `cp-wip` (CP), merged clean, all testbenches netlist. Not yet pushed to origin.
- Docs live under `docs/` (`scope.md`, `pins.md`, `tracking.md`, and
  `verification.md` once Phase-3 sims run).
- **`ibias_gen_v1` layout DONE + signed off (2026-08-14, `verification.md §2.6.1`):**
  full-custom Magic, Magic DRC 0 / KLayout DRC 0 / netgen LVS match uniquely (228 fingers,
  6 ports, `verify_cp.sh` exit 0). **Golden intentionally has one more device than the
  schematic:** `ibias_gen_v1_golden.spice` = the 16 `.sch` devices **+ one tied-off layout
  dummy** (`XMDUM`, m=4) on the 24:5 mirror array. The schematic is NOT edited; any
  full-chip LVS off `ibias_gen_v1.sch` must add the same tied-off dummy or waive the
  one-device count delta. See `verification.md §2.6.1`.

---

## 5. Layout scope decision — Aug 14 (frozen 2026-08-05)

**Context:** Zach is unavailable ~2 weeks (not drawing VCO/inductor for Aug 10–21).
One person (Greg) doing the layout. Deliberate choice: **two blocks fully DRC+LVS
clean and documented beats four half-done** (`scope.md §6` fallback ladder).

**Layout flow (split, decided 2026-08-05):** **PFD = library std cells via LibreLane**
(5 gf180 cells, our topology, re-verified `verification.md §2.2`); **CP_v1 = manual
Magic + netgen LVS** (full-custom analog). VCO/CP need the manual flow regardless.

| Block | Status | Notes (updated 2026-08-15) |
|-------|--------|--------|
| **PFD (`PFD_lib`)** | ✅ **DONE** | **LibreLane layout DRC+LVS clean, all 4 gates passed** (`verification.md §2.3`): Magic/KLayout DRC 0, 2× inv_1 reset delay preserved, REF/FB symmetric (~36 fs), LVS matches golden. Signoff GDS `gds/PFD_lib.gds` |
| **CP_v1** | ✅ **DONE** | Full-custom Magic; **Magic DRC 0 + KLayout signoff DRC 0 + netgen LVS match uniquely** (8 devices / 10 nets / 7 ports), `verify_cp.sh CP_v1` **exit 0** (gate passed 2026-08-13, re-confirmed 2026-08-15); `gds/CP_v1.gds`. Physical-matching refinement (dummies, full guard rings, PEX) DEFERRED. Numbers file-cited in `docs/layout-review-aug14.md` |
| **`ibias_gen_v1` (5.2)** | ✅ **CLOSED** | Bias generator (chip-level, fans out to CP + DIV2 tails). Full-custom; `verify_cp.sh` exit 0 (Magic/KLayout DRC 0, LVS match uniquely). Signed off |
| **DIV2 (`DIV2_QUAD_v1`) (5.3)** | ✅ **CLOSED (1f)** | **DIV2_QUAD_v1 SIGNED OFF** — full quad-phase ÷2, 75 devices (2 CML latches + 3 NMOS bias + 4 slicer converters). **verify_cp.sh DIV2_QUAD_v1 exit 0 vs the GDS** (magic DRC 0, netgen LVS match uniquely, 9 ports CK CKB IBIAS I_P I_N Q_P Q_N VDD VSS, 0 property/port errors) + **KLayout DRC 0 (variant D)**. Golden regenerated via `mk_div2_golden.py` from the .sch (PDK xschemrc, 59 FETs) — identical to committed. **Measured bbox 237.4 × 174.2 µm = 41,340 µm²** (vs 36,500 projection, +13%). Floorplan: 4 converters at the corners, core+bias centred (option-c: IP/QP east-unmirrored, IN/QN west-mirrored). Render in `_cp_work/DIV2_QUAD_v1.png`. **VSS EM (CONFIRMED by sim 2026-08-17; fix scoped + deferred, does NOT block sign-off):** total VSS **22.4 mA** (div2_sb_TT deck i(V_VDD), matches validated headline); **per-converter VSS 2.96 mA** (measured via a 0 V meter split into the IP return). Open gf180mcuD PDK ships NO EM deck at all → compared against an INDUSTRY RULE OF THUMB ~1 mA/µm for ~0.5µm Al (M1–M4), NOT a consulted GF-manual limit. Over-limit everywhere: 7.5 µm plate ~2.3–2.9 mA/µm; ties 0.28–0.56 µm ~5.3–10.6 mA/µm; AND the ROOT bottleneck is ib_conv_v1's internal 0.6 µm M1 VSS bus (line 117) ~4.9 mA/µm. **Fix scope (deferred to prioritise 5.4 VCO):** widen ib_conv_v1's internal VSS bus to ~3 µm + re-verify the cell + all 4 instances; stack the plate on M2+M3+M4 (it is boxed in by bias/latch-B, no in-plane room) to ~22 µm equiv; widen the 4 top ties to ~3 µm; re-gate DIV2_QUAD_v1. Numbers written into `layout-review-aug14.md` DIV2.2. --- HISTORY: Stage C IN GATE-PASSED (47 dev, 11 ports). IN = west, **MIRRORED** (`getcell ib_conv_v1 ; sideways` — NO `select cell`; mirror-x about bbox centre, native px→bxN+9612-px), latch A, INP=OI INM=OIB. Orientation = **option (c)**: P-east-unmirrored (IP/QP), N-west-mirrored (IN/QN) → I&Q identical so mirror offset cancels in quadrature (see div2-layer-plan.md). **West-converter routing rule**: every tap-side riser must cross IP's haul band (OIB M5@5500, OI/INM M4@5800, VDD M4@6500, all span the core) on **M3**, then via_m3m5 to its M5 haul above the band; VDD = short low M4 hop to the mirrored bus; INM escapes EAST of the mirrored CC cap. **Stage B (IP) recap**: getcell'd HIERARCHICAL child (NOT a 2nd flatten — shatters CML folds); 6 nets over-the-top; I_P painted over child OUT. **verify_cp env bug fixed en route**: the ONLY real issue was the container's ambient `PDK=ihp-sg13g2` — verify_cp derives its netgen setup from `$PDK`, so it silently used IHP device rules and nothing LVS'd. Source `/foss/tools/sak/sak-pdk-script.sh gf180mcuD` (sets PDK) or run `PDK=gf180mcuD PDK_ROOT=/foss/pdks verify_cp.sh <cell>`. (An `ext2spice merge aggressive` line was added then REVERTED — it was a misdiagnosis: netgen itself combines the folded fingers via the gf180 setup, so the stock no-merge `verify_extract.tcl` matches uniquely once the PDK is right. Confirmed: ibias_gen_v1 228→match, ib_div2 146→match, CP_v1 38→match with the stock script.) Remaining: **Stage C** (3 more converters IN=OI/OIB/I_N, QP=OQB/OQ/Q_P, QN=OQ/OQB/Q_N → 75-device golden via `mk_div2_golden.py`) + **D** (rename to DIV2_QUAD_v1, 9 top ports, `verify_cp.sh DIV2_QUAD_v1` exit 0, closes 5.3). Stage B's `getcell ib_conv_v1` + 6-net route is the proven template for C. |
| **VCO (`vco_v1`) (5.4)** | 🟡 **IN PROGRESS — devices de-risked, inductor measured** | Complementary cross-coupled LC (from `vco_v1.sch`, netlisted): 2×nfet_03v3 W40 L0.28 + 2×pfet_03v3 W70 L0.28 (cross-coupled), 2×`cap_nmos_03v3_b` varactor (5×5µm, m=21) + 1×`ppolyf_u_3k` tune R (1×5µm=15kΩ), + `vco_inductor_v2` spiral (1.2nH, LVS waiver W3 = pi-model). **De-risk (2026-08-17):** (a) varactor = `gf180mcu::nmoscap_3p3` gencell, w5 l5 → **DRC 0, extracts as `cap_nmos_03v3_b`** (matches netlist), unit bbox 7.44×7.06µm; m=21 → place 21 units parallel (netgen combines). (b) **`ppolyf_u_3k` RESOLVED (2026-08-17):** it is the SAME PHYSICAL DEVICE as `ppolyf_u_1k` — both extract from the identical layer `ppolyf_u_h` (`= poly2·sab·res_mk·resistor`, res_derivations:125); 1k-vs-3k is a fab PROCESS VARIANT (`when '1k'`/`when '3k'` in the KLayout deck), not a layout/marker difference. Magic's tech (gf180mcuD.tech:4156, `hires`→ppolyf_u_1k) has NO 3k device, so magic extracts the identical layout as `ppolyf_u_1k`. **→ Draw with the `ppolyf_u_1k` gencell (w1 l5); verify_cp needs a 1k↔3k relabel WAIVER** (PROVEN: relabel golden 3k→1k → netgen match uniquely; netgen `equate classes` does NOT take for device classes, 3 syntaxes tried). Analogous to inductor W3 — waiver-vs-design-change is Greg's call. (c) **pfet W70 de-risked:** `pfet_03v3 w70 l0.28 nf10` → DRC 0, extracts `w=70u l=0.28u`, bbox 9.98×72.1µm (netgen merges to match golden nf=1). **Inductor bbox MEASURED: `vco_inductor_v2.mag` = 36,400×16,800 iu = 182×84µm** (dual square spiral D_out=76, 5nm/iu). **VCO die-size estimate: inductor-dominated, ~190×90µm ≈ 17,000µm²** (core = varactor array ~35×35 + 4 FETs + R, small vs the inductor). **Remaining:** draw the 3k R, build the 4-FET cross-coupled core (nfet W40 have; pfet W70 gencell) as a standalone rung, place the inductor + varactors, route the tank, gate `verify_cp.sh vco_v1` with the inductor pi-model netgen ignore (W3). |
| **`vco_inductor_v2`** | ✅ **layout DRC-clean** | 182 × 84 µm drawn cell (`team_src/magic/vco_inductor_v2/`); spiral LVS is waiver W3. **Inductor EM re-extraction DEFERRED** (conducting-sheet `ind_em.py` fix, cond. 6) |

> **PFD_lib signoff artifact:** `team_src/magic/PFD_lib.mag` is an unrouted 5-cell placement
> scaffold generated by `team_src/magic/place_pfd.tcl`, retained as a reproducible reference
> for the cell abutment. It is **not a signoff layout and is not LVS-clean**. The committed
> **`gds/PFD_lib.gds` is the sole signoff artifact** for this block.

### 5.1 Area recompute — real drawn extents (2026-08-15)

Measured from the actual `.mag`/GDS bounding boxes (magic `select top cell; box`,
1 µm = 200 internal units; the `vco_inductor_v2` 182 × 84 µm cross-checks the earlier
figure and pins the conversion):

| Block | Real bbox (µm) | Area (µm²) | Source | vs `scope.md §5` estimate |
|-------|---------------|-----------:|--------|---------------------------|
| PFD_lib | 57.0 × 24.0 | 1,368 | `gds/PFD_lib.gds` | est. ~815 (digital) → **+68 %** |
| CP_v1 | 73.5 × 28.0 | 2,059 | `gds/CP_v1.gds` | est. ~1,200 → **+72 %** |
| ibias_gen_v1 | 181.8 × 65.3 | 11,868 | `team_src/magic/ibias_gen_v1.mag` | **not separately budgeted** in §5 |
| **DIV2_QUAD_v1 (5.3)** | 237.4 × 174.2 | **41,340** | `gds/DIV2_QUAD_v1.gds` | 5.3 CLOSED (was "in progress") |
| vco_inductor_v2 (VCO tank) | 182.0 × 84.0 | 15,288 | `…/vco_inductor_v2.mag` | part of the VCO block below |
| **Sum, 4 signed-off blocks** | — | **56,635** | PFD+CP+ibias+DIV2 | — |

**Honest top-level number (CORRECTED 2026-08-17):** the four signed-off blocks measure
**56,635 µm²** (PFD_lib 1,368 + CP_v1 2,059 + ibias_gen_v1 11,868 + DIV2_QUAD_v1 41,340). The
**VCO block is ~18,000 µm²** — inductor-DOMINATED (measured 15,288) plus a small active core
(~2.7 k), NOT the ~43 k the §5 bottoms-up guessed. So blocks ≈ **56,635 + 18,000 = ~75,000 µm²**;
add 30–50 % top-level routing/spacing → **~96,000–114,000 µm²**. The declared **350 × 300 =
105,000 µm²** **STRADDLES** that range — **tight but plausible**, not "short by 40 %". The earlier
"350×300 falls short / needs 370×390 or 400×400" conclusion was built on the guessed 43 k VCO
block and is **retracted**. The real figure arrives at top-level assembly (Phase 7). Per-block
utilization is not recomputed (needs extraction; areas are footprints). #143's area line is **not
edited** (browser action, Greg's to hand-update).

### 5.2 Density check (drop-gate) — 2026-08-15

Bailey: minimum clear density MUST pass; final-DRC failures likely dropped. Ran KLayout
`run_drc.py --density_only --variant=D`, **one cell per invocation**, on all four drawn
blocks. **ALL FOUR FAIL — every failure is a MINIMUM-coverage floor** (`>= X%`, i.e. *too
little* metal), never a max-density violation. Actual coverage (merged layer area / cell
bbox) vs threshold:

| Cell | COMP ≥25% | Poly2 ≥14% | Metal M1…MTop (≥30% each) | Verdict |
|------|-----------|------------|----------------------------|---------|
| PFD_lib | 21.4% (**−3.6**) | 19.1% ✓ | M1 22.8%; M2–M4 1–4%; M5/MTop 0% | FAIL |
| CP_v1 | 17.9% (**−7.1**) | 15.0% ✓ | M1–M5 1.2–3.7%; MTop 0% | FAIL |
| ibias_gen_v1 | 40.6% ✓ | 32.5% ✓ | M1 5.8%, M2 4.3%, M3–M5 0.1–0.7%; MTop 0% | FAIL |
| vco_inductor_v2 | 0% (absent) | 0% (absent) | M4 5.5%; **M5 60.9% ✓**; rest 0% | FAIL |

**Root cause: no metal fill.** These are sparse standalone blocks — metal exists only where
signals route, so every metal layer sits far below the 30 % floor (fill-class failures, not
layout defects). ibias is device-dense enough to pass COMP+Poly2; the inductor passes M5
(the spiral) only. **This is the expected pre-fill state; dummy-metal fill is inserted at
integration to meet these minimums.** Bailey's "minimum density MUST pass" governs the FINAL
integrated GDS (with fill), not these pre-fill blocks. **Fill strategy deliberately NOT
attempted** — it is a design decision (Greg's), and fill choice interacts with the analog
matching / shielding (guard rings, CP_OUT shield, inductor keep-out). Rules hit: DCF.1b (COMP),
PL.8 (Poly2, inductor only), M1.4/M2.4/M3.4/M4.4/M5.4 (metal1–5), MT.3 (MetalTop).

Rubric caveat: the authoritative layout-review requirements land at the **Aug 7
session** (not yet held); the CP/PFD content stays valid but extra artifacts
(PEX/ESD numbers, specific doc format) may be added once the rubric is known.

---

## 6. Aug-10/14 layout-review rubric status (2026-08-05)

Full evidence in `docs/layout-review-aug14.md` (all numbers file-read from run
`librelane_pfd/runs/RUN_2026-08-05_23-52-38`).

| Rubric row | Score | Status |
|---|---|---|
| 1 DRC/LVS correctness | **3/3** | PFD_lib: Magic 0, KLayout 0, route 0, netgen LVS match uniquely |
| 2 Power / ground / current | **3/3** | PDN M1 rail + M4/M5 straps; IR drop VDD 9.6 µV / VSS 18.2 µV, 0 PG violations |
| 3 Analog matching / isolation | **N/A (PFD) · CP drawn, refinement deferred** | PFD under no-analog clause; **CP_v1 drawn + DRC/LVS-clean**, but dummies / full guard rings / PEX matching DEFERRED (see `layout-review-aug14.md` CP.3) |
| 4 Reliability | **2/3** | antenna 0, latch-up DRC-clean (tap-dist setting caveat); EM/ESD/PEX NOT DONE |
| 5 Top-level integration | **2/3** | names match, lvs_config repointed to PFD_lib; block ≠ integrated top |

- **Aug 10 (layout reviews due):** PFD_lib fully closes rows 1, 2, 5 with file-read
  evidence + a rendered image; the review doc is written.
- **Aug 14 (block layout reviews):** PFD_lib **DONE**; **CP_v1 is the open block** —
  golden + drawing packet ready, layout awaiting the GUI draw (`docs/cp-layout-packet.md`).
- **CAT 3 status (updated 2026-08-15):** CP_v1 **is drawn and gate-passed** — Magic DRC 0,
  KLayout signoff DRC 0, netgen LVS match uniquely, `verify_cp.sh` exit 0. Physical-matching
  refinement (dummy fingers, complete guard rings, extracted/PEX matching) is **DEFERRED** —
  that is now the residual CAT 3 gap, not the whole block.
- **`main` freeze condition is now MET.** The old rule held `main` at `20dd3b4` until CP_v1 was
  drawn AND `verify_cp.sh CP_v1` passed, so the `docs/layout-review-aug14.md` CP_v1 section
  (which #143's `blob/main` links track) would not resolve to a page full of `[TODO]`s. Both
  are now true and that section carries real, file-read numbers, so **advancing `main` is
  unblocked — pending Greg's explicit push approval** (`origin/integration` carries the
  commits; the push itself is a separate, manually-approved action).
- Submission repointing: `lvs/lvs_config.json` `TOP_SOURCE` = `PFD_lib`; GDS committed at
  `gds/PFD_lib.gds`, netlist at `lvs/PFD_lib.nl.v` (supersedes the chip_top placeholder for
  the layout review; the integrated RFIC top still governs before Aug 21).

### Aug-10 submission status (2026-08-05)
- **Pushed:** `origin/integration` = `origin/main` = **`a471788`** (main fast-forwarded from
  `6e0f01d`, carrying the CP golden/drawing-packet docs + the PFD_lib review; clean FF).
- **Review doc (verified-resolving permalink):**
  `https://github.com/Zachnad0/AUS-NZ-Track-A-RFIC-Workspace/blob/a4717886eb510d2d1def592887ec62608c509058/docs/layout-review-aug14.md`
- **#143 comment: DRAFTED, NOT YET POSTED** — no GitHub-write path from this environment
  (`gh` absent); Greg pastes the drafted comment (`scratchpad/issue143_aug14_review_draft.md`).
- Weekly-form checkboxes: info.yaml ✅; lvs_config.json + relative path ✅; layout-review docs
  written + linked ✅ **once the #143 comment is posted** (doc itself is on main and resolves).
