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

## Strapping method (worked out; the (e) recipe per nf device)
Do it IN the device child cell (device-local frame; `magic::gencell_makecell` returns the cell
without placing → no flatten shift). Layers: `metal2`, via `m2contact`/`via1` (m1↔m2).
Coords (pfet nf=10 5u L=2, local): S/D columns x=±2520 step 504 (11); gates x=±2268 step 504 (10).
Assign source=even cols {−2520,−1512,−504,504,1512,2520}, drain=odd {−2016,−1008,0,1008,2016}.
**Density collision (the catch):** gate metal1 tabs (y533–579) and S/D tabs (y487–498) are only
35 u apart (< M1.2a 46 u), so metal1 straps at the tab level collide. Avoid by **stacking rails
on metal2 clear of the device** with metal1 risers: source→metal2 rail at y≈730 (risers up from
source tabs, m2contact), drain→metal2 rail at y≈−730 (risers down), gate→metal2 rail at y≈900
(risers up from gate tabs). Risers at source-x vs gate-x are 252 u apart (> 46), no collision;
metal1 riser crossing under a metal2 rail is inter-layer, legal. Then label S/D/G/B ports.
**Status:** placement + method proven; the routing itself (rails+risers+vias per device ×6 types
+ inter-device + guard rings) is a large, iteration-heavy headless effort with real density DRC
friction — QUEUED for a focused/interactive session (see verification/report). Not a guess and not
a gate failure; the recipe above is the path.

## Phase 5.3 — 1kΩ resistor flavor (checked): `ppolyf_u_1k`, 1000 Ω/sq (rho 1000), minW=L=1µm.
R_SER 1k = 1 square; size W≥2µm for ~3.3mA switching current (→L=2µm), ~20–30µm² each, ~100µm² ×4.

## Strapping generator (`strap.tcl`) — electrical strap PROVEN, DRC wall found
`strap_device` (parameterized proc, device-local frame) straps a raw nf device: metal1
risers from S/D/gate tabs → stacked metal2 rails (source/drain/gate) via `m2contact`.
- **Electrical strapping WORKS:** extraction of the strapped pfet nf=10 combines all 10
  fingers to **1 gate net + 2 S/D rails** (the parallel W=50 device the golden wants).
- **DRC: 204 → 30** after via/metal sizing fixes (via1 52, metal1 enclose +12, metal2 56).
  Remaining **30 = M1.2a spacing in the gate/S-D contact band**: gate metal1 tabs sit ~54 u
  (x) / 35 u (y) from the S/D columns — diagonally clear in the bare device (85 u), but any
  strap metal1 or via pad added there breaks the 46 u rule. **guard=1 does NOT help** (also
  extracts 10 unstrapped fingers — the generator never straps S/D). So this congestion is
  universal to every nf device.
- **To clear it:** contact S/D and gates from OPPOSITE sides with via-at-tab + route all
  risers on metal2/metal3 (multi-layer), keeping metal1 minimal. That is dense custom
  routing best done with a canvas — **QUEUED for interactive layout**; the proc + coords are
  the starting point. This is the load-bearing wall for 5.1(e–g) and all of 5.2–5.4.

## Build stages (per packet, DRC=0 at each; render with lay2img.py)
(a) one device → (b) matched pair → (c) interdigitated array + dummies → (d) guard rings →
(e) routing → (f) labels/ports → (g) full verify_cp.sh (match uniquely vs golden).

## Golden dummies (settled Gate 1 + Greg): add the 4 end-dummy fingers to
`CP_v1_golden.spice` as real tied-off instances (gate/S/D to the rail), NOT a count waiver —
2 pfet 5u/2u dummies (PMOS pair ends) + 2 nfet 5u/2u dummies (NMOS pair ends). Confirm exact
extracted form at stage (c).
