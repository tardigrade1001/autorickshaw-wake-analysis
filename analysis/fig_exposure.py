"""Pedestrian exposure figures.

Dust figures read data/diagonal_profiles.npz, written by extract_diagonal.py.
Gust-energy and vertical-transport figures read the committed tables, which
record the section of docs/REPORT.md each value comes from.
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "data"))
import thesis_style as ts
import tables as T

OUT = os.path.abspath(os.path.join(HERE, "..", "docs", "figures"))
D = np.load(os.path.join(HERE, "data", "diagonal_profiles.npz"))
Z = D["heights"]
EYE = 1.66          # the eye level used throughout, in metres


def _peak_mean(name):
    s = D[f"{name}_s"]
    return np.nanmax(s, axis=1), np.nanmean(s, axis=1)


def fig_gust_height():
    """Lateral gust energy against height, three vehicles, with the ratio."""
    z = np.array(sorted(T.GUST))
    a = np.array([T.GUST[k][0] for k in z])
    w = np.array([T.GUST[k][1] for k in z])
    d = np.array([T.GUST[k][2] for k in z])
    fig, (ax, axr) = plt.subplots(1, 2, figsize=(9.4, 4.2), sharey=True)
    for v, k in ((a, "auto"), (w, "wagonr"), (d, "dzire")):
        ax.plot(v, z, color=ts.C[k], label=ts.LABEL[k],
                **ts.marks(markerfacecolor=ts.C[k]))
    ax.set_xlabel("lateral gust energy (J m$^{-3}$)")
    ax.set_ylabel("height above road (m)")
    ax.set_ylim(0, 1.8)
    ax.legend(loc="upper right")
    ts.guides(ax, [(EYE, "eye")])
    ax.text(1.95, EYE + 0.03, "eye level 1.66 m", ha="right", va="bottom",
            fontsize=9.5, color="#5A5A5A")
    ts.panel(ax, "a", dx=-0.14)

    axr.plot(a / w, z, color=ts.C["wagonr"], label="against WagonR",
             **ts.marks(markerfacecolor=ts.C["wagonr"]))
    axr.plot(a / d, z, color=ts.C["dzire"], label="against Dzire",
             **ts.marks(markerfacecolor=ts.C["dzire"]))
    axr.axvline(1.0, color="#1A1A1A", lw=1.0, ls="--")
    axr.text(1.06, 0.06, "parity", fontsize=9.5, color="#5A5A5A")
    axr.set_xlabel("autorickshaw / car  (ratio)")
    axr.set_xlim(0, 3.8)
    axr.legend(loc="upper right")
    ts.guides(axr, [(EYE, "eye")])
    ts.panel(axr, "b", dx=-0.08)
    fig.subplots_adjust(wspace=0.12)
    ts.save(fig, os.path.join(OUT, "fig06_gust_height.png"))


def fig_vertical():
    """Mean signed vertical velocity by height. Positive means lofting."""
    z = np.array(sorted(T.VERTICAL))
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    w = 0.11
    for i, k in enumerate(("auto", "wagonr", "dzire")):
        v = np.array([T.VERTICAL[h][i] for h in z])
        ax.barh(z + (1 - i) * w, v, w, color=ts.C[k], edgecolor="#1A1A1A",
                lw=0.8, label=ts.LABEL[k])
    ax.axvline(0, color="#1A1A1A", lw=1.0)
    ax.set_xlabel("mean vertical velocity (m s$^{-1}$)")
    ax.set_ylabel("height above road (m)")
    ax.set_yticks(z)
    ax.legend(loc="lower right")
    ax.text(0.30, 1.74, "positive means lofting", fontsize=9.5, color="#5A5A5A")
    ts.save(fig, os.path.join(OUT, "fig07_vertical_transport.png"))


def fig_dust_height():
    """Dust concentration against height along the pedestrian diagonal."""
    pa, ma = _peak_mean("auto")
    pw, mw = _peak_mean("wagonr")
    fig, (ax, axr) = plt.subplots(1, 2, figsize=(9.4, 4.2), sharey=True)
    ax.plot(pa, Z, color=ts.C["auto"], label="Autorickshaw, peak")
    ax.plot(pw, Z, color=ts.C["wagonr"], label="WagonR, peak")
    ax.plot(ma, Z, color=ts.C["auto"], ls="--", lw=1.3, label="Autorickshaw, mean")
    ax.plot(mw, Z, color=ts.C["wagonr"], ls="--", lw=1.3, label="WagonR, mean")
    ax.set_xlabel("dust tracer concentration (fraction of source)")
    ax.set_ylabel("height above road (m)")
    ax.set_ylim(0, 2.4)
    ax.set_xlim(0, 1.05)
    ax.legend(loc="upper right")
    ts.guides(ax, [(1.00, "waist"), (EYE, "eye")])
    ax.text(0.02, 1.02, "waist", ha="left", va="bottom", fontsize=9.5,
            color="#5A5A5A")
    ax.text(0.02, EYE + 0.02, "eye level", ha="left", va="bottom",
            fontsize=9.5, color="#5A5A5A")
    ts.panel(ax, "a", dx=-0.14)

    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(pw > 0.02, pa / pw, np.nan)
    axr.plot(r, Z, color=ts.C["auto"],
             **ts.marks(markerfacecolor=ts.C["auto"], markersize=4))
    axr.axvline(1.0, color="#1A1A1A", lw=1.0, ls="--")
    axr.set_xlabel("autorickshaw / WagonR  (ratio of peak)")
    axr.set_xscale("log")
    axr.set_xlim(0.7, 40)
    ts.guides(axr, [(1.00, "waist"), (EYE, "eye")])
    iw = int(np.argmin(np.abs(Z - 1.00)))
    axr.annotate(f"{r[iw]:.0f}x at waist", xy=(r[iw], 1.00), xytext=(3.0, 0.55),
                 fontsize=10, color=ts.C["auto"],
                 arrowprops=dict(arrowstyle="->", color=ts.C["auto"], lw=1.0))
    axr.text(0.78, 2.42, "shown only where the car concentration\n"
                         "exceeds 0.02 of source",
             fontsize=9, color="#5A5A5A", va="top")
    ts.panel(axr, "b", dx=-0.08)
    fig.subplots_adjust(wspace=0.12)
    ts.save(fig, os.path.join(OUT, "fig08_dust_height.png"))


def fig_arrival():
    """Dust arrival at the pedestrian against time since the vehicle passed."""
    show = [0.20, 0.60, 1.00, 1.40]
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 6.4), sharex=True)
    for ax, h, letter in zip(axes.ravel(), show, "abcd"):
        i = int(np.argmin(np.abs(Z - h)))
        for name, k in (("auto", "auto"), ("wagonr", "wagonr")):
            ax.plot(D[f"{name}_tau"], D[f"{name}_s"][i],
                    color=ts.C[k], lw=1.4, label=ts.LABEL[k])
        ax.set_title(f"{Z[i]:.2f} m above the road", fontsize=11)
        ax.set_ylim(0, 1.05)
        ax.set_xlim(0, 2.3)
        ts.panel(ax, letter, dx=-0.13)
        if letter == "a":
            ax.legend(loc="upper right")
    for ax in axes[1]:
        ax.set_xlabel("time since the vehicle passed (s)")
    for ax in axes[:, 0]:
        ax.set_ylabel("tracer concentration")
    fig.subplots_adjust(hspace=0.30, wspace=0.18)
    ts.save(fig, os.path.join(OUT, "fig09_dust_arrival.png"))


def fig_column():
    """Column integral of the tracer, separating redistribution from creation."""
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(9.4, 4.0),
                                  gridspec_kw=dict(width_ratios=[1.5, 1]))
    stat = {}
    for name, k in (("auto", "auto"), ("wagonr", "wagonr")):
        s = np.nan_to_num(D[f"{name}_s"])
        # Z spans 0 to 2.5 m inclusive, so trapezoid integrates the whole
        # column exactly, including the 0 to 0.05 m band where the car
        # concentration peaks. Truncating the bottom biases the comparison.
        col = np.trapezoid(s, Z, axis=0) if hasattr(np, "trapezoid")             else np.trapz(s, Z, axis=0)
        ax.plot(D[f"{name}_tau"], col, color=ts.C[k], lw=1.4, label=ts.LABEL[k])
        stat[name] = (float(col.mean()), float(col.std()))
    ax.set_xlabel("time since the vehicle passed (s)")
    ax.set_ylabel("column integral of tracer (m)")
    ax.set_xlim(0, 2.3)
    ax.legend(loc="lower right")
    ts.panel(ax, "a", dx=-0.13)

    x = [0, 1]
    axb.bar(x, [stat["auto"][0], stat["wagonr"][0]],
            yerr=[stat["auto"][1], stat["wagonr"][1]], width=0.55,
            color=[ts.C["auto"], ts.C["wagonr"]], edgecolor="#1A1A1A", lw=0.9,
            capsize=5, error_kw=dict(elinewidth=1.3))
    for i, n in enumerate(("auto", "wagonr")):
        axb.text(i, stat[n][0] + stat[n][1] + 0.015, f"{stat[n][0]:.3f}",
                 ha="center", fontsize=10)
    axb.set_xticks(x)
    axb.set_xticklabels(["Auto", "WagonR"])
    axb.set_ylabel("column integral (m)")
    ts.panel(axb, "b", dx=-0.22)
    fig.subplots_adjust(wspace=0.34)
    ts.save(fig, os.path.join(OUT, "fig10_column_integral.png"))
    print("  column integral  auto %.3f sd %.3f   wagonr %.3f sd %.3f"
          % (stat["auto"][0], stat["auto"][1], stat["wagonr"][0], stat["wagonr"][1]))


def fig_source_height():
    """The source-height experiment: how far dust rises above where it starts."""
    pa, _ = _peak_mean("auto")
    pr, _ = _peak_mean("auto_raised")
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(9.4, 4.2),
                                  gridspec_kw=dict(width_ratios=[1.3, 1]))
    ax.fill_betweenx([0.0, 0.5], 0, 1.05, color=ts.C["auto"], alpha=0.09)
    ax.fill_betweenx([0.5, 1.0], 0, 1.05, color=ts.C["raised"], alpha=0.12)
    ax.plot(pa, Z, color=ts.C["auto"], label="source 0.0 to 0.5 m")
    ax.plot(pr, Z, color=ts.C["raised"], label="source 0.5 to 1.0 m")
    ax.set_xlabel("peak tracer concentration")
    ax.set_ylabel("height above road (m)")
    ax.set_ylim(0, 2.4)
    ax.set_xlim(0, 1.05)
    ax.legend(loc="upper right")
    ts.guides(ax, [(EYE, "eye")])
    ax.text(1.02, EYE + 0.02, "eye level", ha="right", va="bottom",
            fontsize=9.5, color="#5A5A5A")
    ts.panel(ax, "a", dx=-0.14)

    thr = 0.05

    def ceiling(p):
        ok = np.where(p >= thr)[0]
        return float(Z[ok[-1]]) if len(ok) else float("nan")

    ca, cr = ceiling(pa), ceiling(pr)
    axb.bar([0, 1], [ca, cr], width=0.55, color=[ts.C["auto"], ts.C["raised"]],
            edgecolor="#1A1A1A", lw=0.9)
    axb.bar([0, 1], [0.5, 1.0], width=0.55, color="none", edgecolor="#1A1A1A",
            lw=1.2, ls="--")
    for i, c in enumerate((ca, cr)):
        axb.text(i, c + 0.04, f"{c:.2f} m", ha="center", fontsize=10)
    axb.axhline(EYE, color="#1A1A1A", lw=1.0, ls=":")
    axb.text(1.42, EYE + 0.03, "eye level", ha="right", va="bottom",
             fontsize=9.5, color="#5A5A5A")
    axb.set_xticks([0, 1])
    axb.set_xticklabels(["source\n0.0-0.5 m", "source\n0.5-1.0 m"])
    axb.set_ylabel(f"height reached at s = {thr:.2f} (m)")
    axb.set_ylim(0, 1.95)
    axb.text(-0.44, 1.80, "dashed line: top of the source layer",
             fontsize=9, color="#5A5A5A")
    ts.panel(axb, "b", dx=-0.30, dy=1.09)
    fig.subplots_adjust(wspace=0.34)
    ts.save(fig, os.path.join(OUT, "fig11_source_height.png"))
    print(f"  ceiling at s={thr}:  base {ca:.2f} m   raised {cr:.2f} m   "
          f"gain {cr - ca:.2f} m for a 0.50 m lift")


if __name__ == "__main__":
    ts.apply()
    os.makedirs(OUT, exist_ok=True)
    fig_gust_height()
    fig_vertical()
    fig_dust_height()
    fig_arrival()
    fig_column()
    fig_source_height()
