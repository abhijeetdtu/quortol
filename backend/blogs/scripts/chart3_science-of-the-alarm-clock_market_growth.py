#!/usr/bin/env python3
"""
Chart: Global Alarm Clock Market Growth (2019–2034)
===================================================
Line chart showing historical and projected market size, with a vertical
separator at 2025 and a pie-style annotation for 2025 segment composition.

Data source: Dataintelo, Global Alarm Clock Market Report (2025)
Output: ../images/science-of-the-alarm-clock_market_growth.png  (1200 × 720 px, 150 DPI)
"""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# ============================================================================
# 1. DATA
# ============================================================================
years = np.array([
    2019, 2020, 2021, 2022, 2023, 2024, 2025,
    2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034,
])

market_size = np.array([
    2.1, 2.1, 2.3, 2.4, 2.5, 2.7, 2.8,
    2.9, 3.1, 3.2, 3.4, 3.6, 3.8, 3.9, 4.1, 4.3,
])

historical_years = years[:7]   # 2019–2025
historical_values = market_size[:7]
forecast_years = years[6:]      # 2025–2034 (include 2025 for overlap)
forecast_values = market_size[6:]

# ============================================================================
# 2. STYLE CONSTANTS
# ============================================================================
TEAL = "#2E86AB"
TEAL_LIGHT = "#7DBFCD"
TEAL_DARK = "#1A5F7A"
RED_ACCENT = "#C44536"
GREEN_ACCENT = "#2A9D8F"
GOLD_ACCENT = "#E9C46A"
TEXT_COLOR = "#2C2C2C"
SOURCE_COLOR = "#888888"
GRID_COLOR = "#E8E8E8"
BG_COLOR = "#FAFAFA"
DIVIDER_COLOR = "#888888"

# ============================================================================
# 3. CREATE THE CHART
# ============================================================================
# 8 × 4.8 in @ 150 DPI = exactly 1200 × 720 px
WIDTH, HEIGHT = 8.0, 4.8
DPI = 150

fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# -- Historical line (2019–2025) dashed, lighter --
ax.plot(
    historical_years, historical_values,
    color=TEAL_LIGHT,
    linewidth=2.5,
    linestyle="--",
    marker="o",
    markersize=7,
    markerfacecolor=TEAL_LIGHT,
    markeredgecolor=TEAL_DARK,
    markeredgewidth=1.0,
    zorder=5,
    label="Historical (2019–2025)",
)

# -- Forecast line (2025–2034) solid, full colour --
ax.plot(
    forecast_years, forecast_values,
    color=TEAL,
    linewidth=3.0,
    linestyle="-",
    marker="s",
    markersize=7,
    markerfacecolor=TEAL,
    markeredgecolor=TEAL_DARK,
    markeredgewidth=1.2,
    zorder=6,
    label="Projected (2026–2034)",
)

# -- Vertical separator at 2025 --
ax.axvline(
    x=2025,
    color=DIVIDER_COLOR,
    linewidth=1.2,
    linestyle="--",
    zorder=3,
)
# Small label above the divider
ax.text(
    2025, 4.85, "← Historical  |  Forecast →",
    fontsize=8,
    color=DIVIDER_COLOR,
    ha="center",
    va="top",
    style="italic",
)

# -- Emphasise the 2025 data point --
ax.scatter(
    [2025], [2.8],
    color=TEAL_DARK,
    s=120,
    zorder=10,
    edgecolors="white",
    linewidth=1.5,
)
ax.annotate(
    "$2.8B",
    xy=(2025, 2.8),
    xytext=(2025.8, 2.55),
    fontsize=11,
    fontweight="bold",
    color=TEAL_DARK,
    ha="left",
    arrowprops=dict(arrowstyle="->", color=TEAL_DARK, lw=1.2),
)

# -- Emphasise the 2034 end point --
ax.annotate(
    "$4.3B",
    xy=(2034, 4.3),
    xytext=(2032.5, 4.55),
    fontsize=11,
    fontweight="bold",
    color=TEAL,
    ha="center",
    arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.2),
)

