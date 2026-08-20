# LVS config validation — `lvs/lvs_config.json` (Phase-7 item 1, 2026-08-20)

Validates the repointed `lvs/lvs_config.json` against the organizer's
`extra_be_checks` flow (`d-m-bailey/extra_be_checks`, magic + netgen backend).

## (a) Key structure vs the upstream example — IDENTICAL

Diffed our config against the upstream template
`extra_be_checks/tech/gf180mcuD/lvs_config.user_project_wrapper.json`.
**Same key set, exactly** — `STD_CELL_LIBRARY`, `INCLUDE_CONFIGS`, `TOP_SOURCE`,
`TOP_LAYOUT`, `EXTRACT_FLATGLOB`, `EXTRACT_ABSTRACT`, `LVS_FLATTEN`,
`LVS_NOFLATTEN`, `LVS_IGNORE`, `LVS_SPICE_FILES`, `LVS_VERILOG_FILES`,
`LAYOUT_FILE`. No unknown/missing/misspelled keys.

The only structural difference is **which source-netlist key is populated**:

| key | upstream wrapper (digital) | ours (analog) |
|-----|----------------------------|---------------|
| `LVS_SPICE_FILES`   | `[""]` (empty) | `["$UPRJ_ROOT/team_src/magic/chip_top_golden.spice"]` |
| `LVS_VERILOG_FILES` | 2 gate-level `.v` files | `[""]` (empty) |

`LVS_SPICE_FILES` and `LVS_VERILOG_FILES` are **mutually-exclusive alternatives**:
you populate the one that matches your source netlist. The wrapper is a
gate-level digital block → Verilog. Ours is a full-custom analog chip → SPICE.
Our config is the correct analog mirror of the template.

## (b) Clearing `LVS_VERILOG_FILES` — CORRECT

The concern was that `chip_top` contains gf180 standard cells inside `PFD_lib`.
Checked how they appear in the source golden (`chip_top_golden.spice`): the std
cells are **referenced by name** as subckt instances, e.g.

```
X1  DHI1 RSTN REF  UP  VDD VDD VSS VSS  gf180mcu_fd_sc_mcu7t5v0__dffrnq_1
XN  UP DOWN NANDO      VDD VDD VSS VSS  gf180mcu_fd_sc_mcu7t5v0__nand2_1
XTIE1 DHI1 VDD VDD VSS VSS             gf180mcu_fd_sc_mcu7t5v0__tieh
```

Their **definitions are not in the golden** (it defines only `chip_top` + the 5
blocks). They are resolved from **`STD_CELL_LIBRARY = gf180mcu_fd_sc_mcu7t5v0`**,
whose spice ships in the PDK and is present:
`/foss/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/spice/gf180mcu_fd_sc_mcu7t5v0.spice`.

So the std cells are handled by the SPICE-source + `STD_CELL_LIBRARY` path;
`LVS_VERILOG_FILES` would only be needed if the *source* were gate-level Verilog.
It is not → clearing it is correct. **Confirmed empirically:** `verify_cp.sh
chip_top` extracts the layout and LVS's it against this exact golden →
**"match uniquely"** (netgen pulls the std-cell defs from the PDK setup).

## (c) Path resolution — EXISTS / MISSING

Variables: `$UPRJ_ROOT` = design root; `$PDK` = `gf180mcuD`; `$TOP_SOURCE` =
`chip_top`; `$TOP_LAYOUT` = `$TOP_SOURCE`; `$LVS_ROOT` = the organizer's
`extra_be_checks` install root.

| config path | resolves to | status |
|-------------|-------------|--------|
| `LVS_SPICE_FILES[0]` = `$UPRJ_ROOT/team_src/magic/chip_top_golden.spice` | design tree | **EXISTS** |
| `LAYOUT_FILE` = `$UPRJ_ROOT/gds/$TOP_LAYOUT.gds` = `.../gds/chip_top.gds` | design tree | **EXISTS** |
| `STD_CELL_LIBRARY` = `gf180mcu_fd_sc_mcu7t5v0` | PDK `libs.ref/.../spice/…` | **EXISTS** |
| `INCLUDE_CONFIGS[0]` = `$LVS_ROOT/tech/$PDK/lvs_config.base.json` | `extra_be_checks/tech/gf180mcuD/lvs_config.base.json` | **REAL upstream** (confirmed in Bailey's repo tree), **absent locally** |
| `$LVS_ROOT` (the `extra_be_checks` install itself) | Bailey's env | **MISSING locally** (expected — organizer provides it) |
| `LVS_VERILOG_FILES` = `[""]` | — | intentionally empty |

Every path we own resolves. The only MISSING paths are the two that live under
`$LVS_ROOT` (the base config + the tool root) — supplied by the organizer's
harness, not this repo. `INCLUDE_CONFIGS` points at a path that genuinely exists
in `extra_be_checks` (`tech/gf180mcuD/lvs_config.base.json`), so it will resolve
in Bailey's environment.

The source golden's top port list matches `info.yaml`/`pins.md` exactly (12):
`chip_top VSSA VDDA IBIAS ISS VTUNE CP_OUT I_P I_N Q_P Q_N VDDD REF_IN`.

## (d) Running the organizer's flow locally — NOT possible here; what's missing

Two blockers:

1. **`extra_be_checks` is not installed** in this container (`$LVS_ROOT` absent),
   so the organizer's `run_be_checks`/LVS driver cannot be invoked. Installing it
   + its `tech/gf180mcuD/lvs_config.base.json` would clear this one.

2. **Its stock direct-GDS extraction cannot see two of our devices** — this is the
   important finding for Bailey coordination:
   - The **nmoscap_3p3 varactors** extract as **zero capacitors** from flat GDS
     (magic gets no device from the foundry nmoscap geometry).
   - The **inductor spiral** (`vco_inductor_v2`) is invisible to a flat extract.

   Our local `verify_cp.sh` only passes because `chip_top.abstract` **pre-loads
   device-aware `.mag` cells** (`vco_varactors`, `vco_inductor_v2`) with
   `gds noduplicates true` **before** `gds read`, and adds
   `ignore class vco_inductor_v2` to the netgen setup. Proven: disabling the
   abstract and running the flow directly on the GDS gives **84 DRC + LVS DO NOT
   MATCH** on the vco. The stock `extra_be_checks` GDS path does **not** do this
   preload, so it will mis-extract the VCO tank unless the same abstract mechanism
   is wired into the organizer's flow (or the varactor/inductor are handled as
   black boxes / LEF abstracts on their side).

**Recommendation for tapeout:** flag to Bailey that the VCO's nmoscap varactors
and spiral inductor need device-aware handling (abstract preload or black-box) in
the signoff LVS — a flat GDS extract will not reproduce our `match uniquely`.
Everything else in the config is upstream-identical and path-clean.
