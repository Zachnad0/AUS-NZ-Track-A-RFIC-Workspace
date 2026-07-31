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
| `D_FF_v1` | 5 | 6 (1 dup power) | 1 dup power | Zach | **not touched** — flagged to Zach; not in PFD hierarchy |
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
1. **`D_FF_v1`** — duplicate power `iopin` (symbol 5 pins / schematic 6): one extra
   VDD or VSS `iopin`. Same class as the PFD_v1/D_FF_RST_v1 issue (§1.4) but
   `D_FF_v1` is **not in the PFD hierarchy**, so it does not affect condition 4.
   Should be cleaned before any layout that uses `D_FF_v1`.
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

**Decision pending (Greg):** CML vs TSPC for the high-speed first ÷2. `DIV2_QUAD_v1`
authoring is on hold until the topology is chosen.

**Along the way:** `D_FF_v1` (no reset) can't self-start a toggle FF from the
symmetric latch state (needs a symmetry-break); use `D_FF_RST_v1`. `D_FF_RST_v1`
**RST is active-low**.
