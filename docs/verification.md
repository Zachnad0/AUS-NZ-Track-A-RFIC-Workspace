# Verification Log — AUS/NZ Track A RFIC

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU (gf180mcuD)**
Every simulated number lands here. Last updated: 2026-07-30.

---

## 1. Rail audit (Phase 3, step 15)

**Decision — project rail = 3.3 V for the entire design, analog and digital.**
Basis: all cells are built exclusively from `*_03v3` (3.3 V) devices; there is no
second voltage domain and no cell that requires a lower rail. The 1.8 V values
found in two digital testbenches are **outliers to correct**, not a rail choice.

### 1.1 Testbench-by-testbench

| Testbench | Supply | Stimulus amplitude | Other rail refs | Verdict |
|-----------|--------|--------------------|-----------------|---------|
| `CP_dc_tb` | V_VDD = **3.3** | UP/DOWN altered to 3.3; V_OUT swept 0–3.3 | `dc V_OUT 0 3.3` | ✅ 3.3 |
| `CP_tran_tb` | V_VDD = **3.3** | UP `PULSE(0 3.3 …)`, DOWN `PULSE(0 3.3 …)` | — | ✅ 3.3 |
| `NAND3_v1_tb` | VDD = **3.3** | VA/VB/VC `PULSE(0 3.3 …)` | — | ✅ 3.3 |
| `vco_tb` | V1 = **3.3** | V2 = 1.5 (**VTUNE control voltage**, not a rail); I0 = 1 mA bias | — | ✅ 3.3 |
| `inductor_tb` | V1 altered to **3.3** | (impedance/extraction) | `dc V1 0 3.3` (commented) | ✅ 3.3 |
| `vco_tank_tb` | none (AC) | `Iin0/Iin1 = 0 AC 0.5` | — | ▫️ AC-only, N/A |
| `vco_varactor_tb` | none (AC) | V1 = `0 AC 1` (C–V sweep) | — | ▫️ AC-only, N/A |
| **`PFD_tb`** | **V3 = 1.8** ⚠️ | V1 `PULSE(0 1.8 50n …)`, V2 `PULSE(0 1.8 150n …)` | `.ic v(net1)=1.8` | ❌ **1.8 → correct to 3.3** |
| **`D_FF_RST_v1_tb`** | **VDD = 1.8** ⚠️ | VCLK `PULSE(0 1.8 …)`, VRST `PULSE(0 1.8 …)` | — | ❌ **1.8 → correct to 3.3** |

### 1.2 Cell-by-cell

| Cell | Devices | Rail pins | Hardcoded rail? | Works at 3.3? |
|------|---------|-----------|-----------------|---------------|
| `CP_v1` | 4×nfet_03v3, 4×pfet_03v3 | VDD / VSS | none (comment: "GF180 3.3V") | ✅ native |
| `PFD_v1` | hierarchical | VDD / VSS | none | ✅ |
| `D_FF_RST_v1` | hierarchical | VDD / VSS | none | ✅ |
| `D_FF_v1` | hierarchical | VDD / VSS | none | ✅ |
| `NAND3_v1` | 3×nfet_03v3, 3×pfet_03v3 | VDD / VSS | none | ✅ |
| `NAND_v1` | 2×nfet_03v3, 2×pfet_03v3 | VDD / VSS | none | ✅ |
| `NOT_v1` | 1×nfet_03v3, 1×pfet_03v3 | VDD / VSS | none | ✅ |
| `vco_v1` | 2×nfet_03v3, 2×pfet_03v3, 2×cap_nmos_03v3_b (varactor), 1×ppolyf_u_3k | VDD (tail to GND) | none (1.7 pF = coupling caps, not a rail) | ✅ |

**No non-03v3 device exists anywhere in the design.** `CP_v1`'s 0.32–3.0 V output
compliance window is only meaningful at a 3.3 V rail, and `vco_tb` already runs
VDD = 3.3 V — both consistent with the decision.

### 1.3 Queued corrections (run when the container returns)

- Correct `PFD_tb.sch`: sources 1.8 → 3.3 V, and `.ic v(net1)=1.8` → 3.3.
- Correct `D_FF_RST_v1_tb.sch`: VDD and VCLK/VRST 1.8 → 3.3 V.
- Re-net­list and re-run both after correction; log deltas here.
- **Not edited yet** — deferred until after the issue-#143 edit verification, per
  instruction. Amplitudes will be changed only then, and never silently.

### 1.4 Symbol ↔ schematic pin mismatch (diagnosed; fix approved, pending container)

Detected via `xschem -n` (`Error: Symbol <cell>.sym has N pins, its schematic has
M pins`) and confirmed by direct port extraction (symbol `B …{name=…dir=…}` vs
schematic `ipin/opin/iopin` instances).

| Cell | Symbol pins | Schematic port instances | Redundant | Owner | Action |
|------|-------------|--------------------------|-----------|-------|--------|
| `PFD_v1` | 6 (VDD VSS REF FB UP DOWN) | 8 (VDD×2, VSS×2) | 1×VDD + 1×VSS | Greg | fix |
| `D_FF_RST_v1` | 7 (RST VDD D Q CLK **!Q** VSS) | 19 (VDD×7, VSS×7) | 6×VDD + 6×VSS | Greg | fix |
| `D_FF_v1` | ~~5~~ **6** | ~~6 (1 dup power)~~ **6** | ~~1 dup power~~ **NONE** | Zach | **CLAIM DISPROVEN 2026-08-05** — see note below |
| `NAND3_v1`, `NAND_v1`, `NOT_v1` | 6/5/4 | 6/5/4 | none | Zach | clean, no action |

**Root cause:** duplicate `VDD`/`VSS` `iopin` instances (one dropped per sub-cell).
All port **names are correct and complete** (incl. `!Q`); only power ports repeat.

**Severity:** non-fatal warning — netlists generate and `PFD_v1` verified at 1 MHz,
so xschem de-duplicates same-named power iopins when building the `.subckt`
pinlist. Sims tolerate it; the real risk is **Phase-4 LVS** (duplicate/ordered
ports trip `netgen` port-matching). This is a **clean-before-layout** item.

**Approved fix (`PFD_v1`, `D_FF_RST_v1` only):** convert each redundant power
`iopin` → `lab_pin` (same `lab=`), leaving exactly one `VDD` and one `VSS` `iopin`
per schematic. `lab_pin` keeps the net name at every stub, so VDD/VSS stay unified
by name — no fragmentation risk. No symbol edits, no other cells.

**Verification gate (per cell, when container returns):** after each edit,
re-netlist headlessly and (a) confirm the pin-count warning cleared; (b) diff the
generated netlist pre- vs post-edit — devices + connectivity must be identical
modulo port-list ordering/formatting. Any semantic delta → revert and stop.

**Sequencing:** fix lands + verifies **before** condition-4 results are recorded as
final evidence. Post-fix, re-run the original `PFD_tb` 1 MHz case as a regression
against the UP=101 ns / ~1 ns-reset baseline.

**RESOLVED (2026-07-31):** iopin→lab_pin conversion applied.

| Cell | Change | Gate (a) warning cleared | Gate (b) device netlist diff |
|------|--------|--------------------------|------------------------------|
| `PFD_v1` | p15 (VDD), p16 (VSS) iopin→lab_pin; p3/p4 kept as ports | ✅ `6/8` error gone | ✅ x-instances **identical**; `*.iopin` 24→22 |
| `D_FF_RST_v1` | 6×VDD + 6×VSS iopin→lab_pin; p3/p6 kept as ports | ✅ `7/19` error gone | ✅ x-instances **identical**; `*.iopin` 20→8 |

