#!/bin/bash
# Reproduce the resim.md "Re-run 2026-09-17" row: div2_mix_9614947.spice (one job, 2 threads,
# ~75 s), then analyze.awk on its dump. Usage: run_mix_9614947.sh [repo root]; output in /tmp.
REPO=${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}
export PATH=/foss/tools/bin:$PATH OMP_NUM_THREADS=2
T=/tmp/mix9614947; rm -rf $T && mkdir -p $T && cd $T
s=$(date +%s.%N)
timeout 120 ngspice -b $REPO/signoff/pex/ib_conv_v1/decks/div2_mix_9614947.spice > mix.log 2>&1
echo "ngspice exit $?, $(echo "$(date +%s.%N) - $s" | bc | cut -c1-5) s"
grep -iE "error|could not|cannot" mix.log | head -3
awk -v CORNER=TT -f $REPO/team_src/sim/div2/analyze.awk mix9614947_quad.dat
