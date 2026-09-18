# `signoff/pex/vco_v1/` — R+C parasitic extraction of `vco_v1` (the whole tank)

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Generated 2026-09-18 from `team_src/magic/vco_v1.mag` at commit `6dfb71f`, the first
extraction of the VCO **after** the tank short was fixed (`6573181`).

`vco_v1` is the whole LC tank: `vco_core` (the cross-coupled pair), `vco_varactors`
(42 `cap_nmos_03v3_b` units), `vco_tune_r`, the 1.2 nH spiral, and the two output leads that
`6573181` rebuilt. Fourth block to get an extracted netlist, after `CP_v1` (`../README.md`),
`ib_conv_v1` (`../ib_conv_v1/README.md`) and `vco_core` (`../vco_core/README.md`).

## Files

| File | What it is |
|---|---|
| `vco_v1.pex.spice` | **R+C extracted netlist** — **75 devices, 557 parasitic caps, 683 parasitic resistors**, 1318 lines. Magic `ext2spice`, `cthresh 0 rthresh 0`, `scale off`, `hierarchy off`. |

## Invocation, and the one difference from the other three recipes

Recipe: `team_src/magic/pex_vco_v1.tcl` (committed). Regenerate in-container:

```
magic -dnull -noconsole -rcfile $PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc pex_vco_v1.tcl
```

Same body as `pex_vco_core.tcl` — `extract do resistance` plus the `ext2sim`/`extresist` pair,
`cthresh 0`, `rthresh 0`, `scale off`, `hierarchy off`, `extresist on` — with **one deliberate
difference: the source is the `.mag` hierarchy, not `gds/vco_v1.gds`.**

Reading the GDS would traverse the spiral and short the two terminals together, because a
coil *is* a DC short between its ends. Loading the hierarchy keeps `vco_inductor_v2` as the
LEFview abstract, so the **committed `vco_inductor_v2.ext`** supplies the coil model instead —
two `tm11k` resistors either side of the metal4 bridge node, 7.46 fF per port. `hierarchy off`
then inlines that model, and it appears in the netlist as

```
X43 OUT_n vco_inductor_v2_0/m4_n14800_800# tm11k r_width=8u r_length=76u
X44 vco_inductor_v2_0/m4_n14800_800# OUT_p tm11k r_width=8u r_length=76u
```

`vco_inductor_v2.ext` is read-only in this flow; its md5 is unchanged across the run.

## Counts

| | value |
|---|---|
| extraction runtime | **2 s** (measured 2026-09-18, `timeout 600` wall clock, in-container) |
| hierarchical re-emit | 1 s |
| devices | **75** |
| parasitic caps | 557 |
| parasitic resistors | 683 |

**The device count equals the chip-level extraction's.** `run_full_lvs` on `gds/chip_top.gds`
reports `vco_v1` with 75 devices on both sides. The **42 varactors extract correctly here**
(2 × 21 `cap_nmos_03v3_b`), which a GDS-only read does not manage — see
`docs/verification.md` §3.2.

## Lead resistance, extracted vs geometric

Effective resistance by a Laplacian solve on the 683-resistor network, from the nearest
`vco_core` metal sub-node to the inductor terminal:

| | PEX | geometric | Δ |
|---|--:|--:|--:|
| OUT_p | **0.845 Ω** | 2.333 Ω | −1.488 |
| OUT_n | **0.523 Ω** | 1.733 Ω | −1.210 |
| imbalance | **0.321 Ω** | 0.600 Ω | −0.279 |

The extraction **corroborates the geometric estimate's ordering** — OUT_p is the longer path
and reads higher on both methods — and confirms the `6573181` design targets (≤ 2.5 Ω per side,
ΔR ≤ 1.5 Ω) with more margin than the hand figure suggested. It reads lower because the
geometric number is a 1-D series sum over the drawn length at the drawn width, while the
extractor resolves 2-D current spreading in the 2.4 µm leads and the 2.0 µm buses and treats
each 4×4 via array as a distributed mesh rather than a lumped 4.5/16 Ω.

**The two numbers do not span exactly the same path.** Magic merges the core pin, varactor pin,
inductor pin and top port onto one node name, so there is no labelled pin boundary in either
the flat or the hierarchical emission. The PEX figure is measured to the *nearest* core metal
sub-node, which sits a little inside the boundary. Treat the PEX value as a lower bound and the
geometric value as an upper bound; they bracket the true lead.

One benign extractor warning: `cap(2): no such node vco_inductor_v2_0/w_n8800_n4800#` — a well
node referenced by the abstract's cap records with no counterpart in the flattened view. It
drops one coupling cap and affects nothing else.

## What this does NOT establish

**No simulation has been run against this netlist.** See `../../sim/vco/README.md` for the
bench work and why the transient runs are still open.
