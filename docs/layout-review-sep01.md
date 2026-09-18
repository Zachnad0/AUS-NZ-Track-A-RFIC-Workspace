# Layout Review — Team A01, AUS/NZ Track A RFIC

**IEEE SSCS Chipathon 2026 · GF180MCU (gf180mcuD) · issue [#143](https://github.com/sscs-ose/sscs-chipathon-2026/issues/143)**
Prepared 2026-09-01 for **Caglar Ozdag**, at the request of `silicon-vlsi` on issue #143
(2026-09-01 05:59 UTC), and revised the same day against Caglar's four tapeout-priority items.
Repo state: branch `integration`, commit `25a50c0`.

> **SCOPE (2026-09-11, reviewer reframe).** RF-block characterization chip containing the blocks of an integer-N PLL (LC-VCO with varactor tuning, CML divide-by-2 quadrature divider, PFD, charge pump), brought out to pads for open-loop characterization. Closed-loop lock is not demonstrable on this die: the feedback divides by 2 only and the PFD has no usable phase-detection window at the ~2.5 GHz reference that would require. Not a functioning integer-N PLL.

This document supersedes the 2026-08-10 review deck. **`docs/layout-review-aug14.md` is kept
unchanged as the historical record** and is not superseded — it holds the per-block working
notes this document summarises.

**What changed in the 2026-09-01 revision**, against Caglar's four items:

| Item | Outcome |
|---|---|
| **1 — loop sign + closed-loop lock** | §4.6.1–4.6.3. The loop **divides by 2 and nothing else**, so lock needs a 2.4–2.5 GHz reference where the PFD has **no usable phase-detection window**. Loop sign now stated as a concrete net swap; lock arithmetic done from measured I_CP/KVCO/N. **Closed-loop lock is not demonstrable on this die** — this is the most important finding in the document. |
| **2 — DIV2 VSS current density** | §4.5. **Not shipped, but a working fix is now built.** The original M1 widening **fails LVS — it shorts `NS` to `VSS`** (it had been signed off on DRC + bbox alone, neither of which can see a same-layer short). An **M2 plate + 193 via1 stitch** replaces it: 4.93 → **1.000 mA/µm**. The DIV2-level ties (10b), the collector plate (10c) and the **disconnected IP tie (10d)** are now fixed too — every VSS path in the block is at **1.000 mA/µm or better**, DRC 0, LVS 149/9/22 match uniquely, KLayout var-D clean, bbox unchanged. **`chip_top` re-integrated 2026-09-11**, all six gates green. |
| **3 — PEX / re-simulation** | §4.2.1. R+C extracted for **three** blocks: `CP_v1` 38 dev / 265 C / 269 R, `ib_conv_v1` 14 / 70 / 526, `vco_core` 30 / 194 / 208; every device count equals that block's LVS count. Re-simulated: `CP_v1` match moves ≤ 0.076 pp; **`ib_conv_v1` in the DIV2 bench degrades badly — output swing 131 → 25 mVpp, duty +29 %, VSS current −8.4 %** (`signoff/pex/ib_conv_v1/resim.md`); topology, parameters and `uic` excluded, `S2` parks at 862.9 mV, cause open (item 23). `vco_core` re-sim deferred, and core-only would not be meaningful without tank/varactor PEX (item 23a). Full-chip PEX not attempted. |
| **4 — density fill + nmoscap waiver** | §2.5 and §6 item 13. Waiver evidence assembled and an acceptance request drafted; **density fill not started** and its ownership is unresolved. |

**Nothing in this revision changed the shipped GDS.** `gds/chip_top.gds` is byte-identical to
the artifact all six gates were run against.

> **AMENDED 2026-09-17.** That statement still holds for `gds/chip_top.gds`, which is
> untouched. It no longer holds for the whole tree: the item 23 VDD fix (§6 item 23, commit
> `9614947` on branch `item23`) **does** change `gds/ib_conv_v1.gds` and
> `gds/DIV2_QUAD_v1.gds`. Both were re-gated (DRC 0, LVS match uniquely, KLayout variant-D
> clean, bboxes unchanged), but **`chip_top` has NOT been re-integrated against them and is
> therefore stale with respect to its own children.** Re-running `route_chip.py` / the
> `chip_top` merge is a required follow-up before anything is submitted.

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

> **That is the topology. It is not a loop that can lock** — the feedback divides by 2 and
> nothing else, so lock would need a 2.4–2.5 GHz reference into a PFD that has no usable
> phase-detection window at that rate. **See §4.6.1 before reading the loop as functional.**
> Every block is individually verified and measurable; the die is an open-loop test chip.

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

#### 4.2.1 Extracted UP/DOWN match — the CP's headline spec, now measured on the layout

**This is the one place in the design where a matching claim has been lifted off the schematic.**
R+C parasitic extraction of the signed-off `gds/CP_v1.gds` (38 devices, **265 parasitic caps,
269 parasitic resistors**), swept against the *same* testbench on the schematic golden. Both
decks drive `VGP`/`VGN` from **ideal 50 µA** sources, so the comparison isolates the layout
contribution and nothing else. Artifacts: `signoff/pex/`.

| CP_OUT | schematic | **extracted** | delta |
|---:|---:|---:|---:|
| 0.50 V | +1.675 % | +1.721 % | +0.047 pp |
| 1.00 V | +0.717 % | +0.736 % | +0.019 pp |
| **1.50 V** | −0.001 % | **+0.007 %** | +0.008 pp |
| 2.00 V | −0.849 % | −0.848 % | +0.001 pp |
| 2.50 V | −1.635 % | −1.638 % | −0.004 pp |

Over all 49 points of the 0.4–2.8 V compliance window: schematic mean **−0.193 %**, extracted
mean **−0.182 %**, and **extracted − schematic between −0.008 and +0.076 pp, mean +0.012 pp**.

**The layout does not degrade the charge pump's current match.** At the zero crossing the
extracted figure is **+0.007 %** against the schematic's −0.001 %.

Two further results fall out of the same sweep:

- **The ±2.3 % swing across the window is not a layout defect.** It appears in *both* columns,
  independently reproducing `verification.md` §2.6 S5's finding that the ±2 % variation is the
  CP's intrinsic output-impedance mismatch and is present identically with ideal sources.
- **The historical "0.001 %" is now properly retired.** It was a schematic single-point
  zero-crossing with ideal, perfectly equal sources. The extracted-layout equivalent at the same
  point is **0.007 %**.

**What this does not cover, and must not be read into it:** ideal bias, so the real generator's
**uniform +0.18 %** (§4.3) is **additive and still schematic-level**; **TT only**, no corners;
**no Monte Carlo**, so random device mismatch remains uncaptured everywhere in this project; and
**DC only**, so it says nothing about the **+110 fC/cycle charge injection** (§4.2), which is a
dynamic schematic-level flaw that layout does not fix.

**A flow correction this turned up.** `ext2spice rthresh 0` **emits zero resistors on its own** —
it only sets a reporting threshold. Real parasitic R needs `extract do resistance` → `ext2sim` →
`extresist all` → `ext2spice extresist on`. On this cell that is the difference between **27 caps
/ 0 R** and **265 caps / 269 R**. The earlier `PFD_lib` PEX (§4.1) uses the short form and is
therefore **capacitance-only**.

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

**The comparison base must be stated plainly, because it is not a foundry rule.** The open
gf180mcuD PDK **ships no EM current-density deck at all** — confirmed by search, there is no EM
rule in any DRC or LVS deck. There is therefore **no PDK limit to cite**. The figures above are
compared against an **industry rule of thumb for ~0.5 µm Al (~1 mA/µm on M1–M4, ~2 mA/µm on
thick M5)**, hard-coded at `team_src/magic/phase5/em_sizing.py:1–2`. It is **not** a value read
from the GF design manual — that manual **has not been consulted**, and the real per-layer limits
must come from it before signoff. On the rule-of-thumb basis every conductor above is over.

**EM is a wear-out mechanism, not a functional failure.** Nothing here stops the part working at
power-up; it bounds service life at the stated current. That is why it does not gate DRC, LVS or
the port list, and why it is carried as a reliability item rather than a blocker.

### The bus fix: FAILS LVS (NS–VSS short), and NOT in the shipped GDS

**Measured truth first.** `ib_conv_v1.mag` is `magscale 1 10` = **200 internal units/µm** (not the
100 iu/µm that `chip_top.mag`'s `magscale 1 5` uses — mixing the two is an easy and material
error). Measured on the taped-out `gds/DIV2_QUAD_v1.gds`: cell `ib_conv_v1` is 54.860 µm wide,
giving 10,972 iu ÷ 54.860 µm = **200.000 iu/µm** exactly, and the leftmost metal1 edge sits at
−5.300 µm = −1060 iu, the bus spine. **The bus is 120 iu ÷ 200 = 0.60 µm and the density is
2.96 mA ÷ 0.60 µm = 4.93 mA/µm.** The figures recorded in this document and in
`docs/layout-review-aug14.md` are **correct**.

**A fix was proposed here and is NOT valid — it shorts `NS` to `VSS`.** The proposal is
`ib_conv_v1.tcl:117–119`, `hw` 60 → 300, i.e. **0.60 → 3.00 µm**, which would give
**0.987 mA/µm**. Compensation was applied on the **width axis, not the x-ends**: only the bottom
edge threatens the cell bbox (the I3 hseg and the vseg both sit at y = −2430, bottom edge −2490
against a −2600 floor), so those y anchors shift up by `hw − 60`. That reasoning is sound as far
as it goes, and x genuinely needs no compensation (−1300 against a −1360 cell edge). **It guards
the wrong edge.** `hseg`/`vseg` grow **symmetrically**, so the same +240 that pins the bottom
pushes the **top** edge up by 240 — into a live node that was never considered.

Measured at the tail-nfet column, metal1:

```
UNPATCHED   VSS strip   x  -833..3233   y -1170..-1130
            NS riser    x  -190..-114   y  -974..-787      <- 156 iu clear
PATCHED     VSS run     x -1300..5100   y  -974..-930      <- grew up into the gap
            NS riser    x  -190..-114   y  -930..-787      <- re-cut, now abutting
```

Line 117's `y = -1230` with `hw = 300` puts the top edge at **−930** against an NS bottom of
**−974**: a **44 iu overlap**. Built and measured 2026-09-10 against the unpatched cell in the
same `verify_cp.sh` harness, both read from a scratch path:

| Check | unpatched control | `hw` 60 → 300 |
|---|---|---|
| Magic DRC | **0** | **0** — structurally blind, see below |
| bbox | `-1360 -2600 9612 14564` | **identical** — also blind |
| netgen LVS | **match uniquely**, 14 dev / 6 ports / **17 nets** | **DO NOT MATCH**, **16 nets** |
| netgen detail | — | `Net: VSS` vs `Net: NS`, *(no matching net)*; lost `a_100_n800#` |
| Current density | 4.93 mA/µm | 0.987 mA/µm *(unrealised)* |

**Why DRC 0 and an unchanged bbox proved nothing.** metal1 touching metal1 is a legal merge, not
a spacing violation, so Magic DRC cannot report a same-layer short; and the short happens well
inside the cell, so the bbox cannot move. **The two checks this section originally offered as
verification are both incapable of detecting the defect they were used to rule out.** Any future
VSS-widening attempt must gate on LVS, not on DRC and bbox.

**What a valid fix must do:** add conductor without growing the metal1 footprint into `NS` —
either strap the existing M1 run with M2 through via arrays at each `CVSS` tap (no M1 geometry
change, so no clearance problem), or grow M1 asymmetrically into the free space left and below
only (≈420 iu ≈ 2.1 µm, ~1.41 mA/µm — an improvement, short of the ~1.0 target). **The first
of those is now built and green** — see the next section.

The patch is **regenerated into a scratch path on demand** and **must not be applied** — it is
kept only as the reproducible statement of what was tried: `ib_conv_v1.tcl:117–119`, `hw` 60 → 300,
with the I3 `hseg` and the `vseg` y-anchors lifted by `hw − 60`. Earlier revisions of this section
cited `scratchpad/div2-vss-widen.patch` as a retained file; **no such file exists, and none was
ever committed** — `git log --all --diff-filter=A` over that path returns nothing.

### The bus fix, second attempt: M2 plate + via stitching — BUILT, gates green, NOT shipped

**Built 2026-09-10, entirely from the generator.** The plate and its stitching are emitted by
`phase5/ib_conv_v1.tcl`; a rebuild from the `.tcl` alone into an empty directory reproduces the
cell byte-for-byte (md5 `8c3be58202920ce98e11f019ba51b2e1`, timestamp stripped). Nothing is
hand-drawn, and nothing is applied to the repository.

**The approach.** The M1 hw stays **60** — no metal1 geometry moves, which is what shorted `NS`
last time. Conductor is added on **metal2 only**: a staircase plate merged across all four VSS
segments, plus via1 stitching along the whole M1/M2 overlap. Distributed stitching is not
optional — without it the M1 still carries full current between transfer points and the parallel
M2 buys nothing.

| plate row | footprint (iu) | height |
|---|---|---|
| row 1 (S1, spine) | x −1360…4800, y −1614…−1142 | 472 iu = 2.36 µm |
| row 2 (S2) | x −1360…6400, y −2086…−1614 | 472 iu = 2.36 µm |
| row 3 (S3) | x −1360…8000, y −2558…−2086 | 472 iu = 2.36 µm |

Ceiling −1142 holds exactly **100 iu** clear of the `INP`/`INM` M2 riser pads at y −1042 — the
only M2 obstruction anywhere over the bus path, which is otherwise **0 % occupied**. No row
extends right of its own segment's `CVSS` tap x (4800 / 6400 / 8000).

**Per-segment result — every segment sized for the full 2.96 mA:**

| segment | M1 | M2 | total | density | was |
|---|---:|---:|---:|---:|---:|
| S1 (`CVSS(I1)` 4800,−1230) | 0.60 µm | 2.36 µm | **2.96 µm** | **1.000 mA/µm** | 4.93 |
| S2 (`CVSS(I2)` 6400,−1930) | 0.60 | 2.36 | 2.96 | **1.000** | 4.93 |
| S3 (`CVSS(I3)` 8000,−2430) | 0.60 | 2.36 | 2.96 | **1.000** | 4.93 |
| spine | 0.60 | 2.36 | 2.96 | **1.000** | 4.93 |

**via1 count: 193** — S1 48, S2 61, S3 75, spine 9, at 120 iu pitch. The spine column starts
at y −1392, **not** at the VSS port (−1272); see the hierarchy note below.

**Gates, all green.** Magic DRC **0**; `verify_cp.sh` LVS **14 devices / 6 ports / 17 nets,
circuits match uniquely, 0 property errors** — identical to the unpatched control, and the
17-vs-16 net count is the direct refutation of the `NS`–`VSS` short; bbox
`-1360 -2600 9612 14564` **unchanged**; KLayout **variant-D clean, 0 violations** on a scratch
GDS whose cell list is exactly `['ib_conv_v1']`. Both the LVS control and the patched run were
read from a scratch repository root, never from `team_src/magic`.

**The criterion, and its provenance.** **GF180MCU DRM 14.2 Electro-migration, 110 °C
unidirectional column = 1.00 mA/µm for M1–(TopMetal−1)**, as looked up and recorded in
`docs/phase8-padframe-plan.md` §3q. This is a **foundry design-manual figure, not a PDK figure**
— the open PDK ships no EM data at all — and it is the same number `em_sizing.py:1–2` hard-codes.
Via1 in the same table is 0.58 / 0.28 / 0.18 mA per cut at 85 / 110 / 125 °C. VSS current is DC,
so the unidirectional column applies.

**Margins at the other two junction temperatures, recorded as information and not as
requirements:** 1.000 mA/µm passes 85 °C (2.09 mA/µm) with 2.09× margin and is 1.49× over
125 °C (0.67 mA/µm). Reaching the 125 °C figure would need 4.42 µm total, which does **not** fit:
ceiling −1142 to the −2600 cell floor is 1458 iu shared by three stacked rows, so ≈486 iu ≈
2.43 µm of M2 per row is the geometric ceiling in this cell, about 0.98 mA/µm.

**Two caveats, stated plainly.**
1. **1.000 mA/µm is exactly the 110 °C limit — zero margin.** It meets the criterion and does not
   beat it.
2. **The cell's VSS exit is M2-to-M2, so the spine via column is not the current path.** The
   DIV2-level M2 VSS tie overlaps the plate directly on all four instances (1.832 µm² on
   `ib_conv_v1_0`, 0.496 µm² on the other three), and the two merge on flatten. Before the plate,
   the only exit was a **single 52×52 iu via1** per instance at child x −1058…−1006,
   y −1298…−1246, carrying the whole 2.96 mA — **10.6× over** the 0.28 mA/cut figure at 110 °C.
   The plate relieves that as a side effect. The binding width on the exit is now the DIV2-level
   tie itself, ≈80 iu = 0.40 µm, which is item 10b — and item **10d**, since the IP tie
   connected to nothing at all. Both were fixed on 2026-09-11, one day after this section was
   written; see the DIV2-level VSS section in §4.5.

**A defect only the parent could catch.** The first spine via was placed at the VSS port
(y −1272) so that VSS had a via exit. Standalone the cell was **clean — Magic DRC 0, KLayout
variant-D clean, LVS 14/6/17 match uniquely.** Regenerating `DIV2_QUAD_v1` against it returned
**`DIV2_DRC=4`**, one per converter instance:

```
This layer can't abut or partially overlap between subcells
    box -2414 -2028 -2330 -1976      (+3 more, one per instance)
```

`DIV2_QUAD_v1` paints its own via1 over the converter's VSS port at child x −1058…−1006,
y −1298…−1246, and the new via **partially overlapped it by 20 iu in x**. Magic forbids contact
tiles that abut or partly overlap **across a cell boundary** — a restriction that is invisible
at cell level by construction, so no amount of standalone gating could have found it. The via
was redundant anyway: the plate merges M2-to-M2 with the DIV2-level tie, so VSS already exits
without it. Spine now starts at −1392, and the reason is written into the script so it cannot be
re-added.

**Gate rule that follows: after ANY change to a child cell, re-run parent-level Magic DRC.**
Cell-level DRC, LVS and bbox are all structurally blind to cross-boundary contact conflicts,
exactly as DRC and bbox were blind to the `NS` short. Recorded in `docs/tracking.md`.

**Status: built, gated at both levels, and shipped to the repository sources.**
`phase5/ib_conv_v1.tcl`, both `.mag`, `gds/ib_conv_v1.gds` (new) and `gds/DIV2_QUAD_v1.gds` are
updated. **`chip_top` was re-integrated on 2026-09-11** — see the chip_top section below; `route_chip` and the six
gates run once. Note `DIV2_QUAD_v1.mag` changes only in its own timestamp and the four
`use ib_conv_v1` instance stamps: the plate is entirely inside the child, so the parent carries
no new geometry.

### DIV2-level VSS: ties widened, plate grown, IP reconnected — BUILT and SHIPPED 2026-09-11

All three of 10b, 10c and 10d are fixed in one `ib_div2.tcl` change, gated at parent level and
copied into the repository sources. Criterion throughout: **DRM 14.2 @110 °C unidirectional,
1.00 mA/µm for M1–(TopMetal−1)**, per `docs/phase8-padframe-plan.md` §3q.

| path | before | mA/µm | after | mA/µm |
|---|---|---:|---|---:|
| IP `:238` | 1.00 µm **to nothing** | — (substrate) | strip 2.96 µm, risers **3.00 µm** parallel, slab 4.71 µm | **0.987** |
| IN `:275` | 0.28 µm | 10.571 | 2.96 µm | **1.000** |
| QN vseg `:308` | 0.56 µm | 5.286 | 2.96 µm | **1.000** |
| QN strip `:309` | 0.28 µm | 10.571 | 2.96 µm | **1.000** |
| QP vseg `:342` | 0.56 µm | 5.286 | 2.96 µm | **1.000** |
| QP strip `:343` | 0.28 µm | 10.571 | 2.96 µm | **1.000** |
| **collector plate (10c)** | 7.50 µm @ 22.40 mA | 2.987 | **22.40 µm** | **1.000** |

The plate was grown downward 1500 → 4480 iu after checking the corridor across its **full** x
extent: 1 of 69 100-iu columns holds any M2, and that one is the QP vseg, which is VSS and
merges. It was grown fully, not partially.

**Gates (repo copies, both read from the committed GDS):** `ib_conv_v1` DRC 0, 14/6/17 match
uniquely, 0 property errors; `DIV2_QUAD_v1` DRC 0, **149 devices / 9 ports / 22 nets match
uniquely**, 0 property errors; KLayout variant-D **clean**; GDS cell list
`['ib_conv_v1','DIV2_QUAD_v1']`; bbox **237.360 × 174.170 µm unchanged**; and the metal-only
probe returns **plate = VSS port = IP = IN = QN = QP, one net**.

**A short that only extraction could see.** The first IP route put its east riser at
x 23720…23880 running down to y −4150. That crosses the top edge of the **QP instance** and lands
on `ib_conv_v1`'s VDD bus at child y 14430…14464. Top-level `select net` still reported VSS and
VDD as separate nets — it does not descend into child cells — and the geometry check found no
top-level M2 contact. Only LVS caught it: 8 ports / 21 nets, VDD absorbed into VSS. The riser now
starts at y −3800, above the instance boundary at −3836, and reaches the slab through a connector.

**The pairing to remember: `select net` is hierarchy-blind, LVS is substrate-blind.** Item 10d
existed because LVS cannot see a missing supply tie (the p-substrate is one global node); this
short survived a clean `select net` because that command cannot see into an instance. Neither
check alone is sufficient for a supply path, and the gate rule in `docs/tracking.md` now requires
both.

**Residual I/Q asymmetry, recorded rather than forced.** IP is not a mirror of the other three and
cannot be made one: IN, QN and QP are single widened segments, while IP needed a new path — strip,
two parallel risers straddling the foreign net at x 23500…23620 with 100 iu clearance each side,
and a slab. A single 592 iu riser does not fit, bounded by the x 20718…22860 band to the west and
that net to the east, so the two risers carry 440 iu and 160 iu in parallel. The return-path
lengths were already far from symmetric before this pass and remain so: **IN 6.31 µm, QN 65.03 µm,
QP 86.48 µm**. Widths are now uniform at 2.96 µm; lengths are not, and equalising them would need
re-floorplanning, not re-routing.

**`chip_top` RE-INTEGRATED 2026-09-11.** Rebuilt with `chip_merge.py` then `route_chip.py`; the
merged die carries the new blocks — `ib_conv_v1` via1 **45 → 238** (the +193 stitch) and
`DIV2_QUAD_v1` M2 165 → 169 — with the cell set unchanged at 26 and the die still
**1110.000 × 550.000 µm**. All six gates green against the previous run:

| gate | result | previous |
|---|---|---|
| `drc_boxset` + `drc_delta` | TOTAL 84, 252 boxes, **0 ADDED / 0 REMOVED** | same |
| `klayout_signoff` var-D | 84 PL.5a_LV + 84 PL.5b_LV = **168, all waived** | same |
| `verify_cp.sh chip_top` | DRC 0, 10 devices, 11 ports, match uniquely, 0 property errors | same |
| `landing_check` (0831) | **14/14** targets, 0 nets failed | same |
| `check_placement` | all five blocks reconcile | same |
| `lane_conflicts` *(advisory)* | **0** net-vs-net same-layer overlaps | same |

`chip_top.drcbase` was re-captured, as `docs/verification.md` §8.3 requires when a **block**
GDS changes; the old
baseline remains diffable at `d5588b2`. After the re-base, `drc_delta` reports matching
provenance on both sides (blob `57fe1a59455e`, commit `5b523df0`) and a 0/0 delta.

**A new gate was added: metal-only supply connectivity.** KLayout `LayoutToNetlist`, flattened,
metal1–5 + via1–4 only (no diffusion, no well), text attached from all five metals at datatypes
0 and 10. The die resolves to **19 metal-only nets**: VSS is **exactly one** net
(`REF_IN_PU, VSSA, VSSD` — VSSA and VSSD are one on-chip node by design), and the two supply
rails `VDDA` and `REF_IN_PD, VDDD` are each exactly one net and separate from each other by
design. **The identical extraction on the pre-change `chip_top.gds` returns the same 19 nets
with the same names**, so the supply topology is unchanged by the DIV2 work. This gate exists
because LVS cannot see a missing supply tie — see 10d.

**One pre-existing observation, not a regression: `IBIAS` resolves to TWO separate metal nets.**
It is present identically in the pre-change GDS, so it predates this cycle. Under investigation;
not yet written up as a finding.

### DIV2-level VDD: daisy chain removed — BUILT and SHIPPED 2026-09-17; ties and bus NOT widened

Phase B of item 23, the VDD counterpart of the DIV2-level VSS work above. **One of the three
things attempted was built. The other two are blocked by in-plane congestion, and this section
records the measurement that blocks them rather than a partial widening dressed up as a fix.**

#### Measured before touching anything

| item | value | limit | verdict |
|---|---|---|---|
| M4 VDD bus width (port haul y3772–3828, east haul y6472–6528, south haul y−3228…−3172) | **0.280 µm** each | — | — |
| bus mA/µm at the measured 22.4 mA DIV2 supply | **80.0 mA/µm** | 1.00 mA/µm | **80× OVER** |
| M4 needed for 1.00 mA/µm at 22.4 mA | **22.40 µm** | — | — |
| tie metal, all four (M2 abutment) | 0.600 × 0.600 µm | 2.96 µm | **4.93× OVER** |
| via2 cuts per tie | **1** | 11 (2.96 mA ÷ 0.28) | **10.6× OVER** |
| via3 cuts per tie | **1** | 11 | **10.6× OVER** |

#### (a) The east-side daisy chain — FIXED

QP's riser stopped at y3200 and via'd **down onto `ib_conv_v1_0`'s internal M2 trunk**. QP's
2.96 mA entered IP's private 0.60 µm spine at y3200 and left it at y3850, so IP's own trunk
carried **5.92 mA** over that stretch and a hierarchy-blind `select net` saw two separate
top-level fragments joined only through the child. The riser now runs to y3850 and merges with
IP's own riser in the same column (`ipVbus == qpVbus == 23560`); the y3200 M2 pad and its via
are deleted. One line in `phase5/ib_div2.tcl`.

Metal-only probe (the 10b method) on each instance's VDD pin:

| probe | before | after |
|---|---|---|
| `tie_IP` (inst0) | `23500 −4050 23620 3260` — **separate fragment** | `−2148 −4260 23620 6528` |
| `tie_QP` (inst3) | `23500 −4050 23620 3260` — **separate fragment** | `−2148 −4260 23620 6528` |
| `tie_IN` (inst1) | `−2148 −4260 23602 6528` | `−2148 −4260 23620 6528` |
| `tie_QN` (inst2) | `−2148 −4260 23602 6528` | `−2148 −4260 23620 6528` |
| VDD port | `−2148 −4260 23602 6528` | `−2148 −4260 23620 6528` |

All four ties now land on **the same top-level net as the port**. No instance's current crosses
another instance's internal metal.

#### (b) and (c) — NOT BUILT, and why

The target was every tie ≥ 2.96 µm with ≥ 16 via2 + 16 via3 cuts, and the M4 bus widened to
1.00 mA/µm. **The M4 room is not there.** Each required footprint was intersected against all
top-level M4/via3/via4/M5 and all four children's M4 mapped through their instance transforms:

| required footprint | foreign geometry swallowed | verdict |
|---|---|---|
| rail B (latch-B, y−3228…−3172) widened to 22.40 µm | **11 via3 + 6 via4 + 26 M5 + 55 M4 rects** | **shorts VDD to many nets** |
| rail A (latch-A, y3772…3828) widened to 22.40 µm | 2 via3 + 2 M5 + 14 M4 rects | not safe as drawn |
| east haul widened 5.92 µm upward | via3+via4 at (15422,7572) and (9972,6972) — the IBIAS/INP hauls | not safe |
| IP/QP riser widened to 5.92 µm | M5 INM haul y5756…5844 crosses it | needs inter-layer rework |

This is the same conclusion `docs/tracking.md` reached for VSS — *"it is boxed in by bias/latch-B,
no in-plane room… stack the plate on M2+M3+M4"* — and it applies to VDD for the same reason.
The via-cut target has a second, independent blocker: a parent via2 onto a child VDD pin must
land on child M2, and the child's VDD M2 at the IP and IN tie points is the **0.60 µm trunk**
with the 120 iu via2 stitch column running down its middle, so only **one** parent cut fits per
keep-out window. Landing 16 cuts needs the ties moved onto the child's full-width M2 rows
(row A at child y 14344…14464 runs 9420 iu east and is clear), which is a re-route of all four
ties, not a widening.

**What a phase-B2 would have to do:** stack the VDD bus on M2+M3+M4 rather than widen M4
in-plane, and move the four tie landings from the child's trunk onto its horizontal rows. Both
are re-routes. Neither is attempted here.

#### Gates — control run of the unpatched script first

| gate | control | after |
|---|---|---|
| parent-level magic DRC after `drc catchup` | 0 | **0** |
| `verify_cp.sh DIV2_QUAD_v1` | 149 / 9 / 22 match uniquely | **149 / 9 / 22 match uniquely** |
| KLayout variant-D | clean | **clean** |
| bbox | 237.360 × 174.170 µm | **unchanged** |
| GDS cells | `['DIV2_QUAD_v1','ib_conv_v1']` | **unchanged** |

The control reproduces the committed `.mag` byte-for-byte apart from the timestamp.

**`chip_top` IS STILL STALE.** `gds/DIV2_QUAD_v1.gds` changed again here, and `chip_top` has not
been re-integrated against it since `9614947`. `chip_top` and `route_chip.py` were untouched by
instruction. Re-running the merge and route is a required follow-up before anything is
submitted; the same note stands in §6 item 23.

### DIV2-level VDD phase B2: M2+M3 plates + 16-cut row ties — BUILT and SHIPPED 2026-09-18

Commit `a11e51f`. Where phase B removed the daisy chain, B2 addresses the bus itself. It is
worth being explicit about why: **this was never an EM-only problem.** The IR model built from
the PDK's own sheet and via values showed the worst converter losing **302 mV** before its
supply reached the cell.

**Sheet/via values** — `gf180mcuD.tech` extract section, `style ngspice` default variant, the
same style `extresist` used for the committed PEX: metal1–4 **90 mΩ/sq**, metal5 40 mΩ/sq,
via1/2/3/4 **4.5 Ω per cut**. Cross-check: `resim.md`'s 187 squares = 16.8 Ω reproduces.

**Current split** — 22.4 mA total (`i(v_vdd)`, `div2_sb_TT`); four converters at 2.96 mA each
= 11.84 mA, measured per converter as a VSS return. **The CML core is not measured separately**
— no committed `.meas` isolates it — so the core + bias is the **10.56 mA remainder, split
50/50 between latch A and latch B** because they are identical by construction. That split is
an assumption, not a measurement.

#### Bus width, before and after

| path | before | after (M2 + M3 + M4, M4 not credited) |
|---|---:|---|
| port haul y3800 | 0.280 µm | **21.84 µm** |
| east haul y6500 | 0.280 µm | 11.20 µm plated, 0.28 µm over its last 132 iu |
| south haul / rail B | 0.280 µm | **14.24 µm** |
| vertical x−1000 | 0.280 µm | **2.42 µm** (narrowest row; 11.2 µm elsewhere) |
| IP riser x8700 | 0.280 µm | **5.44 µm** |
| E riser x23560 | 0.280 µm | plated to y≈3006 only — see the gap note below |
| every tie | 1 via2 + 1 via3 | **16 via2 + 16 via3**, 112 iu pitch |

Plate area **M2 2646.17 µm², M3 2275.83 µm²**; plate stitch **346 via2 + 346 via3** at 120 iu
pitch; tie cuts **64** (16 × 4). M4 haul geometry unchanged — a via3 lands directly on the bare
56 iu haul, which is DRC-clean, whereas 84 iu landing pads at 120 pitch fail M4.2a spacing.

#### IR drop, before and after

| port → | before | after | factor |
|---|---:|---:|---:|
| IP (inst0) VDD pin | 265.34 mV | **24.30 mV** | 10.9× |
| **QP (inst3) VDD pin** | **302.19 mV** | **36.68 mV** | **8.2×** |
| IN (inst1) VDD pin | 150.00 mV | **3.20 mV** | 46.9× |
| QN (inst2) VDD pin | 246.38 mV | **7.39 mV** | 33.4× |
| CML latch-B feed | 284.82 mV | **7.07 mV** | 40.3× |

Tie via stack: 9.0 Ω → **0.5625 Ω**, i.e. 26.64 mV → **1.67 mV**, and **0.185 mA per cut**
against the 0.28 mA/cut limit.

#### What is not met, and why

The phase-B2 plan study (a read-only scratch document, not committed) predicted ≤ 1.00 mA/µm everywhere and QP ≈ 5 mV. **Neither is reached.** The east
haul's last 132 iu and, more importantly, **the east riser above y≈3006 are unplated**, so they
still sit at **21.1 mA/µm** and carry 30 of QP's 36.68 mV.

The cause is identified, not guessed: the plate generator excludes the child's own VDD metal
from its obstruction set so the plate may overlap it, and that exclusion list was dumped from
`ib_conv_v1` **before** the phase-A M3 plate and stitch were added. Most of the child's
post-phase-A VDD metal is therefore treated as foreign, and the east riser's plate stops at the
inst0 boundary. Refreshing the exclusion to the current child does extend the plate (east riser
M2 258 → 452 µm², M3 340 → 550 µm²) but reintroduces the hierarchy-only rule — 20 errors of
`This layer can't abut or partially overlap between subcells` — because the plate stitch then
lands on the child's via2 stitch column. Fixing that needs the plate stitch to skip the child's
stitch columns; it does **not** need a child change. **That is the phase-B3 item.** The build
committed here is the version that passes every gate.

#### Gates — control run of the unpatched script first

| gate | control | after |
|---|---|---|
| parent-level magic DRC after `drc catchup` | 0 | **0** |
| `verify_cp.sh DIV2_QUAD_v1` | 149 / 9 / 22 match uniquely | **149 / 9 / 22 match uniquely** |
| KLayout variant-D | clean | **clean** |
| bbox | 237.360 × 174.170 µm | **unchanged** |
| metal-only probe, all four tie pins | — | **same top-level net as the VDD port** |

The control reproduces the committed `.mag` byte-for-byte apart from the timestamp.

**Two defects were found by bisecting plates against ties**, as the gate procedure requires:
plate slabs ending flush against foreign metal in x because the spacing margin was applied only
in y; and a clamping bug that classified an obstruction as neither left nor right once expanded
by the margin, which let the x−1000 riser's M3 plate cross the core VSS M3 spine and **short
VDD to VSS** (LVS 8 ports / 21 nets, DO NOT MATCH). Both are fixed.

**`chip_top` IS STILL STALE.** `gds/DIV2_QUAD_v1.gds` changed again here and `chip_top` has not
been re-integrated since `9614947`. `chip_top`, `route_chip.py` and `phase5/ib_conv_v1.tcl` were
untouched by instruction. Re-running the merge and route remains a required follow-up.

### DIV2-level VDD phase B5: east riser and haul tail plated — BUILT and SHIPPED 2026-09-18

Commit `c72f4a4`, closing what B2 left at 21.1 mA/µm. Two generator defects had to be found
first; both are recorded below as invariants because each produced a *clean-DRC, LVS-shorted*
build, which is the expensive failure mode.

#### IR drop, the full progression

Same PDK values throughout (`gf180mcuD.tech` `style ngspice` default: metal1–4 **90 mΩ/sq**,
via **4.5 Ω/cut**) and the same current split (22.4 mA total; 4 × 2.96 mA measured per
converter; the **10.56 mA remainder taken as CML core + bias and split 50/50 between the two
latches, an assumption, not a measurement** — no committed `.meas` isolates the core).

| port → | pre-B2 | B2 `a11e51f` | **B5 `c72f4a4`** | factor |
|---|---:|---:|---:|---:|
| IP (inst0) | 265.34 mV | 24.30 mV | **6.40 mV** | 41.5× |
| **QP (inst3)** | **302.19 mV** | 36.68 mV | **9.93 mV** | **30.4×** |
| IN (inst1) | 150.00 mV | 3.20 mV | **3.20 mV** | 46.9× |
| QN (inst2) | 246.38 mV | 7.39 mV | **7.40 mV** | 33.3× |
| CML latch-B feed | 284.82 mV | 7.07 mV | **7.08 mV** | 40.2× |

Per segment, mA/µm after B5 — the east haul falls from **21.143 to 0.516** and the east riser
upper from **21.143 to 0.970**:

| segment | min width | mA/µm | IR |
|---|---:|---:|---:|
| rail A (four sub-segments) | 11.48–24.64 µm | 0.240–0.976 | 0.48 / 0.10 / 0.67 / 0.87 mV |
| east haul y6500 | 11.48 µm | **0.516** | 1.83 mV |
| E riser upper | 6.10 µm | **0.970** | 1.10 mV |
| rail B | 14.24 µm | 0.371 | 1.35 mV |
| **IP riser x8700** | 5.44 µm | **1.088** | 1.22 mV |
| **vertical x−1000** | 2.42 µm | **3.405** | 4.20 mV |
| **E riser lower** | 0.28 µm | **10.571** | 3.53 mV |

Tie stacks 0.5625 Ω, **0.185 mA/cut** against the 0.28 limit.

**Three segments remain over 1.00 mA/µm**, each a local neck rather than an unplated run, and
together they contribute 8.9 mV:

- **E riser lower, 0.28 µm** — a plate gap where the row-A tie zone and the `eris` M2 notch meet.
- **vertical x−1000, 2.42 µm** — clamped by the core **VSS M3 spine at x −1206…−1094** and the
  VSS_N tie strip; the plate cannot widen without shorting to VSS.
- **IP riser x8700, 5.44 µm** — clamped by neighbouring foreign M4.

#### Generator invariant 1 — the obstruction source must be the PRE-B2 design

Measure plate room against `DIV2_QUAD_v1.mag` at **`c7c2635`**, never against the committed
`.mag`. The committed cell already contains the plates, so they read as foreign and block every
haul; the first B5 attempt produced **zero slabs** for the port haul before this was found. The
child-VDD exclusion is refreshed from the current `ib_conv_v1.mag`, which is what lets the east
riser plate cross the inst0 boundary at all.

#### Generator invariant 2 — no tie box may be emitted inverted

`b2_tie` paints its metal3 pad as `mx1 → s1` and `s2 → mx2` for each skip window. A window that
falls **outside** `[mx1, mx2]` makes one of those boxes inverted, and magic silently normalises
it into metal where the tie was meant to stay clear. For i0 the window `(23472, 23648)` against
`mx1 = 23644` emitted metal3 at **x 23472…23644** — 172 iu west of the pad, straight across the
child's spine. **DRC was 0 and LVS was shorted.**

This is what actually broke B3, and it took a bisect with `verify_cp` as the oracle to find:
erasing **all 46 plate slabs and all 350 stitch cuts** still left VDD merged with IBIAS, so the
plates were never implicated. Clamping the windows to the pad range was **not** sufficient
either, so the tie skip arguments are left at the literals B2 shipped, which are proven, and
`b2_tie` now guards every metal3 box with an explicit `if {$s1 > $mx1}` / `if {$mx2 > $s2}`.

A corollary worth keeping: `what -list`'s label field reports labels found in the selected
*area*, not labels electrically on the net. The committed, LVS-passing B2 shows `IBIAS` in the
VDD selection exactly as the failing B3 did, so **no label- or geometry-based flat probe can
detect this class of short.** Only hierarchical extraction can.

#### Generator invariant 3 — plates must clear the chip-level routing corridors

Added 2026-09-18 (phase B6). The first two invariants are about geometry the generator can see
from inside `DIV2_QUAD_v1`. This one is about geometry it cannot: **`chip_top` routes through
this cell.** `chip_merge.py` places DIV2 at chip offset `(53000, 61000)` dbu and `route_chip.py`
then drives `VCO_OUTP` and `VCO_OUTN` down across the block on metal3 — at DIV2 `x ≈ 0` (CK) and
`x ≈ 13000` (CKB). A VDD plate under either one is **clean at DIV2 level** (magic DRC 0, LVS
match uniquely, KLayout variant-D clean) and shorts VDD to the VCO clocks the moment the block is
merged. Same failure signature as invariant 2 — clean DRC, clean block LVS, broken on
integration — reached by a different route.

Intersecting every top-level `chip_top` rect and contact inside the DIV2 footprint against the
post-B5 VDD-net metal gave **81 hits**. Seventy-nine are VDDD comb-to-haul and intentional. The
two that matter:

| chip_top shape (DIV2 coords) | net | DIV2 VDD plate it lands on | layer |
|---|---|---|---|
| `(-40, 960, 40, 15240)` | `VCO_OUTP` → CK | `(-1028, 3828, 2024, 4920)` | metal3 |
| `(12960, 960, 13040, 15840)` | `VCO_OUTN` → CKB | `(10212, 6528, 15280, 7620)` | metal3 |

So the free-window measurement now folds in a **third** obstruction source, beside the pre-B2
top-level paint and the child-VDD exclusion: every top-level rect and contact of
`gds/chip_top.gds` **at `162faca`**, mapped from chip dbu into DIV2 internal units, on all of
metal1–metal5 and via1–via4, grown by **60 iu**, for **every net except VDDD** — VDDD may be
overlapped, because that is the net the plates are on. `162faca` is recorded in the generator as
the corridor reference; it is the last `chip_top` built before DIV2 acquired plates, so it is the
only corridor map that is not circular.

**Trimmed corridors must be merged, not deleted.** Cutting a slab around a corridor can leave a
run of one or two scan rows. Dropping those rows satisfies M3.2a but pinches the conductor: it
took the west vertical riser down to the bare 56 iu bus over 0.98 µm — **29.4 mA/µm**, and +2.6 mV
on QN. The generator instead narrows a short run window to the intersection with its neighbour,
so the two merge into one longer slab. No sub-56 gap, no metal lost, minimum width on that riser
back to the B5 value of 2.14 µm.

#### What the corridor clamp costs

Model as in phase B5 (metal1–4 90 mΩ/sq, metal5 40 mΩ/sq, via 4.5 Ω/cut, `Δx/W(x)·Rsheet`
integrated along the path), on the B6 VDD-net dump:

| port | pre-B2 mV | B5 mV | B6 mV | corridor cost |
|---|---:|---:|---:|---:|
| IP (inst0) | 265.34 | 6.40 | 6.50 | +0.10 |
| QP (inst3) | 302.19 | 9.93 | **9.99** | +0.06 |
| IN (inst1) | 150.00 | 3.20 | 3.28 | +0.08 |
| QN (inst2) | 246.38 | 7.40 | 7.50 | +0.10 |
| CML latch-B feed | 284.82 | 7.08 | 7.19 | +0.11 |

**QP stays at 9.99 mV, well inside the ~15 mV budget.** The clamp costs at most 0.11 mV anywhere,
because the two corridors cross hauls wide enough to lose 500 iu without changing their sheet
resistance much. Plate area went from `M2 113494304 / M3 96742632` iu² to
`M2 113948016 / M3 96971168` iu²; stitch 343 via2 + 343 via3; 64 tie cuts, 16 per converter.

#### Re-integration passes unpatched

`chip_merge.py` and `route_chip.py` were run **unmodified**, with only their `--out` redirect,
into a scratch path. Extracted `chip_top` subcircuit, three ways:

| build | DIV2 source | `Xvco_v1_0` output node | DIV2 CK / CKB | nets |
|---|---|---|---|---:|
| committed `gds/chip_top.gds` (`162faca`) | pre-plate | `vco_v1_0/OUT_p` | `vco_v1_0/OUT_p` | 24 |
| rebuild | committed B5 DIV2 | **`VDDD`** | **`VDDD`** | 25 |
| rebuild | B6 DIV2 | `vco_v1_0/OUT_p` | `vco_v1_0/OUT_p` | 24 |

The middle row is the phase-C failure. The bottom row is the fix: the rebuild now agrees with the
signed-off deliverable. Chip gates on the B6 re-integration — magic DRC **0**, LVS **10 devices /
11 ports, match uniquely** (25 nets), KLayout variant-D **exactly 168** items, all `PL.5a_LV` /
`PL.5b_LV` and both waived, bbox **1110 × 550 µm** with the `0/0` boundary, all 25
top-cell labels (12 on `36/10`, 4 on `36/0`) byte-identical in name, layer and position to the
committed `chip_top`, and metal2 corner obstruction identical (SW 218.24 µm², NW 219.90 µm²,
SE/NE empty).
`chip_top` is **not** regenerated by this pass.

#### Two harness traps found in B6

Recorded beside the invariants because both produce a WRONG gate result, not an error.

`verify_cp.sh` prefers `gds/<CELL>.gds` over the `.mag`, and on
`chip_top` the GDS path reports DRC 84 / `DO NOT MATCH` **on the committed deliverable itself** —
the gencells only extract correctly through the `.mag`, so the GDS path is diagnostic, not a
gate. And a `gds write` of `DIV2_QUAD_v1` from inside `team_src/magic` silently drops
`ib_conv_v1` (magic resolves it to an abstract), producing a 145-device GDS that fails LVS; the
export has to run from a directory holding `ib_conv_v1.mag` with no abstract in scope.

The working export recipe, for both `DIV2_QUAD_v1` and anything else with a child master:

```
cd <a scratch dir holding the child .mag, and NO <cell>.abstract>
magic -dnull -noconsole -rcfile $PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc
   # drc off ; gds readonly true ; gds rescale false
   # load <CELL> ; select top cell ; gds write <out>.gds
```

Check the result by cell count before trusting it: the good export of `DIV2_QUAD_v1`
contains **two** cells (`DIV2_QUAD_v1` + `ib_conv_v1`), the silently-broken one contains
one. This is the same root cause as the withdrawn reproducibility claim below — the child
master not being on magic's cell search path — in a different disguise.


#### Toolchain invariant — an abstract's labels are checked against the GDS pin geometry

Adopted 2026-09-18 after the VCO tank short. A magic ABSTRACT (`LEFview true` + `GDS_FILE`)
carries port labels that the *parent* routes to, while the real pins live in the streamed GDS.
Nothing in the flow compares the two, so a scaling error in the abstract is invisible: the parent
routes to the abstract's labels, the `.mag` extraction matches by construction, and only a
geometry read of the stream disagrees. `vco_inductor_v2.mag` held its labels **and their metal5
paint** at 1/10 scale for the whole project.

**Rule: whenever a cell is abstracted, assert its label positions against the pin geometry in the
file `GDS_FILE` points at.** `team_src/magic/analysis/vco_tank_proof.py` does this for the VCO
tank and is the pattern to copy. A `FIXED_BBOX` that converts correctly proves nothing about the
labels — it did convert correctly here.

#### Toolchain invariant — hard-coded block coordinates are checked against the stream

Same root cause, one level up. `phase5/route_chip.py` hard-coded the VCO tap positions
(`x 401.8 / 398.0`) rather than deriving them, so when the block's buses moved the taps silently
stopped reaching them — and the only symptom was a single `MT.2a` spacing error, because
`chip_top.mag` is placement-only and the `.mag` LVS cannot see chip routing at all.

**Rule: a coordinate in `route_chip.py` that names a point inside a block is derived from that
block's built GDS, or it is asserted against it.** The taps in the VCO section above are derived;
the rest of the file has not been audited for the same pattern.

#### Gates — control first

The committed generator run through the identical scratch harness passes (9 / 22 match
uniquely), which is what makes the bisect trustworthy.

| gate | control | B5 |
|---|---|---|
| parent magic DRC after `drc catchup` | 0 | **0** |
| `verify_cp.sh DIV2_QUAD_v1` | 149 / 9 / 22 match uniquely | **149 / 9 / 22 match uniquely**, 0 property errors |
| KLayout variant-D | clean | **clean** |
| bbox | 237.360 × 174.170 µm | **unchanged** |
| metal-only probe, four tie pins | — | **same top-level net as the VDD port** |

~~**`chip_top` IS STILL STALE.**~~ **Resolved 2026-09-18.** `chip_top` was re-integrated in
phase C (`75b44d9`) on the B6 `DIV2_QUAD_v1`; `gds/chip_top.gds` and `team_src/magic/chip_top.mag`
are both current. At the time this line was written `chip_top`, `route_chip.py` and
`phase5/ib_conv_v1.tcl` were untouched by instruction.

### Phase C — the chip-level VDDD path, pad to DIV2

Built 2026-09-18, commit `75b44d9`. Phase B fixed DIV2's *internal* VDD; this is the path that
feeds it. Currents as the phase-C planning study (scratch, not tracked) recorded them: **VDDD 22.9 mA** = DIV2 22.4 (measured,
`i(v_vdd)` of `div2_sb_TT`) + PFD ≈ 0.5 (**inferred, not measured** — no bench `.meas` exists for
PFD; it is 2 % of the total so nothing here turns on it). Model as phase B: metal1–4 90 mΩ/sq,
metal5 40 mΩ/sq, 4.5 Ω per cut; limits 1.00 mA/µm and 0.28 mA/cut.

#### Before and after

| segment | before | | | after | | |
|---|--:|--:|--:|--:|--:|--:|
| | geometry | mA/µm or /cut | IR mV | geometry | mA/µm or /cut | IR mV |
| N07 bar + collector | M2 72.28 µm | 0.32 | 0.0 | M2 6 + M3 5 + M4 5 µm | **1.43** | 1.3 |
| pad descent via2 | **1 cut** | **22.90** | **103.1** | **232 cuts** | 0.099 | 0.4 |
| pad descent via3 | **1 cut** | **22.90** | **103.1** | **232 cuts** | 0.099 | 0.4 |
| x367 leg | M4 3.00 µm | 7.63 | 27.5 | M4 11.5 ∥ M5 11.5 µm | **1.38** | 2.4 |
| y305 rail (E+W+jumper) | M4 3.00 µm | 7.63 | 108.6 | M4 3 ∥ **M5 12 µm strap** | **1.72** | 10.9 |
| jumper via4 ×2 | **1 cut each** | **22.90** | **206.1** | **99 + 201 cuts** | 0.114 | in rail |
| x208 leg, unstrappable | M4 3.00 µm | 7.63 | 81.1 | M4 11.5 µm, 46.5 µm | **1.99** | 8.3 |
| x208 leg, strapped | — | — | — | M4 11.5 ∥ M5 11.5, 70.5 µm | **1.38** | 3.9 |
| via4 → M5 bus | **2 cuts** | **11.45** | **51.5** | **221 cuts** | 0.104 | 0.5 |
| M5 bus | 12 µm | **1.91** | 14.7 | 12 µm | **1.91** | 7.7 |
| via4 → feeder | 40 cuts | **0.57** | 2.6 | **203 cuts** | 0.113 | 0.5 |
| feeder / comb | M4 40 × 0.40 µm | **1.43** | 7.0 | M4 36.1 µm | 0.634 | 2.8 |
| landing | abut DIV2's 0.28 µm M4 haul | — | — | **406 via3** onto the M2/M3 plate bands | 0.056 | 0.3 |
| **pad → DIV2 VDD port** | | | **705.7** | | | **39.3** |
| **pad → PFD** | | | **695.6** | | | **35.8** |

**Four single via cuts carried 412 mV of the old 706 mV — 58 % of the drop in four contacts, each
82× over the 0.28 mA/cut limit.** They are gone: the worst via in the chip-level path is now
**0.113 mA/cut**, a 2.5× margin. For scale, DIV2's own internal drop after B6 is 9.99 mV, so the
chip-level path went from 70× worse than the block it feeds to 3.9× worse.

#### What measurement changed against the plan

The phase-C plan assumed a 12 µm M5 strap could run "the pad trunk, both rails and leg A". It
cannot. **No vertical M5 is possible anywhere between the VDDD bus and the y305 rail**, because
VDDA's M5 bus (y197.5–200.5, x60–405) and the GND ring top (y272.5–287.5) both cross every x in
that corridor — same layer, different net. So:

- the **y305 rail** takes the full 12 µm strap, as planned;
- the **x367 leg** takes M5 end to end (measured: *no* M5 at all in core x[350,400] y[300,352]);
- the **x208 leg** is M4-widened 3.00 → 11.50 µm and strapped on M5 only over the **70.5 µm
  window between** VDDA's bus and the ring top, which is the one gap that exists. 46.5 µm of it
  stays M4-only at 1.99 mA/µm.

The plan also claimed the M2/M3 plate bands "carry no child contacts at all". They carry
**three B6 stitch columns**, at core x 59.87, 77.87 and 108.37. The landing skips them by 60 iu,
which is why it is two x-windows and not one.

The VSSD constraint is unchanged and kept: M4 and via4 stop at core x261.2 and resume at 280.0,
so **die x567.5 stays clear** and only M5 bridges it.

#### M5 residuals — the five segments still over 1.00 mA/µm

Every one is an in-plane width limit in a corridor that was *measured* full, not an oversight.

| segment | mA/µm | why it cannot widen in plane |
|---|--:|---|
| x208 leg, unstrapped 46.5 µm | **1.99** | M4 east neighbour at x218.48; M5 blocked by VDDA's bus and the ring top |
| x367 leg | 1.38 | M4 ∥ M5 both 11.5 µm; wider M4 would cross the N08/REF_IN fingers |
| x208 leg, strapped 70.5 µm | 1.38 | same 11.5 µm channel |
| M5 bus | **1.91** | the y[180,205] band holds GND 15 + VDDD 12 + VDDA 3 already; §"Band-fit" |
| N07 collector stack | 1.43 | the pad-finger row is 1 µm tall; M2+M3+M4 = 16 µm equivalent is all there is |

Reaching 1.00 mA/µm on these needs either a wider power band in the floorplan or a second VDDD
pad, both of which are frame changes and out of scope here. **`phase7-routing-plan.md`'s
EM table has been reconciled to the 1.00 mA/µm limit** so these read as "over" there too, rather
than as the "OK" the table used to record for 1.91.

#### Gates

Run on the repo copies after regeneration. The `.mag` path is the real gate; the GDS path is
diagnostic (see "Two harness traps found in B6" above).

| gate | control | phase C |
|---|---|---|
| magic DRC (`.mag`) | 0 | **0** |
| `verify_cp.sh chip_top` (`.mag`) | 10 dev / 11 ports / 25 nets match uniquely | **10 / 11 / 25 match uniquely** |
| KLayout variant-D (GDS) | 168, all `PL.5a_LV`/`PL.5b_LV` | **168, all `PL.5a_LV`/`PL.5b_LV`** |
| top-cell labels | 25 — 12 on `36/10`, 4 on `36/0`, 4 on `34/10`, 3 on `81/10`, 1 each on `42/10` / `46/10` | **identical in name, layer and position** |
| bbox / `0/0` boundary | 1110 × 550 µm, 1 top-cell `0/0` shape | **unchanged** |
| metal2 corners | SW 218.24, NW 219.90 µm², SE/NE empty | **unchanged** |
| XOR vs control | — | 8577 µm², **0 µm² outside the VDDD path** |

**Two figures in this table were corrected on 2026-09-18; neither is a regression.** The label
row previously read "25, 14 on `36/10`" and the boundary row "5 shapes". Both predate
`aa470c3`, which demoted `REF_IN_PD` / `REF_IN_PU` from the port datatype `36/10` to `36/0`
(see the organizer-flow paragraph below) — hence 14 → 12 on `36/10` with 2 of the 4 on `36/0`
coming from that move. The `0/0` count is 1 shape in the **top cell**; the earlier 5 counted
recursively. Re-measured on the committed `gds/chip_top.gds` itself, so the control and any
rebuild compare equal on both rows.

**Organizer-flow LVS (2026-09-18).** Separately from the gates above, the efabless
`mpw_precheck` `run_full_lvs` check was run against `lvs/lvs_config.json`. It **does not pass**,
and it fails identically at `c7eb341`, so nothing here was introduced by item 23. One of its
three causes was ours and is fixed in `aa470c3` — `REF_IN_PD` / `REF_IN_PU` were on the port
datatype 36/10 and extracted as two extra `chip_top` ports shorted to VDDD and VSSA; demoted
to 36/0 the layout now extracts the golden's own 11 ports with no pin shorts. The other two —
the spiral shorting `OUT_p` to `OUT_n` when the GDS is read as geometry, and the standard
cells extracting as `*_06v0` against a PDK netlist that models them as `*_05v0` — are a tool-flow
gap and a PDK inconsistency respectively, neither expressible in the organizer config
schema. Full recipe, run table and evidence: `signoff/lvs/README.md`, §"The organizer flow".

`chip_top.mag` is a **584-byte placement record with no chip-level metal**, and `route_chip.py`
never writes one — so the `.mag` LVS is blind to chip routing by construction and is unchanged by
this phase except in its timestamps. What actually constrains phase C is the KLayout variant-D
DRC on the GDS, the XOR, and the label/bbox/corner comparison; that is the honest reading of the
gate table above.

### WITHDRAWN 2026-09-10: `ib_div2.tcl` DOES reproduce the signed-off `DIV2_QUAD_v1`

**This section previously reported a reproducibility gap. The claim was wrong and is withdrawn in
full.** Rebuilt 2026-09-10 into a scratch path with `ib_conv_v1.mag` on magic's cell search path,
`ib_div2.tcl` produces `47472 x 34834 iu` = **237.360 × 174.170 µm**, bbox
`-65.000 -105.000 172.360 69.170`, two cells (`DIV2_QUAD_v1` + `ib_conv_v1`), `DIV2_DRC=0` — the
signed-off cell exactly. The saved `.mag` is **byte-identical to the committed blob** apart from its
`timestamp` line: md5 `194e336f230ba91145304670736bc340` on both with that line stripped, compared
against `git show origin/main:` and **not** against the working tree, whose `.mag` a Windows
checkout stores CRLF while the blob is LF (`.mag` is not covered by `.gitattributes`, so a naive
working-tree diff reports every line changed).

**Root cause: the child master was not on magic's cell search path.** Rerunning the identical
script from a directory containing no `ib_conv_v1.mag` reproduces the old number to the micron —
`-12592 -19728 34064 7644` = **233.28 × 136.86 µm**, the exact bbox this section used to record —
with magic logging `Cell ib_conv_v1 couldn't be read` and the built cell carrying **zero
children**. All four `getcell ib_conv_v1` calls (`ib_div2.tcl:210,247,283,316`) had dropped
silently. That is the failure mode already documented in `docs/tracking.md` under DIV2: *getcell
silently drops the instance from the .mag*.

**Why the original control did not catch it.** The stash control varied the *script* and held the
environment fixed, so it returned the same wrong bbox and read as confirmation. The variable was
magic's search path, not the sources. This section also argued that children could not be missing
because `ib_conv_v1.mag` is present on disk — presence on disk is not presence on the search path,
and that distinction is the whole of the bug. The inference that the signed-off cell "most likely
carries manual post-build steps that were never captured in the script" is withdrawn; there are no
such steps.

**Consequence:** DIV2 is regenerable from its committed generator. The reproducibility blocker that
this section placed on the EM fix, on the M2 collector plate and on the four top ties **does not
exist**. What remains open on the EM fix is the decision to ship it, nothing else. Every rebuild
above was written to a scratch path outside the repo and compared, never over a committed
artifact.

**Standing rule adopted 2026-09-01 as a result:** never `gds write` over a committed artifact.
Write rebuilds to a scratch path and compare. (This was learned the hard way in this pass —
`gds/DIV2_QUAD_v1.gds` was briefly overwritten with the short rebuild and restored from git; every
signed-off artifact was verified byte-identical to `HEAD` afterwards.)

### The 7.5 µm M2 collector plate cannot be fixed by widening

Confirmed in source at `ib_div2.tcl:177`:
`box values [$xbias-600] [$ybias-2500] [$xbias+6300] [$ybias-1000]` = 1500 iu = **7.50 µm** tall.
Measured layer margins inside `DIV2_QUAD_v1` (bbox −65.000 −105.000 … 172.360 69.170):

| layer | left | bottom | right | top |
|---|---:|---:|---:|---:|
| metal1 | 0.185 | 0.550 | 0.185 | 0.200 |
| **metal2** | 1.970 | **3.860** | 1.970 | 0.500 |
| metal3 | 1.970 | 6.360 | 1.970 | 0.690 |

**Metal2's bottom margin is 3.860 µm against a ~22 µm target.** The plate cannot grow into the
space available; reaching the target needs the **M3/M4 stacking** the fix scope itself proposes,
which is a different and larger change and is **out of scope for this pass**. The four top ties
(0.28 µm at `ib_div2.tcl:275`/`:309`, 0.56 µm at `:308`/`:342`) were left untouched for the same
reason — they are anchored to converter pin positions and share the DIV2 reproducibility blocker.

A related chip-level EM problem **was** fixed: the DIV2 VDD chip tap was a single 0.28 µm M4
collector carrying all ~22.4 mA at **80 mA/µm**. It is now a **40-point tap on a 3 µm pitch**
across DIV2's two VDD collectors, each a 0.4 µm M4 riser → via4 → 0.44 µm M5 hop to the VDDD
bus. Peak per-wire is now ~0.97 mA/µm on the collector, 1.27–1.40 mA/µm on the riser stubs,
1.9 mA/µm on the VDDD M5 bus. DRC 0, LVS match uniquely, and **DIV2 was not reopened**.

### The VCO tank was SHORTED — found and fixed 2026-09-18

Commit `6573181`. **Both VCO outputs were routed into the same inductor terminal and the other
terminal was left unconnected.** OUT_p and OUT_n were one node; the 1.2 nH coil was a floating
stub, not a resonator. This is a layout defect in the deliverable, not an extraction artifact.

#### The defect

`gds/vco_inductor_v2.gds` is a correct two-terminal spiral: metal5 in two polygons joined by a
single metal4 crossunder through 242 via4 (121 per half). Each polygon meets the cell's bottom
edge (y −24.000 µm) in one 8.000 µm pad:

| | cell x | vco_v1 x |
|---|---|---|
| west terminal | −44.000 … −36.000 | 68.000 … 76.000 |
| east terminal | −6.000 … +2.000 | 106.000 … 114.000 |

Terminal pitch **38.000 µm**. `vco_v1` routed both buses to 107.78–108.22 and 111.58–112.02 —
both inside the **east** pad. Measured on the shipped GDS, vco_v1's own metal5 interacted with
the east terminal in 2 shapes and with the west terminal in **0**.

#### The cause: the same 10× in three files

| file | what it held | correct |
|---|---|---|
| `vco_inductor_v2.mag` (the abstract) | PORT1/PORT2 label rects **and their metal5 paint** at 1/10 scale | ×10 |
| `phase5/vco_v1.tcl` | `P1x -800`, `P2x -40`, `Py -480` | `-8000`, `-400`, `-4800` |
| `phase5/route_chip.py` | chip taps at core x **401.8 / 398.0** = vco_v1 local −0.2 / −4.0 | **362.0 / 400.0** |

The abstract's `FIXED_BBOX` was already correct, and so was the committed
`vco_inductor_v2.ext`, whose ports have always read `-8000 -4800` and `-400 -4800`. Only the
label/paint block was wrong, and `vco_v1.tcl` took its bus positions from it rather than from
the `.ext` or the stream.

**Nothing in the gate set could see it.** The `.mag` flow extracts the inductor as an abstract
with no coil, and its label rects sat exactly where `vco_v1.tcl` routed the buses — so PORT1 and
PORT2 matched by construction and OUT_p/OUT_n came out distinct. The abstract world was
self-consistent and wrong. `vco_v1.tcl`'s own header claimed a *"1a geometry proof: each bus
intersects ONLY its own port lead"*; that proof ran against the abstract.

#### Why option (b-ii)

Three options were measured against the coil axis (x 91.000, the midpoint of the two terminals).
vco_core's outputs are 28.000 µm apart centred at 109.935 and the varactors' pins 23.400 µm apart
centred at 99.440 — **different** centres, neither on the axis — so no single instance shift
centres both:

| option | OUT_p | OUT_n | mismatch |
|---|--:|--:|--:|
| (b-i) OUT_p→east, OUT_n→west | 34.85 | 87.32 | 85.9 % |
| **(b-ii) OUT_p→west, OUT_n→east** | 82.72 | 55.85 | **38.8 %** |
| (a) shift vco_core 19 µm west | 53.85 | 68.32 | 23.7 % |
| (c) centre core **and** varactors, buses cross | 55.35 | 55.35 | 0.0 % |

(b-ii) was taken as the best option that keeps every placement and crosses no buses. (c) is the
only one that reaches 0 %, and it is a re-floorplan of `vco_v1` plus crossing differential buses
— out of scope, and it would need the tank re-simulated to justify.

#### Lead resistance, before and after

Lead = core pin → M5 bus → terminal. Leads widened 0.30 → 2.40 µm; every transition on that path
is a 4×4 array at the phase C large-array pitch (V\*.2b 0.36 µm space; magic models the via3/via4
contact at 0.28 µm, so the cut is 56 and the pitch 128 internal units). 48 lead cuts in all.

| | before | after |
|---|--:|--:|
| OUT_p | 21.55 Ω | **2.333 Ω** |
| OUT_n | 14.07 Ω | **1.733 Ω** |
| ΔR | 7.48 Ω | **0.600 Ω** |
| per transition | 4.50 Ω | **0.281 Ω** |

Targets ≤ 2.5 Ω per side, ΔR ≤ 1.5 Ω, ≤ 0.3 Ω per transition: all met. 0.281 Ω of the 0.600 Ω is
structural — `vco_core` presents OUT_p on metal3 and OUT_n on metal4, so OUT_p needs one
transition more, and `vco_core` was not touched. The buses stay 2.000 µm and equal.

Residual imbalance on the whole routed net (taps included): ΔL 27.30 µm, **ΔC 1.68 fF = 0.32 % of
tank C** (519–1287 fF over the 4.05–6.38 GHz band), against an inductor series R of 0.76 Ω.
The "before" column is informational only: in that layout there was no resonator.

#### Chip level — the taps and the retuned match

`route_chip.py`'s two taps move to core x **362.0** and **400.0**, derived from the built
`gds/vco_v1.gds`, and up the bus from y 94.5 to **95.5** so they clear the new via-array pads
(0.07 µm otherwise — M3.2a/M4.2a fire on same-net geometry). Path lengths are
`(ylane − 95.5) + |xv − xd| + (ylane − 110.0)`:

| | before | after |
|---|--:|--:|
| OUT_p | 494.3 µm | 453.5 µm |
| OUT_n (with notch) | 495.5 µm | **453.5 µm** |
| Δ | 0.2 % | **0.0 %** |

The item-3 metal4 notch shrinks from +64 µm to **+21.0 µm** (east 6.0, up 4.5, west 6.0, down
4.5), in a corridor measured clear on metal4 over core x 399–408, y 183–189.5.

A geometry read of the chip stream now gives `vco_v1` **six** ports with OUT_p and OUT_n
separate, and DIV2's CK/CKB on `vco_v1_0/OUT_p` and `vco_v1_0/OUT_n` — two nets where there was
one. The organizer-flow LVS moves with it: nets **52/53 mismatched → 53/53 matched**, device gap
**5 → 2**. It still fails on the standard-cell `05v0`-vs-`06v0` split, which is unrelated
(`signoff/lvs/README.md`).

#### The tank was re-simulated, and the extracted cell does not start

Done 2026-09-18 (`39138d3`, corrected below). The golden control oscillates — **4.859 GHz,
4.211 Vpp, startup 6.211 ns, drift 0.071 %** at VTUNE 2.0 V — so the topology is sound. The
**extracted** netlist does not: the ±10 mV kick decays inside ~3 ns while the core stays
biased at 1.273 mA tail. Every VCO frequency result on record was taken against a netlist that
does not describe this layout, and that is still true.

**`39138d3` attributed this to ≈ 3.8 Ω of tank series R and to the varactor taps. Both were
wrong.** The leads had been taken as the minimum over metal sub-nodes rather than to the
device terminals, and the 21 varactor units per side were combined as `1/Σ(1/R)` — but they
share the tap wire, so they do not parallelise. Solving properly (tank node → all of a
branch's device terminals shorted into one supernode):

| tank branch | Ω | whose metal |
|---|--:|---|
| lead, OUT_p → 30 `vco_core` drain terminals | 4.742 | 0.845 `vco_v1.tcl`, rest `vco_core` |
| lead, OUT_n → 30 `vco_core` drain terminals | 6.530 | 0.523 `vco_v1.tcl`, rest `vco_core` |
| varactor branch, OUT_p → 21 unit terminals | 3.550 | 0.046 tap, rest `vco_varactors` |
| varactor branch, OUT_n → 21 unit terminals | 3.550 | 0.046 tap, rest `vco_varactors` |
| coil (lumped model, not extracted) | 0.760 | — |
| **tank loop total** | **19.131** | **≈ 1.46 Ω of it is ours** |

So the lead widening recorded above is real and met its targets, but it addressed **1.46 Ω of
a 19.1 Ω loop**. About **11 Ω is inside `vco_core`** and **7 Ω inside `vco_varactors`**,
neither of which this change touched.

Three results make that conclusion hard rather than inferred. Scaling all top-level tank
routing R by **×0.01** still gives 0.000 Vpp. Raising the tail current to 1.5 / 2.0 / 3.0× the
bench nominal gives 0.000 Vpp at every point (tails 1.755 / 2.208 / 3.062 mA — the current
does arrive), and so do 4.0 / 5.0 / 6.0×. And widening the two varactor taps 0.30 → 2.40 µm
with 4×4 via arrays — built in scratch, magic DRC 0, `verify_cp` 4/6/11 match uniquely,
KLayout 168 waived, bbox unchanged, `vco_tank_proof` PASS, chip XOR 173.833 µm² with
0.000 µm² outside `vco_v1` — moved the extracted loop by **0.000 Ω** and was therefore **not
landed**. What does start it is a broad reduction: ×0.3 on every parasitic resistor does not
oscillate, **×0.2 does** (1.78 Vpp, 4.40 GHz). Full tables: `verification.md` §3.2,
`signoff/sim/vco/README.md`.

#### A 4.5 Ω tank was built and gated — and still does not start

`vco_core` and `vco_varactors` were rebuilt with **2.40 µm tank buses and 4×4 via arrays on
every bus-level cut**, plus a second via1 on each nfet drain finger. Both cells are built from
0.42 µm metal hung off single 4.5 Ω via cuts, which is where the loss is: an ablation of the
hand model puts via cuts first (−1.95 / −3.25 / −2.49 Ω per branch), bus metal second
(≈ −1.7 Ω each) and the metal1 fingers nowhere (< 0.06 Ω).

Every widening grows **inward**, because three edges are load-bearing: `vco_core`'s metal3 bus
at x −1342 *is* the cell's bbox left edge, its metal4 bus at x 4342 has 0.13 µm to the bbox
right, and `vco_varactors`' metal3 rail bottom at y −482 *is* that cell's bbox bottom. The two
`vco_core` hauls grow in **opposite** directions — metal3 down, metal4 up — because grown the
same way they overlap ≈ 13.9 µm² of metal3-on-metal4, a direct OUT_p-to-OUT_n capacitance
across the tank. Result: **loop 19.131 → 4.523 Ω (4.2×)**, all gates green, all three bboxes
and every port label byte-identical. It still gives **0.000 Vpp at ISS 1.0× and 1.5×**. The
layout is complete in scratch and **was not landed**. Numbers in `verification.md` §3.2.

**A short that magic DRC and the GDS LVS both missed.** An intermediate version of the widened
`vco_varactors` put a 4×4 via2 array's metal3 pad 23 internal units *over* `vco_v1`'s OUT_n
`via_m3m5` pad. Magic DRC reported **0** — same-layer overlap is connectivity, not spacing —
and `verify_cp` on the **GDS** path reported **4 / 6 / 11 match uniquely**, because that flow
flattens past it. Only `verify_cp` on the **`.mag`** path saw it, as **5 ports / 10 nets, DO
NOT MATCH**. Toolchain invariant: **a cell whose children changed is LVS'd on both the `.mag`
and the GDS path**; the GDS path alone cannot prove two tank nets are still distinct.

#### `cap_bias` was the binding term, and the extracted VCO now oscillates

Classifying every resistor in the 4.5 Ω extraction by net and scaling each class alone named
**`cap_bias`** — the smallest class by summed R (292 Ω against GND's 1.26 MΩ) and the only one
that starts the oscillator when relaxed. It is not a bypassed supply: it hangs off TUNE through
a 1 kΩ `ppolyf` and is the varactor bank's differential virtual ground, so what lands in the
tank is its **bank-to-bank** resistance — OUT_p's 21 terminals to OUT_n's 21 — measured at
**8.045 Ω, more than the whole 4.523 Ω tank loop**.

Its geometry is the pattern already fixed on the well side: six **0.38 µm** metal2 gate columns
51.4 µm long, each hung off **one** via2 cut, into a **0.42 µm** metal3 rail. Columns and rail
to 2.40 µm (the rail grown **down**, its top edge held inside the bbox) and 4×4 arrays on the
six cuts: **8.045 → 1.765 Ω**, tank loop unchanged at 4.523 Ω. The extracted VCO then **starts
at nominal ISS for the first time** — 0.975 Vpp at 4.373 GHz, startup 83 ns, settled — with
≥ 18 % ISS margin, and covers the band at 2× nominal. Tables in `verification.md` §3.2.1.

#### …and it still cannot be landed: the organizer flow loses `OUT_p`

`run_full_lvs` on the regenerated chip gives **51 layout nets against 53 source**, where the
committed chip gives **53 / 53**; the layout loses `vco_v1_0/OUT_p` and gains `ISS`. Bisected to
the **`vco_core`** widening (the same chip with the committed `vco_varactors` regresses
identically). Every other gate passes on that layout — DRC 0 everywhere, `verify_cp` 30/5/7,
42/3/4, 4/6/11 on **both** paths, 10/11/25 at chip level, KLayout exactly 168, labels, bbox,
corners, DEF pin landings, and an XOR of 1047.601 µm² with 0.000 µm² outside `vco_v1`.

The merge appears only when `vco_core` is flattened into `chip_top`, which the `.mag` chip LVS
cannot see because `chip_top.mag` carries no chip-level metal. **Third instance of the same
family**: a connectivity change invisible to every local gate. Invariant: **run the organizer
flow before landing any change inside a block**, not only when chip-level routing moves.

### 4.6 System-level: the loop, and the constraint that governs it

> **Read §4.6.1 first.** The feedback path divides by **2 and nothing else**, which fixes the
> required reference at 2.4–2.5 GHz — a rate the PFD cannot detect at. That single fact
> determines what closed-loop verification is and is not meaningful for this die, so it comes
> before the rest.

#### 4.6.1 N = 2: no usable phase-detection window at the required reference

**Traced through `team_src/magic/chip_top_golden.spice`, not inferred:**

```
line 18:   x_pfd_lib       REF_IN I_P UP DOWN VDDD VSSA   PFD_lib
line 35:   .subckt PFD_lib REF FB UP DOWN VDD VSS                 -> FB = I_P
line 21:   x_div2_quad_v1  VCO_OUTP VCO_OUTN IB_DIV2 I_P I_N Q_P Q_N VDDD VSSA
line 103:  .subckt DIV2_QUAD_v1 CK CKB IBIAS I_P I_N Q_P Q_N VDD VSS   -> I_P = VCO / 2
```

`PFD_lib`'s golden contains exactly 2× `dffrnq_1`, 1× `nand2_1`, 2× `inv_1`, 2× `tieh` —
**no divider**. The only division in the loop is the CML ÷2. **N = 2.**

At the ISM operating point the VCO runs 4.8–5.0 GHz, so `PFD.FB` sees **2.4–2.5 GHz** and lock
requires `REF_IN` at the same rate. Against the PFD's measured reset pulse:

| | Value | Source |
|---|---|---|
| Reference period at 2.45 GHz | **408.2 ps** | 1/2.45 GHz; cf. 416.7 ps at 2.4 GHz, `verification.md` §8.10 |
| PFD minimum reset pulse, typ | **500 ps** | `verification.md` §2, `:120`, `:174` |
| PFD minimum reset pulse, ff | **390 ps** | `verification.md` `:176` |
| **reset ÷ period** | **1.22 typ · 0.96 ff** | |

**There is no usable phase-detection window.** At typ the reset pulse is longer than the entire
reference period. At the fast corner it is 96 % of it — the residual window is ~18 ps, smaller
than the reset path's own corner spread, so the detector has no linear region to work in. This
is a *rate* limit, not a marginal-timing question: the PFD is a 5 V standard-cell design
deliberately slowed with 2× `inv_1` to widen its reset pulse (§4.1), and it was characterised at
**1 MHz and 2 MHz** (`verification.md:111`, `:163`) — three orders of magnitude below the
required rate.

**There is no bench workaround.** `I_P → PFD.FB` is an **internal net** — `I_P` came off the pad
list at `020852a` — so no external divider can be inserted into the feedback path. The loop is
hard-wired at N = 2 with no access.

**Consequence, stated plainly: what was taped out is an open-loop test chip.** Every block is
individually measurable and the bench plan in `docs/pins.md` §7 — VTUNE from a DC source, f–VTUNE
swept open-loop, quadrature measured off-chip — is exactly the right procedure for it. Closed-loop
lock is not demonstrable on this die at any reference frequency. **This is not recorded anywhere
else in the repository**; `docs/scope.md` marks "full integer-N PLL loop closure" as Tier-3
stretch, never started, but does not identify the N = 2 consequence.

**For a respin**, the fix is a feedback divide chain that brings FB into the PFD's proven range:
at N = 2450 a 2.45 GHz VCO gives a 1 MHz reference, which is where the PFD is characterised.
That is added silicon, not a wiring change.

#### 4.6.2 Loop sign: the concrete UP/DOWN → CP-switch assignment

**The measurement.** `PFD_CP_tb` (§4.2) swept static phase error with CP_OUT held at 1.65 V and
measured average output current: **−9.97 µA at φ = −200 ns → +10.19 µA at φ = +200 ns**, linear
through **+0.105 µA at φ = 0**. So REF-lead (φ > 0) drives **UP**, the CP **sources** current, and
**VTUNE rises**.

**The conflict.** `verification.md` §3.2 measures **KVCO ≈ −1.1 GHz/V** near ISM — tuning is
inverted, so VTUNE↑ ⇒ f_VCO↓. But REF leading means the feedback edge is late, i.e. the VCO is
**too slow** and needs f↑. The as-built direct wiring therefore drives **away** from lock.

**The assignment required.** In `CP_v1` (`docs/layout-review-sep01.md` §1.2), `M_PSW` is the
source (pull-up) switch gated from the `UP` port via the `M_INVP`/`M_INVN` inverter, and `M_NSW`
is the sink (pull-down) switch on `DOWN`. The correction is to swap which detector output drives
which switch:

| net | as built (`chip_top_golden.spice:18,20`) | **required** |
|---|---|---|
| `PFD_lib.UP` | → `CP_v1.UP` → `M_PSW` (source) | → **`CP_v1.DOWN`** → `M_NSW` (sink) |
| `PFD_lib.DOWN` | → `CP_v1.DOWN` → `M_NSW` (sink) | → **`CP_v1.UP`** → `M_PSW` (source) |

This is a **chip-level net swap between two block ports** — it changes no block, only the routing
between `x_pfd_lib` and `x_cp_v1` inside `chip_top`. Equivalently it can be absorbed off-chip by
an inverting loop-filter stage, at the cost of making the filter active rather than passive.

**Status: documented, NOT implemented.** No net was swapped and no cell rewired. It is moot for
this die because of §4.6.1, and it is recorded so a respin does not rediscover it.

#### 4.6.3 Lock-feasibility arithmetic, and what it rules in and out

Inputs, all measured: **I_CP = 50 µA** (§4.2, confirmed by 10.19 µA at φ = 200 ns against 10.00 µA
ideal), **|KVCO| = 1.1 GHz/V** (`verification.md` §3.2), **N = 2**.

Loop gain constant for a type-II charge-pump PLL, K = I_CP·K_VCO/(2π·N) with K_VCO in rad/s/V:

> K = (50 µA × 2π × 1.1 GHz/V) / (2π × 2) = **2.750 × 10⁴ A/(V·s)**

**The filter values below are PROPOSED. No loop filter exists in the repository** — it is off-chip
and unstarted, and nothing in `docs/` specifies R, C1 or C2. A standard passive lead-lag
(R + C1 in series, both in parallel with C2) with C2 = C1/10 and the crossover at the zero/pole
geometric mean gives a **56.4° phase margin**, and R = ω_c/K:

| proposed f_c | R | C1 | C2 | verdict |
|---|---:|---:|---:|---|
| **1 MHz** | **228 Ω** | **2.31 nF** | **231 pF** | ordinary passives |
| 10 MHz | 2.28 kΩ | 23.1 pF | 2.3 pF | realisable |
| 100 MHz | 22.8 kΩ | 231 fF | 23.1 fF | C2 is **38× smaller** than the 875 fF pad |
| 245 MHz (F_ref/10) | 56.0 kΩ | 38.5 fF | 3.8 fF | C2 is **227× smaller** than the pad |

**What this rules in:** at any sane loop bandwidth the filter is unremarkable — R ≈ 228 Ω,
C1 ≈ 2.31 nF, C2 ≈ 231 pF at 1 MHz are ordinary board components. **The loop filter is not the
obstacle, and the KVCO/I_CP/N combination is not the obstacle.**

**What this rules out:** pushing f_c toward the conventional F_ref/10 for a 2.45 GHz reference
drives C2 below the **875 fF** pad capacitance (`verification.md` §8.10) by two orders of
magnitude, so the filter would be defined by pad and board parasitics rather than by its own
components.

**The binding constraint is neither** — it is §4.6.1. The arithmetic is recorded because it is
what a bench engineer needs for a respin, and because it demonstrates that the loop's *analogue*
design is sound; only the detector rate is not.

---

### 4.6.4 What has and has not been verified as a loop


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
| `CP_v1` | ✅ | 0 | 0 | ✅ | ✅ DC + transient + PFD pair | ✅ **R+C PEX, UP/DOWN match (§4.2.1)** |
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

1. **The loop cannot lock as taped out, and no closed-loop simulation exists.** The feedback
   path divides by **2 and nothing else** (§4.6.1), fixing the required reference at
   2.4–2.5 GHz, where the PFD's reset pulse is **1.22× the period at typ and 0.96× at ff** —
   **no usable phase-detection window**. `I_P → PFD.FB` is internal, so no external divider can
   be inserted; there is no bench workaround. **What was taped out is an open-loop test chip.**
   Separately and consequently: no lock time, no lock range, no loop bandwidth, no phase margin,
   no closed-loop jitter or spur figure — the loop has never been simulated as a loop. A respin
   needs a feedback divide chain (N ≈ 2450 for a 1 MHz reference), which is added silicon.
2. **No phase noise.** ngspice has no PSS or harmonic-balance engine for autonomous oscillators.
   This is closed as *not obtainable with this toolchain*, not as *done*. It requires a
   PSS-capable simulator at signoff.
3. **The loop-sign inversion is specified but not implemented.** KVCO ≈ −1.1 GHz/V means the
   as-built direct UP→UP / DOWN→DOWN wiring drives **away** from lock. §4.6.2 now states the
   required correction concretely — `PFD_lib.UP → CP_v1.DOWN` and `PFD_lib.DOWN → CP_v1.UP`, a
   chip-level net swap between two block ports that changes no block. **Nothing has been
   swapped or rewired.** Moot for this die given item 1, recorded for a respin.
3a. **The loop filter does not exist.** It is off-chip and unstarted; no R/C1/C2 appears anywhere
   in the repository. §4.6.3 proposes values (228 Ω / 2.31 nF / 231 pF at f_c = 1 MHz, 56.4°
   phase margin) from the measured I_CP, KVCO and N — they are **proposed, not designed or
   verified**, and they show the filter is *not* the obstacle.
4. **No Monte Carlo.** All mismatch figures (FF 0.004 % / TT 0.18 % / SS 0.94 %) are systematic
   process-tracking only. Random device mismatch is not captured anywhere in this design.
5. **No loaded-ss CP steering measurement**, so there is no apples-to-apples dead-zone margin.
6. **The VCO was not re-simulated against the extracted chip-level output load.** The
   −4 to −7 % frequency shift from ~75–95 fF/side is an estimate.
7. **`docs/layout-review-aug14.md`'s "~1.0° I/Q layout offset" appears to use the wrong output
   frequency** (1.25 GHz rather than 2.4–2.5 GHz); the same 2.2 ps is ≈ 1.9–2.0° at the real
   output. Unresolved.

**Physical verification**

8. **PEX exists for `CP_v1` (R+C) and `PFD_lib` (capacitance-only), and nothing else.** There
   is no parasitic extraction for `DIV2_QUAD_v1`, `vco_v1`, `ibias_gen_v1` or `chip_top`, and
   full-chip PEX was not attempted. **The CP UP/DOWN current match is no longer
   schematic-level** — see §4.2.1: R+C parasitics move it by at most **0.076 pp**. Two things
   remain schematic-level and are additive to it: the real `ibias_gen_v1`'s **uniform +0.18 %**
   contribution (`verification.md` §2.6 S5), and the mirror ratio. **Correction to the earlier
   record:** the `PFD_lib` PEX is **capacitance-only** — `pex_pfd.tcl` uses `ext2spice rthresh 0`
   without a resistance-extraction pass, which emits zero resistors. Adequate for the REF/FB
   coupling question it was asked; not a full PEX, and it should not be described as one.
9. **Antenna checking exists only for `PFD_lib`** (LibreLane, 0 violations / 0 diodes). It has
   never been run on the custom blocks or on `chip_top`.
10. **No electromigration deck exists in the open gf180mcuD PDK** — not a missing run, an absent
    rule set. The DIV2 VSS numbers are compared against an **industry rule of thumb** hard-coded
    at `em_sizing.py:1–2`. **The GF design manual HAS since been consulted** (2026-08-23):
    **DRM 14.2 Electro-migration**, recorded in `docs/phase8-padframe-plan.md` §3q, gives
    2.09 / 1.00 / 0.67 mA/µm unidirectional for M1–(TopMetal−1) and 0.58 / 0.28 / 0.18 mA per
    via1 cut at 85 / 110 / 125 °C — so `em_sizing.py`'s flat 1.0 is exactly the 110 °C column,
    and the numbers below are a foundry figure, not a guess. On that basis **the DIV2 internal
    VSS network is over-limit**: the bus is 0.60 µm carrying 2.96 mA = **4.93 mA/µm** (measured
    from the taped-out GDS at 200 iu/µm; the recorded figures are correct). EM is a **wear-out**
    mechanism, not a functional failure — it bounds service life, and does not gate DRC or LVS.
    The M1 widening once recorded here (0.60 → 3.00 µm) is **NOT valid: it shorts the
    differential-pair tail node `NS` to `VSS`** — netgen `DO NOT MATCH`, 16 nets against 17. It
    had been recorded as "verified at cell level" on Magic DRC 0 and an unchanged bbox;
    **neither check can see the defect and LVS was never run on it.** A **replacement is built
    and green** — M2 plate + 193 via1 stitch, M1 untouched, **1.000 mA/µm** against the DRM 14.2
    110 °C figure, DRC 0 / LVS 14-6-17 match uniquely / KLayout var-D clean / bbox unchanged
    (§4.5). **Still not shipped:** no committed `.tcl`, `.mag` or `.gds` has been touched.
10a. **WITHDRAWN 2026-09-10 — `ib_div2.tcl` DOES reproduce the signed-off `DIV2_QUAD_v1`.** This
    item previously reported a **233.28 × 136.86 µm** rebuild against the signed-off
    **237.36 × 174.17 µm** (`47472 x 34834 iu`, commit `1ba0838`) and called it a blocker on any
    future DIV2 change. With `ib_conv_v1.mag` on magic's cell search path the rebuild gives
    `47472 x 34834 iu` = **237.360 × 174.170 µm**, and the saved `.mag` is **byte-identical to the
    committed blob** apart from its timestamp. The old figure is what the script produces when the
    child master is absent and all four `getcell ib_conv_v1` calls drop silently; that was
    reproduced deliberately as a control. **There is no reproducibility blocker on DIV2.** Full
    trace in the "WITHDRAWN 2026-09-10" subsection of §4.5.
10b. **The four DIV2-level converter VSS ties are 0.28 / 0.56 µm, carrying 2.96 mA each.** Measured
    2026-09-11: `:238` IP strip 1.00 µm → 2.960 mA/µm; `:275` IN strip 0.28 µm → **10.571**;
    `:308` QN vseg 0.56 µm → **5.286**; `:309` QN strip 0.28 µm → **10.571**; `:342` QP vseg
    0.56 µm → **5.286**; `:343` QP strip 0.28 µm → **10.571**. Against DRM 14.2 @110 °C
    (1.00 mA/µm) each needs **≥ 2.96 µm**. Surveyed for room: **2.96 µm fits on all six
    segments** — the binding neighbours are VDD 2110 iu below the IN strip and a foreign net
    412 iu below the IP strip; everything else has 1110–22938 iu. **RESOLVED 2026-09-11:** all
    six widened to 2.96 µm = 1.000 mA/µm; see the DIV2-level VSS section in §4.5.
10c. **The 7.5 µm M2 collector plate carries the full 22.40 mA = 2.987 mA/µm, 2.99× over.**
    Budget: 4 ties × 2.96 = 11.84 mA plus 10.56 mA of core rails and bias. Reaching 1.00 mA/µm
    needs **22.40 µm = 4480 iu**, a shortfall of 2980 iu on the present 1500 iu.
    **CORRECTED 2026-09-11 — the earlier "cannot be fixed by widening" was based on the wrong
    measurement.** It cited metal2's **3.860 µm margin to the cell boundary**, which does not
    bound the plate: the plate sits at y −6000…−4500 and the question is what lies below *it*.
    Measured, the corridor x 15000…21844, y −19646…−6000 contains **zero M2** — the only rects
    in that x-band are the QP vseg and its sliver, both VSS — giving **≈13,646 iu ≈ 68 µm** of
    free vertical space against a 2980 iu shortfall. M3/M4/M5 cross it (8/11/6 rects, different
    layers, no short) and it holds **zero via1**, so there are no via landings to collide with.
    **M3/M4 stacking is therefore not the only route**; growing the plate downward in-plane
    reaches the target. **RESOLVED 2026-09-11:** grown 1500 → 4480 iu = 22.40 µm = 1.000 mA/µm,
    in-plane, no stacking; see §4.5.
10d. **The IP converter's VSS tie is not connected to anything — its return is the substrate.**
    `ib_div2.tcl:237–238` says "extend the M2 collector plate east under the conv VSS pin", but
    the plate is at y −6000…−4500 and the strip it draws is at **y −2100…−1900**: it takes the
    plate's *x* edge (21900) at the wrong *y*, 2400 iu above it, and lands on nothing.
    `select net` from the collector plate returns md5 `071c460ca41e` and reaches IN, QN and QP;
    from the IP strip it returns `9daf294bf594`, a 399-byte island of one M2 strip, one via1 and
    the child pad. **`ib_conv_v1_0` therefore returns 2.96 mA through the p-substrate**, which
    `7b470be` already records as not a low-Z return.
    **LVS cannot see this.** The p-substrate is a single global node, so netgen reports
    `Xib_conv_v1_0 … VSS` and "match uniquely" whether or not any metal connects it — the same
    class of blindness as Magic DRC to a same-layer short. **Pre-existing:** present in the
    signed-off `DIV2_QUAD_v1`, in `gds/DIV2_QUAD_v1.gds`, and therefore in `chip_top` on
    `origin/main`. Not caused by the `ib_conv_v1` M2 plate, and not hidden by it.
    **RESOLVED 2026-09-11:** a real metal path was built (strip → two parallel risers → slab),
    and the metal-only probe now returns plate = port = all four ties on one net; see §4.5.
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

    **MEASURED ON THE FULL DIE 2026-09-11** (this is Caglar's review-condition item 4(a); §6 has
    no item 4a — its item 4 is Monte Carlo). `run_drc.py --density_only --variant=D` on
    `gds/chip_top.gds` at `98b01a5`, one cell per invocation, 5.0 s, **measure only — no fill was
    generated**. Die **1110.000 × 550.000 µm = 610,500 µm²**, read from the GDS bbox. Percentages
    are the deck's own, quoted from its log; the µm² column is `(floor − measured) × die area`.

    | layer | rule | measured | floor | shortfall | shortfall µm² |
    |---|---|---:|---:|---:|---:|
    | COMP (+dummy) | DCF.1b | **1.622 %** | ≥ 25 % | 23.378 pp | 142,720 |
    | Poly2 | PL.8 | **1.140 %** | ≥ 14 % | 12.860 pp | 78,511 |
    | Metal1 | M1.4 | **0.790 %** | ≥ 30 % | 29.210 pp | 178,325 |
    | Metal2 | M2.4 | **2.238 %** | ≥ 30 % | 27.762 pp | 169,488 |
    | Metal3 | M3.4 | **0.371 %** | ≥ 30 % | 29.629 pp | 180,885 |
    | Metal4 | M4.4 | **1.476 %** | ≥ 30 % | 28.524 pp | 174,138 |
    | Metal5 | M5.4 | **7.835 %** | ≥ 30 % | 22.165 pp | 135,317 |
    | MetalTop | MT.3 | **7.835 %** | ≥ 30 % | 22.165 pp | 135,317 |

    **All eight fire, and all eight are minimum-coverage floors** — too little metal, never a
    max-density violation. **`MT.3` and `M5.4` are the same physical layer**: this is a 5-layer
    metal stack, so MetalTop *is* Metal5, and the deck reports the identical
    7.835071515151516 % for both. Counting them as two distinct shortfalls would double-count
    135,317 µm².

    The block-level 2026-08-15 figures in `docs/tracking.md` §5.2 are **not comparable** to these:
    those are coverage over each block's own bbox, these are over the whole die. The die is mostly
    empty — five blocks in a 1110 × 550 µm slot — which is why every full-die number is far below
    its floor. Metal5 is the highest at 7.8 % because the power ring and buses live there.
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
20a. ~~`ref_audit.py` does not gate the `signoff/*.md` files.~~ **CLOSED 2026-09-01** — it now
    scans `signoff/**/*.md` (29 → 32 files) and keys heading sets by **relative path** rather
    than basename, so the three `README.md` files cannot silently overwrite one another's
    headings. Ambiguous basenames are reported rather than hidden. The extension immediately
    caught a live defect in `signoff/pex/README.md`.

**Process note**

21. **`chip_top.gds` cannot be byte-reproduced.** A rebuild with an unmodified `route_chip.py`
    differs in 216 bytes, every one inside a BGNLIB/BGNSTR timestamp, with bit-identical geometry
    (same bbox, layer histogram, via count, texts). A differing sha256 therefore does **not** mean
    the layout changed. The identity test for this GDS is the **DRC box set**
    (`drc_boxset.tcl` + `drc_delta.py`), not a hash.
22. **The LVS flow runs `extract all` with no `extract unique`, so magic merges same-named
    labels by name — a genuine metal open between two identically-labelled pieces would extract
    as ONE net and still "match uniquely".** `verify_extract.tcl:52` is `extract all` and nothing
    else; no `extract unique` appears anywhere in the flow. Magic's default is to treat two
    disjoint pieces of metal carrying the same label text as the same node. The gate would
    therefore pass a layout in which a net had been cut in half, provided both halves kept the
    label — which is precisely the failure mode of item 10d, only detectable by a different tool.

    **Worked example, and a false alarm worth recording.** The metal-only connectivity gate added
    on 2026-09-11 reported `IBIAS` resolving to **two separate metal nets**, which looked exactly
    like such a cut. It is not one. The two pieces are the **pad side** (x 0.00–36.29,
    y 260.34–304.66, 814 µm², reaching the die edge at x = 0 and the pad label at (0.50, 282.50))
    and the **core side** (x 20.31–339.70, y 268.87–424.20, 1063 µm², spanning `ibias_gen_v1` and
    `CP_v1`). Re-running the extraction with poly2 (30/0) and contact (33/0) added merges them —
    19 nets → 18, `IBIAS` 2 → 1 — because they are the two terminals of
    `XR_ESD_IBIAS  IBIAS_C IBIAS VSSA ppolyf_u r_width=16e-6 r_length=4e-6`, the ESD ballast in
    `chip_top_golden.spice`. `IBIAS` (pad) and `IBIAS_C` (core) are **deliberately different
    nets**; two metal nets is the correct topology. Both pieces read as `IBIAS` only because
    `ibias_gen_v1`'s block port is also named `IBIAS` — a hierarchy label collision that makes the
    metal-only gate noisy and must be read with that in mind.

    **Why it still matters.** The example is benign, but it only came out benign because the two
    pieces were genuinely different nets. Nothing in the gate set would have told us if they had
    not been. This is the third blind spot in the same family: **LVS is substrate-blind** (10d —
    the p-substrate is one global node, so a missing supply tie is invisible), **`select net` is
    hierarchy-blind** (it does not descend into child cells, which is how a riser shorting a
    child's VDD bus passed a clean probe), and **`extract all` is same-name-merge-blind** (this
    item). Only the metal-only connectivity extraction covers the third. Adopting
    `extract unique` is being evaluated separately; it is **not** adopted as of this writing.
23. **The extracted `ib_conv_v1` does not work in the DIV2 bench, and this is unexplained.**
    Re-simulated 2026-09-11 (`signoff/pex/ib_conv_v1/resim.md`). Against the golden-subckt
    reference in the same deck, with the DIV2 core left schematic and only the converters
    swapped: **output swing 131 → 25 mVpp (−80.9 %)**, duty 49.5 → 63.9 % (+29.1 %), per-converter
    VSS current 2.9735 → 2.7249 mA (−8.4 %), total supply +2.7 % with one PEX converter and
    +10.75 % with four. The INV3 output stops reaching the rails — it sits between 2079 mV and
    2677 mV — so rise and fall times are **undefined**, not merely slow. `f_out` stays exactly
    2.500 GHz throughout.

    **It is a settled state, not incomplete settling**: the envelope is flat from 12 ns to
    20 ns in every run, checked because `team_src/sim/div2/README.md` records some corners
    settling at 24–28 ns while the deck stops at 20 ns. With one converter extracted the other
    three are unchanged to within 0.06 %; with all four extracted they degrade identically and
    the I/Q phase returns to 270.0°.

    **The cause has not been isolated and nothing is claimed about it.** Candidates not
    distinguished: the extracted VSS network, the self-bias path through the extracted `RFB`,
    the 20 ns stop, the `uic` start. The measured VSS port-to-internal drop across the 12
    device-terminal nodes is 0.87–33.68 mV average, 58.50 mV peak on the worst node.

    **What this does NOT say.** It does not say the layout is broken. The block passes DRC, LVS
    (14 / 6 / 17 match uniquely, 0 property errors) and KLayout variant-D, and the silicon it
    describes is the same silicon that produced the schematic result. It says an extracted-view
    simulation of it does not reproduce the schematic behaviour in this bench, which is either a
    real layout effect or a bench/extraction artefact, and which of those has not been
    established.

    **Diagnosed 2026-09-11, three checks (`signoff/pex/ib_conv_v1/resim.md`).** (1) Collapsing
    all 526 parasitic resistors by union-find leaves 13 nodes, the same as the golden, and netgen
    reports **"Circuits match uniquely"**; the only single-connection nodes are the four signal
    ports. (2) Every device and passive parameter matches the golden exactly, passives included —
    `cap_mim` `c_width=5u c_length=10u` (100 fF), both `ppolyf_u_1k` at `r_width=2u`
    `r_length=40.04u` / `2u`. (3) The `RFB` self-bias **holds**: `G1` and `S1` sit at 1577.9 mV,
    equal to the digit. The chain departs at **`S2`, the INV3 input, which parks at 862.9 mV
    against a ~1650 mV trip point** and is flat there from 3 ns. **`uic` is excluded** — removing
    it reproduces every figure to the digit. Topology, parameters, `uic` and run length are ruled
    out; whether the extracted parasitics themselves park `S2` low is **not** established.

    **Cause test 2026-09-11: parasitic capacitance is NOT the cause, and that hypothesis is
    refuted.** Parasitic C per node is a small fraction of the gate load already on it —
    `INP` 0.960 fF (9.3 % of gate), `G1` 3.870 (21.1 %), `S1` 6.516 (13.5 %), `S2` 10.568
    (13.5 %), `S3` 9.422 — with Cox from the PDK's own `nfet_03v3_tox = 8e-009`. Two runs settle
    it: removing **all** parasitic C from `G1` and `S1` (12 caps, 10.39 fF) moves the output from
    25 to **39 mVpp**, recovering 14 mVpp of a 106 mVpp deficit; and adding the full extracted
    `S1` capacitance as a single lumped 6.516 fF to the **golden** costs **1 mVpp** (131 → 130).
    Capacitive loading of the self-bias chain accounts for at most an eighth of the degradation.

    **Resistive test 2026-09-11: the cause IS resistive, and it is the VDD network.** Collapsing
    every parasitic resistor (526 of them, 71,066 Ω) while keeping all capacitance recovers the
    output from 25 to **109 mVpp** against the 131 mVpp reference. Bisected by net group, one run
    each: **VDD alone — 17 resistors, 8,344 Ω — recovers 25 → 94 mVpp, 65 % of the deficit**;
    signal + IBIAS recovers 13 mVpp; and **the VSS mesh recovers nothing at all (25 mVpp)**
    despite carrying 476 resistors and 59,904 Ω, because it is a mesh with parallel paths rather
    than a series bottleneck. The VDD port-to-internal drop, never previously measured, reaches
    **165.33 mV average on `VDD.t5` and 200.17 mV peak on `VDD.t4`** — the two supply terminals
    of the **W44 INV3 pfet**, the widest device in the cell — against 33.68 mV average on the
    worst VSS node.

    **Geometry named 2026-09-11; it is real, not an extraction artifact.** The 17 VDD resistors
    are two populations. Three of them (R4 4,010.79, R5 2,510.79, R6 1,177.45 ohm, 7,699 of the
    8,344) are **nwell body paths**: `VDD.t4` is the *bulk* terminal of the W44 pfet, and the
    tech's `resist (nwell,dnwell)/well 1000000` milliohms/sq = 1000 ohm/sq makes R4 exactly
    **4.01 squares of nwell** between the tap and the device body. A bulk path carries no DC
    current, so those are **not** the mechanism. The mechanism is the supply metal: the INV3
    source path `VDD -> n4 -> n2 -> n0 -> t5` totals **60.92 ohm**, which at the measured
    2.7249 mA gives **166.0 mV** against a measured droop of **165.33 mV, agreement to 0.4 %**.
    The geometry behind it: **every device is `nf = 1`**, the INV3 pfet drawn as one 44 um
    finger, contacted over 98.8 % of its length by 186 contacts, so **contacting is not the
    problem**, but strapped by only **0.230 um of metal1**, which at the tech's 90 milliohms/sq
    is 187 squares = 16.8 ohm, fed by a 0.600 um M2 bus. Both populations reproduce from the
    tech sheet values on the drawn geometry, so the extraction is **consistent and real**.

    **STATUS 2026-09-11: cause characterized, not yet fixed.** The cause is **resistive and
    localized to the converter's VDD distribution**. The extracted converter does not reproduce
    schematic behaviour, and **no single resistor group recovers it**: collapsing the INV2 feed
    alone reaches **83 mVpp**, every VDD resistor **94 mVpp**, every parasitic resistor in the
    cell **109 mVpp**, against a **131 mVpp** schematic reference. The degradation reaches
    further back than the output: `S1` swings **534 mVpp** extracted against **1172 mVpp** in the
    schematic.

    A supply-to-bias gain of **4.15x** at `S2` is measured (an ideal 40 mV drop on INV2's VDD
    moves `S2` by 166 mV, 1490.5 to 1324.3 mV) but is **not shown to be the mechanism**: at that
    gain the extracted INV2 droop of 71.8 mV would put `S2` near 1192 mV, whereas it actually
    sits at 862.9 mV, and the same 40 mV drop leaves the schematic output at a full 131 mVpp.

    **The per-stage groups are not additive and that is unexplained.** Collapsing the INV1 feed
    alone gives 19 mVpp and the INV3 feed alone 18 mVpp, both **worse** than the 25 mVpp of the
    untouched extraction, while the INV2 feed alone gives 83; yet the full metal set, which
    contains all three, gives 71, **below INV2 alone**. No model offered for that.

    **Next step, recorded:** a **full VDD-network relayout** of `ib_conv_v1` (M2 plate, source
    straps, nwell taps), which is the largest recoverable share at 94 of the 106 mVpp deficit,
    followed by re-extraction and extracted re-simulation. The residual between that and the
    109 mVpp all-resistor figure is to be characterized then.

    **STATUS 2026-09-17: the VDD relayout is PARTIALLY built and gated. The re-simulation
    deficit is NOT closed and is not claimed to be.** Commit `9614947` on branch `item23`
    changes `gds/ib_conv_v1.gds` and `gds/DIV2_QUAD_v1.gds` (superseding the "no GDS change"
    statement that stood here). What was built, and what it does and does not buy:

    *Survey first (read-only).* The VDD spine carried the full **2.96 mA** per converter
    through a **0.60 um** M2 bus = **4.93 mA/um**, which is the *identical* number VSS had
    before `11d3d7b`. PEX showed the VDD net as **17 parasitic resistors in a zero-loop tree**
    where VSS now has **476 in a 191-loop mesh**, and cumulative port-to-inverter resistance
    **8.5-10.4x** the VSS side, worst at INV3, the largest driver. Every via on the VDD path
    was a **single cut** — 13 via1 against VSS's 198.

    *Built.* An **M3 plate, 472 iu = 2.36 um**, over the M2 spine (0.60 + 2.36 = **2.96 um**
    -> **1.000 mA/um**), **80 via2 stitch cuts** at 120 iu pitch, and the three inverter VDD
    bus taps taken from **1 to 3 via1 cuts**. **METAL2 and METAL1 are untouched** — union-area
    delta exactly **0 iu^2** — so the M1 widening that shorted `NS` to `VSS` is not repeated.

    *A hierarchy-only defect found and fixed en route.* Nine of the 89 candidate stitch cuts
    had to be skipped. `DIV2_QUAD_v1` drops its **own** via2 straight onto this cell's M2
    spine (the top-level M4 branch lands on child metal, not on top-level metal), so a stitch
    cut there is **clean standalone** but fires **8 parent-level errors**, 2 per instance —
    `Via2 spacing < 48 (V2.2a - 2 * V2.3)` and `This layer can't abut or partially overlap
    between subcells`. Same class as the VSS spine-start defect recorded in §4.5, and the
    reason the keep-out windows are written into `phase5/ib_conv_v1.tcl` rather than tuned by
    hand. Parent DRC went 8 -> 0.

    *Measured, R+C PEX on the committed GDS* (14 devices = LVS count, 625 R; VDD net
    **17 -> 116** resistors and **0 -> 33** independent loops):

    | cumulative R, port -> source contact | before | after | change |
    |---|---|---|---|
    | INV1 (pfet 10u) | 35.45 O | **31.84 O** | -10.2 % |
    | INV2 (pfet 26u) | 47.49 O | **41.72 O** | -12.2 % |
    | INV3 (pfet 44u) | 60.91 O | **53.19 O** | -12.7 % |
    | diff-pair X1 / X11 | 29.33 / 31.26 O | 29.33 / 31.26 O | -0.003 O |

    The diff-pair branch is unmoved by construction: its path leaves the spine at the port and
    runs east on the M1 rail, so a spine plate cannot help it.

    **Why this does not close item 23.** The deficit is 25 -> 131 mVpp, and this document
    already records that driving **every** VDD resistor to zero reaches only **94 mVpp**. A
    **10-13 %** resistance reduction is a small fraction of that ceiling, so the expected swing
    recovery is small. **No re-simulation was run** — the session that built this was
    layout-and-gates only. Item 23 stays **open**: what changed is that the EM violation on the
    VDD spine is now fixed (4.93 -> 1.000 mA/um) and the network is a mesh instead of a tree.
    The source straps and nwell taps named in the original next-step are **still not rebuilt**,
    and the 10 device-level via1 that carry each stage's current are **still single-cut** —
    they have no M1/M2 enclosure room, and widening them needs new M1. Closing item 23 needs
    that relayout plus an extracted re-simulation, in that order.

    **Closing status, 2026-09-18.** The EM and IR work on item 23 is complete across all
    three levels and is recorded in four commits: `9614947` (converter VDD spine,
    4.93 → 1.000 mA/µm), `c72f4a4` (DIV2-level VDD plates and tie arrays, worst converter
    port 302.19 → 9.93 mV), `b597ca2` (the same plates kept out of the chip-level routing
    corridors, 9.93 → 9.99 mV, and re-integration restored), and `75b44d9` (the chip-level
    pad → DIV2 path, 705.7 → 39.3 mV, worst via 22.90 → 0.113 mA/cut). End to end the pad
    to the worst converter VDD pin is **≈ 1008 mV → ≈ 49 mV**. **Item 23 nonetheless stays
    open**, for the reason given above and unchanged by any of it: the 25 → 131 mVpp swing
    deficit is bounded at 94 mVpp even with every VDD resistor driven to zero, the
    device-level via1 are still single-cut for want of M1 enclosure room, and **no
    re-simulation has been run** on any of the four commits. What closes item 23 is the
    device-level relayout plus an extracted re-sim, in that order — not more supply metal.

    *Per-stage current caveat.* The 3-cut target on the bus taps is `ceil(0.74 / 0.28)`, where
    0.74 mA is the **flat average** 2.96/4. The per-stage split is not measured and **no peak
    current measurement exists anywhere in the repo** — every `.meas` in `team_src/sim/` and
    `signoff/pex/ib_conv_v1/decks/` is `AVG`. INV3 (44u/16u) certainly draws more than its
    quarter, so the target is provisional and every mA/um figure here is an average.
23a. **`vco_core` PEX is extracted but not re-simulated, and a core-only re-sim would not be
    meaningful.** The extracted netlist exists (30 devices / 194 C / 208 R,
    `signoff/pex/vco_core/`). It is not re-simulated because `vco_core` is the cross-coupled pair
    alone: the oscillation frequency is set by the tank, and neither `vco_inductor_v2` nor
    `vco_varactors` has been extracted, so a core-only PEX run would move `f` by an amount that
    says nothing about the drawn oscillator. **There is also no committed VCO deck** —
    `team_src/sim/` holds only `div2/`, `ibias/` and `ind_em/`, and `vco_tb.sch` contains no
    `vco_core` instance, so a bench would have to be built as well as netlisted. **When it is
    done, the reference is `docs/verification.md` §3.2, the f–VTUNE re-run on the current
    netlist** (80 ns tran, settled 60–80 ns), not the `docs/verification.md` §3.1 `vco_tb` sweep;
    those two differ and the gap between them is itself unclosed.

---

## 7. What a reviewer should look at first

If time is short, these six things carry the most information:

1. **§2.3 — `I_P` removed from the pin list.** A 912 ps RC on the feedback path would have stopped
   the loop locking, and no gate in our flow could see it because the padring load lives outside
   `chip_top`. It is the most consequential change since the last review.
2. **§4.5 — the divider.** Full-band ÷2 with exact quadrature at every corner is the strongest
   result in the design, and the block was genuinely broken until an architectural fix on
   2026-08-12.
3. **§4.6.1 — N = 2, and no usable phase-detection window.** The most important thing in this
   document. The feedback divides by 2 only, so lock needs a 2.4–2.5 GHz reference into a PFD
   characterised at 1–2 MHz whose reset pulse is 1.22× that period at typ. This die is an
   open-loop test chip, and that is not recorded anywhere else in the repository.
4. **§6 items 10 / 10a — the DIV2 EM fix, and that there is no working fix.** The widening
   recorded as "verified at cell level" (4.93 → 0.987 mA/µm, DRC 0, bbox byte-identical)
   **fails LVS: it shorts `NS` to `VSS`** (2026-09-10). It had never been LVS'd, and DRC and bbox
   cannot see a same-layer short. Separately, the reproducibility gap once given as the reason it
   was unshipped is **withdrawn**: `ib_div2.tcl` regenerates the signed-off block byte-identically.
   The EM exposure is real and **unmitigated**.
5. **§6 item 10d — the IP converter's VSS tie connects to nothing.** `ib_div2.tcl:237–238`
   draws it at the wrong y, so `ib_conv_v1_0` returns its 2.96 mA through the p-substrate. LVS
   is structurally blind to it (substrate is one global node), so it passed every gate and is
   present in the signed-off GDS and in `chip_top` on `origin/main`.
6. **§6 items 13–14 — density fill and the W4 waiver.** The two items most likely to affect
   whether the design is accepted at final signoff, and neither is resolved.

---

## Cross-references

| Topic | Document |
|---|---|
| **Device declaration — every PDK model, count, where used** | `signoff/devices.md` |
| **Top-level LVS report** (`chip_top`) | `signoff/lvs/lvs.report` |
| **Extracted netlists, chip and per block** | `signoff/lvs/chip_top.lvs.spice`, `signoff/lvs/blocks/` |
| **CP_v1 R+C PEX and the extracted UP/DOWN match** | `signoff/pex/` |
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
