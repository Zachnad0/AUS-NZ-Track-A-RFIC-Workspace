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

**Loop sign (KVCO < 0).** The VCO tuning is inverted — KVCO ≈ −683 MHz/V (§3), so
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
(VTUNE ≈ 2.05–2.28 V) and the ÷2 divider brings it to the 2.4–2.5 GHz ISM band.
Plan **B** is adopted; Plan A (native 2.4 GHz, no divider) is eliminated — the
tank cannot reach 2.4 GHz.

Measured f–VTUNE of `vco_v1` (TT, 27 °C, VDD 3.3 V; full sweep in
`verification.md` §3):

| | VTUNE ≈ 0 V | VTUNE ≈ 2.15 V (ISM) | VTUNE ≈ 3.3 V |
|---|---|---|---|
| **VCO** | 6.37 GHz | ~4.9 GHz | 4.11 GHz |
| **÷2 output** | 3.18 GHz | ~2.45 GHz | 2.06 GHz |

- **Native band 4.11–6.37 GHz** → ÷2 output **2.06–3.18 GHz**. The 2.4–2.5 GHz ISM
  target sits mid-range with **tuning margin on both sides**.
- **KVCO ≈ −683 MHz/V** average (up to −1.4 GHz/V mid-range, ≈ −790 MHz/V near the
  ISM operating point). Tuning is **inverted** (freq falls as VTUNE rises — NMOS
  varactor); see the loop-sign note in §2.
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
| ÷2 / quadrature divider | `DIV2_QUAD_v1` (planned) | ⏳ green-lit, **Tier 1 required** | — | Verify across full native 4.11–6.37 GHz (free-run range) + quadrature accuracy + timing margin @ 6.37 GHz worst case; queued after librelane proof | Greg |
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

---

## 7. Partition & test approach (condition 7)

- **Delivery model:** a **block footprint with specified pad types at fixed,
  organizer-scripted placement** — the organizer integrates blocks into the
  padframe. Our interface is the **8-signal block** in `pins.md` §1 (analog 4,
  digital 4, VDDA+VDDD, common ground), not a whole slot.
- **On/off-chip:** loop filter off-chip (`CP_OUT`, `VTUNE`); REF/RST/MON digital;
  RF_OUTP/N differential analog out (2.4–3.2 GHz); IBIAS_CP DC on a digital pad.
- **Bench test:** REF from a signal generator; VTUNE swept by DC source for
  open-loop f–VTUNE; RF_OUTP/N into 50 Ω for spectrum/phase-noise; MON_OUT to a
  counter; loop closed through the off-chip filter for lock tests.
- **The `slot_0p5x0p5` full-frame plan is superseded** (see `pins.md` appendix);
  the workshop-slot LibreLane flow is retained **only as toolchain / sample-GDS
  proof**, not as our integration path.
