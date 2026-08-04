# DIV2_QUAD_v1 — debug state (2026-08-04)

**STATUS: WIP — does NOT divide cleanly yet.** The cell is built, netlist-clean,
and wired correctly device-by-device, but simulation is non-functional. This file
lets a fresh session resume cold without re-deriving. Do not treat DIV2_QUAD_v1 as
verified.

## What it is
CML ÷2 quadrature divider packaged as a subcircuit: 12-nfet CML core (2 master-slave
D-latches) + NMOS 10:1 bias mirror off `IBIAS` + 4× PMOS-input CML→CMOS rail-to-rail
output buffers (diff converter + inverter + 450 Ω on-chip series R) → I_P/I_N/Q_P/Q_N.
Design decisions (Greg, 2026-08-04): IBIAS = chip-level bias, external **240 µA**,
mirror **10:1** → **2.4 mA/tail** (4.8 mA core total); buffers CML→CMOS rail-to-rail
with **450 Ω** series isolation. See `pins.md`, `verification.md` §7.

## Files
- Cell:   `team_src/xschem/DIV2_QUAD_v1.sch` (45 FET + 8 R), symbol `DIV2_QUAD_v1.sym`
- TB:     `team_src/xschem/DIV2_QUAD_tb.sch` — 240 µA into IBIAS, rail-to-rail diff
  clock (T = 200 p = 5 GHz), pad load 300 fF + 50 Ω to gnd on each output.
- Generators (persistent, outside repo): `../_cp_work/gen_div2_quad.py`,
  `../_cp_work/gen_div2_quad_tb.py` (edit + re-run to regenerate the .sch/tb).

## Reproduce (headless, container `iic-osic-tools_xvnc`)
Netlist:
```
docker exec iic-osic-tools_xvnc bash -lc 'export PATH=/foss/tools/bin:/foss/tools/sak:$PATH; \
 source /foss/tools/sak/sak-pdk-script.sh gf180mcuD >/dev/null 2>&1; \
 cd /foss/designs/AUS-NZ-integration/team_src/xschem; \
 xschem -n -q -o /headless/.xschem/simulations DIV2_QUAD_tb.sch'
```
Failing sim run (5 GHz):
```
D=/headless/.xschem/simulations
sed "/^.tran/d" $D/DIV2_QUAD_tb.spice > /tmp/run5g.spice
cat >> /tmp/run5g.spice <<EOF
.ic v(x1.oi)=3.2 v(x1.oib)=0.6 v(x1.oq)=1.9 v(x1.oqb)=1.9
.control
tran 0.2p 6n uic
wrdata /tmp/div2_5g.txt v(i_p)-v(i_n) v(q_p)-v(q_n) v(i_p) v(q_p)
.endc
.end
EOF
cd $D; ngspice -b /tmp/run5g.spice
```
Internal nodes are hierarchical under the instance: `v(x1.oi)`, `v(x1.taila)`, etc.

## Symmetry break REQUIRED to get any motion
Without `.ic`, the CML sits in the perfectly-symmetric metastable state (idiff ≈ 1e-10)
and never starts. The `.ic` above (oi=3.2, oib=0.6) is what makes it move. Real
silicon starts on mismatch/noise; the cell still needs a defined startup story
(RST path or a deliberate small asymmetry).

## Measured (failing run, with the .ic)
| Quantity | Measured | Expected |
|---|---|---|
| idiff = v(oi)−v(oib) swing | **+2.9 / −0.56 V** (asymmetric) | clean symmetric ±swing |
| converter OC_ip swing | **1.09–1.91 V** | enough to fully switch the inverter |
| INVO_ip peak | **2.1 V** (not rail) | ~3.3 V |
| outputs I_P / Q_P | **tens of mV** | ~0.3 Vpp monitor (after 450/50 divider) |
| total supply, steady | **~2.8 mA** | **~18 mA** |
| IBIAS node | ~1.67 V | — |
(Ignore the ~−197 A spike at t=0 — it is the `uic` inrush charging the pad/node caps.)

## Root-cause read + debug order (do in THIS order)
1. **FIRST — measure the actual tail current.** ~2.8 mA total vs ~18 mA expected
   strongly implies the 10:1 mirror is **not delivering 2.4 mA/tail**. That single
   number gates everything else. Command:
   ```
   * add BEFORE .control/tran:
   .save @m.x1.xm_taila[id] @m.x1.xm_tailb[id] @m.x1.xm_bref[id]
   * then in .control after tran:
   print vecmax(abs(@m.x1.xm_taila[id])) vecmin(abs(@m.x1.xm_taila[id]))
   ```
   If tail ≪ 2.4 mA: check M_BREF (W = 4 u, L = 1 u) actually passes 240 µA and its
   VGS; check VDS headroom at TAILA (~0.46 V is marginal for a real tail sinking
   2.4 mA); likely fix is larger tail W (or nf), or lower R loads, or raise the ref.
2. **THEN re-center the CML with real tails.** Adjust R loads (300 Ω) and/or tail
   current so the single-ended common mode + swing match the ideal-tail probe
   operating point (`DIV2_CML_probe_tb`, which divided clean full-band). Confirm a
   clean **symmetric** idiff before touching buffers.
3. **THEN converter/inverter sizing.** PMOS-input diff pair (CM ~2.9 V) must drive
   OC far enough to fully flip the inverter to the rail. Resize NMOS mirror load
   (M_BN1/2), inverter (M_IP/M_IN), buffer tail (M_BT).
4. **Startup last.** Once biased, define the symmetry-break (RST path or a small
   deliberate asymmetry); `uic` sims still need the `.ic`.

Do not re-verify ÷2 / quadrature at 4.11/5.0/6.37 GHz until step 1's tail-current
number is right — the loading claim in `verification.md` §7 (ideal tails) will not
hold until the real mirror delivers the current.
