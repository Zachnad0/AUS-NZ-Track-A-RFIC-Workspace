# Phase 1 — LVS representation throwaways (transistor-level)

Settles how PDK-generator devices (`nfet_03v3`/`pfet_03v3`) extract and how netgen
matches them against a schematic-style golden, BEFORE any real block layout exists.
All results are file-read from real Magic extraction + netgen runs in the
`iic-osic-tools_xvnc` container (`sak-pdk gf180mcuD`).

## Findings

1. **Extraction form.** A generator device flattened into the top cell extracts as
   `X<n> D G S B <device> ad=.. pd=.. as=.. ps=.. w=<W>u l=<L>u` (lowercase w/l,
   plus S/D area+perimeter; no nf/m — those are folded into geometry). See
   `p1_pair.spice`, `p1_m4.spice`.
2. **No def-vs-blackbox mismatch at transistor level.** netgen treats
   `nfet_03v3`/`pfet_03v3` as pin-only **black-box placeholders**. The extracted
   lowercase `w/l` and the golden's uppercase `L/W nf m` MATCH UNIQUELY under the
   **stock** `gf180mcuD_setup.tcl` — no ignore/waiver needed. (`p1_pair.comp.out`)
   The std-cell def-vs-blackbox problem does NOT recur here.
3. **W/L are checked (1% cutoff) but only as "property errors".** netgen still
   prints "Circuits match uniquely" when device sizes are wrong; the size deltas
   come out separately as property errors (`p1_wrong.comp.out`:
   `l circuit1: 2e-06 circuit2: 8e-06 (delta=120%, cutoff=1%)`). A wrongly-sized
   layout would therefore PASS a naive "match uniquely" grep. `verify_cp.sh` was
   hardened to hard-fail (exit 1) on any property error.
4. **`m` = discrete units.** `magic::gencell ... m 4` draws **4 discrete unit
   devices** (common bulk, separate S/D/G), DRC 0 — not one folded device
   (`p1_m4.spice`). Once strapped in parallel, netgen parallel-combines them to a
   single equivalent device and matches EITHER golden form — one `m=4` line
   (`m_form1.spice`) or four `m=1` lines (`m_form2.spice`) — both "match uniquely",
   "Number of devices: 1|1" (`m_f1.out`, `m_f2.out`). So the ibias golden may use
   either representation; the layout must present the `m` units and strap them.

5. **`w` is per-finger; netgen sums combined widths.** `nf=10 w=5` extracts as 10
   discrete `w=5u` fingers (shared-diffusion chain); `nf=10 w=50` → 10x `w=50u`
   (=500um) — so `w` is per-finger, not total (`nf10_w5.spice`, `nf10_w50.spice`).
   When the fingers are strapped in parallel netgen SUMS widths: 10x w=5 matches a
   single `W=50u` golden with NO property error, but a `W=5u` golden property-errors
   (`strap10.spice` vs `g_w50/g_w5`). Same for `m`: 4x w=5 matches `W=20u`, errors
   vs `W=5u`. => CP_v1's `nf=10 @ 5um` layout matches `CP_v1_golden.spice`'s `W=50u`
   cleanly; the hardened gate does not false-fail. REQUIRES correct strapping
   (gates common, alternating S/D common) for the combine to fire.

## Files
- `p1_probe.tcl/.spice` — single-device probe: shows the auto-named wrapper subckt.
- `p1_pair.tcl/.mag/.spice` + `p1_pair_golden.spice` + `p1_pair.comp.out` —
  1 nfet + 1 pfet, matches uniquely (throwaway 1).
- `p1_wrong_golden.spice` + `p1_wrong.comp.out` — wrong-size negative control.
- `p1_m4.tcl/.spice` + `p1_m4b.mag` — generator `m=4` → 4 discrete units.
- `m_layout/m_form1/m_form2.spice` + `m_f1/m_f2.out` — netgen m-form equivalence.
- `nfet_03v3_*.mag`, `pfet_03v3_*.mag` — generated device geometry (terminal coords).

## Method note (for Phase 5)
Generator device cells carry **no port labels** (`port list` empty). Connectivity
must come from metal + labels added at assembly time. Terminal metal1 tab
coordinates are in the device `.mag` (e.g. `nfet_03v3_*.mag`).
