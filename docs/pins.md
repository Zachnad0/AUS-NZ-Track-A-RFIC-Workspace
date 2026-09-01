# Pin / Pad Plan — AUS/NZ Track A RFIC

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU**
Last updated: **2026-09-01**. Slot variant **BH**; pin list frozen for the Aug 28 DEF gate.

> **CORRECTED 2026-09-01 — this file said 13 pins with `I_P` at #9 until today, and that was
> stale by five days.** `I_P` came off the pad list at commit `020852a`, and the correction was
> confirmed against the organizer-issued 12-pin package at `5e55d14`
> (`padframe/A01/project_defs_12pin/BH/A01_BH_interface.yaml`, `participant_pin_count: 12`).
> The authoritative pin list is `info.yaml`'s `pins:` block — **12 entries** — and the LVS
> golden `team_src/magic/chip_top_golden.spice` carries **11 ports** (VSSD is a declared pad
> but the same on-chip node as VSSA, so it is not a separate golden port). §1, §2 and §3 below
> are corrected to that. Only prose changed here; no pin entry, no layout, no netlist.

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

The divider produces four quadrature phases and **4 monitor-grade RF output buffers**
(~2.4–3.2 GHz) drive them; **three of the four reach pads** (`I_N`, `Q_P`, `Q_N`). The
fourth, `I_P`, stays on-chip — see the `I_P` note below. Pin order is the `info.yaml`
order (clockwise from bottom-left, upper-left quadrant); slot letters are read from
`padframe/A01/project_defs_12pin/BH/A01_BH_interface.yaml`.

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
| 9 | **Q_P** | out | analog | quadrature output + (N04) |
| 10 | **VSSD** | — | ground | digital-island ground (N05). Same on-chip node as VSSA; see the VSSD note below. |
| 11 | **VDDD** | — | power | digital supply (N06) |
| 12 | **REF_IN** | in | digital | reference clock (N07). Expands on the pad to REF_IN/PU/PD — PU=0, PD=1 (weak pull-down). |

**Tally:** analog **7** · digital **1** · power **2** · **ground 2** (VSSA, VSSD).
**Block pin total = 12.** chip_top carries **11 LVS ports**: VSSD is the 12th *pad* but is the
SAME internal node as VSSA (one p-substrate, no deep-nwell), so the golden does not give it a
separate port. The organizers' own scrape reads it — `A01_BH_interface.yaml`'s `top_cell_text`
lists `text: VSSD / layer: 36 / datatype: 0`.

> **`I_P` REMOVED FROM THE PAD LIST (2026-08-27, commit `020852a`; confirmed against the real
> 12-pin package at `5e55d14`).** `I_P` is now an **internal net**: `DIV2_QUAD_v1.I_P` →
> `PFD_lib.FB`, and that is how the PLL loop closes. It is not a pad and not a golden port.
>
> **Why it had to go — an RC failure no gate we run could see** (`docs/verification.md` §8.10).
> The PFD's FB tapped `I_P` on the **pad side** of the 1 kΩ `XR_SER_IP`, so the feedback clock
> reached `dffrnq_1`'s CLK through 1 kΩ into the pad's 875 fF: **τ = 912 ps against a 416.7 ps
> period — 11.4 % swing at 2.4 GHz. The loop would not have locked.** Removing the pad drops
> that node to ~23 fF (τ ≈ 23 ps, > 99.9 % swing) and touched **no signed-off block**. The
> padring load sits outside `chip_top`, which is exactly why DRC, LVS and every placement gate
> passed while the loop was broken.
>
> Two consequences that were checked, not assumed: `Q_P` inherited `I_P`'s N04 pad **and its
> jog x** (185.0) — without that it merged into `CP_OUT`'s lane, caught by LVS. And `I_P`'s own
> text inside `DIV2_QUAD_v1`'s GDS had to be demoted to datatype 0, or extraction returned 12
> ports against the golden's 11. It is still visible as `text: I_P / layer: 34 / datatype: 0`
> in the organizers' scrape — a useful probe that their reader does see datatype-0 text.
>
> **ESD consequence:** under the gate-rule in §2 / `docs/esd-which-pins.md`, `I_P` was one of
> only two analog pins that reached a gate and therefore needed a secondary clamp. It is no
> longer a pad, so that requirement disappeared with it.

> **Slot variant BH — 1110 × 550 µm landscape (Greg, 2026-08-22).** Slots **W18–W22**
> (VSSA, VDDA, IBIAS, ISS, VTUNE) + **N01–N07** (CP_OUT, Q_N, I_N, Q_P, VSSD, VDDD,
> REF_IN) — N01–N08 with `I_P` at N04 until it came off the list; everything from Q_P onward
> shifted one slot west (−100.000 µm exactly, the north slot pitch). Chosen over BV for aspect match to the 522 × 309 core and a ~241 µm I/Q haul to
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

