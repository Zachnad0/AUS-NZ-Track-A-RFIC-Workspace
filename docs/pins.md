# Pin / Pad Plan — AUS/NZ Track A RFIC

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU**
Last updated: 2026-07-31. Pin assignments are *(estimate)*.

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

## 1. Block signal interface (primary) — 10 pins

Quadrature is padded to differential I/Q; **4 monitor-grade RF output buffers**
(~2.4–3.2 GHz) drive `I_P/I_N/Q_P/Q_N` off-chip.

| # | Signal | Dir | Pad type | Notes |
|---|--------|-----|----------|-------|
| 1 | **I_P** | out | analog | in-phase output + (2.4–3.2 GHz, buffered); also closes the PLL loop → PFD.FB |
| 2 | **I_N** | out | analog | in-phase output − |
| 3 | **Q_P** | out | analog | quadrature output + |
| 4 | **Q_N** | out | analog | quadrature output − |
| 5 | **VTUNE** | in | analog | control voltage from off-chip loop filter |
| 6 | **CP_OUT** | out | analog | charge-pump output to off-chip loop filter |
| 7 | **IBIAS** | in | analog (DC) | chip-level bias reference (external 240 µA); on-chip bias generator fans out to CP (~50 µA) and DIV2 tails (2.4 mA/tail). Was `IBIAS_CP`; renamed 2026-08-04 — **one pad** |
| 8 | **REF_IN** | in | digital | reference clock |
| 9 | **VDDA** | — | power | analog supply |
| 10 | **VDDD** | — | power | digital supply |

**Tally:** analog **7** · digital **1** · power **2** · **ground 0** (chip-wide
common). **Block pin total = 10.**

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

Block needs **10 pins** (analog 7 + digital 1 + power 2; ground is common, 0). The
binding constraints are **total pin count** and **per-block power** — *not* an
analog-pad budget (each project picks its own pad types within its total).

| Config | Pin total | Fits (need 10)? | Spare | Verdict |
|--------|----------:|-----------------|------:|---------|
| A | 22 | ✓ | 12 | oversized for the block |
| **B** | 16 | ✓ | **6** | **chosen fit** |
| C | 6  | ✗ | −4 | too few pins |
| D | 10 | ✓ (exact) | 0 | fits with zero spare |
| E | 6  | ✗ | −4 | too few pins |

- **Primary: config B (16 pins) — fits the 10-pin block with 6 spare** (was 4 spare at
  12 pins; RST_N/MON_OUT dropped 2026-08-20, see §1). Die ≈ 472 × 270 µm before routing
  sits well inside B's 1/8 share (~624,000 µm²).
- **Config D (10 pins)** now fits the block **exactly** (no reduction needed) — but with
  zero spare it leaves no margin, so B stays primary.

---

## Appendix (SUPERSEDED): wafer.space slot frame

*Retained for reference only. The organizer padframe-proposal model (above)
replaces this; the `slot_*` yamls / `slot_defines.svh` are used only to drive the
LibreLane toolchain / sample-GDS proof (`verification.md` §6), not for our pin
allocation.* `slot_0p5x0p5`: analog 4, bidir 38, input 4, clk/rst, DVDD 4, DVSS 4.
