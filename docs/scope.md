# Scope, Frequency Plan, and Area Estimate — AUS/NZ Track A RFIC

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU (gf180mcuD)**
Last updated: 2026-07-30. Figures marked *(estimate)* are pre-layout and will be
replaced by extracted numbers as blocks are laid out.

This document freezes the design scope in response to the schematic-review
feedback (Conditional-Go), defines the corrected PLL signal chain, states the
frequency plan, and records the derived physical-area estimate.

---

## 1. Frozen scope and tiers

The review asked us to freeze a realistic minimum scope with an explicit fallback.
Blocks are grouped in three tiers. Only Tier 1 + Tier 2 are counted in the
committed silicon area (Section 5); Tier 3 is explicitly stretch.

| Tier | Blocks | Commitment |
|------|--------|------------|
| **1 — Minimum** | VCO, divide-by-2 / quadrature divider, PFD | Must tape out, DRC/LVS-clean |
| **2 — Next** | Charge pump (CP_v1), resettable DFF (D_FF_RST_v1) | Target; already have verified schematics |
| **3 — Stretch** | Full integer-N PLL loop closure, IQ modulator, SPI, output chain | Only if Tier 1+2 close early |

The divide-by-2 / quadrature block's inclusion in Tier 1 is **conditional on the
measured VCO band** — see Section 3.

---

## 2. Corrected PLL signal chain

The schematic-review noted the old block diagram wired the PFD straight into the
loop filter, omitting the charge pump. The corrected chain is:

```
                       (off-chip loop filter)
  REF_IN ─▶ PFD ─▶ CP ─▶ CP_OUT ─▶ [ R + C1 || C2 ] ─▶ VTUNE ─▶ VCO (4.11–6.37 GHz)
             ▲    UP/DN                                            │
             │                                                     ▼
             │                                            CML ÷2 quadrature
             │                                            │      │        │
             └──────────── feedback ◀─────────────────────┘      │        └─▶ MON_OUT
                                                                  ▼
                                     4 buffers ─▶ I_P/I_N/Q_P/Q_N (2.4–3.2 GHz, off-chip)
```

Key points:
- The **charge pump is explicit** and sits between PFD and loop filter.
- The **loop filter is off-chip** (see `pins.md`): the charge-pump output `CP_OUT`
  leaves the die, the passive filter is on the test PCB, and the filtered control
  voltage returns as `VTUNE`. This keeps the large filter capacitors and the RC
  tuning off silicon and lets us tune loop dynamics on the bench.
- The **divider** closes the loop back to the PFD (feedback via DIV2 **I_P** → PFD.FB).
  *(MON_OUT dropped 2026-08-20: DIV2_QUAD_v1 exposes no dedicated monitor tap and its
  divider output runs at ~2.5 GHz — too fast for a monitor pad; pin count 12→10. See
  docs/pins.md §1.)*

**Loop sign (KVCO < 0).** The VCO tuning is inverted — KVCO ≈ −706 MHz/V avg, ≈ −1.1 GHz/V
local near ISM (§3, corrected 2026-08-12), so
frequency *falls* as VTUNE *rises*. For the loop to lock, the UP/DOWN → charge-pump
sense must be **inverted** relative to the textbook KVCO > 0 case: a phase-lead
condition must move VTUNE in the direction that *lowers* VCO frequency toward lock.
Concretely, the CP's pump-up/pump-down assignment (which of UP/DOWN sources vs
sinks into the loop filter) is chosen so that the net correction drives VTUNE the
right way for KVCO < 0. **This is verified empirically at tb level** in the PFD+CP
integration sim (condition 4): the sign of average `I_out` vs static phase error
must move VTUNE toward lock, not away. No cell rewiring is done for this now — it
is a documented design constraint to be confirmed by simulation.

---

## 3. Frequency plan — FINAL (measured)

**Operating spec: 2.4–2.5 GHz output, post-÷2.** The VCO runs at **4.8–5.0 GHz**
(VTUNE ≈ **1.95–2.12 V**) and the ÷2 divider brings it to the 2.4–2.5 GHz ISM band.
Plan **B** is adopted; Plan A (native 2.4 GHz, no divider) is eliminated — the
tank cannot reach 2.4 GHz.

