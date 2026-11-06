# D-block plan: reseating `chip_top` into the 605 × 605 µm die

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)** · 2026-11-06

Bailey issued a new package on issue #143 (comment dated 2026-11-06 05:07 UTC): "Please use the
`D` block". Unpacked at `padframe/A01/project_defs_D/`, tarball sha256
`8991a3ebe8c5e9f0ceb7af7fb5a39783548a4e324c81010a13156250d7024d5a`. Die 605 × 605 µm, usable
366,025 µm², no blockages. This supersedes the 1110 × 550 µm BH die.

> **Status (2026-11-06).** Rungs 1–6 are built, through `402b1d9`. As-built routes differ from this
> plan in places: VSSA descends at x100, the ISS riser is at x14.7, IBIAS at x36, VTUNE's lane at
> y150 and riser at x2.25. The as-built numbers are in `docs/verification.md` §8.13.

All coordinates are **die-frame µm in seat A** unless marked otherwise. Lengths are pre-layout
estimates until the rung that builds them.

## Seat A

`DX, DY = 100, 255` (was 200, 200): the core moves −100 in x and +55 in y. That equals the north
pins' move exactly, so every north row keeps its core coordinates.

| | bbox | margin W / E / S / N |
|---|---|---|
| GND ring, outer (measured from GDS) | (75, 237.5)–(597, 542.5) | 75 / 8 / 237.5 / 62.5 |
| Blocks | (100, 255)–(572, 525.25) | 100 / 33 / 255 / 79.75 |

Landmarks: ring left leg x 82.5–97.5, bottom strap y 237.5–252.5, top strap y 527.5–542.5.
DIV2 (100, 255)–(337.36, 429.17), vco_v1 (390, 255)–(572, 434.48), spiral (390, 350.48)–(572,
434.48), ibias (100, 460)–(281.76, 525.25), CP (310, 460)–(383.5, 488.02), PFD (310, 500)–(366.99,
524). The ring was quoted as 522 × 309 µm; that is the old core metal extent including west stubs.
The ring itself measures 522.0 × 305.0 µm.

## The rules for every row

- Power on M4/M5. Signals on M2/M3.
- Risers run inboard of the pin column. All west pins sit at x 0–1, so a riser in that column would
  short every pin it passes.
- Nothing crosses over the vco spiral.
- Pin landings are bars or plates across the whole finger group, never a drop at the slot centre.
- `R.hwire`/`R.vwire` extend half their width past each endpoint; check grown extents.

Two as-built items sit outside the signal rule and are recorded rather than changed: IBIAS's
short M4 hop over the Q_N/I_N risers, and CP_OUT's own 0.6 µm M4 tap stub.

## The 8 north rows: unchanged

I_N, Q_N, Q_P, VSSD, VDDD, REF_IN, REF_IN_PD, REF_IN_PU. Core coordinates are untouched, and a
landing run with the D targets shifted by the seat passes all 8 (measured before any edit).

## The 6 west rows: to rebuild

Removed in rung 1 because their BH routes reach die x −100, then rebuilt one rung at a time.

| Row | Pin (x 0–1) | Layer | Route | Est. length | Crossings |
|---|---|---|---|---:|---|
| VSSA | y 1.36–73.64 | M5, M2 plate | Ring bottom strap → M5 south (15 µm) at x 90 → y 37.5 → M5 west (9.5 µm) → via at x 16 → M2 plate x 0–16 | 282 µm | ISS lane crosses it once; ISS takes the M4 hop |
| VDDA | y 101.36–173.64 | M4, M2 plate | Via onto the M5 bus at (160, 454) → M4 west, under the ring's left leg → M4 riser x 46 south → y 137.5 → feeder and 18 µm M2 plate | 458 µm | Ring left leg (M4 under M5); clamp feeds tap this riser |
| IBIAS | y 215.34–259.66 | M3, M2 plate | Tap (171.3, 478.9) → M3 west with the existing M4 hop → M3 riser x 34 south → clamp node. Pad plate reaches the core only through the ballast | 379 µm | Q_N/I_N risers (M4 hop); ring left leg |
| ISS | y 315.34–359.66 | M4/M5, M2 plate | Strap and M4 gap descent kept → y 195 → M5 lane west → M4 hop over VSSA → M5 riser x 65 → M5 bus y 337.5 over both clamp bridges → via at x 14 → M2 plate | 737 µm | Ring bottom (M4, existing); VSSA (M4 hop) |
| VTUNE | y 415.34–459.66 | M3, M2 plate | Tap (458.68, 321.7) → M3 west to the gap x 365 → south to y 205 → west to x 10 → M3 riser north → y 437.5 → M2 plate | 798 µm | Ring bottom strap (M3 under M5); VSSA, ISS (other layers); passes below the IBIAS clamp |
| CP_OUT (new) | y 515.34–559.66 | M3, M2 crossing, M2 plate | Existing tap → M3 → M2 across x 400/405 → M3 riser → M3 lane y 585 west → x 10 → M3 south → y 537.5 → M2 plate | 524 µm | Q_P, REF_IN risers (M2, as today); Q_N/I_N/Q_P M2 drops (lane on M3) |

