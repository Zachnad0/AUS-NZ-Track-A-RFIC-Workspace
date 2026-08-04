# Resume notes — session pause 2026-08-04

Session paused for a machine shutdown (Greg closes Docker Desktop, which takes the
running container + Run A down with it). State captured so next session resumes cold.

## Run A (Aug-6 DRC dry-run) — killed mid-Magic-DRC
- The workshop-slot LibreLane flow (`chip_top`, DESIGN_NAME) was **killed while
  running stage 67 `magic-drc`** by the Docker shutdown. Run tag
  `RUN_2026-08-04_20-23-53`.
- **GDS already streamed out and confirmed by file** (survives on the Windows bind
  mount, not container-only):
  `librelane/runs/RUN_2026-08-04_20-23-53/57-klayout-streamout/chip_top.gds`
  = **27,212,418 bytes**.
- **Clean so far:** routing DRC 0 (`route__drc_errors: 0`, 23→5→1→0), KLayout
  antenna 0, KLayout density 0, XOR clean.
- **NOT read:** signoff **Magic DRC + KLayout DRC** never completed — the Magic DRC
  report `67-magic-drc/reports/drc.magic.rpt` was still **0 bytes** at pause. So the
  final geometric DRC count is **unknown / inconclusive**. Do NOT report a DRC pass;
  it was never read.
- Run A log (survives): `/foss/designs/_runA_logs/runA.log` (=
  `C:\Users\grego\eda\designs\_runA_logs\runA.log`, ~5.6 MB).
- Container-only (die with the container, regenerable, not needed): the xschem sim
  netlists under `/headless/.xschem/simulations/` and `/tmp/*.spice`.

### Relaunch Run A (from PowerShell, container must be up)
```
docker exec iic-osic-tools_xvnc bash -lc 'export PATH=/foss/tools/bin:/foss/tools/sak:$PATH; \
 cd /foss/designs/AUS-NZ-integration; \
 SLOT=workshop librelane librelane/slots/slot_workshop.yaml librelane/config.yaml \
   --save-views-to /foss/designs/AUS-NZ-integration/final \
   --pdk gf180mcuD --pdk-root /foss/designs/AUS-NZ-integration/gf180mcu \
   --manual-pdk --scl gf180mcu_fd_sc_mcu7t5v0'
```
(The `--scl gf180mcu_fd_sc_mcu7t5v0` override is mandatory at LibreLane 3.0.3, else it
injects sg13g2 and dies at config load.) To reach the DRC number faster next time,
consider running to the Magic/KLayout DRC steps and reading
`*-magic-drc/reports/drc.magic.rpt` + the KLayout DRC report/metric.

## FIRST action next session — DIV2 tail current
Before anything else on DIV2_QUAD_v1: **measure the actual CML tail current.**
Simulation drew **~2.8 mA steady total vs ~18 mA expected** — that gap most likely
means the 10:1 NMOS mirror is **not delivering 2.4 mA/tail**, which would explain
both the asymmetric CML swing (idiff +2.9/−0.56 V) and the non-switching output
buffers. This number gates all other DIV2 debug. Method (add before `.control`):
```
.save @m.x1.xm_taila[id] @m.x1.xm_tailb[id] @m.x1.xm_bref[id]
* then, after tran, in .control:
print vecmax(abs(@m.x1.xm_taila[id])) vecmin(abs(@m.x1.xm_taila[id]))
```
Full DIV2 debug state, sim commands, `.ic` symmetry-break values, and the ordered
debug plan are in **`docs/div2-debug.md`**. Do not re-verify ÷2/quadrature until the
tail current is correct.

## Repo state at pause
- Branch `integration` = `origin/integration` = `cde74bb` (pushed). Working tree
  clean before this file.
- Local `main` is fast-forwarded to `cde74bb` region (27+ ahead of `origin/main`,
  **unpushed** — submission harvests `main`; that push is Greg's Zach conversation).
- Unsent drafts in scratchpad (session-temp, may not persist): Zach message,
  issue-#143 comment (DRC line still a fill-in). If gone, regenerate from
  `tracking.md` §2 + this file.
