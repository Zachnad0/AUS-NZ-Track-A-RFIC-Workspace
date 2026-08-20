# Tapeout handoff — browser / human-only tasks (Phase-7 item 6, 2026-08-20)

Everything below needs a human in a browser (GitHub write, Google/Bailey sheet,
weekly form) or a decision — none can be done from the EDA container. Current
ground truth, measured on the committed deliverable GDS this session:

| Fact | Value |
|------|-------|
| Die size | **522 × 309 µm** |
| Die area | **161,298 µm² ≈ 0.161 mm²** |
| Pin count | **12** (config B: 1/8 die, 16-pin budget → **4 spare**) |
| Pin breakdown | ground 1 (VSSA) · power 2 (VDDA, VDDD) · analog 8 (IBIAS, ISS, VTUNE, CP_OUT, I_P, I_N, Q_P, Q_N) · digital 1 (REF_IN) |
| Pin order (info.yaml) | VSSA, VDDA, IBIAS, ISS, VTUNE, CP_OUT, I_P, I_N, Q_P, Q_N, VDDD, REF_IN |
| Chip signoff | `verify_cp chip_top` → magic DRC 0, LVS **match uniquely**, KLayout var-D **168 = W4 varactor waiver only**; 5-block regression all PASS |

## 1. Issue #143 — update the area + pin lines

**Do NOT touch the existing `blob/main/...` link targets in the issue** — only
swap the area/pin numbers, leaving the surrounding text and links intact.

- **Area line →** `Area Estimate: 522 × 309 µm = 161,298 µm² (≈ 0.161 mm²), measured on the routed chip_top GDS`
  (was 350 × 300 µm — stale, pre-layout).
- **Pin line →** `Pin count: 12 (config B, 16-pin budget, 4 spare) — 1 ground (VSSA), 2 power (VDDA/VDDD), 8 analog (IBIAS, ISS, VTUNE, CP_OUT, I_P, I_N, Q_P, Q_N), 1 digital (REF_IN)`
  (was 11 / 13 in older drafts — final is 12, one common ground pin).

## 2. Bailey's allocation sheet

Paste-ready row values:

- **Project / team:** A01 — GF180MCU integer-N PLL RFIC (2.4–2.5 GHz)
- **Config:** B (1/8 die share, 16-pin total)
- **Die footprint:** 522 × 309 µm (161,298 µm²) — ~20 % of the config-B share
  (~624,000 µm²); comfortable margin.
- **Pins used / budget:** 12 / 16
- **Ground:** 1 quiet down-bonded quadrant ground (VSSA, pin 0)
- **Signoff status:** chip LVS clean (match uniquely), magic DRC 0, KLayout
  var-D clean except the W4 nmoscap varactor waiver (168 device-internal items).

## 3. Weekly form

- **Area estimate:** 522 × 309 µm (161,298 µm²) — now measured, not estimated.
- **Pin count:** 12 (4 spare in config B).
- **Status / on-track:** On track. chip_top placed, routed, LVS-clean; Phase-7
  tapeout items (DIV2 VDD EM tap, VCO_OUTP/N length match, lvs_config repoint,
  docs) complete this week. Remaining: organizer-side signoff LVS (see the VCO
  device-extraction note in §4) and the ground-net decision (§4).

## 4. Question for Bailey (ground net) + a signoff-LVS heads-up

**Ground-net question (paste-ready):**
> Our layout uses a single ground net — all VSS ties the shared p-substrate
> (no deep-nwell), so LVS carries one ground port (VSSA), and the pin list is 12.
> Do you want a second *isolated* ground (e.g. a separate quiet analog ground)?
> That would require deep-nwell isolation to split the substrate return — a
> block-level change, not a pad add. As drawn there is one electrical ground; the
> die still bonds ground at several ring points (a bond/package detail). Confirm
> whether one common ground is acceptable for the shared padframe.

**Signoff-LVS heads-up (from item 1 validation — see `docs/lvs-config-validation.md`):**
> Our `lvs_config.json` is structurally identical to your
> `user_project_wrapper.json` template (SPICE source instead of Verilog). One
> caveat for the signoff LVS: a **flat GDS extraction will not reproduce our
> `match uniquely`** on the VCO — magic extracts **zero capacitors** from the
> nmoscap_3p3 varactors and cannot see the spiral inductor from flat GDS. Our
> `verify_cp` passes only because `chip_top.abstract` pre-loads device-aware
> `.mag` cells (`vco_varactors`, `vco_inductor_v2`) before `gds read` and adds
> `ignore class vco_inductor_v2` to netgen. The VCO tank needs device-aware
> handling (abstract preload or black-box) in the organizer's LVS.

## What was NOT done (by rule / by access)

- **No push.** 4 local commits sit on `integration` ahead of `origin` (item 2,
  item 3, items 4+5, item 1). Push is a separate, in-the-moment approval.
- **#143 / Bailey sheet / weekly form** are all browser writes — human action.
- #143's `blob/main` link targets were left untouched (as instructed); only the
  area/pin *values* above need editing.
