# team_src/magic/analysis — off-flow analysis & diagnostic scripts

**These are NOT part of the deliverable flow.** The tapeout flow is
`chip_merge.py` → `route_chip.py` → `verify_cp.sh` (+ `route_lib.py`,
`chip_top.abstract`, `klayout_signoff.py`) one directory up. Nothing in here is
imported or run by that flow; these are evidence/measurement scripts kept so the
conclusions in `docs/` are reproducible. Do not wire them into the flow.

## Bailey LVS-flow reproduction (evidence for the flat-GDS gencell finding)
Faithful local reproduction of `d-m-bailey/extra_be_checks`'s two-pass
LEF-abstract extraction (we cannot install the tool — standing rule 1). This is
the evidence behind `docs/gf180-flat-gds-gencell-lvs.md` and
`docs/bailey-lvs-investigation.md`. **Do not delete.**
- `bailey_pass1_abstract.tcl` — PASS 1: `lef write -hide -pinonly` a geometry-free
  abstract of the cells named in `ABSTRACT_CELLS`.
- `bailey_pass2_extract.tcl` — PASS 2: `lef read` + `gds noduplicates yes` + extract
  (keeps the abstract, skips the cell's real geometry).
- `bailey_extract.tcl` — the single-pass (`property LEFview true`) variant, which
  does *not* black-box a coil — kept to show why the two-pass LEF path is needed.

Run in-container against `gds/chip_top.gds` with env `LAYOUT_FILE/TOP/ABSTRACT_CELLS/
FLATGLOB_CELLS/EXT_DIR/OUTSP/DRCOUT` (see the tcl headers).

## Phase-8 padframe DEF analysis
Inputs: the organizer's `A01.def.tgz` (extracted to a working dir — not committed)
and `gds/chip_top.gds`. Produce the numbers in `docs/phase8-padframe-plan.md`.
- `parse_def.py` — parses BV/BH `*_interface.yaml` → per-variant pin tables (name,
  slot, cell, use, dir, edge, `translated_user` rects in µm) + pin-rect spans
  (Item 1). Expects the DEF files under `/tmp/a01/project_defs/<variant>/`.
- `iq_haul.py` — measures the four DIV2 I/Q output tap M1 pads in `chip_top.gds` and
  the Manhattan hauls to the BH north pads for a given core placement (Item 2).
- `core_placement.py` — sweeps the core offset (dx,dy) inside the BH 1110×550
  DIEAREA → I/Q spread, matched length, serpentine budget, vco→pad hauls (§3b/Item 3).

## Phase-8 in-context rehearsal + gate (§3h/§3i/§3j, 4th–5th session)
The rehearsal instances `chip_top` in a throwaway cell and routes the matched I/Q quad, then
gates it four ways. NOT the flow — a sandbox to de-risk the escape/serpentine geometry.
- `phase8_incontext.py` — builds `gds/reh_phase8.gds` (chip_top + 4 routes), `gds/reh_base.gds`
  (blocks only), and `gds/reh_routes.gds` (the 4 routes with NO instance, for a clean
  routes-only extraction). Env: `PHASE8_DY` (default 200), `PHASE8_NOSER` (base lengths only).
  `PLAN[*]["escl"]` picks the escape layer (3 = via at the M1 pin then escape on M3, used for
  the left DIV2-output risers to clear DIV2's M1 frame).
- `reh_drc.tcl` / `reh_why.tcl` — magic DRC of a reh cell (env `REH_CELL`); `reh_why.tcl` dumps
  per-rule violation boxes in µm. Gate: reh_phase8 == reh_base == 84 (the vco PL.5a baseline).
- `reh_extract.tcl` — extracts `reh_routes.gds` (routes only) → node count + `.subckt` ports.
  Necessary but NOT sufficient: it cannot see a haul shorting to a *block* net (§3l).
- `reh_ctx_extract.tcl` — FULL in-context extraction using the SAME abstract preload as
  `chip_top.abstract` (`gds noduplicates true` + `load vco_varactors vco_inductor_v2`), so the
  spiral is black-boxed and the extract sees haul nets AND block nets. Compare chip_top's exposed
  ports vs `reh_base`: a haul that bridges a block internal node shows up as that node exposed +
  tied to the haul (this is how the I_P/Q_P → `a_8764_6964#` short was caught, §3l). Env
  REH_CELL, CTX_OUT. **This is the real distinct-net gate.**
- `cell_list.py` — prints a GDS's cell hierarchy (env GDSF); verify the abstract subcells survive
  before trusting an abstract-preload extract.
- `iq_tap_layers.py` — pin-layer stack at each of the 4 I/Q taps (I_P is a full via stack up to
  M4 → land on its M3, `novia`; the other three are M1-only → via_stack).
- `ring_corridor.py` — every layer in the GND-ring left segment + the escape corridors west of
  DIV2 (proved the ring is M5-only and the "2.5 µm slot" is an artifact, §3i, Item 1).
- `tap_layers.py` — pin layer present at each block tap (VDDA/IBIAS/ISS/VTUNE/CP_OUT/VDDD/REF_IN).
- `vco_tap_escape.py` — scans upward from the vco TUNE/ISS taps → the inductor M5 enclosure that
  blocks a clean escape (§3j, why Item 3 stops at VTUNE).
- Waivers `reh_base.waivers` / `reh_phase8.waivers` (one dir up) mirror `chip_top.waivers`
  (PL.5a_LV/PL.5b_LV) for the KLayout signoff gate.
