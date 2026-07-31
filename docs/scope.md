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
  REF_IN ─▶ PFD ─▶ CP ─▶ CP_OUT ─▶ [ R + C1 || C2 ] ─▶ VTUNE ─▶ VCO ─▶ RF_OUTP/RF_OUTN
             ▲    UP/DN                                            │
             │                                                     ▼
             └──────────────── ÷N divider ◀────────────── (÷2 / quadrature) ◀┘
                                    │
                                    └─▶ MON_OUT (divided-down monitor, digital)
```

Key points:
- The **charge pump is explicit** and sits between PFD and loop filter.
- The **loop filter is off-chip** (see `pins.md`): the charge-pump output `CP_OUT`
  leaves the die, the passive filter is on the test PCB, and the filtered control
  voltage returns as `VTUNE`. This keeps the large filter capacitors and the RC
  tuning off silicon and lets us tune loop dynamics on the bench.
- The **divider** closes the loop back to the PFD and also drives `MON_OUT`, a
  divided-down copy of the VCO for frequency observation on a digital pad.

---

## 3. Frequency plan — PENDING measured f–VTUNE sweep

The review flagged an inconsistency between the proposal (2.4–2.5 GHz) and the
review discussion (4.5–5.7 GHz, ÷2). **We are not publishing a chosen band until
we have a measured f–VTUNE sweep of `vco_v1`.** Two candidates remain open:

| Candidate | VCO native band | Divider in Tier 1? | ISM output |
|-----------|-----------------|--------------------|------------|
| **A** | 2.4–2.5 GHz native | **No** ÷2 needed for minimum scope | VCO directly in-band |
| **B** | ~4.5–5.7 GHz native | **Yes**, ÷2 to reach band | VCO ÷2 → 2.4–2.5 GHz |

The choice between A and B depends solely on the measured oscillation frequency of
`vco_v1` at nominal VTUNE and across the tune range. The measurement (step 11 of
the work plan) is queued; this section will be finalized with the measured band,
KVCO, and the resulting divider decision. Candidate B also determines whether the
high-speed ÷2 divider is feasible at the native rate (review condition 2).

> **Status: OPEN.** No band is committed. The area estimate in Section 5 already
> reserves room for the ÷2/quadrature divider, so it is valid under either
> candidate.

---

## 4. Block status

| Block | File(s) | Schematic | Testbench | Sim status | Owner |
|-------|---------|-----------|-----------|------------|-------|
| VCO core + tank | `vco_v1.sch/.sym` | ✅ | `vco_tb`, `vco_tank_tb`, `vco_varactor_tb` | Baseline oscillation confirmed; full char pending (cond. 5) | Zach |
| Custom inductor | `magic/vco_inductor_v2` | ✅ (layout + `.subckt`) | `inductor_tb` | Preliminary model; re-extraction pending (cond. 6) | Zach |
| PFD | `PFD_v1.sch/.sym` | ✅ | `PFD_tb` | Verified 1 MHz; 3-case re-run pending (cond. 4). **Symbol/schematic pin mismatch to resolve** | Greg |
| Resettable DFF | `D_FF_RST_v1.sch/.sym` | ✅ | `D_FF_RST_v1_tb` | Edge-detector reset verified. **Symbol/schematic pin mismatch to resolve** | Greg |
| NAND3 / NAND / NOT / DFF | `NAND3_v1`, `NAND_v1`, `NOT_v1`, `D_FF_v1` | ✅ | `NAND3_v1_tb` | Leaf cells | Zach/Greg |
| Charge pump | `CP_v1.sch/.sym` | ✅ | `CP_dc_tb`, `CP_tran_tb` | DC + transient characterized; I_CP=50µA placeholder | Greg |
| ÷2 / quadrature divider | — | ⏳ not started | — | Conditional on freq plan (cond. 2) | Greg |
| Loop filter | off-chip | n/a | — | Passive, on test PCB | — |

> **Known issue (carried):** headless netlisting reports symbol-vs-schematic pin
> count warnings on `PFD_v1` (sym 6 / sch 8) and `D_FF_RST_v1` (sym 7 / sch 19),
> caused by duplicate `VDD`/`VSS` `iopin` instances (all port names correct).
> Non-fatal — sims run (PFD verified at 1 MHz); the risk is Phase-4 LVS. Fix
> approved (iopin→lab_pin, one power port each), lands + verifies before condition-4
> evidence is finalized. See `verification.md` §1.4. (`D_FF_v1`, Zach's, has the
> same issue but is not in the PFD hierarchy — flagged to Zach, untouched.)

---

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
