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

## 5. Regression baseline (re-run 2026-08-21, four sessions)

`verify_cp` re-run, all exit 0 (unchanged — the ground/ordering/RF-loading analysis,
the matched-quad dry-run, and the docs made no geometry/schematic/flow change;
route_lib was exercised, not modified):

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
