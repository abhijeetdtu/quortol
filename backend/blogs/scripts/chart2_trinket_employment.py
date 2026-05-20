#!/usr/bin/env python3
"""
Chart 2: Employment History — Gift, Novelty & Souvenir Stores
Bar chart with superimposed trend line showing employment from 2000 to 2026.

Source: U.S. Bureau of Labor Statistics, Current Employment Survey via CEIC
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
# Mix of integer years and fractional (Feb 2026 ≈ 2026.15)
labels = ["2000", "2005", "2010", "2015", "2020", "2021", "2022", "2023", "2024",
          "Feb\n2026"]
x_pos = [2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023, 2024, 2026 + 1/12]
employment = [294.9, 230, 185, 160, 115.9, 126.7, 147.5, 146.5, 145.2, 119.8]

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)

# Bars (use a muted blue)
bar_width = 0.6
bars = ax.bar(x_pos, employment, width=bar_width, color="#56B4E9",
              edgecolor="#2C7FB8", linewidth=0.5, zorder=2, alpha=0.85)

# Trend line connecting the bars
ax.plot(x_pos, employment, color="#0072B2", linewidth=2, marker="o",
        markersize=5, zorder=4, markerfacecolor="#0072B2", markeredgewidth=0)

# ----- annotations -----
# Peak annotation (Dec 2000)
ax.annotate(
    "Peak: 294,900\n(Dec 2000)",
    xy=(2000, 294.9), xytext=(2003, 310),
    fontsize=9, color="#D55E00", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#D55E00", lw=1.3),
    bbox=dict(boxstyle="round,pad=0.3", fc="#FFF5EB", ec="#D55E00", lw=0.8),
)

# Current annotation (Feb 2026)
ax.annotate(
    "Current: 119,800\n(Feb 2026)",
    xy=(2026 + 1/12, 119.8), xytext=(2023, 108),
    fontsize=9, color="#009E73", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#009E73", lw=1.3),
    bbox=dict(boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#009E73", lw=0.8),
)

# ----- labels -----
ax.set_title("Employment in Gift, Novelty & Souvenir Stores", pad=12)
ax.set_xlabel("Year")
ax.set_ylabel("Employment (thousands)")
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylim(0, 340)

# source line
fig.text(0.5, -0.02,
         "Source: U.S. Bureau of Labor Statistics, Current Employment Survey via CEIC",
         ha="center", fontsize=8, color="#555555",
         transform=ax.transAxes)

plt.tight_layout()

# ---------- save ----------
out_dir = Path(__file__).resolve().parents[1] / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "trinket_employment.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {out_path}")
print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