`.subckt` port lists unchanged (`PFD_v1`: VDD UP REF VSS DOWN FB; `D_FF_RST_v1`:
RST VDD D Q CLK !Q VSS). `PFD_tb` + all 3 drafted tbs now netlist with **0**
pin-count errors. 1 MHz regression pending in §2.

*Cosmetic note:* `PFD_v1` already had coincident `lab_pin` VDD/VSS at the converted
iopin locations, so the conversion leaves duplicate (overlapping) lab_pins there —
harmless (same net name), left as-is within the approved convert scope; can be
de-duplicated later if desired. `D_FF_RST_v1` had no coincident labels, so the
conversion was essential to preserve the net names (delete would have fragmented
VDD/VSS).

---

## 2. PFD three-case verification (condition 4)

All at 3.3 V, 1 MHz, 100 ns REF↔FB offset; widths measured in a settled cycle
(TD = 2 µs) at the 1.65 V threshold. Post pin-fix (§1.4) and rail correction
(§1.3).

| Case | Phase | UP width | DOWN width | Interpretation |
|------|-------|---------:|-----------:|----------------|
| `PFD_tb` (corrected) | REF leads 100 ns | **100.5 ns** | 0.48 ns | net UP → pump up |
| `PFD_tb_lead` | REF leads 100 ns | **100.5 ns** | 0.48 ns | matches `PFD_tb` (cross-check) |
| `PFD_tb_lag` | FB leads 100 ns | 0.48 ns | **100.5 ns** | net DOWN → pump down |
| `PFD_tb_eqfreq` | aligned (0°) | 0.50 ns | 0.50 ns | UP = DOWN reset → locked, net-zero |

- **Phase-lead → wide UP, narrow DOWN; phase-lag → the mirror; equal-freq → equal
  narrow reset pulses.** Correct three-region PFD characteristic.
- The reset pulse is **~0.48–0.50 ns at 3.3 V** (vs ~0.98 ns at 1.8 V — faster
  logic at the higher rail), consistent across all cases.
- **1 MHz regression (pin-fix):** original 1.8 V `PFD_tb` post-fix → UP = 101.0 ns,
  reset = 0.98 ns = baseline. Pin fix is behavior-neutral (§1.4).

### 2.1 PFD + CP integration (static phase error → avg I_out; coincident UP+DOWN)

`PFD_CP_tb.sch` (new): `PFD_v1` UP/DOWN → `CP_v1` UP/DOWN; CP_OUT held at 1.65 V
(mid-compliance) by a sense source; i(V_meas) = CP output current. REF fixed at
300 ns delay, FB delay swept (φ = fbdel − 300 ns); avg current over the 3–4 µs
cycle, 3.3 V, 1 MHz.

| φ (ns) | avg I_out (µA) | φ (ns) | avg I_out (µA) |
|---:|---:|---:|---:|
| −200 | −9.97 | +20 | +1.15 |
| −100 | −4.93 | +50 | +2.66 |
| −50 | −2.42 | +100 | +5.17 |
| −20 | −0.91 | +200 | +10.19 |
| **0** | **+0.105** | | |

- **Linear transfer `I_avg = I_CP · φ/T`.** At φ = 200 ns: 50 µA × 200n/1µ = 10 µA
  vs measured 10.19 µA → confirms **I_CP = 50 µA** and a monotonic characteristic
  through zero. Detector gain ≈ 50 nA/ns.
- **Coincident UP+DOWN (φ=0, lock):** residual +0.105 µA = **~105 fC/cycle**,
  matching the known **+110 fC/cycle CP injection**. CP handles simultaneous
  UP+DOWN with only this small net current (no latch-up).
- **LOOP SIGN (KVCO < 0) — verified:** REF-lead (φ>0) → UP → CP **sources** →
  VTUNE **rises**. With KVCO < 0, VTUNE↑ ⇒ freq↓, but a slow VCO (REF leading)
  needs freq↑. So the direct UP→UP / DOWN→DOWN wiring drives **away** from lock —
  **the UP/DOWN→CP sense must be inverted** (swap UP/DOWN into the CP, or invert
  the VTUNE/loop-filter polarity). This empirically confirms the `scope.md` §2
  loop-sign constraint. **Documented only — no cell rewiring** (per ruling); the
  inversion is applied when the loop is closed.

### 2.2 Library-cell PFD (Aug-14 layout path, decided 2026-08-05)

For the Aug-14 layout the **digital chain moves to `gf180mcu_fd_sc_mcu7t5v0` std
cells** (see scope.md device-flavor note): 2× `dffrnq_1` (async active-low-reset DFF)
+ `nand2_1` coincidence, **same PFD topology as `PFD_v1`** (D tied high, reset =
NAND(UP,DOWN) → active-low RN). Re-sim at typical, 3.3 V, 2 MHz:

| Case | Library UP | Library DOWN | Custom PFD_v1 |
|------|-----------:|-------------:|---------------|
| REF leads | 100.5 ns | 0.49 ns | 100.5 / 0.48 |
| FB leads | 0.48 ns | 100.5 ns | 0.48 / 100.5 |
| Equal (raw) | 0.37 ns | 0.38 ns | 0.50 / 0.50 |

- **Async reset confirmed genuine** (`RN` gates latch transistors directly, not
  clocked); **D-high works** (Q→1 on clock, cleared by reset).
- Raw min pulse **0.37 ns** was **narrower** than custom (worse dead-zone floor) →
  **widened with 2× `inv_1` in the RSTN path → min pulse 0.50 ns** (matches/beats
  custom). Three regions re-confirmed with the delay.
- **Corner dead-zone margin:** min reset pulse at **fast digital (ff) = 0.39 ns**;
  CP switch-close at **slow analog (ss) ≈ 0.02 ns** (clamped output). min-pulse(ff) ≫
  CP-engagement → no dead zone at the worst corner split. Corner runs supported
  (`ff`/`ss`/`fs`/`sf`).
  - **CAVEAT — do not read 0.39 vs 0.02 as the true margin.** The CP "steering time"
    is methodology-dependent and the numbers are NOT the same measurement: **0.155 ns**
    (verification §2.1) is **typical corner, 10 pF-loaded**; **0.019 ns** is **ss
    corner, voltage-clamped switch-close** (pure device speed, no load). The
    **loaded** CP steering at the **ss** corner — the number that would pair
    apples-to-apples with min-pulse(ff) — was **never measured**. The qualitative
    conclusion (CP engages in tens of ps ≪ 0.39 ns pulse, and §2.1 shows linear-
    through-zero transfer) holds, but a rigorous loaded-ss steering figure is
    outstanding if tighter margin accounting is needed.
- Decks: `_cp_work/pfd_lib_*.spice`. **Gate PASSED (Greg, 2026-08-05).**

### 2.3 PFD_lib LAYOUT COMPLETE (LibreLane, 2026-08-05) — DRC + LVS clean

Library-cell PFD placed+routed by LibreLane (Classic flow); passes all four sign-off
gates. GDS: `librelane_pfd/runs/RUN_2026-08-05_23-52-38/final/gds/PFD_lib.gds`
(regenerable from `librelane_pfd/config.json` + `src/PFD_lib.v` + the golden).

| Gate | Result |
|------|--------|
| DRC | **Magic 0, KLayout 0** |
| Reset inverters | **2× inv_1 in series on RSTN** (`NANDO→XI1→NDLY→XI2→RSTN`), preserved through full P&R |
| REF vs FB insertion delay | **REF ≈ 48 fs, FB ≈ 12 fs** (wire RC, both UNBUFFERED); ~36 fs mismatch — negligible vs the 0.5 ns pulse |
| netgen LVS vs golden | **Circuits match uniquely** (7 devices / 11 nets) |

