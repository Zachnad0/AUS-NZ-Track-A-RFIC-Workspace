# Pin / Pad Plan — AUS/NZ Track A RFIC

**Team A01 · IEEE SSCS Chipathon 2026 · GF180MCU**
Target slot: **`slot_0p5x0p5`** (per `librelane/slots/slot_0p5x0p5.yaml`).
Last updated: 2026-07-30. Pin assignments are *(estimate)* pending final layout.

> **Slot assumption:** this plan assumes Team A01 is assigned the `slot_0p5x0p5`
> slot (die 1936×2531 µm, core 1052×1647 µm). The larger `slot_workshop` padring
> (60 analog pads) is the tutorial/reference vehicle, not our slot. **Confirm the
> assigned slot with the organizers.**

---

## 1. The fixed padframe (`slot_0p5x0p5`)

Pad **size, count, and location are FIXED** by the organizers; we choose only pad
**types** at the configurable locations. From `slot_defines.svh` + the slot YAML:

| Pad class | Count | Cell / kind | Where |
|-----------|------:|-------------|-------|
| Analog | **4** | analog signal pad | North edge only (`analog[0..3]`) |
| Bidir | 38 | bidirectional I/O (`bidir[0..37]`) | S / E / N / W |
| Dedicated input | 4 | input pad (`inputs[0..3]`) | West edge |
| Clock input | 1 | `clk_pad` (stock single-instance input) | South |
| Reset input | 1 | `rst_n_pad` (stock single-instance input) | South |
| DVDD (power) | 4 | `dvdd_pads[0..3]` | S / E / N / W |
| DVSS (ground) | 4 | `dvss_pads[0..3]` | S / E / N / W |
| Corner | 4 | inserted by LibreLane | corners |

**The 4 analog pads are the binding constraint for this RFIC.**

---

## 2. On-chip / off-chip partition

| Signal | On/off chip | Rationale |
|--------|-------------|-----------|
| Loop filter (R + C1‖C2) | **OFF-chip** | Removes large passives + closed-loop stability risk from silicon; tunable on the bench |
| VCO, PFD, CP, divider | on-chip | Core design |
| Reference | off-chip source → on-chip | Signal generator drives `REF_IN` |
| Charge-pump bias | on-chip preferred | See §4 (IBIAS) |

The off-chip loop filter costs **two** analog pads: `CP_OUT` (charge-pump output
out to the filter) and `VTUNE` (filtered control voltage back to the VCO).

---

## 3. Analog pad assignment — ZERO MARGIN

The default partition consumes **all 4** analog pads with **no spare**:

| Analog pad | Signal | Direction | Measured / driven at this pad |
|-----------|--------|-----------|-------------------------------|
| `analog[0]` | **RF_OUTP** | out | Differential RF output → 50 Ω; power, harmonics, phase noise |
| `analog[1]` | **RF_OUTN** | out | Differential RF output → 50 Ω |
| `analog[2]` | **VTUNE** | in | DC control voltage; open-loop f–VTUNE sweep uses a bench DC source here |
| `analog[3]` | **CP_OUT** | out | Charge-pump output to off-chip loop filter; observe pump up/down |

> ⚠️ **ZERO ANALOG MARGIN.** All 4 analog pads are committed. Any **fifth**
> true-analog (RF or high-impedance) signal is **infeasible on this frame** and
> forces a scope or partition change — it must be escalated, not absorbed.

**RF-pad caveat (test-approach / condition 7):** the analog pad cell carries ESD
structures that add shunt capacitance. At 2.4–5.7 GHz this loads `RF_OUTP/RF_OUTN`;
the output-buffer sizing and any matching must account for measured pad C. This is
a verification item, tracked in `verification.md`.

---

## 4. Digital pads and the DC bias signal

Digital and DC-only auxiliary signals ride the dedicated inputs, `clk_pad`,
`rst_n_pad`, and bidir pads — **never** the analog pads.

| Pad | Signal | Direction | Notes |
|-----|--------|-----------|-------|
| `clk_pad` | **REF_IN** | digital in | Plain digital reference input — native fit for the stock input pad |
| `rst_n_pad` | **RST_N** | digital in | Divider / PFD reset |
| `bidir[0]` (→ output) | **MON_OUT** | digital out | Divided-down VCO copy for frequency observation (counter/scope) |
| `inputs[0]` | **IBIAS_CP** | DC in | External charge-pump I_CP trim — see below |

**IBIAS_CP — DC through a digital pad (per design ruling):** `CP_v1` currently
uses two *ideal* 50 µA reference sources as placeholders. On silicon these become
a real bias network. We **retain an external I_CP trim pin** (`inputs[0]`): with
the loop filter off-chip, I_CP and the loop dynamics are coupled, so a benchtop
trim of the charge-pump reference is cheap insurance for closing the loop. The pin
therefore stays in the committed count (**Digital = 4**). If an on-chip bias
network (constant-gm / resistor-set mirror) is added later, this pad is simply
**tied off** — the count does not change, the trim capability is just unused.

Delivery is a **DC voltage** (not a raw current), so a digital input pad suffices.

> **Pad-cell DC check:** a digital **input** pad presents a high-impedance gate
> (through ESD clamps) to the core — a DC **voltage** reference is sensed with
> negligible current and is safe on `inputs[0]`. A raw DC **current** reference is
> **not** appropriate for a digital I/O pad (no low-impedance DC path to an
> internal mirror node); if external bias is unavoidable it must be a voltage.
> This structural check must be confirmed against the `bi_24t` / input pad cell
> once the container is available; until then IBIAS_CP is carried as provisional.

IBIAS_CP is thus a **committed** pin (Digital = 4), not merely a reservation.

---

## 5. Power / ground assignment (domain-split)

All 4 DVDD + 4 DVSS pads are used, split into analog and digital domains for
isolation (analog domain nearest the VCO/analog pads on the North edge):

| Domain | DVDD pads | DVSS pads |
|--------|-----------|-----------|
| **Analog** (VDDA / VSSA) | `dvdd_pads[2]` (N), `dvdd_pads[1]` (E) | `dvss_pads[2]` (N), `dvss_pads[1]` (E) |
| **Digital** (VDDD / VSSD) | `dvdd_pads[0]` (S), `dvdd_pads[3]` (W) | `dvss_pads[0]` (S), `dvss_pads[3]` (W) |

---

## 6. Pin count summary *(estimate)*

Reported in the weekly-form format. **All four categories are on the fixed frame;
counts are what the committed (Tier 1 + Tier 2) design uses.**

```
Pin count: Power 4  Ground 4  Digital 4  Analog 4
```

- **Power 4** — 4 DVDD (VDDA ×2, VDDD ×2)
- **Ground 4** — 4 DVSS (VSSA ×2, VSSD ×2)
- **Digital 4** — REF_IN (`clk_pad`), RST_N (`rst_n_pad`), MON_OUT (bidir),
  IBIAS_CP (input, external DC I_CP trim; tied off if on-chip bias is added — count stays 4)
- **Analog 4** — RF_OUTP, RF_OUTN, VTUNE, CP_OUT — **fully committed, zero margin**

Spare on the frame after this plan: 37 bidir + 3 inputs + 0 analog. The analog
zero-margin is the item to watch.
