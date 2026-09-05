#!/bin/bash
# Report each vehicle the SAME way: mean over the final 200 iterations, with
# the band. A single last-line value is not a measurement on a bluff body --
# steady RANS limit-cycles around the answer and never settles on it.
printf "%-8s %8s %8s %8s %8s %9s %9s\n" VEHICLE Cd band% Aref CdA cells iters
for L in AUTO DZIRE WAGONR; do
  F=~/aero/$L/postProcessing/forceCoeffs1/0/coefficient.dat
  [ -f "$F" ] || continue
  A=$(grep -m1 'Aref' ~/aero/$L/system/forceCoeffs | tr -dc '0-9.')
  C=$(grep 'Layer mesh' ~/aero/$L/log.snappyHexMesh | tail -1 | sed 's/.*cells:\([0-9]*\).*/\1/')
  N=$(grep -c '^Time = ' ~/aero/$L/log.simpleFoam)
  awk -v L=$L -v A=$A -v C=$C -v N=$N \
      'NR>13 && $1>(N-200) {n++; s+=$2; if(mn==""||$2<mn)mn=$2; if($2>mx)mx=$2}
       END {m=s/n; printf "%-8s %8.4f %7.1f%% %8.3f %8.3f %9s %9s\n",
            L, m, 100*(mx-mn)/m, A, m*A, C, N}' N=$N "$F"
done
