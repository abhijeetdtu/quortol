#!/usr/bin/env python3
"""
Chart 3: National Park Gateway Spending by Category (horizontal bar chart)
Where National Park visitors spent $29 billion in 2024.

Source: National Park Service, 2024 Visitor Spending Effects Report
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

# ---------- data (sorted descending) ----------
categories = [
    "Lodging",
    "Restaurants & Bars",
    "Gas & Oil",
    "Recreation Industries",
    "Local Transportation",
    "Groceries & Convenience",
    "Retail (Souvenirs etc.)",
    "Other",
    "Camping Fees",
]
values = [11.1, 5.7, 2.8, 2.5, 2.0, 1.9, 1.2, 1.2, 0.6]

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)

y_pos = np.arange(len(categories))

# Build color list: highlight "Retail (Souvenirs etc.)" in orange
base_color = "#56B4E9"
highlight_color = "#E69F00"
colors = [highlight_color if cat == "Retail (Souvenirs etc.)" else base_color
          for cat in categories]

bars = ax.barh(y_pos, values, height=0.6, color=colors, edgecolor="white",
               linewidth=0.5, zorder=2)

# Value labels on each bar
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height() / 2,
            f"${val:.1f}B", va="center", fontsize=9, color="#333333",
            fontweight="bold")

# Highlight annotation for Retail
ax.annotate(
    "Souvenir & gift shops",
    xy=(1.2, categories.index("Retail (Souvenirs etc.)")),
    xytext=(3.5, categories.index("Retail (Souvenirs etc.)") + 0.5),
    fontsize=8.5, color="#CC6600", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#CC6600", lw=1.0, linestyle="dashed"),
    bbox=dict(boxstyle="round,pad=0.2", fc="#FFF8E1", ec="#CC6600", lw=0.6),
)

# ----- labels -----
ax.set_title("Where National Park Visitors Spent $29 Billion in 2024", pad=12)
ax.set_xlabel("Visitor Spending ($ billions)")
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=10)
ax.set_xlim(0, 13)

# Total annotation at bottom
ax.text(0.97, 0.03, "Total: $29.0 B", transform=ax.transAxes,
        fontsize=9, color="#555555", ha="right", va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", fc="#F5F5F5", ec="#CCCCCC", lw=0.5))

# source line
fig.text(0.5, -0.02,
         "Source: National Park Service, 2024 Visitor Spending Effects Report (NPS/SR—2025/237)",
         ha="center", fontsize=8, color="#555555",
         transform=ax.transAxes)

plt.tight_layout()

# ---------- save ----------
out_dir = Path(__file__).resolve().parents[1] / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "trinket_nps_spending.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {out_path}")
print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
