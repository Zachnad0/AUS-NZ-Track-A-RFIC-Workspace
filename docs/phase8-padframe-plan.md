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

### 1e. REGENERATED DEF package received 2026-08-22 (`A01.def (1).tgz`) — supersedes §1a–1d where they differ

Greg supplied a **newer** package than the one §1 was written from. Extracted to the
session scratchpad (analysis only, still not committed). What changed and what is now exact:

- **§1d's stale-60×24 flag is RESOLVED.** `A01_selected_variants.json` and the interface
  yamls now carry `source_gds .../gds/A01/chip_top.gds`, `top_cell: chip_top`,
  `rectangle_dbu [-5000, -4300, 99400, 57500]` → **522 × 309 µm**. The generator is sized
  from the real block. No action left on that flag.
- **BH DIEAREA is exact:** `DIEAREA ( 0 0 ) ( 222000 110000 ) ;` at `UNITS DISTANCE MICRONS 200`
  → **1110.000 × 550.000 µm**. `usable_area: 610500`, `origin_microns: [350, 2035]`,
  **`vss_fixed: []`**, `blockages: []`, `routing_blockage_layers: Metal1…Metal5`.
- **§1's pin table gave BOUNDING BOXES. The real pin rects are multi-finger** — this is a
  routing fact, not a formatting detail. A haul must land on a finger, not on the bbox.

| pin | slot | cell | fingers | finger w × h (µm) | bbox `translated_user` (µm) |
|-----|------|------|--------:|-------------------|------------------------------|
| VSSA | W18 | dvss | 6 | 1.000 × 9.500 | x0.00–1.00 y46.36–118.64 |
| VDDA | W19 | dvdd | 6 | 1.000 × 9.500 | x0.00–1.00 y146.36–218.64 |
| IBIAS | W20 | asig_5p0 | 8 | 1.000 × 2.540 | x0.00–1.00 y260.34–304.66 |
| ISS | W21 | asig_5p0 | 8 | 1.000 × 2.540 | x0.00–1.00 y360.34–404.66 |
| VTUNE | W22 | asig_5p0 | 8 | 1.000 × 2.540 | x0.00–1.00 y460.34–504.66 |
| CP_OUT | N01 | asig_5p0 | 8 | 2.540 × 1.000 | x45.34–89.66 y549.00–550.00 |
| I_P | N02 | asig_5p0 | 8 | 2.540 × 1.000 | x145.34–189.66 y549.00–550.00 |
| I_N | N03 | asig_5p0 | 8 | 2.540 × 1.000 | x245.34–289.66 y549.00–550.00 |
| Q_P | N04 | asig_5p0 | 8 | 2.540 × 1.000 | x345.34–389.66 y549.00–550.00 |
| Q_N | N05 | asig_5p0 | 8 | 2.540 × 1.000 | x445.34–489.66 y549.00–550.00 |
| VDDD | N06 | dvdd | 6 | 9.500 × 1.000 | x531.36–603.64 y549.00–550.00 |
| REF_IN (Y) | N07 | in_c | 1 | 0.380 × 1.000 | x633.76–634.14 y549.00–550.00 |
| REF_IN_PD | N07 | in_c | 1 | 0.380 × 1.000 | x694.29–694.67 y549.00–550.00 |
| REF_IN_PU | N07 | in_c | 1 | 0.380 × 1.000 | x698.65–699.03 y549.00–550.00 |

  All rects are **Metal2**, and each is only **1 µm deep** into the project (west pins
  x[0,1]; north pins y[549,550]). The north slot pitch is **100 µm**; N01–N05 centres are
  **67.5 / 167.5 / 267.5 / 367.5 / 467.5**, which is exactly what `phase8_incontext.py`
  already targets. REF_IN's three fingers are **0.38 µm** wide — the narrowest landing in
  the design.
- **The padring `.cfg` fixes the slot CELL TYPES, and A01_BH owns 16 slots: W18–W22 +
  N01–N11** (`user_slot_count: 16`; the 12-pin issue populates W18–W22 + N01–N07 only).
  The generator assigns pins to slots **in info.yaml order** and derives each slot's cell
  from `io_type` — W18 `dvss`←VSSA(ground), W19 `dvdd`←VDDA(power), N06 `dvdd`←VDDD,
  N07 `in_c`←REF_IN. The two BREAKs in `A01_BH_padring.cfg` sit **immediately before N06
  and immediately after N07**, which is the digital island §1c described.

**VSSD lands cleanly, and it does NOT move the RF work (2026-08-22).** Inserting VSSD at
pin index 10 (immediately before VDDD) makes it **N06 `dvss`** and pushes VDDD→N07,
REF_IN→N08 — still inside A01's 16-slot allocation, 3 spare. Two consequences:
- **N01–N05 do not move.** CP_OUT and the four I/Q pads keep x67.5/167.5/267.5/367.5/467.5
  at y549–550, so the matched-quad geometry, the escapes, the lane assignment and the
  provisional 433.76 µm are **unaffected by VSSD**. Only the VDDD and REF_IN hauls shift
  **+100 µm east** (VDDD centre 567.5 → 667.5; REF_IN Y 633.76 → ~733.8).
- **Why immediately-before-VDDD is the right slot:** Bailey's audit flags
  `A01: group 2 missing ground: VDDD REF_IN` but does *not* flag group 1, and group 1's
  ground (VSSA) is its **first** pin. VSSD placed first in group 2 reproduces exactly the
  arrangement the audit already accepts.

**Still to confirm against a regenerated DEF** (do not treat as settled): that the
generator emits the BREAK *before* VSSD rather than between VSSD and VDDD, and that it
emits `in_c` at N08. Both follow from the observed ordering rule, neither is proven.

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

## 3c. Ground-return quantification (2026-08-21, Item 1)

The dx=200 pick was made on I/Q spread alone; here is the ground side, measured.

**Ring, measured (not assumed):** the GND ring is a **15 µm-wide M5 (layer 81)**
loop around the core (four segments, each 15 µm thick — queried from `chip_top.gds`).
Under BH the ring must span the gap from the core's west edge (x = −25+dx) to the
VSSA pad at x0; that spur carries the chip's entire ~26 mA to its single ground pad:

| dx | spur length | squares (÷15 µm) | R (M5 40 mΩ/□) | IR @26 mA | L (~1 pH/µm)† | XL @5 GHz |
|----|-------------|------------------|-----------------|-----------|---------------|-----------|
| 25 | 0 | 0 | 0 | 0 mV | 0 | 0 |
| 200 | 175 µm | 11.7 | 0.47 Ω | **12.1 mV** | 175 pH | 5.5 Ω |
| 243 | 218 µm | 14.5 | 0.58 Ω | 15.1 mV | 218 pH | 6.9 Ω |

- **M5 sheet resistance 40 mΩ/□** (typ; 31 / 49 in the fast/slow corners) — source
  `/foss/pdks/gf180mcuD/libs.tech/magic/gf180mcuD.tech`, `resist (allm5)/metal5`.
- †**Inductance is a rule of thumb** (~1 pH/µm ≈ 1 nH/mm partial self-inductance of an
  on-chip/package wire) — stated as such, not extracted.

