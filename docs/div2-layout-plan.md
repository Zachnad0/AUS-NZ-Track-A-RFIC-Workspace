# DIV2_QUAD_v1 layout — plan + device inventory (prep, 2026-08-14 run #4)

**Status: PREP ONLY.** Run #4's container (`iic-osic-tools_xvnc` / Docker Desktop Linux
engine) was **down** for the whole run and could not be restarted (standing rule 1). All
layout/verification tools (magic, gencell, netgen, KLayout, xschem netlisting) live in that
container, so no DRC/LVS was run this session. This file is the host-only prep so the next
container-up run executes fast: the full device/net inventory (transcribed from the
authoritative generator `team_src/xschem/gen_div2_quad.py`, which the `.sch` is generated
from), the golden's transistor lines ready to paste, and the open device-syntax questions
that MUST be answered in-container before the golden is valid.

## Totals (matches run #3's netlist count: 59 FET + 12 R + 4 C)
- 12 CML-core nfet (W=40 L=0.3) + 3 NMOS-bias nfet + 4 converters × (6 nfet + 5 pfet) = **59 FET**
- 4 CML loads (300 Ω) + 4×(RFB 20k + R_SER 1k) = **12 R**
- 4× CC (100 fF) = **4 C**
- Ports (9): CK CKB IBIAS (in) · VDD VSS (io) · I_P I_N Q_P Q_N (out)

## New device geometries to de-risk BEFORE assembly (item 1a/1b, needs container)
| device | where | de-risk |
|---|---|---|
| **nfet W=40 L=0.3** | 12 CML core + 2 bias tails | 40 µm > W=4 the library was built on. Generate one, READ real S/D pitch + gate + tap y-coords; W=40 is 10× taller than W=4 so NO vertical constant carries over. 40 µm < 200 µm bin so nf=1 is fine, but a 40 µm-tall single finger may want nf>1 folding — decide from the generated geometry. |
| **nfet W=8 L=0.3 / L=1** | converter diff-pair + tail | standard-ish; same family as W=4, re-read if unsure. |
| **nfet W=4/11/16 L=0.3** | converter inverters | small, W=4 family. |
| **pfet W=8/10/26/44 L=0.3** | converter loads + inverters | pfet path proven (ib_ptest) at W=16; re-read W=44 (44 µm, still < 200). |
| **ppolyf_u_1k** | R_SER (1k), loads (300), RFB (20k) | gencell `magic::gencell gf180mcu::ppolyf_u_1k`, defaults `w 1 l 2 rho 1000 val 2000 class resistor`. **1 kΩ = 1 square → w=2 l=2** (or w=1 l=1). **300 Ω = 0.3 sq → w=2 l=0.6** (min L 1 µm may force snaking/lower-value strategy — CHECK gencell minL). **20 kΩ = 20 sq → w=1 l=20, or snake=1** (long; use snake to fold). READ each flavor's real terminal coords + DRC (poly res has its own spacing + the res-marker layer). |
| **CC cap 100 fF** | 4× | the `.sch` uses `capa.sym` (ideal). The LAYOUT needs a real gf180 cap flavor (MIM `cap_mim_*` or MOS cap). 100 fF: MIM ~ 100fF at ~ (area/Cdensity). READ the gencell + its LVS device name. This is the biggest unknown. |

## DF.14 for taps=0 CML devices — CLOSED (run #6, KLayout)
The taps=0 shared-pwell strategy passes DF.14_LV in KLayout (variant D) when a VSS
psubdiff tap strip runs below the device row (tested: strip at y-1120..-1000, clear of
the source-rail vias so no V1.2a). Each W=40 device is only ~4 um tall so one bottom
strip covers the whole single-row latch within the 20 um rule. If devices are stacked in
multiple rows, add a tap strip per row band.

