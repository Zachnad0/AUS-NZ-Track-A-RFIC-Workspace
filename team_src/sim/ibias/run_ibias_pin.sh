#!/bin/bash
# IBIAS pin voltage vs forced current. Runs ibias_pin.spice.in at TT/FF/SS x VDD 3.0/3.3/3.6.
export PATH=/foss/tools/bin:$PATH
cd /foss/designs/AUS-NZ-integration/team_src/sim/ibias
T=/tmp/ibias_pin; mkdir -p $T   # generated decks + logs stay out of the repo
for c in typical ff ss; do
  for v in 3.0 3.3 3.6; do
    sed -e "s/CORNER/$c/g" -e "s/VDDV/$v/g" ibias_pin.spice.in > $T/pin_${c}_${v}.spice
    echo "### $c $v"
    start=$(date +%s.%N)
    ngspice -b $T/pin_${c}_${v}.spice > $T/pin_${c}_${v}.log 2>&1
    end=$(date +%s.%N)
    grep -E "^(v\(ibias\)|v\(x1\.nb\)|i_vgp|i_vgn|i_ibd) |rror" $T/pin_${c}_${v}.log
    echo "wall $(echo "$end - $start" | bc) s"
  done
done
