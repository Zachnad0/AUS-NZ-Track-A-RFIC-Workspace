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
| `VDDA` | 3.3 V | `docs/scope.md` section 4.1 (single 3.3 V rail); all sims TT / 3.3 V / 27 °C (`docs/verification.md` sections 2.6, 3.1) |
| `VDDD` | 3.3 V | `docs/scope.md` §4.1 |
| `VDDA`/`VDDD` current limit | **VDDA 6 mA, VDDD 50 mA** (team decision 11/2) | — |
| Expected supply current, chip | ≈ 25 mA core-only, against a ~50 mA budget | `docs/layout-review-sep01.md` §4 "Power budget" |
| Expected supply current, `VDDD` | 22.9 mA = DIV2 22.4 mA (simulated, `i(v_vdd)` of `div2_sb_TT`) + PFD ≈ 0.5 mA (inferred, not simulated). Later DIV2 runs: 22.118 mA with modelled passives, 22.791 mA with one converter extracted | `docs/layout-review-sep01.md` "Phase C — the chip-level VDDD path"; `docs/phase7-routing-plan.md`; `signoff/pex/ib_conv_v1/resim.md` |
| Expected supply current, `VDDA` | **1.90 mA at ISS 1.0×, 2.93 mA at ISS 2.0×** (TT, 3.3 V, VTUNE 2.0 V, CP idle or sinking). Simulated, and covers all three blocks on `VDDA` (`team_src/magic/chip_top_golden.spice`): VCO 1.300 / 2.332 mA (extracted `vco_v1`, bench buffer on its own supply) + CP 0.050 mA + IBIAS generator 0.549 mA. CP sourcing (UP on) adds 0.050 mA. CP + IBIAS over corners: 0.595 (SS) to 0.600 (FF) mA idle; the VCO was run at TT only. Not included: the 240 µA `IBIAS` reference (add it if the source is powered from `VDDA`) and ESD-diode leakage. The VCO's share leaves the die through the `ISS` pin, not `VSSA`. Replaces the 3.5 mA estimate in `docs/phase7-routing-plan.md` | `signoff/sim/vdda/` (`run_vdda.sh`), run 2026-11-02 |
| `IBIAS` reference current | 240 µA, forced current | `docs/verification.md` §2.6; `docs/pins.md` section 1 |
| `IBIAS` current direction | Sourced **into** the pin from the supply (`I_BIAS VDD IBIAS 240u`); the pin lands on a diode-connected nfet | `team_src/sim/ibias/ibias_op.spice`; `docs/esd-which-pins.md` |
| `IBIAS` pin voltage at 240 µA | **2.066 V TT**, 1.787 V FF, 2.349 V SS; the same at VDD 3.0, 3.3 and 3.6 V (schematic, 27 °C; the generator has no PEX) | `team_src/sim/ibias/ibias_pin.spice.in`, run 2026-11-02 |
| `IBIAS` pin voltage over 120–360 µA | TT 1.892–2.196 V; FF 1.619–1.911 V; SS 2.167–2.484 V | same |
| Required compliance of the external `IBIAS` source | Must hold the pin at ≥ 2.35 V at 240 µA (SS) and ≥ 2.48 V at 360 µA (SS). A source tied to the 3.3 V rail therefore has ≈ 0.95 V of headroom at SS, 240 µA | derived from the two rows above |
| `ISS` tail current, nominal (sim "1.0×") | 1.35 mA tail, from a 1 mA reference into a 1:1 NMOS mirror on the bench | `docs/verification.md` §3.2, §3.2.1 |
| `ISS` tail current, bring-up (sim "2.0×") | ≈ 2.3–2.38 mA tail (reference 1 mA → 2 mA); needed for the top of the tuning range to start | `docs/verification.md` §3.2.1 |
| `ISS` off-chip circuit | **SMU in current-sink mode**, set to the 1.0× / 2.0× currents: 1.30 / 2.34 mA (the VTUNE 2.0 V values in §5.1; 1.27–1.39 / 2.24–2.38 mA across VTUNE), compliance down to 0.8 V (team decision 11/2) | `signoff/sim/iss/` |
| `ISS` node voltage / required sink compliance | v(ISS) 1.0–1.42 V across all simulated points (minimum observed 1.009 V). **The sink must regulate down to 0.8 V** (team decision 11/2). Full table in §5.1. (The 0.698–0.475 V figures in `docs/verification.md` §3.2 come from the pre-landing extraction and do not apply.) | `signoff/sim/iss/`, run 2026-11-02 |
| `VTUNE` range | 0–3.3 V (simulated sweep range) | `docs/verification.md` §3.1, §3.2.1 |
| `VTUNE` step | **0.1 V** (34 points over 0–3.3 V) (team decision 11/2) | — |
| `REF_IN` amplitude / levels | **0 V / 3.3 V** square wave, 100 ps edges in simulation, as the PFD sims used (team decision 11/2) | `team_src/xschem/PFD_tb.sch`, `PFD_CP_tb.sch` (`PULSE(0 3.3 … 100p 100p 500n 1u)`); `docs/verification.md` §2 |
| `REF_IN` frequency | **1 MHz, 50 % duty** (500 ns high, 1 µs period), as the PFD sims used (team decision 11/2). The library-cell PFD was also re-simulated at 2 MHz | same; `docs/verification.md` §2, §2.1, §2.2 |
| Power-up sequencing | **(1) grounds (`VSSA`, `VSSD`); (2) `VDDA` and `VDDD`, current-limited per above; (3) `IBIAS`; (4) `ISS`; (5) `VTUNE`; (6) `REF_IN`** (team decision 11/2). Power down in reverse | — |
| Settling before reading outputs | ≥ 30 ns for the divider; ≥ 200 ns (startup 83 ns) for the VCO | `docs/verification.md` §3.2.1; `docs/scope.md` section 7 |

