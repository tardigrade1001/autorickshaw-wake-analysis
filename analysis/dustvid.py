"""Slow-motion video of the road-dust tracer lofting behind the autorickshaw.

    python dustvid.py [wide|tall] [FPS]

This is AUTOW_D (the advected-layer run), not AUTOW_F. It plots the passive
scalar `s`, which is 1 in air that started in the road-level dust layer and 0
in clean air -- so what you are watching is literally "where the road air went".

WHAT THE VIDEO IS FOR
  The finding is a CEILING, not a plume. The dust front climbs 0.2 -> 0.6 ->
  1.0 m with its peak arriving later at each height (tau = 0.00 / 0.54 / 1.07 s)
  and then stops, well below the face. Both halves matter and the layout says
  both: the field panel shows the delayed climb, and the profile strip pins the
  ceiling against the eye line so the ceiling is visible as measured and
  asserted.

PEDESTRIAN FRAME
  The solve is vehicle-fixed; the pedestrian tracks x = -12 + U*t and passes the
  vehicle at t = 12/U = 0.720 s. Here the PEDESTRIAN is held at x' = 0 and the
  vehicle recedes to -x, which is an exact Galilean shift of the same data, not
  a re-simulation. tau = t - t_pass, so tau = 0 is the moment of passing.

WHY THE PROFILE STRIP IS SAMPLED ON THE DIAGONAL, NOT OVER THE PLANE
  A max over the whole plane finds a transient eddy 30 m downstream and reports
  it as if the pedestrian were standing in it -- that is exactly the error that
  produced a false "dust reaches 1.6 m" call on this dataset. The pedestrian
  occupies ONE x at a time. The strip therefore averages a +/-0.6 m column at
  x' = 0 and nothing else.
"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import imageio_ffmpeg
from gustdraw import stl_profile, person, Resampler

ROOT = r"D:\Blender\Blender Files\Auto tests\cfd\pedPlanesD\pedPlanes"
OUT = r"D:\Blender\Blender Files\Auto tests\report"
STL = r"C:\Temp\auto.stl"

U = 16.67
X0 = -12.0
T_PASS = -X0 / U          # 0.720 s
BG = "#080b12"

# Dust: transparent clean air -> ochre. Deliberately NOT the velocity colormap;
# this is a different quantity and should not be mistaken for the gust figures.
CMAP = LinearSegmentedColormap.from_list("dust", [
    (0.00, "#080b12"), (0.12, "#241a10"), (0.35, "#6b4a1e"),
    (0.60, "#b98436"), (0.82, "#e8be6a"), (1.00, "#fff0c4")])

LAYOUT = sys.argv[1] if len(sys.argv) > 1 else "wide"
FPS = int(sys.argv[2]) if len(sys.argv) > 2 else 30
if LAYOUT not in ("wide", "tall"):
    sys.exit("layout must be wide or tall")

# The x window is set by the aspect ratio, not by taste. With aspect('equal')
# a 19 m x 3 m window is a 6.3:1 letterbox, which leaves two thirds of a 16:9
# frame empty and the field a thin strip. 9.5 m / 3.0 m is 3.2:1, which fills
# the top band; the far tail beyond -7 m is near-uniform and costs nothing.
if LAYOUT == "wide":
    XLIM, ZLIM = (-7.0, 2.5), (0.0, 3.0)
    FIGSIZE, DPI = (16.0, 9.0), 165
    TITLE_FS, LABEL_FS = 26, 17
else:
    # portrait: a 5.0 m span keeps the drawn (equal-aspect) height close to the
    # declared one, so there is no dead band above and below the field
    XLIM, ZLIM = (-3.4, 1.6), (0.0, 3.0)
    FIGSIZE, DPI = (9.0, 16.0), 120
    TITLE_FS, LABEL_FS = 18, 14

GUIDES = [(0.60, "knee"), (1.00, "waist"), (1.60, "EYE LEVEL")]
# heights traced in the history panel, with the colours used for both
HIST = [(0.2, "#fff0c4", "ankle 0.2 m"), (0.6, "#e8be6a", "knee 0.6 m"),
        (1.0, "#c98c3c", "waist 1.0 m"), (1.6, "#ff6b57", "face 1.6 m")]


def snapshots():
    """(tau, dir) for every write whose diagonal position is inside the domain."""
    out = []
    for d in glob.glob(os.path.join(ROOT, "*")):
        if not os.path.isdir(d):
            continue
        t = float(os.path.basename(d))
        tau = t - T_PASS
        if tau < 0 or U * tau > 64.0:
            continue
        out.append((tau, d))
    return sorted(out)


def main():
    snaps = snapshots()
    if not snaps:
        sys.exit("no snapshots on the diagonal -- check ROOT")

    a = np.loadtxt(os.path.join(snaps[0][1], "s_y1p2.raw"))
    pts = np.column_stack([a[:, 0], a[:, 2]])

    # Load every snapshot once and keep it. 473 x 14.7k float64 is ~55 MB, and
    # the loadtxt pass is the dominant cost of the whole render -- doing it
    # twice (once for the history curves, once for the frames) would double the
    # runtime for nothing.
    print(f"loading {len(snaps)} snapshots ...", flush=True)
    S = np.empty((len(snaps), len(a)))
    for i, (_, d) in enumerate(snaps):
        S[i] = np.nan_to_num(np.loadtxt(os.path.join(d, "s_y1p2.raw"))[:, 3],
                             nan=0.0)
    taus = np.array([t for t, _ in snaps])

    # History curves, sampled on the pedestrian diagonal exactly as the profile
    # strip is -- a plane-wide statistic would report an eddy 30 m away.
    hist = {}
    px, pz = pts[:, 0], pts[:, 1]
    for h, _, _ in HIST:
        v = np.empty(len(snaps))
        for i, tau in enumerate(taus):
            m = (np.abs(px - U * tau) <= 0.6) & (np.abs(pz - h) <= 0.15)
            v[i] = S[i][m].mean() if m.any() else np.nan
        hist[h] = v

    # Plot grid is in the PEDESTRIAN frame; the sample points are in the solve
    # frame, so the query grid is shifted per frame and the data stays fixed.
    gx = np.linspace(*XLIM, int((XLIM[1] - XLIM[0]) / 0.035))
    gz = np.linspace(*ZLIM, int((ZLIM[1] - ZLIM[0]) / 0.035))
    GX, GZ = np.meshgrid(gx, gz)
    rs = Resampler(pts)

    vx, vz, vocc, vx0, vx1 = stl_profile(STL)

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor=BG)
    if LAYOUT == "wide":
        ax = fig.add_axes([0.050, 0.455, 0.680, 0.380])
        axp = fig.add_axes([0.775, 0.455, 0.170, 0.380])
        axh = fig.add_axes([0.050, 0.085, 0.895, 0.265])
    else:
        ax = fig.add_axes([0.105, 0.680, 0.610, 0.210])
        axp = fig.add_axes([0.760, 0.680, 0.200, 0.210])
        axh = fig.add_axes([0.105, 0.070, 0.855, 0.530])

    for A in (ax, axp, axh):
        A.set_facecolor(BG)
        for sp in A.spines.values():
            sp.set_color("#3a4150")
        A.tick_params(colors="#8d97a8", labelsize=LABEL_FS - 5)

    im = ax.imshow(np.zeros_like(GX), origin="lower", cmap=CMAP, vmin=0, vmax=1,
                   extent=[*XLIM, *ZLIM], interpolation="bilinear", zorder=1)
    ax.set_aspect("equal")
    ax.set_xlim(*XLIM); ax.set_ylim(*ZLIM)
    ax.set_xlabel("distance behind the autorickshaw  (m)", color="#c3cbd9",
                  fontsize=LABEL_FS)
    ax.set_ylabel("height  (m)", color="#c3cbd9", fontsize=LABEL_FS)

    for zg, lab in GUIDES:
        ax.axhline(zg, color="#5d6982", lw=0.9, ls=(0, (5, 4)), zorder=4)
        ax.text(XLIM[0] + 0.15, zg + 0.045, lab, color="#7f8ca3",
                fontsize=LABEL_FS - 5, zorder=4)

    person(ax, 0.0, "#ff4f3a", z=6)
    veh = ax.imshow(np.zeros((2, 2)), origin="lower", cmap="gray", zorder=5,
                    extent=[0, 1, 0, 1])

    # profile strip
    axp.set_ylim(*ZLIM)
    axp.set_xlim(0, 1.05)
    axp.set_xlabel("road air fraction", color="#c3cbd9", fontsize=LABEL_FS - 3)
    if LAYOUT == "wide":
        axp.set_title("at the person", color="#c3cbd9", fontsize=LABEL_FS - 2, pad=8)
    zp = np.linspace(0, ZLIM[1], 44)
    (pline,) = axp.plot([], [], color="#e8be6a", lw=2.6)
    pfill = [None]
    for zg, _ in GUIDES:
        axp.axhline(zg, color="#5d6982", lw=0.9, ls=(0, (5, 4)))
    axp.text(0.5, 1.63, "never reached", color="#ff6b57",
             fontsize=LABEL_FS - 5, ha="center", va="bottom")

    # history panel: the delayed peak, stated as data
    axh.set_xlim(0, taus.max())
    axh.set_ylim(0, 1.02)
    axh.set_xlabel("tau  -  seconds after the autorickshaw passes",
                   color="#c3cbd9", fontsize=LABEL_FS - 2)
    axh.set_ylabel("road air fraction", color="#c3cbd9", fontsize=LABEL_FS - 3)
    for h, c, lab in HIST:
        axh.plot(taus, hist[h], color=c, lw=2.2, label=lab)
        v = hist[h]
        if np.nanmax(v) > 0.05:                      # mark only real arrivals
            i = int(np.nanargmax(v))
            axh.plot([taus[i]], [v[i]], "o", color=c, ms=6, zorder=5)
            axh.annotate(f"peak {taus[i]:.2f} s", (taus[i], v[i]),
                         textcoords="offset points", xytext=(6, 7),
                         color=c, fontsize=LABEL_FS - 6)
    leg = axh.legend(loc="upper right", facecolor="#11151f", edgecolor="#3a4150",
                     fontsize=LABEL_FS - 5, labelcolor="#c3cbd9", ncol=4)
    leg.get_frame().set_alpha(0.9)
    cursor = axh.axvline(0.0, color="#ffffff", lw=1.4, alpha=0.85, zorder=6)

    tx, ty, sy = (0.050, 0.935, 0.897) if LAYOUT == "wide" else (0.105, 0.955, 0.930)
    title = fig.text(tx, ty, "", color="#ffffff", fontsize=TITLE_FS,
                     fontweight="bold", ha="left")
    sub = fig.text(tx, sy, "", color="#93a0b5", fontsize=LABEL_FS - 4,
                   ha="left")

    # aspect('equal') resizes the field axes at DRAW time, so the profile strip
    # must be aligned to the box matplotlib actually produced, not the one that
    # was requested. Declaring the same height for both leaves them mismatched.
    fig.canvas.draw()
    fp = ax.get_position()
    pp = axp.get_position()
    axp.set_position([pp.x0, fp.y0, pp.width, fp.height])

    path = os.path.join(OUT, f"cfd_f8_dust_{LAYOUT}_master.mp4")
    w, h = int(FIGSIZE[0] * DPI), int(FIGSIZE[1] * DPI)
    w -= w % 2; h -= h % 2
    wr = imageio_ffmpeg.write_frames(path, (w, h), fps=FPS, quality=8,
                                     macro_block_size=1)
    wr.send(None)

    for k, (tau, d) in enumerate(snaps):
        s = S[k]
        xp = U * tau                       # pedestrian's solve-frame position
        q = np.column_stack([(GX + xp).ravel(), GZ.ravel()])
        fld = rs(s, q, nan_outside=True).reshape(GX.shape)
        im.set_data(np.nan_to_num(fld, nan=0.0))

        # vehicle recedes behind the pedestrian
        vshift = -xp
        veh.set_extent([vx0 + vshift, vx1 + vshift, 0, vz.max()])
        veh.set_data(np.where(vocc, 1.0, np.nan))
        veh.set_cmap(matplotlib.colors.ListedColormap(["#39414f"]))

        col = np.abs(GX[0] - 0.0) <= 0.6
        prof = np.nanmean(np.where(np.isnan(fld), 0.0, fld)[:, col], axis=1)
        pz = GZ[:, 0]
        pline.set_data(prof, pz)
        if pfill[0] is not None:
            pfill[0].remove()
        pfill[0] = axp.fill_betweenx(pz, 0, prof, color="#b98436", alpha=0.35)

        cursor.set_xdata([tau, tau])

        # 62 characters do not fit across 1080 px at a readable size
        if LAYOUT == "wide":
            title.set_text(f"Where the road air goes   |   tau = {tau:5.2f} s "
                           f"after the autorickshaw passes")
            sub.set_text("bright = air that started in the road-level dust "
                         "layer   *   it climbs to waist height and stops   "
                         "*   passive scalar, AUTOW_D, 1.33 M cells")
        else:
            title.set_text(f"Where the road air goes   |   tau = {tau:4.2f} s")
            sub.set_text("bright = air off the road surface\n"
                         "it climbs to waist height and stops")

        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        wr.send(np.ascontiguousarray(buf[:h, :w]))
        if k % 50 == 0:
            print(f"  frame {k}/{len(snaps)}  tau={tau:.2f}", flush=True)

    wr.close()
    plt.close(fig)
    print("wrote", path, f"({len(snaps)} frames, {len(snaps)/FPS:.1f} s at {FPS} fps)")


if __name__ == "__main__":
    main()
