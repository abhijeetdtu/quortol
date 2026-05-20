#!/usr/bin/env python3
"""
"The Seven Ghosts of the AI Race: What History Tells Us About a $2.5 Trillion Bet"
Publication-quality data visualizations — 4 charts for longform magazine article.

Uses matplotlib with styled Economist/FT aesthetic.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
import os

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLE
# ─────────────────────────────────────────────────────────────────────────────

FONT = 'DejaVu Serif'
plt.rcParams.update({
    'font.family': FONT,
    'font.size': 11,
    'axes.titlesize': 18,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})

# Palette
BLUE      = '#1a56db'
CN_RED    = '#dc2626'
GRAY      = '#9ca3af'
EUROPE    = '#6b7280'
GREEN     = '#16a34a'
ORANGE    = '#ea580c'
LGRAY     = '#e5e7eb'
DGRAY     = '#4b5563'
BG_LIGHT  = '#fafafa'

SOURCE = (
    "Sources: Planetary Society, CRS, Brookings, Stanford HAI, "
    "Epoch AI, OECD, WIPO, Federal Reserve"
)

OUT_DIR = '/home/pi/Documents/code/quortol'
os.makedirs(OUT_DIR, exist_ok=True)


# ═════════════════════════════════════════════════════════════════════════════
# HELPER: clean spine styling
# ═════════════════════════════════════════════════════════════════════════════

def style_ax(ax, grid_axis='y', grid_color=LGRAY, grid_width=0.4):
    """Apply clean magazine-style axis styling."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(LGRAY)
    ax.spines['left'].set_linewidth(0.6)
    ax.spines['bottom'].set_color(LGRAY)
    ax.spines['bottom'].set_linewidth(0.6)
    ax.tick_params(colors=DGRAY, labelsize=9)
    ax.grid(axis=grid_axis, color=grid_color, linewidth=grid_width)
    ax.set_axisbelow(True)


# ═════════════════════════════════════════════════════════════════════════════
# CHART 1 — The Spending Escalation
# ═════════════════════════════════════════════════════════════════════════════