## 4. Required equipment

Listed generically here. **The make, model and settings actually used are recorded per test in
`results/`** (team decision 11/2; see §6).

- Spectrum analyzer, **≥ 7 GHz, span 1–7 GHz** (team decision 11/2).
- Signal generator for `REF_IN`.
- DC power supplies for `VDDA` and `VDDD`, with current readback.
- Precision DC voltage source for `VTUNE`.
- SMUs: `IBIAS` (current source, ≥ 2.5 V compliance, §5.4); `ISS` (current sink, down to 0.8 V,
  §3); `CP_OUT` (voltage-force, current-measure, §5.3).
- Oscilloscope, **2 channels, ≥ 6 GHz bandwidth, with matched and deskewed cables** (team
  decision 11/2), for I/Q phase and duty cycle.
- 50 Ω cabling and terminations for `I_N`, `Q_P`, `Q_N`; the outputs are designed into a 50 Ω
  instrument (`docs/scope.md` §4).
- Test PCB / socket: TBD pending organizer packaging decision.

## 5. Per-block tests

Each "expected" value is a simulation or PEX result. Pass/fail limits are the team decisions of
11/2, marked as such; where none was made, the limit is `TODO`. Where a schematic number and a
layout-extracted number both exist, the extracted one is listed first, because it describes the
shipped layout.

**Supply currents (all blocks)** (team decision 11/2): pass if each measured supply current is
within **±30 % of simulation**:
- `VDDD`: 22.9 mA, so the window is 16.0–29.8 mA.
- `VDDA` at VTUNE 2.0 V: 1.90 mA at ISS 1.0× (window 1.33–2.47 mA) and 2.93 mA at ISS 2.0×
  (window 2.05–3.81 mA).

The simulated values are in §3. Measure `VDDA` with the `IBIAS` reference supplied separately,
as simulated.

### 5.1 VCO — frequency vs VTUNE, output power, phase noise

The VCO has no pad of its own. It is observed at `I_N` / `Q_P` / `Q_N`, at **f_VCO / 2**.

**Procedure.** Power up in the §3 order. Set the ISS tail. Step `VTUNE` with the DC source
across 0–3.3 V in **0.1 V steps** (team decision 11/2). Wait ≥ 200 ns per point. Read the ÷2 frequency and power on the
spectrum analyzer. Repeat at nominal and at 2× ISS.

**Expected — extracted, landed layout** (`docs/verification.md` §3.2.1, measured on the
`f0f0281` extraction; VCO frequency, ÷2 is half):

| VTUNE | ISS 1.0× | ISS 2.0× |
|---|---|---|
| 0.0 V | 5.762 GHz, 1.969 Vpp core diff. | 5.728 GHz, 3.038 Vpp |
| 2.0 V | 4.372 GHz, 0.974 Vpp | 4.402 GHz, 2.207 Vpp |
| 3.3 V | **does not start** | 3.807 GHz, 1.026 Vpp |

