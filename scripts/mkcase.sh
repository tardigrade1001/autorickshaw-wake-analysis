#!/bin/bash
# Build an external-aero case for one vehicle.
#   mkcase.sh <LABEL> <Aref m2> <Lref m>
#
# Derived from the motorBike tutorial rather than written from scratch: its
# fvSchemes / fvSolution / forceCoeffs / snappy controls are a validated
# simpleFoam + k-omega SST external-aero setup, and the install was checked
# against it (Cd 0.4159). Only the things that MUST differ are changed --
# geometry, domain, reference values, freestream. Everything the comparison
# depends on is therefore identical between vehicles by construction.
# Read args and CLEAR $@ before sourcing: OpenFOAM's bashrc parses the sourcing
# script's positional args and sources what it cannot interpret, so
# `mkcase.sh AUTO 1.618 2.702` made it try to source a file named "AUTO".
# Also source BEFORE `set -e`: its bashrc trips a bash "pop_var_context" error
# under errexit, which aborts the script before it does anything.
LABEL=$1; AREF=$2; LREF=$3
set --
. /usr/lib/openfoam/openfoam2512/etc/bashrc
set -e
U=16.67                      # 60 km/h -- a speed both vehicles actually do
# STL_OVERRIDE lets the fleet queue point at a staged directory (e.g. on atma,
# where the Windows D: drive of his PC does not exist)
STL="${STL_OVERRIDE:-/mnt/d/Blender/Blender Files/Auto tests/cfd/geometry/${LABEL}.stl}"
C=~/aero/${LABEL}

rm -rf $C
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike $C
cd $C
rm -rf 0 constant/triSurface postProcessing log.* processor*

# the tutorial names its body patch "motorBike" throughout 0.orig and system/
grep -rl motorBike 0.orig system | xargs sed -i 's/motorBike/vehicle/g'
# motorBike.stl ships several named regions collected into "motorBikeGroup";
# our wrap is a single unnamed solid, so snappy makes one patch called
# "vehicle" and the group name matches nothing -> "Cannot find patchField
# entry for vehicle" at solver start, long after the mesh is built.
grep -rl vehicleGroup 0.orig | xargs -r sed -i 's/vehicleGroup/vehicle/g'
mkdir -p constant/triSurface
cp "$STL" constant/triSurface/vehicle.stl

# --- freestream and turbulence inlet ---------------------------------------
# I = 1%, l = 0.1*vehicle height ~ 0.17 m
# k = 1.5*(U*I)^2 ;  omega = sqrt(k)/(Cmu^0.25 * l)
cat > 0.orig/include/initialConditions <<EOF
flowVelocity         ($U 0 0);
pressure             0;
turbulentKE          0.042;
turbulentOmega       2.2;
EOF

# --- domain ----------------------------------------------------------------
# 42 x 20 x 10 m at 0.5 m base cell. Inlet 3L upstream, outlet ~6L downstream,
# blockage ratio ~1.2% so the walls do not squeeze the flow.
cat > system/blockMeshDict <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
scale   1;
vertices
(
    (-12 -10  0) ( 30 -10  0) ( 30  10  0) (-12  10  0)
    (-12 -10 10) ( 30 -10 10) ( 30  10 10) (-12  10 10)
);
blocks ( hex (0 1 2 3 4 5 6 7) (84 40 20) simpleGrading (1 1 1) );
edges ();
boundary
(
    inlet        { type patch; faces ((0 4 7 3)); }
    outlet       { type patch; faces ((1 2 6 5)); }
    lowerWall    { type wall;  faces ((0 3 2 1)); }
    upperWall    { type patch; faces ((4 5 6 7)); }
    frontAndBack { type patch; faces ((0 1 5 4) (3 7 6 2)); }
);
EOF

# --- meshing ---------------------------------------------------------------
cat > system/snappyHexMeshDict <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object snappyHexMeshDict; }
castellatedMesh true;
snap            true;
addLayers       true;

geometry
{
    vehicle.stl { type triSurfaceMesh; name vehicle; }
    refineNear  { type searchableBox; min (-2 -3 0); max (12 3 3.5); }
    refineWake  { type searchableBox; min (-4 -5 0); max (24 5 5); }
}

castellatedMeshControls
{
    maxLocalCells 2000000;
    maxGlobalCells 8000000;
    minRefinementCells 10;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;

    features ( { file "vehicle.eMesh"; level 5; } );

    refinementSurfaces
    {
        vehicle { level (4 5); patchInfo { type wall; } }
    }

    resolveFeatureAngle 30;

    refinementRegions
    {
        refineWake { mode inside; levels ((1E15 1)); }
        refineNear { mode inside; levels ((1E15 2)); }
    }

    // far corner of the domain -- provably outside the body, which matters for
    // the autorickshaw because its cabin is OPEN and therefore correctly gets
    // meshed as part of the external flow region
    locationInMesh (-11 -9 9);
    allowFreeStandingZoneFaces true;
}

snapControls
{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 30;
    nRelaxIter 5;
    nFeatureSnapIter 10;
    implicitFeatureSnap false;
    explicitFeatureSnap true;
    multiRegionFeatureSnap false;
}

addLayersControls
{
    relativeSizes true;
    layers { vehicle { nSurfaceLayers 3; } }
    expansionRatio 1.3;
    finalLayerThickness 0.5;
    minThickness 0.1;
    nGrow 0;
    featureAngle 130;
    slipFeatureAngle 30;
    nRelaxIter 5;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}

// errorReduction and nSmoothScale are required by addLayers but are NOT in
// the tutorial's meshQualityDict, so they must be supplied here or the run
// dies at "Scaling iteration 0" -- after castellation and snapping succeeded.
meshQualityControls
{
    #include "meshQualityDict"
    nSmoothScale   4;
    errorReduction 0.75;
}
writeFlags ( scalarLevels layerSets layerFields );
mergeTolerance 1e-6;
EOF

# --- reference values for the force coefficients ----------------------------
cat > system/forceCoeffs <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object forceCoeffs; }
forceCoeffs1
{
    type            forceCoeffs;
    libs            (forces);
    writeControl    timeStep;
    writeInterval   1;
    patches         (vehicle);
    rho             rhoInf;
    rhoInf          1.225;
    liftDir         (0 0 1);
    dragDir         (1 0 0);
    CofR            (${LREF} 0 0.5);
    pitchAxis       (0 1 0);
    magUInf         ${U};
    lRef            ${LREF};
    Aref            ${AREF};
}
EOF

foamDictionary system/controlDict -entry endTime -set 1000
foamDictionary system/controlDict -entry writeInterval -set 500

echo "CASE| $LABEL  Aref=$AREF  Lref=$LREF  U=$U  -> $C"
