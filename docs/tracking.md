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
| **VCO (`vco_v1`) (5.4)** | 🟢 **CLOSED (2026-08-20) — `verify_cp.sh vco_v1` exit 0 (DRC 0, LVS match uniquely, ISS & GND SEPARATE), KLayout var-D 168 = W4 only. bbox 182 × 179.5 µm. Re-sim 4.13–6.35 GHz.** | Complementary cross-coupled LC (from `vco_v1.sch`, netlisted): 2×nfet_03v3 W40 L0.28 + 2×pfet_03v3 W70 L0.28 (cross-coupled), 2×`cap_nmos_03v3_b` varactor (5×5µm, m=21) + 1×`ppolyf_u_3k` tune R (1×5µm=15kΩ), + `vco_inductor_v2` spiral (1.2nH, LVS waiver W3 = pi-model). **De-risk (2026-08-17):** (a) varactor = `gf180mcu::nmoscap_3p3` gencell, w5 l5 → **DRC 0, extracts as `cap_nmos_03v3_b`** (matches netlist), unit bbox 7.44×7.06µm; m=21 → place 21 units parallel (netgen combines). (b) **`ppolyf_u_3k` RESOLVED (2026-08-17):** it is the SAME PHYSICAL DEVICE as `ppolyf_u_1k` — both extract from the identical layer `ppolyf_u_h` (`= poly2·sab·res_mk·resistor`, res_derivations:125); 1k-vs-3k is a fab PROCESS VARIANT (`when '1k'`/`when '3k'` in the KLayout deck), not a layout/marker difference. Magic's tech (gf180mcuD.tech:4156, `hires`→ppolyf_u_1k) has NO 3k device, so magic extracts the identical layout as `ppolyf_u_1k`. **→ Draw with the `ppolyf_u_1k` gencell (w1 l5); verify_cp needs a 1k↔3k relabel WAIVER** (PROVEN: relabel golden 3k→1k → netgen match uniquely; netgen `equate classes` does NOT take for device classes, 3 syntaxes tried). Analogous to inductor W3 — waiver-vs-design-change is Greg's call. (c) **pfet W70 de-risked:** `pfet_03v3 w70 l0.28 nf10` → DRC 0, extracts `w=70u l=0.28u`, bbox 9.98×72.1µm (netgen merges to match golden nf=1). **Inductor bbox MEASURED: `vco_inductor_v2.mag` = 36,400×16,800 iu = 182×84µm** (dual square spiral D_out=76, 5nm/iu). **VCO die-size estimate: inductor-dominated, ~190×90µm ≈ 17,000µm²** (core = varactor array ~35×35 + 4 FETs + R, small vs the inductor). **RUNG 3a DONE (2026-08-18): 4-FET cross-coupled core `vco_core` BUILT + SIGNED OFF** — magic DRC 0, **KLayout DRC 0 (variant D)**, **netgen LVS "Circuits match uniquely"** vs a 4-device golden (`vco_core_golden.spice`), 4 ports ISS/VDD/OUT_p/OUT_n. **Measured bbox 28.55 × 30.25 µm = 863 µm²** (core only; replaces the ~2.7k guess — varactors/inductor add the rest). Built via `phase5/vco_core.tcl` (committed). Build facts locked in: **(1) pfet W70 folds as nf5/w14** (per-finger W=7→total 70; `pfet_leg` PG=100·W, rail-y, and tap-offset all scale with W but were tuned at W16 — nf10/w7 PG=700 does NOT DRC-clean, the compressed tap fails; nf5/w14 PG=1400 works with `tapy=-1500` + a short M2 riser covering the tap via up to the VDD rail). **(2) `nfet_leg` tap-offset FIXED (2026-08-18, commit 5033a5f):** the +252 tap-x offset was tuned for L=2 pitch (504) and collided with a source via at L0.28 (160). Changed to a pitch-relative **offset P** (not P/2 — the nfet tap shares the source-rail y, unlike the pfet's, so P/2 still collides; offset P lands the tap at a drain-column midpoint, clean at every pitch). Regression: ib_nmir4/ib_nmos/ib_pmir all magic DRC 0 + LVS match uniquely (L=2 tap moves 252→504 but passes; their committed .mag left as-is to avoid re-gating ibias_gen_v1, ib_block.tcl authoritative). **vco_core rebuilt with taps=1, hand-painted pwell removed, re-gated clean** (magic DRC 0, KLayout var-D 0, LVS match uniquely, same bbox). **(3) `via_m2m4` paints no M2** → explicit M2 pads at every M4-bus via. Cross-couple routed OUT_p on far-left M3 bus / OUT_n on far-right M4 bus. Golden terminals (from `vco_v1.sch`): nfet bulk=ISS, pfet bulk=VDD — matches leg taps=1 (bulk→source rail), no special-casing. **RUNG 3b DONE (2026-08-18): differential varactor array `vco_varactors` BUILT** — 42× `cap_nmos_03v3_b` (nmoscap_3p3 w5 l5) = XC1 cap_bias↔OUT_n m21 + XC4 cap_bias↔OUT_p m21. 6 cols × 7 rows, pitch X 1560 / Y 1500; **mirror-symmetric** about the vertical centre (cols 0-2 wells→OUT_n, cols 3-5→OUT_p) for differential match; all 42 gates→cap_bias. Gate col buses (M2)→cap_bias M3 rail top; well col buses (M2)→OUT_n/OUT_p M3 rails bottom; guard (psubdiff) auto-ties to substrate. **bbox 46.7 × 54.5 µm.** Gate: **magic DRC 0**, **netgen LVS match uniquely** (42 units combine to 2× m=21). **KLayout var-D: 168 items = EXACTLY 2/unit (42×2) PL.5a_LV/PL.5b_LV** ("field Poly2 to guard-ring"); bussing is M1/M2/M3 only (no poly) and the count is per-unit → INTERNAL to the nmoscap_3p3 gencell, a magic-vs-KLayout device discrepancy like DF.14_LV/NP.1 → **WAIVER W4 (Greg's call, cf inductor W3) — CONFIRMED 2026-08-18:** a BARE single nmoscap_3p3 unit under KLayout var-D shows exactly 2 PL.5a_LV + 2 PL.5b_LV (4 items); 42 units × 4 = 168, zero from bussing. 100 % device-internal. **Contact recipe (proven, `phase5/vco_varactors.tcl`):** unit at box(X,Y) lands child CENTRE at (X+714,Y+676); gate poly-contact M1 at (X+714, Y+676±556); well (nsubdiff) M1 at (X+162, Y+676). The earlier "well won't bus / NW.2a / abut-to-merge" dead-ends were all a **flatten coordinate offset (+714,+676)** — not real access problems; spaced grid at pitch ≥1556(X)/≥1480(Y) clears NW.2a and DF.3a with room. **RUNG 3c WIP DONE (2026-08-18): assembly `vco_v1` PLACED + core↔varactor tank ROUTED** (`phase5/vco_v1.tcl`) — hierarchical getcell of inductor+core+varactor (MASTERS PRE-LOADED or getcell silently drops the instance from the .mag — that bit us: a repo-root `gds write` also loses children not on the search path). Floorplan: inductor native, core+varactor stacked below under the coil centre channel. **bbox 182 × 179 µm.** core↔varactor tank verified DISTINCT (`.subckt vco_v1 VDD ISS OUT_p OUT_n cap_bias`, OUT_p/OUT_n each tie core+var; core OUT_p M3 exits left / OUT_n M4 exits right, up into the clear core-top↔inductor-bottom channel, vias staggered so crossing nets never share a layer). **magic DRC 0; KLayout var-D = 168 = only the 42×4 W4 varactor waiver, ZERO new items from the assembly.** **INDUCTOR-PORT CONNECT DEFERRED (closes 3c):** the dual-spiral's PORT1/PORT2 are M5 leads INTERIOR to one DC-continuous coil; a bus run up to them touches the coil (one node) not the labelled terminal — OUT_p reached PORT2, OUT_n would not reach PORT1, and any real connect DC-merges OUT_p/OUT_n through the coil (correct for an inductor, needs W3 black-box at LVS). Next: use the inductor's designed feed (bottom tails) or re-export edge ports. **RUNG 3d DONE (2026-08-18): tune resistor `vco_tune_r`** — `ppolyf_u_1k` w1 **l15** = 15 squares = 15 kΩ (1k variant, Greg's decision). magic DRC 0, KLayout var-D 0, **netgen match uniquely** vs a ppolyf_u_1k l15 golden. Ports TUNE/cap_bias/GND. **NO 1k↔3k relabel waiver** (golden built as 1k → direct match; drops one planned waiver). .sch still says ppolyf_u_3k w1 l5 → device+length change + tune-range re-sim is Greg's (rule 13). **GDS HIERARCHY AUDIT (2026-08-18):** every committed GDS checked — cells-in-GDS vs .mag `use`: CP_v1 ✓(flat), DIV2_QUAD_v1 ✓(+ib_conv_v1, ib_conv_v1 is flat), PFD_lib ✓(GDS superset incl fill/tie the .mag import dropped), vco_core ✓(flat), vco_varactors ✓(flat), vco_v1 ✓(+3 children, FIXED this session — the earlier 0-item run was a broken GDS). **DIV2_QUAD_v1 re-gated: KLayout var-D 0 on the COMPLETE GDS → sign-off HOLDS** (it was NOT gated on an incomplete layout). ibias_gen_v1.mag is flat, no committed GDS. **W4 VARACTOR WAIVER TESTED (not just accepted):** no nmoscap_3p3 param clears PL.5a/5b_LV — diffcov/polycov (80/100/60), guard-contacts off (grc/glc/gtc/gbc 0), and guard 0 all still give 4/unit; the violation is poly-to-COMP, device-internal. DIV2 (MIM caps + poly-res + dozens of FET gencells) = 0 KLayout items, so ONLY nmoscap_3p3 flags → it is a genuine foundry-gencell discrepancy, but **168 items is a real DRC failure the final signoff may reject (Bailey: failing-DRC designs likely dropped) — Greg's risk call.** **INDUCTOR-PORT (waiver-first attempt):** reconnected both buses into the leads + M5 patches + labels at the pins → extraction STILL shows PORT2=OUT_p but PORT1 dangling and OUT_n merged into OUT_p. Root cause CONFIRMED: the dual-spiral's ports are interior to ONE DC-continuous coil, so a bus reaching them touches the coil (PORT2 catches OUT_p's label, PORT1 catches nothing). The W3 black-box can't help because the LAYOUT must first present PORT1=OUT_n / PORT2=OUT_p at the instance pins, which requires connecting WITHOUT touching the coil — the inductor's designed feed (bottom tails) or re-exported edge ports (a cell-level change to `vco_inductor_v2`, not bus routing). Reverted vco_v1 to the clean core↔var tank. **INDUCTOR-PORT SOLVED (2026-08-18, magic abstract):** 1a geometry proof — OUT_n's M5 bus intersects ONLY the PORT1 lead [-880 -480 -720 1040], OUT_p's only PORT2 [-120 -480 40 1040]; NO coil turn touches either bus → the tank was wired correctly, the "merge/dangling" was purely the DC-continuous coil + hierarchy. 1b fix — `vco_inductor_v2` is now a TRUE ABSTRACT magic cell (`property LEFview true` + `GDS_FILE=gds/vco_inductor_v2.gds` GDS_START 122 GDS_END 17426 + `FIXED_BBOX` + M5 port pads PORT1/PORT2, NO coil geometry). LEFview ALONE with the coil present does NOT black-box the parent (geometry still merges); only a geometry-free abstract does. For a GDS-based extract (verify_cp), pre-load the abstract + `gds noduplicates true` before `gds read` so magic keeps the abstract. Full spiral (271 shapes, DRC-clean) streams into the final GDS from GDS_FILE. → extraction now gives `.subckt vco_v1 VDD OUT_p OUT_n TUNE ISS`, `Xvco_inductor_v2_0 OUT_n OUT_p`, core `ISS VDD OUT_p OUT_n`, all DISTINCT. **RUNG 3e — FULL ASSEMBLY BUILT (2026-08-18, commit b5254c6):** all 4 blocks + tune-R instanced; tank (OUT_p/OUT_n) + power (VDD/ISS via painted top-metal-over-child-port) + cap_bias(varactor↔resistor) + TUNE connected. **Full GDS: 5 cells, inductor 271 shapes, bbox 182×179.5µm, magic DRC 0, KLayout var-D 168 = ONLY W4 varactor waiver.** **LVS NOT CLOSED — 2 items:** (1) inductor abstract has 2 pins; schematic X1 is 3-terminal (OUT_n OUT_p GND) → add GND pin to the abstract. (2) **ISS = GND = substrate MERGE:** gf180 nfet_03v3 bulk = global psub; the core ties bulk→ISS (schematic B=ISS) and the resistor/inductor bodies tie to the same psub → physically ISS=GND=substrate, but the schematic keeps ISS and GND separate. **DESIGN QUESTION FOR GREG (rule 13):** either ISS is intended = ground (sources-to-ground VCO, no tail current source) → tie ISS=GND in the schematic; or the nfets need deep-nwell isolation to separate ISS from substrate. LVS cannot close until this is decided. **5.4 CLOSED (2026-08-20, option-b fix — layout+schematic, not merged-net):** Greg chose to fix the layout, not the topology. **vco_core rebuilt** (commit 3390c30): nfets `taps=0` + explicit pwell + 3 psub taps to a SEPARATE GND rail (y-900), source rail kept as ISS → nfet source=ISS, bulk=GND, DISTINCT. magic DRC 0, KLayout var-D 0, LVS match uniquely vs a golden with ISS/GND separate. bbox 28.55 × **31.55** µm. **Schematic edit** (commit b315c27, the ONE authorized change): `XM1/XM4` bulk ISS→GND (lab_wire GND on each bulk stub; sources still ISS, pfets untouched). **Re-sim as drawn** (body effect now present): starts robustly at every VTUNE — 0.3 V→6.35 GHz (568 mV), 1.5 V→5.53 GHz (544 mV), 3.0 V→4.13 GHz (472 mV); **band 4.13–6.35 GHz ≈ the recorded 4.11–6.37 GHz**, healthy swing, startup margin NOT thin. **vco_v1 re-gated ISS/GND SEPARATE:** core placed 260 lower so its ports realign; core GND rail = VSUBS = the substrate GND net (auto-ties to resistor guard); subckt `VDD ISS OUT_p OUT_n TUNE GND`. **`verify_cp.sh vco_v1` exit 0 (RESULT PASS): magic DRC 0, LVS match uniquely** — golden generated from the edited .sch, NO merged-net assumption. KLayout var-D 168 = W4 only. **verify_cp WIRED for the abstract** (regression-safe, env-gated by an optional `<cell>.abstract` file): `verify_extract.tcl` pre-loads listed cells + `gds noduplicates true` before `gds read` (magic can't extract the nmoscap OR the spiral from FLAT GDS — 0 caps — so vco_varactors + vco_inductor_v2 are pre-loaded from their device-aware .mags), and `verify_cp.sh` adds `ignore class vco_inductor_v2` to the netgen setup. **Regression: CP_v1 / ibias_gen_v1 / DIV2_QUAD_v1 all still `verify_cp` exit 0** (no .abstract file → no-op). **bbox 182 × 179.48 µm.** ONLY remaining waiver: W4 varactor (168 KLayout PL.5, device-internal to nmoscap_3p3 — Bailey/foundry LVS handles the nmoscap from GDS; magic can't). ---- HISTORY (superseded merged-net path): **GND pin added** to the inductor abstract (3-term PORT1/PORT2/GND, GND=floating M5 pad handled by the W3 black-box; MT.4 min-area fixed at 150×150). **ISS INVESTIGATION:** the testbench DRIVES ISS as a tail node — `Viss_meas vss net3 0` (0V ammeter) + `XM1 net3 vsg GND GND nfet_03v3 W=100u` (tail mirror) + `I0 GND vsg 1m` — so ISS is NOT meant to be ground, yet the design ties nfet `B=ISS` with no isolation → physically ISS=GND=substrate. **CORRECTION to earlier record: gf180mcuD HAS DNWELL** (GDS layer 12, DRC rules, + lvpwell) — nfets CAN be isolated (no gencell variant, drawable). **LVS BOTH WAYS (decisive):** golden flat from `vco_v1.sch` (resistor→ppolyf_u_1k w1 l15), netgen with W3 inductor ignore-class: **(a) ISS/GND separate → DO NOT MATCH (6 vs 7 nets); (b) ISS=GND merged → MATCH UNIQUELY.** So the layout is correct and ISS is electrically ground as drawn. **Greg's decision:** either tie ISS=GND in the schematic (accept sources-to-ground, drop the tail mirror) OR isolate the nfets with dnwell+lvpwell (keeps the tail node — a design + layout change). **GATE on the full GDS (5 cells, inductor 271 shapes, bbox 182 × 179.5 µm):** netgen LVS **match uniquely** (merged golden, W3); KLayout var-D **168 = W4 varactor PL.5a/5b only**; magic-on-GDS **84 = the SAME W4 varactor PL.5a** (magic-on-.mag is gencell-aware = 0; the assembly routing itself is DRC-clean). Golden committed as `vco_v1_golden.spice` (MERGED ISS/GND — noted as an assumption pending Greg). `verify_cp.sh vco_v1` needs two flow additions to run this as one command: pre-load the abstract + `gds noduplicates true` in verify_extract.tcl, and `ignore class vco_inductor_v2` in the netgen setup — done manually here. **REMAINING (Greg + follow-up):** decide ISS=GND; if isolate, redraw core nfet bulk→dnwell/lvpwell + re-gate. Floorplan note: active stacked BELOW the inductor → block is 182×**179.5**µm (~32,700µm²), taller than the inductor-only 182×84 — a tighter floorplan (active under the coil opening) would shrink it. **1k/3k design note (item 2, 2026-08-18):** KLayout LVS picks the poly-res sheet GLOBALLY (`POLY_RES = $poly_res || '1k'`, one value per run); 1k & 3k are the same physical layer with no distinguishing marker → a PER-FAB-RUN process choice, NOT co-resident on one die. DIV2's 1k resistors and the VCO's 3k tune R cannot both be nominal on one shuttle run — **Greg's design decision**: pick one variant and re-size the other block's resistors (w1l5 = 5kΩ on the 1k variant, 15kΩ on the 3k). Layout is identical either way. |
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
**VCO block `vco_v1` MEASURED (2026-08-18): bbox 182 × 179.5 µm = ~32,700 µm²** (assembled + gated), NOT the earlier ~18,000 estimate — the active blocks are stacked BELOW the inductor so the block is ~179.5 µm tall (vs the inductor-only 84 µm); a tighter floorplan (active under the coil opening) could approach ~18k. So blocks ≈ **56,635 + 32,700 = ~89,300 µm²**;
**PHASE-7 FLOORPLAN (2026-08-20, measured GDS bboxes): 350×300 does NOT fit.** Blocks: PFD_lib 60×24, CP_v1 73.5×28, ibias_gen_v1 181.8×65.25, DIV2_QUAD_v1 237.4×174.2, vco_v1 182×179.5 → SUM 89,366 µm² (85 % raw util of 350×300, before ANY routing/pads). The two biggest can't share the window: DIV2+vco_v1 side-by-side = **419.4 µm wide > 350**; stacked = **353.7 µm tall > 300**. Proposed floorplan (DIV2 + vco_v1 side-by-side, small blocks stacked in each column): **core 419.4 × 244.7 µm = 102,630 µm² abutted; ~439 × 266 µm with 20 µm channels; + a 12-pad ring on top.** **Honest die ≈ 440–500 × 270–330 µm — the declared 350 × 300 is ~69–90 µm too narrow.** LEVERS to shrink: a compact vco_v1 (active under the coil opening → ~182×84 not 182×179.5, saves ~95 µm of height but NOT width — the 419 width is set by DIV2 237 + vco 182), or stacking DIV2/vco vertically (353 tall, needs a >300 die). **Greg/Bailey decision — the die must grow or a block floorplan must change before allocation.** ---- HISTORY: add 30–50 % top-level routing/spacing → **~96,000–114,000 µm²**. The declared **350 × 300 =
105,000 µm²** **STRADDLES** that range — **tight but plausible**, not "short by 40 %". The earlier
"350×300 falls short / needs 370×390 or 400×400" conclusion was built on the guessed 43 k VCO
block and is **retracted**. The real figure arrives at top-level assembly (Phase 7). Per-block
utilization is not recomputed (needs extraction; areas are footprints). #143's area line is **not
edited** (browser action, Greg's to hand-update).

### 7.1 chip_top PLACEMENT (rung 2a) — 🟢 DONE + SIGNED-OFF (2026-08-20)

All 5 closed blocks instanced into `chip_top`; floorplan `docs/phase7-floorplan.md`.
Block bbox-LL (µm): **DIV2(0,0) · vco(290,0) · ibias(0,205) · CP(210,205) · PFD(210,245)**.
**Die bbox 472.00 × 270.25 µm** (matches floorplan). **magic DRC 0** (`chip_top.mag`);
**KLayout var-D (flat) = 168 = 84 PL.5a_LV + 84 PL.5b_LV = the W4 varactor waiver ONLY**;
23 cells, top=chip_top, all 5 blocks + vco sub-hier + 12 gf180 std-cell leaves.

**KEY BUILD FACTS (locked in):**
- **The deliverable `gds/chip_top.gds` is built by `team_src/magic/phase5/chip_merge.py`
  (KLayout), which streams each block's SIGNED-OFF golden GDS VERBATIM at the floorplan
  offsets — magic must NOT author the chip GDS.** A magic `gds read`→`gds write` roundtrip
  of PFD_lib's foundry std-cell dualgate perturbs sub-grid geometry → a spurious 0.68 µm
  **DV.5** sliver (min-dualgate-width). Streaming golden bytes keeps every block exactly as
  it signed off. `chip_top.mag` (magic) is the PLACEMENT RECORD + magic-DRC gate only.
- **`PFD_lib.mag` is a 496-byte SCAFFOLD** (5 bare logic cells, NO endcap/filltie/tieh) — it
  has no well/substrate ties and trips **20 DF.13/14_MV** (latch-up max-tap-distance) at chip
  level. The SIGNED-OFF `gds/PFD_lib.gds` carries the full tie ring and is clean. `chip_top.tcl`
  now `gds read`s the golden PFD as PFD's master (not the stub). DIV2/ibias/CP `.mag`s ARE full
  layouts (their goldens' source) so load-as-mag stays correct for those three.
- DF.13/14/DV.5 were all chip-context artifacts of the ABOVE, NOT placement errors (zero
  overlap/spacing violations at any point). Diagnosed by attributing KLayout markers to the
  gf180 std cells and diffing stub-.mag vs golden-GDS cell lists.

### 7.2 chip_top ROUTING / LVS (rungs 2b–2d, item 3) — 🔴 GATED on a chip-top SCHEMATIC (Greg's task)

Routing and chip LVS cannot proceed on layout evidence alone — three top-level nets are
**undefined at the block interface** and need a designer decision + a generated golden:
- **`PFD.FB`** (PFD feedback input) — must tie to ONE divider phase; DIV2 exposes
  I_P/I_N/Q_P/Q_N + internal OI/OIB/OQ/OQB. Which phase closes the loop is a design choice.
- **`RST_N`** — pins.md calls it "divider active-low reset", but **DIV2_QUAD_v1 exposes NO
  reset port** (labels: CK CKB IBIAS I_N I_P OI OIB OQ OQB Q_N Q_P VDD VSS). Either DIV2 must
  be revised to bring reset out, or RST_N is NC for this tapeout.
- **`MON_OUT`** — pins.md calls it "divided-down VCO monitor", but **no block exposes a monitor
  output**; it would tap a divider phase (buffered) — undefined.
No pad/IO/ESD cells exist in the design (organizer supplies the shared padframe), so the "12
pads" are 12 **die-edge ports/labels** (rung 2d), not physical pad cells.

**Item 3 — chip-level golden (proposed, NOT produced):** a chip golden must be GENERATED, not
typed. Produce it by drawing `chip_top.sch` in xschem instancing the 5 existing block symbols
+ the 12 die-edge ports, wiring the power/ground/signal map below and resolving the 3 nets
above, then netlisting → `chip_top.spice`. Hierarchical LVS then black-boxes each block
(EXTRACT_ABSTRACT) and matches instance-by-instance. **Drawing that schematic is Greg's task.**

**Power/ground net map (from floorplan, ready for the schematic):**
VDDA → vco.VDD, CP.VDD, ibias.VDD · VDDD → PFD.VDD, DIV2.VDD · GND (chip-wide common, no pin)
→ vco.GND, vco.ISS, CP.VSS, ibias.VSS, PFD.VSS, DIV2.VSS.
**Signal:** REF_IN→PFD.REF · PFD.UP/DOWN→CP.UP/DOWN · CP.CP_OUT→CP_OUT · VTUNE→vco.TUNE ·
vco.OUT_p/OUT_n→DIV2.CK/CKB · DIV2.I_P/I_N/Q_P/Q_N→pads · IBIAS→ibias.IBIAS ·
ibias.VGP/VGN→CP.VGP/VGN · ibias.IB_DIV2→DIV2.IBIAS · PFD.FB / RST_N / MON_OUT = TBD (above).

### 7.3 lvs_config.json repoint (item 4) — ⏸ SPEC READY, NOT APPLIED (blocked on the golden)

`lvs/lvs_config.json` currently: `TOP_SOURCE=PFD_lib`, `LAYOUT_FILE=gds/PFD_lib.gds`,
`LVS_VERILOG_FILES=[lvs/PFD_lib.nl.v]`. To repoint to the chip: set `TOP_SOURCE="chip_top"`
(TOP_LAYOUT already `$TOP_SOURCE`, LAYOUT_FILE already `gds/$TOP_LAYOUT.gds` → resolves to the
clean `gds/chip_top.gds`), and replace the source netlist with the chip golden
(`LVS_SPICE_FILES=[.../chip_top.spice]` from xschem, or a structural `chip_top` Verilog), plus
list the 5 blocks under `EXTRACT_ABSTRACT` for hierarchical LVS. **NOT applied yet: the layout
(gds/chip_top.gds) exists and is clean, but the chip_top SOURCE netlist does NOT — repointing
now would leave Bailey's LVS with a layout and no golden. Apply once 7.2's schematic exists.**

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
