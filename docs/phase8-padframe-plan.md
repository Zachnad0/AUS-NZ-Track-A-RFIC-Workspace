# Phase 8 — padframe DEF integration: analysis & plan

Analysis of the organizer's issued padframe DEF (`A01.def.tgz`, extracted from a
working dir — not committed; analysis/docs only this session). **Two things are
blocked and out of scope:** (1) whether a second ground pin **VSSD** is required
(Bailey: "two ground pins, one per power region"; expanded Friday — the issued
DEF has none, so a regenerated DEF is expected), and (2) therefore the final pin
list and top-level boundary. Everything here holds regardless of how that lands.

Baseline is known-good: `verify_cp` PASS (DRC 0, LVS match uniquely) on `chip_top`
and all five blocks (this session, §5).

---

## 1. DEF inventory (both variants)

DEF units are **200 dbu/µm** (5 nm). `translated_user` = pin rectangle in the
**project's own frame** (origin at the project LL). Pin rects are all **Metal2**.
Both variants: `DIEAREA (0 0)–(…)`, `PINS 14` (12 user pins; REF_IN expands to 3).

### BV — 550 × 1110 µm (portrait). origin 350,1475. vss_fixed W12. usable 610500 µm²

| pin | slot | cell | use | dir | edge | translated_user bbox (µm) |
|-----|------|------|-----|-----|------|---------------------------|
| VSSA | W13 | dvss | GROUND | INOUT | west | x0–1, y106.4–178.6 |
| VDDA | W14 | dvdd | POWER | INOUT | west | x0–1, y206.4–278.6 |
| IBIAS | W15 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y320.3–364.7 |
| ISS | W16 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y420.3–464.7 |
| VTUNE | W17 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y520.3–564.7 |
| CP_OUT | W18 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y620.3–664.7 |
| I_P | W19 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y720.3–764.7 |
| I_N | W20 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y820.3–864.7 |
| Q_P | W21 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y920.3–964.7 |
| Q_N | W22 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y1020.3–1064.7 |
| VDDD | N01 | dvdd | POWER | INOUT | north | x31.4–103.6, y1109–1110 |
| REF_IN (Y) | N02 | in_c | SIGNAL | INPUT | north | x133.8–134.1, y1109–1110 |
| REF_IN_PD (PD) | N02 | in_c | SIGNAL | OUTPUT | north | x194.3–194.7, y1109–1110 |
| REF_IN_PU (PU) | N02 | in_c | SIGNAL | OUTPUT | north | x198.7–199.0, y1109–1110 |

- **Pin-rectangle y-span: y[106.4, 1110.0] µm.** Most distant pin top = **y1110**
  (north). chip_top is **309 µm tall** → **reach shortfall ≈ 801 µm** to the north
  edge; the west analog pins climb to y1065 (Q_N), ~756 µm above chip_top's top.

### BH — 1110 × 550 µm (landscape). origin 350,2035. vss_fixed [] (none). usable 610500 µm²

| pin | slot | cell | use | dir | edge | translated_user bbox (µm) |
|-----|------|------|-----|-----|------|---------------------------|
| VSSA | W18 | dvss | GROUND | INOUT | west | x0–1, y46.4–118.6 |
| VDDA | W19 | dvdd | POWER | INOUT | west | x0–1, y146.4–218.6 |
| IBIAS | W20 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y260.3–304.7 |
| ISS | W21 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y360.3–404.7 |
| VTUNE | W22 | asig_5p0 | SIGNAL | INOUT | west | x0–1, y460.3–504.7 |
| CP_OUT | N01 | asig_5p0 | SIGNAL | INOUT | north | x45.3–89.7, y549–550 |
| I_P | N02 | asig_5p0 | SIGNAL | INOUT | north | x145.3–189.7, y549–550 |
| I_N | N03 | asig_5p0 | SIGNAL | INOUT | north | x245.3–289.7, y549–550 |
| Q_P | N04 | asig_5p0 | SIGNAL | INOUT | north | x345.3–389.7, y549–550 |
| Q_N | N05 | asig_5p0 | SIGNAL | INOUT | north | x445.3–489.7, y549–550 |
| VDDD | N06 | dvdd | POWER | INOUT | north | x531.4–603.6, y549–550 |
| REF_IN (Y) | N07 | in_c | SIGNAL | INPUT | north | x633.8–634.1, y549–550 |
| REF_IN_PD (PD) | N07 | in_c | SIGNAL | OUTPUT | north | x694.3–694.7, y549–550 |
| REF_IN_PU (PU) | N07 | in_c | SIGNAL | OUTPUT | north | x698.7–699.0, y549–550 |

