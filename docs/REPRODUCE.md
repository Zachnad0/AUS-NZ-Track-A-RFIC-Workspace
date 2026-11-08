# Reproducing A01 from a fresh clone

**Team A01 · AUS/NZ Track A RFIC · GF180MCU (gf180mcuD)** · written 2026-11-08 against `3b74fd5`

One recipe, top to bottom: set up the environment, rebuild `gds/chip_top.gds` from the
committed block GDS and show it XORs to zero, run every signoff gate, then re-run the test-plan
simulations. Each step lists its expected result and runtime.

Every step is tagged:

- **[checked 11-08]**: run exactly as written from a fresh clone of `3b74fd5`, in a new container,
  on 2026-11-08. The measured result is shown. The check ran each fenced block non-interactively
  in a detached container (`docker run -d ... sleep`, then `docker exec`) instead of the
  interactive `docker run -it`, with the same image, mount and entrypoint.
- **[recorded]**: the command is the one the team ran. The expected result and runtime come from
  the cited run and were **not** repeated in the 11-08 fresh-clone check.

Runtimes are wall clock on a 32-core box, with every job capped at 2 threads and run one at a
time.

`docs/reproducing-docker.md` and `docs/reproducing-native.md` describe the upstream workshop
LibreLane template (`final/`, `make clone-pdk`). They do **not** build this chip; use this file
instead.

## 0. Read first: the repo path is fixed

The build, sim and abstract files hard-code **`/foss/designs/AUS-NZ-integration`**. That path
appears in `chip_merge.py`, `route_chip.py`, `landing_check.py`, `chip_top.abstract`, every
`signoff/sim/*/run_*.sh` and most `.spice` decks. Inside the container, the clone **must** sit at
exactly that path. A clone anywhere else reads, and can overwrite, whatever is at that path.

## 1. Environment

| Item | Version |
|---|---|
| Container | `hpretl/iic-osic-tools` **2026.05**, digest `sha256:8d846d760c47d35f961871b7e958bb03fe7a0bef4cef0d9177721d0a3535eba1` |
| PDK | `gf180mcuD` at `/foss/pdks`, ciel `gf180mcu` version `7b70722e33c03fcb5dabcf4d479fb0822d9251c9`; magic tech header `1.0.575-2-g7b70722` |
| Tools in that image | magic 8.3.642, netgen 1.5.319, KLayout 0.30.8, ngspice-46, Python 3.12.3 |
| Organizer LVS runner | `d-m-bailey/extra_be_checks`, branch `chipathon2025`, commit `7d1f5efb270003208956e764765f403b755281d7` (2025-11-28) |

### 1.1 Clone and start the container [checked 11-08]

On the host:

```bash
git clone https://github.com/Zachnad0/AUS-NZ-Track-A-RFIC-Workspace AUS-NZ-integration
git -C AUS-NZ-integration checkout main
docker pull hpretl/iic-osic-tools@sha256:8d846d760c47d35f961871b7e958bb03fe7a0bef4cef0d9177721d0a3535eba1
docker run -it --rm -v "$PWD/AUS-NZ-integration:/foss/designs/AUS-NZ-integration" --entrypoint bash hpretl/iic-osic-tools@sha256:8d846d760c47d35f961871b7e958bb03fe7a0bef4cef0d9177721d0a3535eba1
```

`.gitattributes` pins `*.sh`, `*.tcl` and `*.spice` to LF and `*.gds` to binary, so a Windows
checkout with `core.autocrlf=true` is safe.

### 1.2 Shell setup, in every container shell [checked 11-08]

```bash
source /foss/tools/sak/sak-pdk-script.sh gf180mcuD
export PDK=gf180mcuD PDK_ROOT=/foss/pdks OMP_NUM_THREADS=2
export PATH=/foss/tools/bin:/foss/tools/sak:/foss/tools/klayout:$PATH
export PYTHONPATH=/foss/tools/klayout/pymod:$PYTHONPATH
R=/foss/designs/AUS-NZ-integration; cd $R
echo $PDK        # must print gf180mcuD
```

The image's default `PDK` is `ihp-sg13g2`. If `$PDK` is not `gf180mcuD`, `verify_cp.sh` loads
IHP netgen rules and its LVS results are meaningless.

