#!/usr/bin/env python3
"""
Line chart: India's Foodgrain Production, 2019–2026
Uses matplotlib with Agg backend for headless rendering.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# ── Data ──────────────────────────────────────────────────────────────────────
crop_years = [
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
]

production = [297.5, 308.6, 315.7, 329.6, 332.2, 357.7, 376.6]  # Million Tonnes

# ── Figure setup ──────────────────────────────────────────────────────────────
# Figure size: 1200/150 × 720/150 inches → exactly 1200×720 px at 150 DPI
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)
fig.subplots_adjust(left=0.08, right=0.97, top=0.90, bottom=0.12)

# Use colorblind-safe deep blue
line_color = "#1f77b4"
x = np.arange(len(crop_years))

# ── Plot line ─────────────────────────────────────────────────────────────────
ax.plot(
    x, production,
    color=line_color,
    linewidth=2.5,
    marker="o",
    markersize=8,
    zorder=3,
)

# ── Data labels ──────────────────────────────────────────────────────────────
for i, val in enumerate(production):
    offset = 5
    if i == len(production) - 1:
        offset = 4  # slightly tighter for the annotated point
    ax.annotate(
        f"{val:.1f}",
        (x[i], production[i]),
        textcoords="offset points",
        xytext=(0, 12 + offset),
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="#333333",
    )

# ── Annotation at 2025-26 ────────────────────────────────────────────────────
last_x = x[-1]
last_y = production[-1]

ax.annotate(
    "Record 376.6 MT",
    xy=(last_x, last_y),
    xytext=(last_x + 0.45, last_y + 10),
    ha="center",
    fontsize=10,
    fontweight="bold",
    color=line_color,
    arrowprops=dict(
        arrowstyle="->",
        color=line_color,
        lw=1.5,
        connectionstyle="arc3,rad=0.2",
    ),
    bbox=dict(
        boxstyle="round,pad=0.3",
        facecolor="#eef6ff",
        edgecolor=line_color,
        linewidth=1,
    ),
)

# ── Axis styling ─────────────────────────────────────────────────────────────
ax.set_xticks(x)
ax.set_xticklabels(crop_years, fontsize=10)

ax.set_ylabel("Production (Million Tonnes)", fontsize=11)
ax.set_title(
    "India's Foodgrain Production, 2019–2026",
    fontsize=15,
    fontweight="bold",
    pad=12,
)

# Y-axis range with padding
y_min = min(production) - 15
y_max = max(production) + 25
ax.set_ylim(y_min, y_max)

# Light grid lines on y-axis only
ax.yaxis.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
ax.set_axisbelow(True)

# Remove top/right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.5)
ax.spines["bottom"].set_linewidth(0.5)

# ── Source line ───────────────────────────────────────────────────────────────
fig.text(
    0.5, -0.02,
    "Source: Government of India, Ministry of Agriculture",
    ha="center",
    fontsize=8,
    color="#666666",
    transform=ax.transAxes,
)

# ── Save ──────────────────────────────────────────────────────────────────────
output_path = "/home/pi/Documents/code/quortol/backend/blogs/images/chart1_indian-food-history-future_foodgrain_production.png"
fig.savefig(output_path, dpi=150, facecolor="white")
plt.close(fig)

print(f"Chart saved to {output_path}")
