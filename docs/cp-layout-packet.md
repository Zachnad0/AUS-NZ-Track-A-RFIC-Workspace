# CP_v1 layout drawing packet (Aug-14, full-custom analog)

Everything needed to draw CP_v1 in Magic. LVS target: `team_src/magic/CP_v1_golden.spice`
(8 devices, ports `UP DOWN CP_OUT VDD VSS VGP VGN`). Verify with the `docs/layout-flow.md`
recipe (DRC → extract → `netgen` LVS vs golden → "Circuits match uniquely").

## 1. Devices, finger breakdown, dummies

All devices `L` as noted; split into 5 µm fingers where wide, for matching + compactness.

| Device | Type | W / L | Fingers (nf × Wf) | Matching / dummies |
|--------|------|-------|-------------------|--------------------|
| **M_PREF** | pfet_03v3 | 50u / 2u | 10 × 5u | **matched pair with M_PSRC** — common-centroid, +1 dummy finger each end |
| **M_PSRC** | pfet_03v3 | 50u / 2u | 10 × 5u | **matched pair with M_PREF** |
| **M_PSW** | pfet_03v3 | 50u / 0.3u | 10 × 5u | switch, no match; abut to M_PSRC drain (PMID) |
| **M_NREF** | nfet_03v3 | 10u / 2u | 2 × 5u | **matched pair with M_NSNK** — common-centroid, +1 dummy each end |
| **M_NSNK** | nfet_03v3 | 10u / 2u | 2 × 5u | **matched pair with M_NREF** |
| **M_NSW** | nfet_03v3 | 10u / 0.3u | 2 × 5u | switch, no match; abut to M_NSNK drain (NMID) |
| **M_INVP** | pfet_03v3 | 2u / 0.3u | 1 | UP inverter, tiny |
| **M_INVN** | nfet_03v3 | 1u / 0.3u | 1 | UP inverter, tiny |

**Matching is the CP's spec** (UP/DOWN current match = 0.001 % @ 1.5 V in sim). For each
mirror pair use a **common-centroid interdigitation** (e.g. A B B A … so the two devices
share a centroid), **identical finger orientation**, and **1 dummy finger at each array
end** (dummy gate to its rail, S/D shorted to the rail). The long L = 2 u on the mirrors
already aids matching; keep the two devices of a pair in the **same nwell/psub region at
the same y**.

## 2. Guard rings

- **PMOS group** (M_PREF, M_PSRC, M_PSW, M_INVP) sits in one **nwell**. Put a continuous
  **n+ (COMP+nplus) ring tied to VDD** inside the nwell around the PMOS active; also ties
  the nwell to VDD. Ring ~0.5 µm wide, Metal1 contacts every ~1 µm.
- **NMOS group** (M_NREF, M_NSNK, M_NSW, M_INVN) in psub. Continuous **p+ (COMP+pplus) ring
  tied to VSS** around the NMOS active.
- Priority: fully ring the **mirror pairs** — substrate noise on VGP/VGN modulates I_CP →
  loop jitter. Keep **CP_OUT** (to the off-chip loop filter) short and away from switching.

## 3. DUALGATE keep-out to PFD_lib (the mixed-flavor boundary)

CP is 03v3 (no DUALGATE); PFD_lib is 05v0 (DUALGATE over its devices). Exact rules pulled
from `…/klayout/tech/drc/rule_decks/dualgate.drc`:
- **DV.3 — DUALGATE to COMP (unrelated) ≥ 0.24 µm** ← the governing CP↔PFD rule: PFD's
  DUALGATE edge must be ≥ 0.24 µm from any CP COMP/active.
- DV.2 — DUALGATE space ≥ 0.44 µm (between DUALGATE regions; CP has none, so only within PFD).
- DV.6 — DUALGATE encloses PFD's own COMP by 0.24 µm (so PFD's DUALGATE extends 0.24 µm
  past its active).
- Net effect from PFD active edge to CP active: 0.24 (DV.6) + 0.24 (DV.3) = **0.48 µm min**.

**Do → leave a ≥ 0.5 µm block-boundary gap** between CP's outer (VSS p+) guard ring and the
PFD block edge — comfortably clears DV.3. Do **not** abut CP to PFD. Treat them as separate
blocks with a spacing channel (`scope.md §4.2`).

## 4. Suggested floorplan (two bands)

```
  VDD rail ────────────────────────────────────────────  (top, Metal1)
  [ nwell + n+ guard ring (VDD) .......................... ]
  [ dummy | M_PREF/M_PSRC common-centroid (10×5u each) | M_PSW (10×5u) | M_INVP | dummy ]
        VGP gate rail  ───────────────  (PMOS gates; IBIAS_P sinks I_CP from VGP)
                                  ┌── PMID → M_PSW.src
        CP_OUT node  ◄────────────┤  (M_PSW drain + M_NSW drain), exits RIGHT to pad
                                  └── NMID → M_NSW.src
        VGN gate rail  ───────────────  (NMOS gates; IBIAS_N sources I_CP into VGN)
  [ dummy | M_NREF/M_NSNK common-centroid (2×5u each) | M_NSW (2×5u) | M_INVN | dummy ]
  [ p+ guard ring (VSS) .................................. ]
  VSS rail ────────────────────────────────────────────  (bottom, Metal1)
```

## 5. Port locations

| Port | Where | Net / note |
|------|-------|------------|
| **VDD** | top Metal1 rail | PMOS sources + nwell/n+ ring |
| **VSS** | bottom Metal1 rail | NMOS sources + p+ ring |
| **VGP** | PMOS gate rail (mid-top) | gate=drain of M_PREF; **IBIAS_P** current port (external sinks I_CP) |
| **VGN** | NMOS gate rail (mid-bottom) | gate=drain of M_NREF; **IBIAS_N** current port (external sources I_CP) |
| **UP** | left edge | to M_INVP/M_INVN gates (→ UP_B → M_PSW gate) |
| **DOWN** | left edge | to M_NSW gate |
| **CP_OUT** | right edge | M_PSW drain = M_NSW drain; route out, shielded |

Internal nets: `UP_B` (inv out → M_PSW gate), `PMID` (M_PSRC drain → M_PSW src),
`NMID` (M_NSNK drain → M_NSW src). Area estimate ~1200 µm² (`CP_v1_README`); the three
50 µm PMOS dominate.

## 6. Verify (headless, after you draw)
Per `docs/layout-flow.md`: `magic` DRC (expect 0) → `extract all` → `ext2spice` →
`netgen -batch lvs "<ext>.spice CP_v1" "CP_v1_golden.spice CP_v1" $SETUP out` → expect
**"Circuits match uniquely."** Send me the `.mag` and I run this.