### 1.3 The two tech patches

Neither patch is applied to a PDK or runner original, and no tech file is committed. Both are
one-hunk diffs in `signoff/lvs/tech_patches/`. `README.md` there gives the full story.

**`varactor_comp.diff`** (writer side: COMP under the 42 varactor gates). Nothing to do by hand.
`team_src/magic/phase5/write_vco_gds.sh` copies the PDK's magic tech into its output directory,
patches that copy, and refuses to write GDS if the patch is missing (step 2.1).

**`rm5.diff`** (reader side: the inductor's two `tm11k`). This applies to a throwaway copy of
the organizer runner. **[recorded]**: the team's runner copies were made this way. The clone and
patch commands were not re-run on 11-08.

```bash
git clone -b chipathon2025 https://github.com/d-m-bailey/extra_be_checks /tmp/ebc_stock
git -C /tmp/ebc_stock checkout 7d1f5efb270003208956e764765f403b755281d7
cp -r /tmp/ebc_stock /tmp/ebc_rm5
patch /tmp/ebc_rm5/tech/gf180mcuD/gf180mcuD.tech < $R/signoff/lvs/tech_patches/rm5.diff
```

Expected: `patch` applies one hunk at line 2350, deleting the `and RESDEF` line under
`layer rm5 MET5`.

## 2. Rebuild the GDS and XOR it

The deliverable is built in two KLayout passes over the committed block GDS (`gds/PFD_lib.gds`,
`CP_v1.gds`, `ibias_gen_v1.gds`, `DIV2_QUAD_v1.gds`, `vco_v1.gds`):

1. `team_src/magic/phase5/chip_merge.py` streams each block verbatim and places it.
2. `team_src/magic/phase5/route_chip.py` adds all chip-level metal, the seat in the 605 × 605 µm D
   die, and the pin texts. It reads and writes its `--out` file in place.

Both default to writing `gds/chip_top.gds`. Always pass `--out` to a scratch file.

**Out of scope here:** regenerating the five block GDS files themselves from `.mag` (or, for
`PFD_lib`, from LibreLane). The only cell this recipe regenerates from layout source is
`vco_varactors`, in step 2.1. The magic export recipe for the other blocks is in
`docs/layout-review-sep01.md`, under "Two harness traps found in B6". It was not exercised here.

### 2.0 An XOR helper (inline, not a committed script)

```bash
cat > /tmp/xor.py <<'EOF'
# klayout -b -r /tmp/xor.py -rd a=A.gds -rd b=B.gds -rd cell=NAME : flattened per-layer XOR + labels
import pya
def load(p):
    ly = pya.Layout(); ly.read(p); return ly
A, B = load(a), load(b)
ca, cb = A.cell(cell), B.cell(cell)
print("bbox A", ca.dbbox(), "B", cb.dbbox(), "same" if ca.dbbox() == cb.dbbox() else "DIFFERENT")
keys = sorted({(A.get_info(i).layer, A.get_info(i).datatype) for i in A.layer_indexes()} |
              {(B.get_info(i).layer, B.get_info(i).datatype) for i in B.layer_indexes()})
u = A.dbu; tot = 0
def texts(L, c):
    out = []
    for i in L.layer_indexes():
        it = c.begin_shapes_rec(i)
        while not it.at_end():
            s = it.shape()
            if s.is_text():
                t = s.text.transformed(it.trans())
                out.append((L.get_info(i).layer, L.get_info(i).datatype, t.string,
                            round(t.x * L.dbu, 4), round(t.y * L.dbu, 4)))
            it.next()
    return sorted(out)
for l, d in keys:
    ra = pya.Region(ca.begin_shapes_rec(A.layer(l, d)))
    rb = pya.Region(cb.begin_shapes_rec(B.layer(l, d))).transformed(pya.ICplxTrans(B.dbu / A.dbu))
    x = ra ^ rb
    if x.count() > 0:    # not is_empty(): that is False on text-only layers with 0 polygons
        tot += x.area() * u * u
        print("  %d/%d XOR %.3f um2" % (l, d, x.area() * u * u))
print("TOTAL XOR %.3f um2" % tot)
ta, tb = texts(A, ca), texts(B, cb)
print("labels A %d B %d" % (len(ta), len(tb)), "IDENTICAL" if ta == tb else "DIFFER")
EOF
```

**A sha256 match is not the test.** Every rebuild writes new GDS timestamps, so its hash always
differs from the committed file even when the geometry is identical
(`docs/verification.md` §8.11). The identity test is this XOR plus the DRC box set in step 3.2.

### 2.1 Varactors from layout source [checked 11-08]

```bash
bash team_src/magic/phase5/write_vco_gds.sh /tmp/vgds
for c in vco_varactors vco_v1 chip_top; do
  klayout -b -r /tmp/xor.py -rd a=$R/gds/$c.gds -rd b=/tmp/vgds/$c.gds -rd cell=$c | grep -E "TOTAL|labels|bbox"
done
```

This writes `vco_varactors.gds` from `team_src/magic/vco_varactors.mag` with the patched tech, then
splices it into copies of `gds/vco_v1.gds` and `gds/chip_top.gds`. It writes only to `/tmp/vgds`.

Expected: `TECH_OK`, `WROTE`, then `VARACTOR_COMP_GATE PASS` (42 varactors, COMP∩MOS_CAP_MK
1050.000 µm² in each of the three files). Each XOR: `TOTAL XOR 0.000 um2`, bbox same, labels
IDENTICAL (3 / 19 / 529). Measured on 11-08: exactly that, in 22–25 s.

### 2.2 Chip from blocks [checked 11-08]

```bash
mkdir -p /tmp/rebuild
(cd team_src/magic/phase5 && python3 chip_merge.py --out /tmp/rebuild/chip_top.gds | tail -3 \
 && python3 route_chip.py --out /tmp/rebuild/chip_top.gds | tail -2)
klayout -b -r /tmp/xor.py -rd a=$R/gds/chip_top.gds -rd b=/tmp/rebuild/chip_top.gds -rd cell=chip_top
sha256sum gds/chip_top.gds /tmp/rebuild/chip_top.gds
```

Expected: `chip_merge` prints `WROTE /tmp/rebuild/chip_top.gds`, and `route_chip` exits 0.
The XOR reports `bbox ... same`, **`TOTAL XOR 0.000 um2`** with no per-layer lines, and
`labels A 529 B 529 IDENTICAL`. The committed file's sha256 is
`e14b48cae71eeb604ed965bcd70c15610db065d31513be3def3c5711b1943707`; the rebuild's hash differs
(timestamps).

Measured on 11-08: bbox (0,0;605,605) same, `TOTAL XOR 0.000 um2`, 529 labels identical, 8 s
for both passes plus the XOR. Two rebuilds gave two different hashes (`f9407673…`, `6ce75eca…`),
neither equal to the committed one, which is the timestamp effect described above.

## 3. Signoff gates

All of these run on the **committed** `gds/chip_top.gds` and the committed `.mag` cells, from
`$R`.

### 3.1 `verify_cp.sh`, six cells [checked 11-08]

```bash
for c in PFD_lib CP_v1 ibias_gen_v1 DIV2_QUAD_v1 vco_v1 chip_top; do
  echo "== $c"; bash team_src/magic/verify_cp.sh $c | grep -E "DRC errors|devices \(LVS\)|^ports|LVS verdict|RESULT"
done
```

Each cell is magic extraction plus netgen against `team_src/magic/<cell>_golden.spice`. The
script exits 0 only on DRC 0, a unique match and zero property errors. Output goes to
`team_src/magic/verify_work/` (git-ignored).

Measured on 11-08, 33 s for all six:

| Cell | `devices (LVS)` line | `ports` | `LVS verdict` | `RESULT` |
|---|---|---:|---|---|
| `PFD_lib` | 7 (+18 fill/decap ignored) | 6 | match uniquely | PASS |
| `CP_v1` | 38 | 7 | match uniquely | PASS |
| `ibias_gen_v1` | 228 | 6 | match uniquely | PASS |
| `DIV2_QUAD_v1` | 149 | 9 | match uniquely | PASS |
| `vco_v1` | 4 | 6 | match uniquely | PASS |
| `chip_top` | 10 | 11 | match uniquely | PASS |

`DRC errors : 0` on every cell. The `devices (LVS)` line is the script's own summary, not
netgen's merged count (7 / 8 / 17 / 75 / 7 / 10 in `signoff/lvs/README.md`). Both are correct
for what they count; `signoff/devices.md` explains the conventions.

### 3.2 Magic full-chip DRC box set [recorded, 3b74fd5-era run 2026-11-06]

```bash
(cd /tmp && GDSF=$R/gds/chip_top.gds CELL=chip_top magic -dnull -noconsole \
   -rcfile /foss/pdks/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc \
   $R/team_src/magic/analysis/drc_boxset.tcl </dev/null 2>/dev/null \
 | grep -E '^(GDSF|GDSBLOB|SRCCOMMIT|TOTAL|CELLCOUNT|RULE|B|SELFCHECK) ' > /tmp/chip.dump)
grep -E '^(TOTAL|SELFCHECK)' /tmp/chip.dump
python3 team_src/magic/analysis/drc_delta.py team_src/magic/chip_top.drcbase /tmp/chip.dump | tail -4
```

Expected: `TOTAL 0`, `SELFCHECK OK rules=0/0 boxes=0/0`, `ADDED ... 0`, `REMOVED ... 0`,
`RESULT: PASS`. About 2 s.

### 3.3 KLayout variant-D signoff deck [recorded, 402b1d9 baseline]

```bash
python3 team_src/magic/klayout_signoff.py chip_top | tail -3
```

Expected: **0 violations, no waivers.** The old 168 PL.5a/5b_LV items were the varactor COMP
defect and are gone since `8ca968f`. About 17 s.

### 3.4 Organizer LVS, stock and `rm5` [recorded, 2026-11-06]

Needs both runner copies from step 1.3.

```bash
for v in stock rm5; do
  W=/tmp/dlvs_$v; rm -rf $W; mkdir -p $W
  bash -lc "export PDK=gf180mcuD PDK_ROOT=/foss/pdks LVS_ROOT=/tmp/ebc_$v UPRJ_ROOT=$R WORK_ROOT=$W; cd $W; \$LVS_ROOT/run_full_lvs \$UPRJ_ROOT/lvs/lvs_config.json" > $W/run.log 2>&1 </dev/null
  echo "== $v exit $?"; grep -E "^Final result|^Number of (devices|nets):" $W/lvs.report | tail -3
done
```

| Runner | Devices (layout / source) | Nets | Verdict |
|---|---|---|---|
| stock `7d1f5ef` | 16 / 18 | 21 / 22 | **Netlists do not match**: the inductor's 2 `tm11k` only (`Error: LVS mismatch`) |
| `7d1f5ef` + `rm5.diff` | 10 / 10 | 20 / 20 | **Circuits match uniquely**: exit 5, a black-box warning only; 11/11 ports paired |

The stock failure is the open `RESDEF` reader bug, which is still unfixed upstream. See
`signoff/lvs/README.md`, "2026-11-06: D block, `402b1d9`". About 10 s each.

### 3.5 Varactor COMP gate [recorded, 2026-11-06; the same gate ran on step 2.1's files on 11-08]

```bash
klayout -b -r team_src/magic/analysis/varactor_comp_gate.py | grep -E "^PASS|^FAIL|VARACTOR_COMP_GATE"
```

With no `-rd gds=`, it checks the three committed files. Expected: three `PASS` lines, each
`COMP&MOS_CAP_MK 1050.000 um2 (want 1050) | cap_nmos_03v3_b 42 (want 42)`, then
`VARACTOR_COMP_GATE PASS`. About 5 s.

### 3.6 Pad landings [recorded, 2026-11-06]

```bash
klayout -b -r team_src/magic/analysis/landing_check.py </dev/null | grep -E "^[A-Z_]+ +(OK|FAIL)|net\(s\)"
```

Expected: 14 `OK` rows (CP_OUT, IBIAS, ISS, I_N, Q_N, Q_P, REF_IN, REF_IN_PD, REF_IN_PU, VDDA,
VDDD, VSSA, VSSD, VTUNE), then `0 net(s) failed to reach every target finger.` The script
defaults to the D block. About 5 s.

### 3.7 Optional: placement table and doc cross-references [recorded]

```bash
(cd team_src/magic/phase5 && python3 check_placement.py | tail -1)    # consistent, ~4 s
python3 team_src/magic/analysis/ref_audit.py . | tail -2              # RESULT: PASS, 0 unresolved
```

`lane_conflicts.py` is **not** a D-block gate. It holds the old BH allocation.

## 4. Test-plan simulations [recorded, all from runs on 2026-11-02]

These were **not** re-run on 11-08. Each script writes its decks and logs to `/tmp/<name>`.
Expected numbers are as recorded in `docs/test_plan.md`. Jobs marked **> 2 min** exceed a
2-minute-per-job budget, so run them in the background.

| Pin | Command | Expected | Runtime |
|---|---|---|---|
| `VDDA` | `bash signoff/sim/vdda/run_vdda.sh` | CP + IBIAS 0.599 mA (TT idle; 0.595 SS to 0.600 FF); VCO 1.300 mA at ISS 1.0× (0.974 Vpp, 4.372 GHz) and 2.332 mA at 2.0× (2.207 Vpp, 4.402 GHz). Total **1.90 / 2.93 mA** (`docs/test_plan.md` §3) | 3 op points < 1 s; 2 VCO transients **~2 min each, > 2 min** |
| `IBIAS` | `bash team_src/sim/ibias/run_ibias_pin.sh` | v(IBIAS) at 240 µA: **2.066 V TT**, 1.787 V FF, 2.349 V SS, the same at VDD 3.0 / 3.3 / 3.6 V. TT 3.3 V control: VGP / VGN / IB_DIV2 = 50.00 / 49.91 / 239.56 µA (`docs/test_plan.md` §3, §5.4) | 9 runs, < 1 s each |
| `ISS` | `bash signoff/sim/iss/run_iss.sh node`, then `... sweep` | node: six mirror runs, v(ISS) avg 1.018–1.389 V, min **1.009 V** (2.0×, VTUNE 3.3 V); no start at 1.0× / 3.3 V. sweep: 1.00–2.35 mA ideal sink, v(ISS) 1.257 → 1.108 V (`docs/test_plan.md` §5.1) | 12 runs, **~2 min each, ~21 min total, > 2 min** |
| `CP_OUT` | `bash signoff/sim/cp_out/run_cp_out.sh` | at 0.32 / 1.65 / 3.00 V: idle +29.8 / +12.2 / −5.6 pA; UP +50.34 / +50.21 / +48.12 µA; DOWN −48.08 / −50.24 / −50.54 µA (`docs/test_plan.md` §5.3) | 0.3 s |
| `CP_OUT` edge | `bash signoff/sim/cp_out/run_pfd_cp_edge.sh` | idle +12.2 pA before the 50 ns `REF_IN` edge, **+50.21 µA (UP)** after (`docs/test_plan.md` §5.3) | 11 s |
| `I_P` (ib_conv) | `bash signoff/pex/ib_conv_v1/decks/run_mix_9614947.sh $R` | **I_P 29 mVpp**, I_N / Q_P / Q_N 131 mVpp, 2.500 GHz, duty 64.5 %, I/Q 289.6°, INV3 1989…2687 mV (`signoff/pex/ib_conv_v1/resim.md`) | 55.6 s (re-run 11-02); the script header says ~75 s |

The `ISS` and `VDDA` VCO runs are 200 ns transients on the landed `vco_v1` extraction. A run
takes 52–147 s with 2 threads, so budget for the long end.

## 5. What this recipe does not cover

- Block GDS regeneration from `.mag` / LibreLane for `PFD_lib`, `CP_v1`, `ibias_gen_v1`,
  `DIV2_QUAD_v1` and `vco_v1` (only the varactor cell is regenerated, step 2.1).
- The VCO f–VTUNE sweep and PEX re-extraction (`signoff/sim/vco/`, `signoff/pex/*/README.md`).
- Density. It is measured by the KLayout deck in step 3.3; see `docs/verification.md` §8.
