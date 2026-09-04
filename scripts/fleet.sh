#!/bin/bash
# Fleet queue: run every vehicle in a manifest, one after another, unattended.
#
#   fleet.sh <manifest>
#
# manifest lines:  LABEL  Aref_m2  Lref_m
# (both produced by exportcfd.py, which prints the measured frontal area)
#
# STLs are expected at $STLDIR/<LABEL>.stl.
# Each vehicle is INDEPENDENT -- a failure is logged and the queue continues,
# because losing an overnight batch to one bad mesh is the whole risk here.
# OpenFOAM's etc/bashrc PARSES THE SOURCING SCRIPT'S POSITIONAL ARGS and sources
# anything it does not recognise. Sourcing it while $@ still holds our arguments
# made it execute the manifest itself ("manifest.txt: line 2: AUTO: command not
# found"). Capture args, clear $@, then source.
MAN=${1:?usage: fleet.sh <manifest>}
set --
. /usr/lib/openfoam/openfoam2512/etc/bashrc
STLDIR=${STLDIR:-$HOME/stl}
HERE=$(cd "$(dirname "$0")" && pwd)
RESULTS=$HOME/aero/fleet_results.tsv
[ -f "$RESULTS" ] || printf "label\tCd\tband%%\tAref\tCdA\tcells\titers\tstatus\n" > "$RESULTS"

while read -r L A LR; do
  case "$L" in ''|'#'*) continue;; esac
  if grep -qP "^$L\t" "$RESULTS"; then echo "FLEET| $L already done, skipping"; continue; fi
  echo "FLEET| ==== $L (Aref=$A Lref=$LR) ===="
  if [ ! -f "$STLDIR/$L.stl" ]; then
    printf "%s\t-\t-\t%s\t-\t-\t-\tNO_STL\n" "$L" "$A" >> "$RESULTS"; continue
  fi
  # keep per-vehicle logs -- discarding them to /dev/null makes an overnight
  # failure undiagnosable, which is exactly when you cannot afford that
  mkdir -p $HOME/aero/logs
  if ! STL_OVERRIDE="$STLDIR/$L.stl" bash "$HERE/mkcase.sh" "$L" "$A" "$LR" \
       > $HOME/aero/logs/$L.mkcase.log 2>&1; then
    printf "%s\t-\t-\t%s\t-\t-\t-\tMKCASE_FAIL\n" "$L" "$A" >> "$RESULTS"; continue
  fi
  if ! bash "$HERE/runcase.sh" "$L" > $HOME/aero/logs/$L.run.log 2>&1; then
    printf "%s\t-\t-\t%s\t-\t-\t-\tRUN_FAIL\n" "$L" "$A" >> "$RESULTS"; continue
  fi
  F=$HOME/aero/$L/postProcessing/forceCoeffs1/0/coefficient.dat
  C=$(grep 'Layer mesh' $HOME/aero/$L/log.snappyHexMesh | tail -1 | sed 's/.*cells:\([0-9]*\).*/\1/')
  N=$(grep -c '^Time = ' $HOME/aero/$L/log.simpleFoam)
  awk -v L="$L" -v A="$A" -v C="$C" -v N="$N" \
      'NR>13 && $1>(N-200) {n++; s+=$2; if(mn==""||$2<mn)mn=$2; if($2>mx)mx=$2}
       END {if(n){m=s/n; printf "%s\t%.4f\t%.1f\t%s\t%.3f\t%s\t%s\tOK\n",L,m,100*(mx-mn)/m,A,m*A,C,N}
            else  printf "%s\t-\t-\t%s\t-\t%s\t%s\tNO_FORCES\n",L,A,C,N}' "$F" >> "$RESULTS"
  tail -1 "$RESULTS"
done < "$MAN"

echo "FLEET| ==== done ===="
column -t "$RESULTS"