- Startup threshold at VTUNE 2.0 V: starts at 0.85× ISS, dead at 0.70×
  (`docs/verification.md` §3.2.1).
- Startup to 90 % at 1.0× ISS: 83 ns (`signoff/sim/vco/README.md`).
- KVCO: negative (frequency falls as VTUNE rises); ≈ −1.1 GHz/V near the ISM point on the
  **schematic** (`docs/scope.md` §3). Extracted KVCO, as chord slopes between the three VTUNE
  points run on the landed extraction (`docs/verification.md` §3.2.1; arithmetic on that table,
  not a separate simulation):
  - ISS 1.0×, 0 → 2.0 V: (4.372 − 5.762) GHz / 2.0 V = **−0.695 GHz/V**
  - ISS 2.0×, 0 → 2.0 V: (4.402 − 5.728) GHz / 2.0 V = **−0.663 GHz/V**
  - ISS 2.0×, 2.0 → 3.3 V: (3.807 − 4.402) GHz / 1.3 V = **−0.458 GHz/V**

  These chord slopes are the KVCO reference for this plan; no finer extracted sweep will be run
  (team decision 11/2).
- Schematic reference band, for comparison only: 4.05–6.38 GHz (`docs/scope.md` §3). The
  extraction runs 6–11 % lower (`docs/verification.md` §3.2.1).

**ISS sink requirement.** `ISS` is the tail node of the cross-coupled pair. The tail current
flows *out* of the pin into an off-chip sink, which pulls it toward ground. Simulated on the landed
extraction (`signoff/sim/iss/`, `run_iss.sh`, run 2026-11-02, TT, 200 ns, measured 150–200 ns):

*With the bench's 1:1 NMOS tail mirror* (`run_iss.sh node`). The six runs reproduce the band
table above to within 0.003 GHz, including no start at 1.0× / 3.3 V.

| Reference | VTUNE | Sink current | v(ISS) avg | v(ISS) min | Oscillates |
|---|---|---|---|---|---|
| 1 mA (1.0×) | 0.0 V | 1.391 mA | 1.389 V | 1.361 V | yes, 1.968 Vpp |
| 1 mA (1.0×) | 2.0 V | 1.302 mA | 1.237 V | 1.225 V | yes, 0.974 Vpp |
| 1 mA (1.0×) | 3.3 V | 1.274 mA | 1.188 V | 1.187 V | **no** |
| 2 mA (2.0×) | 0.0 V | 2.379 mA | 1.185 V | 1.157 V | yes, 3.037 Vpp |
| 2 mA (2.0×) | 2.0 V | 2.337 mA | 1.137 V | 1.100 V | yes, 2.206 Vpp |
| 2 mA (2.0×) | 3.3 V | 2.235 mA | 1.018 V | **1.009 V** | yes, 1.025 Vpp |

*With an ideal current sink, VTUNE 2.0 V* (`run_iss.sh sweep`). There is no compliance limit,
so v(ISS) is the voltage the die itself sets:

| Sink current | v(ISS) avg | v(ISS) min | Core diff. swing |
|---|---|---|---|
| 1.00 mA | 1.257 V | 1.257 V | 0.065 Vpp, not a sustained oscillation at 200 ns |
| 1.15 mA | 1.248 V | 1.230 V | 0.685 Vpp |
| 1.30 mA | 1.230 V | 1.200 V | 0.898 Vpp |
| 1.60 mA | 1.191 V | 1.143 V | 1.221 Vpp |
| 2.00 mA | 1.148 V | 1.074 V | 1.636 Vpp |
| 2.35 mA | 1.108 V | 1.016 V | 1.974 Vpp |

What this means for the off-chip sink:
- **Current.** 1.0× is about 1.27–1.39 mA (1.30 mA at VTUNE 2.0 V); it does not start at the top
  of the tuning range. 2.0× is about 2.24–2.38 mA (2.34 mA at VTUNE 2.0 V) and covers the whole
  band. At VTUNE 2.0 V an ideal sink needs about 1.15 mA to oscillate; 1.00 mA does not
  sustain one within 200 ns.
