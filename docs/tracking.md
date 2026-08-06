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
| 2 | Consistent frequency plan + feasible divider | Plan B final (VCO 4.11–6.37 GHz ÷2); static CMOS eliminated, **CML ÷2 proven** (clean to 5 GHz), band-top + quadrature WIP; 4 I/Q buffers added. **`DIV2_QUAD_v1` (core+mirror+buffers packaged) is built + netlist-clean but does NOT divide in sim yet — WIP, see `docs/div2-debug.md`** | 🟡 In progress | Greg |
| 3 | PLL diagram must include CP + loop filter | Corrected chain in `scope.md` §2 | 🟢 Done | Greg |
| 4 | Verify PFD for lead / lag / equal-freq | 3-case PFD sim; **resolve sym/sch pin mismatch first** | 🟡 Queued | Greg |
| 5 | Full VCO characterization | f-Vtune, KVCO, power, swing, startup, corners → `verification.md` | 🟡 Queued | Zach |
| 6 | Inductor model is preliminary | Re-extract L/Q/SRF vs `.subckt` | 🟡 Queued | Zach |
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
| **DIV2 (`DIV2_QUAD_v1`)** | ❌ **CUT** | Schematic **not frozen** — output buffer doesn't switch (`div2-debug.md`); laying out a broken cell is wasted work. Revisit for Aug 21 |

Rubric caveat: the authoritative layout-review requirements land at the **Aug 7
session** (not yet held); the CP/PFD content stays valid but extra artifacts
(PEX/ESD numbers, specific doc format) may be added once the rubric is known.
