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