## Resistor geometries — LOCKED (run #6)
Enlarged from the run-#5 first picks (same L/W ratio, bigger body, width >= 2um so end/
contact R is a small fraction and poly matches better -- the 300ohm are the CML loads that
set the ~703 mV swing via I*R, and w=1 is the gencell min where matching is worst):
**R_SER 1k = w2 l2 | CML load 300 = w10 l3 | RFB 20k = w2 l40** (20k is a 40um strip; snake
it in the converter layout if area needs it, and regenerate the golden to the snake form).
Locked in mk_div2_golden.py.

## Sub-block layout status — 1d DONE, 1e sub-blocks all PASS (run #6)
Every DIV2 building block is now individually magic-DRC-0 + LVS-match-uniquely against a
hand-typed sub-block golden (rule 12 governs only the FULL DIV2 golden). Assembly is the
only remaining step.
- **1d CML latch** — `ib_cml.tcl` (6 W=40 nfets + 2×300Ω), 9 ports. PASS, committed.
- **1e diff-pair front-end** — `ib_conv_dp.tcl` (M_NT tail W8L1 + input pair W8L0.3 + PMOS
  mirror W8L0.3), 6 ports. PASS. Gotcha fixed: pfet source→VDD risers must NOT share x with
  the drain vias (they short via the shared M3 via pad) — use an M2 source bridge + one M3
  riser at the far left.
- **1e inverters** — `ib_inv_gen.tcl` `make_inv {cell Wn Wp}` builds ALL THREE: INV1 (10/4),
  INV2 (26/11), INV3 (44/16). (This line used to cite a hand-built `ib_inv1.tcl`. Settled by
  history 2026-08-29, not by guesswork: that file was added in `e80f175` and DELETED the same
  day in `38f317d`, "unify inverters on one make_inv path; retire ib_inv1 one-off", which
  folded it into the proc and regenerated `ib_inv1.mag` from it. It was never renamed and no
  longer exists. Sizes are Wp/Wn and unchanged — `make_inv ib_inv1 4 10` is Wn=4, Wp=10.)
  All three PASS, 4 ports each. Reusable proc: every y-constant linear in Wn/Wp. INV3 is the
  tallest (~9µm risers) and passed first try.
- **Converter FET widths** — `derisk_nfetw.tcl` (W4/11/16) + `derisk_pfetw.tcl` (W10/26/44)
  both DRC 0. The W44 pfet gate M2 reaches YP+4608, so a shared nwell tap strip in the
  converter/DIV2 must sit ≥ YP+4800.
- **GOTCHA (single-finger devices)**: `nfet_leg`/`pfet_leg` with `taps=1` paint NO substrate
  tap on a single-finger device — `welltap`'s loop starts at `xoff-maxc+252`, already past
  `xoff+maxc` when maxc≈82, so the pwell floats and extracts as VSUBS (not VSS). ALL diff-pair
  and inverter FETs are single-finger → use `taps=0` + an explicit pwell/nwell + VSS/VDD tap
  strip (the diff-pair/CML pattern). Wide CML devices (maxc large) are unaffected.
- **NEXT (1e assembly)**: flat converter cell — place the 5 front-end FETs + 6 inverter FETs +
  CC MIM cap (100f w5 l10, m4/m5) + RFB 20k (w2 l40) + R_SER 1k (w2 l2), wire
  OC→CC→G1, RFB S1→G1, G1→INV1→S1→INV2→S2→INV3→S3→R_SER→OUT. Then 1f: 2 latches + 3 NMOS
  bias + 4 converters, 9 ports, `verify_cp.sh DIV2_QUAD_v1` exit 0 (golden via mk_div2_golden.py).

