#!/usr/bin/env python3
"""
Chart 1: Sectoral Output Trend — Gift & Souvenir Stores ($ billions)
Line chart showing sectoral output from 2020–2024 with annotations for
the pandemic drop and the 2024 recovery.

Source: U.S. Bureau of Labor Statistics via FRED (IPUHN453220T300000000)
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
years = [2020, 2021, 2022, 2023, 2024]
output = [14.014, 19.582, 21.152, 20.474, 21.550]

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)

ax.plot(years, output, color="#0072B2", linewidth=2.5, marker="o",
        markersize=7, zorder=3)

# fill below the line for visual emphasis
ax.fill_between(years, output, alpha=0.08, color="#0072B2")

# ----- annotations -----
# Pandemic drop
ax.annotate(
    "Pandemic drop\n$14.0 B",
    xy=(2020, 14.014), xytext=(2020.3, 13.0),
    fontsize=9, color="#D55E00", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#D55E00", lw=1.3),
    bbox=dict(boxstyle="round,pad=0.3", fc="#FFF5EB", ec="#D55E00", lw=0.8),
)

# 2024 recovery
ax.annotate(
    "2024 recovery\n$21.55 B",
    xy=(2024, 21.550), xytext=(2023.5, 22.6),
    fontsize=9, color="#009E73", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#009E73", lw=1.3),
    bbox=dict(boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#009E73", lw=0.8),
)

# ----- labels -----
ax.set_title("Gift & Souvenir Stores — Sectoral Output ($ billions)", pad=12)
ax.set_xlabel("Year")
ax.set_ylabel("Output ($ billions)")
ax.set_xticks(years)
ax.set_ylim(12, 24)

# source line
fig.text(0.5, -0.02,
         "Source: U.S. Bureau of Labor Statistics via FRED (series IPUHN453220T300000000)",
         ha="center", fontsize=8, color="#555555",
         transform=ax.transAxes)

plt.tight_layout()

# ---------- save ----------
out_dir = Path(__file__).resolve().parents[1] / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "trinket_sectoral_output.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {out_path}")
print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
