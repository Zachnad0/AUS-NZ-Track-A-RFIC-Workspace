# Layout Review — Team A01, AUS/NZ Track A RFIC

**IEEE SSCS Chipathon 2026 · GF180MCU (gf180mcuD) · issue [#143](https://github.com/sscs-ose/sscs-chipathon-2026/issues/143)**
Prepared 2026-09-01 for **Caglar Ozdag**, at the request of `silicon-vlsi` on issue #143
(2026-09-01 05:59 UTC). Repo state: branch `integration`, commit `423d148`.

This document supersedes the 2026-08-10 review deck. **`docs/layout-review-aug14.md` is kept
unchanged as the historical record** and is not superseded — it holds the per-block working
notes this document summarises.

**Reading rule used throughout.** Every number below is read from a named file. Where a check
does not exist, the line says *not done* and the item is repeated in §6 (Gaps). §6 is not a
formality — read it before drawing conclusions from §1–§5.

---

## 0. The question that prompted this document

> *"The original proposal was the complete PLL but your first layout review seems like changed
> the scope to only the PFD but now it seems it is the complete PLL with the I/Q."*
> — `silicon-vlsi`, issue #143, 2026-09-01

**The scope never changed. The review record stopped.**

The 2026-08-10 deck (`A1 AUS_NZ Track A RFIC Layout Review.pdf`, 5 slides) reviewed exactly one
block, `PFD_lib`, and said so explicitly on its own slides — slide 3: *"CP_v1 is the analog
block. Golden netlist verified… Layout NOT drawn, so no matching, guard-ring, or isolation
evidence exists yet."* Slide 5: *"This is one block, not the integrated RFIC top, which does not
exist yet."* Slide 5 then states the plan: *"By Aug 14: draw CP_v1… By Aug 21: integrate
PFD_lib and CP_v1 into an RFIC top."*

That plan was executed and then some, and **none of it was ever packaged for review**:

| Date | What closed | Commit / artifact |
|---|---|---|
| 2026-08-13 | `CP_v1` charge-pump layout | `gds/CP_v1.gds` |
| 2026-08-14 | `ibias_gen_v1` bias generator layout | `team_src/magic/ibias_gen_v1.mag` |
| 2026-08-17 | `DIV2_QUAD_v1` quad-phase ÷2 divider layout | `gds/DIV2_QUAD_v1.gds` |
| 2026-08-20 | `vco_v1` LC-VCO layout; **`chip_top` integrated, routed, LVS-clean** | `gds/vco_v1.gds`, `gds/chip_top.gds` |
| 2026-08-22 | Seated into the organizer padframe, slot variant BH | `route_chip.py` |
| 2026-08-25→29 | Secondary ESD clamps, via arrays, density keep-out markers | `7391653`, `914bcdf`, `781e30b`, `efc63e8`, `205263a` |

So the deck Caglar saw is an accurate snapshot of **2026-08-10**, three weeks stale. The design
on disk today is the integrated PLL.

**One genuine scope reduction, made early and not since revisited.** The registered proposal
title is *"Microwave RFIC with integrated VCO, PLL, and IQ modulator"*. **The IQ modulator was
dropped** — `docs/scope.md` §1 places "IQ modulator, SPI, output chain" in **Tier 3 (stretch,
only if Tier 1+2 close early)**, frozen 2026-07-30 in response to the schematic-review
Conditional-Go. Tier 3 was never started.

**This matters for how the `I_P/I_N/Q_P/Q_N` pins are read.** They are **not** modulator ports.
They are the **CML divider's four quadrature phases** brought out through monitor-grade
buffers, so the ÷2 ratio and the I-to-Q phase can be measured on the bench. The quadrature is a
free by-product of the master–slave CML ÷2 topology, not a modulator.

**And one late pin change Caglar will notice.** `I_P` is no longer a pad — it is an internal net
carrying the loop feedback. See §2.3; it is the single most consequential correction made since
the last review.

### What is being taped out, in one line

An **integer-N PLL**: reference in → PFD → charge pump → *off-chip* loop filter → LC-VCO →
CML ÷2 quadrature divider → back to the PFD, with three of the four divider phases brought out
as monitor outputs. Chip-level bias generator on board. Loop filter deliberately off-chip.

```
 REF_IN ─▶ PFD_lib ─▶ CP_v1 ─▶ CP_OUT ─┤ off-chip R + C1‖C2 ├─▶ VTUNE ─▶ vco_v1 (4.13–6.35 GHz)
             ▲ FB                                                            │ VCO_OUTP/N
             │                                                               ▼
             └──────────── I_P (internal) ◀────────── DIV2_QUAD_v1 (CML ÷2, quadrature)
                                                          │
                                          ibias_gen_v1 ────┘   └──▶ I_N, Q_P, Q_N  (pads, 2.4–3.2 GHz)
```

---

## 1. Per-block implementation and status

All five blocks are drawn, DRC-clean and LVS-clean against a hand-written golden netlist.
DRC and LVS results below are read from `team_src/magic/verify_work/*.drc.log` and `*.comp.out`
(the working directory of `team_src/magic/verify_cp.sh`; gitignored, regenerable in ~15 s).
Areas are from `docs/tracking.md` §5.1, measured on the GDS/`.mag` bounding boxes.

| Block | Implementation | Area (µm) | Magic DRC | netgen LVS |
|---|---|---|---|---|
| `PFD_lib` | Library-cell PFD, our topology, LibreLane P&R | 57.0 × 24.0 = 1,368 µm² | **0** | **match uniquely** — 7 dev / 11 nets / 6 ports |
| `CP_v1` | Full-custom analog charge pump, Magic | 73.5 × 28.0 = 2,059 µm² | **0** | **match uniquely** — 8 dev / 10 nets / 7 ports |
| `ibias_gen_v1` | Full-custom bias generator, Magic | 181.8 × 65.3 = 11,868 µm² | **0** | **match uniquely** — 17 dev / 15 nets / 6 ports |
| `DIV2_QUAD_v1` | Full-custom CML ÷2 + 4 slicer converters | 237.4 × 174.2 = 41,340 µm² | **0** | **match uniquely** — 75 dev / 47 nets / 9 ports |
| `vco_v1` | LC-VCO: cross-coupled core + varactor array + spiral + tune R | 182.0 × 179.5 ≈ 32,700 µm² | **0** | **match uniquely** — 7 dev / 7 nets / 6 ports |
| **`chip_top`** | All five integrated, routed, seated in the BH slot | **1110 × 550** (die) | **0** | **match uniquely** — 10 dev / 20 nets / **11 ports** |

`verify_cp.sh` hard-fails on any netgen **property error** (W/L mismatch beyond 1 %) as well as
on a topology mismatch — netgen otherwise prints *"Circuits match uniquely"* while listing size
deltas separately, which would let a mis-sized device through. Every result above is
property-error clean.

> **Two different net counts exist for `chip_top`; the table above uses the LVS one.**
> `verify_cp.sh`'s summary line prints **25 nets** — its own awk tally of distinct node tokens
> in the extracted top-level subcircuit. The number netgen actually compared, and the one
> quoted above, is **20 / 20** (`verify_work/chip_top.comp.out`). The 25 is informational and
> is not gated on; the gate is DRC count, port count, the LVS verdict and property errors.

### 1.1 `PFD_lib` — phase/frequency detector

Two `dffrnq_1` (async active-low-reset DFFs, D tied high via 2× `tieh`) plus a `nand2_1`
coincidence gate, in our own `PFD_v1` topology, built from the **5 V** `gf180mcu_fd_sc_mcu7t5v0`
library and placed/routed by LibreLane Classic. The analog blocks are 3.3 V (`*_03v3`); both run
off the single 3.3 V rail. The flavour split is deliberate and is discussed in `docs/scope.md`
§4.1–4.2 — GF180 ships no 3.3 V standard-cell library, and hand-drawing the digital cells was
not feasible on the schedule.

Signoff run: `librelane_pfd/runs/RUN_2026-08-05_23-52-38/`. First-hand from
`final/metrics.json`:

| Metric | Value |
|---|---|
| `magic__drc_error__count` | **0** |
| `klayout__drc_error__count` | **0** |
| `route__drc_errors` | **0** |
| `design__lvs_error__count` / `design__lvs_device_difference__count` | **0** / **0** |
| `antenna__violating__nets` / `__pins` | **0** / **0** (0 diodes required) |
| `design__power_grid_violation__count` | **0** |
| `route__vias` | 26, all single-cut |
| `design__instance__count` | 52 |

Cell inventory counted directly out of `final/nl/PFD_lib.nl.v`: 2× `dffrnq_1`, 1× `nand2_1`,
2× `inv_1`, 2× `tieh` — 7 LVS devices. The remaining 45 instances are physical-only
(8× `endcap`, 7× `fill_1`, 6× `fill_2`, 6× `filltie`, and 18 `fillcap_*`).

**The reset delay survived P&R, verified in the netlist, not asserted.** `final/nl/PFD_lib.nl.v`
lines 71 and 73 show `inv_1 XI1 (.I(NANDO) …)` → `NDLY` → `inv_1 XI2 (.I(NDLY) …)` → `RSTN`.
A grep for `dlyb|buf` returns nothing else. This matters: the *first* LibreLane run silently
inserted three `dlyb_1` delay buffers, one of them on **FB→CLK but not on REF** — an
asymmetry the locked PLL would have read as real static phase error. The config keys that
suppress it, and a standing reject-the-run rule, are recorded in `docs/verification.md` §2.3.3.

**Power grid** (`resolved.json`, `…/55-openroad-irdropreport/irdrop.rpt`): Metal1 rails
0.6 µm, Metal4 vertical / Metal5 horizontal straps 1.6 µm, Metal4/5 core ring. IR drop at
corner `nom_tt_025C_5v00`: **VDD 9.60 µV worst / VSS 18.2 µV worst, 0.00 %**, all shapes
connected.

**Two documented LVS waivers**, both justified in `docs/verification.md` §2.3.1: (1) the 18
`fillcap_*` decaps are ignored — the same waiver LibreLane's own run applies via `LVS_IGNORE`,
using only the PDK-provided `ignore class`; (2) the golden's standard cells are resolved
against the PDK `mcu7t5v0` SPICE so both sides carry full definitions — a comparison method,
not a violation.

**Tap spacing — stated honestly.** GF180 `DF.13_MV`/`DF.14_MV` cap tap-to-device distance at
**15 µm** for 5 V devices. This build ran with the LibreLane default `FP_TAPCELL_DIST = 20 µm`,
which **exceeds that limit**; it passes only because the block is 57 × 24 µm, the standard cells
self-tap, and six `filltie` cells keep the real distance under 15 µm — confirmed solely by
KLayout DRC = 0. `librelane_pfd/config.json` now carries an explicit `FP_TAPCELL_DIST = 15`
(commit `e3b6cae`), but **that is a config-only change with no LibreLane re-run**, so the GDS
being taped out still relies on the incidental compliance above. 20 µm must not be reused on a
larger 5 V block.

### 1.2 `CP_v1` — charge pump (full-custom analog)

Eight transistors, ports `UP DOWN CP_OUT VDD VSS VGP VGN`. Golden:
`team_src/magic/CP_v1_golden.spice`.

| Device | Type | W/L | Role |
|---|---|---|---|
| M_PREF / M_PSRC | `pfet_03v3` | 50 µ / 2 µ | PMOS mirror **matched pair** |
| M_PSW | `pfet_03v3` | 50 µ / 0.3 µ | UP switch |
| M_NREF / M_NSNK | `nfet_03v3` | 10 µ / 2 µ | NMOS mirror **matched pair** |
| M_NSW | `nfet_03v3` | 10 µ / 0.3 µ | DOWN switch |
| M_INVP / M_INVN | `pfet`/`nfet_03v3` | 2 µ / 1 µ, L 0.3 µ | UP → UP_B inverter |

Layout extracts **38 raw fingers**; netgen reports *"Merged 30 parallel devices"* and both sides
settle at **8 devices / 10 nets**, match uniquely. The `nfet_03v3`/`pfet_03v3` PDK wrappers are
pin-only black boxes to netgen and equate cleanly against the schematic-style golden — handled
in the netgen setup, not by loosening it.

**Matching, as drawn:** mirror pairs `M_PREF↔M_PSRC` and `M_NREF↔M_NSNK` are common-centroid
interdigitated with identical finger orientation, **one dummy finger at each array end**, L = 2 µm
to aid matching, both devices of a pair in the same well region at the same y. n+ guard ring on
VDD around the PMOS group, p+ ring on VSS around the NMOS group. Drawing packet:
`docs/cp-layout-packet.md`.

**What is *not* claimed:** the packet's *full* common-centroid dummy set and complete guard-ring
treatment are **deferred to a matching-refinement pass that has not been done**. There is no
extracted (PEX) match figure for this layout — see §6.

**One known circuit-level flaw, at schematic, not fixable by layout:** **+110 fC/cycle charge
injection** at the switches. It is the likely dominant reference-spur mechanism, and reference
spurs scale directly with |KVCO| — so the corrected KVCO of −1.1 GHz/V (§4.4) makes it ~1.4×
worse than at the old −790 MHz/V figure. Recorded so it is not mistaken for a drawing defect.

### 1.3 `ibias_gen_v1` — chip-level bias generator

Replaces `CP_v1`'s two ideal 50 µA sources and the divider's tail reference with mirrored legs
off one external **240 µA** reference. Ports `IBIAS VGP VGN IB_DIV2 VDD VSS`. Four-row stack
(NMOS mirror/cascode in pwell, PMOS mirror/cascode in nwell), wide W=16 m=24 legs split
2× nf=12, inter-band routing by layer-per-net-class, end dummies on the 24:5 ratio array.
Built headlessly by `team_src/magic/phase5/ib_block.tcl` + `ibias_gen_v1.tcl`.

Extracts **228 raw fingers**; netgen *"Merged 211 parallel devices"* → **17 devices / 15 nets**,
match uniquely. The 17th device is a **layout-only tied-off dummy** (`XMDUM`, nfet W=4 L=2 m=4,
Vds = 0) representing the two end-dummy fingers; it is present in the golden deliberately, so a
forgotten dummy would show as a count mismatch rather than be waived away. The schematic stays
at 16 devices. This is documented in `docs/verification.md` §2.6.1 and is **not** a schematic
error, but any future flow that netlists `ibias_gen_v1.sch` directly must add the same dummy.

**`gds/ibias_gen_v1.gds` is committed** (added at `4156997`, "needed for top-level submission"),
alongside `team_src/magic/ibias_gen_v1.mag`. All five blocks have a committed GDS.

> **Correction, 2026-09-01.** An earlier revision of this document said `ibias_gen_v1` had no
> committed GDS. That was wrong. It came from `docs/tracking.md` §5, where the line
> "ibias_gen_v1.mag is flat, no committed GDS" is dated 2026-08-18 and was true when written —
> the GDS landed afterwards at `4156997`. Verified now with `git ls-files gds/`, which lists
> all thirteen tracked GDS files including `gds/ibias_gen_v1.gds`.

### 1.4 `DIV2_QUAD_v1` — CML ÷2 quadrature divider (full-custom, the RF core)

The largest and most demanding block. **75 devices, 47 nets, 9 ports**
(`CK CKB IBIAS I_P I_N Q_P Q_N VDD VSS`), 237.4 × 174.2 µm. Extracts 149 raw devices at its own
level plus four `ib_conv_v1` instances; netgen *"Merged 126 parallel devices"* → 75, match
uniquely. KLayout variant-D DRC **0** on the complete GDS.

Contents: two NMOS CML D-latches in a master–slave ring (master clocked by VCO `out_p`/`out_n`,
slave on the complement, one loop inversion) → ÷2 with **quadrature I/Q by construction**; three
NMOS bias devices; and **four identical slicer/converter chains** (`ib_conv_v1`) turning the
~0.83–1.4 V CML differential into CMOS levels for the pads.

**Why CML and not static CMOS — measured, not assumed.** `docs/verification.md` §7 records a
toggle-FF probe: at 1.00 GHz the static-CMOS divider gives a clean 3.68 Vpp ÷2; at 2.00 GHz it
falls to 0.61 Vpp and does not reach logic levels; from 3.00 GHz up it is **dead (< 2 mV)**. The
VCO's *slowest* corner is 4.11 GHz. Static CMOS cannot divide this VCO at all. CML costs
continuous bias current — that is the price, and it is the divider's dominant power term.

**Final sizing:** tail 2.4 mA / R 300 Ω per latch (400 µA/2 kΩ and 1.2 mA/500 Ω were both tried
and both failed at the band top). Two tails × 2.4 mA = 4.8 mA CML core, mirrored 10:1 off the
240 µA reference.

**Converter sizing (locked, per phase):** CC 100 fF, RFB 20 kΩ, INV1 pfet 10 µ / nfet 4 µ, INV2
26 µ / 11 µ, INV3 44 µ / 16 µ, R_SER **1 kΩ** (`ppolyf_u_1k`, 2 × 2 µm, on-chip inside the block).

**Floorplan and the one characterised layout limitation.** The four converters sit at the
corners, core and bias centred, in "option-c" orientation (I_P/Q_P east-unmirrored, I_N/Q_N
west-mirrored) so any mirror-induced slicer offset is **common to the I and Q paths and cancels
in the quadrature comparison**. What does not cancel is a routing-length asymmetry: the Q
converters sit ~53 µm below their latch-B taps, so each Q input haul is ~53 µm longer than its I
counterpart. At ~41 fs/µm that is **~2.2 ps**, a *static* I-to-Q offset common to Q_P and Q_N —
not an intra-pair duty error. It is the cost of the stacked-below-Q floorplan.

> **Discrepancy flagged rather than propagated.** `docs/layout-review-aug14.md` DIV2.1 converts
> that 2.2 ps to *"~1.0° at the 1.25 GHz divider output"*. The arithmetic is right for 1.25 GHz,
> but **the divider output is 2.4–2.5 GHz at the ISM operating point**, where 2.2 ps is
> **≈ 1.9–2.0°**, not 1.0°. The physical quantity (~2.2 ps, from ~53 µm) is the reliable number;
> the degree figure in the older doc understates it by ~2×. This has not been re-derived from
> layout and should be treated as an open item, not a result.

### 1.5 `vco_v1` — LC-VCO

Complementary cross-coupled LC oscillator: 2× `nfet_03v3` W40 L0.28 + 2× `pfet_03v3` W70 L0.28
cross-coupled (`vco_core`, 28.55 × 31.55 µm, DRC 0, KLayout var-D 0, LVS match uniquely against
a 4-device golden); a differential varactor array (`vco_varactors`, 42× `cap_nmos_03v3_b` 5×5 µm
= 2 × m=21, mirror-symmetric about the vertical centre for differential match, 46.7 × 54.5 µm);
a tune resistor (`vco_tune_r`, `ppolyf_u_1k` w1 l15 = 15 kΩ); and the custom spiral inductor
`vco_inductor_v2` (**182 × 84 µm, 1.2 nH**; 271 shapes as streamed into the deliverable GDS;
**Magic DRC 0 and KLayout DRC 0**, the KLayout run reporting clean over 247 polygons — the two
shape counts are different tools counting differently, not a discrepancy).

**The inductor is instanced as a true Magic abstract** (`property LEFview true` +
`GDS_FILE`/`GDS_START`/`GDS_END` + `FIXED_BBOX` + M5 port pads, **no coil geometry**), with the
full spiral streamed into the deliverable GDS from `GDS_FILE`. This was necessary, not stylistic:
the dual spiral's PORT1/PORT2 are M5 leads *interior* to one DC-continuous coil, so with the coil
present any parent-level extraction merges `OUT_p` and `OUT_n` through it. `LEFview` alone does
not black-box the parent — only a geometry-free abstract does.

**`ISS` and `GND` are separate, and getting there was a real design decision.** GF180 `nfet_03v3`
bulk defaults to the global p-substrate, so the first assembly extracted `ISS = GND = substrate`
and LVS matched *only* with a merged golden. Rather than accept a sources-to-ground VCO, the
layout was rebuilt (`3390c30`) with `taps=0` + explicit pwell + three psub taps to a **separate
GND rail**, keeping the source rail on `ISS`, plus **one authorised schematic edit** (`b315c27`)
moving `XM1`/`XM4` bulk from `ISS` to `GND`. `verify_cp.sh vco_v1` then passes with ISS and GND
distinct and **no merged-net assumption**. The block was **re-simulated as drawn**, with the body
effect now present: 0.3 V → 6.35 GHz (568 mV), 1.5 V → 5.53 GHz (544 mV), 3.0 V → 4.13 GHz
(472 mV) — **band 4.13–6.35 GHz**, against the previously recorded 4.11–6.37 GHz. Startup margin
is not thin.

**Waiver W4 — the only DRC waiver in the design.** See §2.5.

---

## 2. Chip-level integration — `chip_top`

### 2.1 Die and frame

**The declared die is 1110 × 550 µm — slot variant BH.** Verified this session by KLayout on
`gds/chip_top.gds` (mtime 2026-08-29 02:58): top cell `chip_top`, dbu 0.005, top-cell bbox
**`(0,0; 1110,550)`**, and the layer 0/0 boundary rectangle **identical** — nothing overhangs.
The organizer package agrees: `padframe/A01/project_defs_12pin/BH/A01_BH_interface.yaml` gives
`size_microns: [1110, 550]`, `diearea_dbu: [0,0,222000,110000]`, `usable_area: 610500`.

> **Correction to issue #143.** The issue body still states **522 × 309 µm**. That is the
> **routed core**, not the die — it is the extent the five blocks plus their inter-block routing
> occupy *inside* the slot (core seated at (175.00, 178.50)–(697.00, 487.50)). The declared die
> is 1110 × 550. Corrected issue text is drafted separately and has **not** been posted.

Block placement (`chip_top.mag`, block bbox-LL in core µm): DIV2 (0,0) · vco (290,0) ·
ibias (0,205) · CP (210,205) · PFD (210,245). Block-merge extent 472.00 × 270.25 µm before the
ground ring; 522 × 309 with it. The die is mostly empty — this is a small block in a large slot,
which is the direct cause of the density situation in §6.

**The deliverable GDS is built by KLayout, and Magic must never author it.**
`team_src/magic/phase5/chip_merge.py` streams each block's signed-off golden GDS **verbatim** at
the floorplan offsets; `route_chip.py` adds the chip-level metal. A Magic `gds read`→`gds write`
round-trip of PFD_lib's foundry dualgate perturbs sub-grid geometry and produces a spurious
0.68 µm `DV.5` sliver. It would also **silently lose two of the three density marker layers** —
`NDMY 111/5` is commented out in Magic's techfile and `IND_MK 151/5` is absent from it entirely
(Magic prints `Unknown layer/datatype in boundary, layer=151 type=5` and drops the polygon).
`chip_top.mag` is the placement record and Magic-DRC gate only. (`docs/verification.md` §8.8.)

### 2.2 Pin list and connectivity

**12 pads, 11 LVS ports.** Pads from `info.yaml`; slots from the organizer-issued
`A01_BH_interface.yaml` (`participant_pin_count: 12`); connectivity traced through
`team_src/magic/chip_top_golden.spice`, whose top line is
`.subckt chip_top VSSA VDDA IBIAS ISS VTUNE CP_OUT I_N Q_P Q_N VDDD REF_IN`.

| # | Pad | Type | Slot | Connects to |
|---|---|---|---|---|
| 1 | **VSSA** | ground | W18 | Chip-wide common ground: `PFD_lib.VSS`, `CP_v1.VSS`, `ibias_gen_v1.VSS`, `DIV2_QUAD_v1.VSS`, `vco_v1.GND`, the perimeter GND ring, both ESD `*_N` diode anodes, and the `REF_IN_PU` tie |
| 2 | **VDDA** | power | W19 | `vco_v1.VDD`, `CP_v1.VDD`, `ibias_gen_v1.VDD`, both ESD `*_P` diode cathodes |
| 3 | **IBIAS** | analog | W20 | → `XR_ESD_IBIAS` (`ppolyf_u`, 16 × 4 µm ballast) → `IBIAS_C` → `ibias_gen_v1.IBIAS`. Secondary-ESD diode pair sits on `IBIAS_C`, core-side of the ballast |
| 4 | **ISS** | analog | W21 | `vco_v1.ISS` — the LC-VCO tail/source node, deliberately **not** grounded on-chip. Secondary-ESD diode pair directly on `ISS`, no ballast |
| 5 | **VTUNE** | analog | W22 | `vco_v1.TUNE` → `XR2` (`ppolyf_u_1k` w1 l15, 15 kΩ) → `cap_bias` → varactor bulk of `XC1`/`XC4` |
| 6 | **CP_OUT** | analog | N01 | `CP_v1.CP_OUT` = `M_PSW` drain = `M_NSW` drain; high-impedance out to the **off-chip** loop filter |
| 7 | **Q_N** | analog | N02 | `DIV2_QUAD_v1.Q_N` ← `XR_SER_QN` (1 kΩ) ← `INVO3_QN` |
| 8 | **I_N** | analog | N03 | `DIV2_QUAD_v1.I_N` ← `XR_SER_IN` (1 kΩ) ← `INVO3_IN` |
| 9 | **Q_P** | analog | N04 | `DIV2_QUAD_v1.Q_P` ← `XR_SER_QP` (1 kΩ) ← `INVO3_QP` |
| 10 | **VSSD** | ground | N05 | Digital-island ground pad; **same on-chip node as VSSA** (one p-substrate, no deep-nwell) → no separate golden port |
| 11 | **VDDD** | power | N06 | `PFD_lib.VDD`, `DIV2_QUAD_v1.VDD`, and the `REF_IN_PD` tie |
| 12 | **REF_IN** | `input_cmos` | N07 | `PFD_lib.REF` |

Internal nets: `UP`/`DOWN` (PFD→CP) · `VGP`/`VGN` (bias→CP mirrors) · `IB_DIV2` (bias→divider
tails) · `VCO_OUTP`/`VCO_OUTN` (VCO→divider CK/CKB) · `IBIAS_C` · **`I_P`**.

**Two supply domains, one ground.** CP + VCO + bias on **VDDA**; PFD + divider on **VDDD**.
Ground is common by construction — all VSS ties the shared p-substrate and there is no
deep-nwell, so VSSA and VSSD are one electrical node. VSSD exists because the padring's
digital-domain BREAK isolates a VDDD-powered island holding VDDD + REF_IN, and Bailey's audit
flagged that island verbatim as *"A01: group 2 missing ground: VDDD REF_IN"*. The split buys
noise and bond-inductance isolation, not DC isolation. **Deep-nwell was considered and
deliberately not adopted** this cycle (new layer, new rules); it is the route to a genuinely
separate substrate return if measured spurs ever demand one.

**Two extraction warnings, both intended**, in `verify_work/chip_top.drc.log`:
`Ports "VDDD" and "REF_IN_PD" are electrically shorted` and
`Ports "VSSA" and "REF_IN_PU" are electrically shorted` — i.e. PD = 1, PU = 0, the weak
pull-down configuration declared in `docs/pins.md` §1.

**Slot BH costs one thing worth stating:** BH has no `vss_fixed` pad, so **VSSA carries the full
~1 nH bond inductance (~31 Ω at 5 GHz)**. BH was chosen over BV for aspect match and a ~241 µm
I/Q haul to the north edge (BV would need 550–900 µm up the portrait west edge).

### 2.3 `I_P` — the pin that was removed, and why it matters most

**`I_P` is no longer a pad.** It is an internal net: `DIV2_QUAD_v1.I_P` → `PFD_lib.FB`. That is
how the PLL loop closes.

The reason is a **loop-breaking RC that no gate in our flow could see**
(`docs/verification.md` §8.10, commit `020852a`). The PFD's FB tapped `I_P` on the **pad side**
of the 1 kΩ `XR_SER_IP`, so the feedback clock reached `dffrnq_1`'s CLK through 1 kΩ into the
pad's **875 fF**: **τ = 912 ps against a 416.7 ps period — 11.4 % swing at 2.4 GHz. The loop
would not have locked.** Removing the pad drops that node to ~23 fF (τ ≈ 23 ps, > 99.9 % swing)
and **touched no signed-off block**.

The reason DRC, LVS and every placement gate passed while the loop was broken is that **the
padring's load lives outside `chip_top`** — it is simply not in anything we extract. That is a
standing limitation, recorded as such.

Two consequences were checked rather than assumed: `Q_P` inherited `I_P`'s N04 pad **and its jog
x** (185.0) — without that it merged into `CP_OUT`'s lane, caught by LVS; and `I_P`'s own text
inside `DIV2_QUAD_v1`'s GDS had to be demoted to datatype 0, or extraction returned 12 ports
against the golden's 11. It remains visible as `text: I_P / layer: 34 / datatype: 0` in the
organizers' own scrape of our GDS — incidentally proving their reader does see datatype-0 text,
which closes a separate open risk about the VSSD label.

### 2.4 ESD

**Primary ESD is the organizer padframe's.** Secondary (CDM) clamps are ours: Bailey —
*"Set the `secondary_esd` to false, and then add it yourself to the circuit and layout."*
`secondary_esd: false` is therefore declared on all seven analog pins, because declaring `true`
would claim protection the GDS does not have.

**Built: 2 of 7** — `IBIAS` (`7391653`, relocated `5eda5b6`) and `ISS` (`914bcdf`, relocated
`7aedc20`). Each is a `diode_pd2nw_03v3` + `diode_nd2ps_03v3` pair (10 × 10 µm, m=4) built from
the organizers' own reference cell geometry, with real VSSA straps; `IBIAS` additionally carries
a `ppolyf_u` 16 × 4 µm series ballast, with the clamp on the **core** side of it. They appear in
`chip_top_golden.spice` and are matched by chip LVS (`diode_nd2ps_03v3 (8→2)`,
`diode_pd2nw_03v3 (8→2)`).

**Whether 2 of 7 is complete depends on an unwritten rule.** `docs/esd-which-pins.md` records
organizer guidance (attributed to `jsmoya`, relayed in conversation) that a secondary clamp is
mandatory only on pins that drive a **gate**, because the failure mode is gate-oxide rupture and
a diffusion terminal has no thin oxide to rupture. Every analog pin was traced to its first
device terminal against `chip_top_golden.spice`; **only IBIAS and I_P reach a gate**, and `I_P`
is no longer a pad. Under that rule the rung is closed.

**That rule is not a written spec.** It is not in the DRM or the Chipathon documentation and has
not been confirmed in writing. If it does not hold, **five more clamps are required** (VTUNE,
CP_OUT, I_N, Q_P, Q_N) — and on the I/Q outputs the sizing question becomes load-bearing,
because the reference geometry is ~564 fF per pin, an **88–118 Ω shunt across 2.4–3.2 GHz**. A
thin-strip diode holds 25 µm of perimeter in 5.4 µm² and would cut that ~40×, but whether
perimeter alone carries the CDM spec is unanswered. This is listed in §6.

### 2.5 The one DRC waiver — W4, and why it is gencell-internal

**Magic DRC on `chip_top` is 0.** KLayout variant-D reports **168 items, all waived, all one
device.** The waiver file `team_src/magic/chip_top.waivers` accepts exactly two rules and no
others:

```
PL.5a_LV
PL.5b_LV
```

These are *"field Poly2 to guard-ring"* violations **internal to the PDK's own `nmoscap_3p3`
gencell**. The arithmetic is exact and was measured, not inferred: a **bare single**
`nmoscap_3p3` unit under variant D shows exactly 2× PL.5a_LV + 2× PL.5b_LV = 4 items;
`vco_varactors` instantiates **42** units; 42 × 4 = **168**. Zero items come from the bussing
(which is M1/M2/M3 only, no poly). The waiver was **tested, not assumed**: no gencell parameter
clears it — `diffcov`/`polycov` at 80/100/60, all four guard-contact flags off, and `guard 0`
all still give 4 per unit. And it is specific to this one device: `DIV2_QUAD_v1`, which contains
MIM caps, poly resistors and dozens of FET gencells, reports **0** KLayout items.

Corroborating evidence that it is a tool discrepancy rather than a layout defect: **Magic on the
`.mag` is gencell-aware and reports 0**; Magic on the flat GDS reports 84 — *the same* PL.5a
items. The chip DRC baseline `team_src/magic/chip_top.drcbase` records `TOTAL 84`,
`RULE 252 Poly spacing to diffusion < 20 (PL.5a)`, **252 error boxes, every one inside
`vco_varactors`**.

**This is a real risk and is stated as one.** Bailey has said failing-DRC designs are likely to
be dropped. 168 items is a genuine KLayout failure count, waived on our own judgement that it is
device-internal to a foundry gencell. Foundry/organizer LVS handles the `nmoscap` from GDS;
Magic cannot. **It is Greg's accepted risk, not a resolved issue.**

### 2.6 How the chip is gated

Six gates, all currently green, ~45 s total (`docs/verification.md` §8.12, measured 2026-08-29):

| Gate | Tool | Runtime | What it asserts |
|---|---|---|---|
| `drc_boxset.tcl` + `drc_delta.py` | Magic | 1.8 s | **the DRC error-box *set*, not the total** — 252 boxes, 0 added / 0 removed |
| `klayout_signoff.py chip_top` | KLayout var-D | 16.9 s | 168 items, all matching the two waived rules |
| `verify_cp.sh chip_top` | Magic + netgen | 14.6 s | extraction → 11 ports, LVS match uniquely, 0 property errors |
| `landing_check.py` | KLayout | 4.4 s | every haul physically **reaches** its DEF pin finger, with margin |
| `lane_conflicts.py` | — | 4.0 s | 0 same-layer lane conflicts |
| `check_placement.py` | KLayout | 3.7 s | placement table consistent |

**The box-set discipline is worth one sentence to a reviewer**, because it is the gate that
would catch a silent regression: `drc list count total` is *not* invariant across a frame
change, and it demonstrably moved 108 → 84 for a fully-understood reason (Magic's techfile maps
`PMNDMY 152/5` to a real `fillblock` layer, so the density markers change how it re-tiles the
error plane) while **all 252 error boxes stayed byte-identical**. The gate compares the box
multiset. A zero delta means the same 252 boxes, not merely the same total.

---

## 3. The 2026-08-31 padframe update — checked, and we are clear

On **2026-08-31 12:34 UTC**, after our last package, Bailey posted a new `A01.def.tgz` on
issue #143:

> *"Discovered the possibility of shorts between the I/O cells of projects that are not A
> blocks. I've created new def files with metal2 obstructions in the areas that could
> potentially short (on the corners). If you have a non A-block layout, please check that there
> is no metal 2 in the affected areas."*

Downloaded (sha256 `de6659ce66351f95…`, 27,791 B) and staged at
`padframe/A01/project_defs_12pin_0831/` (commit `423d148`). The 2026-08-27 package at
`padframe/A01/project_defs_12pin/` is **not** overwritten — every gate on record ran against it.

**The entire delta is one addition to each of two files:**

```
A01_BH.def             + BLOCKAGES 1 ;
                       + - LAYER Metal2 + RECT ( 0 0 ) ( 400 4200 ) ;
                       + END BLOCKAGES
A01_BH_interface.yaml  + metal2_blockages: [[0, 0, 400, 4200]]
```

At `UNITS DISTANCE MICRONS 200` (1 dbu = 0.005 µm), that rectangle is
**Metal2, x 0.000–2.000 µm, y 0.000–21.000 µm — the south-west die corner.** All 14 PIN entries,
the DIEAREA, and the package's other files — the padring DEF (552 COMPONENTS), the padring CFG
and Verilog, the pad map and the selected-variants JSON — are byte-identical to the 08-27
package. Every earlier package (08-21,
08-22, 08-23, 08-27) has **no** `BLOCKAGES` section and no `OBS` in any file; this is the first.

**Result — measured on the GDS, not inferred from the route script.** KLayout over
`gds/chip_top.gds`:

| Layer | Polygons | Extent (µm) | Overlap with the blockage |
|---|---|---|---|
| Metal2 drawn `36/0` | 329 | `(0, 46.36) – (699.345, 550)` | **0 polygons, 0.000000 µm²** |
| Metal2 text/pin `36/10` | 34 | `(237.3, 219.66) – (597.635, 469)` | **0 polygons, 0.000000 µm²** |

**The lowest Metal2 anywhere on the die is y = 46.36 µm** — VSSA's W18 landing plate, painted by
`route_chip.py:332` as `R.box(chip, ly, (36,0), -200.0, -153.64, VSSA_XV, -81.36)` = die
x 0–16, y 46.36–118.64. It clears the blockage's top edge (y = 21.0) by **25.36 µm**. A sweep of
every layer found the **only** geometry anywhere below y = 25 µm on the whole die is the 0/0
boundary rectangle itself. The south-west corner is empty.

**The suite was re-run against the 0831 package (2026-09-01) and is green.**
`landing_check.py` was pointed at `project_defs_12pin_0831/` via its `PADFRAME_ROOT`
environment override; its committed default still targets the 08-27 directory and was not
changed. Results:

| Gate | Result |
|---|---|
| `drc_boxset.tcl` + `drc_delta.py` | **PASS** — TOTAL 84, 252 boxes, **0 added / 0 removed**; GDS blob `3231333c68fa` identical both sides |
| `klayout_signoff.py chip_top` | **PASS** — 84 `PL.5a_LV` + 84 `PL.5b_LV` = 168, all waived, no other rule violated |
| `verify_cp.sh chip_top` | **PASS** — DRC 0, 10 devices, **11 ports**, match uniquely, 0 property errors |
| `landing_check.py` (`PADFRAME_ROOT` → 0831) | **PASS** — all 14 targets, **0 nets failed to reach every finger**; worst-case overlaps unchanged |
| `check_placement.py` | **PASS** — all five blocks reconcile, placement record matches the deliverable |
| `lane_conflicts.py` | **0 net-vs-net same-layer overlaps** — see the note below |

Every one of the 14 landing targets still covers every finger with the same worst-case overlap
as before (e.g. VSSA 6/6 at 1.000 × 9.500 µm, REF_IN 1/1 at 0.380 × 1.000 µm), which is the
expected result given the pin geometry is byte-identical — but it is now a measured result
rather than an inference. **No tracked file changed during the run**; only the gitignored
`team_src/magic/verify_work/` was regenerated.

**One caveat about the sixth item, so the table is not read as more than it is.**
`lane_conflicts.py` is **not a pass/fail gate** — it self-documents as *"Exit is advisory
(printed); NOT the flow — an analysis harness"*, and it exits 0 unconditionally. Its
substantive result is part (1), **net-vs-net same-layer overlap = 0**, which is the short
detector. Part (2) compares each planned segment against the built chip on its own layer and
reports 49 touches; those are each net finding **its own already-built geometry** (several are
explicitly labelled `BUILT -- skipped (would self-detect)`), not conflicts.

**And one caveat that the re-run does not remove:** `blockages:` in the interface YAML is
**still `[]`** — `metal2_blockages` is a *new* key, so any tool reading only `blockages` sees
nothing. None of our gates read either key; the Metal2 clearance in the table above was
established by direct geometry query on the GDS, not by a tool consuming the blockage list.

---

## 4. Verification evidence, per block

**Read this first: no raw simulation output is committed.** `team_src/sim/*/.gitignore` excludes
`*.dat`, `*.raw`, `*.txt`, and a search of `team_src/sim` for `*.raw|*.out|*.csv|*.log` returns
**zero files**. Every measured number below lives as a table in `docs/verification.md`; the
decks that produce it are committed; the waveforms are not. A reviewer can re-run but cannot
re-read the original captures.

### 4.1 `PFD_lib`

Decks: `team_src/xschem/PFD_tb.sch`, `PFD_tb_lead.sch`, `PFD_tb_lag.sch`, `PFD_tb_eqfreq.sch`.
Evidence: `docs/verification.md` §2, §2.2.

Three-region characteristic at 3.3 V, 1 MHz, 100 ns REF↔FB offset, widths at the 1.65 V
threshold in a settled cycle:

| Case | UP width | DOWN width | Reading |
|---|---:|---:|---|
| REF leads 100 ns | **100.5 ns** | 0.48 ns | net UP → pump up |
| FB leads 100 ns | 0.48 ns | **100.5 ns** | net DOWN → pump down |
| Aligned (0°) | 0.50 ns | 0.50 ns | equal reset pulses → locked, net zero |

Library-cell re-verification (§2.2): the raw library PFD's minimum reset pulse was **0.37 ns**,
*narrower* than the custom cell — a worse dead-zone floor — so 2× `inv_1` were added to RSTN,
restoring **0.50 ns**. Corner check: min reset pulse at fast-digital (**ff**) = **0.39 ns**.

> **A margin claim that does not hold up, and is withdrawn here.** The older documents pair
> min-pulse(ff) = 0.39 ns against a CP "switch-close" of 0.02 ns. Those are **not the same
> measurement**: 0.155 ns is typical-corner and 10 pF-loaded, while 0.019 ns is ss-corner and
> voltage-clamped with no load. **The loaded-ss CP steering time — the number that would pair
> apples-to-apples — was never measured.** The qualitative conclusion (the CP engages in tens of
> ps, far inside a 0.39 ns pulse, and §4.2 shows a linear-through-zero transfer) stands. A
> rigorous dead-zone margin does not exist.

Layout-level: **PEX** on `gds/PFD_lib.gds` (`cthresh 0 rthresh 0`) gives REF 3.567 fF vs FB
2.377 fF — REF carries **+1.190 fF (33 %)** more, including a 0.360 fF REF↔`X1_1.Z` coupling
onto a clock input. As a fraction of a 1 MHz reference period a pessimistic ~5 ps skew is
~0.002° static offset, and the driver impedances (a pad vs the CML divider) dominate a 1.2 fF
load mismatch outright. **Not reconciled:** the STA insertion delays in the same run are
REF ≈ 48 fs / FB ≈ 12 fs, two orders of magnitude smaller. The likely explanation (STA is
wire-RC only, excluding pin capacitance) **has not been tested**; the two numbers are plausibly
explained, not reconciled.

### 4.2 `CP_v1` and the PFD→CP interface

Decks: `team_src/xschem/CP_dc_tb.sch`, `CP_tran_tb.sch`, `PFD_CP_tb.sch`. Evidence:
`docs/verification.md` §2.1, §2.6 S5.

`PFD_CP_tb` sweeps static phase error with CP_OUT held at 1.65 V and measures average output
current over a 1 µs cycle at 3.3 V:

| φ (ns) | −200 | −100 | −50 | −20 | **0** | +20 | +50 | +100 | +200 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| avg I_out (µA) | −9.97 | −4.93 | −2.42 | −0.91 | **+0.105** | +1.15 | +2.66 | +5.17 | +10.19 |

- **Linear transfer through zero.** At φ = 200 ns the ideal is 50 µA × 200 n/1 µ = 10 µA against
  a measured 10.19 µA → **I_CP = 50 µA confirmed**, detector gain ≈ 50 nA/ns.
- **Coincident UP+DOWN at lock (φ = 0):** residual **+0.105 µA ≈ 105 fC/cycle**, matching the
  known **+110 fC** injection. The CP handles simultaneous UP+DOWN without latch-up.
- **DC compliance:** 0.32–2.98 V, best match 0.0011 % at 1.50 V.

**Loop sign (KVCO < 0) — verified empirically, and it found a real problem.** REF-lead (φ > 0)
→ UP → CP **sources** → VTUNE **rises**. With KVCO < 0, VTUNE↑ means freq↓ — but a slow VCO
(REF leading) needs freq↑. **The direct UP→UP / DOWN→DOWN wiring drives away from lock.** The
UP/DOWN→CP sense must be inverted (swap UP/DOWN into the CP, or invert the loop-filter
polarity). **This is documented, not fixed:** no cell was rewired, and the inversion is to be
applied when the loop is closed — which, since the filter is off-chip, is a bench action. A
reviewer should treat this as an open design constraint carried into bring-up, not a closed item.

> **The 0.001 % UP/DOWN match figure is superseded and should not be quoted.** It was the
> topology's single-point zero-crossing with *ideal, perfectly equal* current sources. With the
> real `ibias_gen_v1` substituted, the delivered figure is **~0.18 % at TT** — see §4.3.

### 4.3 `ibias_gen_v1`

Decks: `team_src/sim/ibias/*.spice` (9 committed decks). Evidence: `docs/verification.md` §2.6
(S1–S7).

- **Collapse holds (TT):** VGP **50.00 µA**, VGN **49.91 µA**, IB_DIV2 **239.56 µA**; total
  VDDA **839 µA**.
- **Linearity/compliance** (120–360 µA input sweep): VGP gain 5/24, linearity < 0.01 %; VGN and
  IB_DIV2 share an added PMOS-mirror stage → −0.18 % at nominal. Output compliance windows
  (VGP 0.247–3.30 V, VGN and IB_DIV2 0.0–3.053 V) **envelop the CP's measured 0.32–3.00 V window
  with margin**.
- **The real deliverable (S5):** with the generator substituted for the ideal sources, it adds a
  **uniform +0.18 %** to the CP source/sink mismatch across 0.4–2.8 V — exactly the
  50.00-vs-49.91 µA VGN deficit. The ±2 % variation with CP_OUT is the CP's own intrinsic
  output-impedance mismatch, present identically with ideal sources (verified by running the
  ideal baseline in the same environment). The sim CP (`CP_core`) was checked identical in port
  order, device set, connectivity and sizing to the LVS golden.
- **Corners (S6):** CP added mismatch **FF 0.004 % / TT 0.18 % / SS 0.94 %**. These are
  **systematic process-tracking numbers. Random device mismatch is not captured and needs Monte
  Carlo, which has not been run.**
- **PSRR** (VDD 3.0–3.6 V, forced-current reference): VGP **0.003 %/V** (≈ 79 dB), VGN and
  IB_DIV2 **1.16 %/V** (≈ 28 dB).
- **Isolation (S4b):** a separate cascode gate for the divider bias buys **~45 dB at 1 MHz /
  ~33 dB at 1 GHz** of isolation between IB_DIV2 and the CP's VGN versus a shared gate.

**Two mechanisms that must not be conflated.** The 0.18 % *static* mismatch maps to a static
phase offset of t ≈ t_rst · ΔI/I ≈ 0.5 ns × 0.002 ≈ **1 ps** (≈ 0.0004° at a MHz reference) —
negligible. **Supply *ripple* on VGN is separate and dynamic**: at 1.16 %/V it modulates I_CP
within a cycle and injects a reference spur, which the static bound does not cover. VGP at
0.003 %/V is immune, so the exposure is VGN-specific and is a **layout** requirement (quiet
VDDA routing to the CP/bias, away from the digital block).

### 4.4 `vco_v1` — RF characterisation

Decks: `team_src/xschem/vco_tb.sch`, `vco_tank_tb.sch`, `vco_varactor_tb.sch`. Evidence:
`docs/verification.md` §3.1, §3.2.

**f–VTUNE (corrected sweep, `docs/verification.md` §3.2 GAP 1)** — TT, 27 °C, 3.3 V, `tran`
settled 60–80 ns:

| VTUNE (V) | 0.0 | 0.8 | 1.2 | 1.6 | 2.0 | 2.4 | 2.8 | 3.3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| VCO (GHz) | 6.378 | 6.127 | 5.848 | 5.476 | 4.929 | 4.490 | 4.187 | 4.047 |
| ÷2 (GHz) | 3.189 | 3.063 | 2.924 | 2.738 | 2.464 | 2.245 | 2.094 | 2.024 |

- **Native band 4.05–6.38 GHz → ÷2 output 2.02–3.19 GHz.** The 2.4–2.5 GHz ISM target sits
  mid-range with tuning margin both sides, at **VTUNE ≈ 1.95–2.12 V**.
- **Tuning is inverted (KVCO < 0)** — NMOS varactor. **Average KVCO ≈ −706 MHz/V; local KVCO
  near ISM ≈ −1.1 GHz/V.**

> **A superseded measurement, kept visible because it changes loop design.** The original
> 2026-07-30 sweep (`docs/verification.md` §3.1) reported a steep mid-curve region and
> −790 MHz/V near ISM. It **does
> not reproduce** on the same netlist and was a measurement artefact; the corrected curve is
> smooth and monotonic, as a physical varactor C–V must be. The band *edges* agree (4.05–6.38 vs
> 4.11–6.37), which is also the evidence that the container did not drift. **The loop filter
> must be designed to −1.1 GHz/V, not −790 MHz/V**: loop bandwidth ∝ √KVCO → ~18 % higher, and
> phase margin shifts. The filter is off-chip and unstarted, so this is bench-adjustable.

**PVT at the ISM point (VTUNE = 2.15 V):**

| Corner | VCO | ÷2 | Core swing (se / diff) | Total I (buf incl.) | Core I (ISS) |
|---|---:|---:|---|---:|---:|
| TT 27 °C | 4.751 GHz | 2.375 | 2.03 / 4.04 Vpp | 5.04 mA (16.6 mW) | 1.38 mA |
| FF | 4.828 | 2.414 | 2.04 / 4.06 | 5.94 mA | 1.57 mA |
| SS | 4.640 | 2.320 | 2.01 / 4.00 | 4.37 mA | 1.24 mA |
| TT −40 °C | 4.740 | 2.370 | 2.19 / 4.36 | 5.26 mA | 1.36 mA |
| TT +85 °C | 4.764 | 2.382 | 1.88 / 3.75 | 4.92 mA | 1.40 mA |

Frequency spread 4.64–4.83 GHz across process, 4.74–4.76 across temperature — tight. Swing is
near rail-to-rail single-ended at every corner, ample to drive the divider's CML clock directly.
**Startup:** self-starts, ~14 ns latency then builds over 16–24 ns to full amplitude (the 14 ns
is op-point metastability breaking on numeric noise; thermal noise starts it faster in silicon).
**Bench: allow ~30 ns after power-up before reading.** **Power:** VCO core is **1.2–1.6 mA
(~4–5 mW)**; the 16.6 mW / 5 mA figure is core *plus the testbench output buffer* and must not
be quoted as core power.

**Re-simulated as drawn** after the ISS/GND separation (body effect now present):
0.3 V → 6.35 GHz, 1.5 V → 5.53 GHz, 3.0 V → 4.13 GHz — **4.13–6.35 GHz**, consistent with the
recorded band, startup margin not thin.

**Output power / harmonics** (the RF sanity baseline): **−1.55 dBm into 50 Ω, H3 −18.4 dBc.**

**Phase noise: not measurable with this toolchain, and closed on that basis.** ngspice has no
PSS or harmonic-balance engine for autonomous oscillators. The only available route is a long
transient plus FFT, and at 5 GHz that number is dominated by the simulator's numerical noise
floor and timestep jitter rather than device thermal/flicker noise — it would be a figure one
would have to caveat into meaninglessness. **The honest answer to "phase noise if possible" is
that it is not obtainable here.** It needs a PSS-capable tool (Spectre / ADS / AFS) at signoff.

**Inductor:** `vco_inductor_v2`, dual square spiral, D_out = 76 µm, **182 × 84 µm, 1.2 nH**.
Layout DRC-clean in both tools. The 1.2 nH rests on the pi-model plus a **Mohan analytical
cross-check** (`docs/verification.md` §4.1), which confirms it. **The EM extraction is built but
not solved** — see §6.

### 4.5 `DIV2_QUAD_v1` — the RF verification that matters most

Decks: `team_src/xschem/DIV2_CML_probe_tb.sch`, `DIV2_QUAD_tb.sch`,
`DIV2_toggle_probe_tb.sch`; `team_src/sim/div2/div2_sb_TT.spice`. Evidence:
`docs/verification.md` §7, §7.1 and `docs/div2-debug.md`.

**Full-band ÷2 with quadrature — CML core, final sizing (tail 2.4 mA / R 300 Ω):**

| VCO in | ÷2 out (measured) | Quadrature phase (I→Q) |
|---:|---:|---:|
| 4.11 GHz | 2.058 GHz | −90.4° |
| 5.00 GHz | 2.500 GHz | −90.0° |
| 6.37 GHz | 3.185 GHz | −90.0° |

Clean ÷2 across the **entire native VCO band**, consistent −90° quadrature at all three points,
differential swing 0.83–1.4 V.

**Full chain including the output converters, across PVT** (`docs/div2-debug.md`, 2026-08-12
rework):

| Corner | I_P (mVpp) | f (GHz) | Duty | I/Q |
|---|---:|---:|---:|---:|
| TT 27 °C | 141 | 2.500 | 49.4 % | **270.0°** |
| FF | 145 | 2.500 | 49.0 % | **270.0°** |
| SS | 94 | 2.500 | 59.9 % | **270.0°** |
| TT −40 °C | 147 | 2.500 | 48.6 % | **270.0°** |
| TT +85 °C | 106 | 2.500 | 59.0 % | **270.0°** |

**Every corner divides correctly at 2.500 GHz with exact quadrature.** All four outputs track
within 1 mVpp because the four converter chains are programmatically generated and identical, so
I/Q is exact at schematic level; the layout adds the ~2.2 ps static term of §1.4. Amplitude
94–147 mVpp (≈ −20 to −17 dBm into 50 Ω) — ample for a monitor pad whose job is confirming the
ratio and the phase. Duty degrades to ~60 % at SS/hot from slew limiting in the fixed-ratio
driver; cosmetic for a monitor, and a stronger output NMOS was tried and made SS **worse**
(stuck-high, 82 % duty) so 44/16 stands.

**This block was genuinely broken for two weeks, and the fix was architectural.** The CML→CMOS
converter failed repeatedly: it looked rail-to-rail at 6–10 ns and collapsed to 21 mVpp by
16–20 ns — a decaying transient during bias settling that `min/max/avg` hid entirely and only a
waveform dump caught. The root cause was a **class**, not an instance: every fault was an
absolute threshold match between two independently-moving nodes, so resizing fixed one and
exposed the next. The 2026-08-12 rework **removed threshold matching by construction** (a
self-biased inverter with an AC-coupled input) rather than chasing another trip point. The
corner table above is the result. `docs/verification.md` §7.1 still carries the pre-fix
"STILL NON-WORKING" text; it is superseded by `docs/div2-debug.md`'s 2026-08-12 section.

**Settling:** the self-biased chain + CML + pad settle within 16–20 ns at all corners including
SS/85 °C, with the startup `.ic` in place. **Bench: allow ~30 ns after power-up before reading**
I_N/Q_P/Q_N or the I/Q phase.

**Electromigration on the VSS network — a known, quantified violation.** Measured from
`div2_sb_TT.spice`: total VSS return **22.4 mA**; **per-converter VSS 2.96 mA** (through a 0 V
meter split into the IP converter's return). Against those currents:

| Conductor | Width | Current density |
|---|---|---|
| `ib_conv_v1` internal VSS bus (**the root bottleneck**) | 0.6 µm M1 | ~4.9 mA/µm |
| M2 collector plate | 7.5 µm | ~2.3–2.9 mA/µm |
| Per-converter VSS ties | 0.28–0.56 µm | ~5.3–10.6 mA/µm |

**The comparison base must be stated plainly: the open gf180mcuD PDK ships no EM current-density
deck at all** — confirmed by search, there is no EM rule in any DRC or LVS deck. There is
therefore **no PDK limit to cite**, and the figures above are compared against an **industry rule
of thumb for ~0.5 µm Al (~1 mA/µm on M1–M4, ~2 mA/µm on thick M5)**, *not* a value read from the
GF design manual, which was not consulted. On that basis every conductor above is over. The fix
is scoped (widen the `ib_conv_v1` bus to ~3 µm and re-verify the cell and all four instances;
stack the plate on M2/M3/M4 to ~22 µm equivalent; widen the four top ties to ~3 µm; re-gate) and
**deliberately deferred**. It is a reliability item; it does not affect the DRC/LVS/port
sign-off. The real per-layer limits must come from the GF manual before signoff.

A related chip-level EM problem **was** fixed: the DIV2 VDD chip tap was a single 0.28 µm M4
collector carrying all ~22.4 mA at **80 mA/µm**. It is now a **40-point tap on a 3 µm pitch**
across DIV2's two VDD collectors, each a 0.4 µm M4 riser → via4 → 0.44 µm M5 hop to the VDDD
bus. Peak per-wire is now ~0.97 mA/µm on the collector, 1.27–1.40 mA/µm on the riser stubs,
1.9 mA/µm on the VDDD M5 bus. DRC 0, LVS match uniquely, and **DIV2 was not reopened**.

### 4.6 System-level: what has and has not been verified as a loop

**There is no closed-loop PLL simulation. None. This is the single largest gap in the
verification set and it is stated first, not last.** A search of all of `docs/*.md` for
closed-loop, lock-time, loop-bandwidth or system-level simulation returns only the scope
document's fallback ladder. There is **no lock time, no lock range, no loop bandwidth, no phase
margin, no closed-loop jitter or spur number**.

What *does* exist is **block-by-block verification plus one genuine two-block integration**:

1. **PFD → CP (§4.2)** is simulated as a pair, and it produced the linear-through-zero
   characteristic, the confirmed 50 µA I_CP, the 105 fC coincident-UP+DOWN residual, and the
   **loop-sign finding** — which is a system-level result obtained from a two-block sim.
2. **Bias → CP (§4.3)** is simulated as a pair, replacing ideal sources with the real generator.
3. **VCO → divider** is verified by construction rather than by a joint transient: the VCO's
   measured swing (2.03 Vpp single-ended at TT) is checked against the CML clock input's
   requirement, and the divider is separately proven across the VCO's full 4.11–6.37 GHz band.
4. **The VCO's chip-level output loading was estimated, not resized for**: OUT_p route ~494 µm,
   OUT_n ~431 µm on 0.4 µm M3/M4 (~0.08 fF/µm ⇒ ~40 / ~35 fF) plus the divider CML input gate
   (~40–55 fF) ⇒ **~75–95 fF/side**. Against the ~844 fF tank that is Δf ≈ **−4 to −7 %**, moving
   the characterised band to ≈ 3.9–6.05 GHz — still covering the 4.8–5.0 GHz the ISM output
   needs, and retunable via VTUNE with no device change. **This is an estimate, and the VCO was
   not re-simulated with the extracted chip-level load.**
5. **VCO_OUTP/N length match was a real defect and was fixed:** 494.3 vs 431.5 µm (62.8 µm,
   12.7 % skew) → a ~64 µm M4 length-match notch on OUT_n cut the residual to ~1.2 µm (~0.2 %).
   DRC 0, LVS match uniquely.

**The deliberate reason the loop is not closed on-chip.** The loop filter is off-chip by design
(`docs/scope.md` §2, §6): `CP_OUT` leaves the die, the passive R + C1‖C2 sits on the test PCB,
and the filtered voltage returns as `VTUNE`. This removes the large capacitors and the
closed-loop stability risk from the silicon critical path and lets loop dynamics be tuned on the
bench. It also means **closed-loop behaviour is a bench measurement, not a pre-silicon one** —
which is a defensible engineering position, but it is not the same as having verified it.

**Power budget, chip level** (`docs/div2-debug.md`, the 2026-08-12 rework section, "Budget"):
DIV2 + 4 converters **~23 mA average**;
VCO core 1.2–1.6 mA (5 mA only if an on-chip buffer like the testbench's is added); IBIAS
0.84 mA; CP ~0.2 mA; PFD small. **Running total ≈ 25 mA core-only, ≈ 29 mA with a VCO buffer,
against a ~50 mA VDDA budget.**

**Bring-up notes for silicon**, collected so they are not rediscovered on the bench:
allow **~30 ns** after power-up before reading the divider outputs or the I/Q phase (real startup
transients, characterised at all corners); sweep VTUNE by DC source for the open-loop f–VTUNE
curve; verify quadrature as the off-chip I-to-Q phase difference into 50 Ω; design the loop
filter for **KVCO = −1.1 GHz/V**; and **apply the UP/DOWN sense inversion** required by KVCO < 0
(§4.2) when the loop is closed.

---

## 5. Summary table — what is done, per block

| Block | Layout | Magic DRC | KLayout DRC | LVS | Schematic sim | Layout-extracted sim |
|---|---|---|---|---|---|---|
| `PFD_lib` | ✅ | 0 | 0 | ✅ | ✅ 3-region + corners | PEX only (caps); no re-sim |
| `CP_v1` | ✅ | 0 | 0 | ✅ | ✅ DC + transient + PFD pair | ❌ none |
| `ibias_gen_v1` | ✅ | 0 | 0 | ✅ | ✅ S1–S7 + PSRR + corners | ❌ none |
| `DIV2_QUAD_v1` | ✅ | 0 | 0 | ✅ | ✅ full band + PVT + I/Q | ❌ none |
| `vco_v1` | ✅ | 0 | 168 (W4 waiver) | ✅ | ✅ f–VTUNE + PVT + startup | ❌ none; re-sim as *drawn schematic* only |
| `vco_inductor_v2` | ✅ | 0 | 0 | waiver W3 (black box) | analytical (Mohan) | ❌ EM solve deferred |
| ESD clamps (2 of 7) | ✅ | 0 | 0 | ✅ (in `chip_top`) | ❌ none | ❌ none |
| **`chip_top`** | ✅ | 0 | 168 (W4) | ✅ 11 ports | ❌ **no closed-loop sim** | ❌ none |

---

## 6. Gaps — stated without softening

Everything in this list is a real absence. None of it is mitigated by anything in §1–§5.

**System / circuit verification**

1. **No closed-loop PLL simulation exists.** No lock time, no lock range, no loop bandwidth, no
   phase margin, no closed-loop jitter, no closed-loop spur figure. The loop has never been
   simulated as a loop.
2. **No phase noise.** ngspice has no PSS or harmonic-balance engine for autonomous oscillators.
   This is closed as *not obtainable with this toolchain*, not as *done*. It requires a
   PSS-capable simulator at signoff.
3. **The loop-sign inversion is documented but not implemented.** KVCO < 0 means the direct
   UP→UP / DOWN→DOWN wiring drives away from lock. Nothing has been rewired; the correction is
   deferred to the off-chip filter/bench.
4. **No Monte Carlo.** All mismatch figures (FF 0.004 % / TT 0.18 % / SS 0.94 %) are systematic
   process-tracking only. Random device mismatch is not captured anywhere in this design.
5. **No loaded-ss CP steering measurement**, so there is no apples-to-apples dead-zone margin.
6. **The VCO was not re-simulated against the extracted chip-level output load.** The
   −4 to −7 % frequency shift from ~75–95 fF/side is an estimate.
7. **`docs/layout-review-aug14.md`'s "~1.0° I/Q layout offset" appears to use the wrong output
   frequency** (1.25 GHz rather than 2.4–2.5 GHz); the same 2.2 ps is ≈ 1.9–2.0° at the real
   output. Unresolved.

**Physical verification**

8. **PEX exists only for `PFD_lib`.** There is no parasitic extraction for `CP_v1`,
   `DIV2_QUAD_v1`, `vco_v1`, `ibias_gen_v1` or `chip_top`. Consequently there is **no extracted
   CP UP/DOWN current match** and **no extracted mirror ratio** — the CP matching claims are
   schematic-level throughout.
9. **Antenna checking exists only for `PFD_lib`** (LibreLane, 0 violations / 0 diodes). It has
   never been run on the custom blocks or on `chip_top`.
10. **No electromigration deck exists in the open gf180mcuD PDK** — not a missing run, an absent
    rule set. The DIV2 VSS numbers are compared against an industry rule of thumb, not a foundry
    limit, and on that basis **the DIV2 internal VSS network is over-limit and the fix is
    deferred**. Real per-layer limits must come from the GF design manual before signoff.
11. **No ESD simulation of any kind.** No HBM, no CDM. The two built clamps are verified
    structurally (DRC + LVS inside `chip_top`) only.
12. **Only 2 of 7 analog pins carry a secondary ESD clamp**, and whether that is complete rests
    on organizer guidance relayed in conversation that is **not written down anywhere we have
    seen**. If it does not hold, five more clamps are required, and the ~564 fF / 88–118 Ω
    loading question on the I/Q outputs becomes load-bearing.
13. **Density fill is not started.** Chip-level fill is unbuilt; only keep-out markers exist
    (rung 2, `205263a`). Pre-fill, all four measured blocks **fail the minimum-coverage floors** —
    e.g. PFD_lib COMP 21.4 % against DCF.1b ≥ 25 %, CP_v1 COMP 17.9 %, metal layers 0–5 % against
    M1.4–M5.4 ≥ 30 %. These are min-coverage failures (too little metal), never max-density
    violations, and they are the expected pre-fill state of sparse blocks in a large slot — but
    **the fill that resolves them does not exist yet**, and Bailey has said minimum density must
    pass on the final GDS. Fill ownership was raised with the organizers and is unanswered; fill
    also interacts with analog matching, the CP_OUT shield and the inductor keep-out, so it was
    left unstarted rather than half-built.
14. **The W4 waiver (168 KLayout PL.5a_LV/PL.5b_LV items) is an accepted risk, not a resolved
    issue.** The evidence that it is `nmoscap_3p3`-gencell-internal is strong and reproducible
    (§2.5), but it is still a nonzero KLayout count on a flow where failing-DRC designs may be
    dropped.
15. **CP_v1's full dummy set and complete guard rings were deferred** and are not drawn. What is
    drawn is common-centroid with one dummy finger per array end and both guard rings.

**Evidence hygiene**

16. **No raw simulation output is committed** — `team_src/sim/*/.gitignore` excludes `*.dat`,
    `*.raw`, `*.txt`; a search returns zero result files. The numbers exist only as tables in
    `docs/verification.md`. The decks are committed and re-runnable, but the original captures
    cannot be re-read.
17. **No KLayout `.lyrdb` report is on disk for any custom block or for `chip_top`.** The only
    KLayout reports present are from the LibreLane `PFD_lib` run. Every other KLayout result in
    this document is quoted from the project documentation, not from a report file a reviewer can
    open. (The runs are reproducible in ~17 s via `klayout_signoff.py`.)
18. ~~`ibias_gen_v1` has no committed GDS.~~ **WITHDRAWN 2026-09-01 — this was wrong.**
    `gds/ibias_gen_v1.gds` is tracked (added at `4156997`); `git ls-files gds/` lists all
    thirteen GDS files. The claim was inherited from a `docs/tracking.md` §5 line dated
    2026-08-18 that the later commit made stale. Nothing was missing; the gap did not exist.
19. **The inductor EM solve is deferred.** `team_src/sim/ind_em/ind_em.py` (openEMS) builds the
    real gf180mcuD metal4/via4/metal5 stack at true z-heights and the FDTD engine runs
    (32 k cells), but the full 3-D solve is ~50 min because dt is capped by the 0.55 µm metal4
    thickness. There is **no measured Q and no measured SRF** — only L = 1.2 nH from the pi-model
    plus the Mohan cross-check. The fix is known (model the metals as conducting sheets to
    coarsen the z-mesh) and has not been run.
20. ~~The six-gate suite has not been run against the 2026-08-31 package.~~ **CLOSED
    2026-09-01** — run and green against `project_defs_12pin_0831/`, results in §3.
    `landing_check.py`'s committed default `DEF_ROOT` still points at the 08-27 directory by
    design; the 0831 run used its `PADFRAME_ROOT` environment override. **What remains open is
    narrower:** `lane_conflicts.py` is advisory and exits 0 unconditionally, so it is a
    reporting tool rather than a sixth gate, and **no tool in the suite reads the DEF's
    `BLOCKAGES` section or the `metal2_blockages` key at all** — the Metal2 clearance is
    established by direct geometry query, not by an automated check that would catch a future
    blockage landing somewhere we do have metal.

**Process note**

21. **`chip_top.gds` cannot be byte-reproduced.** A rebuild with an unmodified `route_chip.py`
    differs in 216 bytes, every one inside a BGNLIB/BGNSTR timestamp, with bit-identical geometry
    (same bbox, layer histogram, via count, texts). A differing sha256 therefore does **not** mean
    the layout changed. The identity test for this GDS is the **DRC box set**
    (`drc_boxset.tcl` + `drc_delta.py`), not a hash.

---

## 7. What a reviewer should look at first

If time is short, these four things carry the most information:

1. **§2.3 — `I_P` removed from the pin list.** A 912 ps RC on the feedback path would have stopped
   the loop locking, and no gate in our flow could see it because the padring load lives outside
   `chip_top`. It is the most consequential change since the last review.
2. **§4.5 — the divider.** Full-band ÷2 with exact quadrature at every corner is the strongest
   result in the design, and the block was genuinely broken until an architectural fix on
   2026-08-12.
3. **§6 items 1–3 — the loop.** Blocks are verified; the loop is not. Loop sign is a known
   inversion that has not been applied.
4. **§6 items 13–14 — density fill and the W4 waiver.** These are the two items most likely to
   affect whether the design is accepted at final signoff, and neither is resolved.

---

## Cross-references

| Topic | Document |
|---|---|
| **Device declaration — every PDK model, count, where used** | `signoff/devices.md` |
| **Top-level LVS report** (`chip_top`) | `signoff/lvs/lvs.report` |
| **Extracted netlists, chip and per block** | `signoff/lvs/chip_top.lvs.spice`, `signoff/lvs/blocks/` |
| Historical per-block review notes (not superseded) | `docs/layout-review-aug14.md` |
| Full verification log, all measured numbers | `docs/verification.md` |
| Scope freeze, tiers, frequency plan, area | `docs/scope.md` |
| Pin/pad plan | `docs/pins.md` |
| Milestones, block status, area recompute, density | `docs/tracking.md` |
| Padframe seat, per-net routes, pin geometry | `docs/phase8-padframe-plan.md` |
| CP drawing packet (matching, guard rings, shielding) | `docs/cp-layout-packet.md` |
| Divider debug history and the converter class fix | `docs/div2-debug.md` |
| Which analog pins need a secondary ESD clamp | `docs/esd-which-pins.md` |
| LVS config chain validation | `docs/lvs-config-validation.md` |
