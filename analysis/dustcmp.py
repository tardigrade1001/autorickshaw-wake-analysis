"""Side-by-side slow-motion video: autorickshaw vs WagonR lofting road dust.

    python dustcmp.py [wide|tall] [FPS]

AUTOW_D and WAGONR_D differ in the vehicle and nothing else. Dust supply,
domain, refinement, schemes and sampling were cloned, and the control confirms
it: upstream of the vehicle both carry the same incoming layer to 4 decimal
places. So every difference on screen is the vehicle.

WHAT THE VIDEO IS FOR
  The result is a split at waist height: 0.428 against 0.018, a factor of 23.
  Two panels sharing one colour scale make that visible without a caption. The
  waist trace panel underneath carries the number, and the eye line sits on both
  panels so the honest half of the finding stays on screen -- NEITHER vehicle
  reaches the face.

WHY BOTH PANELS ARE SAMPLED ON THE DIAGONAL
  The solve is vehicle-fixed. The pedestrian tracks x = -12 + U*t and passes at
  t = 12/U = 0.720 s. Here the pedestrian is pinned at x' = 0 and the vehicle
  recedes, which is a Galilean shift of the same data. A max over the plane
  finds a transient eddy 30 m away and reports it as the pedestrian's exposure;
  that error already produced one false "dust reaches 1.6 m" call on this
  dataset. Every number here is a +/-0.6 m column at x' = 0.

FRAME PAIRING
  The two runs wrote at different times (644 vs 730 snapshots, different adaptive
  timesteps). Frames are paired by NEAREST tau off a common grid, so a frame
  never shows two different wake ages side by side.
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
import paths

OUT = paths.out_dir()

CASES = [
    ("autorickshaw", paths.field_case("D"), paths.geometry(paths.CASE_STL["D"])),
    ("WagonR", paths.field_case("W"), paths.geometry(paths.CASE_STL["W"])),
]

U = 16.67
X0 = -12.0
T_PASS = -X0 / U          # 0.720 s
BG = "#080b12"

CMAP = LinearSegmentedColormap.from_list("dust", [
    (0.00, "#080b12"), (0.12, "#241a10"), (0.35, "#6b4a1e"),
    (0.60, "#b98436"), (0.82, "#e8be6a"), (1.00, "#fff0c4")])

LAYOUT = sys.argv[1] if len(sys.argv) > 1 else "wide"
FPS = int(sys.argv[2]) if len(sys.argv) > 2 else 30
# Third argument caps the snapshots loaded per case, evenly spread across the
# full tau range, so the whole pipeline can be smoke-tested in seconds:
#     python dustcmp.py wide 30 12
# Pairing is by nearest tau, so a capped run still shows matched wake ages.
# Annotated values on a capped run come from the subsample and differ
# from the published numbers. Use it to check the pipeline, not to read
# a result.
MAXFRAMES = int(sys.argv[3]) if len(sys.argv) > 3 else 0
if LAYOUT not in ("wide", "tall"):
    sys.exit("layout must be wide or tall")

if LAYOUT == "wide":
    XLIM, ZLIM = (-7.0, 2.5), (0.0, 2.6)
    FIGSIZE, DPI = (16.0, 9.0), 165
    TITLE_FS, LABEL_FS = 25, 16
else:
    XLIM, ZLIM = (-4.2, 1.8), (0.0, 2.6)
    FIGSIZE, DPI = (9.0, 16.0), 120
    TITLE_FS, LABEL_FS = 18, 14

GUIDES = [(0.60, "knee"), (1.00, "waist"), (1.60, "EYE LEVEL")]
COL = {"autorickshaw": "#e8be6a", "WagonR": "#6fb1d6"}
TRACE_H = 1.00            # the height the whole result turns on


def snapshots(root):
    out = []
    for d in glob.glob(os.path.join(root, "*")):
        if not os.path.isdir(d):
            continue
        tau = float(os.path.basename(d)) - T_PASS
        if tau < 0 or U * tau > 64.0:
            continue
        out.append((tau, d))
    out.sort()
    if MAXFRAMES and len(out) > MAXFRAMES:
        idx = np.linspace(0, len(out) - 1, MAXFRAMES).round().astype(int)
        out = [out[i] for i in idx]
    return out


def main():
    data = {}
    for name, root, stl in CASES:
        snaps = snapshots(root)
        if not snaps:
            sys.exit(f"no snapshots for {name} -- check {root}")
        a = np.loadtxt(os.path.join(snaps[0][1], "s_y1p2.raw"))
        pts = np.column_stack([a[:, 0], a[:, 2]])
        print(f"loading {name}: {len(snaps)} snapshots ...", flush=True)
        S = np.empty((len(snaps), len(a)))
        for i, (_, d) in enumerate(snaps):
            S[i] = np.nan_to_num(np.loadtxt(os.path.join(d, "s_y1p2.raw"))[:, 3],
                                 nan=0.0)
        data[name] = dict(taus=np.array([t for t, _ in snaps]), S=S, pts=pts,
                          rs=Resampler(pts), stl=stl_profile(stl))

    # Common tau grid: the two runs wrote at different adaptive timesteps, so
    # pairing by index would drift them apart. Pair by nearest tau instead.
    tmax = min(d["taus"].max() for d in data.values())
    n = int(min(len(d["taus"]) for d in data.values()))
    grid = np.linspace(0.0, tmax, n)
    for d in data.values():
        d["idx"] = np.abs(d["taus"][None, :] - grid[:, None]).argmin(axis=1)

    # Waist trace, sampled exactly as the panels are drawn.
    for name, d in data.items():
        px, pz = d["pts"][:, 0], d["pts"][:, 1]
        v = np.empty(len(grid))
        for i, k in enumerate(d["idx"]):
            m = (np.abs(px - U * d["taus"][k]) <= 0.6) & (np.abs(pz - TRACE_H) <= 0.15)
            v[i] = d["S"][k][m].mean() if m.any() else np.nan
        d["trace"] = v

    gx = np.linspace(*XLIM, int((XLIM[1] - XLIM[0]) / 0.035))
    gz = np.linspace(*ZLIM, int((ZLIM[1] - ZLIM[0]) / 0.035))
    GX, GZ = np.meshgrid(gx, gz)

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor=BG)
    if LAYOUT == "wide":
        boxes = [[0.055, 0.560, 0.630, 0.250], [0.055, 0.285, 0.630, 0.250]]
        axh = fig.add_axes([0.750, 0.285, 0.205, 0.525])
        axb = fig.add_axes([0.055, 0.070, 0.900, 0.150])
    else:
        boxes = [[0.075, 0.690, 0.640, 0.155], [0.075, 0.510, 0.640, 0.155]]
        axh = fig.add_axes([0.760, 0.510, 0.190, 0.335])
        axb = fig.add_axes([0.075, 0.075, 0.880, 0.340])

    axes, ims, vehs = {}, {}, {}
    for (name, _, _), box in zip(CASES, boxes):
        ax = fig.add_axes(box)
        ax.set_facecolor(BG)
        for sp in ax.spines.values():
            sp.set_color("#3a4150")
        ax.tick_params(colors="#8d97a8", labelsize=LABEL_FS - 6)
        im = ax.imshow(np.zeros_like(GX), origin="lower", cmap=CMAP, vmin=0, vmax=1,
                       extent=[*XLIM, *ZLIM], interpolation="bilinear", zorder=1)
        ax.set_aspect("equal")
        ax.set_xlim(*XLIM); ax.set_ylim(*ZLIM)
        ax.set_ylabel("height  (m)", color="#c3cbd9", fontsize=LABEL_FS - 3)
        for zg, lab in GUIDES:
            ax.axhline(zg, color="#5d6982", lw=0.9, ls=(0, (5, 4)), zorder=4)
            ax.text(XLIM[0] + 0.12, zg + 0.04, lab, color="#7f8ca3",
                    fontsize=LABEL_FS - 7, zorder=4)
        person(ax, 0.0, "#ff4f3a", z=6)
        vehs[name] = ax.imshow(np.zeros((2, 2)), origin="lower", cmap="gray",
                               zorder=5, extent=[0, 1, 0, 1])
        ax.text(0.988, 0.90, name, transform=ax.transAxes, ha="right",
                va="top", color=COL[name], fontsize=LABEL_FS + 1,
                fontweight="bold", zorder=7)
        axes[name], ims[name] = ax, im
    axes[CASES[1][0]].set_xlabel("distance behind the vehicle  (m)",
                                 color="#c3cbd9", fontsize=LABEL_FS - 2)
    axes[CASES[0][0]].set_xticklabels([])

    # vertical profile at the person, both cases on one pair of axes
    axh.set_facecolor(BG)
    for sp in axh.spines.values():
        sp.set_color("#3a4150")
    axh.tick_params(colors="#8d97a8", labelsize=LABEL_FS - 6)
    axh.set_ylim(*ZLIM); axh.set_xlim(0, 1.05)
    axh.set_xlabel("road air fraction", color="#c3cbd9", fontsize=LABEL_FS - 4)
    axh.set_title("at the person", color="#c3cbd9", fontsize=LABEL_FS - 3, pad=6)
    for zg, _ in GUIDES:
        axh.axhline(zg, color="#5d6982", lw=0.9, ls=(0, (5, 4)))
    plines, pfills = {}, {}
    for name, _, _ in CASES:
        (plines[name],) = axh.plot([], [], color=COL[name], lw=2.6, label=name)
        pfills[name] = None
    axh.legend(loc="upper right", facecolor="#11151f", edgecolor="#3a4150",
               fontsize=LABEL_FS - 6, labelcolor="#c3cbd9")
    axh.text(0.52, 1.63, "neither reaches", color="#ff6b57",
             fontsize=LABEL_FS - 7, ha="center", va="bottom")

    # waist trace: the headline number, as data
    axb.set_facecolor(BG)
    for sp in axb.spines.values():
        sp.set_color("#3a4150")
    axb.tick_params(colors="#8d97a8", labelsize=LABEL_FS - 6)
    axb.set_xlim(0, grid.max())
    axb.set_ylim(0, max(np.nanmax(d["trace"]) for d in data.values()) * 1.18)
    axb.set_xlabel("tau  -  seconds after the vehicle passes", color="#c3cbd9",
                   fontsize=LABEL_FS - 3)
    axb.set_ylabel(f"road air at {TRACE_H:.1f} m", color="#c3cbd9",
                   fontsize=LABEL_FS - 4)
    for name, _, _ in CASES:
        v = data[name]["trace"]
        axb.plot(grid, v, color=COL[name], lw=2.4, label=name)
        axb.fill_between(grid, 0, v, color=COL[name], alpha=0.16)
        i = int(np.nanargmax(v))
        axb.plot([grid[i]], [v[i]], "o", color=COL[name], ms=6, zorder=5)
        axb.annotate(f"{v[i]:.3f}", (grid[i], v[i]), textcoords="offset points",
                     xytext=(7, 4), color=COL[name], fontsize=LABEL_FS - 5,
                     fontweight="bold")
    pk = [np.nanmax(data[c[0]]["trace"]) for c in CASES]
    # inside the axes, not a title -- a title here collides with the x-label of
    # the field panel above once aspect('equal') has resized it
    axb.text(0.988, 0.92, f"waist height  -  {pk[0]/pk[1]:.0f}x more road air "
             f"behind the autorickshaw", transform=axb.transAxes, ha="right",
             va="top", color="#c3cbd9", fontsize=LABEL_FS - 1, fontweight="bold")
    cursor = axb.axvline(0.0, color="#ffffff", lw=1.4, alpha=0.85, zorder=6)

    tx, ty, sy = (0.055, 0.930, 0.892) if LAYOUT == "wide" else (0.075, 0.955, 0.925)
    title = fig.text(tx, ty, "", color="#ffffff", fontsize=TITLE_FS,
                     fontweight="bold", ha="left")
    sub = fig.text(tx, sy, "", color="#93a0b5", fontsize=LABEL_FS - 4, ha="left")

    # aspect('equal') resizes the field axes at DRAW time, so anything aligned
    # to them must be re-read from the box matplotlib actually produced.
    fig.canvas.draw()
    f0 = axes[CASES[0][0]].get_position()
    f1 = axes[CASES[1][0]].get_position()
    hp = axh.get_position()
    axh.set_position([hp.x0, f1.y0, hp.width, f0.y1 - f1.y0])
    # the trace panel must clear the drawn field box plus its x-label, so anchor
    # it to f1.y0 to the drawn height, which the requested height does not give
    bp = axb.get_position()
    btop = f1.y0 - (0.085 if LAYOUT == "wide" else 0.075)
    axb.set_position([bp.x0, bp.y0, bp.width, max(0.10, btop - bp.y0)])

    # A capped run writes beside the master so a smoke test never
    # replaces the finished animation.
    tag = "_smoke%d" % MAXFRAMES if MAXFRAMES else "_master"
    path = os.path.join(OUT, f"cfd_f10_dustcmp_{LAYOUT}{tag}.mp4")
    w, h = int(FIGSIZE[0] * DPI), int(FIGSIZE[1] * DPI)
    w -= w % 2; h -= h % 2
    wr = imageio_ffmpeg.write_frames(path, (w, h), fps=FPS, quality=8,
                                     macro_block_size=1)
    wr.send(None)

    for k, tau in enumerate(grid):
        xp = U * tau
        q = np.column_stack([(GX + xp).ravel(), GZ.ravel()])
        for name, _, _ in CASES:
            d = data[name]
            s = d["S"][d["idx"][k]]
            fld = d["rs"](s, q, nan_outside=True).reshape(GX.shape)
            fld = np.nan_to_num(fld, nan=0.0)
            ims[name].set_data(fld)

            vx, vz, vocc, vx0, vx1 = d["stl"]
            vehs[name].set_extent([vx0 - xp, vx1 - xp, 0, vz.max()])
            vehs[name].set_data(np.where(vocc, 1.0, np.nan))
            vehs[name].set_cmap(matplotlib.colors.ListedColormap(["#39414f"]))

            col = np.abs(GX[0] - 0.0) <= 0.6
            prof = np.nanmean(fld[:, col], axis=1)
            plines[name].set_data(prof, GZ[:, 0])
            if pfills[name] is not None:
                pfills[name].remove()
            pfills[name] = axh.fill_betweenx(GZ[:, 0], 0, prof,
                                             color=COL[name], alpha=0.22)

        cursor.set_xdata([tau, tau])
        if LAYOUT == "wide":
            title.set_text("Same road, same dust, two vehicles   |   "
                           f"tau = {tau:5.2f} s after passing")
            sub.set_text("bright = air that started in the road-level dust layer   "
                         "*   identical supply, domain and mesh settings   "
                         "*   only the vehicle differs")
        else:
            title.set_text(f"Two vehicles, one road   |   tau = {tau:4.2f} s")
            sub.set_text("bright = air off the road surface\n"
                         "only the vehicle differs")

        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        wr.send(np.ascontiguousarray(buf[:h, :w]))
        if k % 50 == 0:
            print(f"  frame {k}/{len(grid)}  tau={tau:.2f}", flush=True)

    wr.close()
    plt.close(fig)
    print("wrote", path, f"({len(grid)} frames, {len(grid)/FPS:.1f} s at {FPS} fps)")


if __name__ == "__main__":
    main()
