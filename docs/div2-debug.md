# DIV2_QUAD_v1 — debug state (2026-08-04)

**STATUS: WIP — does NOT divide cleanly yet.** The cell is built, netlist-clean,
and wired correctly device-by-device, but simulation is non-functional. This file
lets a fresh session resume cold without re-deriving. Do not treat DIV2_QUAD_v1 as
verified.

## What it is
CML ÷2 quadrature divider packaged as a subcircuit: 12-nfet CML core (2 master-slave
D-latches) + NMOS 10:1 bias mirror off `IBIAS` + 4× NMOS-input CML→CMOS output converters
→ **1 kΩ** on-chip series R → I_P/I_N/Q_P/Q_N.
Design decisions (Greg, 2026-08-04): IBIAS = chip-level bias, external **240 µA**,
mirror **10:1** → **2.4 mA/tail** (4.8 mA core total). Series isolation R relocked
450 Ω → **1 kΩ** on 2026-08-10 (see the 2026-08-10 section). See `pins.md`,
`verification.md` §7.
> The converter description below (single "diff converter + inverter") is the
> 2026-08-04/05 version; it was rebuilt as a 3-stage chain on 2026-08-10 (still
> non-working — see that section). Front matter kept for continuity.

## Files
- Cell:   `team_src/xschem/DIV2_QUAD_v1.sch` (**59 FET + 12 R + 4 caps** — the "45 FET +
  8 R" here was the pre-2026-08-12 single-inverter converter; the self-biased 3-stage
  rework (commit f600af3) added devices. Breakdown, file-read run #3: 12 CML-core nfet
  + 4 CML loads (300R, one per output OI/OIB/OQ/OQB = 2 latches x 2, NOT 8) + 3 NMOS
  bias nfet + 4 converters x (6 nfet + 5 pfet + RFB 20k + R_SER 1k + CC 100f).
  All R_SER are on-chip inside the .subckt), symbol `DIV2_QUAD_v1.sym`
- TB:     `team_src/xschem/DIV2_QUAD_tb.sch` — 240 µA into IBIAS, rail-to-rail diff
  clock (T = 200 p = 5 GHz), pad load 300 fF + 50 Ω to gnd on each output.
- Generators (persistent, outside repo): `../_cp_work/gen_div2_quad.py`,
  `../_cp_work/gen_div2_quad_tb.py` (edit + re-run to regenerate the .sch/tb).

## Reproduce (headless, container `iic-osic-tools_xvnc`)
Netlist:
```
docker exec iic-osic-tools_xvnc bash -lc 'export PATH=/foss/tools/bin:/foss/tools/sak:$PATH; \
 source /foss/tools/sak/sak-pdk-script.sh gf180mcuD >/dev/null 2>&1; \
 cd /foss/designs/AUS-NZ-integration/team_src/xschem; \
 xschem -n -q -o /headless/.xschem/simulations DIV2_QUAD_tb.sch'
```
Failing sim run (5 GHz):
```
D=/headless/.xschem/simulations
sed "/^.tran/d" $D/DIV2_QUAD_tb.spice > /tmp/run5g.spice
cat >> /tmp/run5g.spice <<EOF
.ic v(x1.oi)=3.2 v(x1.oib)=0.6 v(x1.oq)=1.9 v(x1.oqb)=1.9
.control
tran 0.2p 6n uic
wrdata /tmp/div2_5g.txt v(i_p)-v(i_n) v(q_p)-v(q_n) v(i_p) v(q_p)
.endc
.end
EOF
cd $D; ngspice -b /tmp/run5g.spice
```
Internal nodes are hierarchical under the instance: `v(x1.oi)`, `v(x1.taila)`, etc.

## Symmetry break REQUIRED to get any motion
Without `.ic`, the CML sits in the perfectly-symmetric metastable state (idiff ≈ 1e-10)
and never starts. The `.ic` above (oi=3.2, oib=0.6) is what makes it move. Real
silicon starts on mismatch/noise; the cell still needs a defined startup story
(RST path or a deliberate small asymmetry).

## Measured (failing run, with the .ic)
| Quantity | Measured | Expected |
|---|---|---|
| idiff = v(oi)−v(oib) swing | **+2.9 / −0.56 V** (asymmetric) | clean symmetric ±swing |
| converter OC_ip swing | **1.09–1.91 V** | enough to fully switch the inverter |
| INVO_ip peak | **2.1 V** (not rail) | ~3.3 V |
| outputs I_P / Q_P | **tens of mV** | ~0.3 Vpp monitor (after 450/50 divider) |
| total supply, steady | **~2.8 mA** | **~18 mA** |
| IBIAS node | ~1.67 V | — |
(Ignore the ~−197 A spike at t=0 — it is the `uic` inrush charging the pad/node caps.)

