# Outgoing messages, 2026-09-11

Greg sends these. Each block between its markers is one paste. The sources block at the
bottom is working notes and is NOT part of any paste.

## Block A: issue #143 reply to the reviewer (Caglar Ozdag)

<!-- ===== BEGIN A ===== -->

**Scope reframed** at commit `80f14ad`, per your 9/11 feedback. Touched: `info.yaml` (title and
description), `README.md`, `docs/scope.md`, `docs/layout-review-sep01.md`, `docs/pins.md`.

Open-loop integer-N PLL characterization chip: LC-VCO, quadrature divider, PFD and charge pump.
RF-block characterization chip containing the blocks of an integer-N PLL, brought out to pads for
open-loop characterization. Closed-loop lock is not demonstrable on this die: the feedback
divides by 2 only and the PFD has no usable phase-detection window at the ~2.5 GHz reference that
would require. Not a functioning integer-N PLL. `info.yaml` pin, area and gds fields are
unchanged.

**Item 2, DIV2 VSS current density. Table unchanged from the previous update.** Criterion is
GF180MCU DRM 14.2 electromigration, 110 C unidirectional, 1.00 mA/um for M1 to TopMetal-1.

| path | before | after |
|---|---:|---:|
| ib_conv_v1 internal VSS bus | 4.93 | 1.000 |
| DIV2 ties at 0.28 um (IN, QN, QP strips) | 10.571 | 1.000 |
| DIV2 ties at 0.56 um (QN, QP vsegs) | 5.286 | 1.000 |
| DIV2 tie, I_P converter | not connected | 0.987 |
| 7.5 um collector plate | 2.987 | 1.000 |

**Item 3, PEX and re-simulation.** R+C extracted for three blocks: CP_v1 38 devices / 265 caps /
269 resistors, ib_conv_v1 14 / 70 / 526, vco_core 30 / 194 / 208. Every device count equals that
block LVS device count. CP_v1 re-simulated: parasitics move the UP/DOWN current match by at most
0.076 pp. Extracted re-simulation of the CML-to-CMOS converter does not reproduce schematic
behaviour; the cause is characterized as resistive in the converter's VDD distribution, with no
single element responsible. VDD-network relayout and extracted re-verification are in progress
and I will report the numbers here before final release.

**Item 4, nmoscap waiver.** Posting the evidence separately in this thread as a request to the
organizers for explicit acceptance.

<!-- ===== END A ===== -->

## Block B: issue #143 comment to the organizers

<!-- ===== BEGIN B ===== -->

Requesting explicit acceptance of the 168 PL.5a_LV / PL.5b_LV markers on A01.

| | value |
|---|---:|
| KLayout variant-D items on chip_top | 168 |
| bare single nmoscap_3p3 unit | 2x PL.5a_LV + 2x PL.5b_LV = 4 |
| units in vco_varactors | 42, and 42 x 4 = 168 |
| items contributed by bussing | 0 |
| DIV2_QUAD_v1 KLayout items | 0 |
| magic on .mag, gencell aware | 0 |
| magic on flat GDS | 84, the same PL.5a items |

All 168 are internal to the PDK nmoscap_3p3 gencell. The count is exactly 4 per unit across 42
units, bussing contributes none, and no gencell parameter clears it: diffcov/polycov at
80/100/60, all four guard-contact flags off, and guard 0 all still give 4 per unit. The waiver
file accepts exactly these two rule names and no others.

Please confirm whether these 168 markers are accepted for tapeout, or tell us what you need
instead.

<!-- ===== END B ===== -->

## Block C: Discord to Bailey

<!-- ===== BEGIN C ===== -->

Four things on A01. 1) The reviewer supports tapeout on #143, conditions in progress. 2) Our
export form was corrected 9/2 to EAR99 and Complete, but the audit sheet still shows Q12 flagged
and Unrestricted FALSE, so please refresh it. 3) The stray I_P top-level label the 20260907-1
audit reported UNMATCHED is removed, source fix at commit 80f14ad and GDS regenerated at
162faca; the pin list is unchanged at 12. 4) gds/chip_top.gds on main is updated; die bbox
1110 x 550 um and the pin list are unchanged.

<!-- ===== END C ===== -->

## Sources

| claim | source |
|---|---|
| scope wording, files touched | commit `80f14ad`; `info.yaml`, `README.md`, `docs/scope.md`, `docs/layout-review-sep01.md`, `docs/pins.md` |
| criterion 1.00 mA/um at 110 C | `docs/phase8-padframe-plan.md` 3q, GF180MCU DRM 14.2 |
| item 2 before/after table | `docs/layout-review-sep01.md` 4.5, DIV2-level VSS section |
| CP_v1 PEX 38 / 265 / 269 and 0.076 pp | `signoff/pex/README.md` |
| ib_conv_v1 PEX 14 / 70 / 526 | `signoff/pex/ib_conv_v1/README.md` |
| vco_core PEX 30 / 194 / 208 | `signoff/pex/vco_core/README.md` |
| converter re-sim result and cause | `signoff/pex/ib_conv_v1/resim.md`; `docs/layout-review-sep01.md` 6 item 23 |
| 168 markers, 42 units x 4, bussing 0, magic 0 and 84 | `docs/layout-review-sep01.md` 2.5 |
| waiver accepts exactly PL.5a_LV and PL.5b_LV | `team_src/magic/chip_top.waivers` |
| I_P removed, 14 top-level labels, 12 pins | commits `80f14ad` and `162faca`; `info.yaml` pins block |
| die bbox 1110 x 550 um | `gds/chip_top.gds` bbox, KLayout |

## Not in any block, deliberately

- No claim that density passes. It does not, and no block mentions it.
- Item 23 is described by effect, not by our internal item number.
- The export-form status in Block C is Greg's to confirm; it is not file-read from this repo.