## W=40 CML device strapping — VALIDATED (run #5)
`place_nfet 10 x M 0.3` + `nfet_leg 10 x gc 0.3 yoff **taps=0**` → strapped W=40 (w4 nf10),
magic DRC 0, netgen 10 fingers → match uniquely m=10 (total W=40). **The per-device tap MUST
be off (taps=0)**: at L=0.3 pitch 164 the welltap sits at P/2=82 from the array edge, only
~0.15 µm from the outer source via → V1.2a (via1 spacing). So the CML devices share ONE pwell
with taps painted in clear field (the ibias-cascode pattern). The strap S/D/gate rails come
out UNLABELED; the CML driver routes each device's three rails to its specific topology net
(TAILA/nTA/nLA/OI/OIB/CK/CKB/VDD) — CML is not a common-source/gate mirror, so every device's
rails go to different nets.

## RESOLVED device forms (run #5, in-container)
- **Resistor** extracts as `X<name> <e1> <e2> <bulk> ppolyf_u_1k r_width=Wu r_length=Lu`
  (3-terminal: two poly ends + a psubdiff guard = bulk → VSS). netgen matches uniquely and
  **checks r_width/r_length**, so the golden geometry must equal the drawn geometry. Terminal
  tap = paint metal1 over the end **polycontact** (NOT the full-width guard-ring metal1).
  Geometries chosen: R_SER 1k = w2 l2 · CML load 300 = w5 l1.5 · RFB 20k = w1 l20.
- **Cap** extracts as `X<name> <top> <bot> cap_mim_2f0_m4m5_noshield c_width=Wu c_length=Lu`
  (2-terminal, MIM on m4/m5, 2 fF/µm²). 100 fF = 50 µm² → **w5 l10**.
- **Golden is GENERATED** by `team_src/magic/phase5/mk_div2_golden.py` (netlist .sch → keep
  FETs, map R→ppolyf_u_1k, C→cap_mim). Output `DIV2_QUAD_v1_golden.spice`, 75 devices.
- **W=40 CML nfet**: fold as **w=4 nf=10** (L=0.3, pitch 164) to reuse the proven W=4
  vertical strap constants; total W=40 < 200 µm bin. `pitch_for_L` generalized to
  `200*L+104` (504/304/164 at L=2/1/0.3). CML devices need CUSTOM per-terminal routing
  (they are not a common-source/gate mirror array), so `nfet_leg` does not apply directly.

## (historical) OPEN QUESTIONS — now answered above
1. **ppolyf_u_1k LVS representation.** netgen may see it as an `R` element (value) or as a
   subckt `ppolyf_u_1k` with PLUS/MINUS/BODY pins. Extract one strapped resistor and read
   the `.lvs.spice` device line — the golden's 12 resistors must use that exact form. Ideal
   `device=resistor` in the `.sch` netlist will NOT match a ppolyf_u_1k layout device unless
   the golden is written in the layout device's form (or netgen `property` maps it).
2. **Cap device + LVS form.** Which gf180 cap flavor realizes 100 fF cleanly, and how does
   netgen name it? The golden's 4 caps must match.
3. **verify_cp.sh resistor/cap handling.** verify_cp extracts + LVSes vs the golden; confirm
   it does not need an `ignore`/property tweak for the res/cap models (the fillcap ignore is
   already in the setup).

## Golden — TRANSISTOR lines (faithful, ready to paste; nets/sizes from the generator)
Format `X<name> D G S B <model> L=<>u W=<>u nf=1 m=1`. Ports order = `.sch` subckt:
`CK CKB IBIAS I_P I_N Q_P Q_N VDD VSS` (confirm exact order by netlisting the .sch).