Cell inventory = golden exactly: 2 dffrnq_1 + 1 nand2_1 + 2 inv_1 + 2 tieh; the rest
(endcap/fill/fillcap/filltie) is physical-only (LVS_IGNORE).

**LVS-relevant device count is 7 / 11 nets.** A flattened parasitic extraction reports
**190 transistors** — that is the fill-inflated count (every placer `fillcap`/`fill`/
`endcap`/`filltie` cell counted at device level). Do not quote 190 as a device count; it
reads as a 27× discrepancy against the golden.

#### 2.3.1 Independent DRC/LVS re-confirmation (`team_src/magic/verify_cp.sh`, 2026-08-10)
A standalone headless script (Magic DRC → LVS-netlist extract → netgen LVS vs
`PFD_lib_golden.spice`) reproduces sign-off on the committed `gds/PFD_lib.gds`:
**DRC 0, 7 devices / 6 ports / 11 nets, circuits match uniquely.** Two documented,
justified LVS waivers (rubric row 1 = "passes DRC+LVS with any waivers documented and
justified"):
- **Waiver 1 — fillcap decaps ignored** (18 instances: `fillcap_16`×6, `_32`×3, `_4`×5,
  `_8`×4 — matches the on-record inventory exactly). This is the **same waiver LibreLane's
  own proven run already applied via `LVS_IGNORE`**; the local netgen wrapper adds *only*
  the PDK-provided (but commented) fillcap `ignore class` and nothing else. `endcap`/`fill`/
  `filltie` are empty/tap-only and emit zero devices, so they need no ignore.
- **Waiver 2 — comparison method, not a violation.** The golden's std cells are resolved
  against the PDK `mcu7t5v0` spice so both circuits carry full definitions (a placed
  digital block otherwise LVSes def-vs-blackbox against a schematic golden). CP_v1's
  transistor-level golden will not need this path.

#### 2.3.2 Tapcell spacing corrected 20 → 15 µm (2026-08-10)
`librelane_pfd/config.json` carried no explicit `FP_TAPCELL_DIST`, so it inherited the
LibreLane default **20 µm** (confirmed in `resolved.json`). PFD_lib is 5 V/MV std cells;
GF180 **DF.13_MV/DF.14_MV cap tap-to-device at 15 µm** on `.overlapping(dualgate)` (20 µm
is the LV/3.3 V limit, which passed only incidentally on a small block). Set to an explicit
**15 µm** (commit `e3b6cae`). **No LibreLane re-run** — config-only correction for the next build.

#### 2.3.3 REF/FB parasitic symmetry (PEX, 2026-08-10) — layout-symmetry observation, no fix
Magic PEX on `gds/PFD_lib.gds` (`cthresh 0 rthresh 0`, all coupling caps retained):

| net | rail load | signal coupling | **total cap** |
|---|---|---|---|
| REF | 1.966 fF | 1.601 fF | **3.567 fF** |
| FB  | 1.303 fF | 1.074 fF | **2.377 fF** |
| RSTN (`X2.RN`) | 4.529 fF | 3.242 fF | **7.771 fF** |

REF carries **+1.190 fF (33%) more than FB**, consistent across both rail loading and
signal coupling. The one genuinely interesting line is **REF↔`X1_1.Z` = 0.360 fF —
logic-net crosstalk onto a clock input**, not just rail loading.

**Framed as fraction of the reference period, this is negligible.** At the 1 MHz reference
even a pessimistic ~5 ps skew from 1.2 fF is 5×10⁻⁶ of a cycle ≈ **0.002° static phase
offset** (~1% of the 0.5 ns minimum reset pulse). **And the driver impedances dominate
anyway:** REF is driven by a pad and FB by the CML divider, so their source-impedance
mismatch swamps a 1.2 fF load mismatch outright. This is **not** the `dlyb` trap (that was
hundreds of ps of inserted buffer delay); it is a layout-symmetry observation, no fix.

**Reconciliation with the STA number above.** The §2.3 table lists REF ≈ 48 fs / FB ≈ 12 fs
insertion delay — ~2 orders of magnitude smaller than the fF-implied skew. **Hypothesis
(not yet a finding):** the STA figure is **likely wire-RC only and excludes pin capacitance**,
whereas PEX includes the full node cap. **This explanation has not been tested** — we have no
STA run that adds pin cap to the path — so the two numbers are not yet reconciled, only plausibly
explained. Recorded here so a future reader does not treat them as a contradiction or as settled.

**FIRST-RUN TRAP — read this before repeating.** The FIRST LibreLane run silently
INSERTED 3× `dlyb_1` delay buffers: one on **FB→CLK (but NOT on REF)**, and two on the
UP/DOWN outputs. The FB-only buffer made the REF/FB insertion delay **asymmetric = a
static phase offset the locked PLL reads as real phase error.** A silent design change
that would have shipped a broken PFD. `--skip OpenROAD.CTS` alone did NOT prevent it.

**Config keys that fixed it** (`librelane_pfd/config.json`):
- `CLOCK_PORT: null` — no clock, so the resizer can't treat REF/FB asymmetrically
- `DESIGN_REPAIR_BUFFER_INPUT_PORTS` / `_OUTPUT_PORTS`: `false`
- `PL_RESIZER_BUFFER_INPUT_PORTS` / `_OUTPUT_PORTS`: `false` (deprecated aliases — set both)
- `RSZ_DONT_TOUCH_RX: "REF|FB"` — second-line defense
- `DESIGN_REPAIR_REMOVE_BUFFERS: false` — MUST stay false or it strips the reset inverters

**REJECT-THE-RUN RULE:** any future PFD_lib LibreLane run MUST be rejected unless
`final/nl/PFD_lib.nl.v` shows exactly **2× inv_1 in series on RSTN** and **no dlyb/buffer
on REF or FB**. Grep the netlist before trusting the GDS.

## 2.6 IBIAS generator — delivered CP/DIV2 bias (S1–S7, 2026-08-12)

`ibias_gen_v1` replaces the CP's two ideal 50 µA sources (`I_PREF`/`I_NREF`) and
the DIV2 tail reference with mirrored bias legs off one chip-level reference.
Reference is a **forced current** `I_BIAS = 240 µA` (isource, VDD-independent);
outputs VGP (CP PMOS-diode bias), VGN (CP NMOS-diode bias), IB_DIV2 (divider bias).
All numbers ngspice, TT/3.3 V/27 °C unless stated; decks in `team_src/sim/ibias/`.

**S1 — L uniform (committed).** Amendment-1's L=4 µm **CP output legs** (MN1 →
VGP sink, MP1 → VGN source — these bias the CP, *not* the DIV2 branch; they were the
5% systematic) retracted to uniform **L = 2 µm** on all mirrors (m=10→5 preserves the
**5/24 mirror ratio** to the MN0/MP0 reference: (W/L)·m = 10 vs 48); cascodes stay
L = 1 µm. Commit `bfbb497`.

**S2 — collapse holds (TT).** VGP **50.00 µA**, VGN **49.91 µA**, IB_DIV2 **239.56 µA**;
total VDDA **839 µA**. Matches the predicted collapse.

**S4 — gain / linearity / compliance.** Input sweep 120–360 µA: VGP gain 5/24,
linearity < 0.01 % (NMOS single mirror); VGN & IB_DIV2 share the added PMOS-mirror
stage → −0.18 % at nominal, ≤ −0.5 % at 1.5×. Output compliance (5 % window): VGP
0.247–3.30 V, VGN 0.0–3.053 V, IB_DIV2 0.0–3.053 V — **every branch envelops the
CP's measured 0.32–3.00 V** compliance window with margin.