Nothing here runs over the spiral. VTUNE's tap at y 321.7 is below the spiral's y 350.48.

## Clamps

Neither clamp cell contains M5: `esd_pd2nw`, `esd_nd2ps` and `esd_rpoly` stop at M1 (34/0).

| Clamp | Was (BH) | Now | Why |
|---|---|---|---|
| IBIAS (`esd_rpoly`, `esd_pd2nw`, `esd_nd2ps`) | y 268–292.22 | **y 213–237.22** (Δy −55) | −45 with the pin, −10 to clear the ring. Top edge is 0.28 µm below the ring's y 237.5 |
| ISS (`esd_pd2nw`, `esd_nd2ps`) | y 368–392.22 | **y 323–347.22** (Δy −45) | With the pin. Right edge x 72.6 is 2.4 µm short of the ring |

x positions are unchanged. VSSA straps change shape: the IBIAS strap is now a 10 µm M2 vertical
from the nd2ps frame up into the ring bottom strap, because the clamp sits below the ring. The ISS
strap stays horizontal, into the ring's left leg at x 90.

## East edge

The PU bar's right edge lands at x 599.345, **5.655 µm** from the die edge; the ring's is 8 µm. The
DRC deck has **no minimum distance to a block or die edge**: `pr_bndry` is used only for off-grid
and angle checks, and `CHIP` only for density and antenna windows. The deck cannot see what the
padframe places next to the block. Worth confirming with Bailey that a neighbouring block cannot
come closer than that margin assumes.

## Rungs

Each rung: edit, rebuild (~4 s), six-gate pass (~1 min), one commit.

| Rung | Scope | Estimate |
|---|---|---|
| **1** | Seat, boundary, keep-outs, clamps, `landing_check.py` on D. West rows out | done |
| 2 | VSSA and VDDA (power first, so the clamps tie off) | 30 min |
| 3 | ISS: lane, hop, riser, bus over the clamp node | 30 min |
| 4 | IBIAS: haul, riser to the clamp node, ballast, plate; seed update | 30 min |
| 5 | VTUNE | 20 min |
| 6 | CP_OUT, the new W22 landing | 20 min |
| 7 | Full gate set, organizer LVS, density, new DRC baseline, `info.yaml` review | 30 min |

LVS cannot pass until rung 6. Landing rows are expected to turn green one rung at a time.

## Rung 1 result (2026-11-06)

`route_chip.py` carries `WEST_ROWS_BUILT = False`, which switches off the BH west routes and keeps
their code and notes for the rebuild. The ISS strap, escape and M4 gap descent stay. The clamps'
connecting stubs are in place and open until their rows arrive.

| Gate | Result |
|---|---|
| Rebuild control before any edit | XOR 0.000 µm² against the committed GDS, labels identical |
| Boundary | exactly (0, 0)–(605, 605), bbox asserts pass |
| `landing_check.py` (now defaults to D) | 8 north rows OK, 6 west rows FAIL, as planned |
| Magic DRC (`drc_boxset.tcl`, `drc_delta.py`) | 0 boxes, 0 added, 0 removed; baseline recaptured |
| `klayout_signoff.py chip_top` | 0 violations, no waivers |
| Metal-only nets, routes-only and flattened, BH vs D | no new merges; 5 more nets, the open west stubs |
| `verify_cp.sh chip_top` | DRC 0, 10/10 devices, blocks match; fails on nets 25 vs 20 and ports 10 vs 11, as expected |
| `check_placement.py` | consistent |
| `varactor_comp_gate.py` | PASS, 42 varactors, 1050 µm² |
