#!/usr/bin/env python3
"""
Grouped bar chart: Trappist Monasteries by Region, 1940 vs. Present (c. 2020)
Output: PNG at 1200x720, 150 DPI
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# ── Data ─────────────────────────────────────────────────────────────────────
regions = [
    "Europe",
    "North America",
    "Asia & Pacific",
    "Africa",
    "Central & South America",
]
monasteries_1940 = [75, 5, 6, 1, 0]
monasteries_2020 = [110, 16, 23, 17, 13]

# ── Styling ──────────────────────────────────────────────────────────────────
COLOR_1940 = "#3B7DD8"   # blue
COLOR_2020 = "#E8843B"   # orange
FONT_FAMILY = "sans-serif"

plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "font.size": 11,
    "axes.edgecolor": "#d0d0d0",
    "axes.linewidth": 0.6,
    "grid.color": "#e8e8e8",
    "grid.linewidth": 0.5,
})

# ── Build chart ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

x = np.arange(len(regions))          # label positions
width = 0.35                         # bar width

bars_1940 = ax.bar(
    x - width / 2,
    monasteries_1940,
    width,
    label="1940",
    color=COLOR_1940,
    zorder=3,
)

bars_2020 = ax.bar(
    x + width / 2,
    monasteries_2020,
    width,
    label="c. 2020",
    color=COLOR_2020,
    zorder=3,
)

# Data labels on top of bars
for bars_group, vals in [(bars_1940, monasteries_1940), (bars_2020, monasteries_2020)]:
    for bar_obj, val in zip(bars_group, vals):
        label_text = str(val) if val > 0 else ""
        ax.text(
            bar_obj.get_x() + bar_obj.get_width() / 2,
            bar_obj.get_height() + 1.2,
            label_text,
            va="bottom",
            ha="center",
            fontsize=9,
            color="#333333",
        )

# Axes
ax.set_xticks(x)
ax.set_xticklabels(regions, fontsize=10)
ax.set_ylabel("Number of Monasteries", fontsize=11)
ax.set_ylim(0, 135)
ax.yaxis.set_major_locator(plt.MultipleLocator(20))
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
ax.grid(axis="y", visible=True, zorder=0)
ax.grid(axis="x", visible=False)
ax.tick_params(axis="y", left=False, labelsize=9)
ax.tick_params(axis="x", bottom=False)

# Legend
legend = ax.legend(
    loc="upper left",
    frameon=False,
    fontsize=10,
    handlelength=1.2,
    handletextpad=0.6,
)

# Remove spines except bottom
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#d0d0d0")

# ── Titles & source ──────────────────────────────────────────────────────────
fig.suptitle(
    "Trappist Monasteries by Region: 1940 vs. Present",
    fontsize=18,
    fontweight="bold",
    x=0.125,
    ha="left",
    y=0.96,
)

fig.text(
    x=0.125,
    y=0.915,
    s="The number of monasteries more than doubled, with all growth outside Europe",
    fontsize=11,
    color="#555555",
    ha="left",
)

fig.text(
    x=0.125,
    y=-0.04,
    s="Source: Trappist Order statistics",
    fontsize=8.5,
    color="#999999",
    ha="left",
)

fig.tight_layout(rect=[0, 0.04, 1, 0.90])

# ── Save ─────────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "monasteries_trappist_growth.png"
fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"Chart saved to: {output_path}")
print(f"Dimensions: 1200x720 px, 150 DPI")