- **Compliance.** The ISS node never went below **1.009 V** in any oscillating case (2.0×,
  VTUNE 3.3 V), and sits at 1.0–1.42 V across all runs. **The sink must regulate down to
  0.8 V** (team decision 11/2), about 0.2 V below the lowest simulated point.
- **Settable range.** v(ISS) falls as current rises, by ~0.15 V from 1.0 to 2.35 mA, so a sink
  that regulates down to 0.8 V covers every point simulated. Corners and temperature were not run.
- An ideal sink gives somewhat less swing than the mirror at the same current (0.898 Vpp at
  1.30 mA vs 0.974 Vpp at 1.302 mA). This is likely the mirror's finite output impedance
  letting the tail current move with the oscillation; it is not investigated further here.

**Output power.** The pads are reached through the divider's output converters, so output power
is a DIV2 measurement (§5.2). No VCO-core output power is observable.

**Phase noise.** Measured at the ÷2 output and **reported only** (team decision 11/2). No
simulation exists (`docs/verification.md` §3.2 GAP 2).

**Pass/fail limits** (team decision 11/2):
- **Oscillates at ISS 2.0× at every VTUNE step from 0 to 3.3 V**, seen as a tone at the ÷2
  outputs.
- **Band within ±10 % of the extracted 3.806–5.760 GHz.** VTUNE 3.3 V must land in
  3.425–4.187 GHz (1.713–2.093 GHz at ÷2), and VTUNE 0 V in 5.184–6.336 GHz (2.592–3.168 GHz at
  ÷2). The endpoints come from `signoff/sim/iss/`, run 2026-11-02: 3.806 GHz at 2.0× / 3.3 V and
  5.760 GHz at 1.0× / 0 V. The 2.0× / 0 V point simulated at 5.725 GHz, also inside the window.
- **Frequency monotonic decreasing in VTUNE** across the 0.1 V steps.
- **Output power and phase noise: report only.**

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

- **How the simulated 270.0° maps onto the pads.**
  - *What the bench measures.* `team_src/sim/div2/analyze.awk` takes the time from a rising
    mid-swing crossing of the I_P chain's driver output (`INVO3_IP`) to the next rising crossing
    of the Q_P chain's (`INVO3_QP`), as a fraction of the period × 360. So **270.0° means Q_P
    rises 270° after I_P, i.e. Q_P leads I_P by 90°.**
  - *Which phase each pad carries.* In `team_src/magic/chip_top_golden.spice` (the
    `DIV2_QUAD_v1` subckt, lines 103–179), each output chain is a diff pair on one divider phase
    pair. I_P's pair is driven OIB/OI and I_N's OI/OIB; Q_P's is OQB/OQ and Q_N's OQ/OQB. Each
    chain reaches its pad through `XR_SER_*`. So I_N = I_P + 180° and Q_N = Q_P + 180°. The
    same mapping is in the sim deck (`signoff/pex/ib_conv_v1/resim.md`, "Decks and invocation").
  - *Pads.* The pads are `I_N`, `Q_P` and `Q_N` (`info.yaml` `pins:`; slots N03, N04, N02 in
    `docs/pins.md` §1); `I_P` is internal (it drives `PFD.FB`).
  - *Expected on the scope, taking `I_N` as the reference and measuring rising-edge delay as a
    fraction of the period:* **`Q_P` at +90°** (Q_P = I_P + 270° = I_N + 90°) and **`Q_N` at
    +270°, i.e. −90°** (Q_N = I_P + 90° = I_N − 90°). The §5.2 pass limit 90° ± 10° applies to
    the `I_N` → `Q_P` delay.
  - The simulated phase is taken at the driver outputs, before the 1 kΩ `XR_SER_*` and the pad
    route. Route-length mismatch adds the ~1.0° static offset in the table above; the scope
    cables must be matched/deskewed (§4).
- The ideal-passive schematic numbers (142 mVpp, ~157 mVpp / −12 dBm) are superseded for
  comparison purposes by the modelled-passive 131 mVpp (`team_src/sim/div2/README.md`).
- The all-four-extracted case has not been re-run on the `9614947` converter netlist.
- The DIV2 core is schematic in every one of these runs; only the converters are extracted
  (`signoff/pex/ib_conv_v1/resim.md`).

