#!/bin/bash
# CP_OUT DC currents (cp_out_op.spice). Single ngspice job, 2 threads, a few seconds.
export PATH=/foss/tools/bin:$PATH OMP_NUM_THREADS=2
mkdir -p /tmp/cp_out && cd /tmp/cp_out
s=$(date +%s.%N)
ngspice -b /foss/designs/AUS-NZ-integration/signoff/sim/cp_out/cp_out_op.spice > cp_out_op.log 2>&1
echo "wall $(echo "$(date +%s.%N) - $s" | bc) s"
grep -E "RESULT|rror" cp_out_op.log
