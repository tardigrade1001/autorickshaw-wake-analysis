#!/bin/bash
#   runcase.sh <LABEL>
# The tutorial's own Allrun re-copies motorBike.obj.gz from the resources dir,
# so it cannot be reused verbatim -- the stages are spelled out here instead.
# clear $@ before sourcing -- OpenFOAM's bashrc parses the sourcing script's
# positional args and sources anything it does not recognise
CASE=$1
set --
. /usr/lib/openfoam/openfoam2512/etc/bashrc
set -e
cd ~/aero/$CASE
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# runApplication SKIPS any stage whose log already exists. After a mid-run
# failure that silently reuses the broken mesh and runs the solver on it, so
# clear the logs and decomposition and redo the mesh from blockMesh.
rm -f log.* ; rm -rf processor* postProcessing [1-9]* 0

cat > system/surfaceFeatureExtractDict <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object surfaceFeatureExtractDict; }
vehicle.stl
{
    extractionMethod    extractFromSurface;
    includedAngle       150;
    subsetFeatures      { nonManifoldEdges no; openEdges yes; }
    writeObj            no;
}
EOF

D="-decomposeParDict system/decomposeParDict.6"
runApplication surfaceFeatureExtract
runApplication blockMesh
runApplication $D decomposePar
runParallel $D snappyHexMesh -overwrite
restore0Dir -processor
runParallel $D checkMesh -constant
runParallel $D $(getApplication)
echo "RUN| $CASE finished"
