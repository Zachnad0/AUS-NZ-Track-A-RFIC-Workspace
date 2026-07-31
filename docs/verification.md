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

---

## 2. PFD three-case verification (condition 4) — PENDING

Testbenches drafted (`PFD_tb_lead`, `PFD_tb_lag`, `PFD_tb_eqfreq`) at 3.3 V with
≥50 ns arming delays; netlist + run queued for container availability. Baseline to
reproduce: UP = 101 ns at a 100 ns REF-vs-FB offset, ~1 ns reset pulse, 1 MHz.

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
