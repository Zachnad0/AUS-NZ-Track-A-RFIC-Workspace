# Phase 7 — chip_top routing plan (rungs 4a–4c) — 2026-08-20

**Status: DEFERRED (executable plan below).** The chip GOLDEN
(`team_src/magic/chip_top_golden.spice`) and the LVS harness (`chip_top.abstract`,
`verify_cp.sh chip_top`) are DONE and validated: on the unrouted merge, `verify_cp chip_top`
gives **magic DRC 0, 25 nets, LVS DO NOT MATCH** — the mismatch is entirely the missing
inter-block metal. The golden is independent of the routing (generated from `chip_top.sch`),
so any route can be checked against it with one `verify_cp` run.

Why deferred, not done blind: a DRC-clean, short-free, LVS-matching route of ~11 inter-block
nets + power across a 472×270 µm die, authored in a script without interactive layout
iteration, is a multi-hour job and exactly the situation that has produced every silent short
in this project (a horizontal hop sharing a layer with the vertical riser it crosses). It
exceeds the 15-min-per-task budget. This plan makes the execution deterministic.

## The work-list (chip coords, µm — from `team_src/magic/phase5/port_map.py`)

Pick ONE terminal per block per net (blocks already tie their own multi-label ports internally).

| net | A (block.pin, layer, x,y) | B (block.pin, layer, x,y) | span | notes |
|---|---|---|---|---|
| **VGP** | ibias.VGP M2 (48.9, 222.1) | CP.VGP M2 (210.5, 228.6) | ~162 µm | same layer M2 |
| **VGN** | ibias.VGN M2 (81.9, 268.6) | CP.VGN M2 (230.8, 210.6) | ~150 µm | same layer M2 |
| **IB_DIV2** | ibias.IB_DIV2 M2 (116.3, 268.6) | DIV2.IBIAS M2 (142.3, 92.3) | ~176 µm | same layer M2 |
| **UP** | PFD.UP M2 (246.1, 268.7) | CP.UP M3 (282.3, 220.5) | ~60 µm | M2↔M3 (via2) |
| **DOWN** | PFD.DOWN M2 (247.2, 268.7) | CP.DOWN M2 (271.7, 214.8) | ~59 µm | same layer M2 |
| **I_P** | DIV2.I_P M1 (235.2, 140.3) | PFD.FB M2 (230.4, 245.3) + I_P pad | ~105 µm | M1↔M2; also a pad |
| **VCO_OUTP** | vco.OUT_p M5 (401.8, 94.5) | DIV2.CK M2 (65.0, 109.8) | **~337 µm** | M5↔M2; the ~2.5 GHz net; DIV2.CK is mid-die, NOT on the vco side — floorplan's "short 5 GHz net" assumption does not hold for the real port locations |
| **VCO_OUTN** | vco.OUT_n M5 (398.0, 94.5) | DIV2.CKB M2 (130.0, 109.8) | ~268 µm | M5↔M2; keep matched to VCO_OUTP (differential) |
| **VDDD** | PFD.VDD M4 (229.7, 256.8) | DIV2.VDD M4 (90.0, 124.0) | ~140 µm | same layer M4 |
| **VDDA** | vco.VDD M2 (397.4, 74.8) | CP.VDD M2 (219.5, 231.6) | 3-way star | + ibias.VDD M2 (74.2, 231.6); all M2 |
| **GND** | CP/DIV2/ibias/vco VSS M2 + vco.GND M1 (358.5,49.8) + PFD.VSS M4 (233.0,256.8) | — | 6-way star | chip-wide common; mostly M2 |

Pads (label only + tie to the net; no pad cells — organizer padframe): **IBIAS** ibias.IBIAS
M2 (71.3,223.9); **VTUNE** vco.TUNE M1 (358.7,66.7); **CP_OUT** CP M4 (272.3,215.4); **I_P**
DIV2.I_P (shares the I_P net); **I_N** DIV2.I_N M1 (2.2,140.3); **Q_P** DIV2.Q_P M1
(235.2,51.9); **Q_N** DIV2.Q_N M1 (2.2,51.9); **REF_IN** PFD.REF M3 (210.3,257.6); **VDDA**,
**VDDD** on their routed rails.

## Layer discipline (prevents the silent-short family)

- **Horizontal runs on M4; vertical runs on M3; via3 at every H/V junction.** An H hop and a
  V riser then never share a layer. Two H-nets on M4 → unique Y lane; two V-nets on M3 →
  unique X lane. (Power VDDA/VDDD/GND may use wide M2 straps in the free bands instead.)
- **Confine routing to free space; do NOT route over a block on a layer it uses.** Free bands:
  the y≈174–205 channel (x0–237, ~31 µm) above DIV2 / below ibias; the x≈237–290 channel
  (53 µm) between DIV2 and vco; the region x237–472, y179.5–205 above vco. Grow the die by a
  ~30–40 µm routing margin (config B has ~624,000 µm²; the core is 127,000 — ample room) so
  power rings and long escapes run in the margin, not over cells.
- **vco M5 HAZARD:** the dual spiral occupies vco's M5. Never cross vco on M5. Reach vco.VDD
  (M2), vco.OUT_p/n (M5 leads on vco's left edge ~x398), vco.TUNE (M1), vco.GND/ISS from the
  DIV2↔vco channel (x237–290) on M2/M3/M4, staying clear of the coil.
- Via/enclosure constants (gotchas): via1=52, via2/3/4=56; metal1 encloses via1 by 12; metal
  encloses via3/4 by 2; M3/M4 width 56 (0.28 µm min, use ≥0.6 µm); **M5 min width 88, min
  area 21060**. Extend every segment by its half-width at L-corners. `via_m2m4` paints NO M2 —
  add an explicit M2 pad first. A top-level port label needs top-level metal to land on
  (paint M-over-child-port before labeling). QUERY each rail's real extent; never assume.

## Where to author it

In **KLayout**, as a routing pass appended to `team_src/magic/phase5/chip_merge.py` (the
verbatim golden-merge that builds the deliverable GDS) — magic must not re-render the blocks
(gds-roundtrip perturbs foundry geometry → the DV.5 sliver). Add: (1) 4a power straps/rings,
(2) 4b signal wires per the table, (3) 4c 10 die-edge port labels. Then keep
`chip_top.mag`/`chip_merge.py` consistent via `phase5/check_placement.py`.

## Gates per rung (already wired)

- **magic DRC 0** — `magic … chip_top.tcl` (abstract-aware) or `verify_cp chip_top`'s DRC line.
- **KLayout var-D ≤ 168** (W4 varactor only) — `run_drc.py --variant=D --topcell=chip_top`.
- **LVS progress** — `PDK=gf180mcuD PDK_ROOT=/foss/pdks verify_cp.sh chip_top`; watch the net
  count fall from 25 toward a unique match against `chip_top_golden.spice`.

## Order of execution (each a WIP commit)

1. 4a power: GND common first (biggest net), then VDDA star, then VDDD. Re-run verify_cp — net
   count should drop by ~ (terminals−1) per net joined.
2. 4b signals: the M2 same-layer nets first (VGP, VGN, IB_DIV2, DOWN, VDDD), then the
   cross-layer ones (UP, I_P), then the long differential pair VCO_OUTP/VCO_OUTN last.
3. 4c: 10 die-edge port labels; re-run verify_cp for the final unique match + zero
   property/port errors.