**What it means for the VCO (Item 1d).** The tail current (~1 mA) returns through
**ISS**, not GND, so the VCO's own GND current is small (bulk/well leakage +
displacement); the 12 mV is essentially a **common-mode** shift of the shared on-chip
ground, which the differential tank (472–568 mV) rejects to first order. As a DC bias
shift on the varactor reference it moves the frequency ~10 MHz (0.2 %), retunable via
VTUNE. The 175 pH / 5.5 Ω of added return reactance is **common-mode** and, crucially,
is dwarfed by the unavoidable **VSSA bond-wire inductance** (~1 nH → ~31 Ω @5 GHz — the
on-chip spur is <20 % of it).

**Verdict (Item 1e): the ground penalty at dx=200 does NOT change the placement.**
12 mV DC IR and 175 pH are small absolutely, common-mode to the differential VCO, and
a minor fraction of the bond inductance. If even 12 mV is unwanted, widening the west
ground spur to ~30 µm (or stacking M4+M5) halves it to ~6 mV — trivial. **dx=200
stands.** The honest, boring conclusion: ground does not materially decide this.

## 3d. Pad ordering — a better assignment exists (Item 2)

info.yaml's pin ORDER sets which output lands on which north slot (x145/245/345/445),
and it is ours to choose. Sweeping all 24 orderings at dx=200/dy=262.5 (taps: I_N/Q_N
left x2.18, I_P/Q_P right x235.18):

| order @ x145,245,345,445 | I/Q spread | matched (4×max) | total | crossings |
|--------------------------|-----------:|----------------:|------:|-----------|
| I_P,I_N,Q_P,Q_N (current) | 288 | 2000 | 1428 | 3 |
| **Q_N,I_N,I_P,Q_P (proposed)** | **58** | **1077** | **962** | **0** |
| Q_N,I_P,I_N,Q_P | 47 | 1256 | 1162 | 1 |
| I_P,Q_P,Q_N,I_N | 14 (min) | 1656 | 1628 | 4 |

**Proposed reorder: Q_N, I_N, I_P, Q_P** (left-taps → left-pads). It nearly **halves
the matched wire (2000 → 1077 µm)**, cuts spread 288 → 58, and **removes all three
crossings** — the left/right tap order now matches the pad order. Rail-break rule
holds: all four stay in the analog north slots between CP_OUT and VDDD. **Cost
(Item 2b):** it splits the differential Q pair to opposite ends (Q_N x145, Q_P x445),
but these are **single-ended monitor outputs** (each buffered into its own 1 kΩ→50 Ω
instrument), measured individually — so adjacency is an organizational nicety, not an
electrical cost, and length-matching (which the reorder improves) is what preserves
quadrature accuracy. The min-spread ordering (I_P,Q_P,Q_N,I_N, spread 14) is rejected:
it needs ~1656 µm of matched wire (more loss) and 4 crossings.

**PROPOSED info.yaml change (record for after Friday — NOT edited): reorder the four
outputs to Q_N, I_N, I_P, Q_P across the north analog slots.** Re-confirm against the
regenerated DEF's slot map first.

## 3e. RF loading the outputs will actually see (Item 3)

Length-matching gives each output on-chip wire that no sim included. Added
capacitance, using the VCO-load figure **0.08 fF/µm for a 0.4 µm wire** (assumed
**M3**, the signal haul layer):
- current ordering, ~500 µm matched → **40 fF/output**;
- **proposed reorder, ~269 µm matched → ~21.5 fF/output.**

Effect on the recorded **157 mVpp** monitor (1 kΩ R_SER into 50 Ω, 300 fF pad C): the
added C shunts the pad node, but 50 Ω dominates the load there, so at 3 GHz
(VCO ÷2 upper band) |Z_load| falls only 48.1 → 47.6 Ω with +40 fF — a **~1 % amplitude
drop (157 → ~155 mVpp)**; with the reorder's +21.5 fF it is **~0.6 %** (~156 mVpp).
**The outputs remain usable** for divide-ratio (amplitude essentially unchanged) and
quadrature accuracy (the matched length holds the I-to-Q skew). **Characterized
limitation:** on-chip routing adds ~40 fF (~21.5 fF reordered) per output, ~1 %
(~0.6 %) monitor-amplitude loss at 3 GHz — negligible, recorded here alongside the
existing VCO load-pull, I/Q offset, and DIV2 EM items.

---

## 3f. Channel map + dy sweep → recommended placement dx=200, **dy=200** (2026-08-21)

Built the per-layer occupancy map (`docs/phase8-channel-map.md`,
`analysis/channel_map.py`) and swept dy against it (`analysis/dy_sweep.py`,
`analysis/phase8_dryrun.py`).

**dy sweep** (dx=200, proposed order; matched haul vs the clear channel above the core,
DIEAREA y[287.5+dy, 549]):

| dy | matched | per-output | clear channel | lanes+serpentine fit? |
|----|--------:|-----------:|--------------:|-----------------------|
| 262.5 | 1077 | 269 | −2 µm | **NO** (last-session problem: core reaches the pad row) |
| 240 | 1167 | 292 | 20 µm | NO |
| 220 | 1247 | 312 | 40 µm | tight |
| **200** | **1327** | **332** | **60 µm** | **yes** |
| 180 | 1407 | 352 | 80 µm | yes (comfortable) |
| 160 | 1487 | 372 | 100 µm | yes |

**Recommended: dy = 200** — the highest dy (shortest haul, matched 1327 µm =
332 µm/output) that still opens a ≥60 µm clear channel above the core for the four
horizontal lanes + the 58 µm serpentine + pad landing. **Cost vs dy=262.5:**
+250 µm total, +63 µm/output (269→332 µm). **Conflict flag (Item 2b):** dy ≥ ~215
forces the lanes over the top blocks (M3-on-M3 silent shorts) — avoid. **Strongest
argument against dy=200:** its 60 µm channel is *marginal* — if the 4-lane + serpentine
stack does not fit, drop to **dy=180** (+80 µm total haul, +20 µm channel headroom).

**Dry-run at dy=200 (Item 3, `analysis/phase8_dryrun.py`, throwaway cell):**
- length matching **EXACT** — all four to **331.760 µm** (<1e-3 µm); **magic DRC 0**,
  **KLayout signoff PASS**; the four routes extract as separate nets (own lanes → no
  merges, DRC-0 spacing confirms no touching).
- lanes land at **y≈490 in the clear channel** (y[487.5,549]) — clear, as designed.
- overlap check of the route's straight M3 risers vs the block metal (DIEAREA frame):
  benign M3-over-**M2** crossings of ibias/CP/DIV2 (different layer, no short), but
  **real M3-on-M3 conflicts:** the **right risers (I_P/Q_P at x235) cross CP.M3 and
  PFD.M3**, and the tap escape crosses DIV2.M3. **Resolution (per the map):** the
  right risers must **jog to the x288–397 clear column** before rising, and the taps
  escape on their own layer/axis (phase-7 technique). The left risers (Q_N/I_N at
  x2.18) are already left of ibias's M3 — clear.
