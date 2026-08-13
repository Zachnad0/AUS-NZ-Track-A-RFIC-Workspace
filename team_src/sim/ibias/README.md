# IBIAS generator sims (Phase 2, S1–S7) — reproducible decks

All ngspice, TT/3.3 V/27 °C unless the deck says otherwise. Run in the
`iic-osic-tools_xvnc` container after `sak-pdk gf180mcuD`. Results are recorded in
`docs/verification.md` §2.6.

## Regenerate the included subckts (if the .sch changed)
From `team_src/xschem`:
```
xschem -n -q -o <out> ibias_gen_tb.sch   # then extract the subckt:
awk '/^\.subckt ibias_gen_v1/{p=1} p{print} /^\.ends/{if(p)exit}' ibias_gen_tb.spice > ibias_sub.spice
xschem -n -q -o <out> CP_v1.sch          # then wrap the 8 devices as CP_core (7-port, no ideal sources):
{ echo '.subckt CP_core UP DOWN CP_OUT VDD VSS VGP VGN'; \
  awk '/^XM_PREF/{p=1} /^I_PREF/{p=0} p{print}' CP_v1.spice; echo '.ends'; } > CP_core.spice
```
`ibias_sub_shared.spice` = `ibias_sub.spice` with MP2c cascode gate VBCPD→PA
(S4b control experiment).

## Decks
| deck | S | measures |
|---|---|---|
| `ibias_op.spice` | S2/S6 | branch currents VGP/VGN/DIV2 + CP added-mismatch; corner via `sed 's/ngspice CORNER/ngspice ff/'` (typical/ff/ss) |
| `ibias_compliance.spice` | S4 | output-node compliance windows per branch |
| `ac_test.spice` | S4b | IB_DIV2→VGN AC coupling; swap `ibias_sub_active.spice` between `ibias_sub` (separate) and `ibias_sub_shared` (shared) |
| `s5_gen.spice` | S5 | CP UP/DOWN source & sink vs CP_OUT, generator-driven (ideal baseline = run `CP_dc_tb.sch`) |
| `ibias_psrr.spice` | PSRR | VGP/VGN/DIV2 vs VDD 3.0–3.6 V |

Run: `ngspice -b <deck>.spice`. Input-current gain sweep (S4) uses `ibias_gen_tb.sch`
netlisted + a `dc I_BIAS 120u 360u` control.

## Headline numbers (TT)
VGP 50.00 µA, VGN 49.91 µA, IB_DIV2 239.56 µA. CP added-mismatch: FF 0.004 %,
TT 0.18 %, SS 0.94 % (process tracking only — random mismatch needs Monte Carlo).
PSRR: VGP 0.003 %/V, VGN/DIV2 1.16 %/V. Reference is a forced current.
