"""
Chart: Recognition Gap — How Long It Took to Regulate Yesterday's "Safe" Materials
Horizontal bar chart showing years between industrial introduction and first major regulation.
Matplotlib, 1200×720 px, 150 DPI, Okabe-Ito colorblind-safe palette.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Okabe-Ito palette (colorblind-safe) ───────────────────────────────────────
OKABE_ITO = [
    "#D55E00",  # vermillion
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # green
    "#CC79A7",  # pink
    "#56B4E9",  # sky blue
]

# ── Data (sorted by Gap descending) ───────────────────────────────────────────
materials = [
    "Lead (paint)",
    "Asbestos",
    "Lead (gasoline)",
    "DDT",
    "Radium (dials)",
    "Thalidomide",
]

# Display labels with intro year for context
label_texts = [
    "Lead (paint)\n(1880s → 1971)",
    "Asbestos\n(1900 → 1973)",
    "Lead (gasoline)\n(1923 → 1973)",
    "DDT\n(1942 → 1972)",
    "Radium (dials)\n(1915 → 1925)",
    "Thalidomide\n(1957 → 1961)",
]

years_introduced = [1880, 1900, 1923, 1942, 1915, 1957]
years_regulated  = [1971, 1973, 1973, 1972, 1925, 1961]

# Gap in years (Lead paint is ~85, exact years give 91 but source says ~85)
gaps = [85, 73, 50, 30, 10, 4]

# Gap display strings (with tilde for Lead paint)
gap_labels = ["~85", "73", "50", "30", "10", "4"]

n = len(materials)

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 12,
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

# ── Horizontal bars ────────────────────────────────────────────────────────────
y_pos = np.arange(n)

bars = ax.barh(y_pos, gaps, height=0.6, color=OKABE_ITO, zorder=3, edgecolor="white", linewidth=0.5)

# ── Gap value labels at end of each bar ────────────────────────────────────────
for i, (bar, gap_str) in enumerate(zip(bars, gap_labels)):
    ax.text(
        bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
        gap_str,
        va="center", ha="left",
        fontsize=14, fontweight="bold", color="#222222",
    )

# ── Y-axis: material labels ───────────────────────────────────────────────────
ax.set_yticks(y_pos)
ax.set_yticklabels(label_texts, fontsize=11, ha="right")
ax.set_ylim(-0.6, n - 0.4)

# ── X-axis ─────────────────────────────────────────────────────────────────────
ax.set_xlabel("Years from Introduction to First Major Regulation",
              fontsize=12, labelpad=8)
ax.set_xlim(0, max(gaps) * 1.18)

# Round x-axis ticks to clean numbers
ax.set_xticks(np.arange(0, max(gaps) + 11, 10))
ax.xaxis.set_major_locator(plt.MultipleLocator(10))
ax.xaxis.set_minor_locator(plt.MultipleLocator(5))

# ── Grid: vertical lines only ──────────────────────────────────────────────────
ax.xaxis.grid(True, linestyle="-", alpha=0.2, color="#999999", zorder=0)
ax.set_axisbelow(True)

# ── Title & subtitle ───────────────────────────────────────────────────────────
ax.set_title(
    "How Long It Took to Regulate Yesterday's \"Safe\" Materials",
    fontsize=20, fontweight="bold", pad=8, color="#111111",
)

ax.text(
    0.0, 1.02,
    "Years between industrial-scale introduction and first major regulation or ban",
    transform=ax.transAxes, fontsize=12, color="#555555",
    ha="left", va="bottom",
)

# ── Source line ────────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.02,
    "Source: USGS, CDC, EPA, NEJM — dates of first major regulation",
    ha="center", va="bottom",
    fontsize=10, color="#777777",
    transform=fig.transFigure,
)

# ── Adjust layout ──────────────────────────────────────────────────────────────
fig.tight_layout(rect=[0, 0.04, 1, 1])

# ── Save PNG ───────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_png = output_dir / "once-safe-now-toxic_recognition_gap.png"
fig.savefig(output_png, dpi=150, bbox_inches=None,
            facecolor="white", edgecolor="none", pad_inches=0.1)
plt.close(fig)

print(f"Chart saved → {output_png.resolve()}")
print(f"  Dimensions:  1200 × 720 px @ 150 DPI")
print(f"  Format:      PNG")
print(f"  Bars:        {n}")
print(f"  Max gap:     {max(gaps)} years (Lead paint)")
print(f"  Min gap:     {min(gaps)} years (Thalidomide)")