**S4b — separate DIV2 cascode gate justified.** Injecting AC at IB_DIV2 and
measuring the current transfer to VGN: with the shipped **separate** cascode gate
(VBCPD) the transfer is 1.24e−6 @ 1 MHz / 3.61e−5 @ 1 GHz; with a **shared** PA gate
it is 2.35e−4 / 1.57e−3 — i.e. the separate gate buys **~45 dB (1 MHz) / ~33 dB
(1 GHz)** additional isolation of the divider bias node from the CP's VGN bias.

**S5 — CP UP/DOWN match with the generator substituted (the real deliverable, TT).**
Full CP (`CP_core`, 7-port, ideal sources removed) driven by the generator, DC-swept
CP_OUT. `CP_core` was verified **identical in port order, device set, connectivity and
sizing to the LVS reference `CP_v1_golden.spice`** — the sim-CP and the golden-CP are
the same circuit, so this characterizes what will be taped out. The generator adds a **uniform +0.18 %** to the CP source/sink mismatch across
the whole 0.4–2.8 V range — exactly the 50.00-vs-49.91 µA VGN deficit. The ±2 %
variation of mismatch vs CP_OUT is the CP's **intrinsic output-impedance mismatch,
present identically with ideal sources** (verified by running the ideal baseline in
the same environment: gen−ideal = +0.18 % at every point).

> **The 0.001 % figure was the CP topology's single-point zero-crossing with ideal,
> perfectly-equal sources — NOT the delivered circuit.** The delivered generator-driven
> figure is **~0.18 % at TT** at a fixed operating point.

**S6 — corners (process tracking only, NOT random mismatch).** VGP is corner-invariant
(50.00 µA, forced-current NMOS mirror). CP added-mismatch: **FF 0.004 %, TT 0.18 %,
SS 0.94 %** (the VGN/DIV2 PMOS-mirror path carries the spread). These are **systematic
process-tracking** numbers; **random device mismatch is not captured and requires
Monte Carlo** — a TT/corner figure must not be presented as the delivered match.

**PSRR (VDD 3.0–3.6 V, forced-current reference).** Because the reference is a forced
current (not a resistor to VDD, which would make I_ref track VDD and void the number):
VGP **0.003 %/V** (≈79 dB, cascoded NMOS mirror), VGN & IB_DIV2 **1.16 %/V** (≈28 dB,
PMOS-mirror path).

> **Two distinct mechanisms — do not conflate them.** The 0.18 % *static* mismatch is
> bounded to ~1 ps ≈ 0.0004° by the phase-offset argument above and is negligible.
> **Supply *ripple* on VGN is a separate, dynamic mechanism**: at 1.16 %/V it modulates
> I_CP within a cycle, injecting a reference spur — the static phase-offset bound does
> NOT cover it. This is not a Phase 2 reopen; it is a **Phase 5 layout requirement**:
> the `Vb_p` decap earns its place, and VDDA to the CP/IBIAS must be routed quiet and
> away from the digital block (see block-separation rules). VGP (0.003 %/V) is immune,
> so the exposure is VGN-specific.

**Context — is 0.18 % alarming? No.** A CP current mismatch ΔI/I produces a static
phase offset bounded by the reset-pulse balance: t_φ ≈ t_rst · (ΔI/I) ≈ 0.5 ns ·
0.002 ≈ **1 ps**, i.e. **≈ 0.0004–0.0007° at the MHz-class reference** — negligible.
Moreover the CP's known **+110 fC/cycle charge injection** (§2.1; ~105 fC measured at
φ=0) is the **likely dominant reference-spur mechanism**, not the 0.18 % static
mismatch. The generator does not meaningfully degrade the CP.

### 2.6.1 IBIAS LAYOUT COMPLETE (`ibias_gen_v1`, 2026-08-14) — DRC + LVS clean
Full-custom Magic layout of the 16-device generator, headless via a parameterized
generator (`team_src/magic/phase5/ib_block.tcl` + `ibias_gen_v1.tcl`). Four-row stack
(NMOS mirror/cascode in pwell, PMOS mirror/cascode in nwell; ~150×64 µm), wide W=16
m=24 legs split 2×nf=12 (200 µm model bin), inter-band routing by layer-per-net-class
(M2 S/D, M3 crossings, M4 cascode-VDD, M5 PA/VBCPD cross-band), end dummies on the 24:5
ratio array. Sign-off (`team_src/magic/verify_cp.sh ibias_gen_v1`, exit 0):

| Gate | Result |
|------|--------|
| Magic DRC | **0** |
| KLayout DRC (variant D) | **0** |
| netgen LVS vs `ibias_gen_v1_golden.spice` | **228 fingers → 16 devices + m=4 end-dummy → match uniquely** |
| Ports | **6** (IBIAS VGP VGN IB_DIV2 VDD VSS), 0 port errors, 0 property errors |

Render: `docs/renders/ibias_gen_v1_{white,black}.png`. Both NMOS-side (`ib_nmos`, 112
fingers) and PMOS-side (`ib_pmos`, 116 fingers) also verify standalone.

**Golden ≠ schematic by one device — intentional, flagged here.** `ibias_gen_v1_golden.spice`
carries **17 device instances**: the 16 from `ibias_gen_v1.sch`/`.sym` **plus one layout-only
tied-off dummy** `XMDUM` (nfet W=4 L=2, m=4; gate→NB, source=drain=VSS). The dummy is the two
end-dummy fingers on the 24:5 mirror array, netgen-merged; it draws no current (Vds=0) and
changes no node's connectivity, but it must appear in the golden or LVS reports a device-count
mismatch. This is the standard "add end-dummies as tied-off instances" convention (same as
CP_v1 and `ib_nmos`), **not** a schematic error — the schematic stays at 16 devices and does
not need editing. Any future full-chip LVS that netlists `ibias_gen_v1.sch` directly must add
the same tied-off dummy, or waive the one-device count delta, to match the drawn layout.

## 3. VCO characterization (condition 5)

### 3.1 f–VTUNE sweep (measured) — establishes the frequency plan