**Pass/fail limits** (team decision 11/2):
- **A tone at f_VCO / 2 on both the I output (`I_N`) and a Q output (`Q_P` / `Q_N`).**
- **Quadrature phase 90° ± 10°.**
- Swing and duty cycle: report only.

Note against the simulations above: the all-four-extracted and schematic cases sit at exactly
quadrature (270.0°, i.e. 90°). The one-converter-extracted case (289.6°) is 19.6° off, which would
fail. That case models only one converter extracted, which a fabricated die cannot have, so it is
a sensitivity indicator rather than an expected result.

### 5.3 PFD + CP — UP/DOWN response, pump current

**Observability.** `UP` and `DOWN` are internal, and `PFD.FB` is wired to the divider's `I_P`
(f_VCO / 2). The only observable is `CP_OUT`. The simulated three-region PFD response used
`REF`/`FB` at 1 MHz with direct `UP`/`DOWN` probes, which the die cannot reproduce.

**Scope: a `CP_OUT`-only partial test** (team decision 11/2). The PFD's three-region response
and the UP/DOWN pulses are not tested; only what `CP_OUT` shows is.

**Procedure.** Hold `CP_OUT` with an SMU (voltage-force, current-measure) at **0.32, 1.65 and
3.00 V**, the ends and middle of the simulated compliance window. Drive `REF_IN` per §3
(0/3.3 V, 1 MHz), and also hold it low (its weak pull-down does this when undriven). With the VCO
running and with it stopped (ISS sink off), record the `CP_OUT` current in each combination.

**Expected `CP_OUT` current** (`signoff/sim/cp_out/cp_out_op.spice`, run 2026-11-02: extracted
`CP_v1` biased by `ibias_gen_v1` at 240 µA, TT, 3.3 V, DC operating point). Positive means the CP
sources current out of `CP_OUT`; negative means it sinks.

| `CP_OUT` | UP/DN idle | UP only (context) | DOWN only (context) |
|---|---|---|---|
| 0.32 V | +29.8 pA | +50.34 µA | −48.08 µA |
| 1.65 V | +12.2 pA | +50.21 µA | −50.24 µA |
| 3.00 V | −5.6 pA | +48.12 µA | −50.54 µA |

**Single-edge check** (`signoff/sim/cp_out/pfd_cp_edge.spice`, run 2026-11-02: `PFD_lib` from
the layout golden with the gf180 7-track standard cells, extracted `CP_v1`, `ibias_gen_v1` at
240 µA, `CP_OUT` held at 1.65 V, `FB` held low, one `REF_IN` rising edge 0 → 3.3 V at 50 ns,
TT):

| | UP | DOWN | `CP_OUT` current |
|---|---|---|---|
| before the edge (20–45 ns) | 0 V | 0 V | +12.2 pA (idle) |
| after the edge (150–200 ns) | 3.3 V | 0 V | **+50.21 µA (UP)** |

With `FB` static, the reference flip-flop sets and nothing resets it, so the pump stays on UP. In
this simulation the t = 0 operating point happened to start idle. On silicon the starting state
is **undetermined: the PFD has no external reset**, so any of idle, UP or DOWN may come up at
power-on. Holding `FB` low models the VCO stopped (ISS sink off). The level `I_P` actually rests
at with the VCO stopped was not simulated.

**Pass/fail — three-band check** (team decision 11/2; replaces the ±30 % idle limit):

| Band | `CP_OUT` current |
|---|---|
| idle | \|I\| < 1 µA |
| UP | +35 … +65 µA |
| DOWN | −35 … −65 µA |

- **Every reading must land in one of the three bands.**
- **With the VCO stopped, one `REF_IN` rising edge must give UP**, matching the single-edge
  check above.
- The band a reading starts in after power-up is not itself a pass/fail criterion, because the
  power-up state is undetermined.
- **PFD state with the VCO running: report only** (team decision 11/2). With `FB` at the
  ~2 GHz divider output the PFD is far outside its simulated range, so which band `CP_OUT`
  settles in is recorded, not judged. The three-band check above still applies to the reading
  itself.

The DC values in the table above sit in these bands: idle at picoamps; UP +48.1 to +50.3 µA;
DOWN −48.1 to −50.5 µA. The block-level values below are context.

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

**Pass/fail limits:** the three-band check above (team decision 11/2).

### 5.4 IBIAS

