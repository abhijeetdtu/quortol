#!/usr/bin/env python3
"""
chart3_new-england-homes_rent_gap.py

Grouped bar chart: Rent affordability gap in Massachusetts Gateway Cities.
Data from MassINC Gateway Cities Housing Monitor, Chapter 2: Housing
Affordability, September 2025.

Output: 1200×720 px PNG at 150 DPI.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")                # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import (
    AnchoredText, OffsetImage, AnnotationBbox,
)

# ── Matplotlib global settings ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.sans-serif":  ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size":        13,
    "axes.labelpad":    12,
    "axes.titlepad":    16,
    "xtick.major.pad":  6,
    "ytick.major.pad":  6,
})

# ── Data ──────────────────────────────────────────────────────────────────────
categories  = ["Median Renter\nIncome", "Income Required\nfor Average Rent"]
values      = [54000, 94000]
gap         = 40000

# Year-over-year for the inset annotation
yoy_2024 = 38000
yoy_2025 = 40000

# ── Colorblind-safe palette ───────────────────────────────────────────────────
COLOR_ACTUAL = "#0072B2"   # blue
COLOR_NEEDED = "#E69F00"   # orange
COLOR_GAP    = "#D55E00"   # vermillion (accent for the gap annotation)
COLOR_GRID   = "#d0d0d0"
COLOR_TEXT   = "#333333"
COLOR_SOURCE = "#888888"

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4.8))   # 1200×720 @ 150 DPI

# -- Bars ----------------------------------------------------------------------
bar_width   = 0.55
x_positions = [0, 1]
bars = ax.bar(
    x_positions, values, bar_width,
    color=[COLOR_ACTUAL, COLOR_NEEDED],
    edgecolor="white",
    linewidth=1.2,
    zorder=3,
)

# -- Data labels on top of bars ------------------------------------------------
for x, v in zip(x_positions, values):
    ax.text(
        x, v + 2000,
        f"${v:,}",
        ha="center", va="bottom",
        fontsize=14, fontweight="bold",
        color=COLOR_TEXT,
    )

# -- Gap annotation: bracket + label between the two bars -----------------------
# We draw a vertical bracket spanning from $54,000 to $94,000 at x = 0.5 (between
# the two bars) and label it with the gap amount.
bracket_x = 0.5   # centred between the two bars

# Vertical line with serifs (bracket)
gap_y_bottom = values[0]   # 54000
gap_y_top    = values[1]   # 94000

# Draw a thin vertical line for the bracket
ax.plot(
    [bracket_x, bracket_x],
    [gap_y_bottom, gap_y_top],
    color=COLOR_GAP,
    linewidth=1.8,
    solid_capstyle="butt",
    zorder=4,
)

# Serif ticks at top and bottom of bracket
serif_len = 0.12
for y_pos in (gap_y_bottom, gap_y_top):
    ax.plot(
        [bracket_x - serif_len, bracket_x + serif_len],
        [y_pos, y_pos],
        color=COLOR_GAP,
        linewidth=1.8,
        solid_capstyle="butt",
        zorder=4,
    )

# Arrowheads pointing inward on the bracket
# Downward arrow at the top
ax.annotate(
    "",
    xy=(bracket_x, gap_y_top - 1200),
    xytext=(bracket_x, gap_y_top),
    arrowprops=dict(
        arrowstyle="->", color=COLOR_GAP, lw=1.8,
        shrinkA=0, shrinkB=0,
    ),
    zorder=5,
)
# Upward arrow at the bottom
ax.annotate(
    "",
    xy=(bracket_x, gap_y_bottom + 1200),
    xytext=(bracket_x, gap_y_bottom),
    arrowprops=dict(
        arrowstyle="->", color=COLOR_GAP, lw=1.8,
        shrinkA=0, shrinkB=0,
    ),
    zorder=5,
)

# Gap label centred on the bracket
ax.text(
    bracket_x + 0.28, (gap_y_bottom + gap_y_top) / 2,
    f"Affordability\nGap: ${gap:,}",
    ha="center", va="center",
    fontsize=12, fontweight="bold",
    color=COLOR_GAP,
    linespacing=1.3,
)

# -- YoY inset annotation (lower-left area) ------------------------------------
# Text box showing the widening gap from 2024 to 2025
yoy_text = (
    f"Gap widened\n"
    f"2024: ${yoy_2024:,}\n"
    f"2025: ${yoy_2025:,}\n"
    f"↑ {yoy_2025 - yoy_2024:,} increase"
)
ax.text(
    0.02, 0.02, yoy_text,
    transform=ax.transAxes,
    ha="left", va="bottom",
    fontsize=9.5,
    color="#666666",
    linespacing=1.4,
    bbox=dict(
        boxstyle="round,pad=0.5",
        facecolor="#f8f8f8",
        edgecolor="#cccccc",
        linewidth=0.8,
    ),
    zorder=6,
)

# -- Axes formatting -----------------------------------------------------------
ax.set_xticks(x_positions)
ax.set_xticklabels(categories, fontsize=13, color=COLOR_TEXT)
ax.set_ylabel("Annual Income (2024 dollars)", fontsize=13, color=COLOR_TEXT)

# Y-axis: dollar formatting with commas
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda y, _: f"${y:,.0f}")
)
ax.set_ylim(0, 115000)

# -- Title, subtitle, source ----------------------------------------------------
fig.suptitle(
    "Rent Affordability Gap, Massachusetts Gateway Cities, 2025",
    fontsize=18, fontweight="bold", color=COLOR_TEXT,
    x=0.5, y=1.0, ha="center",
)
# Subtitle using fig.text instead of ax.set_title for better positioning control
fig.text(
    0.5, 0.92,
    "The typical renter earns $54,000 but needs $94,000 to afford average asking rent",
    ha="center", va="top",
    fontsize=11, color="#666666",
)
ax.set_xlabel("")   # no need for x-axis label — categories are self-explanatory

# Source line at bottom of figure
fig.text(
    0.5, 0.015,
    "Source: MassINC Gateway Cities Housing Monitor, Chapter 2: Housing Affordability, September 2025",
    ha="center", va="bottom",
    fontsize=9, color=COLOR_SOURCE,
)

# -- Magazine-quality theme ----------------------------------------------------
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#bbbbbb")
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_color("#bbbbbb")
ax.spines["bottom"].set_linewidth(0.6)

ax.tick_params(
    axis="both", which="both",
    length=0,                  # no tick marks
    colors=COLOR_TEXT,
)
ax.grid(axis="y", color=COLOR_GRID, linewidth=0.4, zorder=0)
ax.grid(axis="x", visible=False)
ax.set_axisbelow(True)

# -- Tight layout to avoid clipping --------------------------------------------
fig.tight_layout(rect=[0, 0.035, 1, 0.895])

# ── Output ─────────────────────────────────────────────────────────────────────
script_dir = Path(__file__).parent.resolve()
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_path = images_dir / "new-england-homes_rent_gap.png"
print(f"Saving chart → {output_path}")

fig.savefig(
    output_path,
    dpi=150,
    format="png",
    bbox_inches=None,
    facecolor="white",
    edgecolor="none",
    pad_inches=0,
)
print("Done.")