`vco_tb` (Zach's tank + buffers), TT, 27 °C, VDD 3.3 V. Method: for each VTUNE,
`tran 5p 150n uic`; frequency = 10 rising zero-crossings of (out_p−out_n) measured
in the settled 100–150 ns window; Vpp = peak-to-peak of the buffered differential
output into 50 Ω over the same window.

| VTUNE (V) | VCO freq (GHz) | ÷2 output (GHz) | Vpp diff (V) |
|---:|---:|---:|---:|
| 0.0 | 6.367 | 3.18 | 0.553 |
| 0.4 | 6.324 | 3.16 | 0.549 |
| 0.8 | 6.247 | 3.12 | 0.543 |
| 1.2 | 5.669 | 2.83 | 0.526 |
| 1.6 | 5.442 | 2.72 | 0.524 |
| 2.0 | 5.235 | 2.62 | 0.522 |
| 2.4 | 4.919 | 2.46 | 0.518 |
| 2.8 | 4.527 | 2.26 | 0.502 |
| 3.3 | 4.114 | 2.06 | 0.457 |

- **Native band 4.11–6.37 GHz**; ÷2 output 2.06–3.18 GHz; ISM 2.4–2.5 GHz at
  VTUNE ≈ 2.05–2.28 V (mid-range).
- **KVCO ≈ −683 MHz/V** avg; −1.4 GHz/V steepest (0.8→1.2 V); −790 MHz/V near ISM.
  **Inverted tuning (KVCO < 0)** — drives the loop-sign constraint (`scope.md` §2).
- Drives Plan B (`scope.md` §3, FINAL).

> **SUPERSEDED (2026-08-12), see §3.2 GAP 1.** This 7/30 table's mid-curve is not
> reproducible on the same netlist (container proven stable). The band edges hold, but the
> corrected sweep gives a smooth curve with ISM at **VTUNE ≈ 1.95–2.12 V** and local KVCO
> **≈ −1.1 GHz/V** (not 2.05–2.28 V / −790 MHz/V). Use §3.2's numbers for Plan B.

**Portability bug — FIXED (2026-08-12).** `vco_inductor_v2.sym` hardcoded
`spice_sym_def=".include /foss/designs/xschem/vco_inductor_v2.subckt"` (a path that
does not exist in any clone). Changed to `$UPRJ_ROOT/team_src/xschem/…` (ngspice
expands `$UPRJ_ROOT`; portable across the 3 clones, matches the Phase 7.2 lvs
convention). Sims require `UPRJ_ROOT` set to the clone root.

### 3.2 VCO characterization (2026-08-12) — power/swing/startup/PVT measured; 2 gaps
Current netlist (= `origin/main`, no diff), `vco_tb`, `.option method=gear`, at the
ISM operating point **VTUNE = 2.15 V**. `tran 5p 80n`, settled 60–80 ns. File-read.

| corner | VCO freq | ÷2 | core swing (se / diff) | total I (buf incl) | core I (ISS) |
|---|---|---|---|---|---|
| TT 27C  | 4.751 GHz | 2.375 | 2.03 / 4.04 Vpp | 5.04 mA (16.6 mW) | 1.38 mA (4.6 mW) |
| FF      | 4.828 | 2.414 | 2.04 / 4.06 | 5.94 mA (19.6 mW) | 1.57 mA |
| SS      | 4.640 | 2.320 | 2.01 / 4.00 | 4.37 mA (14.4 mW) | 1.24 mA |
| TT −40C | 4.740 | 2.370 | 2.19 / 4.36 | 5.26 mA | 1.36 mA |
| TT +85C | 4.764 | 2.382 | 1.88 / 3.75 | 4.92 mA | 1.40 mA |

- **Swing:** near rail-to-rail single-ended (~2 Vpp-se, core rides 1.27–3.30 V) at every
  corner — a strong oscillator, ample to drive the divider CML clock directly.
- **Startup:** self-starts; ~14 ns latency then builds 16→24 ns to full 4.04 Vpp diff
  (the 14 ns is op-point metastability breaking on numeric noise — thermal noise starts
  it faster in silicon). **Bench: allow ~30 ns before reading.**
- **Power:** VCO **core 1.2–1.6 mA (~4–5 mW)**; the 16.6 mW / 5 mA "VCO" budget figure is
  core **plus the TB output buffer** (source-followers + 1 mA bias). Budget line = 5 mA if
  an on-chip buffer like the TB's is used; core alone is ~1.4 mA.
- **Freq PVT** spread 4.64–4.83 GHz (process) / 4.74–4.76 (temp) at VTUNE 2.15 V — tight.

**GAP 1 — RESOLVED: §3.1's mid-curve was a measurement error; corrected sweep below.**
Container is stable (CP compliance reproduced, above), so §3.1 was NOT drift. Re-ran the
f-VTUNE sweep on the current netlist (core net1−net2, 80 n tran, settled 60–80 ns):

| VTUNE (V) | VCO (GHz) | ÷2 (GHz) | core diff (Vpp) | §3.1 said | Δ |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 6.378 | 3.189 | 4.33 | 6.367 | +11 |
| 0.8 | 6.127 | 3.063 | 4.30 | 6.247 | −120 |
| 1.2 | 5.848 | 2.924 | 4.26 | 5.669 | +179 |
| 1.6 | 5.476 | 2.738 | 4.20 | 5.442 | +34 |
| 2.0 | 4.929 | 2.464 | 4.09 | 5.235 | −306 |
| 2.4 | 4.490 | 2.245 | 3.95 | 4.919 | −429 |
| 2.8 | 4.187 | 2.094 | 3.78 | 4.527 | −340 |
| 3.3 | 4.047 | 2.024 | 3.68 | 4.114 | −67 |

- **Band edges MATCH** §3.1 (mine 4.05–6.38 GHz vs 4.11–6.37) — the native band and Plan B's
  structure stand. The corrected curve is **smooth and monotonic** (a physical varactor C–V);
  §3.1's anomalous "steep 0.8→1.2 V / KVCO −1.4 GHz/V" region does **not** reproduce and was
  the error (likely mid-range settling/measurement artifacts at those points).
- **Corrected ISM mapping:** DIV2 2.4–2.5 GHz ⇒ VCO 4.8–5.0 GHz at **VTUNE ≈ 1.95–2.12 V**
  (§3.1 said 2.05–2.28 V — shifted **down ~0.15 V**). Avg KVCO −706 MHz/V (≈ §3.1's −683),
  but **local KVCO near ISM ≈ −1.1 GHz/V** (§3.1 said −790 MHz/V — steeper; matters for loop
  gain). **`scope.md` Plan B VTUNE window and the loop-filter KVCO should be updated to
  1.95–2.12 V / −1.1 GHz/V.** ISM stays comfortably mid-band — reachable — as predicted.

**GAP 2 — phase noise is NOT measurable with the open-source toolchain (closed).** ngspice
has no PSS or harmonic-balance engine for autonomous oscillators, so the only route is a
long transient + FFT. At 5 GHz that number is dominated by the simulator's numerical noise
floor and timestep jitter, NOT device (thermal/flicker) noise — it would be a figure one
would have to caveat into meaninglessness. Per Caglar's "phase noise if possible": the
honest answer to condition 5 is that it is not obtainable here; it needs a PSS-capable tool
(Spectre/ADS/AFS) at signoff. Output power/harmonics ARE measurable and stand as the
sanity baseline (Zach's tb): −1.55 dBm into 50 Ω, H3 −18.4 dBc.

**Container stability — CONFIRMED across 3 independent domains (no drift).** GAP 1 is a
§3.1 error, not drift:
1. **DC** — CP_v1 compliance reproduces **0.32–2.98 V / best 0.0011 % @ 1.50 V** vs the
   2026-07-22 record 0.32–3.00 V / 0.001 %.
2. **Analog transient** — the corrected VCO **band edges match** §3.1 (4.05–6.38 vs
   4.11–6.37 GHz); if models had drifted, oscillation frequency would have moved and it
   didn't (only §3.1's mid-curve, a measurement artifact, differs).
3. **Digital transient** — PFD_v1 **min reset pulse 0.500 ns** at equal REF/FB vs the
   0.48–0.50 ns record.
So the whole pre-7/30 evidence base (PFD dead-zone, CP steering, etc.) is safe. **Toolchain
fingerprint (record for future drift detection): ngspice-46 (KLU), open_pdks `7b70722e33c…`,
Ubuntu 24.04.4.**

### 4.0 Inductor `.mag` DRC — CLEAN in both tools (2026-08-14, file-read)
The spiral `vco_inductor_v2.mag` had never been shown DRC-clean (it gates 5.4). Checked
headless: **Magic DRC 0** (`drc euclidean on`, full check) and **KLayout DRC 0** — GDS
written from the `.mag`, `run_drc.py --variant=D` (5LM/11K, matches gf180mcuD) reports
"run is clean, GDS has no DRC violations" over 247 polygons. **Scope caveat:** this is the
base FEOL/BEOL deck; `--density` was **not** run, so the metal-fill/min-density question in
§4 item 3 (no automatic fill protection for the inductor) is still open and separate from
this clean base-rule result. The spiral is placeable as-is for 5.4; density/fill ownership
stays a Bailey question.

### 4.1b Inductor EM (6.2) — openEMS setup built + runs; solve deferred (2026-08-14)
`team_src/sim/ind_em/ind_em.py` (openEMS): parses the `.mag` (20 units/um), builds the
gf180mcuD metal4/via4/metal5/rm5 stack at the real z-heights (magic tech `height` lines:
m4 4.68-5.23, via4 5.23-5.83, m5 5.83-6.8325 um), places a differential lumped port across
the 30 um gap between the two metal5 leads (no ground plane -> Z11 = jwL+R of the coil),
meshes (edge-decimated to 1.5 um min), and post-processes Z11 -> L/Q/SRF vs the 1.2 nH
pi-model. **Verified: model builds, FDTD engine runs** (32k cells, dt 9.6e-16 s, ~3-6
MCells/s). **Solve DEFERRED under the 15 min/launch cap:** the low-freq Gaussian pulse needs
~297k timesteps and dt is capped by the 0.55 um metal4 thickness (a thin 3D z-cell) -> ~50
min full 3D solve. **Resume fix:** model metal4/metal5 as openEMS conducting sheets so the
z-mesh coarsens to ~1.5 um -> dt ~3e-15 s -> ~11 min solve; re-place the gap port on the
metal5 sheet plane; the post-processing runs unchanged. Not critical-path — Mohan (§4.1)
already confirms 1.2 nH; EM is a Q/SRF refinement.

## 4. Inductor / condition 6 — state + plan (2026-08-12, not yet run)

**The spiral IS drawn — not model-only.** `team_src/magic/vco_inductor_v2/vco_inductor_v2.mag`
is a real 3-turn dual square spiral (43 shapes on metal4/via4/metal5/rm5 + labels; params
D_in=20, D_out=76, N=3, W=8, S=2, Gap=30). BUT `team_src/xschem/vco_inductor_v2.subckt` is an
**analytical lumped π-model** (L0 0.60 n ×2 = 1.2 nH, metal R via `tm11k`, C) — hand-computed
from spiral formulas, **NOT extracted from the `.mag`**. This is the "preliminary model"; the
whole VCO band (§3.2, 4.05–6.38 GHz) rests on that 1.2 nH. **EM has never been run.**

**Revised order (the spiral being already isolated relaxes the Phase 5/6 coupling):** EM runs
on the existing `.mag` **independent of 5.4** — no need to draw it first. So: (1) Mohan
analytical cross-check of 1.2 nH; (2) openEMS/FastHenry on `vco_inductor_v2.mag` for real
L/Q/SRF/coupling; (3) if L disagrees, **PREFER accept-and-replan over redraw** — ISM sits
mid-band with margin, and chasing a target L costs Q/area for no functional gain; a 20–30 %
error does not put 2.4–2.5 GHz out of reach, so redraw ONLY if extracted L moves ISM outside
tuning range. 5.4's VCO layout just *places* this cell.

**Three items to settle BEFORE 5.4 (planned tonight, unresolved):**

1. **Inductor LVS — DECIDED (waiver, black-box the spiral).** Extraction of the drawn spiral
   metal yields distributed R/L, NOT the analytical π-model's lumped elements — netgen has
   nothing to match a spiral against a π-model, and this is unlike the transistor/std-cell cases.
   **Decision:** treat `vco_inductor_v2` as a **black box** in LVS and substitute the golden's
   π-model subckt for it, at BOTH the VCO block level and the RFIC top level. This is the third
   documented LVS waiver under rubric row 1 (alongside the two existing `__fillcap_[[:digit:]]+`
   decap ignores). **Waiver W3 (inductor black-box):** in the netgen setup, `ignore class` the
   spiral cell (regexp-restricted to `vco_inductor_v2` only, exactly as the fillcap ignores are
   scoped — NOT a blanket loosen), so netgen compares the rest of the VCO against the golden with
   the inductor represented by its π-model on both sides. Justification: the spiral is a passive
   with an EM-derived model; its terminal connectivity (PORT1/PORT2/GND) IS checked, only its
   internal distributed structure is black-boxed — standard practice for inductors/RF passives.
   Implement in `verify_cp.sh`'s local setup at the VCO/top stage (mirrors the fillcap block).
2. **Top-metal keep-out.** Spiral is on metal4/metal5/rm5; integration is organizer-scripted.
   **Confirm nothing is routed above the spiral** — overlying metal degrades Q and shifts L, and
   we do not control the organizer's router. Coordinate the keep-out with the organizer.
3. **Density vs Q — the sleeper (confirmed real in the gf180 deck).** Bailey requires min clear
   density; fill under/around a spiral degrades Q / shifts L. Checked
   `libs.tech/klayout/tech/drc`: an inductor marker **`IND_MK` (layer 151/5) exists but only
   `fill_comp.rb`/`fill_poly2.rb` honor it** (COMP/poly fill excluded within a 3 µm halo — protects
   substrate). **`fill_metal.rb` does NOT reference IND_MK** — metal fill only keeps 2 µm from
   existing metal, so it **WILL fill the spiral interior/surroundings (metal4/5), degrading Q**.
   `metalX_blk` (datatype 5) exempts a region from the density *requirement* but does **not** stop
   the fill script. So there is **no automatic metal-fill protection for the inductor** in this deck.
   **Fix — lead with owning the fill, not negotiating it:** **pre-fill our own block to density
   with a manual metal-fill keep-out around the spiral**, so the GDS we hand over is already
   density-compliant and the organizer's fill flow has nothing to add — this removes the dependency
   on a script we don't control and can't test against. `metalX_blk` over the inductor covers the
   residual density exemption; the waiver documents both. **Fallback if we do end up negotiating a
   keep-out:** ask only for the **inner opening + ~1 trace-width of surround** (where fill actually
   hurts Q — far-surround fill is nearly harmless); a narrow technically-justified ask gets granted,
   a whole-block one gets pushed back. **Open question for Bailey (Greg to ask — pairs with the
   stale #143 items):** on a team block, does the *team* run metal fill or the integration script?
   "integration is organizer-scripted" vs "your own project must pass min clear density" leaves fill
   ownership ambiguous, and the answer decides whether pre-filling works or is moot. Settle before
   final DRC.

### 4.1 Mohan analytical cross-check (2026-08-12, done — CONFIRMS 1.2 nH)
**Turn count read directly from `.mag` geometry (scale 20 units/µm — seg width 160 u = W=8 µm).**
The metal5 path is **TWO 3-turn square spirals side by side**, each D_out=76 µm (left half spans
x −2240..−720 = 1520 u = 76 µm), **30 µm apart (= the Gap param)**, connected **in series-aiding**
(differential, PORT1/PORT2 at bottom-center). Left half turns at x −2160/−1960/−1760 (pitch 200 u
= 10 µm = W+S) ⇒ **N=3 per half**, not one 6-turn concentric spiral. metal4 = a short underpass
bridge only.
**Earlier draft compared per-half Mohan against the TOTAL 1.2 nH — that was the error.** Correct
comparison, per half: Mohan current-sheet (square c1=1.27 c2=2.07 c3=0.18 c4=0.13, n=3, D_out=76,
D_in=20 ⇒ d_avg=48, ρ=0.583) = **0.49 nH**; π-model per half = 0.6 nH → **18 %, within Mohan's
~15–20 % accuracy**. Total = 2·L_half + 2M ≈ 2×0.49 + ~0.10 (halves 30 µm apart, weak k) ≈
**~1.08 nH vs the π-model's 1.2 nH — agree within ~10 %. The 1.2 nH is CONFIRMED analytically.**

**Consequence:** the Plan B band (4.05–6.38 GHz, measured on 1.2 nH) **stands**; ISM 2.4–2.5 GHz is
reachable as measured. **EM (6.2) is a Q / SRF / exact-L refinement, NOT a frequency critical-path.**
Per 6.3, if EM nudges L, prefer accept-and-replan (re-sim, move VTUNE, propagate) over redraw.

(6.2 stays PENDING until openEMS or FastHenry is installed — **queued for Greg**; runs on the
existing `.mag`, independent of the block layout.)

## 5. Notes — "For Zach" (Greg to relay; not edited here)

Two items in Zach's never-edit cells, left untouched:
1. **`D_FF_v1` — DUPLICATE-IOPIN CLAIM DISPROVEN (2026-08-05).** Zach asked us to
   delete the duplicate VDD/VSS iopins; on investigation **there are none.** The
   earlier "symbol 5 pins / schematic 6, 1 dup power" note was **incorrect** (likely
   confused with `D_FF_RST_v1`, which genuinely had 12 duplicate power iopins, since
   fixed §1.4). Verified on disk:
   - `D_FF_v1.sch` has **exactly one** `iopin lab=VDD` (p3) and **one** `iopin
     lab=VSS` (p6) — 6 ports total (CLK, D, VDD, Q, !Q, VSS). (The many `N …
     {lab=VDD/VSS}` lines are wire segments, not ports.)
   - `D_FF_v1.sym` has **6 pins** (VDD, D, Q, CLK, !Q, VSS) — matches the 6 schematic
     ports. Netlisting emits **no** symbol-vs-schematic pin-mismatch warning.
   - Identical across **all four origin branches** (main, integration, cp-wip,
     reset-dff-wip); the `.sch`/`.sym` were never modified since creation (`413a1db`).
   - `D_FF_v1` is **not instantiated by any cell** in the repo (PFD uses
     `D_FF_RST_v1`), so it affects no netlist/LVS regardless.
   **Do not "fix" this — deleting a VDD or VSS iopin would remove a required port.**
   If Zach still sees a duplicate, he is looking at a different/local copy; confirm
   which before any edit.
2. **`vco_v1`** — hardcoded include `/foss/designs/xschem/vco_inductor_v2.subckt`
   (portability bug: breaks netlisting in any clone not at that exact path). Should
   be a relative include or resolved via `XSCHEM_LIBRARY_PATH`.

## 6. LibreLane pipeline proof (Aug-6 sample-GDS backing) — PASS (to floorplan)

Ran the workshop-slot flow to floorplan (`--to OpenROAD.Floorplan`) in the
container (LibreLane **3.0.3**).

- **First attempt failed at PDK config load:** `TclError: no files matched glob
  "…/gf180mcuD/libs.ref/sg13g2_stdcell/techlef/*__nom.tlef"`. LibreLane 3.0.3
  injects `sg13g2_stdcell` (an **IHP** SCL) as the default instead of honoring the
  PDK's `STD_CELL_LIBRARY=gf180mcu_fd_sc_mcu7t5v0`. This is the 3.0.3-vs-pinned-
  3.0.0 drift the repo docs warn about.
- **Workaround (no pin, no install):** force `--scl gf180mcu_fd_sc_mcu7t5v0` on the
  CLI. Config load then cleared.
- **Result:** synthesis + floorplan complete, "Flow complete.", exit 0. Floorplan
  die 2935×2935 µm, core 442…2493 (matches the workshop slot). Benign warnings
  only. **The pipeline runs end-to-end at 3.0.3 with the `--scl` override.** Full
  signoff (Run A) uses the same override.

## 7. Divide-by-2 divider feasibility (DIV2, condition 1 minimum scope)

**Static CMOS cannot divide the VCO — a high-speed first stage is mandatory.**

Probe `DIV2_toggle_probe_tb.sch`: `D_FF_RST_v1` as a toggle FF (D tied to !Q),
reset to break latch symmetry, CLK swept. TT, 27 °C, 3.3 V.

| CLK | QOUT Vpp | ÷2? |
|---:|---:|---|
| 1.00 GHz | 3.68 V | ✅ clean (QOUT = 500 MHz) |
| 2.00 GHz | 0.61 V | ✗ not reaching logic levels |
| 3.00–6.37 GHz | < 2 mV | ✗ dead |

- **Static-CMOS max clean ÷2 ≈ 1–1.5 GHz**, dead by 3 GHz.
- **VCO native band is 4.11–6.37 GHz** (§3) — static CMOS can't handle even the
  *slowest* VCO frequency, let alone the 6.37 GHz worst case.
- **First divider stage must be CML or TSPC.** CML (differential current-steering)
  takes the differential VCO clock directly, reaches 6.37 GHz easily in 180 nm, and
  gives quadrature I/Q naturally — but burns static bias current and is larger.
  TSPC (dynamic, single clock) is lighter but marginal at 6.37 GHz in 180 nm. Static
  CMOS (`D_FF_v1`-style) is viable only for later ÷2 stages once ≤ ~1 GHz.

**Decision: CML** (Greg). Single CML ÷2 = two NMOS CML D-latches in a master-slave
ring, master clocked by VCO `out_p`/`out_n`, slave on the complement; one loop
inversion (slave outputs cross-fed to master inputs) → ÷2 with **quadrature I/Q**
at VCO/2 (2.06–3.18 GHz). Device-level (per latch): track pair + cross-coupled
latch pair + clock-steering pair (6× nfet_03v3, W≈10 µm/L=0.3 µm), 2× load R
(≈2 kΩ for ~400 mV single-ended swing at 200 µA tail), tail current source.
Two latches + a CMOS-level output buffer (CML ~400 mV → rail). Bias explicit:
external `IBIAS_CP`-style reference sets the tail current (documented, `pins.md`).

**Power cost (vs static-CMOS elimination above):** CML draws **continuous** bias —
2 latches × 200 µA tail ≈ **0.4 mA → ~1.3 mW static** at 3.3 V (before the output
buffer), against **~0 static** for the (unusable) static-CMOS divider. This is the
price of reaching the 4.11–6.37 GHz band; it is the divider's dominant power term.

**Build + bring-up (in progress).** Flat probe `DIV2_CML_probe_tb.sch` (12×
nfet_03v3 CML ÷2, ideal tails, R loads, differential clock) — generated
programmatically, netlist-clean, zero auto-nets.

Sizing progression (W=40 µm nfet_03v3, differential clock, ideal tails):

| tail / R | 1 GHz | 3 GHz | 5 GHz | 6.37 GHz | swing |
|----------|-------|-------|-------|----------|-------|
| 400 µA / 2 kΩ | ✅ ÷2 | ✗ | ✗ | ✗ | 1.6 V |
| 1.2 mA / 500 Ω | — | — | ✅ ÷2 | ✗ (~2 GHz) | 0.44 V |
| **2.4 mA / 300 Ω** | — | — | ✅ ÷2 | ✅ **÷2** | 0.83–1.4 V |

**Full-band ÷2 + quadrature CONFIRMED** (final sizing, tail 2.4 mA / R 300 Ω):

| VCO in | ÷2 out (meas) | quadrature phase(I→Q) |
|-------:|--------------:|----------------------:|
| 4.11 GHz | 2.058 GHz | −90.4° |
| 5.00 GHz | 2.500 GHz | −90.0° |
| 6.37 GHz | 3.185 GHz | −90.0° |

- Clean ÷2 across the **entire 4.11–6.37 GHz native band**; consistent **−90°
  quadrature** (Q leads I) at all three points. Differential swing 0.83–1.4 V.
- **Final power (honest):** two tails × 2.4 mA = **4.8 mA → ~16 mW static** at 3.3 V
  (before output buffers), vs ~8 mW at the 5 GHz-only checkpoint and ~0 for the
  eliminated static-CMOS divider. **Reaching the 6.37 GHz band top doubled the
  current** — the dominant divider power term and the price of the CML choice.

**Remaining:** CMOS-level output buffers (4×, for I_P/I_N/Q_P/Q_N); replace ideal
tails with a real bias mirror (`IBIAS`); package into `DIV2_QUAD_v1.sch/.sym`
(cell + symbol). Can wait for the next session / Run-A window (with condition-5 VCO
characterization + condition-6 inductor re-extraction).

**Bias mirror sizing (decided 2026-08-04):** external reference **240 µA** into a
diode-connected NMOS at the bias pad sets `VBIAS`; each tail device mirrors **10:1**
→ **2.4 mA per tail**. Two tails → **4.8 mA total CML core current** (240 µA × 10 ×
2 = 4.8 mA). This replaces the two ideal 2.4 mA sources in `DIV2_CML_probe_tb`.
Output-buffer topology: CML→CMOS rail-to-rail (PMOS-input diff converter, since the
CML common mode sits near VDD, + CMOS inverter). **Buffer supply current vs the
off-chip 50 Ω load is under review — see the load-model note; a rail-to-rail buffer
into a DC/AC-coupled 50 Ω exceeds a single VDDA pad's ~50 mA budget, so the output
stage is not finalized.**

**Decision (Greg):** CML chosen.

**Along the way:** `D_FF_v1` (no reset) can't self-start a toggle FF from the
symmetric latch state (needs a symmetry-break); use `D_FF_RST_v1`. `D_FF_RST_v1`
**RST is active-low**.

### 7.1 Output converter — reworked to 3 stages, STILL NON-WORKING (2026-08-10)

Full analysis in `docs/div2-debug.md` (2026-08-10 section). Summary:

- **CML core is unaffected and still divides** — OI−OIB = **±0.557 V steady** at 16–20 ns.
  The `move-b` fix (CML-input pair 16 µm → 8 µm) recovered the differential from the
  Miller-collapsed ±0.13–0.20 V to full ±0.557 V, and it **holds in steady state**.
- **The CML→CMOS output converter still does not work.** Rebuilt as a 3-stage chain
  (skewed trip-setter → restoring inverter → driver). At 6–10 ns it looked rail-to-rail
  (I_P 142 mVpp); measured to **16–20 ns it collapses to 21 mVpp** — the earlier result
  was a decaying transient during bias settling.
- **Root cause is a class:** every converter fault so far is an *absolute threshold match
  between two independently-moving nodes* (PMOS input vs |Vth|; inverter trip vs OC;
  stage-1 midpoint vs stage-2 trip). Resizing fixes one instance and exposes the next.
  **Aug-21 rework removes threshold matching by construction** (self-biased inverter with
  AC-coupled input, or a differential OC/OCB converter), rather than chasing another trip.
- **Output monitor load relocked 450 Ω → 1 kΩ series isolation R** (supersedes the
  "under review" note above and the old 450 Ω ruling). 1 kΩ gives ~124–157 mVpp (−12 dBm)
  at the 50 Ω instrument — ample for a monitor pad — with a moderate 3-stage driver at
  **~12.6 mA peak / ~6.3 mA avg per** the four buffers, comfortably inside the ~50 mA VDDA
  budget (core ~8.7 mA). This **subsumes the earlier output-buffer supply concern**.
- **Toolchain note (portable):** under `uic`, bias nodes start at 0 and a chain with a DC
  operating point needs **>10 ns to settle** — run 20 ns, measure 16–20 ns. The old
  "settles by 2–6 ns" applies to the CML core only. `min/max/avg` hid this collapse; it was
  caught only by dumping the waveform.

DIV2 remains **CUT from the Aug-14 scope**; this is an Aug-21 item.

---

## 8. Chip-level DRC baseline (phase 8) — compare BOX SETS, not totals

### 8.1 The rule
**magic's `drc list count total` is frame-dependent and is NOT a valid gate across a frame
change.** Seating `chip_top` inside the A01_BH DIEAREA on 2026-08-22 was a pure +200/+200
translation — no geometry created, moved relative to anything, or deleted — yet the reported
total went **84 → 106**. The violations themselves were bit-identical: **252 boxes on both
sides, 0 added, 0 removed**, one rule (`PL.5a`, poly spacing to diffusion < 20). Magic
re-attributes errors per cell when the parent frame moves.

Proven three ways, not assumed:
1. Three throwaway variants of the seated GDS through the same deck — 0/0 boundary layer
   deleted → still 106; boundary restored at the old core extent → still 106; core
   translated back −200/−200 → **84**. It tracks absolute position, not the boundary.
2. Box-set multiset comparison after normalising the shift → **0 added, 0 removed**.
3. KLayout, the actual signoff deck, reports **84 PL.5a_LV + 84 PL.5b_LV before and after** —
   unchanged.

> **A phase-8 "zero added violations" gate must compare the box set. A gate comparing totals
> would have read this as 22 new violations and sent someone hunting a bug that does not
> exist.**

### 8.2 The committed baseline
`team_src/magic/chip_top.drcbase` — the seated `chip_top` box set, regenerate with
`analysis/drc_boxset.tcl`:

| figure | value | frame |
|--------|-------|-------|
| magic total | **106** | seated (die frame, boundary 0,0–1110,550) |
| violation boxes | **252** | seated |
| rules | 1 — `Poly spacing to diffusion < 20 (PL.5a)` | — |
| per-cell attribution | `vco_v1` 84, `vco_varactors` 84, `chip_top` 106 | seated |
| magic total | **84** — **PRE-SEAT ONLY, do not compare against a seated run** | core frame (boundary −25,−21.5–497,287.5) |

All 252 are the device-internal `nmoscap_3p3` errors inside `vco_varactors` — the same
population as the **W4** KLayout waiver (168 = 84 PL.5a_LV + 84 PL.5b_LV).

### 8.3 The tools
- **`team_src/magic/analysis/drc_boxset.tcl`** — env `GDSF` (required), `CELL` (default
  `chip_top`). Emits `TOTAL`, `CELLCOUNT <cell> <n>`, `RULE <n> <text>`, and one
  `B x0 y0 x1 y1` per violation box in magic internal units (1 iu = 1 GDS dbu = 0.005 µm).
- **`team_src/magic/analysis/drc_delta.py <baseline> <candidate> [--shift DX_IU DY_IU]`** —
  compares the two dumps as **multisets**. `--shift` offsets the baseline so a core-frame
  dump can be compared against a die-frame one (the +200/+200 seat is `--shift 40000 40000`).
  Exit 0 iff the candidate adds no box; it also reports boxes that vanished, since that is a
  change worth seeing too.

Reference run reproducing §8.1:
```
$ drc_delta.py preseat.dump seated.dump --shift 40000 40000
baseline : TOTAL=84   boxes=252  (shift +40000,+40000 iu applied)
candidate: TOTAL=106  boxes=252
NOTE: totals differ (84 -> 106). That alone means nothing ...
ADDED   (in candidate, not in baseline): 0
REMOVED (in baseline, not in candidate): 0
RESULT: PASS -- no violation box in the candidate that the baseline lacks.
```

### 8.4 Do not compare across rule sets
Three different chip-level DRC numbers exist for the same GDS and they are not
interchangeable:

| what | number | why it differs |
|------|--------|----------------|
| `verify_cp.sh chip_top` (magic) | **0** | preloads the `vco_varactors` + `vco_inductor_v2` abstracts, so the PL.5a geometry is never traversed |
| `drc_boxset.tcl` (magic, full geometry) | **106 / 252 boxes** seated | no preload — this is the phase-8 haul gate |
| `klayout_signoff.py chip_top` | **PASS, 168 waived** | the signoff deck; W4 waiver = 84 PL.5a_LV + 84 PL.5b_LV |

A number from one row means nothing against a number from another.