Corrected f–VTUNE of `vco_v1` (TT, 27 °C, VDD 3.3 V; full sweep + the correction of the
7/30 mid-curve error in `verification.md` §3.2):

| | VTUNE ≈ 0 V | VTUNE ≈ 2.0 V (ISM) | VTUNE ≈ 3.3 V |
|---|---|---|---|
| **VCO** | 6.38 GHz | 4.93 GHz | 4.05 GHz |
| **÷2 output** | 3.19 GHz | 2.46 GHz | 2.02 GHz |

- **Native band 4.05–6.38 GHz** → ÷2 output **2.02–3.19 GHz**. The 2.4–2.5 GHz ISM
  target sits mid-range with **tuning margin on both sides**.
- **KVCO ≈ −706 MHz/V** average; **local KVCO near the ISM point ≈ −1.1 GHz/V**
  (corrected 2026-08-12 — the old −790 MHz/V and the −1.4 GHz/V "mid-range" came from
  a non-reproducible mid-curve in the frequency plan that §3 superseded; the real curve is smooth/monotonic). Tuning is
  **inverted** (freq falls as VTUNE rises — NMOS varactor); see the loop-sign note in §2.
  **Loop-filter design must use −1.1 GHz/V** (loop BW ∝ √KVCO → ~18% higher, phase
  margin shifts; off-chip filter is unstarted so this is bench-adjustable).
- **Divider is REQUIRED** and stays in Tier 1 minimum scope.

**Paper-trail resolved (condition 2):** the proposal's 2.4–2.5 GHz was always the
**post-divider output**; the review's 4.5–5.7 GHz was the **native VCO band**. Both
are correct and are now unified by the measurement: VCO 4.11–6.37 GHz → ÷2 →
2.06–3.18 GHz, ISM at mid-tune.

> **Caveats:** single corner (TT, 27 °C) only; the swing figures are the *buffered*
> differential output into 50 Ω, not the tank swing; full VCO characterization
> (corners, current/power, startup, phase noise, tank swing) is **condition 5,
> still pending** (`verification.md` §3).

---

## 4. Block status

| Block | File(s) | Schematic | Testbench | Sim status | Owner |
|-------|---------|-----------|-----------|------------|-------|
| VCO core + tank | `vco_v1.sch/.sym` | ✅ | `vco_tb`, `vco_tank_tb`, `vco_varactor_tb` | f–VTUNE measured 4.11–6.37 GHz (§3); full char pending (cond. 5) | Zach |
| Custom inductor | `magic/vco_inductor_v2` | ✅ (layout + `.subckt`) | `inductor_tb` | Preliminary model; re-extraction pending (cond. 6) | Zach |
| PFD | `PFD_v1.sch/.sym` | ✅ | `PFD_tb` | Verified 1 MHz; 3-case re-run pending (cond. 4). **Symbol/schematic pin mismatch to resolve** | Greg |
| Resettable DFF | `D_FF_RST_v1.sch/.sym` | ✅ | `D_FF_RST_v1_tb` | Edge-detector reset verified. **Symbol/schematic pin mismatch to resolve** | Greg |
| NAND3 / NAND / NOT / DFF | `NAND3_v1`, `NAND_v1`, `NOT_v1`, `D_FF_v1` | ✅ | `NAND3_v1_tb` | Leaf cells | Zach/Greg |
| Charge pump | `CP_v1.sch/.sym` | ✅ | `CP_dc_tb`, `CP_tran_tb` | DC + transient characterized; I_CP=50µA placeholder | Greg |
| ÷2 quadrature divider (CML) | `DIV2_CML_probe` → `DIV2_QUAD_v1` | 🟡 CML ÷2 proven; clean to 5 GHz, band-top tuning WIP | `DIV2_CML_probe_tb` | Divides ÷2 (verification.md §7); reaching 6.37 GHz + quadrature accuracy WIP | Greg |
| RF output buffers (×4) | `DIV2_QUAD_v1` (converter) | 🟡 3-stage converter built, **non-working in steady state** | — | CML→CMOS converter → **1 kΩ** series isolation R → pad; monitor-grade I_P/I_N/Q_P/Q_N at 2.4–3.2 GHz. Aug-21 rework (see `div2-debug.md`) | Greg |
| Loop filter | off-chip | n/a | — | Passive, on test PCB | — |

