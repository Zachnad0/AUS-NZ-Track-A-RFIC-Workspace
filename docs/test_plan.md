# Test Plan — AUS/NZ Track A RFIC (Team A01)

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU (gf180mcuD)**
Drafted 2026-11-02. **DRAFT — every value marked `TODO` has no source in this repository and
must be filled in before the bench session; nothing here is invented.** Every number that is
given is a pre-silicon simulation or PEX result, cited by file path. None of it is a measurement
of silicon.

---

## 1. Scope

This is an **open-loop characterization** plan for the die described in `info.yaml`
(`project.title`): *"Open-loop integer-N PLL characterization chip: LC-VCO, quadrature divider,
PFD and charge pump"* (the scope of issue #143).

- **No closed-loop lock is claimed, and none is tested.** The feedback path divides by 2 only and
  `I_P → PFD.FB` is an internal net, so no external divider can be inserted; at the ~2.4–2.5 GHz
  reference that N = 2 requires, the PFD's reset pulse is 1.22× the period at typ and 0.96× at
  ff (`docs/layout-review-sep01.md` §4.6.1; `info.yaml` `project.description`).
- Every block is measured open-loop through its own pads: VCO via the ÷2 outputs, DIV2 at the
  I/Q pads, PFD+CP at `CP_OUT`, IBIAS at its reference pad.
- No phase-noise target exists, because no phase-noise simulation exists: ngspice has no PSS or
  harmonic-balance engine (`docs/verification.md` §3.2 GAP 2; `docs/layout-review-sep01.md` §6
  item 2).

## 2. Pin map

Exact names and types from `info.yaml` `pins:` (12 pads, in file order). Pad slots are from
`docs/pins.md` §1; the slot variant there (BH) predates the final padframe assignment, so the
**package pin / bond map is TBD pending organizer packaging decision**.

| # | Pin (`info.yaml`) | `io_type` | Function (`docs/pins.md` §1; supply domains from `docs/layout-review-sep01.md`) | Package pin |
|---|---|---|---|---|
| 1 | `VSSA` | ground | Quiet analog ground; same on-chip node as VSSD | TBD pending organizer packaging decision |
| 2 | `VDDA` | power | Analog supply (CP, VCO, IBIAS) | TBD pending organizer packaging decision |
| 3 | `IBIAS` | analog | Chip-level bias reference, external current | TBD pending organizer packaging decision |
| 4 | `ISS` | analog | LC-VCO tail node, driven off-chip | TBD pending organizer packaging decision |
| 5 | `VTUNE` | analog | VCO control voltage | TBD pending organizer packaging decision |
| 6 | `CP_OUT` | analog | Charge-pump output | TBD pending organizer packaging decision |
| 7 | `Q_N` | analog | Divider quadrature output − | TBD pending organizer packaging decision |
| 8 | `I_N` | analog | Divider in-phase output − | TBD pending organizer packaging decision |
| 9 | `Q_P` | analog | Divider quadrature output + | TBD pending organizer packaging decision |
| 10 | `VSSD` | ground | Digital-island ground; same on-chip node as VSSA | TBD pending organizer packaging decision |
| 11 | `VDDD` | power | Digital supply (PFD, DIV2) | TBD pending organizer packaging decision |
| 12 | `REF_IN` | input_cmos | PFD reference input; weak pull-down (PD=1, PU=0) | TBD pending organizer packaging decision |

Not available at any pad: `I_P` (internal, feeds `PFD.FB`), the PFD's `UP`/`DOWN`, and the
IBIAS generator's outputs `VGP`/`VGN`/`IB_DIV2` (`docs/pins.md` §1;
`docs/layout-review-sep01.md` §4.6.1).

**ESD handling.** Secondary clamps exist on `IBIAS` and `ISS` only. `VTUNE`, `CP_OUT`, `I_N`,
`Q_P` and `Q_N` have none, and no ESD simulation of any kind has been run (`docs/pins.md` §2).

## 3. Supply and bias conditions

