#!/bin/bash
#   mktrans.sh <SRC_CASE>
# Build a TRANSIENT (URANS) case from an already-converged steady case, reusing
# its decomposed mesh and its converged fields as the initial condition.
#
# WHY FIXED-FRAME AND NOT OVERSET:
# A vehicle travelling in a straight line at constant speed through still air is
# Galilean-identical to the wind-tunnel case -- same physics, different frame.
# Moving mesh buys nothing here. What the steady solve is MISSING is unsteadiness
# (vortex shedding), and that is what pimpleFoam adds. v_y is frame-invariant, so
# the sideways gust a roadside pedestrian feels is read directly off these planes.
#
# The pedestrian time history is recovered rigorously, with NO frozen-flow
# assumption, by saving the planes EVERY timestep and then reading the diagonal
# x = -U*t through the (x, t) data: that is exactly what a fixed observer sees as
# the vehicle goes past.
#
# Cost: starting from the converged steady field skips spin-up, and PIMPLE is
# implicit so maxCo ~5 is legitimate. ~1.6 cm finest cell / 16.67 m/s -> dt ~5 ms,
# so 2 s is ~400 steps -- comparable to the steady run, not 20x it.
SRC=$1
CASE=${SRC}_T
set --
. /usr/lib/openfoam/openfoam2512/etc/bashrc
set -e

cd ~/aero
[ -d "$SRC/processor0/constant/polyMesh" ] || { echo "TRANS| $SRC has no decomposed mesh"; exit 1; }
rm -rf $CASE
cp -r $SRC $CASE
cd $CASE
rm -f log.*
rm -rf postProcessing

# Converged steady field -> t = 0 of the transient. Renaming beats carrying a
# time origin of 1000 s through every plot.
LATEST=$(ls processor0 | grep -E '^[0-9]+$' | sort -n | tail -1)
echo "TRANS| seeding from steady t=$LATEST"
for d in processor*; do
    rm -rf $d/0
    mv $d/$LATEST $d/0
    ls -d $d/[0-9]* 2>/dev/null | grep -v "$d/0$" | xargs -r rm -rf
done

cat > system/fvSchemes <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
// second-order in time; 'bounded' is dropped from div -- it is a steady-state
// device that adds a fictitious source proportional to div(phi)
ddtSchemes       { default backward; }
gradSchemes      { default Gauss linear; limited cellLimited Gauss linear 1; }
divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind limited;
    div(phi,k)      Gauss limitedLinear 1;
    div(phi,omega)  Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes    { default corrected; }
wallDist         { method meshWave; }
EOF

cat > system/fvSolution <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.01;
        smoother        GaussSeidel;
    }
    pFinal          { $p; relTol 0; }
    "(U|k|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-7;
        relTol          0.1;
    }
    "(U|k|omega)Final" { $U; relTol 0; }
}

PIMPLE
{
    nOuterCorrectors        2;
    nCorrectors             2;
    nNonOrthogonalCorrectors 1;
    turbOnFinalIterAndSubIters yes;
}

relaxationFactors
{
    equations { ".*" 1; }
}
EOF

# Write controlDict from scratch. The motorBike tutorial's functions block
# carries streamLines, wallBoundedStreamLines and ensightWrite -- harmless in a
# steady run that writes twice, ruinous in a transient sampling every timestep.
# Keep only forceCoeffs and the pedestrian planes.
AREF=$(foamDictionary system/forceCoeffs -entry forceCoeffs1/Aref -value)
LREF=$(foamDictionary system/forceCoeffs -entry forceCoeffs1/lRef -value)
cat > system/controlDict <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     pimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         2.0;
deltaT          0.0005;
writeControl    adjustableRunTime;
writeInterval   0.5;
purgeWrite      0;
writeFormat     binary;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   8;
runTimeModifiable true;
adjustTimeStep  yes;
maxCo           5;
maxDeltaT       0.01;

functions
{
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
        magUInf         16.67;
        lRef            ${LREF};
        Aref            ${AREF};
    }

    // planes at three pedestrian standoffs, EVERY timestep, so the pedestrian
    // time history can be taken as the diagonal x = -U*t through (x,t)
    pedPlanes
    {
        type            surfaces;
        libs            (sampling);
        writeControl    timeStep;
        writeInterval   1;
        fields          (U p k);
        interpolationScheme cellPoint;
        surfaceFormat   raw;
        surfaces
        {
            y1p2 { type cuttingPlane; point (0 1.2 0); normal (0 1 0); interpolate true; }
            y2p0 { type cuttingPlane; point (0 2.0 0); normal (0 1 0); interpolate true; }
            y3p0 { type cuttingPlane; point (0 3.0 0); normal (0 1 0); interpolate true; }
        }
    }
}
EOF

echo "TRANS| $CASE ready  (pimpleFoam, endTime 2.0 s, maxCo 5)"