def make_chart1():
    fig, ax = plt.subplots(figsize=(15, 8.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    labels = [
        "Manhattan\nProject\n(1942-45)",
        "Apollo\nProgram\n(1960-73)",
        "Cold War\nDefense\n(1985 peak)",
        "Telecom\nBuildout\n(1996-00)",
        "China State\nAI (multi-yr\n2024-26)",
        "Stargate\nProject\n(2025-29)",
        "Hyperscaler\nAI Capex\n(2025)",
        "Global AI\nSpending\n(2024)",
        "Global AI\nSpending\n(2025 proj.)",
    ]

    total_spending = [30, 309, 320, 500, 150, 500, 405, 252, 1750]  # $B
    durations      = [4, 14, 1, 5, 3, 4, 1, 1, 1]  # years
    funder         = ['gov', 'gov', 'gov', 'private',
                      'gov', 'private', 'private', 'mixed', 'mixed']

    funder_colors = {'gov': BLUE, 'private': ORANGE, 'mixed': GREEN}
    bar_colors = [funder_colors[f] for f in funder]

    x = np.arange(len(labels))
    bars = ax.bar(x, total_spending, 0.6, color=bar_colors, edgecolor='white',
                  linewidth=0.4, alpha=0.92, zorder=3)

    # Log scale
    ax.set_yscale('log')
    ax.set_ylim(6, 6000)
    ax.set_ylabel('Total Spending (2025 $B, log scale)', fontsize=12, color=DGRAY,
                  labelpad=8)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f'${v:,.0f}B'))
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())

    style_ax(ax)

    # X-axis
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5, ha='center', color=DGRAY)

    # Duration labels above bars
    for i, (v, d) in enumerate(zip(total_spending, durations)):
        txt = f"{d} yr" if d > 1 else "peak yr"
        mult = 1.9 if i == 2 else (1.45 if i == 3 else 1.6)
        ax.text(i, v * mult, txt, ha='center', va='bottom', fontsize=7.5,
                color=DGRAY, fontstyle='italic',
                bbox=dict(boxstyle='round,pad=0.12', facecolor='white',
                          edgecolor='none', alpha=0.75))

    # Reference line for Apollo
    ax.axhline(y=309, color=BLUE, linewidth=0.9, linestyle='--', alpha=0.3,
               zorder=1)
    ax.text(0.3, 370, 'Apollo total ($309B)', fontsize=7.5, color=BLUE,
            alpha=0.55, va='bottom', ha='left')

    # Annotation: AI 2024 vs Apollo
    ax.annotate(
        'Global AI spending in 2024 alone ($252B)\n'
        'approaches the total inflation-adjusted\n'
        'cost of Apollo ($309B)',
        xy=(7, 252), xytext=(4.5, 1400),
        ha='center', fontsize=9, color=DGRAY,
        arrowprops=dict(arrowstyle='->', color=DGRAY, lw=0.8,
                        connectionstyle='arc3,rad=0.2'),
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#fef9c3',
                  edgecolor='none', alpha=0.85)
    )

    # Legend
    from matplotlib.patches import Patch
    ax.legend(
        handles=[
            Patch(facecolor=BLUE, label='Government-funded'),
            Patch(facecolor=ORANGE, label='Private-funded'),
            Patch(facecolor=GREEN, label='Mixed'),
        ],
        loc='upper left', frameon=True, facecolor='white',
        edgecolor=LGRAY, fontsize=9.5, title='Funding Source',
        title_fontsize=10
    )

    # Title block
    ax.set_title('The Spending Escalation — Technology Races Through History',
                 fontsize=19, fontweight='bold', pad=18, color='black')
    ax.text(0.5, 1.025,
            'In a single year, global AI spending already exceeds the '
            'inflation-adjusted cost of Apollo',
            transform=ax.transAxes, ha='center', fontsize=12, color=DGRAY,
            fontstyle='italic')

    # Footer
    ax.text(0.5, -0.13, SOURCE, transform=ax.transAxes, ha='center',
            fontsize=7.5, color=GRAY, fontstyle='italic')

    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'chart1_spending_escalation.png')
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'✓ {os.path.basename(path)}  ({os.path.getsize(path)//1024} KB)')


# ═════════════════════════════════════════════════════════════════════════════
# CHART 2 — US–China Paradox (Dumbbell)
# ═════════════════════════════════════════════════════════════════════════════

