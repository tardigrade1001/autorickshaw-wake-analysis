#!/bin/bash
#   resume.sh <LABEL>
# Restart the SOLVER from the latest written time, reusing the existing mesh.
#
# Why this exists: a WSL job cannot be made drop-proof on atma. Detaching with
# `nohup setsid` dies because WSL shuts the VM down when the last session exits;
# `wmic process call create` (the ORCA technique) spawns into session 0, where
# the WSL VM does not start properly and mpirun dies before writing a byte.
# ORCA survives that only because orca.exe is a native Windows binary.
#
# So: accept that a dropped network kills the run, and make that cheap.
#   processor*/constant/polyMesh        the mesh -- the expensive part (~20 min)
#   processor*/<time>/                  fields, every writeInterval
#   postProcessing/.../coefficient.dat  the Cd history, appended EVERY iteration
# The last one is the important one: the RESULT is never at risk, only
# completion. A run cut off at iteration 900 still yields a valid mean over its
# final 200.
LABEL=$1
set --
. /usr/lib/openfoam/openfoam2512/etc/bashrc
set -e
cd ~/aero/$LABEL
. $WM_PROJECT_DIR/bin/tools/RunFunctions

if [ ! -d processor0/constant/polyMesh ]; then
    echo "RESUME| $LABEL has no mesh -- run runcase.sh first"
    exit 1
fi

LATEST=$(ls processor0 | grep -E '^[0-9]+(\.[0-9]+)?$' | sort -n | tail -1)
echo "RESUME| $LABEL restarting from t=${LATEST:-0}"

grep -rl vehicleGroup 0.orig | xargs -r sed -i 's/vehicleGroup/vehicle/g'
if [ -z "$LATEST" ] || [ "$LATEST" = "0" ]; then
    restore0Dir -processor
    foamDictionary system/controlDict -entry startFrom -set startTime
else
    foamDictionary system/controlDict -entry startFrom -set latestTime
fi
foamDictionary system/controlDict -entry endTime -set 1000
# tight writeInterval: a dropped link then costs at most 100 iterations of
# fields, and zero iterations of force history
foamDictionary system/controlDict -entry writeInterval -set 100

# runApplication/runParallel refuse to rerun while a log exists; move it aside
# rather than delete, so a failed attempt stays inspectable
[ -f log.simpleFoam ] && mv log.simpleFoam log.simpleFoam.$(date +%s)
runParallel -decomposeParDict system/decomposeParDict.6 $(getApplication)
echo "RUN| $LABEL solver finished"
