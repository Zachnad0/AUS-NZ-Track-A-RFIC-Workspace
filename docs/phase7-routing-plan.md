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

---

## PROGRESS + LESSONS (2026-08-20, rung 3a WIP)

Routing infra is built and validated: `route_lib.py` (via stacks M1–M5, wires; gf180 via
0.26 µm + enclosures) is **DRC-clean** in isolation (`route_selftest.py`). `route_chip.py`
adds top-level metal to the placed `chip_top.gds` (run after `chip_merge.py`).

**Power buses** live in the **y[180,205] band** — verified clear of ALL block geometry across
the full width. Ports escape up a via stack to **M4**, an **M4 riser** drops to the bus level,
**via4 to the M5 bus only at the target**.

**SILENT SHORT — found and fixed (the key lesson).** The first cut ran risers on **M5**, so a
riser crossing a *non-target* M5 bus silently merged two nets (the GND riser crossed the VDDD
bus → PFD.VDD extracted as `VSUBS`). **DRC-legal, LVS-fatal.** This is the project's recurring
failure mode. Rule for all remaining routing: **vertical risers on M4, horizontal buses on M5;
a riser vias to M5 only where it joins its own bus.** Verified by re-extraction: after the fix
each supply is a distinct net and VDDA correctly ties CP.VDD + ibias.VDD.

**Connected so far** (magic DRC 0, KLayout var-D 168): VDDA = CP.VDD + ibias.VDD; GND bus on
CP/ibias/PFD VSS; VDDD bus on PFD.VDD. No shorts.

**The hard blocker — interior ports in dense metal.** vco (VDD/GND/ISS) and DIV2 (VDD/VSS,
CK/CKB) expose their ports deep inside dense block metal (DIV2 dense on M2/M3/M4; vco active
dense on M1/M2). A via drop lands on the port fine (M3/M4/M5 are locally clear above it), but
the **riser from the port out to a channel/band crosses dense block metal and shorts**. These
need per-net threading through the sparse upper-layer gaps — the remaining iterative work.
Reachable-from-a-channel ports (CP/ibias/PFD, DIV2 I_P/Q_P on the right edge, PFD REF/UP/DOWN
on its edges) route cleanly; interior ports are the cost. The loop is `chip_merge → route_chip
→ run_drc / verify_cp chip_top` (watch the net count and the per-block VDD/VSS net names).

---

## ITEM 1+2 (2026-08-20): the "interior port" blocker is REFUTED; real EM sizing

**Tap a net anywhere on its metal, not at its label.** Full-extent geometry (`net_extent.py`,
`corridor.py`) shows the "buried" power ports reach accessible metal:

| net | metal extent (chip µm) | closest block edge | escape |
|---|---|---|---|
| DIV2.VSS (M2) | x[59,184] y[6.4,84.6] | **bottom 6.4 µm** | tap low, out the bottom margin |
| DIV2.VDD (M4) | x[54,183] y[84,138] | top 36.5 µm | hardest — see below |
| vco.VDD (M2) | x[390,410] y[73,75] | right 62 µm | jog to the x366–385 M5 corridor, riser up |
| vco.ISS (M2) | x[387,413] y[60] | right 59 µm | same corridor |
| vco.GND (M1) | x[357,360] y[50,68] | bottom 50 µm | below spiral; jog to corridor |

**M5 occupancy / clear corridors:** PFD **0** M5 (fully clear); ibias/CP **4** each (thin
rails at y270 / y213,231); vco spiral fills x290–366 but **x366–385 is an M5-clear vertical
corridor**; DIV2 M5 fills x33–204 but **x220–235 is M5-clear**. So over-block M5 routing is
possible in the clear columns. DIV2.VDD is the one genuinely awkward net (extent x≤183, y≤138;
nearest M5 corridor x220–235 is 37 µm right and its own metal doesn't reach it) — will need a
short M-jog or a lower-layer thread; flagged.

**EM sizing** (`em_sizing.py`; 1 mA/µm M2–M4, 2 mA/µm M5):

| net | segment | width | I (mA) | mA/µm | verdict |
|---|---|--:|--:|--:|---|
| GND | M5 bus | 15 µm | 26.4 | 1.76 | OK |
| VDDD | M5 bus | 12 µm | 22.9 | 1.91 | OK |
| VDDA | M5 bus | 3 µm | 3.5 | 1.17 | OK |
| VDDD | DIV2.VDD riser | **23 µm** | 22.4 | 0.97 | OK (22 µm was 1.02, over) |
| GND | DIV2.VSS riser | **23 µm** | 22.4 | 0.97 | OK |
| VDDA | vco.VDD riser | 2 µm | 2.0 | 1.00 | OK |
| ISS | vco.ISS riser | 2 µm | 1.0 | 0.50 | OK |
| — | PFD/CP/ibias risers | 1–2 µm | ≤1.0 | ≤0.5 | OK |

Currents: **VDDA 3.5, VDDD 22.9, GND 26.4, ISS 1.0 mA** (DIV2 22.4 on record; vco/CP/ibias/PFD
estimated from bias structure). **Band-fit:** GND15+VDDD12+VDDA3+spacing = 32 µm > the 25 µm
band → **GND's 15 µm strap goes in a grown bottom margin** (DIV2.VSS reaches 6.4 µm from the
bottom edge, taps straight down); VDDD12+VDDA3 stay in the y[180,205] band.

---

## SESSION 2026-08-20b: GND is free, power+ports routed, signal map

**Biggest realization: GND needs NO routing.** Every block's VSS and vco.GND already extract as
**VSUBS (substrate)** — the chip-wide common has no pad, so it is one net by construction. Power
routing is only VDDA + VDDD.

**Routed & DRC-clean (KLayout signoff PASS = W4 waiver only; magic DRC 0; check_placement OK):**
- **VDDD = PFD.VDD + DIV2.VDD** COMPLETE. DIV2.VDD tapped on its M4 collector (x160 @ y137.5),
  risen up the x160 M5-clear column.
- **VDDA = CP.VDD + ibias.VDD** (2/3).
- **11 port labels** (VDDA VDDD on buses; IBIAS VTUNE ISS CP_OUT I_P I_N Q_P Q_N REF_IN on the
  block ports) → chip_top ports 0 → **11**.
- Extraction diff'd every rung; **one silent short caught** (vco.VDD corridor riser touched the
  OUT_p lead → OUT_p=VDDA) and backed out.

**Signal-net accessibility (`sig_extent.py`, tap at extent):**
| net | A (accessible?) | B (accessible?) | verdict |
|---|---|---|---|
| UP | PFD.UP top edge (0µm) | CP.UP right edge (1µm) | tractable |
| DOWN | PFD.DOWN top edge | CP.DOWN 9.7µm from bottom | tractable |
| FB=I_P | PFD.FB bottom edge (0µm) | DIV2.I_P right edge (1.2µm) | tractable, ~105µm span |
| VGP | ibias.VGP 17µm up | CP.VGP top edge (0.1µm) | tractable |
| VGN | ibias.VGN top edge (1.5µm) | CP.VGN bottom edge (1.3µm) | tractable |
| IB_DIV2 | ibias.IB_DIV2 top edge | **DIV2.IBIAS 81.7µm deep** | hard |
| VCO_OUTP/N | vco.OUT_p/n right edge | DIV2.CK/CKB interior, **337µm span** | hard (diff pair) |

**Remaining for LVS match:** vco.VDD (a tap clear of the OUT_p lead), the 8 signal nets above,
then `verify_cp chip_top` unique match. GND + ports + VDDD + 2/3 VDDA are done.