> **Output-buffer load ruling (updated 2026-08-10): series isolation R = 1 kΩ, not 450 Ω.**
> The pad is a monitor into the instrument 50 Ω; scope amplitude = 3.3·50/(R_SER+50), and
> the load at the driver ≈ R_SER + 45 Ω (pad 300 fF ∥ 50 Ω at 5 GHz). 450 Ω (0.33 Vpp) was
> locked assuming a free rail-to-rail driver; costed out that driver is ~140 µm pfet/device
> ×4 + a 4th taper stage (~26 mA). **1 kΩ gives ~124–157 mVpp (−12 dBm)** — ample to confirm
> ÷2 ratio and I/Q phase — with a moderate 3-stage driver at ~12.6 mA peak / ~6.3 mA avg over
> the four buffers. Rationale + arithmetic in `div2-debug.md`.
> **OPEN (Aug-21):** the four on-chip 1 kΩ resistors need a **flavor + area check against the
> PDK** (which gf180 resistor layer, sheet ρ, and the resulting area ×4).

> **Known issue (carried):** headless netlisting reports symbol-vs-schematic pin
> count warnings on `PFD_v1` (sym 6 / sch 8) and `D_FF_RST_v1` (sym 7 / sch 19),
> caused by duplicate `VDD`/`VSS` `iopin` instances (all port names correct).
> Non-fatal — sims run (PFD verified at 1 MHz); the risk is Phase-4 LVS. Fix
> approved (iopin→lab_pin, one power port each), lands + verifies before condition-4
> evidence is finalized. See `verification.md` §1.4. (`D_FF_v1`, Zach's, has the
> same issue but is not in the PFD hierarchy — flagged to Zach, untouched.)

---

## 4.1 Device flavor — mixed 5 V digital / 3.3 V analog (decided 2026-08-05)

**The digital chain (PFD + its cells) uses the `gf180mcu_fd_sc_mcu7t5v0` standard-cell
library, which is built from 5 V (`*_05v0`) devices. The analog blocks (VCO, CP, and
the divider) stay full-custom `*_03v3` (3.3 V).** Both run on the single 3.3 V rail.

**Why:** with Zach out ~2 weeks and one person on layout, hand-drawing the custom
digital cells (`D_FF_RST_v1`, `NAND3_v1`, …) by Aug 14 is not feasible. The library
has the exact cells our PFD needs — `dffrnq_1` (async active-low-reset DFF) and
`nand2_1` — which are pre-drawn and DRC-clean, so the PFD is assembled from them in
our own topology and **re-verified** (lead/lag/equal + dead-zone + corners, see
`verification.md §2.2`, gate passed). This supersedes the earlier "all cells 03v3"
uniformity (`verification.md §1`) **for the digital chain only**.

**Consequences accepted:** (1) the digital chain tapes out library std cells, not our
characterized custom cells; (2) 5 V devices at 3.3 V are slower — irrelevant at the
PFD's MHz reference rate; (3) the reset path needed 2× `inv_1` of added delay to
restore the minimum pulse to 0.50 ns. See §4.2 for the layout-adjacency implications.

## 4.2 Layout implication — 5 V std cells next to 03v3 analog

Placing 5 V (`05v0`) std cells next to 3.3 V (`03v3`) analog in the same die has real
DRC consequences, all handled by keeping the digital as a **self-contained block**,
not by interleaving device flavors:

- **DUALGATE boundary.** gf180 marks 5 V devices with the `DUALGATE` layer. The std
  cells carry DUALGATE over their transistors; the 3.3 V analog does not. DUALGATE has
  its own enclosure/spacing rules, so the digital block needs a **DUALGATE keep-out /
  spacing to the nearest 03v3 device** at its boundary. (This is the same class of
  issue the `chip_top` flow config flags: "DUALGATE drawn into high-level cells.")
- **Well / implant spacing.** 5 V cells use their own well/implant; inter-flavor well
  and nplus/pplus spacing rules apply at the block edge → budget a **guard-ring +
  spacing margin** between the digital block and any analog block.
