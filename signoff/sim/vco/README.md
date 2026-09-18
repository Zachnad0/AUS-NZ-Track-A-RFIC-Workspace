# `signoff/sim/vco/` — VCO startup, golden control vs extracted

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Run 2026-09-18 at commit `77b62bb`, the tank-level check `docs/verification.md` §3.2 has needed
since the tank short was fixed in `6573181`.

**Result: the control oscillates and is settled; the extracted netlist does not start.**

## Files

| File | What it is |
|---|---|
| `vco_tb.spice` | the bench, netlisted headlessly from `team_src/xschem/vco_tb.sch` |
| `mkdeck2.py` | builds the run decks — stimulus and options from the bench, DUT swapped for the golden or the extracted netlist |
| `analyze.py` | f0, swing, startup, supply current and amplitude drift from the `wrdata` dump |
| `ctrl40.spice` | the control deck as run |
| `pex40.spice` | the extracted deck as run |
| `mkdeck.py` | the earlier 80 ns deck builder, kept for the runtime record below |

## The deck, and how it differs from the `docs/verification.md` §3.2 bench

Stimulus, buffer, load and options are the bench's: `.option reltol=1e-5`, `method=gear`,
`bypass=0`, `numparam jobs=4`, and the four PDK includes. `ngspice-46`, `set num_threads=2`.
Deltas, all deliberate:

| | `docs/verification.md` §3.2 bench | this deck | why |
|---|---|---|---|
| DUT | the xschem `vco_v1` | **`team_src/magic/vco_v1_golden.spice`** | the golden is the netlist the *layout* is LVS'd to. The bench schematic carries `ppolyf_u_3k r_length=5u` where the golden, `vco_tune_r` and the layout all carry `ppolyf_u_1k r_length=15u`; a control built on the bench schematic would not be measuring the circuit that was built. |
| transient | `tran 5p 80n`, settled 60–80 ns | **`tran 5p 40n uic`**, measured 30–40 ns | `uic` skips the operating point, which is what made the earlier attempt unaffordable — the same bench needed **36.5 s per 5 ns** with `op`, i.e. ~583 s for 80 ns. With `uic` the whole 40 ns control takes **8 s**. It also makes this a genuine cold start rather than a perturbation of a solved bias point. |
| kick | none (numerical noise, 40 ns of settling discarded) | **`.ic v(net1)=0.01 v(net2)=-0.01`** | a defined ±10 mV differential kick, so startup time means something |
| VTUNE | 2.15 V headline, swept | **2.0 V** | the band-centre point on the `docs/verification.md` §3.2 sweep, where the record reads 4.929 GHz / 4.09 Vpp |

**No solver option was added.** No `gmin`, no relaxed tolerances. `uic` removed the need.

## Runtimes

| run | wall clock |
|---|--:|
| control, golden, 40 ns | **8 s** |
| extracted, probe 5 ns | 1 s |
| extracted, 40 ns | **21 s** |
| *(for the record: the same bench with `op` instead of `uic`, 5 ns)* | *36.5 s* |

## Results

Measured over 30–40 ns on the core differential `v(net1) − v(net2)`.

| | record, `verification.md` §3.2 @ 2.0 V | control (golden) | extracted |
|---|--:|--:|--:|
| f0 | 4.929 GHz | **4.859 GHz** (−1.42 %) | — does not oscillate |
| core differential swing | 4.09 Vpp | **4.211 Vpp** (+3.0 %) | **0.000 Vpp** |
| startup to 90 % of final | not recorded | **6.211 ns** | not reached |
| supply current, mean `i(v1)` | not recorded | **5.177 mA** | 4.197 mA (bias only) |
| tail current, mean `i(viss)` | not recorded | 1.404 mA | 1.273 mA |
| amplitude drift, 30–35 vs 35–40 ns | — | **0.071 %** → settled | — |

The control **is settled** on the stated criterion (drift < 1 %), so 30–40 ns is a valid window.

The −1.42 % on f0 and +3.0 % on swing are against a record (`docs/verification.md` §3.2)
taken on a different deck: different
DUT (bench schematic vs golden, including the resistor delta above), different start (`op` plus
40 ns of settling vs a cold `uic` start), and a different window (60–80 ns vs 30–40 ns). The
control is not a reproduction of that run and should not be read as one; it is the same
circuit the layout implements, measured cleanly.