- **Verdict:** phase 8 at dy=200 is a **routing job** — the lane channel is clear and
  the primitives match exactly; the remaining work is the DIV2-output riser escapes
  via the mapped clear columns. It converges; it is not a floorplan wall.

## 3g. The other ten pins at dx=200/dy=200 (Item 4)

| pad | source | edge | haul (µm) | path |
|-----|--------|------|----------:|------|
| VSSA | GND ring | west | ~175 (spur) | ring extends to the west edge — clear, low-R |
| VDDA | VDDA bus | west | ~175–260 (bus) | bus extends west — clear (the 522 point-figure overstates it) |
| IBIAS | ibias.IBIAS | west | 412 | exits ibias west into the empty region — clear |
| **ISS** | vco.ISS | west | **717** | **LONG** — vco(right)→west pad, full-die crossing; DC/high-Z, clear band at y≈378 |
| **VTUNE** | vco.TUNE | west | **774** | **LONG** — same; DC tune, clear band at y≈480 |
| CP_OUT | CP.CP_OUT | north | 538 | up-and-left; low-freq analog |
| VDDD | PFD.VDD | north | 230 | up-and-right — clear |
| REF_IN | PFD.REF | north | 348 | up-and-right — clear |
| REF_IN_PU | tie→VSS | north | short | tie to the ground ring (pull-down, §2) |
| REF_IN_PD | tie→VDD | north | short | tie to the VDDD bus (pull-down, §2) |

**Flags (Item 4b):** every pin has a clear path; **ISS (717) and VTUNE (774) are the
materially-long ones** — the vco sits on the right and both pads are on the west edge,
so they cross the full die. Both are **DC/high-Z** (tail node, tune voltage), so the
length costs only resistance (negligible), and the clear M2/M3 bands at y≈378 / y≈480
provide the crossing lane. No pin is unroutable.

**VSSD implication (Item 4c, analysis only — do NOT add):** VDDD and REF_IN sit in the
north **digital island** (x531–699). A VSSD pad, if Friday requires one, would land in
that island (north, near VDDD x531) and draw its ground from the **digital VSS taps**
— PFD.VSS (die ≈x433,y457) or DIV2.VSS (die ≈x353,y279) — a moderate up-and-right haul
like VDDD. It would NOT come from the analog VSSA ring; keeping the digital return
local to that island is the point of the padring's VDDD/REF_IN break.

---

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

### Matched-quad dry-run at real coordinates (2026-08-21, Item 4)

Rehearsed `route_lib.matched_route` on the four real taps, the four BH pad rects, the
chosen placement (dx=200/dy=262.5), and the **proposed** ordering (§3d), in a
throwaway cell (`team_src/magic/analysis/phase8_dryrun.py`):
- **Length matching EXACT** — all four routed to **269.260 µm** (err < 1e-3 µm).
- **magic DRC 0; KLayout signoff PASS (0 violations)** on the throwaway cell.
- Route bbox (167,314)–(468,549) µm **overlaps** both the y[180,205] power band
  (DIEAREA y421.5–446.5) and the top blocks ibias/CP/PFD (DIEAREA y466.5–534.5).

**Verdict: phase 8 is a ROUTING job, not a floorplan-impossible one — with one
placement caveat.** The primitives produce exact, DRC-clean matched routes; the
proposed reorder makes the hauls **mostly vertical risers** (taps ≈ under their pads)
with only ~58 µm of serpentine. The band overlap is benign — the M3 signal hauls cross
the M5 band on a **different layer** (no short, the phase-7 discipline). The real
constraint is that the risers must thread **clear columns** between the top blocks
(as phase 7 did), and at **dy=262.5 the core is packed to the north edge**, leaving no
clear horizontal channel — the lanes/serpentine land over the top blocks. **Refinement:
lower the core (~dy 160–180) to open an ~80–110 µm clear channel above it** for the
horizontal lanes + serpentine + pad landing, at the cost of ~80–110 µm of extra
(still-matched) haul each. So the placement is a joint optimum of I/Q haul length **and**
haul-channel room, not haul length alone — settle the exact dy against the regenerated
DEF and the confirmed clear-column map next session.

---

## 3h. In-context rehearsal + VTUNE shielding (2026-08-21, 4th session)

### The isolated dry run proved less than it looked (Item 1)
Rebuilt the rehearsal WITH the five blocks present — `chip_top` instanced at
dx=200/dy=200 in a throwaway cell (`analysis/phase8_incontext.py`; all masters present,
confirmed by the 84 varactor-PL.5a baseline). Two corrections to last session:
- **The 331.760 µm match was the CONFLICTING route.** Jogging the right risers into the
  clear x381–404 (ibias↔CP) gap lengthens them, so the true matched length after the
  jog is **~458 µm** (Q_P is the longest; the shorter three pad up to it).
- **The matched quad does NOT drop in DRC-clean in context.** `reh_base` (blocks only) =
  84 (varactor); `reh_phase8` (with routes) = 86 — the routes add **M3.2a**:
  - **Left risers (Q_N/I_N)** are squeezed between the **GND ring** (die x197.5) and DIV2
    (die x200) — a ~2.5 µm slot; a riser there collides (M3.2a) with the ring-area M3.
  - **Matching serpentine** (~130–166 µm, from the routing spread) does **not** fit the
    channel — M3.2a at both dy=200 (60 µm) AND dy=180 (80 µm).
  - Right risers (I_P/Q_P) escape east into the DIV2↔vco gap, rise to the vco-top/CP-
    bottom window (crossing the M5 band on M3 — benign), jog into the x381–404 gap, and
    rise past CP — that base geometry is workable.
- Extraction: the 0.28 µm M3.2a are near-shorts (spacing), not overlaps, so **no merges**.
- **Verdict:** phase 8 converges but is a **hand-tuned routing job, not a drop-in
  primitive**. The left risers need the ring pulled off DIV2 (a few µm more dx margin, or
  a ring notch) to open their slot; the matching serpentine must go in the **wide empty
  side regions** (x0–175 west, x697–1110 east; 588 µm) — **not** the 60–80 µm channel.
  The primitives length-match exactly; the escape/serpentine PLACEMENT is the build work.

### dy=180 does not rescue the serpentine (Item 3)
The serpentine budget is set by the routing spread (~130–166 µm), not by dy. It needs
~12 µm-tall fingers × 4 stacked lanes → more than either 60 µm (dy200) or 80 µm (dy180)
holds (M3.2a at both). **So the channel holds the four lanes + pad landing only; the
matching serpentine relocates to the side regions regardless of dy.** dy=200 therefore
stands for the lanes; dy is not the serpentine lever — the side regions are.

### VTUNE / ISS coupling: a quantified nothing (Item 2)
- **KVCO = 822 MHz/V** (band 4.13–6.35 GHz over VTUNE 0.3–3.0 V, on record).
- **Coupling caps (magic tech):** M2–M2 sidewall **0.047 fF/µm** (parallel, min spacing);
  crossover (different layers) ~0.005 fF each.
- **The 15 kΩ tune resistor** (golden `XR2 TUNE cap_bias 15kΩ`) sits between the 774 µm
  routing and the varactor and **low-passes the routing coupling**.