- **Pin-rectangle x-span: x[0, 699.0] µm.** Most distant pin right = **x699** (north,
  REF_IN_PU). chip_top is **522 µm wide** → **reach shortfall ≈ 177 µm** horizontally;
  the north pins sit at y550, **≈ 241 µm** above chip_top's 309-µm top.

### 1c. Padring breaks (from the full 2935×2935 `padring.cfg`)

The `.cfg` is the workshop-wide padring; A01 occupies a slot subset. Breaks insert
`brk5` break-fillers, splitting the continuous VDD/VSS rails into isolated islands.
The `.cfg` gives no per-break comment; the structure shows two relevant breaks:

- **Inter-project break** — after `W11 dvss`, a `BREAK` precedes A01's west run
  (`W12 dvss / W13 dvss / W14 dvdd / W15… asig`). Isolates A01's west power island
  from the neighbouring project. All A01 west pads share **one rail powered by VSSA
  + VDDA** (BV: W13/W14; BH: W18/W19), feeding the west analog pads' ESD.
- **Digital-domain break** — the VDDD + REF_IN pads sit **between two BREAKs**
  (BV: `BREAK; N01 dvdd; N02 in_c; BREAK`; BH: `BREAK; N06 dvdd; N07 in_c; BREAK`).
  This isolates a **digital island powered by VDDD** containing REF_IN. **It has no
  dedicated ground pad** in the issued DEF — exactly the "second ground (VSSD)"
  gap Bailey flagged for Friday. In BH the five analog north pads (CP_OUT, I/Q) sit
  **before** that break, so they share the VSSA/VDDA analog rail (continuous from
  the west run through the NW corner); in BV all analog signals are on the west rail.

Result — **which pins land on which rail:** analog rail (VSSA+VDDA) → IBIAS, ISS,
VTUNE, CP_OUT, I_P, I_N, Q_P, Q_N (+ VSSA, VDDA themselves); digital island (VDDD,
no VSSD yet) → VDDD, REF_IN.

### 1d. Generator project size — the OLD block, confirmed

`A01_selected_variants.json`: `source_gds gds/A01/PFD_lib.gds`, `top_cell PFD_lib`,
`rectangle_dbu [0,0,60000,24000]` → **60 × 24 µm**, `participant_pin_count 12`,
`selected_variants [BV, BH]`. So the generator sized the project from the **old
PFD_lib block (60×24), not chip_top (522×309)** — as expected.

**Did it affect the allocation? No.** The die size and pin slots are set by the
config + pin count (12), not the project GDS: both variants give **610500 µm²
usable**, ≫ chip_top's 161,000 µm² (522×309), so there is no under-allocation. The
stale 60×24 is metadata only — it would matter solely if a fit-check consumed it,
which it did not. **Flag:** re-point the generator's `source_gds`/`top_cell` at
`chip_top` before any future fit-check or a regenerated DEF, so the recorded
project size is the real 522×309.

---

## 2. REF_IN needs three connections (in_c PU/PD) — findings

The DEF expands REF_IN onto `gf180mcu_fd_io__in_c` (PINS 14): **REF_IN** on **Y**
(INPUT), **REF_IN_PU** on **PU** (OUTPUT), **REF_IN_PD** on **PD** (OUTPUT). "OUTPUT"
is from the core's view — the core **drives** PU/PD (they are the cell's control
inputs).

**What PU/PD do (cited):**
- Official GF180MCU IO datasheet lists `in_c` as *"5V WR CMOS input only pad with
  pull-up/down"* — PU/PD control an on-pad pull-up/pull-down.
- PDK **liberty** (`gf180mcu_fd_io__tt_025C_3v30.lib`): pins PU `input`, PD `input`,
  PAD `input`, **Y `output`, function `((PAD))`** — Y is the buffered pad signal to
  the core. **LEF** agrees: PU/PD/PAD `DIRECTION INPUT USE SIGNAL`, Y `OUTPUT`.
- PDK **Verilog** `in_c`: `buf #1 (Y, PAD)` — Y follows PAD; PU/PD are analog pull
  controls, not modeled digitally there.
- PDK **CDL** `in_c`: PU/PD are ESD-diode-protected control-gate inputs feeding
  level-shift logic that drives a **~100 kΩ poly-resistor ladder pull** on PAD
  (R196–R211 through node n15).
