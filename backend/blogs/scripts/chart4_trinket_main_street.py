#!/usr/bin/env python3
"""
Chart 4: Main Street America — Annual Local Reinvestment
Bar chart showing reinvestment dollars from 2019–2024 with ROI annotation.

Source: Main Street America, Collective Impact Statistics (2025)
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ---------- styling ----------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 11,
    "axes.titlesize": 15,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

# ---------- data ----------
years = [2019, 2020, 2021, 2022, 2023, 2024]
reinvestment = [4.21, 3.85, 4.58, 5.12, 5.68, 7.65]

# Color: cool blue-green gradient emphasizing the 2024 surge
bar_colors = ["#88CCEE", "#88CCEE", "#88CCEE", "#88CCEE", "#88CCEE", "#009E73"]

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)

bars = ax.bar(years, reinvestment, width=0.5, color=bar_colors,
              edgecolor="#2C7FB8" if False else "#005A3C",
              linewidth=0.5, zorder=2)

# Value labels above each bar
for bar, val in zip(bars, reinvestment):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.12,
            f"${val:.2f}B", ha="center", fontsize=9, color="#333333",
            fontweight="bold")

# ----- ROI annotation text box -----
# Place it in the top-right area of the plot
ax.text(
    0.96, 0.95,
    "2024 ROI:\n$21.73 per $1\nspent on operations",
    transform=ax.transAxes,
    fontsize=9.5, color="#005A3C",
    ha="right", va="top",
    fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.5", fc="#E8F5E9", ec="#009E73", lw=1.0),
)

# ----- labels -----
ax.set_title("Main Street America — Annual Local Reinvestment", pad=12)
ax.set_xlabel("Year")
ax.set_ylabel("Reinvestment ($ billions)")
ax.set_xticks(years)
ax.set_ylim(0, 9.5)

# source line
fig.text(0.5, -0.02,
         "Source: Main Street America, 2025 Designated Communities & 2024 Collective Impact Statistics",
         ha="center", fontsize=8, color="#555555",
         transform=ax.transAxes)

plt.tight_layout()

# ---------- save ----------
out_dir = Path(__file__).resolve().parents[1] / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "trinket_main_street.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {out_path}")
print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
