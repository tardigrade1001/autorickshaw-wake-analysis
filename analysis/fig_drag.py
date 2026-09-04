"""Drag figures. Source data: analysis/data/*.dat, written by forceCoeffs.

Every value is computed here from the committed histories. The tables module is
used only for reference quantities and for the withdrawn result.
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
import thesis_style as ts
import tables as T

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.abspath(os.path.join(HERE, "..", "docs", "figures"))
FILE = {"auto": "AUTOW.dat", "wagonr": "WAGONR.dat",
        "dzire": "DZIRE.dat", "bus": "BUS.dat"}
ORDER = ["dzire", "wagonr", "auto", "bus"]
SHORT = {"dzire": "Dzire", "wagonr": "WagonR", "auto": "Auto", "bus": "Bus"}
WINDOW = 200          # the averaging window the report uses


def history(key):
    """-> (iteration, Cd) from a forceCoeffs .dat file."""
    a = np.loadtxt(os.path.join(DATA, FILE[key]), comments="#")
    return a[:, 0], a[:, 1]


def stats(key):
    """Mean and band over the final WINDOW iterations, as the report defines them."""
    _, cd = history(key)
    w = cd[-WINDOW:]
    return w.mean(), (w.max() - w.min()) / w.mean()


def fig_convergence():
    """Cd against iteration, all four vehicles, with the averaging window marked."""
    fig, (ax, axz) = plt.subplots(1, 2, figsize=(9.4, 4.0),
                                  gridspec_kw=dict(width_ratios=[1.35, 1]))
    for k in ORDER:
        it, cd = history(k)
        ax.plot(it, cd, color=ts.C[k], lw=1.4, label=ts.LABEL[k])
        axz.plot(it, cd, color=ts.C[k], lw=1.4)
    ax.set_xlim(0, 1000); ax.set_ylim(0, 1.4)
    ax.set_xlabel("Iteration"); ax.set_ylabel(r"$C_d$")
    ax.legend(loc="upper right")
    ts.panel(ax, "a", dx=-0.13)

    axz.axvspan(800, 1000, color="#E8E8E8", zorder=0)
    axz.text(900, 0.565, "averaging\nwindow", ha="center", va="top",
             fontsize=9.5, color="#5A5A5A")
    for k in ORDER:
        m, b = stats(k)
        axz.axhline(m, color=ts.C[k], lw=0.7, ls="--", zorder=1)
    axz.set_xlim(600, 1000); axz.set_ylim(0.24, 0.58)
    axz.set_xlabel("Iteration"); axz.set_ylabel(r"$C_d$")
    ts.panel(axz, "b", dx=-0.18)
    fig.subplots_adjust(wspace=0.30)
    ts.save(fig, os.path.join(OUT, "fig03_cd_convergence.png"))


def fig_drag_summary():
    """Cd with its oscillation band, against published ranges where they exist."""
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    for i, k in enumerate(ORDER):
        m, b = stats(k)
        half = 0.5 * b * m
        ax.errorbar(i, m, yerr=half, color=ts.C[k], capsize=4, elinewidth=1.4,
                    **ts.marks(markerfacecolor=ts.C[k], markersize=9, ls="none"))
        ax.text(i + 0.14, m, f"{m:.3f}", va="center", fontsize=10, color=ts.C[k])
        if k in T.PUBLISHED:
            lo, hi = T.PUBLISHED[k]
            ax.add_patch(Rectangle((i - 0.30, lo), 0.60, hi - lo,
                                   facecolor="#D9D9D9", edgecolor="none", zorder=0))
    w = T.WITHDRAWN_AUTO
    ia = ORDER.index("auto")
    ax.errorbar(ia, w["cd"], yerr=0.5 * w["band"] * w["cd"], color="#B0B0B0",
                capsize=4, elinewidth=1.2,
                **ts.marks(markerfacecolor="white", markeredgecolor="#B0B0B0",
                           markersize=8, ls="none"))
    ax.annotate("withdrawn\n(corrupted geometry)", xy=(ia, w["cd"]),
                xytext=(ia - 0.75, 0.72), fontsize=9, color="#7A7A7A",
                ha="center",
                arrowprops=dict(arrowstyle="-", color="#B0B0B0", lw=0.9))
    ax.add_patch(Rectangle((-0.45, 0.175), 0.28, 0.028, facecolor="#D9D9D9",
                           edgecolor="none"))
    ax.text(-0.10, 0.189, "published range for the class", va="center",
            fontsize=9.5, color="#5A5A5A")
    ax.set_xticks(range(len(ORDER)))
    ax.set_xticklabels([ts.LABEL[k].replace(" ", "\n") for k in ORDER])
    ax.set_ylabel(r"$C_d$"); ax.set_ylim(0.15, 0.80); ax.set_xlim(-0.6, 3.6)
    ts.save(fig, os.path.join(OUT, "fig04_cd_summary.png"))


def fig_cda():
    """Cd.A drawn as the area it physically is, beside frontal area."""
    fig, (ax, axr) = plt.subplots(1, 2, figsize=(9.4, 4.0),
                                  gridspec_kw=dict(width_ratios=[1, 1.15]))
    x = np.arange(len(ORDER))
    aref = [T.DRAG[k]["aref"] for k in ORDER]
    cda = [stats(k)[0] * T.DRAG[k]["aref"] for k in ORDER]
    ax.bar(x - 0.19, aref, 0.36, color="#D9D9D9", edgecolor="#1A1A1A", lw=0.9,
           label=r"frontal area $A$")
    ax.bar(x + 0.19, cda, 0.36, color=[ts.C[k] for k in ORDER],
           edgecolor="#1A1A1A", lw=0.9, label=r"$C_d\cdot A$")
    ax.set_xticks(x); ax.set_xticklabels([SHORT[k] for k in ORDER])
    ax.set_ylabel(r"m$^2$"); ax.legend(loc="upper left")
    ts.panel(ax, "a", dx=-0.15)

    # Cd.A as literal squares at true relative scale
    axr.set_aspect("equal")
    xc = 0.0
    for k in ORDER:
        v = stats(k)[0] * T.DRAG[k]["aref"]
        s = np.sqrt(v)
        axr.add_patch(Rectangle((xc, 0), s, s, facecolor=ts.C[k],
                                edgecolor="#1A1A1A", lw=1.0, alpha=0.85))
        axr.text(xc + s / 2, -0.14, f"{v:.2f}", ha="center", va="top", fontsize=10)
        xc += s + 0.16
    axr.set_xlim(-0.1, xc); axr.set_ylim(-0.42, 2.15)
    axr.set_yticks([]); axr.set_xticks([])
    for sp in axr.spines.values():
        sp.set_visible(False)
    axr.set_title(r"$C_d\cdot A$ at true relative scale (m$^2$)", fontsize=11, pad=12)
    ts.panel(axr, "b", dx=-0.06, dy=1.10)
    ts.save(fig, os.path.join(OUT, "fig05_drag_area.png"))


if __name__ == "__main__":
    ts.apply()
    os.makedirs(OUT, exist_ok=True)
    fig_convergence()
    fig_drag_summary()
    fig_cda()
    print("\ncomputed from the committed histories:")
    for k in ORDER:
        m, b = stats(k)
        print(f"  {ts.LABEL[k]:16s} Cd={m:.4f}  band={b*100:.1f}%  "
              f"CdA={m*T.DRAG[k]['aref']:.3f}")
