"""
Catskills Region Visitor Spending, 2019–2024
Vertical bar chart, magazine-quality styling

Data source: Empire State Development / Tourism Economics
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# ── Data ──────────────────────────────────────────────────────────────────────
years = [2019, 2020, 2021, 2022, 2023, 2024]
spending = [1600, 1200, 1937, 2296, 2454, 2628]  # $ millions

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 13,
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

bar_color = "#00897B"  # warm earthy teal, colorblind-safe

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

x = np.arange(len(years))
bar_width = 0.55

# Bars
bars = ax.bar(x, spending, width=bar_width, color=bar_color,
              edgecolor="none", zorder=3)

# Data labels on top of bars
for xi, val in zip(x, spending):
    ax.text(xi, val + 60, f"${val}M", ha="center", va="bottom",
            fontsize=12, fontweight="bold", color="#222222")

# Axes
ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in years], fontsize=13)
ax.set_xlabel("")

ax.set_ylabel("Visitor Spending ($ millions)", fontsize=13, labelpad=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}M"))

# Y-axis range: 0 with a bit of headroom
ax.set_ylim(0, max(spending) * 1.18)

# Grid: light horizontal lines only
ax.yaxis.grid(True, linestyle="-", alpha=0.25, color="#999999", zorder=0)
ax.set_axisbelow(True)

# Title
ax.set_title("Catskills Region Visitor Spending, 2019–2024",
             fontsize=18, fontweight="bold", pad=18, color="#111111")

# Source line
fig.text(0.5, -0.02,
         "Source: Empire State Development / Tourism Economics",
         ha="center", va="top",
         fontsize=10, color="#777777",
         transform=ax.transAxes)

# Tight layout to accommodate labels
fig.tight_layout(rect=[0, 0.04, 1, 1])

# ── Save ──────────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "catskills-next-act_visitor_spending.png"
fig.savefig(output_path, dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
plt.close(fig)

print(f"Chart saved → {output_path.resolve()}")
print(f"  Dimensions: 1200 × 720 px @ 150 DPI")
print(f"  Format:     PNG")
