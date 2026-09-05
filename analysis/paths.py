"""Where the analysis scripts find their inputs and write their outputs.

The sampled surfaces are the raw output of the transient runs: several hundred
snapshots per case, tens of gigabytes in total. They stay outside the
repository, so any script that reads a flow field resolves its location here.

Three environment variables control it, each with a documented local default:

    VEHICLE_AERO_FIELDS   parent of the case directories (sampled surfaces)
    VEHICLE_AERO_OUT      where animations and large presentation frames land
    VEHICLE_AERO_GEOMETRY parent of the vehicle surfaces used for silhouettes

`geometry/AUTOW.stl` ships with the repository and is found without any
environment variable. The comparator surfaces are third-party and are supplied
by the reader, see geometry/README.md.

Every lookup goes through `field_case`, `geometry` or `out_dir`, so a missing
input reports the path it wanted and the variable that changes it.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))

# Local defaults, recorded so the scripts run unchanged on the machine the
# study was produced on.
DEFAULT_FIELDS = r"D:\Blender\Blender Files\Auto tests\cfd"
DEFAULT_OUT = r"D:\Blender\Blender Files\Auto tests\report"

# Case name -> sampled-surface directory, relative to the fields root. The
# layout differs between cases because the earlier runs predate the move to
# postProcessing/.
CASE_DIR = {
    "F": os.path.join("pedPlanes"),
    "D": os.path.join("pedPlanesD", "pedPlanes"),
    "W": os.path.join("wagonrD", "postProcessing", "pedPlanes"),
    "R": os.path.join("autowR", "postProcessing", "pedPlanes"),
}

# Case name -> surface used for the vehicle silhouette in the animations.
CASE_STL = {
    "F": "AUTOW.stl",
    "D": "AUTOW.stl",
    "R": "AUTOW.stl",
    "W": "WAGONR.stl",
}

_MISSING = """{what} not found:
    {path}
Set {var} to the directory holding it, or see {doc}."""


def fields_root():
    return os.environ.get("VEHICLE_AERO_FIELDS", DEFAULT_FIELDS)


def out_dir():
    d = os.environ.get("VEHICLE_AERO_OUT", DEFAULT_OUT)
    os.makedirs(d, exist_ok=True)
    return d


def field_case(case, required=True):
    """Sampled-surface directory for one case letter."""
    path = os.path.join(fields_root(), CASE_DIR[case])
    if required and not os.path.isdir(path):
        raise SystemExit(_MISSING.format(
            what="sampled surfaces for case " + case, path=path,
            var="VEHICLE_AERO_FIELDS", doc="cases/README.md"))
    return path


def geometry(name, required=True):
    """A vehicle surface. `geometry/` in the repository is searched first."""
    for base in (os.path.join(REPO, "geometry"),
                 os.environ.get("VEHICLE_AERO_GEOMETRY", ""),
                 r"C:\Temp"):
        if not base:
            continue
        path = os.path.join(base, name)
        if os.path.isfile(path):
            return path
    if required:
        raise SystemExit(_MISSING.format(
            what="vehicle surface " + name,
            path=os.path.join(REPO, "geometry", name),
            var="VEHICLE_AERO_GEOMETRY", doc="geometry/README.md"))
    return None


def report():
    """One line per input, for checking a fresh checkout."""
    lines = ["fields root: " + fields_root(), "output dir : " + out_dir()]
    for c in sorted(CASE_DIR):
        p = field_case(c, required=False)
        lines.append("case %s: %s  %s" % (c, "present" if os.path.isdir(p) else "absent", p))
    for n in sorted(set(CASE_STL.values())):
        p = geometry(n, required=False)
        lines.append("stl %-12s %s" % (n, p if p else "absent"))
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
