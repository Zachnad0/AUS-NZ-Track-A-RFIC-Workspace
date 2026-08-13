# Phase 5.1 — CP_v1 layout (scripted, Magic Tcl)

Target: `team_src/magic/CP_v1_golden.spice` (8 devices + dummies), packet
`docs/cp-layout-packet.md`. Verify via `team_src/magic/verify_cp.sh` (Phase 1 hardened).
Run in `iic-osic-tools_xvnc` after `sak-pdk gf180mcuD`.

## Opener — guard 0 vs guard 1 (DECIDED: guard 0 + manual group ring)
`guard_test.tcl` / `gt_array.tcl`, file-read DRC:
- single pfet 5u/2u: guard=1 DRC 0 (bbox 900 wide, ring adds ~0.76µm/side); guard=0 DRC 0
  (bbox 748 wide, bare active).
- nf=10 shared-diffusion array: guard=0 DRC 0 (5284 wide), guard=1 DRC 0 (5376 wide, ONE
  ring around the whole device).

**Finding:** `guard` rings the whole DEVICE, so multi-finger arrays *within one device* are
fine either way. The blocker is the matched PAIR: M_PREF and M_PSRC are two separate devices
that must common-centroid interdigitate (A B B A). Under guard=1 each gets its OWN ring — two
rings cannot interleave. **So: `guard 0` on the mirror devices, and draw ONE group guard ring
around the combined common-centroid array** (matches the packet's "ring the mirror pairs").
guard=0 arrays are DRC-clean, so this is feasible. This is settled before array topology.

## Build stages (per packet, DRC=0 at each; render with lay2img.py)
(a) one device → (b) matched pair → (c) interdigitated array + dummies → (d) guard rings →
(e) routing → (f) labels/ports → (g) full verify_cp.sh (match uniquely vs golden).

## Golden dummies (settled Gate 1 + Greg): add the 4 end-dummy fingers to
`CP_v1_golden.spice` as real tied-off instances (gate/S/D to the rail), NOT a count waiver —
2 pfet 5u/2u dummies (PMOS pair ends) + 2 nfet 5u/2u dummies (NMOS pair ends). Confirm exact
extracted form at stage (c).