| Quantity | Value | Source |
|---|---|---|
| `VDDA` | 3.3 V | `docs/scope.md` §4.1 (single 3.3 V rail); all sims TT / 3.3 V / 27 °C (`docs/verification.md` §2.6, §3.1) |
| `VDDD` | 3.3 V | `docs/scope.md` §4.1 |
| `VDDA`/`VDDD` current limit | TODO | — |
| Expected supply current, chip | ≈ 25 mA core-only, against a ~50 mA budget | `docs/layout-review-sep01.md` §4 "Power budget" |
| Expected supply current, `VDDD` | 22.9 mA = DIV2 22.4 mA (simulated, `i(v_vdd)` of `div2_sb_TT`) + PFD ≈ 0.5 mA (inferred, not simulated). Later DIV2 runs: 22.118 mA with modelled passives, 22.791 mA with one converter extracted | `docs/layout-review-sep01.md` "Phase C — the chip-level VDDD path"; `docs/phase7-routing-plan.md`; `signoff/pex/ib_conv_v1/resim.md` |
| Expected supply current, `VDDA` | 3.5 mA, **an estimate from bias structure, not a simulation**; needs a run (§8) | `docs/phase7-routing-plan.md` ("vco/CP/ibias/PFD estimated from bias structure") |
| `IBIAS` reference current | 240 µA, forced current | `docs/pins.md` §1; `docs/verification.md` §2.6 |
| `IBIAS` current direction | Sourced **into** the pin from the supply (`I_BIAS VDD IBIAS 240u`); the pin lands on a diode-connected nfet | `team_src/sim/ibias/ibias_op.spice`; `docs/esd-which-pins.md` |
| `IBIAS` pin voltage / compliance | TODO; needs a run (§8). No `v(IBIAS)` output is committed | — |
| `ISS` tail current, nominal (sim "1.0×") | 1.35 mA tail, from a 1 mA reference into a 1:1 NMOS mirror on the bench | `docs/verification.md` §3.2, §3.2.1 |
| `ISS` tail current, bring-up (sim "2.0×") | ≈ 2.3–2.38 mA tail (reference 1 mA → 2 mA); needed for the top of the tuning range to start | `docs/verification.md` §3.2.1 |
| `ISS` off-chip circuit (mirror or current sink) | TODO | — |
| `ISS` node voltage / required sink compliance | TODO; needs a run on the landed extraction (§8). The only recorded ISS-node voltage, 0.698 V at 4.0× falling to 0.475 V at 6.0×, is from the **pre-landing** extraction that did not oscillate, so it does not apply | `docs/verification.md` §3.2 |
| `VTUNE` range | 0–3.3 V (simulated sweep range) | `docs/verification.md` §3.1, §3.2.1 |
| `REF_IN` amplitude / levels | TODO | — |
| `REF_IN` frequency | TODO (PFD simulated at 1 MHz and 2 MHz) | `docs/layout-review-sep01.md` §4.6.1 |
| Power-up sequencing | TODO | — |
| Settling before reading outputs | ≥ 30 ns for the divider; ≥ 200 ns (startup 83 ns) for the VCO | `docs/scope.md` §7; `docs/verification.md` §3.2.1 |

## 4. Required equipment

Generic only; models and settings are `TODO`.

- Spectrum analyzer, covering at least the ÷2 output band (`TODO`: frequency range).
- Signal generator for `REF_IN`.
- DC power supplies for `VDDA` and `VDDD`, with current readback.
- Precision DC voltage source for `VTUNE`.
- DC current sources (or SMU) for `IBIAS` and `ISS`, and for forcing/measuring `CP_OUT`.
- Oscilloscope, with enough bandwidth for the ÷2 outputs (`TODO`: required bandwidth), for I/Q
  phase and duty cycle.
- 50 Ω cabling and terminations for `I_N`, `Q_P`, `Q_N`; the outputs are designed into a 50 Ω
  instrument (`docs/scope.md` §4).
- Test PCB / socket: TBD pending organizer packaging decision.

## 5. Per-block tests

Each "expected" value is a simulation or PEX result. **The repo defines no acceptance
tolerances, so every pass/fail limit is `TODO`.** Where a schematic number and a layout-extracted
number both exist, the extracted one is listed first, because it describes the shipped layout.

### 5.1 VCO — frequency vs VTUNE, output power, phase noise

The VCO has no pad of its own. It is observed at `I_N` / `Q_P` / `Q_N`, at **f_VCO / 2**.

**Procedure.** Set the supplies and IBIAS (§3). Set the ISS tail. Step `VTUNE` with the DC source
across 0–3.3 V (step size: TODO). Wait ≥ 200 ns per point. Read the ÷2 frequency and power on the
spectrum analyzer. Repeat at nominal and at 2× ISS.

**Expected — extracted, landed layout** (`docs/verification.md` §3.2.1, measured on the
`f0f0281` extraction; VCO frequency, ÷2 is half):

| VTUNE | ISS 1.0× | ISS 2.0× |
|---|---|---|
| 0.0 V | 5.762 GHz, 1.969 Vpp core diff. | 5.728 GHz, 3.038 Vpp |
| 2.0 V | 4.372 GHz, 0.974 Vpp | 4.402 GHz, 2.207 Vpp |
| 3.3 V | **does not start** | 3.807 GHz, 1.026 Vpp |

- Startup threshold at VTUNE 2.0 V: starts at 0.85× ISS, dead at 0.70× (`docs/verification.md`
  §3.2.1).
