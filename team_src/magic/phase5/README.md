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
guard=0 arrays are DRC-clean, so this is feasible. Settled before array topology.

**Generalizes (applies to IBIAS 5.2 too):** the rule is not "always guard 0" — it is *only
matched pairs need the manual group ring*. Any SINGLE multi-finger device (e.g. an IBIAS
mirror leg drawn as one `m`-unit device, or the CP switches/inverter which have no match)
may keep `guard=1` if convenient — its own ring is fine. Reserve guard=0 + group ring for
the interdigitated matched pairs.

## Progress + the real cost of (e) (2026-08-12, file-read)
- **Device geometry** (`dev_geom.tcl`, units 200/µm): pmir(nf10 5u L2) 5284×1356, psw(nf10 L0.3)
  1884, invp 408, pdum 748; nmir(nf2 5u L2) 1128, nsw 448, invn 284, ndum 624.
- **(b) PMOS matched pair** (MPREF+MPSRC adjacent, guard=0, flattened): **DRC 0**.
- **(b,c) all 8 devices + 4 dummies placed** in two bands (`place_cp.tcl`): abutting → 122 DRC
  (diffusion/contact/misrecognized-device at boundaries); **spaced by gap G=400 (2µm) → 70 DRC,
  all Metal1 min-area (M1.3) + spacing (M1.2a)** on the bare, unrouted S/D contact tabs. No
  device-level errors. These clear once routing straps merge the tabs.
- **THE CRUX for (e):** the generator does NOT strap nf devices — a `pfet nf=10` is 11
  shared-diffusion columns of bare contact tabs (widest metal1 = 46 u = 0.23µm; no strap rails),
  electrically a finger CHAIN, not a parallel W=50 device. Each device needs designer alternate-
  column strapping (source columns → metal2 rail_S via M1-M2 vias, drain columns → rail_D, gates →
  gate rail) to become the parallel device the golden expects (netgen then sums to W=50). S/D
  columns are at device-local x = −2520..+2520 step 504 (11 cols); even idx = source, odd = drain
  by our choice. Best done IN the child cell (device-local frame, no flatten shift) + port labels,
  then place+abut at top. This is the load-bearing effort of 5.1 and repeats for every nf device
  in 5.2/5.3. Post-flatten coords otherwise require extraction (`a_X_Y#` names) per net.

## Build stages (per packet, DRC=0 at each; render with lay2img.py)
(a) one device → (b) matched pair → (c) interdigitated array + dummies → (d) guard rings →
(e) routing → (f) labels/ports → (g) full verify_cp.sh (match uniquely vs golden).

## Golden dummies (settled Gate 1 + Greg): add the 4 end-dummy fingers to
`CP_v1_golden.spice` as real tied-off instances (gate/S/D to the rail), NOT a count waiver —
2 pfet 5u/2u dummies (PMOS pair ends) + 2 nfet 5u/2u dummies (NMOS pair ends). Confirm exact
extracted form at stage (c).
