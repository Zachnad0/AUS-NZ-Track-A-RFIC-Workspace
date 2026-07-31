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

## 3. VCO characterization (condition 5) — PENDING
## 4. Inductor re-extraction (condition 6) — PENDING
