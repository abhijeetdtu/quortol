#!/usr/bin/env python3
"""
Chart: Visitor Spending vs. Population — Berkshire County, 2019–2024

Dual-axis combo chart:
  - Bars (left axis): Visitor spending in $ millions
  - Line + points (right axis): Population

Colorblind-safe palette, publication-quality styling.
Manual layout (no constrained_layout) to avoid twinx() clipping.

Sources:
  Dean Runyan Associates / Mass.gov MOTT (visitor spending)
  U.S. Census Bureau (population estimates V2024)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

# =====================================================================
# 1. DATA
# =====================================================================

df = pd.DataFrame({
    "Year":       [2019, 2020, 2021, 2022, 2023, 2024],
    "Spending":   [674.3, 490.8, 768.2, 862.4, 829.2, 839.3],
    "Population": [129028, 129089, 129089, 128763, 128047, 128726],
})

# Compute year-over-year change for the annotation
yoy_2020 = (df.loc[df["Year"] == 2020, "Spending"].values[0]
            / df.loc[df["Year"] == 2019, "Spending"].values[0] - 1) * 100

# =====================================================================
# 2. COLOR PALETTE (colorblind-safe)
# =====================================================================

SPEND_COLOR = "#4C72B0"   # warm blue     — bars
POP_COLOR   = "#C44E52"   # dark red      — line & points
GRID_COLOR  = "#E8E8E8"
TEXT_COLOR  = "#333333"
CAPTION_CLR = "#888888"
BG_COLOR    = "#FFFFFF"
PANEL_COLOR = "#FCFCFC"

# =====================================================================
# 3. BUILD CHART
# =====================================================================

# 1200 × 720 px @ 150 DPI
w_inches = 8.0
h_inches = 4.8
dpi = 150

fig, ax1 = plt.subplots(figsize=(w_inches, h_inches), dpi=dpi)
fig.patch.set_facecolor(BG_COLOR)

# FIX 1: Manual layout instead of constrained_layout (which clips with twinx)
fig.subplots_adjust(top=0.85, bottom=0.18, left=0.12, right=0.88)

# ----- Bars: Visitor Spending (left axis) -----

bars = ax1.bar(
    df["Year"],
    df["Spending"],
    width=0.55,
    color=SPEND_COLOR,
    alpha=0.88,
    zorder=3,
    edgecolor="none",
)

ax1.set_xlim(2018.4, 2025.0)
ax1.set_ylim(400, 1000)
ax1.set_ylabel("Visitor Spending ($ millions)", color=TEXT_COLOR, fontsize=12)
ax1.set_xlabel("")

# Format y-axis ticks
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}"))

# ----- Population Line (right axis) -----

ax2 = ax1.twinx()
ax2.set_ylim(127500, 129500)
ax2.set_ylabel("Population", color=TEXT_COLOR, fontsize=12)

line = ax2.plot(
    df["Year"],
    df["Population"],
    color=POP_COLOR,
    linewidth=1.8,
    zorder=5,
    marker="o",
    markersize=7,
    markeredgecolor="white",
    markeredgewidth=0.8,
)

# Format population y-axis with commas
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))

# ----- X-axis -----

ax1.set_xticks(df["Year"])
ax1.set_xticklabels([str(y) for y in df["Year"]], fontsize=10, color=TEXT_COLOR)

# ----- Population label at end of line (FIX 2: annotate with leader line) -----

last_row = df[df["Year"] == 2024].iloc[0]
ax2.annotate(
    "Population",
    xy=(2024, last_row["Population"]),
    xytext=(2024.55, last_row["Population"]),
    color=POP_COLOR,
    fontsize=10.5,
    fontweight="bold",
    va="center",
    ha="left",
    arrowprops=dict(
        arrowstyle="-",
        color=POP_COLOR,
        lw=0.8,
    ),
    zorder=10,
)

# ----- Annotation: pandemic dip (FIX 3: repositioned to avoid bar overlap) -----

ax1.annotate(
    "COVID-19 crash\n\u2212{:.0f}% from 2019".format(abs(yoy_2020)),
    xy=(2020, 490.8),            # arrow tip at top of the 2020 bar
    xytext=(2020.60, 590),       # text shifted right & up, clear of adjacent bars
    ha="center",
    va="bottom",
    fontsize=9.5,
    color="#666666",
    arrowprops=dict(
        arrowstyle="->",
        color="#666666",
        lw=0.8,
        connectionstyle="arc3,rad=0.08",  # slight curve for visual polish
    ),
    zorder=10,
)

# =====================================================================
# 4. THEME / STYLING
# =====================================================================

# FIX 4: Title via set_title (above axes, within subplots_adjust top margin)
ax1.set_title(
    "Visitor Spending vs. Population \u2014 Berkshire County, 2019\u20132024",
    fontsize=16,
    fontweight="bold",
    color="#222222",
    ha="center",
    pad=18,
)

# Subtitle — positioned lower in axes coords (y=0.98, va="top") so it sits
# just below the title and is not clipped by the figure edge.
ax1.text(
    0.5, 0.98,
    "\\$839 million in tourism, yet the county keeps shrinking",
    fontsize=11,
    color="#555555",
    ha="center",
    va="top",
    transform=ax1.transAxes,
)

# Background
ax1.set_facecolor(PANEL_COLOR)
ax2.set_facecolor(PANEL_COLOR)

# Grid
ax1.grid(axis="y", color=GRID_COLOR, linewidth=0.4, zorder=0)
ax1.grid(axis="x", visible=False)
ax1.set_axisbelow(True)

# Spines
for spine in ax1.spines.values():
    spine.set_color("#CCCCCC")
    spine.set_linewidth(0.4)
for spine in ax2.spines.values():
    spine.set_color("#CCCCCC")
    spine.set_linewidth(0.4)

# Tick parameters
ax1.tick_params(axis="y", colors=TEXT_COLOR, labelsize=10)
ax2.tick_params(axis="y", colors=TEXT_COLOR, labelsize=10)
ax1.tick_params(axis="x", colors=TEXT_COLOR, labelsize=10)

# Remove top spines
ax1.spines["top"].set_visible(False)
ax2.spines["top"].set_visible(False)

# Move left and right spines slightly for a cleaner look
ax1.spines["left"].set_position(("outward", 8))
ax2.spines["right"].set_position(("outward", 8))
ax1.spines["bottom"].set_position(("outward", 6))

# ----- Caption (source line) — FIX 5: kept above cut-off with wider bottom margin -----

ax1.text(
    0.5,
    -0.08,
    "Sources: Dean Runyan Associates (MOTT) \u2022 U.S. Census Bureau",
    fontsize=8.5,
    color=CAPTION_CLR,
    ha="center",
    va="top",
    transform=ax1.transAxes,
)

# =====================================================================
# 5. EXPORT
# =====================================================================

image_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
image_dir.mkdir(parents=True, exist_ok=True)

script_path = Path(
    "/home/pi/Documents/code/quortol/backend/blogs/scripts"
    "/chart1_the-two-berkshires_spending_vs_population.py"
)
png_path = image_dir / "the-two-berkshires_spending_vs_population.png"

fig.savefig(
    png_path,
    dpi=dpi,
    facecolor=BG_COLOR,
    edgecolor="none",
)

plt.close(fig)

# Verify
file_size = png_path.stat().st_size
print(f"Chart saved to: {png_path}")
print(f"Script:       {script_path}")
print(f"File size:    {file_size:,} bytes")
print(f"Dimensions:   {w_inches * dpi:.0f} x {h_inches * dpi:.0f} px @ {dpi} DPI")
print(f"Layout:       constrained_layout removed; subplots_adjust(top=0.85, bottom=0.18, left=0.12, right=0.88)")
