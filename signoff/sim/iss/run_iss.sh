#!/bin/bash
# ISS node voltage and sink compliance on the landed vco_v1 extraction.
# usage: run_iss.sh node|sweep. One job at a time, ngspice capped at 2 threads; ~2 min per run.
# Generated decks, logs and .dat go to /tmp/iss.
export PATH=/foss/tools/bin:$PATH OMP_NUM_THREADS=2 UPRJ_ROOT=/foss/designs/AUS-NZ-integration
HERE=/foss/designs/AUS-NZ-integration/signoff/sim/iss
T=/tmp/iss; mkdir -p $T
run() {  # name mode amps vtune
  python3 $HERE/mk_vco_iss.py $T "$@" || exit 1
  echo "### $1 ($2 $3, VTUNE $4)"
  s=$(date +%s)
  ngspice -b $T/$1.spice > $T/$1.log 2>&1
  echo "wall $(( $(date +%s) - s )) s"
  grep -iE "^(viss_avg|viss_min|viss_max|iss_avg)|rror" $T/$1.log
  python3 $HERE/analyze_iss.py $T/$1.dat
}
case "$1" in
  node)   # bench mirror at 1.0x / 2.0x, VTUNE 0 / 2.0 / 3.3 V
    for m in 1m 2m; do for v in 0.0 2.0 3.3; do run node_${m}_${v} mirror $m $v; done; done ;;
  sweep)  # ideal current sink, VTUNE 2.0 V
    for i in 1.0m 1.15m 1.3m 1.6m 2.0m 2.35m; do run sink_${i}_2.0 ideal $i 2.0; done ;;
  *) echo "usage: $0 node|sweep"; exit 2 ;;
esac