- **Polarity — now CONFIRMED for in_c (2026-08-21), not just inferred.** The
  official PDK page **"4.1 Digital I/O Cell Control Pins"** gives the truth table
  for the digital I/O pads' pull control (in_c is a digital input pad) verbatim:

  | PU | PD | Resistive Pulling |
  |----|----|-------------------|
  | 0 | 0 | Normal CMOS (no pull) |
  | 0 | 1 | **Pull Down** |
  | 1 | 0 | Pull Up |
  | 1 | 1 | Normal CMOS (no pull) |

  So **PU/PD are active-high enables**: `PU=1,PD=0`→pull-up, `PU=0,PD=1`→pull-down,
  `PU=0,PD=0` (or `1,1`)→no pull. This **agrees with** last session's inference from
  the sibling `bi_t` Verilog (`rnmos(PAD,gnd,~OE&&~PU&&PD)` /
  `rnmos(PAD,pwr,~OE&&PU&&~PD)`) — that analogy is now backed by an in_c-applicable
  source, superseding the earlier "inferred by analogy, never confirmed" caveat.
  Source: <https://gf180mcu-pdk.readthedocs.io/en/latest/IPs/IO/gf180mcu_fd_io/digital.html>.

**Options for an externally-driven reference clock:**

| PU | PD | effect | consequence |
|----|----|--------|-------------|
| 0 | 0 | no pull (high-Z) | nothing loads/biases a driven clock; but a *disconnected* clock floats. |
| **0** | **1** | **weak pull-down (~100 kΩ) — DECISION** | REF_IN parks at a clean logic 0 when the bench clock is disconnected; ~100 kΩ is negligible against a 50 Ω generator when driven. |
| 1 | 0 | weak pull-up | idle high; uncommon for a clock. |
| float | — | **NOT acceptable** | CMOS control-gate inputs; floating → indeterminate pull, drift near threshold, crowbar current, noise pickup. Both **must** be driven. |

