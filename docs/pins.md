# Pin / Pad Plan — AUS/NZ Track A RFIC

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU**
Last updated: 2026-07-31. Pin assignments are *(estimate)*.

> **Integration model (updated):** the design is delivered as a **block footprint
> with specified pad types at fixed (organizer-scripted) placement**; the organizer
> integrates blocks into the padframe. Our deliverable is the **8-signal block
> interface** below, not a whole slot. The old `slot_0p5x0p5` mapping is retained
> as a **superseded appendix** for reference only.

---

## 1. Block signal interface (primary)

**8 signals + split supplies + common ground.**

| # | Signal | Dir | Pad type | Notes |
|---|--------|-----|----------|-------|
| 1 | **RF_OUTP** | out | analog | quadrature RF out, 2.4–3.2 GHz (VCO ÷2) |
| 2 | **RF_OUTN** | out | analog | quadrature RF out (differential) |
| 3 | **VTUNE** | in | analog | control voltage from off-chip loop filter |
| 4 | **CP_OUT** | out | analog | charge-pump output to off-chip loop filter |
| 5 | **REF_IN** | in | digital (input) | reference clock |
| 6 | **RST_N** | in | digital (input) | active-low reset (divider/PFD) |
| 7 | **MON_OUT** | out | digital (bidir→out) | divided-down VCO monitor |
| 8 | **IBIAS_CP** | in | digital (input), DC | external charge-pump bias (DC voltage); tied off if on-chip bias |

Supplies: **VDDA + VDDD** (split analog/digital, preferred). **Ground: chip-wide
common** (single node, shared across all blocks).

**Type tally:** analog **4** (RF_OUTP, RF_OUTN, VTUNE, CP_OUT) · digital **4**
(REF_IN, RST_N, MON_OUT, IBIAS_CP) · power **2** (VDDA, VDDD) · ground **1** (common).

---

## 2. Per-analog-signal ESD (design consideration)

Each analog pad carries **secondary ESD** structures that add shunt capacitance to
the signal. **RF_OUTP/RF_OUTN operate at 2.4–3.2 GHz**, where this pad + ESD C
directly loads the output — output-buffer sizing and any matching **must budget the
measured pad/ESD capacitance**. VTUNE (DC) and CP_OUT (low-frequency) are
insensitive. Tracked as a verification item (`verification.md`).

---

## 3. Fit vs. pin-accounting interpretation (pending organizer confirmation)

Two open interpretations of what counts toward a block's **pin total**:
**(i)** power (VDDA+VDDD) + common ground counted → block total **11**;
**(ii)** signals only → block total **8**. The binding physical resource is
**analog pads (4 needed)**; digital/power/ground are abundant in every config.

Configs A–E = the five padframe pad-budgets, by analog-pad count (from
`slot_defines.svh`); **D = slot_0p5x0p5** (current fit), **B = the 6-analog request
target**.

| Config | Analog pads | Fits (need 4 analog)? | Analog spare | Block total (i)/(ii) | Risk |
|--------|------------:|-----------------------|-------------:|----------------------|------|
| A | 2  | ✗ **no** | −2 | 11 / 8 | analog-starved — infeasible |
| **B** | 6  | ✓ | **+2** | 11 / 8 | comfortable — **request target** |
| C | 4  | ✓ tight | 0 | 11 / 8 | zero analog margin |
| **D** (0p5x0p5) | 4  | ✓ tight | 0 | 11 / 8 | zero analog margin — **current fit** |
| E (workshop) | 60 | ✓ | +56 | 11 / 8 | tutorial vehicle, not our slot |

- **Physical fit is interpretation-independent** — driven by the 4 analog pads.
  Configs C and D fit with **zero analog margin**; B adds +2; A cannot fit; E is not
  our slot.
- **The interpretation shifts only the declared total** (11 vs 8 = the 2 power + 1
  ground) and how the organizer tallies it — not which configs physically fit.

> **PENDING organizer (Bailey) confirmation of pin accounting.** Once (i) vs (ii)
> is fixed, one issue pin-line variant is posted (D-fit or B-request). Both drafts
> are staged.

---

## Appendix (SUPERSEDED): slot_0p5x0p5 full-frame mapping

*Retained for reference. The block-footprint model (§0) replaces per-slot pin
assignment; the organizer places pads. Do not treat as the live plan.*

`slot_0p5x0p5` frame: analog **4** (`analog[0..3]`, N edge), bidir 38, dedicated
input 4, `clk_pad`, `rst_n_pad`, DVDD 4, DVSS 4, 4 corners. Default mapping:
analog[0..3] → RF_OUTP/RF_OUTN/VTUNE/CP_OUT; `clk_pad`→REF_IN; `rst_n_pad`→RST_N;
a bidir→MON_OUT; an input→IBIAS_CP; DVDD/DVSS domain-split VDDA/VDDD/VSSA/VSSD.
Zero analog margin (4 of 4 used).
