# Manual layout flow — Magic draw + DRC + extract + netgen LVS

Flow for the Aug-14 custom-cell layouts (CP_v1 + PFD chain). Chosen over LibreLane
because our cells are custom transistor-level (not gf180 std cells) and CP/VCO need
the manual flow regardless. **Verified end-to-end 2026-08-05** on the gf180 std-cell
inverter `gf180mcu_fd_sc_mcu7t5v0__inv_1`: DRC = 0, extract OK, **netgen LVS
"Circuits match uniquely."**

## Environment (every step)
```
docker exec iic-osic-tools_xvnc bash -lc 'export PATH=/foss/tools/bin:/foss/tools/sak:$PATH; \
 source /foss/tools/sak/sak-pdk-script.sh gf180mcuD >/dev/null 2>&1; ...'
PDK=/foss/designs/AUS-NZ-integration/gf180mcu/gf180mcuD
RC=$PDK/libs.tech/magic/gf180mcuD.magicrc
SETUP=$PDK/libs.tech/netgen/gf180mcuD_setup.tcl
```

## Step 1 — DRAW the layout (interactive, Magic GUI on noVNC)
**This step is a GUI task** — placing/routing a DRC-clean full-custom cell needs the
visual canvas; it cannot be done blind headless. Draw the cell in Magic (device
generators: `gf180mcu::nfet_03v3`, `gf180mcu::pfet_03v3` via the Devices menu),
label ports (A, Y, VDD, VSS for NOT_v1), save as `team_src/magic/<cell>.mag`.
The headless agent runs Steps 2-4 (all verifiable) and reports pass/fail.

## Step 2 — schematic reference netlist (LVS source of truth)
```
cd team_src/xschem
xschem -n -q -o /headless/.xschem/simulations <cell>.sch
# -> /headless/.xschem/simulations/<cell>.spice   (the characterized design)
```
Note: a bare .sch netlists flat with *.ipin markers. For netgen, compare against the
cell subckt; confirm the subckt name matches the .mag cellname when we do the first
real custom cell.

## Step 3 — DRC + extract (Magic headless) — VERIFIED
Write a tcl script and run `magic -dnull -noconsole -rcfile $RC script.tcl`:
```
load <path-to>/<cell>            ;# no .mag extension
drc euclidean on
drc check
puts "DRC_COUNT [drc list count total]"   ;# expect 0
extract all
ext2spice lvs
ext2spice -o /tmp/<cell>_ext.spice
quit -noprompt
```
Read `DRC_COUNT` from stdout (0 = clean) and confirm `/tmp/<cell>_ext.spice` exists
with the expected `.subckt` + devices.

## Step 4 — netgen LVS (layout vs schematic) — VERIFIED
```
netgen -batch lvs "/tmp/<cell>_ext.spice <cell>" "<schematic>.spice <cell>" \
  "$SETUP" /tmp/<cell>_lvs.out
grep -iE "Circuits match|do not match" /tmp/<cell>_lvs.out
```
PASS = "Circuits match uniquely." Anything else → read the report, do not call it clean.

## Proven transcript (std-cell inv_1, 2026-08-05)
- `drc list count total` = **0**
- extract → `.subckt gf180mcu_fd_sc_mcu7t5v0__inv_1 I ZN VDD VNW VPW VSS` (2 FETs)
- netgen → **"Circuits match uniquely."**

## First custom cell target: NOT_v1 (inverter, nfet+pfet W=1u L=0.28u, ports A/Y/VDD/VSS)
Reference netlist already extracted: `XM2 Y A VSS VSS nfet_03v3 ...`,
`XM4 Y A VDD VDD pfet_03v3 ...`. Draw in GUI (Step 1), then Steps 2-4 verify it.
Do NOT batch the other leaf cells until NOT_v1 is DRC+LVS clean end to end.
