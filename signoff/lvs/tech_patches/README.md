# `signoff/lvs/tech_patches/` — two magic tech-file patches, and the varactor COMP defect

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)** · 2026-11-02

No tech file is committed and no PDK or runner file is ever edited. These are diffs, applied
to throwaway copies.

| Patch | Applies to | Side | What it fixes |
|---|---|---|---|
| `varactor_comp.diff` | magic `gf180mcuD.tech`: `$PDK_ROOT` 1.0.575 (container) and the `extra_be_checks` 1.0.558 copy (same hunk) | **writer** (cifoutput `gdsii`) | COMP (22/0) is not written under 3.3 V varactor gates |
| `rm5.diff` | `extra_be_checks@7d1f5ef` `tech/gf180mcuD/gf180mcuD.tech` | **reader** (cifinput) | `vco_inductor_v2` extracts as an open instead of two `tm11k` |

## The defect: no COMP under the 42 varactor gates

`vco_varactors` holds 42 `cap_nmos_03v3_b` (`nmoscap_3p3`, 5 × 5 µm). In magic each gate is
the device type `nvaractor`. When magic writes GDS, the `gdsii` cifoutput `DIFF` layer (COMP,
22/0) is

```
 layer DIFF 	schottky
	and-not	scsep
	or	alldiff
```

`alldiff` = `alldifflv,alldiffmv`. The 6 V list `allndiffmv` includes `mvnvaractor` and
`allpdiffmv` includes `mvpvaractor`, but the 3.3 V lists `allndifflv`/`allpdifflv` leave
`nvaractor`/`pvaractor` out. So a 3.3 V varactor gate gets POLY, NPLUS, NWELL and
`MOS_CAP_MK` (166/5) in the GDS, but **no COMP**: poly over field oxide, not a MOS varactor.

The tech's own cifinput rule `layer nvar POLY and DIFF and NPLUS and nwelldef and-not DUALGATE`
needs that COMP, so magic cannot read its own varactors back. The PDK's KLayout LVS defines
`cap_nmos_03v3_b = (nplus ∩ poly2 ∩ comp) − v5_xtor − dualgate, ∩ nwell, interacting mos_cap_mk`
(`general_derivations.lvs:23,25,56`, `moscap_derivations.lvs:55`), so the foundry deck could not
see them either. This was present in **every** `vco_varactors.gds`, `vco_v1.gds` and
`chip_top.gds` committed before 2026-11-02.

It hid in plain sight. The 168 KLayout PL.5a_LV/PL.5b_LV items, waived as "W4, internal to the
`nmoscap_3p3` gencell", and magic's GDS-path DRC 84 were both this defect. The "bare single unit
also shows 4" check reproduced it rather than clearing it, because the unit had gone through the
same stock writer. The `.mag`-based gates (`verify_cp.sh`, the VCO PEX) could not see it: they
never read the GDS's varactors.

## Evidence (committed GDS `057251a` vs fixed GDS)

| Check | Before | After |
|---|---|---|
| COMP ∩ `MOS_CAP_MK` over the 42 gates (flattened `chip_top`) | **0.000 µm²** | **1050.000 µm²** (42 × 25) |
| PDK `cap_nmos_03v3_b` derivation, `vco_varactors` / `vco_v1` / `chip_top` | **0 / 0 / 0** | **42 / 42 / 42** |
| GDS XOR, fixed vs before, all three files | — | **22/0 +1050.000 µm² only**; bbox and all labels (3 / 19 / 529) identical |
| KLayout variant-D DRC, `vco_varactors` / `vco_v1` / `chip_top` | 168 / 168 / 168 (84 PL.5a_LV + 84 PL.5b_LV) | **0 / 0 / 0**, no new rule |
| Magic DRC (`drc_boxset.tcl`), same three | TOTAL 84; 252 / 117 / 252 boxes | **0 / 0 / 0** |
| Organizer `run_full_lvs`, stock `extra_be_checks@7d1f5ef` | 14 vs 18 devices, failed pin matching | 16 vs 18: varactors match, only the 2 `tm11k` missing |
| Organizer `run_full_lvs`, with `rm5.diff` | 15 vs 17 (varactors missing) | **Circuits match uniquely**: top 10/10, 20/20 nets; `vco_v1` 8/8 incl. `cap_nmos_03v3_b (42→2)` (exit 5 = matched, with black-boxed `tm11k`/`cap_nmos_03v3_b` and ignored fill cells) |
| `verify_cp.sh` × 6 | PASS | PASS, identical device/port/net counts (reads the varactors from `.mag`, so blind to this either way) |
| `vco_v1` R+C PEX from GDS (coil kept as the abstract, as the VCO PEX was made) | 33 devices, **0 varactors** | 75 devices, 42 varactors, 804 C / 1259 R, coil lines identical to `signoff/pex/vco_v1/vco_v1.pex.spice`; OUT_p/OUT_n C −0.28 % vs that `.mag` PEX |
| VCO, ISS 2.0×, VTUNE 0 / 2.0 / 3.3 V, from that PEX (200 ns) | — | **5.7278 / 4.4020 / 3.8069 GHz**, 3.036 / 2.205 / 1.025 Vpp, startup 13.0 / 20.3 / 22.7 ns; record 5.728 / 4.402 / 3.807 GHz |