- Startup to 90 % at 1.0× ISS: 83 ns (`signoff/sim/vco/README.md`).
- KVCO: negative (frequency falls as VTUNE rises); ≈ −1.1 GHz/V near the ISM point on the
  **schematic** (`docs/scope.md` §3). Extracted KVCO, as chord slopes between the three VTUNE
  points run on the landed extraction (`docs/verification.md` §3.2.1; arithmetic on that table,
  not a separate simulation):
  - ISS 1.0×, 0 → 2.0 V: (4.372 − 5.762) GHz / 2.0 V = **−0.695 GHz/V**
  - ISS 2.0×, 0 → 2.0 V: (4.402 − 5.728) GHz / 2.0 V = **−0.663 GHz/V**
  - ISS 2.0×, 2.0 → 3.3 V: (3.807 − 4.402) GHz / 1.3 V = **−0.458 GHz/V**

  A local KVCO at the operating point needs a finer extracted sweep (§8).
- Schematic reference band, for comparison only: 4.05–6.38 GHz (`docs/scope.md` §3). The
  extraction runs 6–11 % lower (`docs/verification.md` §3.2.1).

**Output power.** The pads are reached through the divider's output converters, so output power
is a DIV2 measurement (§5.2). No VCO-core output power is observable.

**Phase noise.** Measured at the ÷2 output. Expected value: **TODO**. No simulation exists
(`docs/verification.md` §3.2 GAP 2).

**Pass/fail limits:** TODO (frequency tolerance, minimum tuning range, startup threshold).

### 5.2 DIV2 — I/Q outputs, phase error

**Procedure.** With the VCO running (§5.1), read `I_N`, `Q_P` and `Q_N` into 50 Ω. Measure:
frequency (equal to f_VCO / 2), swing, duty cycle, and the I-to-Q phase difference on the scope.
`I_P` is not available, so the phase is taken between `I_N` and `Q_P` / `Q_N`. Wait ≥ 30 ns
after VCO power-up.

**Expected:**

| Metric | Extracted converter | Schematic, modelled passives | Source |
|---|---|---|---|
| f_out (bench at f_VCO = 5 GHz) | 2.500 GHz | 2.500 GHz | `signoff/pex/ib_conv_v1/resim.md` |
| Output swing per converter (1 kΩ R_SER into 50 Ω, `docs/phase8-padframe-plan.md`) | **29 mVpp** (one converter extracted, at `9614947`) | 131 mVpp | `signoff/pex/ib_conv_v1/resim.md` "Re-run 2026-09-17" |
| Duty cycle | 64.5 % (one converter extracted) | 49.5 % | same |
| I/Q phase, all four converters equal | 270.0° (all-four PEX, pre-`9614947` netlist) | 270.0° | `signoff/pex/ib_conv_v1/resim.md` "PEX result" |
| I/Q phase, one converter extracted | 289.6° | — | `signoff/pex/ib_conv_v1/resim.md` "Re-run 2026-09-17" |
| Static I-to-Q offset from layout | ~1.0° (Q input hauls ~53 µm longer) | — | `docs/layout-review-aug14.md` |
| Divider + converters supply current | 22.791 mA (one converter extracted) | 22.118 mA | `signoff/pex/ib_conv_v1/resim.md` |

- 270.0° is the bench's reading of the quadrature relationship (90° target, `docs/scope.md` §7).
  How the bench sign convention maps onto the pads is TODO.
- The ideal-passive schematic numbers (142 mVpp, ~157 mVpp / −12 dBm) are superseded for
  comparison purposes by the modelled-passive 131 mVpp (`team_src/sim/div2/README.md`).
- The all-four-extracted case has not been re-run on the `9614947` converter netlist.
- The DIV2 core is schematic in every one of these runs; only the converters are extracted
  (`signoff/pex/ib_conv_v1/resim.md`).

**Pass/fail limits:** TODO (minimum swing, duty-cycle window, I/Q phase error limit).

### 5.3 PFD + CP — UP/DOWN response, pump current

**Observability.** `UP` and `DOWN` are internal, and `PFD.FB` is wired to the divider's `I_P`
(f_VCO / 2). The only observable is `CP_OUT`. The simulated three-region PFD response used
`REF`/`FB` at 1 MHz with direct `UP`/`DOWN` probes, which the die cannot reproduce.

**Procedure:** TODO. The repo contains no simulated or documented procedure for driving the PFD
open-loop on this die, given `FB` is the ~2 GHz divider output. One untested option would be to
hold one PFD input static (VCO stopped, or `REF_IN` held low by its pull-down) so that one pump
direction stays on, then force `CP_OUT` with a voltage source and measure its current. No
simulation supports this, so it is not a plan yet.