**Observability.** The generator's outputs are internal. The observables are the `IBIAS` pin
voltage at the forced current, and the downstream effects: the CP current at `CP_OUT` (§5.3) and
the divider's supply current (§5.2).

**Source.** Drive `IBIAS` from an SMU in current-source mode, or from another current source
whose compliance is **≥ 2.5 V**. The simulated pin voltage reaches 2.349 V at 240 µA and 2.484 V
at 360 µA in the SS corner (`team_src/sim/ibias/ibias_pin.spice.in`); a source with less
headroom will not deliver the programmed current. Set the SMU's voltage limit above 2.5 V but not
above `VDDA`: the pin has an ESD diode to `VDDA` (`D_ESD_IBIAS_P` in
`team_src/magic/chip_top_golden.spice`).

**Procedure.** Force 240 µA into `IBIAS` and record the pin voltage. Sweep 120–360 µA (the
simulated input range) and record the change in supply current. **The IBIAS share of a rail's
current is that rail's current at `IBIAS` = 240 µA minus its current at `IBIAS` = 0** (team
decision 11/2), with everything else unchanged. The simulated generator draw on `VDDA` is
0.549 mA (§3).

**Expected** (`docs/verification.md` §2.6, schematic TT; the generator has no extracted sim,
`docs/layout-review-sep01.md` §5):

| Metric | Value |
|---|---|
| VGP / VGN branch currents | 50.00 µA / 49.91 µA |
| IB_DIV2 | 239.56 µA |
| Generator total supply current | 839 µA |
| Gain, VGP | 5/24, linearity < 0.01 % over 120–360 µA |
| PSRR, VDD 3.0–3.6 V | VGP 0.003 %/V; VGN and IB_DIV2 1.16 %/V |
| `IBIAS` pin voltage at 240 µA | 2.066 V TT (1.787 FF, 2.349 SS), independent of VDD; `team_src/sim/ibias/ibias_pin.spice.in` |
| VGN branch at SS, VDD 3.0 V | 48.30 µA at 240 µA and 59.72 µA at 360 µA (VGP stays 50.00 / 75.00), so the PMOS-mirror path runs out of headroom at low supply in the slow corner; same deck |

**Pass/fail limits** (team decision 11/2): **`IBIAS` pin voltage 1.6–2.5 V at 240 µA.** The
simulated FF–SS spread is 1.787–2.349 V.

## 6. Results publishing

Matching the commitment in `README.md` ("Testing commitment"): the fabricated chip will be tested
and the measurement results published in this repository. Team A01 currently has a single active
member, who carries out the testing and publishing.

**Location and format** (team decision 11/2): a top-level **`results/`** directory. Each test
gets a **Markdown summary** and the **raw data as CSV**. Each summary records the **date** and the
**equipment used** (make, model, settings).

## 7. Known simulation gaps that limit these targets

From `docs/layout-review-sep01.md` §6 and the files cited above:

- No phase-noise simulation.
- No Monte Carlo. All mismatch figures are systematic corner tracking only.
- No full-chip PEX. VCO, CP and the DIV2 converters are extracted individually; PFD has
  capacitance-only PEX; IBIAS and the DIV2 core have none.
- The VCO was not re-simulated against the extracted chip-level output load.
- No ESD simulation.

## 8. Values that need a new simulation run

None. The local-KVCO sweep that was listed here was dropped: the §5.1 chord slopes stand (team
decision 11/2). For reference, a 200 ns run on the landed extraction takes 52–147 s with 2
threads (measured 2026-11-02).

Done on 2026-11-02:
- IBIAS pin voltage and compliance: §3 and §5.4. 9 runs, under 1 s each; the TT / 3.3 V control
  reproduces the recorded 50.00 / 49.91 / 239.56 µA.
- `VDDA` current: §3. Its VCO runs reproduce the recorded 0.974 Vpp / 4.372 GHz and
  2.207 Vpp / 4.402 GHz.
- `ISS` node voltage and sink compliance: §5.1. 12 runs, ~21 min total. The compliance sweep used
  an ideal current sink stepped over 1.0–2.35 mA rather than a swept voltage source: a voltage
  source on `ISS` sets the tail current itself and so does not measure a sink's compliance.
- `CP_OUT` DC currents: §5.3. One ngspice job, 0.3 s.
- PFD + CP single `REF_IN` edge: §5.3. One ngspice job, 11 s.