The fixed GDS was produced by a magic `gds write` of the unchanged `team_src/magic/vco_varactors.mag`
with the patched tech. A **control** write with the stock tech XORs to 0.000 µm² against the old
committed GDS, so the path reproduces the old file exactly and the 1050 µm² is the patch alone.

## The fix, and how it is kept fixed

- **`team_src/magic/phase5/write_vco_gds.sh OUTDIR`** is the only sanctioned way to write these
  GDS files. It copies `$PDK_ROOT`'s tech into OUTDIR, applies `varactor_comp.diff` (it fails if
  the patch does not apply), and runs magic with that tech. The magic script checks
  `[tech filename]` for the patched line and **refuses to `gds write`** otherwise; this was tested
  with the line reverted. It then splices the cell into copies of `gds/vco_v1.gds` and
  `gds/chip_top.gds` (`team_src/magic/phase5/splice_cell.py`) and runs the gate. It writes only into
  OUTDIR. Its output XORs to 0.000 µm² against the committed fixed GDS.
- **`team_src/magic/analysis/varactor_comp_gate.py`** (`klayout -b -r …`): COMP ∩ `MOS_CAP_MK`
  = 1050 µm² and 42 PDK-derived `cap_nmos_03v3_b`, on all three files. Exit 1 on the pre-fix GDS,
  exit 0 on the fixed one.
- **The W4 waiver is revoked.** `chip_top.waivers` and `vco_v1.waivers` accept nothing, so any
  PL.5a/5b that reappears fails `klayout_signoff.py`.
- **The DRC baseline** `team_src/magic/chip_top.drcbase` is recaptured: TOTAL 0, 0 boxes.
- `vco_varactors.tcl` and `vco_v1.tcl` carry a GDS-export warning in their headers.

The organizer's reader needs only `rm5.diff`, which is Bailey's pending tech fix (issue #143,
2026-09-25).

## Upstream status (checked 2026-11-03)

**The varactor COMP defect is already fixed upstream; none of the toolchains in use has the fix.**
`fossi-foundation/open-pdks` (formerly `RTimothyEdwards/open_pdks`) PR #526,
"magic/gf180mcu: Add {n,p}varactor to all{n,p}difflv" (Sylvain Munaut), adds `nvaractor` and
`pvaractor` to the `allndifflv`/`allpdifflv` aliases in open_pdks' magic template for gf180mcu
(gf180mcu.tech under gf180mcu/magic). It is
commit `c0d31fc556`, 2026-06-14; Tim Edwards merged it the same day via opencircuitdesign.com,
so GitHub shows the PR as closed, not merged. `516b142d35` (same day) then corrected the
moscap/varactor drawing routines in the device generator. Both are in today's `main`/`master`.
Upstream fixed it at the alias, which also feeds DRC and extract rules that use `alldifflv`.
`varactor_comp.diff` changes only the gdsii COMP output, the narrowest change that fixes the GDS.

| Toolchain | open_pdks | Has the fix? |
|---|---|---|
| container `$PDK_ROOT` (used to write our GDS) | 1.0.575, `7b70722`, 2026-03-01 | **no**, 68 commits behind `c0d31fc556` |
| organizer runner `extra_be_checks@7d1f5ef` tech | 1.0.558, `486fb86`, 2025-11-22 | **no**, 99 commits behind |
| local `gf180mcu/` (wafer-space PDK, tag 1.8.0) | 1.0.562, `8fa792c` | **no** |

So any 3.3 V varactor written by magic with these PDKs, on any team's die, lacks COMP unless the
writer is patched or the PDK is updated past `c0d31fc556`.

**`rm5.diff` is NOT fixed upstream.** `main` still has `layer rm5 MET5 / and RESDEF / and MET5RES`
and `calma RESDEF 110 *`, so the inductor `tm11k` gap remains in every version. A one-line fix
against upstream `main` (`55f1ea3`) is in `open_pdks_rm5_pr.diff`, with draft issue and PR text in
`open_pdks_rm5_draft.md`. **Not posted.** On the cause: magic's writer never emits `RESDEF` for
metal resistors (`layer RESDEF allres` excludes `rm1`–`rm5`), so the input rule could not match
even its own output. The PDK's KLayout deck derives the top-metal resistor without `RES_MK`.

## Reproducing

```
bash team_src/magic/phase5/write_vco_gds.sh /tmp/vco_gds      # in the iic-osic-tools container
klayout -b -r team_src/magic/analysis/varactor_comp_gate.py   # on the committed gds/
```
