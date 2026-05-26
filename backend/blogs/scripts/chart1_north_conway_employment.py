#!/usr/bin/env python3
"""
Chart 1: Employment by Industry — North Conway, NH (ZIP 03860)
Horizontal bar chart using ACS 2024 5-year estimates from USZip.com.

Data: US Census Bureau ACS 2024 5-year estimates via USZip.com
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# ---------- styling ----------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 11,
    "axes.titlesize": 16,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

# ---------- data (sorted descending) ----------
industries = [
    "Retail Trade",
    "Arts, Entertainment, Recreation,\nAccommodation, Food",
    "Educational Services,\nHealth Care, Social Assistance",
    "Construction",
    "Professional, Scientific,\nManagement, Admin Services",
    "Finance, Insurance, Real Estate",
    "Public Administration",
    "Manufacturing",
]
employed = [568, 387, 291, 205, 156, 134, 108, 43]

# Colorblind-safe warm muted palette (per spec)
bar_colors = [
    "#2C3E50",  # dark blue-gray
    "#E67E22",  # warm orange
    "#3498DB",  # blue
    "#27AE60",  # green
    "#8E44AD",  # purple
    "#D35400",  # burnt orange
    "#7F8C8D",  # gray
    "#1ABC9C",  # teal
]

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)  # 1200x720 at 150 DPI

y_pos = np.arange(len(industries))

# Horizontal bars
bars = ax.barh(y_pos, employed, color=bar_colors, height=0.6, edgecolor="white",
               linewidth=0.5, zorder=3)

# Data labels at end of each bar
for i, (bar, val) in enumerate(zip(bars, employed)):
    ax.text(
        val + 8, bar.get_y() + bar.get_height() / 2,
        f"{val:,}",
        va="center", ha="left", fontsize=10, fontweight="bold",
        color=bar_colors[i],
    )

# Y-axis labels
ax.set_yticks(y_pos)
ax.set_yticklabels(industries)

# X-axis
ax.set_xlabel("Workers Employed")
ax.xaxis.set_major_locator(mticker.MultipleLocator(100))
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
ax.set_xlim(0, max(employed) * 1.22)  # room for labels

# Remove y-axis grid lines (keep horizontal clean)
ax.grid(axis="y", visible=False)

# ---------- titles ----------
ax.set_title("Employment by Industry — North Conway, NH", pad=10, fontweight="bold")
ax.text(
    0.5, 1.01,
    "Workers aged 16+ by industry sector  |  Source: ACS 2024 5-year estimates, ZIP 03860",
    transform=ax.transAxes, ha="center", fontsize=9, color="#555555",
)

# ---------- source line ----------
fig.text(0.5, -0.02,
         "Data: US Census Bureau ACS 2024 5-year estimates via USZip.com",
         ha="center", fontsize=8, color="#777777",
         transform=ax.transAxes)

plt.tight_layout()

# ---------- save ----------
out_dir = Path(__file__).resolve().parents[1] / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "north_conway_employment.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {out_path}")
print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