- **Concrete worst case:** a 50 µm inadvertent parallel run with a 0.5 V, 2.5 GHz
  aggressor → Cc ≈ 2.35 fF → ~18 mV on the routing node → filtered by the 15 kΩ +
  varactor to **~0.37 mV at the varactor → 0.3 MHz FM → ≈ −84 dBc** spur at 2.5 GHz
  offset. The natural geometry (VTUNE runs west, the I/Q outputs and CML clocks run
  north — perpendicular crossovers, ~0.005 fF) gives **< 0.1 mV → negligible**.
- **Mitigations & cost:** grounded guard trace ± (~1550 µm² over 774 µm, ~10× reduction);
  ground plane under (~465 µm² + ties); reroute perpendicular / avoid parallel runs
  (0 area); accept.
- **Recommendation:** **routing discipline** — keep VTUNE (and ISS) perpendicular to the
  switching aggressors and off parallel runs; the 15 kΩ tune resistor already shields the
  routing. No dedicated guard/plane needed (≈ −84 dBc worst-case, negligible in practice).
  ISS is milder still (low-impedance tail node, AM-to-PM). A quantified nothing.

### Fourteen-net crossing table (Item 4, from the occupancy map, dx200/dy200)

| net | layer | crosses | same/inter | resolution |
|-----|-------|---------|------------|------------|
| Q_N, I_N | M3 riser | GND ring M3 region (die x182.5–197.5) | **same** | thread the 2.5 µm ring↔DIV2 slot; widen it with a few µm dx or a ring notch |
| I_P, Q_P | M3 riser | CP.M3 + PFD.M3 at x235 | **same** | jog into the x381–404 ibias↔CP gap (validated in the rehearsal) |
| I_P, Q_P | M3 riser | M5 power band (y182–200) | inter | benign (M3 over M5) |
| ISS, VTUNE | M2/M3 | the 4 north I/Q risers | inter | keep perpendicular (they run N, VTUNE runs W) |
| ISS, VTUNE | M2/M3 | M5 power band | inter | benign |
| VSSA | M5 | — (perimeter ring spur) | — | clear, ~175 µm west spur |
| VDDA | M5 bus | signal risers | inter | benign (M5 over M2/M3) |
| VDDD | M4/M5 | signal risers | inter | benign |
| IBIAS | M2 | own-block escape then clear west region | — | minor |
| CP_OUT | M2/M3 | ibias body (if routed over it) | **same** if over ibias | route via the x181–204 clear column / top band |
| REF_IN | M2/M3 | digital-island region (north) | minor | local, north |
| REF_IN_PU/PD | M2 | — (short rail ties: PU→ring, PD→VDDD) | — | trivial |

The **only same-layer (real) conflicts** are the four I/Q risers (resolved: right→gap,
left→ring slot) and CP_OUT-over-ibias (resolved via the clear column). Everything else is
inter-layer (power on M4/M5 over signals on M2/M3) or perimeter — benign.

---

## 3i. Ring characterized, quad closes to a clean gate (2026-08-21, 5th session)

The 4th-session §3h "2.5 µm slot / M3.2a against the ring" conclusion was **wrong about the
mechanism** and is superseded here. Characterizing the ring layer stack and running the
actual gate (not inferring it) both changed the answer.

### The GND ring is M5-only — the "2.5 µm slot" is an artifact (Item 1)
Queried every layer in the ring's left segment and at the M3.2a corner
(`analysis/ring_corridor.py`, chip coords):
- **At the ring corner (chip x[−12,2], y[262,285]): only M5 (layer 81) + the 0/0 boundary.**
  No M1/M2/M3/M4, no vias. The ring is a plain 15 µm M5 loop (chip x −17.5…−2.5).
- **West of DIV2 (chip x<0) is empty on M1–M4** except that M5 ring. DIV2's edge M1 frame
  starts at chip x0.18; its only M2/M3 is a single via stack **at** the tap (chip y≈49),
  none west of it.
- Therefore a riser on M1/M2/M3 sits freely anywhere west of DIV2's M1 (>0.28 µm clear) out
  over the M5 ring — **M3-vs-M5 has no spacing rule.** The left riser was never boxed into a
  2.5 µm slot; it was **escaping on M1 hard against DIV2's M1 frame** (the real M1.2a).

### What the rehearsal actually violated, and the fix (Item 1b)
With the map-derived escapes, `reh_phase8` = 87 (84 baseline **+3**), all route-vs-route,
**none against the ring**:
- **M1.2a** at die (200.2, 252): the Q_N tap-escape M1 pad abutting DIV2's M1 frame. →
  **Fix:** via M1→M3 **at the tap pin** and escape on **M3** (past the frame; no M1 painted
  near it). `PLAN[*]["escl"]=3` for the two left nets.
- **M3.2a** at die (388, 508): my own I_P lane crossing my own Q_P riser at the right jog. →
  **Fix:** reorder the two jogs — I_P low-jog + west column (x385, lane 508), Q_P high-jog +
  east column (x400, lane 516) — so no lane crosses a riser.

### The extraction earned its keep — a DRC-clean silent short (Item 2c)
"M3.2a is a spacing rule, so no merge" was **sound reasoning and still wrong** — so we ran
the diff. Extracting the **routes-only** cell (`reh_routes.gds` = the top-cell shapes = the
4 hauls, no instance; `analysis/reh_extract.tcl`) first gave **3 nodes**, ports
`Q_N I_P Q_P` — **I_N had merged into Q_N.** The two left escapes *overlapped* (0 gap →
no M3.2a spacing violation, same layer → no width violation) where I_N's higher-y escape
swept west across Q_N's riser. **Fix:** order the left risers **west-to-east** (Q_N riser
west of I_N's) so neither escape crosses the other's riser.

### The clean gate (all four parts, dx=200/dy=200)
| gate part | reh_base (blocks only) | reh_phase8 (+4 hauls) | verdict |
|-----------|------------------------|-----------------------|---------|
| magic DRC total (`reh_drc.tcl`) | 84 (all PL.5a in vco_varactors) | **84** | **0 added** |
| KLayout signoff variant-D (`klayout_signoff.py`) | PASS, 168 waived (84 PL.5a_LV+84 PL.5b_LV) | PASS, **168** waived | identical |
| extraction node count, routes-only | 0 | **4** | diff = +4 nets |
| distinct nets (`.subckt` ports) | — | `Q_N I_N I_P Q_P` | **4 distinct** |

The quad **closes to a clean gate in context.** The escape/jog placement is the build work;
the length-matching primitive is exact (all four = **433.76 µm**, error 0.0000).

### Extending to the other hauls — where the rehearsal stops (Item 3)
Order attempted: VTUNE, ISS, IBIAS, CP_OUT, VDDD, REF_IN(+PU/PD), VSSA, VDDA. **It stops
at the first one, VTUNE — and the reason is structural, not a routing tweak.**

