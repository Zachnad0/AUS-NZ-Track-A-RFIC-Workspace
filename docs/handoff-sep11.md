# Draft comment for sscs-ose/sscs-chipathon-2026 issue 143

Greg posts this. Paste everything between the markers. The sources block below the
comment is working notes and is NOT part of the paste.

<!-- ===== BEGIN COMMENT ===== -->

**Item 2 closed: DIV2 VSS current density.** Criterion GF180MCU DRM 14.2 electromigration, 110 C unidirectional, 1.00 mA/um for M1 to TopMetal-1. Figures mA/um.

| path | before | after |
|---|---:|---:|
| ib_conv_v1 internal VSS bus | 4.93 | 1.000 |
| DIV2 ties at 0.28 um (IN, QN, QP strips) | 10.571 | 1.000 |
| DIV2 ties at 0.56 um (QN, QP vsegs) | 5.286 | 1.000 |
| DIV2 tie, I_P converter | not connected | 0.987 |
| 7.5 um collector plate | 2.987 | 1.000 |

The I_P converter VSS tie was drawn at the wrong y and reached nothing, so that instance returned its 2.96 mA through the p-substrate. LVS could not see it because the substrate is one global node. It is now metal-connected. Gates at ce09ccf: magic DRC 0, netgen LVS match uniquely (chip_top 10 devices, 11 ports, 0 property errors), KLayout variant-D 168 all waived, drc_delta 0 added 0 removed, landing_check 14/14, check_placement consistent.

**Item 4, nmoscap waiver.** Please confirm explicit acceptance.

| | value |
|---|---:|
| KLayout variant-D items on chip_top | 168 |
| bare nmoscap_3p3 unit | 2x PL.5a_LV + 2x PL.5b_LV = 4 |
| units in vco_varactors | 42, and 42 x 4 = 168 |
| from bussing / from DIV2_QUAD_v1 | 0 / 0 |
| magic on .mag / on flat GDS | 0 / 84, same PL.5a |

No gencell parameter clears it: diffcov/polycov at 80/100/60, all four guard-contact flags off, and guard 0 all still give 4 per unit.

**Item 3, PEX.** R+C extracted for three blocks: CP_v1 38 devices / 265 caps / 269 resistors, ib_conv_v1 14 / 70 / 526, vco_core 30 / 194 / 208. Every device count equals that block LVS device count. No full-chip PEX.

**Item 4a, density.** Full die 1110.000 x 550.000 um = 610,500 um2, measure only, no fill generated. All eight are minimum-coverage floors, not max-density violations. MT.3 and M5.4 are one physical layer in this 5 metal stack, so their shortfalls are not additive. Is fill team-owned or integration-owned?

| layer | rule | measured | floor | shortfall um2 |
|---|---|---:|---:|---:|
| COMP | DCF.1b | 1.622% | 25% | 142,720 |
| Poly2 | PL.8 | 1.140% | 14% | 78,511 |
| Metal1 | M1.4 | 0.790% | 30% | 178,325 |
| Metal2 | M2.4 | 2.238% | 30% | 169,488 |
| Metal3 | M3.4 | 0.371% | 30% | 180,885 |
| Metal4 | M4.4 | 1.476% | 30% | 174,138 |
| Metal5 / MetalTop | M5.4 / MT.3 | 7.835% | 30% | 135,317 |

**chip_top.** gds/chip_top.gds on main was updated 2026-09-11 at ce09ccf, DIV2 fixes only. Die bbox 1110 x 550 um and the 12-pin list are unchanged.

<!-- ===== END COMMENT ===== -->

## Sources

| claim | source |
|---|---|
| criterion 1.00 mA/um at 110 C | `docs/phase8-padframe-plan.md` 3q, GF180MCU DRM 14.2 |
| bus 4.93 to 1.000; tie and plate before/after | `docs/layout-review-sep01.md` 4.5, DIV2-level VSS section |
| I_P tie disconnected, substrate return, LVS-blind | `docs/layout-review-sep01.md` 6 item 10d |
| chip_top gates at ce09ccf | `docs/layout-review-sep01.md` 4.5 chip_top section; commit `0a4b73b` |
| 168 items, 42 units x 4, bussing 0, DIV2 0, magic 0 and 84 | `docs/layout-review-sep01.md` 2.5 |
| waiver accepts exactly PL.5a_LV and PL.5b_LV | `team_src/magic/chip_top.waivers` |
| CP_v1 PEX 38 / 265 / 269 | `signoff/pex/README.md` |
| ib_conv_v1 PEX 14 / 70 / 526 | `signoff/pex/ib_conv_v1/README.md` |
| vco_core PEX 30 / 194 / 208 | `signoff/pex/vco_core/README.md` |
| density percentages and floors | `run_drc.py --density_only --variant=D` log, recorded at `docs/layout-review-sep01.md` 6 item 13 |
| die 1110.000 x 550.000 um | `gds/chip_top.gds` bbox, KLayout |
| shortfall um2 | computed as (floor - measured) x 610,500 um2 |
| 12-pin list unchanged | `info.yaml` pins block |

## Not in the comment, deliberately

- Item 1 (loop lock) is not mentioned. It was answered 2026-09-01 and Caglar has not replied.
- Item 10d is described by effect, not by our internal item number.
- No claim that density passes. It does not. Only the measurement is reported.
