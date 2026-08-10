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
(not yet a finding):** the STA figure is **wire-RC only and excludes pin capacitance**,
whereas PEX includes the full node cap. The two are not directly comparable until pin cap
is added to the STA path; recorded here so a future reader does not treat them as contradictory.

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

**Note on the run:** `vco_v1`'s netlist hardcodes an include path
`/foss/designs/xschem/vco_inductor_v2.subckt`; corrected to the clone's actual
path in the *generated deck only* to run (no schematic edit — see "For Zach").

### 3.2 Remaining VCO characterization — PENDING
Corners (ss/ff + temp), supply current/power, startup time, tank swing, phase
noise/harmonics. Sanity baseline (Zach's tb): −1.55 dBm into 50 Ω, 16.6 mW,
H3 −18.4 dBc.

## 4. Inductor re-extraction (condition 6) — PENDING

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
