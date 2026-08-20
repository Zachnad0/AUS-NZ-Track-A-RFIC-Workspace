# GF180MCU gencell devices don't survive a flat-GDS LVS extract

**A flow-level finding for chip-level integration LVS (`extra_be_checks`), not an
A01-specific problem.** Any Chipathon project that instances a **GF180MCU gencell
device magic cannot rebuild from flat GDS** — an **nmoscap varactor**
(`nmoscap_3p3` / `cap_nmos_03v3_b`) or a **spiral inductor** — will fail chip
LVS the same way. Sharing the evidence and our workaround in case it helps the
signoff flow.

## What fails

Running the extraction exactly as `extra_be_checks/run_extract` does — magic
reads the top GDS flat and extracts a SPICE netlist — on a chip that contains an
`nmoscap_3p3` varactor and a spiral inductor:

- **magic DRC = 84**, and every one of them is a **single rule, PL.5a** (*Poly
  spacing to diffusion < 0.1 µm*), located **inside the nmoscap_3p3 devices**.
  These are the device's own internal poly-to-COMP spacing — the same items a
  KLayout signoff waives (PL.5a_LV / PL.5b_LV). They are not real spacing errors;
  they are the gencell's internal geometry seen without device recognition.
- The varactor extracts as **zero capacitors** (`grep -c '^C'` on the netlist =
  0). The cap device is simply gone.
- The spiral inductor's two terminals **merge into one net** — a differential
  inductor is DC-continuous metal, and with no inductor device model magic joins
  its ports (which then shorts whatever the two terminals drive, e.g. a divider's
  CK/CKB).

Net result: **LVS DO NOT MATCH**, on a layout that is otherwise correct and passes
LVS with the workaround below.

## Why it fails

GF180 `nmoscap_3p3` (and the FET/res gencells) are **magic gencells**: magic
knows they are devices because it drew them and carries the device identity in the
cell's parameters/hierarchy. **Writing to GDS and reading it back FLAT drops that
identity** — magic sees only the raw layers (poly, COMP, contact, metal) and no
longer recognizes a capacitor, so it extracts none and its raw internal geometry
trips generic DRC (PL.5a). The spiral is worse: **GF180 magic has no inductor
extraction at all**, so a flat coil is just one continuous wire and its two
terminals collapse to a single node.

The device recognition lives in the cell, not the shapes — so the failure is
**inherent to any flat-GDS round trip**, independent of the project.

## How we worked around it locally

We keep a device-aware view of just the un-extractable cells and preload it
**before** the flat `gds read`, using `gds noduplicates true` so magic keeps the
preloaded version and skips those cells' flat geometry from the stream:

```tcl
gds noduplicates true
load vco_varactors        ;# a .mag that draws the nmoscap_3p3 gencells -> extracts as caps
load vco_inductor_v2      ;# a geometry-free abstract (LEFview) for the spiral
gds read chip_top.gds     ;# noduplicates keeps the two views above
load chip_top
extract ...
```
plus `ignore class vco_inductor_v2` in the netgen setup for the (black-box)
inductor. With this, `chip_top` extracts the varactors as real caps, keeps the
inductor's ports distinct, and netgen reports **match uniquely**.

## What the signoff flow would need

Two possible hooks for `extra_be_checks`, either would fix it generically:

1. **A device-aware preload**, like above: allow a project to name cells whose
   device-aware `.mag` (or gencell-regenerated view) should be `load`ed with
   `gds noduplicates true` before `gds read`. This is the most faithful — the
   varactor stays a real cap in LVS.

2. **The existing `EXTRACT_ABSTRACT` LEF path — with a caveat.** `run_extract`
   already black-boxes a cell by writing a pin-only LEF (PASS 1) and re-reading it
   with `gds noduplicates yes` (PASS 2). That *does* drop the shorting coil and
   the un-extractable varactor. **But** `magic lef write` emits `ORIGIN <llx>
   <lly>` for a cell whose native lower-left is not `(0,0)`, and `lef read` then
   places the abstract shifted by `-ORIGIN`, so the abstract pins miss the metal
   they should touch. P&R blocks are origin-normalized so this never bites them;
   **hand-drawn analog cells with a non-zero native origin do.** Origin-
   normalizing the abstracted cell (or having `run_extract` compensate the LEF
   ORIGIN on read) closes this.

Happy to share the exact reproduction scripts (a faithful two-pass local
reproduction of `run_extract`) if useful.

---

### Evidence commands (for anyone reproducing)

```bash
# faithful reproduction of run_extract's extraction, no device-aware preload:
#   magic ... bailey_extract.tcl   with ABSTRACT_CELLS=""  -> 84 DRC (all PL.5a), 0 caps
#   grep -c '^C' chip_top.gds.spice            # -> 0  (varactors gone)
#   grep 'RULE' chip_top.drc                    # -> only 'PL.5a (Poly spacing to diffusion)'
# with the device-aware preload (chip_top.abstract): netgen -> Circuits match uniquely
```
