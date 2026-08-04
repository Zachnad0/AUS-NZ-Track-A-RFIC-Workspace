# Resume notes — updated 2026-08-05 (second pause)

Session paused again for a machine shutdown (Greg closes Docker Desktop, which takes
the container + the running KLayout DRC down with it). State captured to resume cold.

## Repo state (pushed — safe off this machine)
- **`origin/main` = `origin/integration` = `3ace987`** (both pushed 2026-08-05, with
  Greg's per-branch OK). main now carries Zach's VCO + CP/PFD/DIV2 + docs + **info.yaml
  and lvs/lvs_config.json** at the submission paths. Zach approved the integration→main
  merge; the push is done.
- Any commit made *after* `3ace987` (this notes update + verification.md D_FF_v1 fix)
  is **local-only** unless a later push is recorded here.

## Aug-6 DRC dry-run — GDS + Magic DRC good, KLayout DRC inconclusive
Run tag `RUN_2026-08-04_20-23-53` (workshop-slot `chip_top`).
- **GDS confirmed by file:** `…/57-klayout-streamout/chip_top.gds` = **27,212,418 bytes**.
- **Magic DRC (stage 67) COMPLETED = 0 errors** — read from
  `67-magic-drc/state_out.json` (`"magic__drc_error__count": 0`) and
  `67-magic-drc/reports/drc.magic.rpt` (chip_top, no violations). This is a real,
  read-from-file result, not inferred.
- Routing DRC 0, KLayout antenna 0, KLayout density 0, XOR clean (all earlier).
- **KLayout DRC (stage 68): INCONCLUSIVE.** It was resumed this session (see below)
  and was still executing DRC rules (CONTACT derivations, ~DF.19) when the shutdown
  killed it. No report written, no count. **Do not report a KLayout DRC pass.**

### How KLayout DRC was resumed (repeat next session — no rebuild needed)
LibreLane 3.0.3 resumes from existing stage outputs. The DRC-only resume that skips
the ~40-min synth/PnR/streamout rebuild:
```
docker exec iic-osic-tools_xvnc bash -lc 'export PATH=/foss/tools/bin:/foss/tools/sak:$PATH; \
 cd /foss/designs/AUS-NZ-integration; \
 librelane librelane/slots/slot_workshop.yaml librelane/config.yaml \
   --pdk gf180mcuD --pdk-root /foss/designs/AUS-NZ-integration/gf180mcu --manual-pdk \
   --scl gf180mcu_fd_sc_mcu7t5v0 \
   --last-run --from KLayout.DRC --to KLayout.DRC \
   --with-initial-state /foss/designs/AUS-NZ-integration/librelane/runs/RUN_2026-08-04_20-23-53/67-magic-drc/state_out.json'
```
Verified: this logs "Using existing run at 'RUN_2026-08-04_20-23-53'" and reuses the
run dir (no new RUN_, no rebuild). When it finishes, read the count from
`68-klayout-drc/state_out.json` (`klayout__drc_error__count`) and
`68-klayout-drc/reports/drc.klayout.*`. KLayout DRC on the 85 MB padframe GDS takes
10+ min (deep run_mode).

## D_FF_v1 duplicate-iopin claim — DISPROVEN, do not chase
Zach asked to delete duplicate VDD/VSS iopins in D_FF_v1. **There are none.** Verified:
1 VDD iopin + 1 VSS iopin in `D_FF_v1.sch`, 6 pins in `D_FF_v1.sym`, matched 6/6, no
netlist warning, identical across all four origin branches, never modified since
`413a1db`, and not instantiated anywhere in the repo. The old "5/6 duplicate" note was
wrong (likely confused with `D_FF_RST_v1`). Corrected in `verification.md` §1.4/§5.
**Deleting an iopin would remove a required port — do not do it.** If Zach still sees a
dup, he has a different local copy; confirm which before any edit.

## DIV2 tail-current measurement — the ngspice gotcha (start here next session)
Goal: measure the delivered CML tail current (design target 2.4 mA/tail; prior session
saw ~2.8 mA total supply vs ~18 mA expected → mirror suspected under-delivering).
**Gotcha found:** `nfet_03v3` is a **subcircuit wrapper** (X-prefixed instance
`XM_TAILA`, primitive buried in nested PDK subckts), so `@m.x1.xm_taila[id]` is
**invalid** — that is the wall both sessions hit. **Measure through the 300 Ω loads
instead** (all tail current returns through the two latch loads):
```
* in a .control block after: tran 0.2p 6n uic, with .ic v(x1.oi)=3.2 v(x1.oib)=0.6 v(x1.oq)=1.9 v(x1.oqb)=1.9
let itaila=(v(vdd)-v(x1.oi))/300 + (v(vdd)-v(x1.oib))/300
let itailb=(v(vdd)-v(x1.oq))/300 + (v(vdd)-v(x1.oqb))/300
meas tran itaila_avg avg itaila from=4n to=6n
meas tran itailb_avg avg itailb from=4n to=6n
```
Re-netlist first (container-only sim dir is wiped on restart):
`xschem -n -q -o /headless/.xschem/simulations DIV2_QUAD_tb.sch`. Full DIV2 debug plan
in `docs/div2-debug.md`. This measurement gates all other DIV2 debug — do it first.

## Artifacts on the Windows bind mount (survive shutdown)
- `…\RUN_2026-08-04_20-23-53\57-klayout-streamout\chip_top.gds` (27 MB)
- `…\RUN_2026-08-04_20-23-53\67-magic-drc\reports\drc.magic.rpt` (Magic DRC = 0)
- `C:\Users\grego\eda\designs\_runA_logs\runA.log` and `runA_resume_klayoutdrc.log`
- Generators: `…\_cp_work\gen_div2_quad.py`, `gen_div2_quad_tb.py`
Container-only (die, regenerable): `/headless/.xschem/simulations/*`, `/tmp/*.spice`.
