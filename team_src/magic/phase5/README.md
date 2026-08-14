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

## Phase 5.2 IBIAS layout — progress (2026-08-14, `ib_block.tcl` generator library)
Composable strapped-leg generator built on the CP strap procs. Reusable: `place_nfet`
(gencell, distinct name), `nfet_leg` (strap an already-flattened nf-device, UNLABELED
rails), `via_m2m3`. Pattern: place ALL devices (distinct names) -> `flatten` ONCE ->
strap (the mtest pattern; strapping before flatten or reusing a device name trips a Tk
`.params.title.ient` gencell-dialog error headless).
- **CP2 `ib_n24`** (`ib_nleg.tcl`): single strapped nfet **nf=24** W=4 L=2 (96 um, under
  the 200 um model-bin wall). Magic DRC 0, **KLayout DRC 0**, netgen 24 fingers -> match
  uniquely m=24, 3 ports. De-risks the widest device. Wide devices need a **ROW of
  substrate taps** at column midpoints (5040-unit spacing) so every finger is within 20 um
  of a tap (DF.14_LV, KLayout-only) — one edge tap is not enough past ~13 um half-width.
- **CP3a `ib_nmir4`** (`ib_nmir.tcl`): NMOS mirror row MN0:MN1:MN2:MNB = **24:5:24:2** (the
  ratio-critical set). All gate=NB, all source=VSS merged by continuous M2 bars (NB@y960,
  VSS@y-600) bridging the per-leg rails; MN0 diode drain risered up to NB. Magic DRC 0,
  **KLayout DRC 0**, netgen 55 fingers -> 4 devices -> match uniquely, 5 ports.
- **Remaining (deferred, large):** NMOS cascodes (MNC0/1/2, nfet L=1 — verify the L=1 S/D
  pitch first), then the PMOS side. **PMOS is a NEW device geometry:** pfet W=16 has a TALL
  16 um S/D contact strip (pdiffc y143..3317 at 20 u/um) and sits in NWELL with n+ taps —
  the W=4 nfet vertical strap constants do NOT carry over; needs its own y-geometry. And
  W=16 m=24 = 384 um > 200 um model wall -> split each wide pfet leg into 2x nf=12 (192 um)
  in parallel (netgen should combine to m=24). Then 2-row cascode assembly + inter-band
  routing (NB/PB/PA/VBCPD/IBIAS) + XCDEC decap + ports + verify_cp.sh.

### Two hard-won gotchas from CP3a (add to the deck-gotchas list)
- **Label each net ONCE at its port.** A rail proc that labels every per-leg rail with the
  shared net name (e.g. VSS on 4 source rails) leaves MULTIPLE same-name labels; `port make`
  over a region touching two of them fails silently -> netgen "(no pin, node is NB)" port
  error while the netlist still "matches uniquely with port errors". Fix: paint rails
  UNLABELED, merge with a continuous bar, and `label`+`port make` once at a clean spot.
- **A `label` over pwell can stick to pwell, not the metal2 under the box** ("Moving label
  X from space to pwell"), even after `paint metal2` there — happened only for a small
  device's drain. Route the label to a metal2 pad in CLEAR FIELD (y>700, above the pwell
  top) and it sticks to metal2 (as the NB bar at y960 did). This is why VBCPD gets a riser
  to a pad above the pwell.

## Phase 5.3 — 1kΩ resistor flavor (checked): `ppolyf_u_1k`, 1000 Ω/sq (rho 1000), minW=L=1µm.
R_SER 1k = 1 square; size W≥2µm for ~3.3mA switching current (→L=2µm), ~20–30µm² each, ~100µm² ×4.

## Strapping generator (`strap.tcl`) — SOLVED (DRC 0 + LVS combine). Wall broken.
**The 30 M1.2a "wall" was a wrong-topology artifact, not a density limit.** Fix (2026-08-13):
generate the device with **`topc=0 botc=0`** (no gate metal1 contacts → metal1 count 62→22),
strap **gates on a polysilicon rail** (one polycontact→via1→metal2 at the far end, over field),
**S/D on metal2** (source top-contacted, drain bottom-contacted). metal1(S/D)-vs-poly(gate) is
inter-layer, so the congested band is empty by construction. Verified on pfet nf=10 w=5 L=2:
**STRAP_DRC=0**, netgen **Number of devices 1|1, match uniquely, W=50**. Closes the deferred
Phase 1 routed-strapping check. `strap_device`/`gate_polyrail` procs are reusable per block;
gf180 minimums hoisted to constants (via1 52, metal1 encl +12, metal2 56, riser +12). Key
geometry (pfet nf=10 5u L2, device-local): S/D cols ±2520 step 504, tabs y±492; poly rail
must sit ABOVE pdiff (y>500) or it forms a spurious FET; nwell ±2642/±630.

## Progress (2026-08-13) — all structural methods PROVEN, DRC 0 + LVS
- **Single strapped device** (`strap.tcl` procs): pfet nf=10 → W=50, DRC 0, match uniquely.
- **Interleaved PMOS mirror** (`cp_pmos.tcl`): M_PREF+M_PSRC nf=20 common-centroid ABBA, split
  drains VGP(M2)/PMID(M3), gate poly-rail, vertical M2 VGP unify. **DRC 0; netgen 20→2 merged,
  match uniquely** vs `cp_pmos_golden.spice`.
