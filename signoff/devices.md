# Device declaration — `chip_top`

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD) · issue
[#143](https://github.com/sscs-ose/sscs-chipathon-2026/issues/143)**
Generated 2026-09-01 from commit `52a783a`, layout `gds/chip_top.gds`.

Every device on the die, by **exact PDK model name**. Written in response to the Fraunhofer
requirement that each chip declare precisely which devices it uses.

**Source of every count in this file:** `signoff/lvs/chip_top.lvs.spice` — the Magic-extracted
netlist of the taped-out layout, hierarchy expanded and `m=` multipliers applied. Nothing here
is taken from a schematic, a plan, or a note. The netgen comparison that certifies this netlist
matches our golden is `signoff/lvs/lvs.report` (**"Circuits match uniquely"**).

---

## 1. Devices used

| PDK model name | Count | Where used | PDK definition |
|---|---:|---|---|
| `nfet_03v3` | **304** | `CP_v1` 7 · `ibias_gen_v1` 112 · `DIV2_QUAD_v1` 165 · `vco_v1` 20 | `sm141064.ngspice` — *"Subcircuit model for 3.3V NMOS"* |
| `pfet_03v3` | **177** | `CP_v1` 31 · `ibias_gen_v1` 116 · `DIV2_QUAD_v1` 20 · `vco_v1` 10 | `sm141064.ngspice` — *"Subcircuit model for 3.3V PMOS"* |
| `nfet_05v0` | **95** | `PFD_lib` only — inside `gf180mcu_fd_sc_mcu7t5v0` standard cells | `sm141064.ngspice:47094` |
| `pfet_05v0` | **95** | `PFD_lib` only — inside `gf180mcu_fd_sc_mcu7t5v0` standard cells | `sm141064.ngspice:47152` |
| `cap_nmos_03v3_b` | **42** | `vco_v1` / `vco_varactors` — the VCO tuning varactor array | `sm141064.ngspice` — *"Subcircuit Model for 3.3v NMOS in Nwell capacitor"* |
| `ppolyf_u_1k` | **13** | `DIV2_QUAD_v1` 12 · `vco_v1` 1 | `sm141064.ngspice` — *"3-terminal 1k high-Rs p+ poly resistor on field oxide (3.3V area)"* |
| `diode_nd2ps_03v3` | **8** | `chip_top` — secondary ESD, `esd_nd2ps` ×2 instances | `sm141064.ngspice:45` — *"Model for 3.3V N+/Psub diode"* |
| `diode_pd2nw_03v3` | **8** | `chip_top` — secondary ESD, `esd_pd2nw` ×2 instances | `sm141064.ngspice:46` — *"Model for 3.3V P+/Nwell diode"* |
| `cap_mim_2f0_m4m5_noshield` | **4** | `DIV2_QUAD_v1` — AC-coupling cap, one per `ib_conv_v1` slicer (×4) | `sm141064_mim.ngspice:252` |
| `tm11k` | **2** | `vco_v1` / `vco_inductor_v2` — the spiral's top-metal leads | `sm141064.ngspice:39116` — *"2-terminal top metal 11k resistor"* |
| `ppolyf_u` | **1** | `chip_top` — `esd_rpoly`, the IBIAS ESD series ballast (16 × 4 µm) | `sm141064.ngspice` — *"3-terminal unsalicided p+ poly resistor"* |
| | **749** | **total device instances on the die** | |

**11 distinct PDK models.** Every name above was checked to exist in the PDK on disk, both as
a SPICE model in `gf180mcu/gf180mcuD/libs.tech/ngspice/` and as a `device` line in
`gf180mcu/gf180mcuD/libs.tech/magic/gf180mcuD.tech`.

### Device × block matrix

| device | `PFD_lib` | `CP_v1` | `ibias_gen_v1` | `DIV2_QUAD_v1` | `vco_v1` | ESD (chip) | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cap_mim_2f0_m4m5_noshield` | – | – | – | 4 | – | – | 4 |
| `cap_nmos_03v3_b` | – | – | – | – | 42 | – | 42 |
| `diode_nd2ps_03v3` | – | – | – | – | – | 8 | 8 |
| `diode_pd2nw_03v3` | – | – | – | – | – | 8 | 8 |
| `nfet_03v3` | – | 7 | 112 | 165 | 20 | – | 304 |
| `nfet_05v0` | 95 | – | – | – | – | – | 95 |
| `pfet_03v3` | – | 31 | 116 | 20 | 10 | – | 177 |
| `pfet_05v0` | 95 | – | – | – | – | – | 95 |
| `ppolyf_u` | – | – | – | – | – | 1 | 1 |
| `ppolyf_u_1k` | – | – | – | 12 | 1 | – | 13 |
| `tm11k` | – | – | – | – | 2 | – | 2 |
| **total** | **190** | **38** | **228** | **201** | **75** | **17** | **749** |

---

## 2. Configurator-name mapping

Some tools name devices differently from the PDK. Where an alias is known, it is given here;
the **PDK model name is the authoritative one** and is what appears in our netlists.

| Configurator / form name | Real PDK model | Basis for the mapping |
|---|---|---|
| `np_3p3` | **`diode_nd2ps_03v3`** | **Direct evidence from foundry collateral** — see below. Corroborated by the model index, `sm141064.ngspice:45`: *"`diode_nd2ps_03v3` Model for 3.3V **N+/Psub** diode"*. `np` = N+/P-substrate; `3p3` = 3.3 V = the PDK's `03v3`. |
| `pn_3p3` | **`diode_pd2nw_03v3`** | **Inferred by symmetry**, not directly evidenced. `sm141064.ngspice:46`: *"`diode_pd2nw_03v3` Model for 3.3V **P+/Nwell** diode"*. `pn` = P+/N-well, the mirror of the `np` case above. It is the only 3.3 V diode left once `np_3p3` is assigned. |

**The direct evidence for `np_3p3`.** The PDK ships 15 diode unit-test layouts under
`libs.tech/klayout/tech/lvs/testing/testcases/unit/diode_devices/layout/`. Fourteen name their
sub-cells after the device — `diode_pd2nw_03v3_CDNS_…`, `diode_nw2ps_06v0_CDNS_…`, and so on.
**Exactly one breaks the pattern:** `diode_nd2ps_06v0_dn.gds` has top cell
`diode_nd2ps_06v0_dn` but sub-cells named **`np_3p3_dw_CDNS_…`**. That is a leftover internal
name in the foundry's own test collateral for the device the PDK ships as `diode_nd2ps_*`
(`_dw` = deep-well, matching the file's `_dn` suffix). So `np_3p3` is not a Chipathon
invention — it is a GlobalFoundries-side alias for the **N+/P-substrate** diode.

> **Neither `pn_3p3` nor `np_3p3` is a usable device name.** Neither is a SPICE `.model` or
> `.subckt`, a `device` line in the Magic techfile, or a token in any KLayout DRC/LVS deck.
> A search of every **text** file in the vendored PDK, this repository, and the organizer
> repository snapshot (`sscs-chipathon-2026-main`) returns **nothing** for either. `np_3p3`
> survives only inside one **binary GDS** as the cell name above; `pn_3p3` appears nowhere at
> all, in any form. **Anything aggregating this project must use the `diode_*_03v3` names** —
> `pn_3p3`/`np_3p3` will not match a netlist, ours or anyone's.
>
> The `3p3` spelling is also an organizer-side convention — the reference ESD cell in the
> organizer repo is `io_secondary_3p3` — but that is a **cell** name, not a device model. The
> PDK spells 3.3 V devices `*_03v3` throughout.

**No other alias is on record.** For the other nine models we have no configurator name, and
none is invented here. Use the PDK model name verbatim.

The only 3.3 V diodes the PDK defines at all are `diode_nd2ps_03v3`, `diode_pd2nw_03v3` and
`diode_nw2pw_03v3` (`gf180mcuD.tech:4163–4164` plus the `*_03v3` name index). We use the first
two. We do not use `diode_nw2pw_03v3`.

---

## 3. Counting conventions — read this before quoting a number

Three different device counts exist for this design. All three are correct for what they
measure, and they are routinely confused.

| Convention | `chip_top` | What it counts |
|---|---:|---|
| **Flattened extracted instances** *(used throughout this file)* | **749** | Every physical device drawn on the die, hierarchy expanded, `m=` applied. This is the number a foundry aggregation wants. |
| **netgen merged devices** | **10** at top level | What LVS compares after parallel-merging. netgen folds fingers and parallel units into one logical device, so a `W=50 µm` PMOS drawn as 10 × 5 µm fingers counts as **one**. Per block: `PFD_lib` 7, `CP_v1` 8, `ibias_gen_v1` 17, `DIV2_QUAD_v1` 75, `vco_v1` 7. |
| **`verify_cp.sh` summary line** | 10 | Its own tally of instance lines in one subcircuit's own body, **not** descending into child cells — and it counts a child *instantiation* as one line. E.g. it prints 149 for `DIV2_QUAD_v1`: 145 leaf devices plus 4 `ib_conv_v1` instance lines. Each `ib_conv_v1` flattens to 14 devices, so the physical total is 145 + 4×14 = **201**, the flattened figure above. |

Worked example, `CP_v1`: the layout draws **38** transistor fingers; netgen reports
*"Merged 30 parallel devices"* and compares **8** devices against the golden's 8. Both numbers
appear in `signoff/lvs/blocks/CP_v1.lvs.report`.

---

## 4. Per-device notes

**`nfet_05v0` / `pfet_05v0` — 5 V devices, and why a 3.3 V chip has them.** GF180 ships no
3.3 V standard-cell library, so the digital PFD is built from `gf180mcu_fd_sc_mcu7t5v0`, which
is a 5 V cell library. Both flavours run off the single 3.3 V supply. The two flavours are kept
in separate blocks and never interleaved (`docs/scope.md` §4.1–4.2). Of the 95 per polarity:
**34 are in functional cells** (2× `dffrnq_1` = 28, 1× `nand2_1` = 2, 2× `inv_1` = 2,
2× `tieh` = 2) and **61 are in decap/fill cells** (`fillcap_16` ×6, `fillcap_32` ×3,
`fillcap_4` ×5, `fillcap_8` ×4). The fill cells are LVS-ignored but are **physically present
on the die** and are counted here.

**`ppolyf_u` and `ppolyf_u_1k` are different PDK models**, not a typo. `ppolyf_u` is the
generic unsalicided p+ poly resistor (used once, as the IBIAS ESD ballast); `ppolyf_u_1k` is
the 1 kΩ/□ high-sheet variant (used 13×). Note the PDK also defines `ppolyf_u_3k`, which is the
**same physical layer** — 1k vs 3k is a per-fab-run process choice, not a layout difference, so
the two cannot both be nominal on one shuttle run (`docs/tracking.md` §5). We draw everything
as `ppolyf_u_1k`.

**`ppolyf_u_1k` × 13, by function:** 4 CML load resistors (300 Ω) in `DIV2_QUAD_v1`; 4 feedback
resistors (20 kΩ) and 4 output series-isolation resistors (1 kΩ), one of each per `ib_conv_v1`
slicer; and 1 VCO tune resistor (15 kΩ, `vco_tune_r`). Same model, four different geometries.

**`cap_nmos_03v3_b` × 42 = two logical varactors.** The differential tuning array is drawn as
42 identical 5 × 5 µm units, mirror-symmetric about the vertical centre, which netgen merges
into the golden's 2 devices at `m=21` each.

**`tm11k` × 2 — extracted, not instantiated.** We did not place a `tm11k`. The custom spiral
inductor `vco_inductor_v2` has no foundry device model, so it is an LVS `ignore class`; its two
M5 leads nevertheless extract as top-metal resistors (`r_width=8u r_length=76u` each) because
the Magic techfile maps M5 to `tm11k` (`gf180mcuD.tech:4141`). **It is a real PDK model and it
does appear in our netlist**, so it is declared — but the physical object is a 1.2 nH inductor,
not two resistors. If an aggregation expects only instantiated devices, `tm11k` is the one row
to ask about.

**`diode_nd2ps_03v3` / `diode_pd2nw_03v3` × 8 each = 2 logical clamps each.** Secondary ESD on
two pins, `IBIAS` and `ISS`. Each clamp is drawn as 4 parallel 10 × 10 µm units; netgen reports
`(8->2)`. Only 2 of the 7 analog pins carry a secondary clamp — see
`docs/layout-review-sep01.md` §2.4 for why, and for the unwritten-rule risk attached to that.

---

## 5. Cross-references

| | |
|---|---|
| Top-level LVS report | `signoff/lvs/lvs.report` |
| Extracted chip netlist (source of every count here) | `signoff/lvs/chip_top.lvs.spice` |
| Per-block reports and netlists | `signoff/lvs/blocks/` |
| How to regenerate, and the two LVS waivers | `signoff/lvs/README.md` |
| Full layout review, verification and gaps | `docs/layout-review-sep01.md` |
| Pin/pad plan | `docs/pins.md` |