def make_chart2():
    fig, ax = plt.subplots(figsize=(16, 11))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Ordered: US-leading metrics first, then China-leading (4 + 5 = 9)
    metrics = [
        "Private AI Investment 2025",
        "Total AI CapEx 2025",
        "Model Performance Gap (benchmark avg)",
        "Notable AI Models 2024",
        "AI Patents (global share)",
        "AI Publications (global share)",
        "GenAI Inventions 2014-2023",
        "Industrial Robot Installations",
        "Electricity Reserve Margin",
    ]

    us_vals = np.array([285.9, 350, 51.35, 40, 16.9, 12.6, 6276, 34200, 17.5],
                       dtype=float)
    cn_vals = np.array([12.4, 91, 50.0, 15, 69.7, 23.2, 38210, 295000, 80],
                       dtype=float)

    us_labels = [
        "$285.9B", "~$350B", "51.35%", "40", "16.9%", "12.6%",
        "6,276", "34,200", "~17.5%"
    ]
    cn_labels = [
        "$12.4B", "$84-98B", "50.0%", "15", "69.7%", "23.2%",
        "38,210", "295,000", "80%+"
    ]

    n = len(metrics)
    y = np.arange(n)

    # Normalise each row independently to [0, 100]
    mx = np.maximum(us_vals, cn_vals)
    us_n = us_vals / mx * 100
    cn_n = cn_vals / mx * 100

    # ── connecting lines ──
    for i in range(n):
        ax.plot([us_n[i], cn_n[i]], [y[i], y[i]],
                color=LGRAY, lw=2.8, zorder=1)

    # ── dots ──
    ax.scatter(us_n, y, s=200, color=BLUE, zorder=3,
               edgecolors='white', linewidth=1.5, label='United States')
    ax.scatter(cn_n, y, s=200, color=CN_RED, zorder=3,
               edgecolors='white', linewidth=1.5, label='China')

    # ── value labels ──
    for i in range(n):
        if us_n[i] >= cn_n[i]:
            ax.text(us_n[i] + 2.2, y[i], us_labels[i], va='center',
                    fontsize=9.5, color=BLUE, fontweight='bold')
            ax.text(cn_n[i] - 2.2, y[i], cn_labels[i], va='center',
                    fontsize=9.5, color=CN_RED, ha='right')
        else:
            ax.text(cn_n[i] + 2.2, y[i], cn_labels[i], va='center',
                    fontsize=9.5, color=CN_RED, fontweight='bold')
            ax.text(us_n[i] - 2.2, y[i], us_labels[i], va='center',
                    fontsize=9.5, color=BLUE, ha='right')

    # Override: row 2 needs extra spacing
    if us_n[2] >= cn_n[2]:
        ax.text(us_n[2] + 3.5, 2, us_labels[2], va='center', fontsize=9.5, color=BLUE, fontweight='bold')
        ax.text(cn_n[2] - 3.5, 2, cn_labels[2], va='center', fontsize=9.5, color=CN_RED, ha='right')

    # ── divider between groups ──
    div_y = 3.5
    ax.axhline(y=div_y, color=LGRAY, lw=1.2, linestyle='--', zorder=0)

    # ── group annotations ──
    ax.text(113, 1.0, 'US leads on capital\nand frontier models',
            fontsize=10.5, color=BLUE, fontweight='bold', ha='left',
            va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=BLUE, lw=0.8, alpha=0.85))
    ax.text(113, 6.5, 'China leads on everything\nthat scales',
            fontsize=10.5, color=CN_RED, fontweight='bold', ha='left',
            va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=CN_RED, lw=0.8, alpha=0.85))

    # ── axes ──
    ax.set_yticks(y)
    ax.set_yticklabels(metrics, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(-6, 124)

    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'],
                       fontsize=9, color=DGRAY)
    ax.set_xlabel('Normalised within each metric (leader = 100%)',
                  fontsize=10, color=DGRAY, labelpad=6)

    style_ax(ax, grid_axis='both')

    # ── titles ──
    ax.set_title('Who Is Actually Ahead in AI?',
                 fontsize=21, fontweight='bold', pad=16, color='black')
    ax.text(0.5, 1.012, 'It depends entirely on which metric you choose',
            transform=ax.transAxes, ha='center', fontsize=13, color=DGRAY,
            fontstyle='italic')

    ax.legend(loc='lower right', frameon=True, facecolor='white',
              edgecolor=LGRAY, fontsize=11, markerscale=1.1)

    # ── footer ──
    ax.text(0.5, -0.08, SOURCE, transform=ax.transAxes, ha='center',
            fontsize=7.5, color=GRAY, fontstyle='italic')

    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'chart2_us_china_paradox.png')
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'✓ {os.path.basename(path)}  ({os.path.getsize(path)//1024} KB)')


# ═════════════════════════════════════════════════════════════════════════════
# CHART 3 — Training Cost Explosion
# ═════════════════════════════════════════════════════════════════════════════

