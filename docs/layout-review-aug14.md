# Aug-14 Layout Review — Team A01 (AUS/NZ Track A RFIC)

Block under review: **PFD_lib** (library-cell PFD, gf180 5 V std cells, our PFD topology).
All numbers below are read from files in the passing run
`librelane_pfd/runs/RUN_2026-08-05_23-52-38/` unless noted. Image: `docs/img/PFD_lib_white.png`.
Second Aug-14 target CP_v1 is analog full-custom — golden + drawing packet done, and the
**layout is now drawn and gate-passed** (Magic + KLayout DRC 0, netgen LVS match uniquely,
`verify_cp.sh` exit 0 — see the CP_v1 section).

Ground note (applies throughout): the padframe provides **one chip-wide common ground**
(#143: ground = 0 pins). `VSSA`/`VSSD` are **on-chip routing labels only — not separate
ground pins**. `VDDA`/`VDDD` are the two real power pins.

---

## 1. DRC and LVS correctness

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
  separately by `team_src/magic/verify_cp.sh` (`verification.md §2.3.1`): **DRC 0, 7 devices /
  6 ports / 11 nets, circuits match uniquely**. Two documented, justified LVS waivers:
  - **Fillcap decaps ignored** (18 instances, matches the inventory below). Same waiver
    LibreLane's own run already applied via `LVS_IGNORE`; the local netgen wrapper adds
    *only* the PDK-provided (commented) fillcap `ignore class`, nothing else.
  - **Comparison method, not a violation:** golden std cells resolved against the PDK
    `mcu7t5v0` spice so both circuits carry full definitions (else a placed digital block
    LVSes def-vs-blackbox against a schematic golden).
- **Cell inventory** (`final/nl/PFD_lib.nl.v`): 2× dffrnq_1, 1× nand2_1, 2× inv_1, 2× tieh;
  everything else physical-only (endcap×8, fill_1×7, fill_2×6, fillcap_16×6, fillcap_32×3,
  fillcap_4×5, fillcap_8×4, filltie×6).
- **Reset delay preserved:** `NAND(UP,DOWN)→NANDO→XI1→NDLY→XI2→RSTN→both DFF.RN` — 2× inv_1
  in series on RSTN, confirmed in the final post-route netlist.

Not verified: nothing outstanding for this row.

---

## 2. Power, ground, current paths

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

## 3. Analog matching, symmetry, noise isolation

- **PFD_lib** is all-digital std cells; it qualifies under the rubric's **"no analog
  circuitry" clause** — matching/symmetry/noise-isolation do not apply to this block.
- **CP_v1** is the analog block for this row. Real status, stated plainly:
  - Golden LVS netlist **verified** (`team_src/magic/CP_v1_golden.spice`, 8 devices, parses).
  - Drawing packet **written** (`docs/cp-layout-packet.md`): matched-mirror finger breakdown +
    dummies, guard rings, noise-driven ≥20 µm CP↔PFD separation (not the 0.48 µm DRC floor),
    CP_OUT shielding.
  - **Layout DRAWN and gate-passed** (2026-08-13): `CP_v1.mag` + `gds/CP_v1.gds`, Magic DRC 0,
    KLayout signoff DRC 0, netgen LVS match uniquely (8 devices), `verify_cp.sh` exit 0 — see
    the CP_v1 section below for the file-cited numbers.

Still NOT-DONE for CP_v1 (physical-matching refinement, deferred): extracted (PEX) device
matching, full dummy fingers + complete guard-ring geometry, and the CP↔PFD noise separation /
CP_OUT shielding (top-integration placement, not a block-level number).

---

## 4. Reliability and physical-design risks

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
  **Corrected 2026-08-10:** `librelane_pfd/config.json` now carries an explicit
  `FP_TAPCELL_DIST = 15` (commit `e3b6cae`); it had been inheriting the LibreLane default
  20 µm. This is **config-only — no LibreLane re-run** — so this build's GDS still relies on
  the incidental compliance above; the corrected 15 µm applies to the next build.
- **DUALGATE spacing** (cited from `docs/scope.md §4.2`, not re-derived): DV.3 (DUALGATE-to-COMP)
  0.24 µm, DV.2 (DUALGATE space) 0.44 µm → ~0.48 µm PFD-active-to-CP-active DRC floor. That is
  a **DRC floor, not the block gap**; the noise-driven CP↔PFD gap is ≥ 20 µm (§3 / packet `docs/cp-layout-packet.md` §3b).
- **ESD:** this block has **no pads**; secondary ESD sits with the **organizer padframe**
  (`scope.md §7`, `pins.md §2`). ESD is not a block-level artifact here.

Not verified / NOT DONE: **current-density / electromigration** (no check exists in the run —
LibreLane Classic flow does not run it); **ESD quantification**; **PEX** (parasitic extraction).

---

## 5. Top-level integration and connectivity

Evidence (file-read):
- **Name correspondence — all match `PFD_lib`:** GDS top cell (`final/gds/PFD_lib.gds`),
  `.v` module (`module PFD_lib`), `.def` DESIGN, and golden `.subckt PFD_lib`.
- **Block interface:** ports `REF FB UP DOWN VDD VSS` (`final/nl/PFD_lib.nl.v`; golden matches).
- **Submission pointer repointed:** `lvs/lvs_config.json` `TOP_SOURCE` = `PFD_lib`,
  `LVS_VERILOG_FILES` = `$UPRJ_ROOT/lvs/PFD_lib.nl.v`, `LAYOUT_FILE` =
  `$UPRJ_ROOT/gds/$TOP_LAYOUT.gds` → `gds/PFD_lib.gds` (both committed; no run-tag paths).
- **Signoff artifact — one, unambiguous:** `team_src/magic/PFD_lib.mag` is an unrouted
  5-cell placement scaffold generated by `team_src/magic/place_pfd.tcl`, retained as a
  reproducible reference for the cell abutment. It is **not a signoff layout and is not
  LVS-clean** (5 abutted cells, no routing/labels, missing the 2 tie cells → would fail LVS
  on sight). The committed **`gds/PFD_lib.gds` is the sole signoff artifact** for this block.

Not verified: this is a **single block**, not the integrated RFIC top (which does not exist
yet). Top-level padframe integration, inter-block routing, and the CP/VCO/DIV2 blocks are not
part of this GDS. `lvs_config` TOP must be repointed at the integrated top before the Aug-21
GDS (`tracking.md §4`).

---

# CP_v1 — charge pump (full-custom analog) — LAYOUT GATE PASSED (2026-08-13)

**`CP_v1.mag` is drawn and `gds/CP_v1.gds` is committed.** `bash team_src/magic/verify_cp.sh
CP_v1` (which reads the committed GDS in preference to the `.mag`) **exits 0** — re-confirmed
this session (2026-08-15). Every measured number below is read from the verify_work logs and
the KLayout report, each cited inline. Checks that genuinely do not exist in the flow yet
(PEX, EM, ESD quantification, antenna) are written as **NOT-DONE** lines, not softened and not
scored — the rubric is the reviewer's instrument.

**Device table** (golden, 8 transistors; ports `UP DOWN CP_OUT VDD VSS VGP VGN`):

| Device | Type | W / L | Role |
|--------|------|-------|------|
| M_PREF | pfet_03v3 | 50u / 2u | PMOS mirror **ref** — matched pair ↔ M_PSRC |
| M_PSRC | pfet_03v3 | 50u / 2u | PMOS mirror **source** — matched pair ↔ M_PREF |
| M_PSW  | pfet_03v3 | 50u / 0.3u | UP switch (gated by UP_B) |
| M_NREF | nfet_03v3 | 10u / 2u | NMOS mirror **ref** — matched pair ↔ M_NSNK |
| M_NSNK | nfet_03v3 | 10u / 2u | NMOS mirror **sink** — matched pair ↔ M_NREF |
| M_NSW  | nfet_03v3 | 10u / 0.3u | DOWN switch |
| M_INVP | pfet_03v3 | 2u / 0.3u | UP inverter (UP → UP_B) |
| M_INVN | nfet_03v3 | 1u / 0.3u | UP inverter |

## CP.1 — DRC and LVS correctness
- **Magic DRC = 0** — `team_src/magic/verify_work/CP_v1.drc.log` (`VERIFY_DRC_COUNT=0`).
- **KLayout signoff DRC = 0 violations** — `run_drc.py --variant=D --topcell=CP_v1` on
  `gds/CP_v1.gds`: *"Klayout DRC run is clean. GDS has no DRC violations"*, report
  `team_src/magic/verify_work/klayout_cp/CP_v1_main.lyrdb` (main deck, 4.3 s). The main deck
  includes the FEOL latch-up / substrate-tap rules (DF.14 etc.), so those pass too.
- **netgen LVS = Circuits match uniquely** — `team_src/magic/verify_work/CP_v1.lvs.log` and
  `CP_v1.comp.out`: layout extracts 38 raw fingers, netgen parallel-merges 30 → **8 devices
  (4 nfet_03v3 + 4 pfet_03v3), 10 nets**, both sides equal; **7 ports** (`.subckt CP_v1 VDD
  VSS VGP VGN DOWN CP_OUT UP`, `CP_v1.lvs.spice`) with cell pin lists equivalent. `verify_cp.sh`
  treats any device-property (W/L) error as a hard fail; the run reports the clean
  *"match uniquely"* verdict, so **zero property errors and zero port errors**.
- **verify_cp.sh CP_v1 → exit 0** (`RESULT: PASS`), matching against the hand golden
  `team_src/magic/CP_v1_golden.spice` (8 devices).
- **PDK wrapper handling (resolved, was flagged as the first gotcha):** `nfet_03v3`/`pfet_03v3`
  are PDK wrapper subcircuits; netgen treats them as **black-box placeholders** and the
  extracted raw devices equate to the golden's wrapped devices (*"Device classes … are
  equivalent"* in `CP_v1.comp.out`). Handled in the netgen setup, not by loosening it.

## CP.2 — Power, ground, current paths
- **Chip-wide COMMON ground.** `VSSA`/`VSSD` are **on-chip labels only — NOT separate ground
  pins**; the padframe provides one chip-wide common ground (#143). The two guard-ring
  returns route separately and **star-connect to the single common-ground point**. No
  separate off-chip ground return exists; no claim of one should appear.
- **VGP/VGN are current PORTS off the chip-level IBIAS generator — NOT pads.** VGP feeds the
  diode ref M_PREF (external IBIAS_P **sinks** I_CP from VGP); VGN feeds M_NREF (external
  IBIAS_N **sources** I_CP into VGN). Block ports only — pin count unaffected. The schematic's
  ideal 50 µA `I_PREF`/`I_NREF` sources are **not laid out**.
- **Supplies split (these ARE pins):** CP on **VDDA**, PFD on **VDDD** (`pins.md` power 2).
  Ground is the exception — common, not split.
- **Current path:** PMOS mirror sources I_CP when UP; NMOS mirror sinks when DOWN;
  `CP_OUT = M_PSW drain = M_NSW drain`, high-impedance into the off-chip loop filter.
- **IR drop / rail current density: NOT-DONE** — needs PEX; no parasitic extraction exists for
  `CP_v1` (the LibreLane OpenROAD IR-drop report covers `PFD_lib` only, not this full-custom block).

## CP.3 — Analog matching, symmetry, noise isolation
- **Matching is the CP's spec** (UP/DOWN current match 0.001 % @ 1.5 V in *schematic* sim).
  Mirror pairs **M_PREF↔M_PSRC** and **M_NREF↔M_NSNK**: common-centroid interdigitation,
  identical finger orientation, **1 dummy finger each array end**, L = 2 µm aids matching,
  both devices of a pair in the same nwell/psub region at the same y (packet §1).
- **+110 fC injection is a known SCHEMATIC-LEVEL flaw** (charge injection at the switches),
  documented at the schematic; it is **not** a layout defect and layout does not fix it —
  recorded so the review doesn't attribute it to the drawing.
- **Noise isolation:** n+ guard ring (VDD) around the PMOS group, p+ ring (VSS) around the
  NMOS group; ring the mirror pairs first (substrate noise on VGP/VGN modulates I_CP → loop
  jitter). **CP↔PFD gap ≥ 20 µm (30–50 µm is cheap), NOT the 0.48 µm DRC floor**; double
  guard ring (CP p+ VSSA, PFD p+ VSSD); CP_OUT shielded (coplanar VSSA shields + ground
  plane, kept short, never parallel to any switching net).
- **Deep nwell deliberately NOT adopted this cycle** (new layer + new DRC rules, wrong week);
  recorded as a later-revision isolation option if measured spurs demand it.
- **Extracted matching (PEX): NOT-DONE** — no PEX in the flow, so no extracted UP/DOWN current
  match or parasitic-aware mirror ratio for the drawn layout; the 0.001 % is schematic-only.
- **Full dummies + complete guard rings: DEFERRED** to a matching-refinement pass — the drawn,
  LVS-clean `CP_v1.mag` implements the 8 golden devices; the packet's full common-centroid
  dummy fingers and complete guard-ring treatment are not claimed as done here.
- **Achieved CP↔PFD gap: N/A at block level** — `CP_v1` is a standalone block with no PFD
  adjacency drawn; the ≥ 20 µm noise gap is a top-integration placement number, not set here.

## CP.4 — Reliability and physical-design risks
- **ESD:** block has **no pads**; secondary ESD sits with the organizer padframe. **ESD
  quantification NOT DONE.**
- **Electromigration / current density: NOT-DONE** — no EM check exists in the flow; needs PEX
  on the drawn layout.
- **DUALGATE keep-out to PFD_lib:** DV.6 (0.24 µm) + DV.3 (0.24 µm) = **0.48 µm is the DRC
  floor only** (oxide/well legality). The real CP-to-PFD gap target is the **20–50 µm
  noise-driven separation** (CP.3), not 0.48 µm.
- **Latch-up (DRC): PASS** — the KLayout main deck (CP.1, 0 violations) includes the substrate-
  tap / DF.14 latch-up rules, so they pass on the drawn GDS.
- **Antenna: NOT-DONE** — antenna is a separate KLayout `--antenna` run; it has not been run on
  `CP_v1` (the LibreLane antenna report covers `PFD_lib` only).

## CP.5 — Top-level integration and name correspondence
- **Name correspondence: PASS** — golden is `.subckt CP_v1`; the GDS top cell is `CP_v1`
  (`verify_cp.sh` and `run_drc.py --topcell=CP_v1` both read `gds/CP_v1.gds` as top cell `CP_v1`).
  Ports `UP DOWN CP_OUT VDD VSS VGP VGN` match the golden (`CP_v1.lvs.spice` subckt line).
- **VGP/VGN are block current ports** off the chip-level IBIAS generator (CP.2), not pads.
- **Block ≠ integrated top** (as with PFD_lib); `lvs_config` repoint to the integrated top is
  an Aug-21 item.

---

# DIV2_QUAD_v1 — quad-phase ÷2 divider (full-custom) — LAYOUT GATE PASSED (2026-08-17)

**`DIV2_QUAD_v1.mag` drawn, `gds/DIV2_QUAD_v1.gds` committed.** `verify_cp.sh DIV2_QUAD_v1` exit 0
vs the GDS (magic DRC 0, netgen LVS match uniquely, 9 ports, 0 property/port errors); KLayout DRC
0 (variant D). 75 devices; measured bbox 237.4 × 174.2 µm = 41,340 µm².

## DIV2.1 — I/Q quadrature: CHARACTERIZED layout limitation (~1.0°)
The four slicer converters are placed option-c (I_P/Q_P east-unmirrored, I_N/Q_N west-mirrored) so
any mirror-induced slicer offset is common to the I and Q paths and cancels in the quadrature
comparison. The residual is a **routing-length asymmetry**: the Q converters sit ~53 µm below their
latch-B taps (the I converters sit at their latch-A taps' y-level), so each Q input haul is ~53 µm
longer than its I counterpart. At ~41 fs/µm (CML 300 Ω load driving ~0.2 fF/µm wire) that is ~2.2 ps
→ **~1.0° at the 1.25 GHz divider output**. It is COMMON to Q_P and Q_N (both mirror-paired, equal
hauls) → a static I-to-Q offset, not an intra-pair duty error, adding a small fixed layout term to
the schematic-sim I/Q result (270.0° exact). It is the cost of the stacked-below Q floorplan chosen
to keep the I pair adjacent to the core.

## DIV2.2 — Electromigration on the VSS network: KNOWN VIOLATION (now quantified)
No longer unknown. Total VSS return **22.4 mA** (SPICE, div2_sb_TT deck, i(V_VDD) 16–20 ns — matches
the validated headline); **per-converter VSS 2.96 mA** (measured through a 0 V meter split into the
IP converter's return). The open gf180mcuD PDK ships **NO EM current-density deck at all** (no EM
rule in any DRC/LVS deck — confirmed by search). There is therefore no PDK limit to cite; the
comparison below uses an **industry rule of thumb for ~0.5 µm Al metal, ~1 mA/µm (M1–M4), ~2 mA/µm
(thick M5)** — NOT a value read from the GF design manual (which was not consulted). The real
per-layer limits must come from that manual before sign-off. Against the rule of thumb:
- 7.5 µm M2 collector plate carries the ~17–22 mA aggregate → **~2.3–2.9 mA/µm — OVER**.
- Per-converter VSS ties are 0.28–0.56 µm carrying ~2.96 mA → **~5.3–10.6 mA/µm — well OVER**.
**Fix = widen the plate to ~22 µm and every per-converter tie to ~3 µm** (M2/M3), then re-gate
DIV2_QUAD_v1. This is a reliability fix on the VSS rail; the DRC/LVS/port sign-off is unaffected.

---

## Phase-7 chip-level result (added 2026-08-20)

`chip_top` — all five signed-off blocks integrated. Image: `docs/img/chip_top_black.png`.

- **[SUPERSEDED — see the CLOSED section below; the final die is 522 × 309 µm.]** Die bbox
  472.00 × 270.25 µm was the pre-GND-ring extent; the final closed die grew to 522 × 309 µm for
  the ring margin. The old **350 × 300 is STALE and short** (DIV2 237 + vco 182 side-by-side alone
  is 419 µm wide). (Updating #143's area line and Bailey's sheet is Greg's browser action.)
- **DRC:** magic DRC 0 (abstract-aware); **KLayout var-D = 168 = W4 varactor waiver ONLY**
  (84 PL.5a + 84 PL.5b, device-internal to nmoscap_3p3). Placement is overlap/spacing-clean.
- **Deliverable GDS** built by `team_src/magic/phase5/chip_merge.py` (KLayout) — streams each
  block's signed-off golden verbatim (no magic re-render, which perturbs foundry geometry).
- **Chip golden** `team_src/magic/chip_top_golden.spice` — generated from `chip_top.sch`
  (10 ports) + the 5 inlined block goldens (115 devices). `verify_cp.sh chip_top`: magic DRC 0,
  LVS DO NOT MATCH on the UNROUTED merge (missing inter-block metal only).
- **Pins reduced 12 → 10:** RST_N + MON_OUT dropped (no matching block port; see docs/pins.md).
- **Remaining:** inter-block routing (rungs 4a–4c) per `docs/phase7-routing-plan.md`, then the
  chip LVS match and the `lvs_config.json` repoint to `chip_top`.

---

## Phase-7 chip CLOSED — LVS clean (2026-08-20)

`chip_top` is fully placed, routed, and **LVS-clean**. Image: `docs/img/chip_top_black.png`.

- **Declared area: 522 × 309 µm** (the one number to use; grew from 472×270 for the GND-ring
  margin). Config B is 550 × 1110 — 28 µm width margin, ~800 µm vertical headroom.
- **Chip LVS: `verify_cp chip_top` → magic DRC 0, 12 ports, "match uniquely", zero property/port
  errors, PASS.** 5-block regression all exit 0. All 12 nets connected (VDDA=CP+ibias+vco,
  VDDD=PFD+DIV2, ground ring, UP/DOWN/FB, VGP/VGN/IB_DIV2, VCO_OUTP/N). All signals routed at
  chip level via clear M3/M4 columns above each pin — **no block layout edits were needed.**
- **W4 waiver: 168 items** (84 PL.5a_LV + 84 PL.5b_LV) — nmoscap_3p3 gencell field-poly-to-guard,
  device-internal; `klayout_signoff.py chip_top` reports them WAIVED and PASSes.
- **Grounds (Bailey req):** **12 pins**, one ground pin **VSSA** (quiet quadrant ground, pin 0).
  The layout has ONE ground electrical net (all VSS ties the shared p-substrate; no deep-nwell) →
  ONE LVS ground port (VSSA), so a second VSSD pad was dropped (it would star as a missing port in
  Bailey's audit). The die still bonds ground at more ring points — a bond/package detail, not a
  second pin. 0/0 boundary present at the die extent. **(Open question for Bailey: whether a second
  isolated ground is wanted — that requires deep-nwell to split the substrate return; see the
  known-limitations list below.)**
- **VCO output load (A5, estimate — NOT resized):** OUT_p route ~494 µm, OUT_n ~431 µm (0.4 µm
  M3/M4, ~0.08 fF/µm ⇒ ~40 / ~35 fF) + DIV2 CML input gate (W=40 ⇒ ~40–55 fF) ⇒ **~75–95 fF/side**.
  Against the ~844 fF tank that is Δf ≈ **−4 to −7 %** (f ∝ 1/√C): the characterized 4.13–6.35 GHz
  band shifts to ≈ 3.9–6.05 GHz, still covering the 4.8–5.0 GHz needed for the 2.4–2.5 GHz ÷2
  output. Retunable via VTUNE; no device change.
- **DIV2 VDD chip tap — FIXED (Phase-7 item 2, 2026-08-20).** The old single 0.28 µm M4 collector
  ran all ~22.4 mA at **80 mA/µm**. Replaced by a **multi-point tap**: 40 injection points on a
  3 µm pitch across DIV2's two VDD collectors (24 on the y137.5 collector, 16 on y124), each a
  0.4 µm M4 riser → via4 → 0.44 µm M5 hop to the VDDD bus. Per-wire peak now: collector-between-taps
  ~0.97 mA/µm (was 80), riser stubs 1.27–1.40 mA/µm (0.56 mA each), VDDD M5 bus 1.9 mA/µm. DRC 0,
  LVS match uniquely. (DIV2 was **not** reopened.)
- **VCO_OUTP/N length match — FIXED (Phase-7 item 3, 2026-08-20).** Was OUT_p 494.3 µm vs OUT_n
  431.5 µm (62.8 µm / 12.7 % skew). A ~64 µm M4 length-match notch on OUT_n (into the clear right
  margin east of the VDDA bus) cut the residual to ~1.2 µm (~0.2 %). DRC 0, LVS match uniquely.
- **DIV2 internal VSS EM — KNOWN, DEFERRED (DIV2-internal, not a chip-route item).** Per-converter
  VSS 2.96 mA on 0.28–0.56 µm ties (~5.3–10.6 mA/µm); the root bottleneck is `ib_conv_v1`'s internal
  0.6 µm M1 VSS bus carrying ~4.9 mA/µm; the 7.5 µm plate ~2.3–2.9 mA/µm. Note the ~1 mA/µm figure
  is an **industry rule-of-thumb for ~0.5 µm Al**, NOT a GF180 PDK rule (the open PDK ships no EM
  deck). Fix = widen the ib_conv bus to ~3 µm + stack the plate on M2/M3/M4 + widen ties, then
  re-gate DIV2 — a reliability fix that does not affect DRC/LVS/port sign-off.
- **I/Q offset:** the divider I/Q phase target is 90° with a residual **~1.0° static I-to-Q offset**
  — the Q converters' input hauls run ~53 µm longer than the I converters' (~2.2 ps at the divider
  output), common to Q_P/Q_N so it is a fixed offset, not an intra-pair duty error. It is the cost
  of the stacked-below Q floorplan; unchanged by the item-3 VCO_OUTP/N equalization above.
