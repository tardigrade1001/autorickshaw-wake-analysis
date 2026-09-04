"""Compute pedestrian-diagonal dust profiles and commit them as derived data.

Run once against the raw sampled planes. Writes data/diagonal_profiles.npz so
every exposure figure regenerates without the multi-gigabyte field data.

In the solve frame the vehicle is fixed and the pedestrian tracks x = -12 + U*t,
passing the vehicle at t_pass = 12/U. Time since the pass is tau = t - t_pass and
the pedestrian then sits at x = U*tau. Sampling that diagonal converts wake age
into the exposure history a walking person actually receives. A plane-wide
maximum is a different quantity and must not be substituted for it.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dustplane as dp

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data",
                   "diagonal_profiles.npz")
HEIGHTS = np.round(np.linspace(0.0, 2.5, 51), 4)   # 0 to 2.5 m inclusive, hits round heights
CASES = {"auto": "D", "wagonr": "W", "auto_raised": "R"}


def main():
    out = {"heights": HEIGHTS}
    for name, key in CASES.items():
        dp.use(key)
        tau, cur = dp.arrival(tuple(HEIGHTS))
        m = np.vstack([cur[h] for h in HEIGHTS])       # (n_heights, n_tau)
        out[f"{name}_tau"] = tau
        out[f"{name}_s"] = m.astype(np.float32)
        print(f"{name:12s} case {key}  {m.shape[0]} heights x {m.shape[1]} diagonal points")
    np.savez_compressed(OUT, **out)
    print("wrote", OUT, f"{os.path.getsize(OUT)/1048576:.1f} MB")


if __name__ == "__main__":
    main()
