#!/bin/bash
# One REF_IN edge into PFD_lib + extracted CP_v1 (pfd_cp_edge.spice). One job, 2 threads.
export PATH=/foss/tools/bin:$PATH OMP_NUM_THREADS=2
mkdir -p /tmp/cp_out && cd /tmp/cp_out
s=$(date +%s.%N)
timeout 120 ngspice -b /foss/designs/AUS-NZ-integration/signoff/sim/cp_out/pfd_cp_edge.spice > pfd_cp_edge.log 2>&1
echo "exit $? wall $(echo "$(date +%s.%N) - $s" | bc) s"
grep -iE "^(i_before|i_after|up_before|dn_before|up_after|dn_after)|rror" pfd_cp_edge.log
