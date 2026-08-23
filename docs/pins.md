# Pin / Pad Plan — AUS/NZ Track A RFIC

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU**
Last updated: 2026-08-22. Slot variant **BH**; pin list frozen for the Aug 28 DEF gate.

> **Integration model — organizer padframe proposal.** Projects share a die
> (**2235 × 2235 µm project area, 88 pins total**). Each project is allocated a
> **config** = a **die share + fixed pin total**; the project chooses its own pad
> **types** within that total. **Power counts against a block's pin total; ground
> is a single chip-wide common** (no block pin) — confirmed by organizer (Bailey).
> The old wafer.space `slot_*` yamls / `slot_defines.svh` are **toolchain-only**
> now (sample-GDS proof) — see SUPERSEDED appendix.

Config totals (organizer proposal):

| Config | Die share | Pin total |
|--------|-----------|----------:|
| A | 1/4  | 22 |
| **B** | 1/8  | **16** |
| C | 1/8  | 6 |
| D | 1/16 | 10 |
| E | 1/16 | 6 |

---

## 1. Block signal interface (primary) — 13 pins

Quadrature is padded to differential I/Q; **4 monitor-grade RF output buffers**
(~2.4–3.2 GHz) drive `I_P/I_N/Q_P/Q_N` off-chip. Pin order below is the info.yaml order
(clockwise from bottom-left, upper-left quadrant); it matches the 12 chip_top LVS ports.

| # | Signal | Dir | Pad type | Notes |
|---|--------|-----|----------|-------|
| 1 | **VSSA** | — | ground | quiet down-bonded quadrant ground (Bailey: first quadrant pin). One ground net (all VSS ties the shared p-substrate; no deep-nwell) → one ground pin. The die still bonds ground at more ring points (package detail). |
| 2 | **VDDA** | — | power | analog supply |
| 3 | **IBIAS** | in | analog (DC) | chip-level bias reference (external 240 µA); on-chip bias generator fans out to CP (~50 µA) and DIV2 tails (2.4 mA/tail). Was `IBIAS_CP`; renamed 2026-08-04 — **one pad** |
| 4 | **ISS** | in | analog (DC) | LC-VCO tail node. Kept OFF-CHIP-drivable (not tied to GND) so the tail current stays controllable — the 4.13–6.35 GHz band was characterized with a 1 mA tail mirror on ISS; grounding it on-chip would move the operating point. |
| 5 | **VTUNE** | in | analog | control voltage from off-chip loop filter |
| 6 | **CP_OUT** | out | analog | charge-pump output to off-chip loop filter |
| 7 | **Q_N** | out | analog | quadrature output − (north slot N02) |
| 8 | **I_N** | out | analog | in-phase output − (N03) |
| 9 | **I_P** | out | analog | in-phase output + (2.4–3.2 GHz, buffered); also closes the PLL loop → PFD.FB (N04) |
| 10 | **Q_P** | out | analog | quadrature output + (N05) |
| 11 | **VSSD** | — | ground | digital-island ground (N06). Same on-chip node as VSSA; see the VSSD note below. |
| 12 | **VDDD** | — | power | digital supply (N07) |
| 13 | **REF_IN** | in | digital | reference clock (N08). Expands on the pad to REF_IN/PU/PD — PU=0, PD=1 (weak pull-down). |

**Tally:** analog **8** · digital **1** · power **2** · **ground 2** (VSSA, VSSD).
**Block pin total = 13.** chip_top carries 12 LVS ports today; VSSD is the 13th port and is
the SAME internal node as VSSA (one p-substrate, no deep-nwell), so the golden ties both
port labels to one net.

> **Slot variant BH — 1110 × 550 µm landscape (Greg, 2026-08-22).** Slots **W18–W22**
> (VSSA, VDDA, IBIAS, ISS, VTUNE) + **N01–N08** (CP_OUT, Q_N, I_N, I_P, Q_P, VSSD, VDDD,
> REF_IN). Chosen over BV for aspect match to the 522 × 309 core and a ~241 µm I/Q haul to
> the north edge (BV: 550–900 µm up the portrait west edge). Cost: BH has no `vss_fixed`, so
> VSSA carries the full ~1 nH bond inductance (~31 Ω at 5 GHz). See
> `docs/phase8-padframe-plan.md` §3.

> **VSSD added (2026-08-22).** The padring's digital-domain BREAK isolates a VDDD-powered
> island holding VDDD + REF_IN, and that island had **no ground pad** — Bailey's GDS audit
> flags it verbatim as `A01: group 2 missing ground: VDDD REF_IN`. VSSD sits immediately
> before VDDD (mirroring VSSA-before-VDDA in the analog island) so it lands inside that
> island and supplies its ESD/return locally. **This does not create a second ground net:**
> Bailey confirmed 2026-08-21 that user-defined grounds are all shorted through the padring
> and substrate and are electrically one node — the split buys noise and bond-inductance
> isolation only. REF_IN's pull-down (PD=1) therefore ties to VSSD, the digital island's
> ground, not to VSSA.