- **Mitigation (already our partition):** PFD and CP are **separate blocks** with pad
  interfaces (`pins.md`), so the flavor boundary lands at the inter-block gap, where a
  guard ring + spacing absorbs it — no device-level interleaving. Do **not** place
  individual 5 V std cells inside a 3.3 V analog block.
- **LVS/DRC decks** cover both flavors (single gf180mcuD deck / netgen setup), so no
  tooling change — only the physical spacing/guard-ring discipline at the boundary.

> **The DUALGATE spacing is a DRC floor, NOT the intended block gap.** DV.3 (0.24 µm
> DUALGATE-to-COMP) → ~0.48 µm PFD-active-to-CP-active is only what keeps the oxide/well
> *legal*. It does **nothing** for noise. PFD is a hard-switching block and **CP_OUT is
> high-impedance into the off-chip loop filter**, so substrate/capacitive coupling there
> becomes **reference spurs on VTUNE**. The **real CP↔PFD separation is noise-driven:
> ≥ 20 µm (30–50 µm is cheap — area isn't the constraint), double guard rings, CP on VDDA /
> PFD on VDDD, and CP_OUT shielded along its route to the pad.** Full spec in
> `docs/cp-layout-packet.md §3b`. Do not let a future reader treat 0.48 µm as the gap.
> **Two clarifications:** (1) the guard-ring **VSSA/VSSD are on-chip labels only — NOT
> separate ground pins**; the padframe gives one chip-wide common ground (#143), so the two
> returns are routed separately and **star-connected to the single common-ground point**.
> (2) **Deep nwell is NOT adopted for Aug 14** (new layer + new DRC rules, wrong week) —
> it's a later-revision isolation option if measured spurs demand it.

## 5. Physical area estimate *(estimate)*

**Area Estimate: 350 µm × 300 µm** *(pre-layout estimate — Tier 1 + Tier 2 blocks)*

Derived bottom-up, not invented:

1. **Inductor (measured):** headless Magic bbox of `vco_inductor_v2.mag` =
   **182 µm × 84 µm** (15,288 µm²) — the dominant single element.
2. **VCO block:** inductor + ~40 % for cross-coupled pair, varactors, and output
   buffers, plus a magnetic keep-out ring → **≈ 240 µm × 180 µm** block.
3. **Digital (std-cell density basis):** gf180mcu 7-track cell areas
   (INV 8.78, NAND2 10.98, NAND3 15.37 µm²) applied to the transistor hierarchy:
   - D_FF_RST_v1 = 1·NAND3 + 5·NAND2 + 10·INV = 158 µm²
   - PFD_v1 = 2·D_FF_RST + 1·NAND2 = **327 µm²**
   - ÷2/quadrature divider ≈ 2·DFF ≈ **162 µm²** (contingency)
   - At ~60 % placement utilization → ≈ 815 µm².
4. **Charge pump (custom):** from device geometry (3× W=50µm PMOS, 3× W=10µm NMOS,
   folded, + guard ring) → **≈ 1,200 µm²**.
5. **Routing / guard rings:** +50 % on the digital + CP subtotal → ≈ 3,000 µm².
6. **Total active** ≈ 43,000 (VCO w/ keep-out) + 3,000 (digital + CP) ≈ 46 k µm².
7. **Rounded to a clean rectangle with keep-out / buffer / routing headroom:**
   **350 µm × 300 µm** (105,000 µm²), ≈ 2× the bottoms-up active area.

> **[CORRECTED 2026-08-17 — this §5 bottoms-up is superseded by measured layout; see
> `tracking.md` area table.]** Two lines above were badly off: (a) the "÷2/quadrature divider
> ≈ 162 µm²" (item 3) was a std-cell-DFF guess — the real full-custom CML+slicer
> `DIV2_QUAD_v1` measures **41,340 µm²**; (b) the "43 k VCO w/ keep-out" over-counted — the VCO
> is inductor-dominated at **~18,000 µm²** (measured inductor 15,288 + ~2.7 k core). Measured
> reality: 4 signed-off blocks = **56,635 µm²** + VCO ~18,000 = **~75,000 µm²** of blocks; with
> 30–50 % top routing → **~96,000–114,000 µm²**. So **350×300 (105,000) STRADDLES the range —
> tight but plausible**, NOT the "≈ 2× slack" this line claims. **FINAL (Phase-7 assembly, routed + GND ring, measured on the deliverable
> GDS): die = 522 × 309 µm = 161,298 µm² ≈ 0.161 mm² — the number to use.** The 350×300 estimate
> above is stale/short; kept only as the bottoms-up record.

**Slot fit:** the `slot_0p5x0p5` core is **1052 µm × 1647 µm** (from
`librelane/slots/slot_0p5x0p5.yaml`, CORE_AREA [442,442,1494,2089]). The estimate
uses **33 % of the core width and 18 % of the core height** — comfortable margin,
well inside the slot with room for stretch (Tier 3) blocks.

Density basis justification: gf180mcu 7-track standard-cell areas are a
conservative proxy for our gate-level digital (manual full-custom is typically
equal or denser), so the digital term does not under-estimate. The CP term is
custom analog and is dominated by the three W=50 µm PMOS devices.

---

## 6. Fallback plan

If schedule slips, scope collapses toward Tier 1 in this order:

1. **Drop Tier 3** (PLL closure, IQ mod, SPI, output chain) — already stretch.
2. **Drop CP + loop closure (Tier 2 partial):** tape out VCO + divider + PFD as
   independently testable blocks with their own pads; characterize open-loop.
3. **Minimum viable tapeout:** VCO + divider only, fully characterized, with PFD
   as a separate testable cell. This still answers the core review conditions
   (VCO characterization, divider feasibility) and yields a DRC/LVS-clean GDS.

The off-chip loop filter is deliberate insurance: it removes the largest passive
components and the closed-loop stability risk from the silicon critical path.

---

## 7. Partition & test approach (condition 7)

- **Delivery model:** a **block footprint with specified pad types at fixed,
  organizer-scripted placement** — the organizer integrates blocks into the
  padframe. Our interface is the **8-signal block** in `pins.md` §1 (analog 4,
  digital 4, VDDA+VDDD, common ground), not a whole slot.
- **On/off-chip:** loop filter off-chip (`CP_OUT`, `VTUNE`); REF/RST/MON digital;
  **`I_P/I_N/Q_P/Q_N` differential quadrature analog out (2.4–3.2 GHz) via 4
  monitor-grade output buffers**; `IBIAS_CP` analog DC bias.
- **Bench test:** REF from a signal generator; VTUNE swept by DC source for
  open-loop f–VTUNE; **quadrature verified as the off-chip I/Q phase difference**
  (I_P/I_N vs Q_P/Q_N into 50 Ω, target 90°) on a scope/VNA; MON_OUT to a counter;
  loop closed through the off-chip filter for lock tests.
- **The `slot_0p5x0p5` full-frame plan is superseded** (see `pins.md` appendix);
  the workshop-slot LibreLane flow is retained **only as toolchain / sample-GDS
  proof**, not as our integration path.

**Bring-up / calibration notes (silicon):**
- **Corrected KVCO ≈ −1.1 GHz/V near ISM** (was −790 MHz/V; `verification.md` §3.2). Two
  consequences for whoever designs the (off-chip, unstarted) **loop filter**: loop
  bandwidth ∝ √KVCO → **~18% higher**, and **phase margin shifts** — bench-adjustable, not
  a redesign, but design the filter with −1.1 GHz/V. **Reference spurs scale directly with
  KVCO**, so CP_v1's known **+110 fC charge injection now maps to ~1.4× the VTUNE frequency
  deviation** it did at −790 — strengthens the injection caveat (`verification.md` §2.6).
  The **static phase-offset bound is KVCO-independent** (~1 ps from the 0.18% CP mismatch —
  unchanged). Update the loop-filter KVCO everywhere it is quoted.
- **DIV2 output settling:** the self-biased converters + CML + pad settle in ~16 ns (TT) to
  ~26 ns (SS/85 °C). **Allow ~30 ns after VCO power-up before reading** I_P/I_N/Q_P/Q_N or
  the I/Q phase on the bench (`div2-debug.md`). Startup transients are real in silicon too.