## Root-cause read + debug order (do in THIS order)
1. **FIRST — measure the actual tail current.** ~2.8 mA total vs ~18 mA expected
   strongly implies the 10:1 mirror is **not delivering 2.4 mA/tail**. That single
   number gates everything else. Command:
   ```
   * add BEFORE .control/tran:
   .save @m.x1.xm_taila[id] @m.x1.xm_tailb[id] @m.x1.xm_bref[id]
   * then in .control after tran:
   print vecmax(abs(@m.x1.xm_taila[id])) vecmin(abs(@m.x1.xm_taila[id]))
   ```
   If tail ≪ 2.4 mA: check M_BREF (W = 4 u, L = 1 u) actually passes 240 µA and its
   VGS; check VDS headroom at TAILA (~0.46 V is marginal for a real tail sinking
   2.4 mA); likely fix is larger tail W (or nf), or lower R loads, or raise the ref.
2. **THEN re-center the CML with real tails.** Adjust R loads (300 Ω) and/or tail
   current so the single-ended common mode + swing match the ideal-tail probe
   operating point (`DIV2_CML_probe_tb`, which divided clean full-band). Confirm a
   clean **symmetric** idiff before touching buffers.
3. **THEN converter/inverter sizing.** PMOS-input diff pair (CM ~2.9 V) must drive
   OC far enough to fully flip the inverter to the rail. Resize NMOS mirror load
   (M_BN1/2), inverter (M_IP/M_IN), buffer tail (M_BT).
4. **Startup last.** Once biased, define the symmetry-break (RST path or a small
   deliberate asymmetry); `uic` sims still need the `.ic`.

Do not re-verify ÷2 / quadrature at 4.11/5.0/6.37 GHz until step 1's tail-current
number is right — the loading claim in `verification.md` §7 (ideal tails) will not
hold until the real mirror delivers the current.

---

## PARKED 2026-08-05 — root cause NARROWED to the output buffer (supersedes the above)

The tail-current suspicion above was **wrong**. Measured directly (via the 300 Ω
loads, since `nfet_03v3` is a subckt wrapper — `@m.x1.xm_taila[id]` is invalid):

| Quantity | Measured | Verdict |
|---|---|---|
| Tail A / Tail B current | **2.428 / 2.427 mA** | ✅ on target (2.4 mA design) |
| CML idiff, settled, **buffers in cutoff** | **±0.57 V symmetric** | ✅ CML core divides fine |
| Total supply | 8.7 mA | biased, not starved |

The earlier "±2.9 V asymmetric idiff" and "~2.8 mA supply" were **measurement
artifacts** (t=0 startup transient / wrong probe). **Mirror and CML core are GOOD.**
The whole problem is the 4 output CML→CMOS converters.

**Change already made (2026-08-05):** swapped the converters PMOS-input → **NMOS-input
diff pair + PMOS current-mirror load, NMOS tail off IBIAS** (`gen_div2_quad.py`,
regenerated). Necessary — the PMOS pair was in cutoff (CML CM 2.93 V too near VDD).
But **still does not switch.** Two coupled faults remain, both measured:

1. **OC never crosses the inverter trip.** Inverter trip = **1.515 V** (standalone DC
   sweep, M_IP 8u / M_IN 4u). OC operating point = **1.87 V**, swing **1.79–2.07 V** —
   min stays above the trip, inverter pinned low.
2. **Converter loads the CML.** With the NMOS pair conducting, idiff collapsed
   **0.57 V → 0.13–0.20 V** (hypothesis: 16 µm input devices' Miller-multiplied gate
   cap attenuating the 5 GHz CML swing).

### RESUME HYPOTHESIS (Greg, 2026-08-05) — treat as SIZING, not architecture. DO NOT implement yet.
1. **Skew the inverter UP to OC's ~1.87 V center** (widen M_IP / narrow M_IN so the
   trip rises from 1.515 V toward 1.87 V) — rather than trying to drag OC down to
   1.515 V.
2. **Shrink the 16 µm NMOS input devices** to cut the Miller loading that collapsed
   idiff from 0.57 to 0.13–0.20 V.
