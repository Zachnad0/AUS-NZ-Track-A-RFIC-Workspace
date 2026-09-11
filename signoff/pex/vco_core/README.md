# `signoff/pex/vco_core/` — R+C parasitic extraction of `vco_core`

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Generated 2026-09-11 from `gds/vco_core.gds` at commit `e60e686`.

`vco_core` is the LC-VCO's complementary cross-coupled pair. Third block to get an extracted
netlist, after `CP_v1` (`../README.md`) and `ib_conv_v1` (`../ib_conv_v1/README.md`). This
closes the block-level half of review-condition item 3.

## Files

| File | What it is |
|---|---|
| `vco_core.pex.spice` | **R+C extracted netlist** of the committed layout — **30 devices, 194 parasitic caps, 208 parasitic resistors**, 436 lines. Magic `ext2spice`, `cthresh 0 rthresh 0`, flattened. |

## Invocation

Recipe: `team_src/magic/pex_vco_core.tcl` (committed), identical to `pex_ib_conv_v1.tcl` apart
from the cell name and GDS path. Regenerate in-container from `team_src/magic/pex_work`:

```
magic -dnull -noconsole -rcfile $PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc ../pex_vco_core.tcl
```

Source is the **committed** `gds/vco_core.gds`. The script writes only into
`team_src/magic/pex_work/` (gitignored) and never writes a GDS.

## Counts

| | value |
|---|---|
| devices | **30** |
| parasitic caps | 194 |
| parasitic resistors | 208 |

**The device count equals the LVS device count.** `verify_cp.sh vco_core` reports 30 devices /
5 ports / 7 nets, match uniquely, 0 property errors, DRC 0.

**Why 30 and not 4.** The schematic golden `vco_core_golden.spice` is a **4-device** circuit:
two `nfet_03v3` and two `pfet_03v3`. The layout folds them into fingers — the W70 pfets are
drawn `nf5/w14` — so extraction sees 30 separate device instances, which netgen then combines
back to the golden's 4. Both numbers are correct for what they count; the PEX check is against
the **extracted** count of 30, which is what `verify_cp` also reports.

## Comparison across the three extracted blocks

| block | devices | caps | resistors |
|---|---:|---:|---:|
| `CP_v1` | 38 | 265 | 269 |
| `ib_conv_v1` | 14 | 70 | 526 |
| `vco_core` | 30 | 194 | 208 |

`ib_conv_v1` is the outlier on R because its VSS bus carries a 193-cut via1 stitch; each cut
and each segment between cuts extracts as its own resistor.

## What this does NOT include

No testbench and no re-simulation. The recorded VCO band (4.13–6.35 GHz) and swing figures are
**schematic-level** and are not re-derived here. Extracting the netlist does not by itself say
anything about oscillation frequency; a PEX re-sim of an autonomous oscillator would need a
transient run that is not part of this pass and is not claimed.
