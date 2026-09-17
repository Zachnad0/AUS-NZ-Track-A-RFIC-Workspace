# `signoff/pex/ib_conv_v1/` — R+C parasitic extraction of `ib_conv_v1`

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)**
Generated 2026-09-11 from `gds/ib_conv_v1.gds` at commit `ce09ccf`.

`ib_conv_v1` is the DIV2 slicer converter, instanced ×4 inside `DIV2_QUAD_v1`. It is the
second block to get an extracted netlist, after `CP_v1` (`../README.md`). Item 3 of the
2026-09-01 review conditions asks for critical-block PEX; this is the block whose internal
VSS bus carries 2.96 mA and was rebuilt on 2026-09-11 with an M2 plate and a 193-cut via1
stitch, so an extracted view of it is worth having.

## Files

| File | What it is |
|---|---|
| `ib_conv_v1.pex.spice` | **R+C extracted netlist** of the committed layout — **14 devices, 70 parasitic caps, 526 parasitic resistors**, 614 lines. Magic `ext2spice`, `cthresh 0 rthresh 0`, flattened. |

## Invocation

Recipe: `team_src/magic/pex_ib_conv_v1.tcl` (committed), adapted from `pex_cp_v1.tcl` with
only the cell name and GDS path changed. Regenerate in-container from `team_src/magic/pex_work`:

```
magic -dnull -noconsole -rcfile $PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc ../pex_ib_conv_v1.tcl
```

Source is the **committed** `gds/ib_conv_v1.gds`. The script writes only into
`team_src/magic/pex_work/` (gitignored) and never writes a GDS.

## Counts, and the one check that matters

| | value |
|---|---|
| extraction runtime | **~1 s** (measured 2026-09-17, `timeout 600` wall clock, in-container) |
| devices | **14** |
| parasitic caps | 70 |
| parasitic resistors | 526 |

**The device count equals the LVS device count.** `verify_cp.sh ib_conv_v1` reports 14 devices
/ 6 ports / 17 nets, match uniquely, 0 property errors. A PEX netlist with a different device
count from the LVS netlist would mean the extraction had dropped or invented a device, which is
the failure this check exists to catch.

Why the R:C ratio is so different from `CP_v1` (269 R / 265 C there, 526 R / 70 C here): the
via1 stitch added on 2026-09-11 is 193 cuts along the VSS bus, and each cut plus each metal
segment between cuts becomes its own parasitic resistor. The high R count is the stitch being
modelled, not an extraction anomaly.

## What this does NOT include

No testbench and no re-simulation. `CP_v1`'s PEX exists to produce an extracted **current
match** number; this one is the extracted netlist only. Nothing in the review conditions asks
for an `ib_conv_v1` operating-point number, and none is claimed here.

## Units: emitted with `ext2spice scale off`

These netlists carry **absolute** device dimensions (`w=8u l=0.3u`). Magic's default emits a
global `.option scale=5n` with dimensions in internal units (`w=1600 l=60`). That option is
**global to the deck**, so a scaled netlist cannot be combined with an absolute-unit bench: it
would rescale every other device too. Earlier revisions of these files were scaled. The two
forms describe the same devices (1600 x 5n = 8u, verified per device), and re-extraction with
`scale off` gives identical counts.
