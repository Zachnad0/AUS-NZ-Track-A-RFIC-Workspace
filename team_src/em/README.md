# Inductor EM extraction (Phase 6.2) — INSTALL QUEUED

**Status 2026-08-13:** zip extracted to `Downloads/openEMS_x64/openEMS/` — `openEMS.exe` runs
(`Usage: openEMS <FDTD_XML_FILE>`). No-Python-module path attempted but **blocked**: the HDF5
port post-processing needs `numpy`+`h5py`, and NEITHER is installed for Python 3.12 (and the
bundled `openems`/`csxcad` wheels are cp313/cp314). So a result needs an install either way —
the Python 3.13 + bundled cp313 wheels path below is the surest (uses `extract_inductor.py`
directly). L is already confirmed ~1.2 nH analytically (§4.1); this run only refines Q/SRF.
Note: the spiral FDTD may exceed the couple-minute compute cap — chunk or run it yourself.

`extract_inductor.py` reproduces the drawn `vco_inductor_v2.mag` metal5 geometry and
extracts L/Q/SRF via openEMS FDTD (lumped port PORT1↔PORT2). **Runs on Windows, not the
container** (repo + .mag are Windows-side).

## Install blocker (for Greg — I can't install per rule 1)
Bundled wheels in `Downloads/openEMS_x64_v0.0.36-93-g7b9cd51_msvc.zip` are **cp313 + cp314
only**; your Python is **3.12.10** — incompatible (a cp313 wheel needs CPython 3.13).

**PREFERRED (smaller install, 2026-08-13): numpy + h5py on your existing 3.12 — NO Python 3.13.**
The openEMS *Python module* (cp313) is only a convenience wrapper. The binary path needs neither
it nor 3.13: hand-write a CSX XML → `openEMS.exe <xml>` (extracted, runs) → it writes HDF5 field
dumps → post-process Z11 = V/I with numpy+h5py (both have cp312 wheels). So:
```
py -3.12 -m pip install numpy h5py
```
Then run `openEMS.exe` on the CSX XML (a `write_csx.py` generator + `post_z11.py` reader are the
remaining pieces to write — see extract_inductor.py for the geometry/port definitions to port
into raw XML; the bundled `matlab/AddLumpedPort.m` is the reference for the port probe boxes).
NOTE: the spiral FDTD may exceed the couple-minute compute cap — run it yourself / chunk it.

---
**Alt (surest but heavier): install Python 3.13, then use the bundled cp313 wheels.**
1. Install Python 3.13 (python.org). 2. Extract the zip to e.g. `C:\openEMS`. 3.:
```
py -3.13 -m pip install numpy matplotlib h5py
py -3.13 -m pip install "C:\openEMS\openEMS\python\csxcad-0.6.3-cp313-cp313-win_amd64.whl" "C:\openEMS\openEMS\python\openems-0.0.36-cp313-cp313-win_amd64.whl"
```
4. Add `C:\openEMS\openEMS` to PATH (so `openEMS.exe` is found by the module).
Then: `py -3.13 team_src\em\extract_inductor.py`.

Alt (no new Python) — try PyPI for a cp312 wheel: `py -3.12 -m pip install openEMS csxcad`
(uncertain a cp312 wheel exists; `py -3.12 -m pip index versions openems` to check).

## Before trusting Q/SRF
`extract_inductor.py` has PLACEHOLDER metal5 z-height/thickness (10 µm / 0.9 µm). Set them
from the gf180 layer/thickness table first. **L is stack-insensitive** (already confirmed
~1.2 nH analytically, §4.1); Q and SRF need the real stack. Per 6.3: if L nudges, accept-and-
replan (re-sim VCO, move VTUNE) over redraw — ISM is reachable at 1.2 nH.