> **I/Q pad order — now Q_N, I_N, Q_P at N02–N04** (was Q_N, I_N, I_P, Q_P at N02–N05 on
> 2026-08-22; `I_P` removed 2026-08-27 and Q_P took its N04 slot). The ordering rationale
> below is unchanged and still governs the three surviving outputs. Left taps → left pads, per
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

**`secondary_esd: false` on all seven analog pins (2026-08-22; eight until `I_P` came off the
list 2026-08-27).** Bailey: *"Set the secondary_esd to false, and then add it yourself to the
circuit and layout."* The padframe generator adds nothing, so declaring `true` would claim
protection the GDS does not have. The clamps (diode perimeter > 25 µm plus a > 50 Ω series
poly resistor) are ours to build and are a **final-data** item, not an Aug-28-gate item.

**Built so far: 2 of 7** — `IBIAS` (commit `7391653`, relocated `5eda5b6`) and `ISS`
(`914bcdf`, relocated `7aedc20`). Under the gate-rule in `docs/esd-which-pins.md` that is
**complete**: only pins that drive a gate need a secondary clamp, `IBIAS` and `I_P` were the
only two that did, and `I_P` is no longer a pad. **That rule is organizer guidance relayed in
conversation — it is not a written spec and has not been confirmed in writing.** If it does
not hold, five more clamps are required (VTUNE, CP_OUT, I_N, Q_P, Q_N).

Each analog pad carries **secondary ESD** structures adding shunt capacitance.
**I_N/Q_P/Q_N operate at 2.4–3.2 GHz** (VCO ÷2), where pad + ESD C loads the
output — the output-buffer sizings **must budget the measured pad/ESD C**. On the organizers'
reference geometry that is ~564 fF, an 88–118 Ω shunt across the band. VTUNE, CP_OUT, IBIAS
(DC / low-freq) are insensitive. Verification item — **no ESD simulation of any kind has been
run**; the clamps are verified structurally (DRC + LVS inside `chip_top`) only.

> **Bias-pad rename (2026-08-04):** `IBIAS_CP` → **`IBIAS`**, a chip-level bias
> reference. One external 240 µA feeds an on-chip bias generator that fans out to
> both the charge pump (~50 µA) and the DIV2 CML tails (2.4 mA each). This matches
> `CP_v1`'s stated end-state (mirrored bias from the PLL bias generator). **Pin
> count is unchanged by the rename (still one analog-DC pad).** Issue #143's
> pin-line wording may need to follow this rename (Greg to update — external).

---

## 3. Config fit (against the real proposal totals)

Block needs **12 pins** (analog 7 + digital 1 + power 2 + ground 2). The
binding constraints are **total pin count** and **per-block power** — *not* an
analog-pad budget (each project picks its own pad types within its total).

| Config | Pin total | Fits (need 12)? | Spare | Verdict |
|--------|----------:|-----------------|------:|---------|
| A | 22 | ✓ | 10 | oversized for the block |
| **B** | 16 | ✓ | **4** | **chosen fit** |
| C | 6  | ✗ | −6 | too few pins |
| D | 10 | ✗ (12 > 10) | −2 | too few pins |
| E | 6  | ✗ | −6 | too few pins |

- **Primary: config B (16 pins) — fits the 12-pin block with 4 spare** (RST_N/MON_OUT
  dropped 2026-08-20, ISS + VSSA ground added 2026-08-20, VSSD added 2026-08-22, `I_P`
  removed 2026-08-27, see §1). Confirmed by the organizer-issued package:
  `padframe/A01/project_defs_12pin/BH/A01_BH_interface.yaml` → `participant_pin_count: 12`.
- **Slot BH allocates 1110 × 550 µm = 610,500 µm² (`usable_area: 610500`), and that is the
  declared die.** `gds/chip_top.gds` is drawn to it: KLayout gives top cell `chip_top`,
  dbu 0.005, top bbox and layer 0/0 boundary both `(0,0;1110,550)`. **The 522 × 309 µm figure
  is the ROUTED CORE, not the die** — it is what the block cluster plus its routing occupies
  inside the slot, and it is the number still quoted in issue #143. Do not use it as the die.

---

## Appendix (SUPERSEDED): wafer.space slot frame

*Retained for reference only. The organizer padframe-proposal model (above)
replaces this; the `slot_*` yamls / `slot_defines.svh` are used only to drive the
LibreLane toolchain / sample-GDS proof (`verification.md` §6), not for our pin
allocation.* `slot_0p5x0p5`: analog 4, bidir 38, input 4, clk/rst, DVDD 4, DVSS 4.