**Why the IQ quad closed and these do not:** the four IQ taps sit at block *edges* — Q_N/I_N
at chip x2.18 are west of ibias's M3 (x14.8), so they escape west on M3 into open die; I_P/Q_P
jog out of CP into the validated x381–404 gap. The remaining hauls originate **inside** their
blocks. Measured escapes (`analysis/vco_tap_escape.py`, `tap_layers.py`, chip coords):
- **VTUNE** tap chip(358.68,66.70), M1: **enclosed by the vco inductor** — M5 spiral fills
  y90–186 above it, vco M3 reaches up to y≈89 and the OUT-lead M5 to x472; the tap x is
  inside vco M3 (x358.5–419.8). Any riser at the tap crosses live vco M5/M3, and a westward
  exit at the tap's low y (66.7) crosses DIV2 M3 (x2–235.4) — there is **no clear band at
  y≈66**; the clear bands are all at y174–287.5, above the block bodies. A coupling-safe
  VTUNE (KVCO 822 MHz/V, §3h) must *not* rise through the inductor at all.
- **ISS** tap chip(395.84,60.33): same inductor enclosure (M5 y92–196).
- **IBIAS** chip(71.30,223.90) and **VDDA** chip(74.16,231.60): inside the ibias body;
  a drop on M3 at the tap x crosses ibias M3 (x14.8–177.8).

**The escape from a block-interior tap needs the block's port/net context** — to tell a
same-net touch (safe: it *is* the TUNE/ISS/IBIAS net) from a cross-net short. The generic
rehearsal router does not encode that. §3g already showed each of these has a clear *path*
once escaped (open west/north die); turning the escape itself into DRC-clean, short-free
geometry is **per-block build work**, not a sandbox primitive.

**A second, independent limit:** the rehearsal's verification is a **routes-only** extraction
(the 4 hauls with no chip_top instance). That proves the *routes* don't merge each other, but
it **cannot** catch a haul shorting to a *block* net — and same-layer overlap is invisible to
DRC (only spacing/width fire). Catching tap-to-block distinctness needs the **full LVS-abstract
flow** (the Bailey LEF-abstract extraction, `analysis/bailey_pass2_extract.tcl`), because a
flat full-cell extraction shorts the inductor's OUT_p/OUT_n. So the honest gate for the
single-net hauls is LVS-in-context, not the routes-only rehearsal.

**Verdict (Item 3d — do not force it):** the rehearsal closes the hard, matched, RF-critical
IQ quad with a real four-part gate. The remaining eight single-net hauls are each a
block-edge-escape problem that belongs in the real build (with block ports + LVS-in-context),
and §3g establishes their paths are clear. The rehearsal has done its job — it de-risked the
one case that genuinely needed geometry (the quad) and *measured* exactly what the others need.

## 3k. What survives a pin-list change, and what must be redone (Item 4)

Two things are still BLOCKED upstream (not this session's to decide): whether **VSSD** is
required, and the **final pin list / order**. This records which phase-8 results survive a
pin-list change and which must be regenerated.

| result | survives a pin-list change? | why |
|--------|:--:|-----|
| **Core placement dx=200 / dy=200** | **SURVIVES** | set by block-to-die-edge clearance + the ground-return budget (§3c) + the clear-column geometry (§3f), none of which depends on which signal lands on which pad. A VSSD pad lands in the north digital island (§3g) without moving the core. |
| **BH variant choice (1110×550)** | **SURVIVES** | driven by usable area + padring breaks (§1, §3), pin-list-independent. |
| **Ground-return quantification (§3c)** | **SURVIVES** | M5 ring/spur R is a function of placement, not pinout. |
| **RF output loading (§3e, ~40 fF/1%)** | **SURVIVES** | a property of the pad+ESD+haul length for an I/Q output; survives as long as I/Q stay on N-edge pads at similar haul length. |
| **VTUNE/ISS coupling analysis (§3h)** | **SURVIVES** | depends on KVCO, the 15 kΩ tune R, and perpendicular routing discipline — not on pin assignment. Re-check only if VTUNE/ISS move to an edge that forces a parallel run past the aggressors. |
| **The routing primitives (`route_lib.py`)** | **SURVIVES** | parameterized (endpoints in, length-matched path out); pin-list-independent by construction. |
| **The escape *technique* per tap** (M3-at-pin for the DIV2 outputs; jog-into-gap for CP; the west-to-east left-riser ordering) | **SURVIVES** | a property of each *block tap's* local layer stack, which does not change when the pad it targets changes. |
| **Matched length 433.76 µm** | **REDO** | it is `max(base)` over the four IQ nets for *this* pad assignment (Q_N→x167.5 … Q_P→x467.5) at dx200/dy200. Reorder the pads (e.g. the proposed Q_N,I_N,I_P,Q_P north order, §3d) and the per-net base lengths — hence the target — change. The *method* survives; the *number* is provisional. History: 269→332→458→433.76. |
| **Per-net escape *coordinates* / lane assignment** | **REDO** | which lane (490/500/508/516) and which pad-x each net targets is pin-list-specific. |
| **The channel/crossing budget (§3h table)** | **PARTIAL** | the clear columns/bands (§3f, from the blocks) survive; which net occupies which is redone. |
| **Pad reorder proposal (§3d)** | **REDO/CONFIRM** | it *is* a pin-list proposal; it stands or is replaced when Friday fixes the pin list. |
| **A VSSD haul** | **NEW if required** | not routed; §3g pre-analyzed its source (digital VSS taps, north island) so adding it is additive, not a re-baseline. |

**One-line rule:** everything set by *placement + block geometry* survives; everything set by
*which signal goes to which pad* is provisional. The rehearsal was built so the survivors are
the expensive parts (geometry, primitives, technique) and the redo parts are cheap (re-run the
matcher with the new endpoints).

### Provisional matched length: 433.76 µm
Down from the 4th-session ~458 µm because the left risers now escape M1→M3 **at the tap**
(no M1 escape leg + shorter path) rather than an M1 escape then via. History:
269 → 332 → 458 → **433.76**. It would move again if: core placement dx/dy changes; the pad
reorder changes which physical pad each net targets; or the currently-longest net (Q_P base
433.8, the pad target) changes. All four are padded to the longest base with serpentine in
the clear side regions, so the **number is provisional on placement + pin list**, not on the
routing style (which is now fixed).

---

## 3l. The in-context extraction works — and it caught a tap-to-block short in the "closed" quad (2026-08-22, 6th session)

§3j claimed a full in-context extract was impossible (flat extract shorts the inductor).
**That was wrong** — the repo already had the mechanism: `chip_top.abstract` +
`verify_extract.tcl` preload the `vco_varactors` + `vco_inductor_v2` abstracts with
`gds noduplicates true`, so `gds read` keeps the geometry-free abstract instead of traversing
the spiral. `reh_phase8.gds` instances that same `chip_top` cell (subhierarchy intact —
verified with `cell_list.py`), so the identical preload extracts the rehearsal **in full
context** without the inductor merging OUT_p/OUT_n. Harness: `analysis/reh_ctx_extract.tcl`.

**It immediately caught a real short the routes-only gate (§3i) had declared clean.** Extract
the same `chip_top` cell in two contexts and compare its exposed ports:
- `reh_base` (no routes): chip_top → **12 clean ports** (`… I_P I_N Q_P Q_N …`).
- `reh_phase8` (with the §3i routes): chip_top → **14 ports** — the two
  `DIV2_QUAD_v1_0/ib_conv_v1_{0,3}/a_8764_6964#` internal **bias nodes** exposed and **bridged
  to `I_P` / `Q_P`**. The chip_top instance line tied both port 9 (`a_8764#`) and port 10
  (`I_P`) to net `I_P`, and both port 11 and port 13 to `Q_P`.

The geometry is identical between the two runs; the only difference is the four routes, so the
**I_P and Q_P hauls shorted the DIV2 output to an ib_conv bias node.** Cause: I_P/Q_P escaped
on an **M1 hwire** running east from the tap, straight across the `a_8764_6964#` M1 node. Q_N/I_N
(M3-at-pin escape, no M1 hwire) were clean. This is invisible to DRC (an *overlap* leaves no
spacing gap) and to the routes-only extract (`a_8764#` lives inside chip_top, absent from
`reh_routes`). It reconciles with §3i rather than overturning it: the §3i four-part gate passed
*as stated*, but its part 3 (routes-only extraction) was explicitly flagged as unable to see
tap-to-block shorts — this harness is exactly the tool that closes that gap.

**Fix (both right nets):**
- **I_P/Q_P → M3-at-pin escape** (`escl=3`, no M1 hwire) removes the bias-node bridge.
- **I_P `novia=True`:** the I_P output pin is a **full via stack** (M1→via1→M2→via2→M3→via3→M4;
  `_iqtaps.py`), so adding our own via1/via2 tripped **V1.2a/V2.2a** against the pin's vias.
  Instead the M3 route **lands on the pin's existing M3** (its eastward first segment overlaps
  it) with no new via. Q_P/Q_N/I_N pins are **M1-only**, so they keep the via_stack (collision-free).