3. Even with the trip centered, a **280 mV OC swing gives poor edges** — converter
   **gain likely needs raising too** (load/tail sizing).

Cell + generator are in place (`DIV2_QUAD_v1.sch/.sym`, `_cp_work/gen_div2_quad.py`).
DIV2 is **CUT from the Aug-14 layout scope** (see `tracking.md`); revisit for Aug 21.

---

## 2026-08-10 — output converter reworked to 3 stages; STILL NON-WORKING (steady-state collapse)

Worked the three sizing moves from the Aug-05 hypothesis, then split the output
into a 3-stage chain. Each individual move measured as intended, but the assembled
chain **collapses in steady state**. Root cause is now understood as a *class* of
fault, not a sizing miss. Commit `92e59ce` carries the non-working `.sch`; the
pinned Ron and stage-3 sizing are the Aug-21 starting point.

### What was measured (all numbers file-read, not estimated)
| Step | Change | Result |
|---|---|---|
| move-a | inv trip skew, M_IP 8u→26u (standalone DC sweep) | trip 1.521 → 1.876 V |
| move-b | CML-input pair M_BN1/2 16u→8u | **idiff recovered to ±0.557 V** (from ±0.13–0.20); OC swing 280→495 mV |
| Ron pin | triode Ron·W (Vgs=3.3, L=0.3u) | **nfet 1707 Ω·µm, pfet 4833 Ω·µm** (ratio 2.83) |
| move-c | 3-stage: st1 26/4 skew → st2 38/4 restore → st3 44/16 driver, R_SER 1k | see below |

move-b's idiff recovery is the one durable win here — it holds in steady state
(OI−OIB = ±0.557 V at 16–20 ns). The CML core is unaffected and still divides.

### The move-c 3-stage chain and why it fails
Structure: split the single skewed inverter into **threshold / restoration / drive**:
- **stage 1** — 26u/4u skewed inverter, trip 1.876 V, drives only stage-2 gate.
- **stage 2** — 38u/4u, trip pinned to stage-1's *6–10 ns* output midpoint (1.98 V).
- **stage 3** — 44u/16u driver (Ron ≈ 110 Ω off the pinned Ron·W) into R_SER 1k + pad.

At **6–10 ns** it looked solved: INVO3 rail-to-rail, I_P **142 mVpp**, supply 19.7 mA
avg. **This was a decaying transient.** Measured to **16–20 ns** (true settled bias):
I_P collapses to **21 mVpp**, INVO3 rides 2.50–2.97 V (stuck high).

Front-end is innocent: **OC is stable** early vs late (swings 1.62–2.13 V, avg 1.87 V,
still crosses its trip). The collapse is inside the chain — **stage-1 output INVO1
rides up to a 2.18 V settled midpoint** (its 26u/4u skew = fast pull-up, slow pull-down
→ spends more time high), which is now **above stage-2's 1.98 V trip**, so stage 2
de-saturates (2.97 → 1.04 Vpp) and the output dies. The stage-2 trip had been pinned
to the *transient* 1.98 V midpoint; the *settled* midpoint is 2.18 V.

### Option-1 (trip-chase) — TRIED, FAILS THIS WAY. Do not reopen.
Pushed stage-2 trip to ~2.16 V (pfet 85u) to match the settled midpoint. The healthy
window did not get fixed — it **moved in time**: I_P at 16–20 ns recovered to 124 mVpp
but the 6–10 ns window went **dead (1.9 mVpp)**, and stage 2 still didn't saturate
(1.25 Vpp). No single trip works across all time (the midpoint drifts as bias settles),
let alone across PVT. Chasing the trip **relocates** the failure; it does not remove it.

### Root cause is a CLASS, not an instance
All three converter faults to date are the same thing — an **absolute threshold match
between two nodes whose levels move independently** with sizing, loading, bias settling,
and PVT:
1. (Aug-04) PMOS input pair in cutoff vs |Vth| — CML common mode too near VDD.
2. (Aug-05) inverter trip 1.515 V vs OC operating point 1.87 V.
3. (Aug-10) stage-1 midpoint 2.18 V vs stage-2 trip 1.98 V.
Resizing fixes an instance and exposes the next one. This is the third instance.

### Aug-21 rework — REMOVE threshold matching by construction (evaluate both, size neither yet)
- **Self-biased inverter**: feedback R from output to input holds the stage at its own
  switching threshold automatically across PVT; AC-couple the input through a cap.
  No absolute level to match, by construction.
