"""Drawing pieces shared by the still (gustfig.py) and the video (gustvid.py).

One source of truth for the vehicle silhouette, the human figure and the colour
ramp, so the two cannot drift apart and disagree about the same scene.
"""
import numpy as np
from scipy import ndimage
from scipy.spatial import Delaunay, cKDTree
from scipy.interpolate import LinearNDInterpolator
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

EYE = 1.60
BG = "#080b12"
VMAX = 3.2


class Resampler:
    """Linear interpolation onto the plotting grid -- NOT nearest-neighbour.

    Nearest-neighbour paints every CFD cell as a hard-edged block. That is
    invisible while the mesh is fine and severe once it is not: measured cell
    spacing on this plane is 0.125 m out to x = 12 m, then 0.25 m to x = 24 m,
    then 0.50 m (and 0.25/0.50 m above z = 4/7 m) -- the snappyHexMesh
    refinement boxes. On a 0.035 m plotting grid that is a 4 px block near the
    vehicle but a 14 px stair-step in the far wake, with dead-straight seams
    where the boxes end.

    It reads as structure in the wind. It is the mesh. A gaussian_filter of
    sigma ~1 px cannot remove a 14 px block, and raising sigma enough to do so
    would smear away the real near-field detail.

    The Delaunay triangulation is built ONCE per case: the sample points are
    identical in every snapshot (same plane, same mesh), which the callers
    already assert.
    """

    def __init__(self, pts):
        self.tri = Delaunay(pts)
        self.near = cKDTree(pts)          # fallback outside the convex hull

    def __call__(self, vals, q, nan_outside=False):
        """nan_outside=True leaves query points beyond the data as NaN.

        The nearest-neighbour fallback is fine for the small gaps INSIDE the
        hull (the vehicle body), but it is wrong past the domain outlet: the
        pedestrian frame extends to x ~ 30.8 m against a 30 m outlet, so the
        right edge of every late frame had no data and was being painted with
        the last available cells. Out there the cells are 0.50 m, which is a
        ~20 px rectangle -- the blockiness the linear interpolation was meant
        to kill, reappearing exactly where there was nothing to interpolate.
        Draw nothing where nothing was computed; pair with cmap.set_bad(BG).
        """
        vals = np.asarray(vals)
        f = LinearNDInterpolator(self.tri, vals)(q)
        bad = ~np.isfinite(f)             # query points outside the hull
        if bad.any() and not nan_outside:
            f[bad] = vals[self.near.query(q[bad])[1]]
        return f

    def outside(self, q):
        """Boolean mask of query points beyond the data.

        Kept separate from __call__ so the field can be smoothed on a
        nearest-FILLED array and only then blanked. Smoothing an array that
        already contains NaN propagates the NaN one kernel-width inwards and
        eats a stripe of real data at the boundary.
        """
        return self.tri.find_simplex(q) < 0

# deep blue -> blue -> cyan -> green -> yellow -> white, as in the Blender renders
CMAP = LinearSegmentedColormap.from_list(
    "gust", ["#080b12", "#101d3d", "#1b3c7a", "#2478c0", "#38bcd8",
             "#8fe0a8", "#ffd94d", "#ffffff"])
# NaN (no data past the domain outlet) renders as background, not as colour --
# see Resampler.outside(). Without this matplotlib draws NaN transparent, which
# over a dark axes happens to look right but leaks through anything underneath.
CMAP.set_bad(BG)


def stl_profile(path):
    """Filled (x, z) silhouette of a binary STL.

    Grid resolution is derived from the STL's own vertex count. The two wraps
    differ 11x in triangle count, so one fixed grid either dithers the sparse
    WagonR into confetti or blurs the dense auto into a featureless box. Both
    happened. Blur-then-threshold was worse still: at any threshold loose enough
    to close the WagonR it filled the auto's whole bounding rectangle.
    """
    raw = open(path, "rb").read()
    ntri = int(np.frombuffer(raw, dtype="<u4", count=1, offset=80)[0])
    rec = np.frombuffer(raw, dtype=np.uint8, count=ntri * 50, offset=84
                        ).reshape(ntri, 50)
    v = np.frombuffer(rec[:, 12:48].tobytes(), dtype="<f4").reshape(-1, 3)
    x, z = v[:, 0].astype(float), v[:, 2].astype(float)
    nx = int(np.clip(np.sqrt(len(v)) / 2.2, 70, 300))
    nz = max(int(nx * (z.max() - 0.0) / max(x.max() - x.min(), 1e-6)), 40)
    xe = np.linspace(x.min(), x.max(), nx + 1)
    ze = np.linspace(0.0, max(z.max(), 0.1), nz + 1)
    H, _, _ = np.histogram2d(x, z, bins=[xe, ze])
    occ = ndimage.binary_fill_holes(
        ndimage.binary_closing(H > 0, np.ones((3, 3))))
    return (xe[:-1] + xe[1:]) / 2, (ze[:-1] + ze[1:]) / 2, occ.T, x.min(), x.max()


def stl_plan(path):
    """Filled (x, y) silhouette -- the same trick as stl_profile, seen from above.

    Shares the vertex-count-derived resolution rule, which is the part that
    actually mattered: a fixed grid dithers the sparse WagonR wrap into confetti
    and blurs the dense auto into a box.
    """
    raw = open(path, "rb").read()
    ntri = int(np.frombuffer(raw, dtype="<u4", count=1, offset=80)[0])
    rec = np.frombuffer(raw, dtype=np.uint8, count=ntri * 50, offset=84
                        ).reshape(ntri, 50)
    v = np.frombuffer(rec[:, 12:48].tobytes(), dtype="<f4").reshape(-1, 3)
    x, y = v[:, 0].astype(float), v[:, 1].astype(float)
    nx = int(np.clip(np.sqrt(len(v)) / 2.2, 70, 300))
    ny = max(int(nx * (y.max() - y.min()) / max(x.max() - x.min(), 1e-6)), 30)
    xe = np.linspace(x.min(), x.max(), nx + 1)
    ye = np.linspace(y.min(), y.max(), ny + 1)
    H, _, _ = np.histogram2d(x, y, bins=[xe, ye])
    occ = ndimage.binary_fill_holes(
        ndimage.binary_closing(H > 0, np.ones((3, 3))))
    return (xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2, occ.T


def person(ax, x=0.0, col="#ff4f3a", z=10):
    """A recognisable human, so 'up at your face' is legible without a caption."""
    out = [ax.add_patch(plt.Circle((x, 1.66), 0.10, color=col, zorder=z))]
    # The trunk starts at the HIP (0.78), where the legs fork. Drawing it from
    # the ground up instead puts a line straight down between the legs, which
    # reads as anatomy nobody intended.
    for pts, lw in ([([x, x], [0.78, 1.55]), 4.5],
                    [([x - 0.22, x, x + 0.19], [0.86, 1.34, 0.92]), 3.0],
                    [([x - 0.17, x, x + 0.17], [0.0, 0.78, 0.0]), 3.4]):
        out += ax.plot(*pts, color=col, lw=lw, zorder=z, solid_capstyle="round")
    return out
