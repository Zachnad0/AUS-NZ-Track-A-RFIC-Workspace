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
  - **Layout NOT drawn.** No CP `.mag`, no CP DRC/LVS/matching evidence exists yet.

Not verified (CP_v1): entire layout, device matching, guard-ring geometry, CP↔PFD noise
separation, CP_OUT shielding — all pending the GUI draw.

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
  a **DRC floor, not the block gap**; the noise-driven CP↔PFD gap is ≥ 20 µm (§3 / packet §3b).
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

# CP_v1 — charge pump (full-custom analog) — LAYOUT NOT DRAWN

**`CP_v1.mag` does not exist yet.** This section reviews the block against the five rubric
rows from its schematic golden (`team_src/magic/CP_v1_golden.spice`) and drawing packet
(`docs/cp-layout-packet.md`). **Every *measured layout* number below is an explicit `[TODO]`
placeholder** that stays open until `CP_v1.mag` exists **and** `team_src/magic/verify_cp.sh`
has been run on it. Schematic/golden/packet facts are stated as such.

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
- **LVS target:** `CP_v1_golden.spice` — 8 transistor-level devices, 7 ports, `*_03v3` primitives.
- **DRC:** `[TODO]` (expect 0) — after `CP_v1.mag` is drawn and `verify_cp.sh CP_v1` runs.
- **LVS:** `[TODO]` (expect "circuits match uniquely", 8 devices) — same gate.
- **Known LVS gotcha to handle first (not a defect, a flow note):** `nfet_03v3`/`pfet_03v3`
  are **PDK wrapper subcircuits** around the primitive. Extracting `CP_v1.mag` yields **raw
  devices** while the golden instantiates the wrappers → the identical **def-vs-blackbox
  mismatch** seen on PFD_lib's std cells. Fix by **resolving the PDK primitive spice on the
  golden side (or flattening both)** — *not* by loosening the netgen setup. `verify_cp.sh`
  will need the analogous primitive-wrapper handling before CP_v1 LVS will pass.

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
- **IR drop / rail current density:** `[TODO]` — after layout + PEX.

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
- **Extracted matching / achieved gap:** `[TODO]` — after `CP_v1.mag` + PEX.

## CP.4 — Reliability and physical-design risks
- **ESD:** block has **no pads**; secondary ESD sits with the organizer padframe. **ESD
  quantification NOT DONE.**
- **Electromigration / current density: NOT DONE** — no EM check exists in the flow; `[TODO]`
  until PEX on the drawn layout.
- **DUALGATE keep-out to PFD_lib:** DV.6 (0.24 µm) + DV.3 (0.24 µm) = **0.48 µm is the DRC
  floor only** (oxide/well legality). The real CP-to-PFD gap target is the **20–50 µm
  noise-driven separation** (CP.3), not 0.48 µm.
- **Antenna / latch-up (DRC):** `[TODO]` — after layout.

## CP.5 — Top-level integration and name correspondence
- **Name correspondence:** golden is `.subckt CP_v1`; `[TODO]` GDS top cell / `.mag` cell name
  = `CP_v1` (after drawing). Ports `UP DOWN CP_OUT VDD VSS VGP VGN` match the golden.
- **VGP/VGN are block current ports** off the chip-level IBIAS generator (CP.2), not pads.
- **Block ≠ integrated top** (as with PFD_lib); `lvs_config` repoint to the integrated top is
  an Aug-21 item.