**The corrected quad gate (dx200/dy200), now five parts:**
| gate part | reh_base | reh_phase8 | verdict |
|-----------|----------|------------|---------|
| magic DRC total | 84 | **84** | 0 added |
| KLayout signoff variant-D | PASS, 168 waived | PASS, **168** | identical |
| routes-only extraction | 0 nodes | **4 nodes** | +4 nets |
| **full in-context** chip_top ports | 12 clean | **12 clean** | no bias node exposed |
| **full in-context** output→net map | — | I_P→I_P, Q_N→Q_N, I_N→I_N, Q_P→Q_P | **each distinct from every block net** |

Matched length unchanged at **433.76 µm** (all four, err 0.0000). **Lesson recorded:** the
in-context extraction is now the real distinctness gate; the routes-only extract is necessary
but not sufficient. Every subsequent haul (Items below) is gated with `reh_ctx_extract.tcl`.

## 3m. VTUNE "boxed" (WITHDRAWN, see 3n); and the .ext trap that was quietly corrupting the baseline (2026-08-22, tapeout drive)

### VTUNE: the tap is reachable, the rise is not (Item 2d)
`phase8_incontext.py`'s `HAUL` table cited a section 3m that had never been written. Recording it:

- **The TUNE tap IS accessible.** The gate pad sits *inside* the varactor comp ring, so a
  lateral M1 escape shorts the ring to VSSA (caught by the in-context extract). Via **up**
  (M1 -> M3) at the pad, then M3 west over the ring into the DIV2<->vco gap, is clean.
- **The rise to the west pad is boxed.** The only M2/M3-clear rise columns are **x181-204**,
  unreachable at low y because DIV2 blocks x<235.4, and **x288-397**, which sits under the
  inductor spiral (M5 x290-472). The sole column clear of *both* is **x288-290** - about
  2 um, 1 um off the spiral - i.e. a ~96 um M3 run beside the live inductor. Section 3h's
  coupling work forbids exactly that for the tune node (KVCO 822 MHz/V).

So the `VTUNE_tap` entry documents clean tap access only; the haul itself is unsolved and is
**T3's hardest single-net route**, not a routing tweak.

> **SUPERSEDED THE SAME DAY - see 3n.** This "boxed" conclusion was reached while chip_top
> was still 522 x 309. Once T2 seated the core inside the 1110 x 550 DIEAREA there was free
> die south of it, and a west-then-**south** exit through the 52.6 um DIV2<->vco gap crosses
> nothing but the GND ring. VTUNE is not boxed. The column analysis above is also wrong on a
> detail: x288-290 is not M4-clear. ISS is the same enclosure but is a DC
tail node, so rising under the spiral is acceptable for it.

### The `.ext` trap - same failure class as the silent I_N/Q_N short
`team_src/magic/vco_inductor_v2/vco_inductor_v2.ext` is tracked and carries the **real**
inductor extraction (`device rsubckt tm11k`, ports PORT1/PORT2). It was found modified in
the working tree at the start of this drive, overwritten by a **geometry-free abstract** -
no device, plus a new `GND` port.

**It was not a one-off from an analysis script.** `verify_cp.sh` - the flow gate itself -
reproduced the corruption on its very next run. The mechanism: **magic writes each cell's
`.ext` beside the file that cell was loaded from, not to the current directory.** Both
`verify_extract.tcl` and `reh_ctx_extract.tcl` `addpath` into the source tree to preload the
abstracts, so `extract all` writes back into `team_src/magic/vco_inductor_v2/`.
`reh_ctx_extract.tcl` already had a `cd /tmp` with a comment claiming it kept `.ext` files
out of the repo - **`cd` does not do it**, which is why the comment was there and the file
was corrupted anyway.

This corrupts **in the direction that hides shorts**: the abstract drops the device and adds
a port, so a later extraction diff compares against a baseline that has fewer things in it
than the real cell. Same class as the DRC-clean I_N/Q_N merge in section 3i - a check that
looks green because the thing it would have caught was silently removed from what it
compares to.

**Fix:** `extract path [pwd]` before `extract all` in both scripts, pinning the output
directory. Verified: `verify_cp.sh chip_top` returns byte-identical results (DRC 0, 5
devices, 12 ports, 21 nets, match uniquely) and the tracked `.ext` sha256 is **unchanged**
across the run.

### Regression (2026-08-22) - two cells, not six
Only two cells had a reason to have moved, so only two were run. `PFD_lib`, `CP_v1`,
`ibias_gen_v1` and `DIV2_QUAD_v1` were untouched and their section 5 results stand.

| cell | DRC | devices | ports | nets | LVS | wall |
|------|----:|--------:|------:|-----:|-----|-----:|
| chip_top | 0 | 5 | 12 | 21 | match uniquely | 14.6 s |
| vco_v1 | 0 | 4 | 6 | 11 | match uniquely | 11.2 s |

`vco_v1` was re-run because its `.ext` had been disturbed and restored, so its last result
was not trustworthy. Both match section 5.

### **T4 baseline: chip_top blocks-only magic DRC = 84** (2026-08-22)
Measured with `analysis/reh_drc.tcl` at `REH_CELL=chip_top` - full geometry, **no** abstract
preload, which is the same rule set the phase-8 gate uses:

```
==== chip_top  TOTAL 84 ====
  84  chip_top / vco_v1 / vco_varactors   (the same 84 counted hierarchically)
```

