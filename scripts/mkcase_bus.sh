#!/bin/bash
# Build the city-bus case. Same numerics as the car cases (motorBike-derived
# fvSchemes / fvSolution / snappy controls, k-omega SST, U=16.67); ONLY the
# domain and the refinement boxes are resized, because an 11 m body in the
# car domain would sit at 3.9% blockage and have <3 body lengths of wake.
#
# Comparability between vehicles is set by BLOCKAGE RATIO, not by an identical
# box: cars ~1.2%, bus 1.75%. The base cell stays 0.5 m so that snappy's
# refinement levels -- which are RELATIVE to the base cell -- give the bus the
# same surface resolution as the cars. Coarsening the far field would have been
# cheaper and would have silently under-resolved the bus.
LABEL=$1; AREF=$2; LREF=$3
set --
. /usr/lib/openfoam/openfoam2512/etc/bashrc
set -e
U=16.67
STL="${STL_OVERRIDE:-$HOME/geom/${LABEL}.stl}"
C=~/aero/${LABEL}

rm -rf $C
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike $C
cd $C
rm -rf 0 constant/triSurface postProcessing log.* processor*
grep -rl motorBike 0.orig system | xargs sed -i 's/motorBike/vehicle/g'
grep -rl vehicleGroup 0.orig | xargs -r sed -i 's/vehicleGroup/vehicle/g'
mkdir -p constant/triSurface
cp "$STL" constant/triSurface/vehicle.stl

# l = 0.1 * body height = 0.31 m  (cars: 0.15 m -> omega 2.2). Same method,
# scaled to the body, so freestream turbulence is not a hidden variable.
cat > 0.orig/include/initialConditions <<EOF
flowVelocity         ($U 0 0);
pressure             0;
turbulentKE          0.042;
turbulentOmega       1.2;
EOF

# 100 x 32 x 14 m at 0.5 m base cell = 358k base cells.
# inlet 2L upstream, outlet ~6L downstream, blockage 7.85/448 = 1.75%.
cat > system/blockMeshDict <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
scale   1;
vertices
(
    (-22 -16  0) ( 78 -16  0) ( 78  16  0) (-22  16  0)
    (-22 -16 14) ( 78 -16 14) ( 78  16 14) (-22  16 14)
);
blocks ( hex (0 1 2 3 4 5 6 7) (200 64 28) simpleGrading (1 1 1) );
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

cat > system/snappyHexMeshDict <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object snappyHexMeshDict; }
castellatedMesh true;
snap            true;
addLayers       true;

geometry
{
    vehicle.stl { type triSurfaceMesh; name vehicle; }
    refineNear  { type searchableBox; min (-3 -4 0);  max (14 4 4.5); }
    refineWake  { type searchableBox; min (-6 -7 0);  max (42 7 7.5); }
}

castellatedMeshControls
{
    maxLocalCells 4000000;
    maxGlobalCells 12000000;
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

    locationInMesh (-21 -15 13);
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

meshQualityControls
{
    #include "meshQualityDict"
    nSmoothScale   4;
    errorReduction 0.75;
}
writeFlags ( scalarLevels layerSets layerFields );
mergeTolerance 1e-6;
EOF

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