**DECISION (Greg, 2026-08-21 — overrides last session's PU=0/PD=0):** tie
**REF_IN_PU = 0 (→VSS) and REF_IN_PD = 1 (→VDD)** = **Pull Down**. Reasoning: on a
bench part the reference clock is often disconnected, and a floating CMOS receiver
input can oscillate and draw crowbar current; a pull-down instead gives a clean
logic 0 so the PFD sees *no reference* and the VCO parks at a band edge —
deterministic and diagnosable. The 100 kΩ pull is negligible against a 50 Ω
generator when the clock IS driven. Do **not** leave either floating. No
`chip_top.sch`/`info.yaml` edit this session — the pin list may change after Friday,
so the tie is recorded here to make the call once.

---

## 3. Variant recommendation: **BH**, with the counter-argument

**Recommendation: BH (1110 × 550, landscape).**

- **Aspect match.** chip_top is 522 × 309 — a *landscape* core. BH's die is
  landscape (1110 × 550); chip_top drops into the bottom-left with only ~241 µm of
  height headroom to the north pins. BV is *portrait* (550 × 1110): chip_top fills
  the bottom ~28 % and leaves ~800 µm of dead die above, across which the pins are
  stacked — every top/west pin becomes a long haul.
- **Critical I/Q outputs.** I_P/I_N/Q_P/Q_N (2.4–3.2 GHz differential, from DIV2 at
  chip lower-left) go to BH's **north edge ≈ 241 µm** up — short. In BV they land on
  the **west edge at y720–1065**, i.e. **~550–900 µm** of haul up a tall die: added
  delay, loss, differential mismatch and coupling on the deliverable RF signals —
  the worst place to compromise.
- **Source proximity.** BH puts CP_OUT and the I/Q outputs on the north edge near
  their sources (CP top-middle, DIV2 lower-left); the west pins (VSSA at the GND
  ring, VDDA at the band, IBIAS aligned with the top-left ibias block) are on the
  near-left edge. ISS/VTUNE (from vco on the right) haul left in either variant, but
  BH's shorter die keeps them ≤ ~240 µm of vertical.
- **Fit.** Both give 610500 µm² usable ≫ 161k; not a differentiator. BH also has
  large width headroom (1110 vs 522) vs BV's tight 28 µm width margin (522 vs 550).

**Strongest argument against BH (for BV):** BV carries a **fixed down-bonded quiet
ground `vss_fixed W12`** immediately adjacent to VSSA (W13) — a dedicated, low-
inductance quiet-ground bond that a phase-noise-sensitive LC-VCO benefits from. BH
has no fixed ground in A01's slot (ground = VSSA only). For a VCO, ground quality
feeds phase noise, so BV's W12 is a real advantage.

**Why BH still wins:** the on-chip GND ring + the VSSA bond already set the VCO
ground; VSSA can itself be down-bonded. The RF-output routing penalty in BV
(hundreds of µm on the differential I/Q) is a larger, more certain degradation of
the actual deliverable than the incremental ground-inductance gain of a second
fixed bond. And the Friday VSSD decision may add a dedicated ground regardless,
eroding BV's W12 edge. **Revisit after the regenerated DEF.**

---

## 3b. I/Q length matching & core placement (2026-08-21)

### The padframe REINTRODUCES the I/Q mismatch — a designed-in requirement
Phase 7 length-matched `VCO_OUTP/N` inside chip_top. The BH padframe undoes that at
the top level: the four divider outputs land at fixed north pads **I_P x145, I_N
x245, Q_P x345, Q_N x445 — 100 µm apart, a 300 µm x-spread** — while all four
originate from adjacent DIV2 converters (taps at x2.18 / x235.18). The Q hauls run
further and pass over the vco. **This is inherent to the pad pitch, not the pin
ordering, and BV is worse — so it is not an argument against BH.** It must be
designed in from the start of phase-8 routing (a matched-length quad router, §4),
**not** patched late as VCO_OUTP/N was.

### Output taps (Item 2a — the real net metal, tap-the-extent)
From `port_map.py` + measured M1 in `gds/chip_top.gds` (current chip frame). Each
output escapes to a DIV2 edge as a **0.60 × 0.60 µm M1** port pad:

| net | DIV2 tap (chip µm) | M1 pad extent |
|-----|--------------------|---------------|
| I_P | (235.18, 140.27) | (234.88,139.97)–(235.48,140.57) |
| I_N | (2.18, 140.27) | (1.88,139.97)–(2.48,140.57) |
| Q_P | (235.18, 51.92) | (234.88,51.62)–(235.48,52.22) |
| Q_N | (2.18, 51.92) | (1.88,51.62)–(2.48,52.22) |

I/Q at two x-extremes (I_P/Q_P right x235, I_N/Q_N left x2) and two y-levels (I
y140, Q y52). Because the pads increase left→right (I_P<I_N<Q_P<Q_N) while the taps
alternate right/left, **I_P↔I_N and Q_P↔Q_N cross** — a layer-managed crossing the
quad router must handle.

### Haul lengths & padding (Items 2b–2c)
Placement assumption: chip_top's core (boundary −25..497 × −21.5..287.5) placed in
the 1110×550 DIEAREA by an offset (dx,dy); tap_die = tap + (dx,dy). Fit ⇒ dx∈[25,613],
dy∈[21.5,262.5]. Manhattan haul tap→pad, per placement (µm):

| placement (dx,dy) | I_P | I_N | Q_P | Q_N | max | spread | matched(4×max) | total pad |
|-------------------|-----|-----|-----|-----|-----|--------|----------------|-----------|
| bottom-left (25, 21.5) | 480 | 628 | 583 | 916 | 916 | 436 | 3664 | 1670 |
| top-left (25, 262.5) | 239 | 387 | 342 | 675 | 675 | 436 | 2700 | 1057 |
| top dx200 (200, 262.5) | 414 | 212 | 302 | 500 | 500 | 288 | 2000 | 572 |
| **top dx243 (243, 262.5)** | 457 | 169 | 345 | 457 | **457** | 288 | **1828** | **400** |

Matching pads the three shorter hauls up to the longest, so the cost of matching is
**4 × (longest haul)** and the serpentine budget is `total pad`. Moving the core to
the **top** (dy 262.5, DIV2 nearest the north pads) roughly halves everything vs
bottom-left; shifting **right** (dx→243) balances the left/right crossing so the max
haul bottoms out at **457 µm** with only **400 µm** of total serpentine.

### Does the padding fit? (Item 2d)
Yes. At dx≈200–243 the 522-wide core leaves **~415–588 µm of empty die width**
(x0–175 west + x697–1110 east) plus the vertical clear columns — ample room for
horizontal serpentine meanders. The **y[180,205] power band** is crossed on M2/M3
(signals) vs M4/M5 (power) — not blocked. The serpentine stays inside the 20 µm GND
perimeter margin. The tight spot is the ≤~60 µm between the core top (y550 at
dy262.5) and the north pads; land the hauls in the core's clear columns and route
the matching meanders in the empty side regions, not that gap.

### Core placement recommendation (Item 3)
Evaluated at dy=262.5 (core at top — the I/Q, CP_OUT, VDDD, REF_IN all land north, so
minimizing their vertical haul dominates) across dx, plus a bottom baseline:

vco→pad columns use the vco's own taps (ISS (395.84,60.33), TUNE (358.68,66.70),
VDD (397.44,74.83)); GND→VSSA = the horizontal gap the perimeter GND ring must span
from the core's left edge (x = −25+dx) out to the west VSSA pad at x0.

