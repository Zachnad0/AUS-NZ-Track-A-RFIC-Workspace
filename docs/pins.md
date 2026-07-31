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

## 1. Block signal interface (primary) — 12 pins

Quadrature is padded to differential I/Q; **4 monitor-grade RF output buffers**
(~2.4–3.2 GHz) drive `I_P/I_N/Q_P/Q_N` off-chip.

| # | Signal | Dir | Pad type | Notes |
|---|--------|-----|----------|-------|
| 1 | **I_P** | out | analog | in-phase output + (2.4–3.2 GHz, buffered) |
| 2 | **I_N** | out | analog | in-phase output − |
| 3 | **Q_P** | out | analog | quadrature output + |
| 4 | **Q_N** | out | analog | quadrature output − |
| 5 | **VTUNE** | in | analog | control voltage from off-chip loop filter |
| 6 | **CP_OUT** | out | analog | charge-pump output to off-chip loop filter |
| 7 | **IBIAS_CP** | in | analog (DC) | charge-pump bias reference |
| 8 | **REF_IN** | in | digital | reference clock |
| 9 | **RST_N** | in | digital | active-low reset (divider active-low RST confirmed) |
| 10 | **MON_OUT** | out | digital | divided-down VCO monitor |
| 11 | **VDDA** | — | power | analog supply |
| 12 | **VDDD** | — | power | digital supply |

**Tally:** analog **7** · digital **3** · power **2** · **ground 0** (chip-wide
common). **Block pin total = 12.**

---

## 2. Per-analog-signal ESD (design consideration)

Each analog pad carries **secondary ESD** structures adding shunt capacitance.
**I_P/I_N/Q_P/Q_N operate at 2.4–3.2 GHz** (VCO ÷2), where pad + ESD C loads the
output — the 4 output-buffer sizings **must budget the measured pad/ESD C**.
VTUNE, CP_OUT, IBIAS_CP (DC / low-freq) are insensitive. Verification item.

---

## 3. Config fit (against the real proposal totals)

Block needs **12 pins** (analog 7 + digital 3 + power 2; ground is common, 0). The
binding constraints are **total pin count** and **per-block power** — *not* an
analog-pad budget (each project picks its own pad types within its total).

| Config | Pin total | Fits (need 12)? | Spare | Verdict |
|--------|----------:|-----------------|------:|---------|
| A | 22 | ✓ | 10 | oversized for the block |
| **B** | 16 | ✓ | **4** | **chosen fit** |
| C | 6  | ✗ | −6 | too few pins |
| D | 10 | ✗ (12 > 10) → ✓ reduced | 0 | **fallback** (see below) |
| E | 6  | ✗ | −6 | too few pins |

- **Primary: config B (16 pins) — fits the 12-pin block with 4 spare.** Our
  350 × 300 µm footprint (`scope.md` §5) sits well inside B's 1/8 die share.
- **Fallback: config D (10 pins)** if B is unavailable — drop to **single-ended
  I_P/Q_P** (remove I_N/Q_N) and **merge VDDA+VDDD** → **10 pins exact**. Costs the
  differential I/Q outputs (monitor becomes single-ended) and supply isolation.

---

## Appendix (SUPERSEDED): wafer.space slot frame

*Retained for reference only. The organizer padframe-proposal model (above)
replaces this; the `slot_*` yamls / `slot_defines.svh` are used only to drive the
LibreLane toolchain / sample-GDS proof (`verification.md` §6), not for our pin
allocation.* `slot_0p5x0p5`: analog 4, bidir 38, input 4, clk/rst, DVDD 4, DVSS 4.