- **Differential-input converter** using both OC and OCB: self-referencing, and it stops
  discarding the differential nature of the CML signal (the current single-ended design
  throws that away for no benefit).
Keep from move-c: the pinned Ron·W and the stage-3 44u/16u driver sizing (real, reusable).

### Toolchain notes (apply to any block with a DC operating point, not just DIV2)
- **`uic` bias settling is slow.** Under `uic`, bias nodes start from 0 and the converter
  chain needs **>10 ns** to settle. The old "startup settles by 2–6 ns" note applies to the
  **CML core only**. For anything with a DC operating point: **run 20 ns, measure 16–20 ns.**
  Measuring the 6–10 ns window is measuring a transient and will read false-positive.
- **min/max/avg hid this collapse completely** (OC's min/max/avg were identical early vs
  late while the output died). It was only caught by **dumping the waveform** and reading
  cycle-to-cycle. For settling/steady-state questions, dump and inspect — don't trust `meas`
  envelope stats alone.

### R_SER relock 450 Ω → 1 kΩ (see `scope.md`)
450 Ω was locked assuming a free rail-to-rail driver. Costed out, that driver is ~140 µm
pfet/device ×4 + a 4th taper stage (~26 mA). 1 kΩ delivers **157 mVpp (−12 dBm) unloaded /
~124 mVpp built** at the 50 Ω instrument — ample for a monitor pad confirming ÷2 ratio and
I/Q phase — with a moderate driver in **3 stages** and ~12.6 mA peak / ~6.3 mA avg. Amplitude
arithmetic: V_scope = 3.3·50/(R_SER+50); load at INVO ≈ R_SER + 45 Ω (pad 300 fF ∥ 50 Ω at
5 GHz). This **subsumes the old T6 output-load task** (the 450 Ω isolation-R ruling).

### 2026-08-12 rework — SELF-BIASED AC-COUPLED CONVERTER (SOLVED; class removed)
Canonical schematic is **regenerated** from `team_src/xschem/gen_div2_quad.py` (+ TB
`gen_div2_quad_tb.py`, which now writes the startup `.ic`) — `DIV2_QUAD_v1.sch` is a
generated artifact; all four chains are identical by construction, not by hand-edit.
Numbers below are file-read from the **regenerated** schematic, `tran 0.2p 20n uic`,
measured 16-20 ns. (`team_src/sim/div2/mk_sb.py` was the netlist-level prototype used to
find the topology; the generator is now the source of truth.)

**Topology (per phase).** Keep the diff-pair front end (M_NT tail, M_BN1/2 in = OIB/OI,
M_BP1/2 mirror load -> OC) — it already extracts the differential info and gives gain;
it was never the problem. Break the DC hand-off that was:
`OC --CC(100fF)--> G1 --> INV1(self-biased, pfet 10u/nfet 4u, RFB 20k INVO1->G1) --> INV2(26u/11u) --> INV3(44u/16u) --R_SER 1k--> I_P`.
The feedback RFB pins G1 = INVO1 = INV1's own switching threshold across PVT; the AC
coupling strips OC's ~1.87 V common mode. **There is no absolute level to match, by
construction** — this removes the failure class, not the third instance of it. RFB·CC =
2 ns (corner 80 MHz << 2.5 GHz signal). INV3 44/16 + R_SER 1k kept from move-c.

**Result — the old design COLLAPSED at TT (21 mVpp @ 16-20 ns); the new one holds.**
With the startup `.ic` in the TB, 16-20 ns is a valid settled window at EVERY corner:

| corner | I_P (mVpp) | INVO3 rail (mV) | f (GHz) | duty | I/Q |
|---|---|---|---|---|---|
| TT (27C)  | 141 | -16 .. 2950 | 2.500 | 49.4% | 270.0 deg |
| FF        | 145 | -38 .. 3023 | 2.500 | 49.0% | 270.0 deg |
| SS        |  94 | 795 .. 2802 | 2.500 | 59.9% | 270.0 deg |
| TT -40C   | 147 | -55 .. 3057 | 2.500 | 48.6% | 270.0 deg |
| TT 85C    | 106 | 526 .. 2785 | 2.500 | 59.0% | 270.0 deg |

All four outputs (I_P/I_N/Q_P/Q_N) track within 1 mVpp — the 4 chains are identical
(generated), so I/Q is **EXACT quadrature (270.0 deg = Q_P leads I_P by 90 deg**; swap
Q_P/Q_N labels if lag is wanted) at every corner. **Every corner divides correctly
(2.500 GHz) with exact quadrature** — the class fix holds across full PVT.

