"""
Single source of truth for every figure in this study.

Design intent: generator scripts contain ZERO literal colours / sizes / fonts.
Everything visual lives here, so re-theming = edit this file and re-run the
generators. Colours are SEMANTIC (keyed by what they mean), so one colour keeps
one meaning across all twelve figures.

    import thesis_style as ts
    ts.apply()                      # global rcParams
    ...plot using ts.VEHICLE['auto'], ts.finish(ax), ts.save(fig, name)...

Follows the shared visual grammar of the author's thesis figure system.
"""
import os
import matplotlib as mpl

# -- neutral palette (generic multi-series) ---------------------------------
RED     = '#E8352B'   # primary / emphasis
BLUE    = '#2E6FB0'   # secondary series
GREY    = '#5A5A5A'   # baseline / control
INK     = '#1A1A1A'   # near-black (reference)
GREEN   = '#2E7D32'
PURPLE  = '#8E44AD'
ORANGE  = '#C97A2B'
MAGENTA = '#C0328A'
TEAL    = '#2A9D8F'
PALETTE = [RED, BLUE, GREEN, PURPLE, ORANGE, GREY]

# -- SEMANTIC vehicle identity (consistent throughout the study) -------------
# One colour per vehicle, reused in every figure it appears in.
VEHICLE = {
    'auto':   RED,      # autorickshaw, the primary subject
    'wagonr': BLUE,     # tall hatchback, secondary comparison
    'dzire':  GREY,     # low sedan, second comparator
    'bus':    INK,      # city bus, reference upper bound on road-vehicle drag
}

LABEL = {
    'auto':   'Autorickshaw',
    'wagonr': 'Maruti WagonR',
    'dzire':  'Maruti Dzire',
    'bus':    'City bus',
}
SHORT = {'auto': 'Auto', 'wagonr': 'WagonR', 'dzire': 'Dzire', 'bus': 'Bus'}

# -- SEMANTIC run roles ------------------------------------------------------
CONTROL    = PURPLE     # validation, mesh refinement, perturbed-IC repeat
RAISED     = ORANGE     # the source-height experiment
SUPERSEDED = '#B0B0B0'  # withdrawn results, retained where they explain the method
GHOST      = '#8A8A8A'  # guide lines, reading heights
PALE       = '#D9D9D9'  # published ranges, shaded windows

# flat lookup used by the generators
C = dict(VEHICLE, robust=CONTROL, raised=RAISED, ref=INK,
         pale=PALE, ghost=GHOST, superseded=SUPERSEDED)

# heights used as reading marks, in metres
GUIDES = [(0.20, 'ankle'), (0.50, 'knee'), (1.00, 'waist'), (1.60, 'eye')]
EYE = 1.66            # the eye level used throughout, in metres

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.abspath(os.path.join(HERE, '..', 'docs', 'figures'))
os.makedirs(FIG_DIR, exist_ok=True)


def apply():
    """Global rcParams -- the house look (fonts, ticks, frame, weights)."""
    mpl.rcParams.update({
        'figure.figsize':    (5.2, 4.0),
        'figure.dpi':        150,
        'savefig.dpi':       300,
        'savefig.bbox':      'tight',
        'figure.facecolor':  'white',
        'axes.facecolor':    'white',
        'savefig.facecolor': 'white',
        'font.family':       'DejaVu Sans',
        'font.size':         11,
        'axes.labelsize':    12.5,
        'axes.titlesize':    12,
        'axes.linewidth':    1.1,
        'axes.axisbelow':    True,
        'axes.grid':         False,
        'xtick.direction':   'in',
        'ytick.direction':   'in',
        'xtick.top':         True,
        'ytick.right':       True,
        'xtick.major.size':  5,
        'ytick.major.size':  3,
        'xtick.minor.size':  3,
        'ytick.minor.size':  3,
        'legend.frameon':    False,
        'legend.fontsize':   10,
        'lines.linewidth':   1.7,
        'lines.markersize':  6,
        'errorbar.capsize':  3,
    })
    mpl.rcParams['ytick.major.size'] = 5


def frame(ax, lw=1.1):
    """Crisp black frame and inward ticks on all four sides."""
    for s in ax.spines.values():
        s.set_edgecolor(INK)
        s.set_linewidth(lw)
    ax.tick_params(colors=INK, which='both', top=True, right=True,
                   direction='in')


def finish(ax, xlabel=None, ylabel=None, title=None, legend=True):
    """Apply the shared per-axes finishing touches."""
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title)
    ax.tick_params(which='both', top=True, right=True)
    if legend and ax.get_legend_handles_labels()[0]:
        ax.legend()


def panel_tag(ax, tag, x=-0.14, y=1.03):
    """Bold (a)/(b)/... panel label in axes coords."""
    t = tag if tag.startswith('(') else f'({tag})'
    ax.text(x, y, t, transform=ax.transAxes, fontsize=13, fontweight='bold',
            va='bottom', ha='left')


def panel(ax, letter, dx=-0.14, dy=1.03):
    """Alias kept so every generator calls one implementation."""
    panel_tag(ax, letter, x=dx, y=dy)


def guides(ax, heights=GUIDES, axis='y', color=GHOST):
    """Mark the standard reading heights with reference lines."""
    for z, _name in heights:
        if axis == 'y':
            ax.axhline(z, color=color, lw=0.8, ls=':', zorder=0)
        else:
            ax.axvline(z, color=color, lw=0.8, ls=':', zorder=0)
    return ax


def marks(**kw):
    """Marker keywords giving coloured points a near-black outline."""
    d = dict(marker='o', markeredgecolor=INK, markeredgewidth=0.8)
    d.update(kw)
    return d


def save(fig, name):
    """Save into docs/figures/ as PNG at house DPI; return the path."""
    import matplotlib.pyplot as plt
    path = name if os.path.isabs(name) else os.path.join(
        FIG_DIR, name if name.endswith('.png') else name + '.png')
    fig.savefig(path)
    plt.close(fig)
    print('saved:', os.path.basename(path))
    return path