> **I/Q pad order Q_N, I_N, I_P, Q_P (2026-08-22).** Left taps → left pads, per
> `phase8-padframe-plan.md` §3d: matched wire 2000 → ~1077 µm, I/Q spread 288 → 58 µm, and
> all three route crossings removed. Splitting the Q pair to opposite slots costs nothing —
> these are single-ended monitor outputs, each into its own 1 kΩ→50 Ω instrument.

> **ISS brought out to its own pad (2026-08-20).** chip_top.sch had transiently tied
> vco_v1.ISS to GND; that reversed the 5.4 option-(b) decision (ISS a separate tail node)
> and invalidated the characterization (the tail mirror set ~1 mA; grounded sources set the
> current by sizing+supply, far above 1 mA — a different VCO). ISS is now an analog pad in
> the analog group. `vco_v1.GND` (nfet-bulk/substrate return) stays on the common ground.

> **RST_N and MON_OUT DROPPED (2026-08-20, Phase-7 integration).** Neither maps to a
> real block port, so keeping them would have forced reopening a signed-off block:
> - **RST_N** — `DIV2_QUAD_v1` exposes **no reset port** (its top labels are CK CKB
>   IBIAS I_N I_P OI OIB OQ OQB Q_N Q_P VDD VSS). The "divider active-low reset" was
>   never brought out; adding it means re-laying-out and re-signing-off DIV2.
> - **MON_OUT** — **no block exposes a monitor tap**. It could only have tapped a
>   divider phase, which runs at ~2.5 GHz (VCO÷2) — far too fast for a monitor pad /
>   counter, so it would not have been usable anyway.
>
> The loop feedback now uses **I_P → PFD.FB** directly (any quadrature phase closes the
> loop; I_P is the pick). Pin count 12 → **10**, still well inside config B's 16.

---

## 2. Per-analog-signal ESD (design consideration)

**`secondary_esd: false` on all eight analog pins (2026-08-22).** Bailey: *"Set the
secondary_esd to false, and then add it yourself to the circuit and layout."* The padframe
generator adds nothing, so declaring `true` would claim protection the GDS does not have.
The eight CDM clamps (diode perimeter > 25 µm plus a > 50 Ω series poly resistor) are ours
to build and are a **final-data** item, not an Aug-28-gate item.

Each analog pad carries **secondary ESD** structures adding shunt capacitance.
**I_P/I_N/Q_P/Q_N operate at 2.4–3.2 GHz** (VCO ÷2), where pad + ESD C loads the
output — the 4 output-buffer sizings **must budget the measured pad/ESD C**.
VTUNE, CP_OUT, IBIAS (DC / low-freq) are insensitive. Verification item.

> **Bias-pad rename (2026-08-04):** `IBIAS_CP` → **`IBIAS`**, a chip-level bias
> reference. One external 240 µA feeds an on-chip bias generator that fans out to
> both the charge pump (~50 µA) and the DIV2 CML tails (2.4 mA each). This matches
> `CP_v1`'s stated end-state (mirrored bias from the PLL bias generator). **Pin
> count is unchanged by the rename (still one analog-DC pad).** Issue #143's
> pin-line wording may need to follow this rename (Greg to update — external).

---

## 3. Config fit (against the real proposal totals)

Block needs **13 pins** (analog 8 + digital 1 + power 2 + ground 2). The
binding constraints are **total pin count** and **per-block power** — *not* an
analog-pad budget (each project picks its own pad types within its total).

| Config | Pin total | Fits (need 13)? | Spare | Verdict |
|--------|----------:|-----------------|------:|---------|
| A | 22 | ✓ | 9 | oversized for the block |
| **B** | 16 | ✓ | **3** | **chosen fit** |
| C | 6  | ✗ | −7 | too few pins |
| D | 10 | ✗ (13 > 10) | −3 | too few pins |
| E | 6  | ✗ | −7 | too few pins |

- **Primary: config B (16 pins) — fits the 13-pin block with 3 spare** (RST_N/MON_OUT
  dropped, ISS + VSSA ground added 2026-08-20, VSSD added 2026-08-22, see §1). Slot BH
  allocates 1110 × 550 = 610,500 µm² usable; the routed core is 522 × 309 µm.

---

## Appendix (SUPERSEDED): wafer.space slot frame

*Retained for reference only. The organizer padframe-proposal model (above)
replaces this; the `slot_*` yamls / `slot_defines.svh` are used only to drive the
LibreLane toolchain / sample-GDS proof (`verification.md` §6), not for our pin
allocation.* `slot_0p5x0p5`: analog 4, bidir 38, input 4, clk/rst, DVDD 4, DVSS 4.
