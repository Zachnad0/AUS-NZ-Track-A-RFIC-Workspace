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
| **DIV2 (`DIV2_QUAD_v1`) (5.3)** | 🟡 **IN PROGRESS — 1f prepped** | Schematic frozen (`gen_div2_quad.py`→`.sch`, `f600af3`). **1d CML latch + 1e converter both GATE-PASSED** (magic DRC 0 + KLayout DRC 0 var-D + LVS match uniquely; ib_cml, ib_conv_v1). **1f target golden generated: 75 devices** (39 nfet + 20 pfet + 12 res + 4 cap; `DIV2_QUAD_v1_golden.spice`). Both instantiated blocks are the proven flat recipes. **Remaining (1f): flat assembly** of 2 latches (12 CML W40 nfets MA1-6/MB1-6 + 4×300R) + 3 NMOS bias (M_BREF W4 / M_TAILA,B W40, L1, off IBIAS) + 4 converters (ib_conv_v1 recipe: IP=OIB/OI/I_P, IN=OI/OIB/I_N, QP=OQB/OQ/Q_P, QN=OQ/OQB/Q_N) + inter-band routing (quadrature OI/OIB/OQ/OQB latch→converter, TAILA/TAILB, IBIAS fan-out, CK/CKB, VDD/VSS, 4 outputs), 9 ports. GATE `verify_cp.sh DIV2_QUAD_v1` exit 0. Est. multi-session (converter alone was one session) |
| **VCO core (5.4)** | ⬜ **NOT STARTED** | Full-custom RF; the inductor is drawn (below). Blocked on 5.3 close |
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
| vco_inductor_v2 | 182.0 × 84.0 | 15,288 | `…/vco_inductor_v2.mag` | 15,288 measured (matches) |
| **Sum drawn** | — | **30,583** | — | — |

**Honest top-level number:** the **350 × 300 µm = 105,000 µm²** in `scope.md §5` and #143
**remains an estimate, not a measured die** — the two largest contributors are still
undrawn: the **VCO active core** (~28 k µm² beyond the inductor, from §5's 43 k VCO-block
figure) and the **full DIV2 block** (5.3, in progress). The drawn finished blocks total
**30,583 µm² ≈ 29 %** of the 105 k budget. Two facts erode the old slack: CP_v1 and PFD_lib
came in ~70 % over their bottoms-up estimates, and **ibias_gen_v1 (~11.9 k µm²) was never in
the §5 bottoms-up** at all. So 350 × 300 is still the working planning rectangle but should be
treated as a **firm floor, not a 2×-slack target** — revisit once the VCO core and DIV2 are
drawn. Per-block device utilization is not recomputed here (needs extraction; the areas above
are footprints). #143's area line is **not edited** (browser action, Greg's to hand-update).

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
