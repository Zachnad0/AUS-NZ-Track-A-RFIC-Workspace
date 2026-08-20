# Making the submission pass Bailey's LVS — investigation (2026-08-20)

Goal: make `chip_top` pass `d-m-bailey/extra_be_checks` run on `gds/chip_top.gds`
straight (no `chip_top.abstract` device-aware preload). Our local `verify_cp`
passes only because it preloads device-aware `.mag`s; Bailey does not.

## What EXTRACT_ABSTRACT actually does (read from source, not guessed)

Bailey's real driver is `run_extract`, a **two-pass** magic flow (NOT the
standalone `scripts/gds.analog.spice.tcl`, which only does `property LEFview true`
and does not black-box a coil):

- **PASS 1 (`abstract.tcl`):** `gds read` the full layout; for each
  `EXTRACT_ABSTRACT` cell `load $cell; property LEFview true`, delete its child
  instances + non-port layers ("shorted ports can cause problems in parent
  hierarchy"), then **`lef write $cell -hide -pinonly`** — a geometry-free,
  pins-only LEF.
- **PASS 2 (`extract.tcl`):** `lef read` those LEFs, then
  `gds flatten yes; gds noduplicates yes; gds read` so magic KEEPS the geometry-
  free abstract and SKIPS the cell's real geometry from the stream, then extract.

netgen is then `lvs "<layout> <top>" "<source> <top>" <setup> <report>
**-blackbox** -json` — `-blackbox` matches empty subckts by port.

Reproduced faithfully here: `team_src/magic/bailey_pass1_abstract.tcl` +
`bailey_pass2_extract.tcl` (and `bailey_extract.tcl` for the single-pass variant).

## Confirmed: the current submission fails Bailey's flow

Bailey-flow reproduction on the current GDS (no abstract):
- **magic DRC = 84**, a single rule **PL.5a (Poly spacing to diffusion <0.1µm)**,
  entirely inside the nmoscap_3p3 varactors — the SAME device-internal family as
  the KLayout **W4** waiver (84 PL.5a_LV + 84 PL.5b_LV). Nothing else.
- vco_v1 extracts with **0 capacitors** (varactors invisible from flat GDS).
→ LVS DO NOT MATCH. This is the real state of the submission on Bailey's machine.

## The abstraction works in principle, but hits a coordinate blocker

- `lef write -pinonly` on vco_v1 yields **6 clean separate pins** (OUT_p/OUT_n do
  NOT merge — the pin-only LEF drops the DC-continuous spiral). So the mechanism
  can black-box the coil.
- Abstracting the two un-extractable **children** (`vco_inductor_v2`,
  `vco_varactors`) keeps vco_v1's core + substrate visible, so **GND connects to
  VSSA via the substrate automatically** (no risky over-vco routing) and
  OUT_p/OUT_n stay separate. Abstracting **vco_v1 whole** instead leaves its GND
  pin interior and unreachable without a forbidden geometry change.
- **BLOCKER (root-caused):** our custom `vco_v1` is **not origin-normalized** —
  its native lower-left is `(-112,-119.48)µm`, not `(0,0)`. `magic lef write`
  therefore emits `ORIGIN 112 119.48`, and on `lef read` the abstract lands
  shifted by `-ORIGIN`: measured cell bbox `(-224,-238.96)` instead of
  `(-112,-119.48)`. Every abstracted pin then misses the chip/tank metal it
  should touch, so extraction shows the pins isolated and netgen mismatches.
  Bailey's flow is built for P&R blocks whose origin is at (0,0); a hand-drawn
  analog block with a non-zero native origin trips this.

## Resolution

**Origin-normalization DONE (commit `item1`).** `chip_merge.py` now shifts
vco_v1's frame so its bbox-LL is (0,0) and places it directly at the floorplan
target — the shift and placement cancel, so a flat XOR of `chip_top.gds` before
vs after is **0 polygons** (absolute geometry byte-identical). `gds/vco_v1.gds`
is untouched. Re-test: PASS-1 `lef write` now emits **`ORIGIN 0.000 0.000`** (was
112 119.48), and in the two-pass reproduction the vco_v1 abstract's
**TUNE/ISS/OUT_p/OUT_n pins now land on the chip nets** (VTUNE/ISS/DIV2.CK/CKB)
instead of isolated locals. Invariants all held (verify_cp chip_top + vco_v1
match uniquely, KLayout 168 W4, check_placement CONSISTENT, boundary 522×309,
5-block regression clean).

**Still open (deferred — "config on faith", unverifiable without the real tool):**
- Two pins still need connecting for a full abstract match: **VDD** (chip taps
  the vco.VDD M2 wire mid-run at x405, but the abstract pin sits at x397.5 — add
  a VDD port label at x405) and **GND** (no routed tap — either abstract the two
  *children* instead of vco_v1 so GND stays connected via the substrate, or add a
  chip GND tap to the vco.GND pin).
- Setting `EXTRACT_ABSTRACT` in `lvs_config.json` + a black-box golden, and
  converting our `verify_cp` to the same abstract, would complete it — but that
  cannot be confirmed to pass Bailey's real flow here (rule 1), so it is left for
  a machine with `extra_be_checks` or coordination with Bailey.

No regression: `verify_cp chip_top` PASSES (DRC 0, match uniquely); the on-main
chip is untouched.
