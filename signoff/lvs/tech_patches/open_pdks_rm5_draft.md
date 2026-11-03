# Draft: open_pdks issue + PR for the gf180mcu `rm5` cifinput rule

**Status: DRAFT, not posted.** Target: `fossi-foundation/open-pdks`, branch `main` (checked at
`55f1ea3`, 2026-11-02). The patch is `open_pdks_rm5_pr.diff` in this directory, a one-line
deletion that applies cleanly to that commit. Requested by Bailey in #143 (2026-11-03). The
"1.2 nH" is the lumped-model value: `L0` + `L1` = 0.60 nH each,
`team_src/xschem/vco_inductor_v2.subckt` lines 11 and 16.

---

## Issue

**Title:** gf180mcu magic tech: metal5 resistors (`rm5`) never extract from GDS (`rm5` requires `RESDEF`, which is never present)

In `gf180mcu/magic/gf180mcu.tech` the cifinput rule for the metal5 resistor is

```
#ifdef METALS5 || METALS6
 layer rm5 MET5
 and RESDEF
 and MET5RES
```

`MET5RES` is `calma MET5RES 110 15`. `RESDEF` is `calma RESDEF 110 *`, and on output it is written
only for `allres` (`layer RESDEF allres` / `calma 110 5`), which covers the poly and diffusion
resistors but not `rm1`–`rm5`. A metal5 resistor is written as MET5 + 110/15 only, so the rule
above cannot match magic's own output, and in our runs it never matches a GDS read either. The
metal under the 110/15 marker is removed from `m5` (`and-not MET5RES`) and does not become `rm5`,
so the resistor comes in as an **open**.

The PDK's KLayout LVS deck defines the top-metal resistor without `RES_MK`:
`tm_res = top_metal.and(top_metal_res)` (res_derivations.lvs:150), with
`metal5_res = get_polygons(110, 15)`.

How we found it: our Chipathon 2026 die (A01) has a 1.2 nH spiral on metal5 whose two halves
carry `Metal5_Res` (110/15) markers and should extract as two `tm11k`. With the stock tech the
organizer LVS (`d-m-bailey/extra_be_checks`, `chipathon2025` @ `7d1f5ef`, tech 1.0.558) never
produces those two `tm11k`:

| our GDS | stock tech | tech with `and RESDEF` removed from `rm5` |
|---|---|---|
| before an unrelated varactor fix | 14 vs 18 devices, failed pin matching | 15 vs 17 |
| current | **16 vs 18 devices**; the only missing devices are the 2 `tm11k` | **Circuits match uniquely** (chip 10/10 devices, 20/20 nets; VCO 8/8) |

(The "unrelated varactor fix" was the missing COMP under 3.3 V `nvaractor`, already fixed upstream
in PR #526 / `c0d31fc556`; our PDK copies predate it.) Full evidence:
https://github.com/Zachnad0/AUS-NZ-Track-A-RFIC-Workspace/blob/main/signoff/lvs/tech_patches/README.md

Also noticed while reading, **not tested**:
- `rm1`–`rm4` and `rmtp` use the same `and RESDEF and METnRES` pattern, so they probably have
  the same problem.
- In the cifinput calma list, `calma MET2RES 110 11` (next to the MET1 mappings) looks like it
  should be `MET1RES`. Output writes `MET1RES` as 110/11, and there is no `calma MET1RES` on input.

---

## PR

**Title:** magic/gf180mcu: Drop RESDEF from the rm5 cifinput rule

**Body:**

The metal5 resistor cifinput rule requires `RESDEF`, but magic never writes `RESDEF` for metal
resistors (`layer RESDEF allres` excludes `rm1`–`rm5`). The PDK's KLayout deck also derives the
top-metal resistor from the metal and the 110/15 marker alone (`tm_res =
top_metal.and(top_metal_res)`). So `rm5` never extracts from GDS: the metal under the 110/15
marker comes in as an open.

This removes `and RESDEF` from `rm5`, so `rm5 = MET5 and MET5RES`, which matches what the writer
emits. `m5` is unchanged (`and-not MET5RES`), so no metal5 outside a 110/15 marker is affected.

Tested on our GF180 Chipathon die with the organizer LVS (`extra_be_checks@7d1f5ef`): the spiral's
two `tm11k` now extract and the chip goes from 16 vs 18 devices (failed pin matching) to
"Circuits match uniquely".

Scope is deliberately `rm5` only, because that is the one I could test. `rm1`–`rm4` and `rmtp` have
the same pattern and probably want the same change, and `calma MET2RES 110 11` looks like a typo
for `MET1RES`. Happy to extend this if you agree.

```
--- a/gf180mcu/magic/gf180mcu.tech
+++ b/gf180mcu/magic/gf180mcu.tech
@@ -2769,7 +2769,6 @@ style  import
 
 #ifdef METALS5 || METALS6
  layer rm5 MET5
- and RESDEF
  and MET5RES
```