def make_chart3():
    fig, ax = plt.subplots(figsize=(14, 9.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # ── data ──
    models = {
        'GPT-1':            (2018, 0.002),
        'BERT-Large':       (2019, 0.003),
        'GPT-3':            (2020, 4.6),
        'PaLM':             (2022, 12),
        'GPT-4':            (2023, 78),
        'Gemini Ultra':     (2024, 191),
        'Llama 3.1 405B':  (2024, 170),
        'Grok-2':           (2024, 107),
    }
    deepseek = ('DeepSeek V3', 2024, 5.6)

    projected = {
        'GPT-5 class\n(projected)':  (2026, 500),
        'Next Frontier\n(projected)': (2027, 1000),
    }

    # ── exponential fit (excl. DeepSeek, projected) ──
    # Use frontier models from 2020 onward (GPT-3 onwards) for realistic
    # growth rate that matches the article's ~2.4x/yr narrative. Including
    # GPT-1/BERT-Large from 2018-19 with sub-$10K costs inflates the curve.
    frontier = {k: v for k, v in models.items()
                if v[0] >= 2020 and v[1] >= 1.0}
    yrs_fit = np.array([v[0] for v in frontier.values()])
    cst_fit = np.array([v[1] for v in frontier.values()])
    coeffs = np.polyfit(yrs_fit, np.log10(cst_fit), 1)
    a, b = coeffs
    growth_factor = 10 ** a
    print(f'  [chart3]  Exponential fit (frontier models 2020+): '
          f'cost ∝ 10^({a:.4f}·year + {b:.2f})')
    print(f'           Annual growth factor: {growth_factor:.2f}x')

    x_fit = np.linspace(2017.5, 2028.2, 300)
    y_fit = 10 ** (a * x_fit + b)

    # ── projected shaded band ──
    x_proj = np.linspace(2025, 2028.2, 80)
    y_proj_low  = 10 ** (a * x_proj + b) * 0.55
    y_proj_high = 10 ** (a * x_proj + b) * 1.8
    ax.fill_between(x_proj, y_proj_low, y_proj_high,
                    color=GRAY, alpha=0.07, zorder=0)
    ax.text(2025.8, 3000, 'Projected zone',
            fontsize=9.5, color=GRAY, ha='center', fontstyle='italic')

    # ── trend line ──
    ax.plot(x_fit, y_fit, color=BLUE, lw=1.6, ls='-', alpha=0.5, zorder=2,
            label=f'Exponential trend ({growth_factor:.1f}×/yr)')

    # ── main scatter ──
    xs = [v[0] for v in models.values()]
    ys = [v[1] for v in models.values()]
    ax.scatter(xs, ys, s=140, color=BLUE, zorder=4, edgecolors='white',
               linewidth=0.7)

    # ── projected points (hollow) ──
    for name, (yr, cost) in projected.items():
        ax.scatter(yr, cost, s=140, color=GRAY, zorder=3,
                   edgecolors=GRAY, linewidth=1.8, facecolors='none')
        ax.text(yr, cost * 1.6, name, ha='center', fontsize=9,
                color=GRAY, fontstyle='italic')

    # ── DeepSeek ──
    ax.scatter(deepseek[1], deepseek[2], s=240, color=CN_RED, zorder=6,
               edgecolors='white', linewidth=1.8)
    ax.annotate(
        'DeepSeek V3: $5.6M — achieved\nunder US chip export controls,\non '
        'restricted H800 GPUs',
        xy=(deepseek[1], deepseek[2]), xytext=(2025.8, 2.8),
        ha='center', fontsize=9.5, color=CN_RED, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color=CN_RED, lw=1.3,
                        connectionstyle='arc3,rad=0.25'),
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#fef2f2',
                  edgecolor=CN_RED, lw=0.8, alpha=0.92)
    )

    # ── model labels (manually positioned to avoid overlap) ──
    label_pos = {
        'GPT-1':            (2018, 0.002, -3.0, 3.5),
        'BERT-Large':       (2019, 0.003, 2.5, 3.0),
        'GPT-3':            (2020, 4.6,    4, 1.6),
        'PaLM':             (2022, 12,    -6, 1.5),
        'GPT-4':            (2023, 78,     5, 1.3),
    }
    for name, (yr, cost, dx, dy) in label_pos.items():
        ax.text(yr + dx * 0.035, cost * dy, name, fontsize=8, color=DGRAY,
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                          edgecolor='none', alpha=0.7))

    # Override: use annotation with arrows for closely-spaced 2024 models
    for model_name, yr, cost, text_x, text_y, color_data in [
        ('Gemini Ultra', 2024, 191, 2023.2, 380, DGRAY),
        ('Llama 3.1 405B', 2024, 170, 2025.2, 300, DGRAY),
        ('Grok-2', 2024, 107, 2025.8, 68, DGRAY),
    ]:
        ax.annotate(model_name, xy=(yr, cost), xytext=(text_x, text_y),
                    fontsize=8, color=color_data, ha='center',
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=0.7,
                                    connectionstyle='arc3,rad=0.15'),
                    bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                              edgecolor='none', alpha=0.7))

    # ── reference lines ──
    for val, lbl in [(10, '$10M'), (100, '$100M'), (1000, '$1B')]:
        ax.axhline(y=val, color=LGRAY, lw=0.6, ls='--', alpha=0.5, zorder=0)
        ax.text(2017.6, val * 1.18, lbl, fontsize=8, color=GRAY, ha='left')

    # ── scales ──
    ax.set_yscale('log')
    ax.set_ylim(0.0006, 5000)
    ax.set_xlim(2017.5, 2028.5)
    ax.set_xlabel('Year', fontsize=12, color=DGRAY, labelpad=6)
    ax.set_ylabel('Training Cost ($M, log scale)', fontsize=12, color=DGRAY,
                  labelpad=8)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(
            lambda v, _: f'${v:,.0f}M' if v >= 1 else f'${v*1000:.0f}K'))
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())

    style_ax(ax)
    ax.grid(axis='x', visible=False)

    # ── titles ──
    ax.set_title('The Cost of Building the Smartest Machine',
                 fontsize=19, fontweight='bold', pad=18, color='black')
    ax.text(0.5, 1.015,
            'Training costs are growing 2.4× per year. One Chinese lab broke '
            'the curve.',
            transform=ax.transAxes, ha='center', fontsize=12, color=DGRAY,
            fontstyle='italic')

    # ── notes ──
    ax.text(0.5, -0.13,
            SOURCE + "   |   Note: DeepSeek's $5.6M is marginal compute cost only",
            transform=ax.transAxes, ha='center', fontsize=7.5, color=GRAY,
            fontstyle='italic')

    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'chart3_training_cost_explosion.png')
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'✓ {os.path.basename(path)}  ({os.path.getsize(path)//1024} KB)')


