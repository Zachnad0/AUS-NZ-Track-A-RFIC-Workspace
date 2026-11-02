#!/bin/bash
# write_vco_gds.sh OUTDIR -- the ONLY sanctioned way to turn team_src/magic/vco_varactors.mag
# into GDS, and to carry it into vco_v1.gds and chip_top.gds.
#
# !!! A plain magic `gds write` with the stock gf180mcuD tech DROPS COMP (22/0) UNDER ALL 42
# !!! VARACTOR GATES: the gdsii cifoutput DIFF layer omits 3.3 V nvaractor/pvaractor. The GDS
# !!! then has poly over field oxide instead of MOS varactors, and the PDK LVS finds 0 of them.
# !!! See signoff/lvs/tech_patches/README.md.
#
# This script: (1) builds a patched copy of $PDK_ROOT's tech in OUTDIR/tech by applying
# signoff/lvs/tech_patches/varactor_comp.diff (the PDK file is never edited, no tech file is
# committed), (2) writes vco_varactors.gds with it -- refusing to run if the loaded tech is not
# the patched one, (3) splices that cell into copies of gds/vco_v1.gds and gds/chip_top.gds,
# (4) runs team_src/magic/analysis/varactor_comp_gate.py on all three. It writes ONLY into
# OUTDIR (standing rule: never `gds write` over a committed artifact); copy into gds/ by hand
# after the gate and the usual chip gates pass.
set -euo pipefail
OUT=${1:?usage: write_vco_gds.sh OUTDIR}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)          # team_src/magic/phase5
REPO=$(cd "$HERE/../../.." && pwd)
: "${PDK_ROOT:=/foss/pdks}"; PDK=gf180mcuD
export PATH=/foss/tools/bin:/foss/tools/klayout:$PATH
mkdir -p "$OUT/tech"; OUT=$(cd "$OUT" && pwd)
case "$OUT" in "$REPO/gds"|"$REPO/gds/") echo "FATAL: OUTDIR must not be $REPO/gds" >&2; exit 2;; esac

cp "$PDK_ROOT/$PDK/libs.tech/magic/$PDK.tech" "$OUT/tech/$PDK.tech"
patch -s "$OUT/tech/$PDK.tech" < "$REPO/signoff/lvs/tech_patches/varactor_comp.diff" \
  || { echo "FATAL: varactor_comp.diff does not apply to $PDK_ROOT tech -- re-derive it" >&2; exit 3; }
sed "s|^tech load .*|tech load $OUT/tech/$PDK.tech|" "$PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc" > "$OUT/tech/$PDK.magicrc"

cat > "$OUT/tech/write.tcl" <<TCL
set tf [tech filename]
set fh [open \$tf]; set body [read \$fh]; close \$fh
if {![regexp {\n\tor\talldiff,nvaractor,pvaractor\n} \$body]} {
    puts "FATAL: loaded tech \$tf lacks the varactor COMP patch -- refusing to gds write"
    quit -noprompt
}
puts "TECH_OK \$tf"
path search [concat "$REPO/team_src/magic" [path search]]
drc off
load vco_varactors
select top cell
gds write $OUT/vco_varactors.gds
puts "WROTE $OUT/vco_varactors.gds"
quit -noprompt
TCL
rm -f "$OUT/vco_varactors.gds" "$OUT/vco_v1.gds" "$OUT/chip_top.gds"   # a refused run must not pass on a stale file
( cd "$OUT/tech" && magic -dnull -noconsole -rcfile "$OUT/tech/$PDK.magicrc" "$OUT/tech/write.tcl" ) | grep -E "TECH_OK|FATAL|WROTE"
[ -f "$OUT/vco_varactors.gds" ] || { echo "FATAL: no GDS written (see FATAL above)" >&2; exit 4; }

for c in vco_v1 chip_top; do
  klayout -b -r "$HERE/splice_cell.py" -rd src="$REPO/gds/$c.gds" -rd new="$OUT/vco_varactors.gds" \
          -rd cellname=vco_varactors -rd out="$OUT/$c.gds"
done
klayout -b -r "$REPO/team_src/magic/analysis/varactor_comp_gate.py" \
        -rd gds="$OUT/vco_varactors.gds,$OUT/vco_v1.gds,$OUT/chip_top.gds"