# ============================================================================
# 4. SEGMENTED BREAKDOWN ANNOTATION (2025 composition)
# ============================================================================
# A small table / text block in the lower-right area
breakdown_box_x = 2028.5
breakdown_box_y = 1.8

# Draw a subtle bounding box
bbox_props = dict(
    boxstyle="round,pad=0.5",
    facecolor="#F0F7FA",
    edgecolor=TEAL_LIGHT,
    linewidth=0.8,
)

breakdown_text = (
    "2025 Market Composition\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "Digital alarm clocks    42.5%\n"
    "Smart alarm clocks      fastest growing\n"
    "Traditional / analog    declining share"
)

ax.text(
    breakdown_box_x, breakdown_box_y,
    breakdown_text,
    fontsize=9,
    color=TEXT_COLOR,
    ha="left",
    va="bottom",
    family="monospace",
    bbox=bbox_props,
    zorder=20,
)

# ============================================================================
# 5. CAGR ANNOTATION
# ============================================================================
# Place CAGR label above the forecast line, near the middle
ax.annotate(
    "CAGR 4.9%\n(2025–2034)",
    xy=(2029.5, 3.3),
    fontsize=10,
    fontweight="bold",
    color=GREEN_ACCENT,
    ha="center",
    va="bottom",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#E8F5E9", edgecolor=GREEN_ACCENT, linewidth=0.8),
)

# ============================================================================
# 6. AXIS LABELS & FORMATTING
# ============================================================================
ax.set_xlabel("Year", fontsize=12, color=TEXT_COLOR, labelpad=8)
ax.set_ylabel("Market Size (US$ billions)", fontsize=12, color=TEXT_COLOR, labelpad=8)

ax.set_xlim(2018.2, 2035.2)
ax.set_ylim(1.5, 5.0)

ax.set_xticks(np.arange(2019, 2035, 1))
ax.tick_params(axis="x", labelsize=10, rotation=45, color=TEXT_COLOR)
ax.tick_params(axis="y", labelsize=10, color=TEXT_COLOR)

# Y-axis with one decimal place
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))

# ============================================================================
# 7. TITLE & SUBTITLE
# ============================================================================
ax.set_title(
    "The Global Alarm Clock Market",
    fontsize=18,
    fontweight="bold",
    color=TEXT_COLOR,
    pad=40,
    loc="left",
)

# Subtitle (positioned manually since fig.suptitle gets tricky)
ax.text(
    2018.2, 4.85,
    "$2.8 billion in 2025, projected to reach $4.3 billion by 2034 (CAGR 4.9%)",
    fontsize=11,
    color="#555555",
    ha="left",
    va="top",
)

# ============================================================================
# 8. LEGEND
# ============================================================================
legend = ax.legend(
    loc="upper left",
    fontsize=10,
    frameon=True,
    facecolor=BG_COLOR,
    edgecolor=GRID_COLOR,
    framealpha=0.95,
)
legend.get_frame().set_linewidth(0.8)

# ============================================================================
# 9. GRID
# ============================================================================
ax.grid(True, linestyle=":", linewidth=0.6, color=GRID_COLOR, alpha=0.8)
ax.set_axisbelow(True)

# Remove top and right spines for cleaner look
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color(GRID_COLOR)
ax.spines["bottom"].set_color(GRID_COLOR)

# ============================================================================
# 10. SOURCE LINE
# ============================================================================
ax.text(
    2018.2, 1.55,
    "Source: Dataintelo, Global Alarm Clock Market Report (2025)",
    fontsize=9,
    color=SOURCE_COLOR,
    ha="left",
    va="bottom",
    style="italic",
)

# ============================================================================
# 11. SAVE  — exactly 1200 × 720 px @ 150 DPI
# ============================================================================
plt.tight_layout()

script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)
output_png = images_dir / "science-of-the-alarm-clock_market_growth.png"

plt.savefig(
    output_png,
    dpi=DPI,
    facecolor=BG_COLOR,
    edgecolor="none",
)
plt.close()

print(f"✓ Chart saved to {output_png}")
print(f"  Dimensions: {int(WIDTH * DPI)} × {int(HEIGHT * DPI)} px  @  {DPI} DPI")