**Expected (block-level, not reproducible as-is at the pads):**

| Metric | Value | Source |
|---|---|---|
| Pump current I_CP | 50 µA (10.19 µA average at φ = +200 ns, 1 MHz) | `docs/verification.md` §2.1 |
| Detector gain | ≈ 50 nA/ns at 1 MHz | `docs/verification.md` §2.1 |
| UP/DOWN current mismatch, extracted CP, 0.4–2.8 V | −2.283 % to +2.321 %; +0.007 % at 1.50 V | `signoff/pex/README.md` |
| Added mismatch from the real IBIAS generator | +0.18 % TT (FF 0.004 %, SS 0.94 %), schematic-level | `docs/verification.md` §2.6 S5/S6 |
| CP_OUT compliance | 0.32–3.00 V | `docs/verification.md` §2.6 S4 |
| Charge injection | +110 fC/cycle (≈ 105 fC measured at φ = 0) | `docs/verification.md` §2.1 |
| PFD reset pulse | 0.50 ns typ, 0.39 ns ff (internal, not observable) | `docs/layout-review-sep01.md` §4.6.1 |
| Loop sign | REF-lead → UP → CP sources → CP_OUT rises | `docs/verification.md` §2.1 |

**Pass/fail limits:** TODO.

### 5.4 IBIAS

**Observability.** The generator's outputs are internal. The observables are the `IBIAS` pin
voltage at the forced current, and the downstream effects: the CP current at `CP_OUT` (§5.3) and
the divider's supply current (§5.2).

**Procedure.** Force 240 µA into `IBIAS` and record the pin voltage. Sweep 120–360 µA (the
simulated input range) and record the change in supply current. The procedure to separate the
IBIAS share of the supply current from the other blocks on the same rail is TODO.

**Expected** (`docs/verification.md` §2.6, schematic TT; the generator has no extracted sim,
`docs/layout-review-sep01.md` §5):

| Metric | Value |
|---|---|
| VGP / VGN branch currents | 50.00 µA / 49.91 µA |
| IB_DIV2 | 239.56 µA |
| Generator total supply current | 839 µA |
| Gain, VGP | 5/24, linearity < 0.01 % over 120–360 µA |
| PSRR, VDD 3.0–3.6 V | VGP 0.003 %/V; VGN and IB_DIV2 1.16 %/V |
| `IBIAS` pin voltage at 240 µA | TODO; needs a run (§8) |

**Pass/fail limits:** TODO.

## 6. Results publishing

Matching `README.md` ("Testing commitment"): **Team A01 is committed to testing the fabricated
chip and publishing the measurement results in this repository.** Location and format inside the
repo: TODO.

## 7. Known simulation gaps that limit these targets

From `docs/layout-review-sep01.md` §6 and the files cited above:

- No phase-noise simulation.
- No Monte Carlo. All mismatch figures are systematic corner tracking only.
- No full-chip PEX. VCO, CP and the DIV2 converters are extracted individually; PFD has
  capacitance-only PEX; IBIAS and the DIV2 core have none.
- The VCO was not re-simulated against the extracted chip-level output load.
- No ESD simulation.

## 8. Values that need a new simulation run

None of these has been run. The runtimes are estimates. The only recorded extracted-VCO runtime
is 21 s for 40 ns on the pre-landing netlist (`signoff/sim/vco/README.md`); no 200 ns runtime
is recorded.

| Value | Run needed | Estimated runtime |
|---|---|---|
| `IBIAS` pin voltage at 240 µA | `team_src/sim/ibias/ibias_op.spice` with `v(IBIAS)` printed (schematic; the generator has no PEX) | seconds |
| `IBIAS` compliance | DC sweep of `I_BIAS` over 120–360 µA, recording `v(IBIAS)` (the README's S4 sweep) | seconds |
| `ISS` node voltage, landed extraction | `signoff/sim/vco/pex200.spice` with the ISS node added to `wrdata`, at ISS 1.0×/2.0× and VTUNE 0/2.0/3.3 V (6 runs of 200 ns) | ~2 min per run, ~10–15 min total |
| `ISS` minimum compliance for oscillation | Same deck with the ISS node held by a swept voltage source (≈ 6–8 points) | ~2 min per point, ~15 min |
| Local extracted KVCO | `pex200.spice` swept over VTUNE 0–3.3 V in 0.25 V steps at ISS 1.0× and 2.0× (≈ 28 runs) | ~1 h |
| `VDDA` current | `vco_v1` supply current without the bench's output buffer (extracted, 200 ns), plus CP and IBIAS operating points. The VCO bench's `i(v1)` includes its buffer, so it cannot be used directly | ~2–5 min |