```
* --- CML core (12x nfet W=40 L=0.3, bulk=VSS) ---
XMA1 OIB  OQ  nTA   VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMA2 OI   OQB nTA   VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMA3 OIB  OI  nLA   VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMA4 OI   OIB nLA   VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMA5 nTA  CK  TAILA VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMA6 nLA  CKB TAILA VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMB1 OQB  OIB nTB   VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMB2 OQ   OI  nTB   VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMB3 OQB  OQ  nLB   VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMB4 OQ   OQB nLB   VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMB5 nTB  CKB TAILB VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
XMB6 nLB  CK  TAILB VSS nfet_03v3 L=0.3u W=40u nf=1 m=1
* --- NMOS bias mirror off IBIAS (L=1, bulk=VSS) ---
XM_BREF  IBIAS IBIAS VSS VSS nfet_03v3 L=1u W=4u  nf=1 m=1
XM_TAILA TAILA IBIAS VSS VSS nfet_03v3 L=1u W=40u nf=1 m=1
XM_TAILB TAILB IBIAS VSS VSS nfet_03v3 L=1u W=40u nf=1 m=1
* --- 4x converter (tag IP/IN/QP/QN); INP,INM,OUT per tag below ---
* per tag T with (INP,INM,OUT):  IP:(OIB,OI,I_P) IN:(OI,OIB,I_N) QP:(OQB,OQ,Q_P) QN:(OQ,OQB,Q_N)
* XM_NT_T   NS_T  IBIAS VSS  VSS nfet L=1u   W=8u
* XM_BN1_T  DN1_T INP   NS_T VSS nfet L=0.3u W=8u
* XM_BN2_T  OC_T  INM   NS_T VSS nfet L=0.3u W=8u
* XM_BP1_T  DN1_T DN1_T VDD  VDD pfet L=0.3u W=8u
* XM_BP2_T  OC_T  DN1_T VDD  VDD pfet L=0.3u W=8u
* XM_IP1_T  INVO1_T G1_T   VDD VDD pfet L=0.3u W=10u
* XM_IN1_T  INVO1_T G1_T   VSS VSS nfet L=0.3u W=4u
* XM_IP2_T  INVO2_T INVO1_T VDD VDD pfet L=0.3u W=26u
* XM_IN2_T  INVO2_T INVO1_T VSS VSS nfet L=0.3u W=11u
* XM_IP3_T  INVO3_T INVO2_T VDD VDD pfet L=0.3u W=44u
* XM_IN3_T  INVO3_T INVO2_T VSS VSS nfet L=0.3u W=16u
* CC_T   (cap)  OC_T   - G1_T        100f  -> real cap device (TBD)
* RFB_T  (res)  INVO1_T- G1_T        20k   -> ppolyf_u_1k (TBD form)
* R_SER_T(res)  INVO3_T- OUT         1k    -> ppolyf_u_1k (TBD form)
```
(NOTE: nfet terminal order in the golden is D G S B; the generator's `nfet(G,D,S,B)` maps to
`X D G S B`. Verify against the actual `.sch` netlist once the container is back — do not
trust this transcription blind for signoff.)

## Floorplan approach (model on ibias_gen_v1's flat four-row assembly)
- **CML core**: 2 latches (MA*, MB*), each = tail pair (MA5/MA6) + input pair (MA1/MA2) +
  cross-coupled pair (MA3/MA4). W=40 devices dominate area. Differential -> keep OI/OIB and
  OQ/OQB pairs symmetric (common-centroid the cross-coupled MA3:MA4 and MB3:MB4).
- **300 Ω loads** sit above the CML to VDD (4 resistors).
- **NMOS bias** (M_BREF diode + 2 tails) as a small mirror row (reuse the nfet_leg mirror
  pattern; tails are W=40 like the CML).
- **4 converters** as 4 identical columns (generated once, placed ×4 — the generator-proc
  approach), each: diff pair + PMOS mirror load + CC + RFB + 3 inverters + R_SER.
- Routing by layer-per-net-class (M2 intra, M3/M4 crossings, M5 power) as in ibias.
- de-risk order per queue: 1a W=40 nfet -> 1b R/C -> 1c one CML latch -> 1d one converter ->
  1e full assembly + `verify_cp.sh DIV2_QUAD_v1` exit 0.

## Golden source-of-truth
Generate the golden by **netlisting the current `.sch`** in-container (it is the validated
design, commit f600af3 — do NOT edit it), then transform the ideal R/C into the layout device
forms per the open questions above. The transistor lines here are a faithful preview to speed
that up, not a substitute for the real netlist.
