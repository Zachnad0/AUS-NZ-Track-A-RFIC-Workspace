# Phase 7 — chip_top floorplan (2026-08-20)

Die size is settled (config B ≈ 624,000 µm²; a ~470×270 core is ~20% of it). Floorplan
to fit comfortably with real routing channels, not to squeeze.

## Measured block bboxes (from committed GDS)
| block | W × H (µm) | role |
|---|---|---|
| DIV2_QUAD_v1 | 237.4 × 174.2 | ÷2 quad divider — fastest-switching, aggressor |
| vco_v1 | 182.0 × 179.5 | LC VCO — noise victim AND aggressor |
| ibias_gen_v1 | 181.8 × 65.25 | bias — feeds CP (VGP/VGN) + DIV2 (IB_DIV2) |
| CP_v1 | 73.5 × 28.0 | charge pump |
| PFD_lib | 60.0 × 24.0 | phase-freq detector — digital |

## Placement constraints (drive it, not just area)
- vco_v1 kept away from PFD_lib (digital) and from DIV2's converter chains (aggressors).
- ibias between CP_v1 and DIV2_QUAD_v1 (DC bias lines VGP/VGN/IB_DIV2, long runs OK,
  must NOT cross the VCO tank).
- Signal chain REF_IN→PFD→CP→(off-chip loop filter)→VTUNE→vco→DIV2→PFD. CP_OUT & VTUNE
  go off-chip → near their pads. VCO OUT_p/OUT_n → DIV2 CK/CKB is the 5 GHz net → short.
- All 12 pads sit in the upper-left quadrant (config B), clockwise from bottom-left.

## Proposed placement (getcell is LOWER-LEFT aligned; coords in µm, ×200 for iu)
| block | LL (µm) | occupies (µm) |
|---|---|---|
| DIV2_QUAD_v1 | (0, 0) | (0,0) – (237.4, 174.2) — bottom-left |
| vco_v1 | (290, 0) | (290,0) – (472, 179.5) — bottom-right, 53 µm gap from DIV2 |
| ibias_gen_v1 | (0, 205) | (0,205) – (181.8, 270.3) — mid-left, above DIV2 |
| CP_v1 | (210, 205) | (210,205) – (283.5, 233) — mid, right of ibias, near PFD |
| PFD_lib | (210, 245) | (210,245) – (270, 269) — top-mid, far from vco |

**Core bbox ≈ 472 × 270 µm = 127,400 µm².** Channels: 53 µm DIV2↔vco (5 GHz OUT→CK +
isolation), ~31 µm DIV2↔ibias, ~12 µm CP↔PFD. Pad ring (12 pads, upper-left) sits
outside this core; die grows to ~560–600 × 360–400 µm with the ring — still ~1/6 of the
config-B allocation. Rationale: vco (bottom-right) is diagonally opposite PFD (top-mid)
and only abuts DIV2 across a 53 µm channel carrying the one net that must be short.

## Net plan (for rungs 2b–2d)
- REF_IN(pad)→PFD.REF ; PFD.FB←divider feedback (one of DIV2's I/Q outputs — chip-top
  schematic must define which; see phase7 LVS note).
- PFD.UP/DOWN→CP.UP/DOWN ; CP.CP_OUT→CP_OUT(pad).
- VTUNE(pad)→vco.TUNE ; vco.OUT_p/OUT_n→DIV2.CK/CKB.
- DIV2.I_P/I_N/Q_P/Q_N→I_P/I_N/Q_P/Q_N(pads).
- ibias.IBIAS←IBIAS(pad) ; ibias.VGP/VGN→CP.VGP/VGN ; ibias.IB_DIV2→DIV2.IBIAS.
- Power: VDDA(pad)→vco.VDD, CP.VDD, ibias.VDD ; VDDD(pad)→PFD.VDD, DIV2.VDD.
- Ground: chip-wide common (no pin) — vco.GND/ISS-return, all blocks' VSS. Size rails
  for current (DIV2 ~22 mA); check SEGMENTS not just the trunk.
- ~~RST_N(pad)→PFD/DIV2 reset ; MON_OUT(pad)→monitor tap~~ **DROPPED 2026-08-20** — no
  block exposes a reset or monitor port; pins 12→10. PFD.FB now driven by DIV2 **I_P**.
