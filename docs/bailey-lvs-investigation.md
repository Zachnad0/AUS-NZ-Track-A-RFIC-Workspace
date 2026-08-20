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

## Options to finish (need a decision)

1. **Origin-normalize the abstracted cell(s).** Regenerate `vco_v1.gds` (or the
   two child GDS) shifted so LL = (0,0), and compensate the placement in
   `chip_merge.py` so the ABSOLUTE deliverable geometry is byte-identical. This is
   a rigid frame shift, not a device/wire move — but it does touch block GDS, a
   rule-12 gray area, and cannot be fully verified without Bailey's tool.
2. **Verify against the real `extra_be_checks`.** Rule 1 forbids installing it
   here. If it is available on another machine, run the abstract config there to
   confirm alignment before committing.
3. Keep the device-aware `chip_top.abstract` as our internal signoff and document
   for Bailey that the VCO tank (nmoscap varactors + spiral) needs device-aware
   handling / an origin-normalized abstract in the signoff LVS.

No LVS-affecting change was committed; `verify_cp chip_top` still PASSES
(DRC 0, match uniquely) and the on-main chip is untouched.
