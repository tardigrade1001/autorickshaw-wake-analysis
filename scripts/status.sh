#!/bin/bash
echo "=== live processes ==="
pgrep -fa 'fleet.sh|snappyHexMesh|simpleFoam' | cut -c1-90 | head -6
echo "=== fleet.log tail ==="
tail -6 ~/fleet.log 2>/dev/null || echo "(no log)"
echo "=== results so far ==="
[ -f ~/aero/fleet_results.tsv ] && column -t ~/aero/fleet_results.tsv || echo "(none yet)"
for L in AUTO DZIRE WAGONR; do
  f=~/aero/$L/log.simpleFoam
  [ -f "$f" ] && echo "$L iters=$(grep -c '^Time = ' $f)"
done