## The extracted netlist does not start

The envelope, peak-to-peak per 2 ns, on the core differential:

```
1ns:0.04  3ns:0.00  5ns:0.00  7ns:0.00 ... 39ns:0.00
```

The ±10 mV kick decays to nothing within ~3 ns and never recovers. The circuit is alive and
correctly biased — the tail draws 1.273 mA and the supply 4.197 mA, against the control's
1.404 / 5.177 mA — so this is a **damped** oscillator, not a broken deck.

### One deck correction was needed to get here, and it is part of the measurement

**Magic's extraction contains no inductance.** `grep -c "^L"` on both `vco_v1.pex.spice` and the
committed `vco_inductor_v2.ext` returns **0**: magic extracts R and C only, and the `.ext` models
the coil as two `tm11k` resistors plus caps. Run as extracted, the tank has no resonator at all
and sits flat — which is exactly what the first attempt showed, and it means nothing about the
layout. `mkdeck2.py` therefore removes the coil's 9 R/C-only elements and instantiates the
lumped model that does carry the 1.2 nH (`team_src/xschem/vco_inductor_v2.subckt`, `L0`/`L1` =
0.60 n) in their place. Everything else — every lead, bus, via array and all 42 varactors — stays
extracted. **The 0.000 Vpp above is from that corrected deck**, not the inductorless one.

### Series resistance in the tank loop

> **The table originally published here (≈ 3.8 Ω total) was wrong and is corrected below.**
> Two errors in the Laplacian solve: the output leads were taken as the *minimum* effective
> resistance over the branch's metal sub-nodes instead of to the device terminals, and the 21
> varactor units per side were combined as `1/Σ(1/R)`. The units **share the tap wire**, so
> they do not parallelise. The correct quantity is the effective resistance from the tank node
> to all of a branch's device terminals shorted into one supernode.

| tank branch | Ω |
|---|--:|
| lead, OUT_p → 30 `vco_core` drain terminals | 4.742 |
| lead, OUT_n → 30 `vco_core` drain terminals | 6.530 |
| varactor branch, OUT_p → 21 unit terminals | 3.550 |
| varactor branch, OUT_n → 21 unit terminals | 3.550 |
| coil (lumped model, two `tm11k`) | 0.760 |
| **total** | **19.131** |

against **0.76 Ω** for the golden, which has the coil and nothing else — about **25× the loss**.
At ωL ≈ 30–48 Ω over the band that puts tank Q below 2.5, and the cross-coupled pair's negative
resistance cannot cover that.

**The varactor taps are not the cause.** Only ≈ 1.46 Ω of the 19.131 is metal that
`phase5/vco_v1.tcl` draws — leads 0.845 + 0.523, and the two varactor taps **0.046 Ω each**.
About 11 Ω sits inside `vco_core` and 7 Ω inside `vco_varactors`. The 11.3–25.3 Ω per unit
quoted in the original text is `vco_varactors`' own internal M3 rail, reached through the tap,
not the tap itself; and there are **two** taps in `vco_v1.tcl`, not 42.

Confirmed by simulation rather than argument: scaling **all** top-level tank routing R by 0.01
still gives 0.000 Vpp, and widening the two taps 0.30 → 2.40 µm with 4×4 via arrays (built and
fully gated, not landed) changed the extracted loop by **0.000 Ω**. What does start it is a
broad reduction — scaling *every* parasitic resistor by ×0.3 does not oscillate, **×0.2 does**
(1.78 Vpp, 4.40 GHz) — so the shortfall is cumulative and needs ~3–5× less total parasitic R.

## What this does and does not establish

It establishes that the corrected layout's own parasitics are heavy enough that **the VCO does
not start in this bench at VTUNE 2.0 V**, and it gives the first measured runtimes for the
bench. It does **not** establish that the fabricated VCO will not oscillate: the extracted deck
is pessimistic in at least two known ways — magic's R+C extraction with `rthresh 0` keeps every
parasitic resistor with no reduction, and the lumped coil model carries only DC metal
resistance with no frequency-dependent treatment. A proper answer needs the 18 Ω inside
`vco_core` and `vco_varactors` either reduced or shown to be an extraction artifact; nothing
reachable from `vco_v1.tcl` moves it.
