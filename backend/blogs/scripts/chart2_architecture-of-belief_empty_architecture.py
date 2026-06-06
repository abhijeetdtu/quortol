#!/usr/bin/env python3
"""
Chart: "The Empty Architecture"
Rajopadhye & Ghatpande 2022 — Vedic astrology empirical test.

Grouped bar chart: compliance rates for 6 principles across 9 planets.
One facet per principle, side-by-side bars for Group A vs Group B.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
short_planets = ["Sun", "Moon", "Mars", "Mer", "Jup", "Ven", "Sat", "Rah", "Ket"]

principles = [
    "P1: Planet in 6th/8th/12th house",
    "P2: Planet aspect/conjunct malefics",
    "P3: Debilitated or enemy sign",
    "P4: Debilitated + malefic aspect",
    "P5: Conjunct lord 6th/8th/12th",
    "P6: Malefic nakshatra",
]

principles_short = ["P1", "P2", "P3", "P4", "P5", "P6"]

group_a_data = [
    [12, 18, 14, 16, 11, 13, 15, 10,  9],   # P1
    [22, 28, 35, 20, 18, 15, 40, 25, 20],   # P2
    [ 8, 12, 10,  8,  6,  7, 14,  5,  4],   # P3
    [ 3,  4,  5,  3,  2,  2,  6,  2,  1],   # P4
    [15, 20, 18, 15, 12, 14, 22, 16, 13],   # P5
    [ 7, 11,  9,  7,  5,  6, 12,  8,  7],   # P6
]

group_b_data = [
    [13, 17, 15, 17, 10, 12, 14, 11, 10],   # P1
    [21, 29, 34, 19, 19, 16, 39, 26, 19],   # P2
    [ 9, 11, 11,  9,  7,  6, 13,  6,  5],   # P3
    [ 4,  3,  6,  4,  3,  1,  5,  3,  2],   # P4
    [16, 19, 19, 16, 13, 13, 21, 17, 14],   # P5
    [ 8, 10, 10,  8,  6,  5, 11,  9,  8],   # P6
]

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
n_planets = len(planets)
n_principles = len(principles)
bar_width = 0.35
x = np.arange(n_planets)

fig, axes = plt.subplots(
    nrows=2, ncols=3,
    figsize=(16, 10),
    sharex=True,
    sharey=False,
)

# Flatten for easy iteration
axes_flat = axes.flatten()

# Colorblind-safe palette (IBM Carbon / Tableau 10 accessible)
color_a = "#4C78A8"   # muted blue (Group A)
color_b = "#F58518"   # orange (Group B)

# Titles for each subplot
descriptions = [
    "Planet in 6th/8th/12th house",
    "Conjunct/square/opp.\nSaturn, Mars, Rahu, Ketu, Uranus",
    "Debilitated or enemy sign",
    "Debilitated/enemy sign\n+ malefic aspect",
    "Conjunct lord of\n6th/8th/12th house",
    "Malefic nakshatra\n(Krittika, Ashlesha, Mula)",
]

for i, ax in enumerate(axes_flat):
    # Bars
    bars_a = ax.bar(
        x - bar_width / 2,
        group_a_data[i],
        bar_width,
        label="Group A (intelligent)",
        color=color_a,
        edgecolor="white",
        linewidth=0.4,
        alpha=0.9,
    )
    bars_b = ax.bar(
        x + bar_width / 2,
        group_b_data[i],
        bar_width,
        label="Group B (intellectually disabled)",
        color=color_b,
        edgecolor="white",
        linewidth=0.4,
        alpha=0.9,
    )

    # Value labels on bars (only where > 0)
    for bar in bars_a:
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.6,
                f"{int(h)}",
                ha="center",
                va="bottom",
                fontsize=6,
                color="#333333",
                fontweight="normal",
            )
    for bar in bars_b:
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.6,
                f"{int(h)}",
                ha="center",
                va="bottom",
                fontsize=6,
                color="#333333",
                fontweight="normal",
            )

    # Subplot title
    ax.set_title(
        f"{principles_short[i]}: {descriptions[i]}",
        fontsize=11,
        fontweight="bold",
        pad=8,
    )

    # Horizontal reference line at y=0
    ax.axhline(y=0, color="black", linewidth=0.5, linestyle="--", alpha=0.6)

    # Y-axis
    ax.set_ylabel("Compliance rate (%)", fontsize=9)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True, prune="both"))
    ax.tick_params(axis="y", labelsize=8)

    # X-axis
    if i >= 3:  # bottom row
        ax.set_xticks(x)
        ax.set_xticklabels(short_planets, fontsize=8.5, rotation=0)
    else:
        ax.tick_params(axis="x", labelbottom=False)

    # Grid lines (horizontal only, light)
    ax.grid(axis="y", alpha=0.3, linestyle="--", linewidth=0.4)
    ax.set_axisbelow(True)

    # Remove top/right spines for cleaner look
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend — only on first subplot
    if i == 0:
        ax.legend(
            loc="upper left",
            fontsize=8,
            frameon=True,
            facecolor="white",
            edgecolor="#cccccc",
            framealpha=0.9,
        )

# Overall figure title and subtitle
fig.suptitle(
    "The Empty Architecture: No Astrological Principle Differentiates the Two Groups",
    fontsize=15,
    fontweight="bold",
    y=1.02,
    va="bottom",
)

# Subtitle via a text annotation
fig.text(
    0.5,
    0.975,
    "Compliance rates for 6 fundamental principles across 9 planets — "
    "Group A (intelligent) vs. Group B (intellectually disabled)",
    ha="center",
    va="top",
    fontsize=10,
    fontstyle="italic",
    color="#444444",
)

# Source line
fig.text(
    0.5,
    -0.005,
    "Data from Rajopadhye & Ghatpande 2022, Skeptical Inquirer",
    ha="center",
    va="top",
    fontsize=8,
    color="#666666",
    fontstyle="italic",
)

# Adjust layout
plt.subplots_adjust(
    left=0.06,
    right=0.98,
    top=0.92,
    bottom=0.07,
    hspace=0.28,
    wspace=0.22,
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_dir = "/home/pi/Documents/code/quortol/backend/blogs/images"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "architecture-of-belief_empty_architecture.png")

fig.savefig(
    output_path,
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
    edgecolor="none",
)

plt.close(fig)
print(f"Chart saved to: {output_path}")
