#!/bin/bash
# VDDA current: CP_v1 (PEX) + ibias_gen_v1 op points at TT/FF/SS, then vco_v1 (PEX) 200 ns
# transients at ISS 1.0x and 2.0x. One job at a time, ngspice capped at 2 threads.
# Generated decks, logs and .dat go to /tmp/vdda. VCO runs take ~2 min each.
export PATH=/foss/tools/bin:$PATH OMP_NUM_THREADS=2 UPRJ_ROOT=/foss/designs/AUS-NZ-integration
HERE=/foss/designs/AUS-NZ-integration/signoff/sim/vdda
T=/tmp/vdda; mkdir -p $T
for c in typical ff ss; do
  sed "s/CORNER/$c/g" $HERE/cp_ib_vdda.spice.in > $T/cp_ib_$c.spice
  echo "### CP+IBIAS $c"
  ngspice -b $T/cp_ib_$c.spice > $T/cp_ib_$c.log 2>&1
  grep -E "^i\(|rror" $T/cp_ib_$c.log
done
python3 $HERE/mk_vco_vdda.py $T
for m in 1x 2x; do
  echo "### VCO $m"
  s=$(date +%s)
  ngspice -b $T/vco_vdda_$m.spice > $T/vco_$m.log 2>&1
  echo "wall $(( $(date +%s) - s )) s"
  grep -iE "^(ivco_avg|iss_avg|ibench_avg)|rror" $T/vco_$m.log
done
