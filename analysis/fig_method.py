"""Method figures: study workflow, validation, and the geometry acceptance test.

Values come from the committed tables, which record the section of
docs/REPORT.md each one is taken from.
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "data"))
import thesis_style as ts
import tables as T

OUT = os.path.abspath(os.path.join(HERE, "..", "docs", "figures"))


def _box(ax, x, y, w, h, text, face="white", edge="#1A1A1A", fs=9.5, lw=1.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                facecolor=face, edgecolor=edge, lw=lw, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, zorder=3, linespacing=1.35)


def _arrow(ax, p0, p1, style="-|>", color="#1A1A1A", ls="-"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=13,
                                 lw=1.2, color=color, linestyle=ls,
                                 shrinkA=1, shrinkB=1, zorder=1))


def fig_workflow():
    """Study design, from source geometry through to the two result sets."""
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")

    _box(ax, 0.15, 4.55, 1.95, 0.85,
         "source meshes\n4 vehicles", face="#F0F0F0")
    _box(ax, 2.55, 4.55, 2.15, 0.85,
         "voxel wrap\nsigned-distance\nisosurface", face="#F0F0F0")
    _box(ax, 5.15, 4.55, 2.30, 0.85,
         "geometry acceptance\nstreamwise + lateral\nray census", face="#FDECEA")
    _box(ax, 7.90, 4.55, 1.95, 0.85,
         "snappyHexMesh\n0.5 m base cell", face="#F0F0F0")

    # the discontinued branch, kept because it explains the adopted test
    _box(ax, 5.15, 3.05, 2.30, 0.85,
         "0.06 m wrap rejected\nwindscreen erased\n" r"$C_d$ inflated 29%",
         face="white", edge="#B0B0B0", fs=9.0)
    _arrow(ax, (6.30, 4.55), (6.30, 3.90), color="#B0B0B0", ls="--")

    _box(ax, 0.15, 2.15, 2.55, 0.95,
         "steady RANS\n" r"simpleFoam, $k$-$\omega$ SST" "\n1000 iterations",
         face="#F0F0F0")
    _box(ax, 0.15, 0.55, 2.55, 1.05,
         "drag result\n" r"$C_d$, $C_d\!\cdot\!A$, 4 vehicles",
         face="#FDECEA")

    _box(ax, 3.30, 2.15, 3.05, 0.95,
         "transient URANS\n" r"pimpleFoam, 0 to 3 s" "\npassive scalar released\nat road level",
         face="#F0F0F0", fs=9.0)
    _box(ax, 3.30, 0.55, 3.05, 1.05,
         "pedestrian exposure\ngust energy and dust\nalong the walked diagonal",
         face="#FDECEA", fs=9.0)

    _box(ax, 6.95, 2.15, 2.90, 0.95,
         "controls\nmotorBike validation\nmesh refinement\nrepeat with perturbed IC",
         face="#F3EAF7", edge="#8E44AD", fs=8.8)
    _box(ax, 6.95, 0.55, 2.90, 1.05,
         "raised-source run\nsource lifted 0.5 m\nceiling gain measured",
         face="#FBF0E4", edge="#C97A2B", fs=9.0)

    _arrow(ax, (2.10, 4.97), (2.55, 4.97))
    _arrow(ax, (4.70, 4.97), (5.15, 4.97))
    _arrow(ax, (7.45, 4.97), (7.90, 4.97))
    # distribution bus, broken where the rejected-branch arrow crosses it
    _arrow(ax, (8.87, 4.55), (8.87, 4.28))
    _arrow(ax, (8.87, 4.28), (6.52, 4.28), style="-")
    _arrow(ax, (6.08, 4.28), (1.42, 4.28), style="-")
    _arrow(ax, (1.42, 4.28), (1.42, 3.10))
    _arrow(ax, (4.82, 4.28), (4.82, 3.10))
    _arrow(ax, (8.40, 4.28), (8.40, 3.10))
    _arrow(ax, (1.42, 2.15), (1.42, 1.60))
    _arrow(ax, (4.82, 2.15), (4.82, 1.60))
    _arrow(ax, (8.40, 2.15), (8.40, 1.60))

    ax.text(0.15, 5.72, "Every case derives from the validated motorBike tutorial. "
                        "Only geometry and reference quantities change.",
            fontsize=9.5, color="#5A5A5A")
    ts.save(fig, os.path.join(OUT, "fig01_workflow.png"))


def fig_validation():
    """Validation against the motorBike tutorial and against published ranges."""
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(9.4, 4.0),
                                  gridspec_kw=dict(width_ratios=[1, 1.25]))
    v = T.VALIDATION
    for i, (name, val) in enumerate((("$C_d$", v["cd"]), ("$C_l$", v["cl"]))):
        for j, mach in enumerate(("Ryzen 5 3600", "Ryzen 5 5600X")):
            ax.plot(i + (j - 0.5) * 0.22, val, color=ts.C["robust"],
                    **ts.marks(markerfacecolor=ts.C["robust"] if j == 0 else "white",
                               markersize=10, ls="none"))
        ax.text(i + 0.30, val, f"{val:.4f}", va="center", fontsize=10,
                color=ts.C["robust"])
    ax.set_xticks([0, 1]); ax.set_xticklabels(["$C_d$", "$C_l$"])
    ax.set_ylabel("coefficient")
    ax.set_xlim(-0.6, 1.7); ax.set_ylim(-0.05, 0.55)
    ax.text(-0.5, 0.50, "motorBike tutorial,\nreproduced on two machines",
            fontsize=9.5, color="#5A5A5A", va="top")
    ax.text(-0.5, 0.02, "filled and open markers are\nthe two machines. They agree\n"
                        "to the last written digit.",
            fontsize=8.8, color="#5A5A5A", va="bottom")
    ts.panel(ax, "a", dx=-0.17)

    order = ["dzire", "wagonr"]
    for i, k in enumerate(order):
        lo, hi = T.PUBLISHED[k]
        axb.add_patch(Rectangle((i - 0.26, lo), 0.52, hi - lo,
                                facecolor="#D9D9D9", edgecolor="none", zorder=0))
        axb.plot(i, T.DRAG[k]["cd"], color=ts.C[k],
                 **ts.marks(markerfacecolor=ts.C[k], markersize=10, ls="none"))
        axb.text(i + 0.16, T.DRAG[k]["cd"], f"{T.DRAG[k]['cd']:.3f}",
                 va="center", fontsize=10, color=ts.C[k])
    axb.set_xticks(range(len(order)))
    axb.set_xticklabels(["Maruti Dzire\n(subcompact sedan)",
                         "Maruti WagonR\n(tall hatchback)"])
    axb.set_ylabel("$C_d$"); axb.set_ylim(0.24, 0.40); axb.set_xlim(-0.6, 1.6)
    axb.add_patch(Rectangle((0.85, 0.252), 0.16, 0.010, facecolor="#D9D9D9",
                            edgecolor="none"))
    axb.text(1.05, 0.257, "published range for the class", va="center",
             fontsize=9.5, color="#5A5A5A")
    ts.panel(axb, "b", dx=-0.14)
    fig.subplots_adjust(wspace=0.34)
    ts.save(fig, os.path.join(OUT, "fig02_validation.png"))


def fig_census():
    """The geometry acceptance test, applied to a 0.06 m and a 0.03 m wrap."""
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(9.4, 4.2))
    L = T.VEHICLE_LENGTH

    z = np.array(sorted(T.RAY_CENSUS))
    raw = np.array([T.RAY_CENSUS[h][0] for h in z])
    bad = [T.RAY_CENSUS[h][1] for h in z]
    ax.axvspan(0, L, color="#F0F0F0", zorder=0)
    ax.text(L - 0.05, 1.02, "vehicle extent", ha="right", fontsize=9.5,
            color="#5A5A5A")
    ax.plot(raw, z, color=ts.C["ref"], label="raw source",
            **ts.marks(markerfacecolor=ts.C["ref"], markersize=8))
    for h, b in zip(z, bad):
        if b is None:
            ax.plot(L - 0.06, h, marker="x", color=ts.C["auto"], markersize=10,
                    markeredgewidth=2.0, ls="none")
            ax.text(L - 0.16, h, "no hit", ha="right", va="center",
                    fontsize=9.5, color=ts.C["auto"])
        else:
            ax.plot(b, h, color=ts.C["auto"],
                    **ts.marks(markerfacecolor=ts.C["auto"], markersize=8,
                               ls="none"))
            ax.annotate("", xy=(b, h), xytext=(raw[list(z).index(h)], h),
                        arrowprops=dict(arrowstyle="->", color=ts.C["auto"], lw=1.3))
            ax.text(b - 0.06, h - 0.045, "ray flew 2.23 m into the body",
                    ha="right", va="top", fontsize=9, color=ts.C["auto"])
    ax.plot([], [], color=ts.C["auto"],
            **ts.marks(markerfacecolor=ts.C["auto"], ls="none"),
            label="0.06 m wrap")
    ax.set_xlabel("streamwise first-hit distance (m)")
    ax.set_ylabel("height above road (m)")
    ax.set_xlim(0, 2.9); ax.set_ylim(1.05, 1.58)
    ax.legend(loc="upper left")
    ts.panel(ax, "a", dx=-0.15)

    zb = np.array(sorted(T.BUS_CENSUS))
    rb = np.array([T.BUS_CENSUS[h][0] for h in zb])
    wb = np.array([T.BUS_CENSUS[h][1] for h in zb])
    axb.plot(rb, zb, color=ts.C["ref"], label="raw source",
             **ts.marks(markerfacecolor=ts.C["ref"], markersize=8))
    axb.plot(wb, zb, color=ts.C["bus"], ls="--", label="0.03 m wrap",
             **ts.marks(markerfacecolor="white", markersize=8))
    for h, r, w in zip(zb, rb, wb):
        axb.annotate("", xy=(w, h), xytext=(r, h),
                     arrowprops=dict(arrowstyle="->", color="#9A9A9A", lw=1.0))
    axb.set_xlabel("streamwise first-hit distance (m)")
    axb.set_ylabel("height above road (m)")
    axb.set_xlim(0.25, 0.78)
    axb.legend(loc="upper left")
    axb.text(0.30, 1.05, "every height present in the source is\n"
                         "present in the wrap, offset 3 to 7 cm\n"
                         "in one consistent direction",
             fontsize=9, color="#5A5A5A", va="bottom")
    ts.panel(axb, "b", dx=-0.15)
    fig.subplots_adjust(wspace=0.30)
    ts.save(fig, os.path.join(OUT, "fig12_geometry_census.png"))


if __name__ == "__main__":
    ts.apply()
    os.makedirs(OUT, exist_ok=True)
    fig_workflow()
    fig_validation()
    fig_census()