| placement | I/Q spread | I/Q matched | total→14 pins | vco→ISS / VTUNE / VDDA | GND→VSSA |
|-----------|-----------:|------------:|--------------:|------------------------|----------|
| bottom-left (25,21.5) | 436 | 3664 | 6493 | 721 / 777 / 508 | 0 (core at x0) |
| top-left (25,262.5) | 436 | 2700 | **4972** | **480 / 536 / 577** | 0 (core at x0) |
| **top dx200 (200,262.5)** | **288** | 2000 | 5458 | 655 / 711 / 752 | ring extends 175 |
| top dx243 (243,262.5) | 288 | **1828** | 5630 | 698 / 754 / 795 | ring extends 218 |

**Recommendation: core at top, dx = 200, dy = 262.5 — boundary x[175, 697],
y[241, 550].** It gives the minimum I/Q spread (288 µm) and near-minimum matched
length (2000 µm) with only 572 µm of serpentine — the RF outputs are the deliverable
— while keeping the vco's DC/bias hauls (ISS 655, VTUNE 711 µm — both DC/high-Z,
haul-tolerant) and the power hauls (VDDA 585 µm, bus-distributed) acceptable. dx can
be pushed to 243 for the absolute-shortest matched I/Q (1828 µm, 400 µm serpentine)
at ~40 µm more vco DC haul.

**Strongest argument against it:** **top-left (dx=25)** has ~10 % lower total haul
(4972 vs 5458), the shortest vco→ISS/VTUNE (480 / 536 µm), and puts the whole core
hard against the west edge so the VDDA/VSSA pads sit right on the bus/ring — which
favors supply/ground integrity — for an LC-VCO, IR drop and ground bounce feed
phase noise. It loses only because VDDA/VSSA are wide bus/ring-distributed (low-R,
haul-tolerant) whereas the I/Q are thin RF signals where length directly costs
loss/mismatch — so the I/Q-optimal dx wins. If Friday's regenerated DEF moves the
pad map, re-run this sweep before committing a placement.

---

## 4. Phase-8 top-level expansion plan (plan only — nothing built)

