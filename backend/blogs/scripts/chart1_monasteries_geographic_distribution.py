#!/usr/bin/env python3
"""
Horizontal bar chart: Benedictine Monks by Country, 2024
Output: PNG at 1200x720, 150 DPI
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from pathlib import Path

# ── Data ─────────────────────────────────────────────────────────────────────
data = {
    "country": [
        "United States", "France", "Germany", "Italy", "Tanzania", "Vietnam",
        "Austria", "India", "Brazil", "United Kingdom", "South Korea", "Spain",
        "Switzerland", "Belgium",
    ],
    "monks": [1040, 526, 510, 492, 327, 309, 264, 245, 201, 198, 148, 134, 125, 97],
}
df = pd.DataFrame(data).sort_values("monks", ascending=True)

# ── Styling ──────────────────────────────────────────────────────────────────
BAR_COLOR = "#3B7DD8"
FONT_FAMILY = "sans-serif"

plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "font.size": 11,
    "axes.edgecolor": "#d0d0d0",
    "axes.linewidth": 0.6,
    "grid.color": "#e8e8e8",
    "grid.linewidth": 0.5,
    "ytick.major.pad": 6,
})

# ── Build chart ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

bars = ax.barh(
    df["country"],
    df["monks"],
    height=0.65,
    color=BAR_COLOR,
    zorder=3,
)

# Data labels at end of each bar
for bar_obj, val in zip(bars, df["monks"]):
    ax.text(
        bar_obj.get_width() + 12,
        bar_obj.get_y() + bar_obj.get_height() / 2,
        str(val),
        va="center",
        ha="left",
        fontsize=9.5,
        color="#333333",
    )

# Axes
ax.set_xlim(0, df["monks"].max() * 1.18)  # room for labels
ax.xaxis.set_major_locator(mticker.MultipleLocator(200))
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
ax.grid(axis="x", visible=True, zorder=0)
ax.grid(axis="y", visible=False)
ax.tick_params(axis="y", left=False, labelsize=10)
ax.tick_params(axis="x", bottom=False, labelsize=9)

# Remove spines except bottom
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#d0d0d0")

# ── Titles & source ──────────────────────────────────────────────────────────
fig.suptitle(
    "Benedictine Monks by Country, 2024",
    fontsize=18,
    fontweight="bold",
    x=0.125,
    ha="left",
    y=0.96,
)

fig.text(
    x=0.125,
    y=0.915,
    s="Total: 5,875 monks across 19 congregations worldwide",
    fontsize=11,
    color="#555555",
    ha="left",
)

fig.text(
    x=0.125,
    y=-0.04,
    s="Source: Benedictine Confederation Catalogus 2025",
    fontsize=8.5,
    color="#999999",
    ha="left",
)

fig.tight_layout(rect=[0, 0.04, 1, 0.90])

# ── Save ─────────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "monasteries_geographic_distribution.png"
fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"Chart saved to: {output_path}")
print(f"Dimensions: 1200x720 px, 150 DPI")