**Amplitude** ranges 94 mVpp (SS) to 147 mVpp (cold). SS/hot fall below the 124 mV
"built" target (94/106 mVpp) because the fixed-ratio 44/16 driver + R_SER load is
slew-limited at the slow corners (INVO3 low rail rises to ~0.5-0.8 V). For a monitor pad
whose job is confirming the /2 ratio and I/Q phase this is fine — 94 mVpp (~-20 dBm into
50 ohm) is easily measured; freq and quadrature are exact. Not chasing more driver (brief
pins 44/16; a bigger driver costs area/power for a monitor).

**Duty cycle** 49.4% at TT (49% FF, 60% SS/hot — slow-corner skew from the fixed-ratio
INV2/INV3 driving the 2.5 GHz + R_SER load; cosmetic for a monitor). Strengthening the
output nfet was TRIED (INV3 44/22, INV2 nfet 13) and made SS **worse** (stuck-high, 82%
duty) by gate-loading INV2 — reverted. 44/16 stands.

**Settling (condition-7 bring-up note).** The self-biased chain + CML + pad settle to the
true operating point; the startup `.ic` (CML latch seed + G1 self-bias pre-charge, now in
the TB) pulls that settling inside 16-20 ns at ALL corners incl SS/85 C (without it, slow
corners needed ~24-26 ns and a 16-20 ns read showed settling artifacts, e.g. SS f=2.54 /
I/Q=262). **On the bench, allow ~30 ns after power-up before reading** — startup
transients are real in silicon too; this is characterization, not an omission.

**Budget (3.5).** Full divider + 4 converters supply current = **~23 mA avg** (22.96 mA,
peak ~21.6 mA over the window; the transient inherently includes dynamic CV^2f on the
stage-3 gates and short-circuit current — no hand-calc needed) vs the ~50 mA VDDA budget.
~46% used. **Running RFIC total to watch (Phase 7): DIV2 ~23 mA + VCO (core 1.2-1.6 mA
/ ~4-5 mW; 5 mA / 16.6 mW ONLY if an on-chip buffer like the TB's is included — see
verification.md 3.2) + IBIAS 0.84 mA + CP ~0.2 mA + PFD (digital, small). Running total
~25 mA core-only / ~29 mA with VCO buffer, against the 50 mA ceiling. Track now.**

**Locked converter sizing (per phase):** CC 100 fF, RFB 20 kO, INV1 pfet 10u/nfet 4u,
INV2 pfet 26u/nfet 11u, INV3 pfet 44u/nfet 16u, R_SER 1 kO. Internal node G1_<ph>.

**Schematic realization — DONE (regenerated).** `gen_div2_quad.py` updated with the new
topology and `DIV2_QUAD_v1.sch` regenerated; the reworked netlist is confirmed to
reproduce the table above directly (no hand-edit, all 4 chains identical). Generator path
is now relative to the script and it lives in `team_src/xschem/` (was `_cp_work` scratch
with a hardcoded Windows output path). This is the source of Phase 5.3's layout golden.

### 2026-08-14 (run #2) — R_SER confirmed ON-CHIP, no schematic gap
Reconciled the "12 resistors" count against the 1k R_SER isolation ruling. Netlist of the
current `DIV2_QUAD_v1.sch` (file-read) has exactly **12 R = 4 CML loads (300R: RA1/RA2/RB1/
RB2) + 4 RFB (20k) + 4 R_SER (1k: R_SER_IP/IN/QP/QN)**. The R_SER resistors are emitted by
`gen_div2_quad.py` line 95 `res(x0+1560,1800,"R_SER_%s"%tag,S3,OUT,"1k")` INSIDE each
converter chain, connecting internal INVO3 (S3) to the block OUTPUT ports; the subckt
boundary is `.subckt DIV2_QUAD_v1 CK CKB IBIAS I_P I_N Q_P Q_N VDD VSS`. So R_SER is on-chip,
inside the block, **not testbench-only** — no schematic gap. (The earlier "8 CML loads"
worry was wrong: the /2 has 2 latches x 2 loads = 4 CML loads, not 8.) **Open for 5.3
layout only:** the generator emits ideal `device=resistor`; the LVS golden must map R_SER
1k -> `ppolyf_u_1k` (2x2um) and the 300R CML loads to their real flavor.