### DIEAREA & pin rects → `chip_merge.py` frame
- **DBU already matches.** `chip_merge` sets `master.dbu = 0.005` (200/µm); the DEF
  is 200/µm. So DEF coordinates map **1:1** into chip_merge's frame — integration is
  a pure **translation** (where chip_top's core origin sits in the project frame),
  no scaling.
- chip_merge would (a) set the deliverable's extent to the DEF **DIEAREA**, (b)
  position the existing block-merge (DIV2/vco/ibias/CP/PFD, unchanged relative
  layout) at a chosen offset inside it (bottom-left for BH), and (c) the DEF
  `translated_user` rects become the fixed routing targets. The blocks' internal
  placement does not move; only the whole core is offset within the larger die.
- **`check_placement.py`** compares chip_top.mag's placement record against the
  chip_merge deliverable. Growing the die + offsetting the core changes chip_top's
  absolute frame, so check_placement **must be re-baselined** for phase 8 (the
  block-relative placements are unchanged; the guard's reference geometry is not).
  Treat a check_placement diff here as expected-once, then re-lock.

### The 0/0 boundary
- The current layer-0/0 boundary (522 × 309, at (−25,−21.5)–(497,287.5)) is
  chip_top's *standalone* die outline. Under the padframe the **DEF DIEAREA is the
  authoritative die extent**, so the 0/0 boundary is **replaced** — redrawn to the
  DIEAREA (BH: (0,0)–(1110,550)). The two do not coexist; a single boundary = the
  DIEAREA. The core geometry stays; it simply sits inside the larger outline.

### Long-haul routes
- The current **y[180,205] band** carries the M5 VDDD/VDDA buses full-width, and
  **GND is a 15 µm M5 ring in a 20 µm perimeter margin**. In BH the north pins sit
  ~241 µm **above** chip_top's top (y309); hauls run **up from each block tap,
  crossing the y[180,205] power band on a *different layer* (signals M2/M3, power
  M4/M5 — the silent-short discipline), then up the new die area** (y309→550) to the
  north pin rects. West pins route **left** to x0. Diff pairs (I/Q, VCO_OUT already
  matched internally) should be routed as matched-length pairs up to the north pads.
- Ground: extend the perimeter GND ring/margin out to the new DIEAREA and tie it to
  the **VSSA** pad (west); the VDDD digital island (north) still lacks a ground pad
  pending the VSSD decision — do not resolve here.

### The existing 12 die-edge port labels
- chip_top carries **12 top-level port labels** today (VDDA, VDDD, VSSA + the 9
  signal ports), scattered at block-tap locations near its own perimeter — *not* at
  one edge. (The prompt's "11" excludes the VSSA ground-ring label at y−2.0; the
  route_chip print "13 labels" is stale — reconcile to **12**, matching the 12 LVS
  ports.)
- Under the padframe these labels **move to the DEF pin rectangles** at the DIEAREA
  edges (a top-level label must land on top-level metal, so each haul carries its
  net's metal to the pin rect and the label sits there). **Two new labels are
  added** — REF_IN splits into REF_IN / REF_IN_PU / REF_IN_PD (12 → 14), with PU/PD
  tied per §2. A VSSD (if Friday adds it) would add one more. So: existing labels
  relocate; +2 (REF_IN PU/PD) new; possibly +1 (VSSD).

### Work estimate (rungs)
1. **Decide inputs** — variant (BH, pending Friday), final pin list (post-VSSD),
   REF_IN PU/PD tie (§2). *(gated on Friday)*
2. **Frame** — chip_merge: set DIEAREA, offset the core, replace the 0/0 boundary;
   re-baseline check_placement.
3. **Haul routing — west pins** — VSSA/VDDA/IBIAS/ISS/VTUNE to the west edge (band
   crossings on diff layers).
4. **Haul routing — north pins** — CP_OUT + matched I/Q pairs + VDDD + REF_IN up to
   the north edge (the RF-critical rung; matched-length diff pairs).
5. **Ground/PU-PD** — extend GND ring to the DIEAREA + VSSA tie; REF_IN_PU/PD
   tie-offs; VSSD if required.
6. **Labels** — relocate the 12 labels to the pin rects, add REF_IN PU/PD (+VSSD).
7. **Verify** — magic DRC + KLayout signoff (W4 waiver), chip LVS vs the padframe
   netlist (`padring.v`), check_placement re-lock, 5-block regression.

Roughly **6–8 rungs** — a phase comparable in effort to phase-7 routing, dominated
by rung 4 (RF haul routing) and rung 7 (padframe-level LVS). Several are gated on
Friday's VSSD/pin-list decision.

---

## 5. Regression baseline (re-run 2026-08-21)

`verify_cp` re-run, all exit 0 (unchanged — this session added only route_lib
primitives + docs + file moves, no geometry/flow change):

| cell | DRC | LVS |
|------|-----|-----|
| chip_top | 0 | match uniquely |
| PFD_lib | 0 | match uniquely |
| CP_v1 | 0 | match uniquely |
| ibias_gen_v1 | 0 | match uniquely |
| DIV2_QUAD_v1 | 0 | match uniquely |
| vco_v1 | 0 | match uniquely |

Known-good — the next session starts from here.

---

## 6. Housekeeping (2026-08-21)

Off-flow analysis/diagnostic scripts were moved out of `team_src/magic/` into
**`team_src/magic/analysis/`** (with a README) so nobody mistakes them for flow
scripts — they are NOT run by the tapeout flow:
- the **bailey_* LVS-flow reproduction** (evidence for the flat-GDS gencell finding,
  `docs/gf180-flat-gds-gencell-lvs.md`) — kept, not deleted;
- this session's **DEF/haul/placement parsers** (`parse_def.py`, `iq_haul.py`,
  `core_placement.py`) that produced §1–§3b.

**Phase-8 haul primitives** were added to `route_lib.py` (length-matched quad
router, def-pin lander, per-net length accounting) with a committed self-test —
built and DRC-gated in isolation, **not** wired into `chip_merge.py`/`route_chip.py`.
See `route_selftest` for the gate results.