All 84 are the known `PL.5a` in `vco_varactors`. This is **identical to `reh_base`'s 84**, so
the two baselines agree. **Every phase-8 DRC number is a delta against 84, never an
absolute.** Note that `verify_cp.sh chip_top` reports **DRC 0** for the same GDS - it
preloads the `vco_varactors` abstract, so the PL.5a geometry is not traversed. Two different
numbers, two different rule sets; do not compare across them.

*(Minor, unfixed: `reh_drc.tcl`'s per-rule printer has its `lindex` indices swapped - it
prints the count where the rule name belongs - and its violation-box loop aborts on a
non-numeric operand. The TOTAL is correct; the breakdown is mislabelled.)*

### Break-before-VSSD is settled
Confirmed from `padframe/A01/project_defs/BH/A01_BH_pad_map.yaml`:

```yaml
breaks:
- instance: BRK_BEFORE_N06
  reason: additional_power_ground_set
  before_slot: N06        # = VDDD's slot in the 12-pin issue
- instance: BRK_AFTER_BH
  reason: project_boundary
  after_slot: N07
```

BV shows the same pattern (`before_slot: N01`, `after_slot: N02`). The reason is
`additional_power_ground_set` - the break fires before a power/**ground** *set*, not before a
lone power pad - and Bailey approved an `info.yaml` whose digital group runs DVSS, signals,
DVDD, which only validates under that reading. With VSSD inserted it becomes the set's first
member, so the break should move to VSSD's slot.

**Still verify when the regenerated DEF lands:** `breaks[0].before_slot` must name **VSSD's**
slot, not VDDD's. If it names VDDD, VSSD is outside the digital island and must move to
*after* VDDD. `in_c` landing at N08 remains genuinely open.

---

## 3n. VTUNE is NOT boxed - 3m's premise died when the core was seated (2026-08-22)

Section 3m concluded VTUNE was boxed. **That conclusion is withdrawn.** It was reached while
chip_top was 522 x 309 and every route had to win an internal column; T2 seated the core at
(175.00,178.50)-(697.00,487.50) inside a 1110 x 550 die, which created free die **south of
y178.5, west of x175, east of x697 and north of y487.5** that did not exist when 3m was
written. Re-measured against the real geometry with `analysis/vtune_routes.py` (occupancy scan
per segment, seated GDS, writes nothing).

### Where the tap actually is, and which way it faces
- **VTUNE tap: die (558.68, 266.70) on M1** (= core (358.68, 66.70)), read from the `L34/10
  VTUNE` label in the seated GDS - not from memory.
- Block extents, die coords: `DIV2 (200.00,200.00)-(437.36,374.17)`,
  `vco_v1 (490.00,200.00)-(672.00,379.48)`, `ibias (200,405)-(381.76,470.25)`,
  `CP (410,405)-(483.50,433.02)`, `PFD (410,445)-(466.99,469.00)`.
- **The DIV2<->vco gap is die x437.36-490.00 - 52.6 um wide**, not the ~2 um 3m implied. 3m's
  "x288-290" came from the channel map's *clear columns*, which were computed for
  **y[175,287.5] core** - the band a NORTH-bound riser crosses. Nobody had measured the gap at
  the tap's own y, going SOUTH, because before T2 there was nothing south to go to.
- **East is genuinely blocked** (measured): 141 um east of the tap crosses M1 x6, M2 x6, M3 x5,
  M4 x2, M5 x6, comp x5, poly x6 and 11 vias - it is the vco interior. The tap faces **west**.

### The three candidates, measured

| route | length | what it crosses |
|-------|-------:|-----------------|
| **(a) west into the gap, SOUTH out of the core, west through free die, north up the west strip** | **977.38 um** | tap escape (M1/comp/cont/poly x1 - the tap's own comp ring, handled by the 3m via-up-at-the-pad); **M5 x4** = the GND ring only. The 455 um west lane at y165, the 317.5 um riser at x10 and the 9.5 um pad jog are **CLEAR on every layer**. |
| (d) 3m's die-x489 column, north past the spiral | 798.98 um | **M5 x18 + M4 x2** on the riser - i.e. roughly half the 228 um rise sits over spiral turns |
| (a-north) north exit through the gap at die x486 | 798.98 um | M3 x18, M4 x14, M5 x4, M2, v2, v3 - the CP/PFD/ibias region, and it lands in the same 60 um channel the I/Q quad needs |

**772 of route (a)'s 977 um is virgin die with nothing on any layer.**

**A correction to 3m while we are here:** the "x288-290" column is **not M4-clear**. Measured at
die y290-386: x486 M4, x487 M3+M4+v3, x488 M4, x489 M4, x490 M4+M5, x491 M4+M5. The channel
map's columns were "clear of M2 AND M3" only; M4 was never in that criterion.

### One trap worth recording
The west riser must be held **inboard at x~10, never at the pad column x0.5**. The west pin
rectangles all sit at x[0,1] - VSSA y46.36-118.64, VDDA y146.36-218.64, IBIAS y260.34-304.66,
ISS y360.34-404.66 - so a riser run up x0.5 to reach VTUNE at y460-505 would short VTUNE to
IBIAS, ISS, VDDA and VSSA at the padring. Approach inboard, jog west onto the fingers at the
target y only.

### Costing the four options

| | route | length | coupling | what it invalidates | effort |
|-|-------|-------:|----------|---------------------|--------|
| **(a)** | around the core through free die | **977 um** (+178 vs the alternatives) | **~ -107 dBc**: nearest aggressor is DIV2 metal 35 um from the y165 lane; ~0.17 fF over 455 um -> ~1.4 mV on the routing node -> /48.6 through the 15k -> 0.028 mV -> 0.023 MHz | **nothing** | **2-3 h** |
| (b) | re-place blocks inside the core | n/a | n/a | matched-quad length (433.76), lane assignment, every per-net escape coordinate, the 3f dy sweep, the 3h crossing table, the channel map, the 3c ground-return numbers, the check_placement baseline; re-gate everything | 2-3 days |
| (c) | re-open vco_v1 to bring TUNE to an edge | shortest possible | best | vco_v1's sign-off (DRC 0 / LVS match uniquely / KLayout 168=W4) and chip_top's; touches the one cell carrying the inductor abstract **and** the W4 waiver | 3-5 days, and it re-opens a signed-off block six days before the gate |
| (d) | accept the die-x489 run | 799 um | **~ -78 dBc** capacitive, **magnetic term unquantified** | nothing, but see below | 1-2 h |

**(d)'s number, by the 3h method, and why it should not be trusted at face value.** 18 of 38
riser segments over M5 ~ 108 um of overlap. Using the recorded 0.047 fF/um -> Cc ~ 5.08 fF;
against the node C ~ 63 fF implied by 3h's own calibration point (2.35 fF, 0.5 V -> 18 mV) the
divider is 0.0747, so a ~2 Vpp-se tank (verification.md 3.2: "near rail-to-rail single-ended")
puts ~149 mVpp on the routing node; the 15 kohm tune R low-passes it (~/97 at 5 GHz) to
~1.54 mV -> x822 MHz/V -> 1.27 MHz -> **-78 dBc**. Two reasons that is optimistic:
1. **0.047 fF/um is a sidewall figure being applied to an overlap geometry.** M3 running under
   M5 plate is not two coplanar M2 wires at minimum spacing.
2. **It captures no magnetic coupling.** The spiral is an inductor; the trace forms a loop in
   its field. That is the actual reason for the never-route-under-the-spiral rule, and
   quantifying it needs EM (`team_src/em/extract_inductor.py` / openEMS), not a cap-per-um.

The 3h calibration is reproduced exactly by this method (0.3 MHz at 2.5 GHz -> -84.4 dBc vs the
recorded -84 dBc), so the arithmetic is sound; it is the model's *scope* that does not cover (d).

### Recommendation: **(a)**
Route (a) buys a route that crosses nothing but the GND ring, on a different layer with no
applicable rule, for **+178 um on a DC node** whose series 15 kohm makes the added resistance
irrelevant. It invalidates nothing, needs no block re-opened, and it puts VTUNE on the opposite
side of the die from the I/Q RF hauls instead of alongside them. (d) saves 178 um and buys an
unquantified magnetic risk on the most phase-noise-sensitive node in the design. (b) and (c)
are large, and neither is necessary once the south exit is on the table.

Secondary benefit: the same south corridor is the natural path for **ISS** (die tap
(595.84,260.33), same vco enclosure, DC tail node), so solving VTUNE this way likely solves ISS
too - to be confirmed when it is routed, not assumed here.

---

## 4. T2 DONE - the core is seated in the A01_BH DIEAREA (2026-08-22)

`gds/chip_top.gds` now **is** the padframe block: boundary exactly `(0,0)-(1110,550) um` =
`(0,0)-(222000,110000)` dbu, the A01_BH `DIEAREA` verbatim.

### How
A final step in `route_chip.py`, after all routing, replacing the old
"0/0 boundary at the true die extent" code:

```python
DX, DY = 200.0, 200.0            # core offset inside the die (3f)
DIE_W, DIE_H = 1110.0, 550.0     # A01_BH DIEAREA, exact
chip.transform(pya.DTrans(DX, DY))
ly.clear_layer(ly.layer(0, 0))   # exactly one boundary, whatever was there before
chip.shapes(ly.layer(0, 0)).insert(pya.DBox(0.0, 0.0, DIE_W, DIE_H))
```

Seating here rather than offsetting `chip_merge.py`'s `BLOCKS` table means **every routing
coordinate above it stays core-frame and unchanged**, and `check_placement.py` keeps
comparing core-frame to core-frame - verified still `PLACEMENT CONSISTENT`, exit 0, **no
re-baseline needed**. A guard raises if the cell already looks seated (bbox LL x >= 0), so
running `route_chip.py` twice cannot silently double-shift the core.

### Measured, verified independently in KLayout
```
core frame  : (-25.00,-21.50)-(497.00,287.50)  522.0 x 309.0 um
seated      : core occupies (175.00,178.50)-(697.00,487.50)
top bbox    : (0,0)-(222000,110000) dbu   = (0.000,0.000)-(1110.000,550.000) um
layer 0/0   : exactly 1 shape in chip_top, 0 in every other cell
```
The old 522 x 309 rectangle is **gone**, not coexisting - `clear_layer` guarantees it. dbu is
0.005 um on both sides, so this was a pure translation, no scaling.

### The four-part gate on the reframed cell

| gate part | before reframe | after reframe | verdict |
|-----------|----------------|---------------|---------|
| KLayout signoff (the real signoff DRC) | PASS, 168 waived (84 PL.5a_LV + 84 PL.5b_LV) | PASS, **168 waived**, same split | **identical** |
| `verify_cp.sh chip_top` DRC | 0 | **0** | identical |
| extraction: devices / ports / nets | 5 / 12 / 21 | **5 / 12 / 21** | identical |
| LVS | match uniquely | **match uniquely** | identical |
| `check_placement.py` | CONSISTENT | **CONSISTENT** | identical |
| magic hierarchical DRC count | 84 | **106** | **disagreed - investigated below** |

### The magic 84 -> 106 count is an artifact. The violations did not change.
Reported rather than papered over, because a DRC number disagreeing with a baseline is
exactly the thing that must not be waved through. Three independent checks:

1. **Isolation.** Three throwaway variants of the reframed GDS, same DRC deck:
   - 0/0 boundary layer deleted entirely -> **106**
   - 0/0 boundary put back at the old core extent -> **106**
   - core translated back by -200/-200 -> **84**

   So it is not the boundary rectangle at all. It tracks the **absolute position** of the
   core, which cannot create or destroy a poly-to-diffusion spacing violation.

2. **The violation set is bit-identical.** Dumped every error box from `drc listall why` for
   the seated and the unseated cell, added +40000 dbu to each unseated coordinate, and
   compared as multisets: **252 boxes both sides, 0 extra, 0 missing.** Same violations,
   same places, same multiplicities.

3. **KLayout agrees with the baseline, not with magic.** The signoff deck reports
   **84 PL.5a_LV + 84 PL.5b_LV before and after** - unchanged.

All 106 are the single known rule `PL.5a` (poly spacing to diffusion < 20), the device-internal
`vco_varactors` errors that are waived at signoff. Magic's per-cell attribution shifts
(`vco_varactors` 84, `vco_v1` 84, `chip_top` 84 -> **106**) when the parent frame moves; the
hierarchical *count* is frame-dependent, the *box set* is not.

**Consequence for T4 - use the box set, not the count.** `drc list count total` is not a safe
invariant across a frame change. The T4 magic-DRC baseline at the seated frame is:

> **chip_top seated, blocks only: magic total 106, 252 error boxes, all PL.5a in
> vco_varactors.** Every phase-8 haul is a delta against **that**, and a delta of zero must
> mean *the same 252 boxes*, not merely the same total.

The pre-seat figure of 84 stays valid only for the pre-seat frame; do not compare across.

### Not done here, deliberately
The GND ring still stops at the old core perimeter (die x157.5-689.5). Extending it west to
the DIEAREA edge for VSSA is **T3**, not T2. Pin labels are still at their block-tap
positions; relocating them onto the DEF pin fingers is also T3, and waits on the regenerated
DEF because VDDD and REF_IN move +100 um east.

---

## 5. Regression baseline (re-run 2026-08-21, five sessions)

`verify_cp` re-run 5th session, all exit 0 / RESULT PASS. This session touched only
`analysis/` scripts, `.waivers` for the throwaway reh cells, and docs — **route_lib.py was
NOT modified**, and no block layout/schematic/flow file was touched:

| cell | DRC | devices (LVS) | LVS |
|------|-----|---------------|-----|
| chip_top | 0 | 5 | match uniquely |
| PFD_lib | 0 | 7 (+18 fill/decap) | match uniquely |
| CP_v1 | 0 | 38 | match uniquely |
| ibias_gen_v1 | 0 | 228 | match uniquely |
| DIV2_QUAD_v1 | 0 | 149 | match uniquely |
| vco_v1 | 0 | 4 | match uniquely |

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