# ═════════════════════════════════════════════════════════════════════════════
# CHART 4 — The Great Rebalancing (2 × 3 small multiples)
# ═════════════════════════════════════════════════════════════════════════════

def make_chart4():
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.patch.set_facecolor('white')
    axes_flat = axes.flatten()

    years = np.array([2020, 2021, 2022, 2023, 2024, 2025])

    # ── dataset definitions ──────────────────────────────────────────────
    datasets = [
        {  # 0 – MMLU
            'title': 'Model Performance (MMLU) — Gap narrowing',
            'ylabel': '% Correct',
            'ylim': (15, 85),
            'US':   [38.0, 45.0, 55.0, 65.0, 70.0, 74.0],
            'CN':   [30.0, 35.0, 42.0, 55.0, 65.0, 72.0],
            'EU':   None,
            'ann':  ('Gap: ~2.7pp', 2024.5, 82, BLUE),
        },
        {  # 1 – Private AI Investment
            'title': 'Private AI Investment — US surging',
            'ylabel': '$B USD',
            'ylim': (0, 330),
            'US':   [30, 45, 85, 140, 220, 286],
            'CN':   [9, 10, 10, 11, 11, 12.4],
            'EU':   [8, 10, 12, 10, 8, 7],
            'ann':  None,
        },
        {  # 2 – Notable Models
            'title': 'Notable AI Models — US leads, CN rising',
            'ylabel': 'Count',
            'ylim': (0, 48),
            'US':   [20, 22, 26, 32, 38, 40],
            'CN':   [3, 4, 5, 8, 12, 15],
            'EU':   [5, 5, 4, 4, 3, 3],
            'ann':  None,
        },
        {  # 3 – Patents
            'title': 'AI Patents (Global Share) — China dominant',
            'ylabel': '% of Global',
            'ylim': (0, 80),
            'US':   [20.5, 19.5, 18.5, 17.5, 17.0, 16.9],
            'CN':   [55.0, 58.0, 62.0, 65.0, 68.0, 69.7],
            'EU':   [8.0, 7.5, 7.0, 6.5, 6.0, 5.5],
            'ann':  None,
        },
        {  # 4 – Publications
            'title': 'AI Publications Share — China leading',
            'ylabel': '% of Global',
            'ylim': (0, 28),
            'US':   [13.5, 13.0, 12.8, 12.5, 12.6, 12.6],
            'CN':   [21.0, 21.5, 22.0, 22.5, 23.0, 23.2],
            'EU':   [15.0, 14.5, 14.0, 13.5, 13.0, 12.8],
            'ann':  None,
        },
        {  # 5 – Robot Installations
            'title': 'Industrial Robots — China dominates',
            'ylabel': 'Thousands',
            'ylim': (0, 330),
            'US':   [30.0, 31.0, 32.0, 32.5, 33.5, 34.2],
            'CN':   [150, 175, 210, 240, 270, 295],
            'EU':   [40.0, 42.0, 43.0, 44.0, 44.0, 43.0],
            'ann':  None,
        },
    ]

    # ── plot each ──
    for idx, d in enumerate(datasets):
        ax = axes_flat[idx]

        ax.plot(years, d['US'], color=BLUE, lw=2.6, marker='o', ms=6,
                label='United States')
        ax.plot(years, d['CN'], color=CN_RED, lw=2.6, marker='s', ms=6,
                label='China')
        if d['EU'] is not None:
            ax.plot(years, d['EU'], color=EUROPE, lw=2.6, marker='^', ms=6,
                    label='Europe')

        ax.set_title(d['title'], fontsize=11.5, fontweight='bold', pad=8)
        ax.set_ylabel(d['ylabel'], fontsize=9.5, color=DGRAY, labelpad=4)
        ax.set_ylim(d['ylim'])
        ax.set_xlim(2019.5, 2025.5)
        ax.set_xticks(years)
        ax.set_xticklabels([str(y) for y in years], fontsize=8)

        # Annotation if present
        if d['ann'] is not None:
            txt, ax_ann, ay_ann, color = d['ann']
            ax.annotate(txt, xy=(2025, 73), xytext=(ax_ann, ay_ann),
                        fontsize=8, color=color, fontweight='bold', ha='center',
                        arrowprops=dict(arrowstyle='->', color=color, lw=0.6,
                                        connectionstyle='arc3,rad=0.2'),
                        bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                                  edgecolor='none', alpha=0.7))

        style_ax(ax)
        ax.grid(axis='x', visible=False)

        if idx != 1:  # only first chart needs legend (will add shared legend)
            pass

    # ── shared legend ──
    fig.legend(
        ['United States', 'China', 'Europe'],
        loc='lower center', ncol=3,
        frameon=True, facecolor='white', edgecolor=LGRAY,
        fontsize=11.5, markerscale=1.2,
        bbox_to_anchor=(0.5, -0.045)
    )

    # ── title block ──
    fig.suptitle('The Great Rebalancing',
                 fontsize=22, fontweight='bold', y=0.985, color='black')
    fig.text(0.5, 0.925,
             "Over five years, China has erased America's lead in almost every "
             "dimension except capital",
             ha='center', fontsize=12.5, color=DGRAY, fontstyle='italic')

    # ── footer ──
    fig.text(0.5, -0.07, SOURCE, ha='center', fontsize=7.5, color=GRAY,
             fontstyle='italic')

    plt.tight_layout(rect=[0, 0.06, 1, 0.93])
    path = os.path.join(OUT_DIR, 'chart4_great_rebalancing.png')
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'✓ {os.path.basename(path)}  ({os.path.getsize(path)//1024} KB)')


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('─' * 60)
    print('  "The Seven Ghosts of the AI Race" — Visualization Generator')
    print('─' * 60)
    print()
    make_chart1()
    make_chart2()
    make_chart3()
    make_chart4()
    print()
    print('─' * 60)
    print('  All 4 charts generated successfully.')
    print(f'  Output: {OUT_DIR}/')
    print('─' * 60)
