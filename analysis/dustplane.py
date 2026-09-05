"""AUTOW_F pedestrian-plane analysis.

The sampled surface is a VERTICAL plane at y = 1.2 m (the pedestrian standoff),
NOT a horizontal plane at 1.2 m height:

    y1p2 { type cuttingPlane; point (0 1.2 0); normal (0 1 0); }

so x is streamwise (-12 .. 65 m), z is height (0 .. 10 m).

Two jobs, in this order:

  control()  face-band lateral KE at z = 1.60 m in the near-body window.
             refineNear was deliberately unchanged from AUTOW_T2, so this
             number must reproduce T2's. If it drifts, the domain extension
             changed something and no tracer result is trustworthy yet.

  arrival()  road tracer s along the pedestrian diagonal. In the solve frame
             the vehicle is fixed and the pedestrian tracks x = -12 + U*t,
             passing the vehicle at t_pass = 12/U. Time since the vehicle
             passed is tau = t - t_pass, and the pedestrian then sits at
             x = U*tau. Sampling the (t, x) diagonal is what converts wake
             age into the quantity he actually described.
"""

import os, sys, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import paths

# The four transient cases. Directories resolve through paths.py, which reads
# VEHICLE_AERO_FIELDS; the sampled surfaces are too large to ship.
#   F  diffusive wall source -- tracer was a NULL, kept for the velocity result
#   D  advected inlet layer (s=1 below 0.3 m) + setFields seeding -- the fix
#   W  WagonR, same dust supply / domain / refinement / schemes as D. Only the
#      vehicle STL and the 4 forceCoeffs constants differ.
#   R  autorickshaw again, dust supply RAISED to 0.5-1.0 m. Same 0.5 m slab
#      thickness D really supplied (the coarse cell at z=0.25 fills 0-0.5 m),
#      lifted exactly 0.5 m. Single-variable test of source height.
CASES = dict(paths.CASE_DIR)
ROOT = paths.field_case("D")
U = 16.67                 # 60 km/h inlet, matches 0.orig/U
X0 = -12.0                # inlet plane = pedestrian start
T_PASS = -X0 / U          # 0.720 s, pedestrian abreast of the vehicle

_cache = {}


def use(case):
    """Switch case ('F', 'D', 'W' or 'R'). Clears the cache -- it is keyed by time only."""
    global ROOT
    ROOT = paths.field_case(case)
    _cache.clear()
    return ROOT


def times():
    ts = sorted(float(os.path.basename(d)) for d in glob.glob(os.path.join(ROOT, "*"))
                if os.path.isdir(d))
    return np.array(ts)


def _dirname(t):
    # directory names are the unrounded write times; match by nearest
    if "dirs" not in _cache:
        _cache["dirs"] = {float(os.path.basename(d)): d
                          for d in glob.glob(os.path.join(ROOT, "*")) if os.path.isdir(d)}
    d = _cache["dirs"]
    k = min(d, key=lambda v: abs(v - t))
    return d[k], k


def load(t, field="s"):
    """-> (x, z, values). values is (n,) for s, (n,3) for U."""
    key = (round(t, 6), field)
    if key in _cache:
        return _cache[key]
    d, _ = _dirname(t)
    a = np.loadtxt(os.path.join(d, f"{field}_y1p2.raw"))
    x, z = a[:, 0], a[:, 2]
    v = a[:, 3] if field == "s" else a[:, 3:6]
    if len(_cache) > 40:                       # 14.7k points x 965 files: cap it
        _cache.clear()
        _cache["dirs"] = {float(os.path.basename(p)): p
                          for p in glob.glob(os.path.join(ROOT, "*")) if os.path.isdir(p)}
    _cache[key] = (x, z, v)
    return x, z, v


def _band(x, z, x0, x1, zc, dz):
    return (x >= x0) & (x <= x1) & (z >= zc - dz) & (z <= zc + dz)


def control(zc=1.60, dz=0.10, x0=-2.0, x1=12.0, n=12):
    """Lateral KE in the near-body face band, averaged over the last n snapshots.

    Lateral = cross-stream, i.e. the components that are zero in the free
    stream: Uy (spanwise) and Uz (vertical). The streamwise Ux is dominated
    by the 16.67 m/s inlet and would swamp the wake signal.
    """
    ts = times()
    vals = []
    for t in ts[-n:]:
        x, z, v = load(t, "U")
        m = _band(x, z, x0, x1, zc, dz)
        if not m.any():
            continue
        ke = 0.5 * (v[m, 1] ** 2 + v[m, 2] ** 2)
        vals.append(ke.mean())
    vals = np.array(vals)
    print(f"control  z={zc:.2f}+/-{dz}  x[{x0},{x1}]  n_snap={len(vals)}  "
          f"cells/snap={int(m.sum())}")
    print(f"         lateral KE mean={vals.mean():.4f}  sd={vals.std():.4f}  "
          f"m2/s2   (compare against AUTOW_T2)")
    return vals.mean()


def profile(t, x_at, dx=0.5, zmax=4.0, nz=41):
    """Vertical tracer profile at streamwise station x_at, one snapshot."""
    x, z, s = load(t, "s")
    m = (np.abs(x - x_at) <= dx) & (z <= zmax)
    if m.sum() < 5:
        return None, None
    edges = np.linspace(0, zmax, nz + 1)
    idx = np.digitize(z[m], edges) - 1
    out = np.full(nz, np.nan)
    for i in range(nz):
        sel = idx == i
        if sel.any():
            out[i] = s[m][sel].mean()
    return 0.5 * (edges[:-1] + edges[1:]), out


def arrival(heights=(0.2, 0.6, 1.0, 1.6, 2.0), dz=0.15, dx=0.6):
    """Tracer concentration at the moving pedestrian, vs time since passing.

    Returns (tau, {height: s}). Only snapshots whose diagonal position is
    inside the domain are used.
    """
    ts = times()
    rows = []
    for t in ts:
        tau = t - T_PASS
        xp = U * tau
        if tau <= 0 or xp > 64.0:
            continue
        x, z, s = load(t, "s")
        m0 = np.abs(x - xp) <= dx
        if m0.sum() < 5:
            continue
        rec = [tau]
        for h in heights:
            m = m0 & (np.abs(z - h) <= dz)
            rec.append(s[m].mean() if m.any() else np.nan)
        rows.append(rec)
    a = np.array(rows)
    return a[:, 0], {h: a[:, i + 1] for i, h in enumerate(heights)}


def report(heights=(0.2, 0.6, 1.0, 1.6, 2.0)):
    tau, cur = arrival(heights)
    print(f"arrival  {len(tau)} points on the diagonal, tau {tau.min():.2f}..{tau.max():.2f} s")
    print(f"{'tau_s':>6} " + " ".join(f"{h:>7.1f}m" for h in heights))
    for lo in np.arange(0, math.floor(tau.max()) + 0.25, 0.25):
        m = (tau >= lo) & (tau < lo + 0.25)
        if not m.any():
            continue
        print(f"{lo:6.2f} " + " ".join(f"{np.nanmean(cur[h][m]):8.4f}" for h in heights))
    print()
    for h in heights:
        v = cur[h]
        ok = ~np.isnan(v)
        if not ok.any():
            continue
        i = int(np.nanargmax(v))
        print(f"  z={h:4.1f} m   peak s={v[i]:.4f} at tau={tau[i]:.2f} s   "
              f"final={v[ok][-1]:.4f}")
    return tau, cur


if __name__ == "__main__":
    control()
    print()
    report()
