# Which analog pins need a secondary ESD clamp — decision record

**Status:** decision record, 2026-08-25. Records the evidence and the rule it rests on so the
conclusion can be re-derived or overturned cleanly. **The rule is organizer GUIDANCE relayed in
conversation, not a confirmed written spec — see "What this rests on" below.**

## The rule

**Secondary ESD is mandatory only on pins that drive a GATE.** Pins landing on a diffusion do
not require one, because the failure mode the secondary clamp exists to prevent is gate-oxide
rupture: the primary clamp in the pad cell bounds the pad against the padring rails, and the
secondary bounds the *core-side* node against the *core* rails so the thin oxide never sees the
residual. A diffusion terminal has no thin oxide to rupture; it fails, if at all, by junction
breakdown, which the primary already covers.

**Attributed to jsmoya**, relayed by Greg 2026-08-25. See caveats at the end.

## The evidence — every analog pin traced to its first device terminal

Traced through `team_src/magic/chip_top_golden.spice`, following the net through 2-terminal
passives (the series resistors) to the device terminal on the far side. Terminal roles are the
model port orders: FET `(drain, gate, source, bulk)`; `cap_nmos_03v3_b` `(B, G)` — confirmed
from the PDK symbol's pin numbering, B is pin 1 and G is pin 2; diode `(anode, cathode)`.

| pad | verdict | proving device and terminal |
|-----|---------|------------------------------|
| **IBIAS** | **GATE + DIFFUSION** | `ibias_gen_v1/XMNC0 nfet_03v3` — diode-connected, the net is on **both drain and gate** |
| **ISS** | DIFFUSION | `vco_v1/XM1 nfet_03v3` **source** — the LC-VCO tail node |
| **VTUNE** | DIFFUSION | `vco_v1/XC1,XC4 cap_nmos_03v3_b` **bulk/well** (port 1 = B). The tank swings on the varactor GATE (`OUT_p`/`OUT_n`); the tune voltage sits on the diffusion side, behind a 15 kohm `XR2` |
| **CP_OUT** | DIFFUSION | `CP_v1/XM_PSW pfet_03v3` drain and `XM_NSW nfet_03v3` drain |
| **I_P** | **GATE + DIFFUSION** | `DIV2/XM_IP3_IP,XM_IN3_IP` drains, **and** `PFD_lib` FB -> `X2 dffrnq_1` **CLK** -> `X_tn10 nfet_05v0` **gate** |
| **I_N** | DIFFUSION | `DIV2/XM_IP3_IN,XM_IN3_IN` drains |
| **Q_P** | DIFFUSION | `DIV2/XM_IP3_QP,XM_IN3_QP` drains |
| **Q_N** | DIFFUSION | `DIV2/XM_IP3_QN,XM_IN3_QN` drains |

**Only two of the eight reach a gate: IBIAS and I_P.**

`I_P` is the asymmetric one and it is easy to miss: it is the only I/Q pin that reaches a gate,
and it does so because it doubles as the PLL loop feedback. `I_N`, `Q_P` and `Q_N` have no
feedback path and are diffusion-only. Note also that `I_P`'s gate is a **5 V** std-cell device
(`gf180mcu_fd_sc_mcu7t5v0`), and that its gate sits on the PAD side of `XR_SER_IP` — the 1 kohm
protects the driver's drain, not the gate. See `docs/verification.md` 8.10.

## What is built, and what the rule implies

| pin | gate? | clamp built? | required under the rule? |
|-----|-------|--------------|--------------------------|
| IBIAS | yes | **yes** (`7391653`, relocated `5eda5b6`) | **yes** |
| ISS | no | **yes** (`914bcdf`, relocated `7aedc20`) | no — built anyway |
| I_P | yes | no | **yes**, unless the pad is removed |
| VTUNE, CP_OUT, I_N, Q_P, Q_N | no | no | no |

**ISS was built before this rule was known.** It is not required by it. It is kept: it is
already gated clean, it costs nothing further, and ISS is the VCO tail return where a clamp to
the core rails is defensible on its own merits. Removing it would be churn for no gain.

**I_P is the one open requirement**, and it interacts with a separate decision: option B
(removing `I_P` from the pin list to fix the loop-feedback RC problem in `docs/verification.md`
8.10). If B goes ahead, `I_P` stops being a pad and the requirement disappears with it. If B
does not, `I_P` needs a clamp — and it is the pin where the 400 um2 / 564 fF loading objection
is sharpest, because it is a 2.4-3.2 GHz output.

## What this rests on, and what would change it

**This is organizer guidance relayed in conversation. It is not a written spec, we have not
seen it in the DRM or in the Chipathon documentation, and it has not been confirmed in
writing.** The whole reduction from eight clamps to two depends on it.

**If jsmoya comes back and says every analog pin needs a secondary clamp regardless of what it
lands on**, then:

- six more clamps are required: VTUNE, CP_OUT, I_N, Q_P, Q_N, and I_P (or five, if B removes
  I_P). Each is the same structure already built twice: `esd_pd2nw` + `esd_nd2ps` + tabs +
  M2 frames + a VSSA strap, plus a ballast where the pin has none;
- **the open sizing question becomes load-bearing again.** The organizers' reference cell is
  400 um2 / 160 um perimeter per diode. On CP_OUT and VTUNE that is leakage into an off-chip
  loop filter; on the I/Q outputs it is **564 fF, an 88-118 ohm shunt across 2.4-3.2 GHz**. A
  thin-strip diode holds 25 um of perimeter in 5.4 um2 and would cut that ~40x. Whether
  perimeter alone carries the CDM spec is still unanswered;
- the two clamps already built do not change. The relocation work does not change.

**If the rule holds**, the remaining work on this rung is zero once I_P is resolved.

## Cross-references

- `docs/verification.md` 8.10 — the padring capacitance that makes `I_P`'s feedback path fail,
  and why no gate we run can see it
- `docs/verification.md` 8.9 — why substrate and well ties need a physical argument, not an LVS
  result; it is why the clamps carry real VSSA straps
- `docs/gf180-de3-deck-defect.md` — unrelated PDK deck defect found while doing this work
