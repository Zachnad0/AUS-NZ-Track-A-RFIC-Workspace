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
| 6 | Inductor model is preliminary | Mohan cross-check (6.1) done — **does NOT confirm 1.2 nH** (0.5–2 nH range), EM elevated to critical-path; openEMS/FastHenry install QUEUED | 🟡 6.1 done, 6.2 queued | Zach/CC |
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

---

## 5. Layout scope decision — Aug 14 (frozen 2026-08-05)

**Context:** Zach is unavailable ~2 weeks (not drawing VCO/inductor for Aug 10–21).
One person (Greg) doing the layout. Deliberate choice: **two blocks fully DRC+LVS
clean and documented beats four half-done** (`scope.md §6` fallback ladder).

**Layout flow (split, decided 2026-08-05):** **PFD = library std cells via LibreLane**
(5 gf180 cells, our topology, re-verified `verification.md §2.2`); **CP_v1 = manual
Magic + netgen LVS** (full-custom analog). VCO/CP need the manual flow regardless.

| Block | Aug 14 | Status |
|-------|--------|--------|
| **PFD (`PFD_lib`)** | ✅ **DONE** | **LibreLane layout DRC+LVS clean, all 4 gates passed** (`verification.md §2.3`): Magic/KLayout DRC 0, 2× inv_1 reset delay preserved, REF/FB symmetric (~36 fs), LVS matches golden. GDS in `librelane_pfd/runs/…/final/gds/` |
| **CP_v1** | 🟡 **TARGET (next)** | Self-contained analog; sizing frozen; ~2 d manual Magic. Analysis + golden + floorplan headless; Greg draws (matching/guard-ring) |
| **VCO core** | ❌ **CUT** | Full-custom RF, high effort; **Zach out** — cannot be drawn by Aug 14 |
| **DIV2 (`DIV2_QUAD_v1`)** | ❌ **CUT** | Schematic **not frozen** — output converter doesn't switch in steady state (`div2-debug.md`, 2026-08-10: 3-stage rework, threshold-matching class fault); laying out a broken cell is wasted work. Revisit for Aug 21 |

> **PFD_lib signoff artifact:** `team_src/magic/PFD_lib.mag` is an unrouted 5-cell placement
> scaffold generated by `team_src/magic/place_pfd.tcl`, retained as a reproducible reference
> for the cell abutment. It is **not a signoff layout and is not LVS-clean**. The committed
> **`gds/PFD_lib.gds` is the sole signoff artifact** for this block.

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
| 3 Analog matching / isolation | **N/A (PFD) · NOT YET (CP)** | PFD under no-analog clause; **CP_v1 layout not drawn** ← the gap |
| 4 Reliability | **2/3** | antenna 0, latch-up DRC-clean (tap-dist setting caveat); EM/ESD/PEX NOT DONE |
| 5 Top-level integration | **2/3** | names match, lvs_config repointed to PFD_lib; block ≠ integrated top |

- **Aug 10 (layout reviews due):** PFD_lib fully closes rows 1, 2, 5 with file-read
  evidence + a rendered image; the review doc is written.
- **Aug 14 (block layout reviews):** PFD_lib **DONE**; **CP_v1 is the open block** —
  golden + drawing packet ready, layout awaiting the GUI draw (`docs/cp-layout-packet.md`).
- **CAT 3 gap (explicit):** the analog block CP_v1 has **no drawn layout**, so no
  matching/symmetry/guard-ring/noise-isolation evidence exists yet. This is the single
  largest remaining Aug-14 item.
- **⚠ DO NOT fast-forward `main` yet. `main` stays at `20dd3b4` until CP_v1 is drawn AND
  `verify_cp.sh CP_v1` passes.** `docs/layout-review-aug14.md` now carries a CP_v1 section
  that is entirely `[TODO]` placeholders, and #143's body links track `blob/main` — if `main`
  advances to include it before CP_v1 is real, reviewers following those links open a document
  full of TODOs. Advance `main` only once the CP_v1 section has real, file-read numbers.
  (`origin/integration` may carry the work-in-progress commits; `main` must not.)
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
