#!/usr/bin/env python3
"""
Chart: India's Top Agricultural Exports, 2024–25 (US$ Billion)
Output: ../images/indian-food-history-future_export_composition.png  (1200 × 720 px, 150 DPI)

Horizontal bar chart showing the top 10 agricultural and processed food
export commodities from India for the fiscal year 2024–25.

Data source: APEDA (Agricultural and Processed Food Products Export
Development Authority), Government of India, 2024–25.
"""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ============================================================================
# 1. DATA  —  Sorted largest to smallest (from APEDA)
# ============================================================================
commodities = [
    "Marine Products",
    "Non-Basmati Rice",
    "Basmati Rice",
    "Spices",
    "Buffalo Meat",
    "Sugar",
    "Coffee",
    "Misc Processed Items",
    "Tobacco (Unmanufactured)",
    "Oil Meals",
]

values = [7.41, 6.53, 5.94, 4.45, 4.06, 2.16, 1.81, 1.68, 1.48, 1.34]

# ============================================================================
# 2. STYLE CONSTANTS
# ============================================================================
BAR_COLOR = "#e67e22"        # Spice-inspired saffron / warm orange
BAR_EDGE_COLOR = "#c96b1e"   # Slightly darker edge for definition
TEXT_COLOR = "#2c2c2c"
SOURCE_COLOR = "#888888"
GRID_COLOR = "#eaeaea"
BG_COLOR = "#ffffff"

# ============================================================================
# 3. CREATE THE CHART
# ============================================================================
# 8 × 4.8 in @ 150 DPI = exactly 1200 × 720 px
WIDTH, HEIGHT = 8, 4.8
DPI = 150

fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT))

# --- Horizontal bars ---
y_pos = np.arange(len(commodities))

bars = ax.barh(
    y_pos,
    values,
    height=0.65,
    color=BAR_COLOR,
    edgecolor=BAR_EDGE_COLOR,
    linewidth=0.5,
    zorder=2,
)

# --- Data labels at end of each bar ---
for bar, val in zip(bars, values):
    ax.text(
        bar.get_width() + 0.08,
        bar.get_y() + bar.get_height() / 2,
        f"${val:.2f}B",
        va="center",
        ha="left",
        fontsize=10,
        color=TEXT_COLOR,
        fontweight="semibold",
    )

# --- Y-axis: commodity labels ---
ax.set_yticks(y_pos)
ax.set_yticklabels(commodities, fontsize=11, color=TEXT_COLOR)

# --- X-axis ---
ax.set_xlim(0, 9.0)  # Room for labels past the longest bar (7.41)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("${x:.0f}B"))
ax.tick_params(axis="x", labelsize=9, colors="#555555")

# --- Title ---
ax.set_title(
    "India's Top Agricultural Exports, 2024–25 (US$ Billion)",
    fontsize=16,
    fontweight="bold",
    color=TEXT_COLOR,
    pad=10,
    loc="left",
)

# --- Grid + spines ---
ax.xaxis.grid(True, color=GRID_COLOR, linewidth=0.4, zorder=0)
ax.yaxis.grid(False)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["bottom", "left"]:
    ax.spines[spine].set_color(GRID_COLOR)
    ax.spines[spine].set_linewidth(0.5)

ax.invert_yaxis()
ax.set_ylabel("")
ax.set_xlabel("")

# --- Layout: manual margins to leave room for source at bottom ---
fig.subplots_adjust(left=0.20, right=0.90, top=0.88, bottom=0.10)

# --- Source line (in figure coordinates, below axes) ---
fig.text(
    0.5, 0.02,
    "Source: APEDA, Government of India, 2024-25",
    fontsize=8,
    color=SOURCE_COLOR,
    ha="center",
    va="bottom",
)

# ============================================================================
# 4. SAVE PNG  — exactly 1200 × 720 px @ 150 DPI
# ============================================================================
output_path = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "indian-food-history-future_export_composition.png"
)
plt.savefig(
    output_path,
    dpi=DPI,
    facecolor=BG_COLOR,
    edgecolor="none",
)
plt.close()

print(f"✓ Chart saved to {output_path}")
print(f"  Dimensions: {int(WIDTH * DPI)} × {int(HEIGHT * DPI)} px  @  {DPI} DPI")
