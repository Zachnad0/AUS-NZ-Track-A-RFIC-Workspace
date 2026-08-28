# Organizer-issued padframe package (A01)

**Do not edit anything under `A01/`.** These are third-party artifacts issued by the
Chipathon 2026 organizers (D. Mitch Bailey), generated from the `info.yaml` we publish on
`main`. They are committed here as *inputs*, verbatim. When the organizers regenerate,
replace the tree wholesale and record the delta below — do not hand-patch.

They live in the repo because they were lost once already: they had only ever been
extracted to a scratch/`/tmp` working dir, nothing in the tree referenced them, and phase-8
depends on them for the DIEAREA and every pin rectangle.

## Provenance

| field | value |
|-------|-------|
| source archive | `A01.def (1).tgz` |
| sha256 | `b07a01ab46b00cbda141a262852e95cffc4e2925b445fd4332dc44087904e720` |
| received | 2026-08-22 |
| generator | Bailey's padframe generator, `spec_blob_sha 7398a4da36e4d6ad9f9b76c06813b073c9c0ed2f` |
| generated from | our `info.yaml` at **12 pins** (pre-VSSD) |

`.gitattributes` marks `padframe/** -text`, so git performs **no** eol conversion and the
files stay byte-exact against a future re-issue.

## What is in it

```
A01/project_defs/
├── A01_selected_variants.json     # project size + which variants were allocated
├── BH/                            # 1110 x 550 um landscape  <-- A01's CHOSEN variant
│   ├── A01_BH.def                 # DIEAREA + PINS 14 (12 user pins; REF_IN -> Y/PU/PD)
│   ├── A01_BH_interface.yaml      # per-pin rects in top_level / extended / translated_user
│   ├── A01_BH_pad_map.yaml        # pin -> slot -> cell, and the padring BREAK list
│   ├── A01_BH_padring.cfg         # slot/cell table for the whole padring
│   ├── A01_BH_padring.def         # placed padring
│   ├── A01_BH_padring.svg         # rendering
│   └── A01_BH_padring.v           # padring netlist (the LVS reference at chip level)
└── BV/                            # 550 x 1110 um portrait, NOT chosen -- kept for the record
```

`translated_user` is the coordinate system our GDS is authored in: origin at the project
lower-left, 200 dbu/µm. `A01_BH.def` `DIEAREA ( 0 0 ) ( 222000 110000 )` = **1110.000 ×
550.000 µm**, which is the exact size chip_top's boundary must become.

## Delta vs the previous issue (`A01.def.tgz`, 2026-08-21)

Only the **project-size metadata** changed. `A01_BH.def`, both `pad_map`s, both
`padring.cfg`s, the `.v` and the `.svg` are byte-identical between the two issues, so no
geometry moved:

| field | 2026-08-21 | 2026-08-22 |
|-------|-----------|-----------|
| `source_gds` | `gds/A01/PFD_lib.gds` | `.../gds/A01/chip_top.gds` |
| `top_cell` | `PFD_lib` | `chip_top` |
| `layout_dbu_microns` | 0.001 | 0.005 |
| `rectangle_dbu` | `[0, 0, 60000, 24000]` | `[-5000, -4300, 99400, 57500]` |
| size | 60 × 24 µm | **522 × 309 µm** |

That closes the "stale generator size" flag in `docs/phase8-padframe-plan.md` §1d — the
generator is now sized from the real block.

## This package is one issue behind our pin list

It was generated from the 12-pin `info.yaml`. As of 2026-08-22 `info.yaml` declares **13**
pins (VSSD added, I/Q reordered to Q_N/I_N/I_P/Q_P, `secondary_esd: false`), so the next
regeneration will differ:

- `N01`–`N05` (CP_OUT + the four I/Q pads) **do not move**;
- `VDDD` shifts `N06` → `N07` and `REF_IN` shifts `N07` → `N08`, both **+100 µm east**;
- `N06` becomes `VSSD` (`gf180mcu_fd_io__dvss`).

**Check on arrival** — `A01_BH_pad_map.yaml` → `breaks[0].before_slot` must name **VSSD's**
slot, not VDDD's. The break's `reason` is `additional_power_ground_set`, i.e. it fires
before a power/ground *set*, and VSSD becomes that set's first member. If the regenerated
map points the break at VDDD instead, VSSD is outside the digital island and must move to
*after* VDDD. Also unverified: that the generator emits `gf180mcu_fd_io__in_c` at `N08`.

See `docs/phase8-padframe-plan.md` §1 and §1e for the full analysis.

## 12-pin re-issue received 2026-08-27 (`A01.def (3).tgz`) — THE CURRENT PACKAGE

| field | value |
|-------|-------|
| source archive | `A01.def (3).tgz` |
| sha256 | `5ea8e9c6c252fc1ce64b12d7383c60e1da939fcfb5de9fe7f251836ec04e27dd` |
| received | 2026-08-27 23:42 |
| extracted to | `A01/project_defs_12pin/` — **BH only, no BV this time** |
| generated from | our `info.yaml` at **12 pins** (I_P removed) |

`A01/project_defs_12pin_SYNTH/` is our own pre-build synthesis, kept for the diff. It was
**exactly right**: 0 pin-level differences against the real package across every slot, cell,
terminal, direction, use and rectangle. The only top-level differences were our `SYNTHESIZED`
marker, `participant_pin_count` (we left it at 13; the real one says 12), and `top_cell_text`,
which is his scrape of our GDS and so necessarily newer than ours. Keep both until the dry run;
delete the SYNTH copy after.

**The padring break followed VSSD, as predicted**: `BRK_BEFORE_N06` -> **`BRK_BEFORE_N05`**,
reason still `additional_power_ground_set`, and `BRK_AFTER_BH` moved N08 -> N07. The prediction
came from `padring.cfg` being a SEQUENTIAL table where `BREAK` is positional and keyed to cell
type, not slot number — the same pattern is visible at W17/W18.

**`top_cell_text` settles the f31d594 open risk.** That commit demoted VSSD's label to 36/0 and
recorded as unverified whether Bailey's scrape reports datatype-0 text. It does: the scrape
lists `VSSD` at **36/0**, `IBIAS` at **36/0** (our block-tap demotion) and `I_P` at **34/0**
(demoted when it stopped being a pad), alongside every 36/10 port. So the demotions cost us
nothing in his audit, and there are no audit flags for A01 anywhere in the package.