- **Interleaved NMOS mirror** (`cp_nmos.tcl`): M_NREF+M_NSNK nf=4, split drains VGN(M2)/NMID(M3).
  **DRC 0; netgen 4→2 merged, match uniquely** vs `cp_nmos_golden.spice`.
- (`strap.tcl` is a clean proc library; constants incl via1 52 / via2 56 hoisted.)
Remaining to the gate: strap the switches/inverter/dummies (same procs), place all in the two-band
floorplan (flatten-into-CP with tracked offset OR port-make + instance), inter-device routing
(PMID→M_PSW.src, CP_OUT, UP_B, VGN, NMID, VDD/VSS rails), group guard rings (= bulk ties), 7 ports
(`port make`), `verify_cp.sh` exit 0. Mechanical assembly on the proven methods.

## Assembly progress (2026-08-13, `cp_full.tcl`) — 6/8 devices DRC 0 in the floorplan
Placement math: device at `box(FX-hw, FY-hh)` + gencell then flatten => geometry at `CP=local+(FX,FY)`;
strap at CP coords (NMOS band `yn` helper adds YN=-3600). Done, DRC 0:
- **PMOS mirror** nf=20 @ (0,0), **NMOS mirror** nf=4 @ (0,-3600) — both split-drain strapped.
- **M_PSW** @ (7000,0): source->PMID, drain->CP_OUT, gate->UP_B. **M_NSW** @ (7000,-3600):
  source->NMID, drain->CP_OUT, gate->DOWN. **CPFULL_DRC=0.**
DRC traps paid: gate_polyrail contact `cx` must be LEFT of `px2` (else the M2 rail runs backwards);
single-column rails need >= M2.3 min area (extend them); gate contact >=46u clear of nearest S/D col.

**Inverters (M_INVP 2u, M_INVN 1u) need a tiny-device gate strap — NOT the poly rail.** Their
W is too small: a poly rail within the well trips PL.5a (poly-to-diffusion <20) and CO.7, and the
W=1u INVN well can't fit a 74u-tall poly-contact rail at all. Approach: extend the gate poly as a
**vertical stub UP past the well** to a widened polycontact in clear field, then via1->metal2 to UP.
S/D straps (strap_col at cols ±82) are fine — vias land at the far rail, clear of the gate.

## Remaining to the gate (mechanical): inverters (stub strap) + 4 dummies (tied-off, add to golden) +
## inter-device routing (PMID mirror<->PSW, CP_OUT PSW<->NSW, NMID mirror<->NSW, UP_B inv<->PSW,
## VDD/VSS unify) + group guard rings (=bulk ties) + 7 ports (`port make`) + verify_cp.sh exit 0.

## Remaining CP build (superseded by the progress above)
(c) **Interleaved mirror pair**: one `pfet nf=20` (topc=0), gate poly-rail→VGP, source→VDD,
    **split the 10 drain columns**: 5→VGP (= gate net, M_PREF) / 5→PMID (M_PSRC), common-centroid.
    Two drain rails interleaved ⇒ multi-layer: VGP-drains on metal2, PMID-drains on **metal3**
    (via2/`m3contact`) — the split-drain analog of the source/drain layer split. Same for the
    NMOS pair (nf=4). (d) group guard rings (n+/VDD around PMOS nwell, p+/VSS around NMOS) —
    these also provide the bulk ties dropped from the single-device verify. (e) inter-device
    routing VGP/VGN/PMID/NMID/CP_OUT/UP_B. (f) port labels UP/DOWN/CP_OUT/VDD/VSS/VGP/VGN via
    `port make`. (g) `verify_cp.sh` → match uniquely, exit 0. Add the 4 end-dummies to
    `CP_v1_golden.spice` as tied-off instances at (c).

## (historical) Strapping generator — electrical strap PROVEN, DRC wall found
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
- **Refined solution (specified, needs interactive execution):** opposite-side contacting
  alone is insufficient — the BARE S/D top tabs sit ~7 u from gate top vias. The clean recipe:
  (1) **gate = polysilicon rail** connecting the gate poly fingers directly (all one net VGP;
  poly R is fine for a gate), with ONE polycontact→metal via at a clear spot — no metal1 vias
  in the congested band; (2) **S/D multi-layer from the bottom**: source via1→metal2 rail
  (y −720), drain via1+via2→metal3 rail (y −900), so the two interleaved S/D nets ride
  different layers and don't collide. This is dense custom routing best done with a canvas —
  **QUEUED for interactive layout**; `strap.tcl` (electrical strap proven) + the column coords
  are the starting point. This is the load-bearing wall for 5.1(e–g) and all of 5.2–5.4, and
  is why the full routed GDS is an interactive multi-session effort, not a headless one.

## Build stages (per packet, DRC=0 at each; render with lay2img.py)
(a) one device → (b) matched pair → (c) interdigitated array + dummies → (d) guard rings →
(e) routing → (f) labels/ports → (g) full verify_cp.sh (match uniquely vs golden).

## Golden dummies (settled Gate 1 + Greg): add the 4 end-dummy fingers to
`CP_v1_golden.spice` as real tied-off instances (gate/S/D to the rail), NOT a count waiver —
2 pfet 5u/2u dummies (PMOS pair ends) + 2 nfet 5u/2u dummies (NMOS pair ends). Confirm exact
extracted form at stage (c).
