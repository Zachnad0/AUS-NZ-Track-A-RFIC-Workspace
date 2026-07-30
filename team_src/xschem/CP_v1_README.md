# CP_v1 — Charge Pump (GF180 3.3V), Team A1 AUS/NZ Track A RFIC

Single-ended **switched current-steering charge pump** for the PLL loop.
Cell: `CP_v1.sch` / `CP_v1.sym`. Testbenches: `CP_dc_tb.sch`, `CP_tran_tb.sch`.

## Topology
- **PMOS mirror** `M_PREF` (diode) → `M_PSRC` sources `I_CP` into `CP_OUT` when `UP=1`.
- **NMOS mirror** `M_NREF` (diode) → `M_NSNK` sinks `I_CP` from `CP_OUT` when `DOWN=1`.
- **Drain switches** `M_PSW` (pmos, gated by `UP_B`) and `M_NSW` (nmos, gated by `DOWN`).
  Both off ⇒ `CP_OUT` high-Z.
- Internal **inverter** `M_INVP`/`M_INVN` generates `UP_B` (active-low) for the pmos switch.
- `I_CP` set by two **ideal 50 µA references** (`I_PREF`, `I_NREF`).

> **`I_CP = 50 µA` is a PROVISIONAL PLACEHOLDER.** Final value is a loop-design
> decision to be made with the loop filter (see Saima). In silicon the ideal
> references become a mirrored bias from the PLL bias generator — there is no
> `IBIAS` pin in v1.

Pins: `UP`, `DOWN` (in), `CP_OUT` (out), `VDD`, `VSS` (inout). Devices: `nfet_03v3` / `pfet_03v3` only.

## Final device sizing (Round 4 of 6)
| Device | role | W | L |
|---|---|---|---|
| M_PREF / M_PSRC | pmos mirror | 50u | 2u |
| M_PSW | pmos switch | 50u | 0.3u |
| M_NREF / M_NSNK | nmos mirror | 10u | 2u |
| M_NSW | nmos switch | 10u | 0.3u |
| M_INVP / M_INVN | UP inverter | 2u / 1u | 0.3u |

## Results (typical corner, 27 °C, I_CP = 50 µA, VDD = 3.3 V)
**DC** (`CP_dc_tb`):
- Compliance window (|I_up−I_dn|/I_CP < 5%): **0.32 V … 3.00 V** (2.68 V, 81% of rail).
- Flat band (<1% mismatch): **0.82 V … 2.08 V** (1.26 V).
- Best mismatch **0.001%** @ 1.50 V; mid-rail (1.65 V) mismatch **0.24%**.
- Off-state leakage: **< 7 pA** across 0–3.3 V.

**Transient** (`CP_tran_tb`, 10 pF load, 1 ns pulses):
- High-Z hold current ≈ **1 pA** (both switches off).
- Steering time to 90% I_CP: **0.155 ns** (UP), **0.024 ns** (DOWN) — both ≪ 1 ns.
- Charge/pulse (settled): UP **+199 fC**, DOWN **−89 fC**.
- **Net charge injection per matched UP+DOWN pair: +110 fC** (dominant v1 non-ideality).

## Known v1 limitations / v2 candidates
1. **Switching charge injection & UP/DOWN asymmetry** (net +110 fC/pair). Driven by
   the large pmos switch vs small nmos switch and by PMID/NMID swinging to the rails
   during hold (charge sharing when a switch closes). → v2: current-steering with
   dump devices that keep PMID/NMID near CP_OUT, dummy/complementary switches, or a
   unity-gain amp to hold the dump nodes.
2. **UP path has one inverter of extra delay vs DOWN** → small static skew. → v2:
   matched complementary drive.
3. **Finite mirror output resistance** sets the compliance edges. → v2: cascode mirrors.

## Reproduce (headless, from PowerShell via docker exec)
```
docker exec iic-osic-tools_xvnc bash /foss/designs/_cp_work/netlist.sh CP_dc_tb
docker exec iic-osic-tools_xvnc bash /foss/designs/_cp_work/goDC.sh          # DC + analysis
docker exec iic-osic-tools_xvnc bash /foss/designs/_cp_work/netlist.sh CP_tran_tb
docker exec iic-osic-tools_xvnc bash /foss/designs/_cp_work/sim.sh CP_tran_tb
docker exec iic-osic-tools_xvnc python /foss/designs/_cp_work/analyze_tran.py
```
Netlists/raw land in `/headless/.xschem/simulations/`; helper scripts and data live
in `/foss/designs/_cp_work/` (= `C:\Users\grego\eda\designs\_cp_work`, outside the repo).

## Open in xschem GUI (noVNC), if you want to look at it
Open Greg's usual noVNC desktop, then in a terminal there:
```
sak-pdk gf180mcuD
cd /foss/designs/AUS-NZ-CP-sandbox/team_src/xschem
xschem CP_v1.sch      # or CP_dc_tb.sch / CP_tran_tb.sch
```
