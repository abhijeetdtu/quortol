#!/usr/bin/env python3
"""
Horizontal bar chart: Median home values across the six New England states.
Data: U.S. Census Bureau QuickFacts, 2020–2024 American Community Survey 5-Year Estimates.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
states = [
    "Massachusetts",
    "Rhode Island",
    "New Hampshire",
    "Connecticut",
    "Vermont",
    "Maine",
]
values = [562_100, 404_200, 402_500, 366_900, 316_600, 296_600]

national_median = 332_700

# ---------------------------------------------------------------------------
# Figure setup
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.8), dpi=100)
# Remove extra margins
fig.subplots_adjust(left=0.18, right=0.88, top=0.88, bottom=0.15)

# ---------------------------------------------------------------------------
# Bar colours – single warm hue, intensity varying by value
# ---------------------------------------------------------------------------
base_color = np.array([0.839, 0.373, 0.196])  # #D55E00-ish muted red-orange
# Scale saturation from 0.45 to 1.0 based on value rank
normalised = (np.array(values) - min(values)) / (max(values) - min(values))
colours = [base_color * (0.50 + 0.50 * v) for v in normalised]
# Clamp to valid RGB
colours = [np.clip(c, 0, 1) for c in colours]

# ---------------------------------------------------------------------------
# Horizontal bars (y=0..5, highest value at top → index 0 at top)
# ---------------------------------------------------------------------------
y_pos = np.arange(len(states))
bars = ax.barh(y_pos, values, height=0.65, color=colours, edgecolor="none", zorder=3)

# ---------------------------------------------------------------------------
# Data labels on bars
# ---------------------------------------------------------------------------
for bar, val in zip(bars, values):
    label = f"${val:,}"
    ax.text(
        bar.get_width() + 8_000,
        bar.get_y() + bar.get_height() / 2,
        label,
        va="center",
        ha="left",
        fontsize=9,
        color="#333333",
        fontweight="bold",
    )

# ---------------------------------------------------------------------------
# Vertical reference line – national median
# ---------------------------------------------------------------------------
ax.axvline(
    x=national_median,
    color="#555555",
    linestyle="--",
    linewidth=1.2,
    zorder=4,
)
# Label for the reference line
ax.text(
    national_median,
    -0.45,
    f"U.S. National Median: ${national_median:,}",
    ha="center",
    va="top",
    fontsize=8.5,
    color="#555555",
    style="italic",
)

# ---------------------------------------------------------------------------
# Annotation – Massachusetts exceeds national average by 69 %
# ---------------------------------------------------------------------------
ma_value = values[0]
pct_above = (ma_value - national_median) / national_median * 100
ax.annotate(
    f"Massachusetts exceeds national median by {pct_above:.0f}%",
    xy=(ma_value, 0),
    xytext=(ma_value + 95_000, 0.35),
    ha="left",
    va="bottom",
    fontsize=8,
    color="#881100",
    fontweight="semibold",
    arrowprops=dict(arrowstyle="->", color="#881100", lw=0.9),
)

# ---------------------------------------------------------------------------
# Axis labels & ticks
# ---------------------------------------------------------------------------
ax.set_yticks(y_pos)
ax.set_yticklabels(states, fontsize=11, fontweight="semibold", color="#222222")

ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.set_xlim(0, max(values) * 1.30)  # room for labels and annotation
ax.tick_params(axis="x", labelsize=9, colors="#555555")

# ---------------------------------------------------------------------------
# Titles
# ---------------------------------------------------------------------------
ax.set_title(
    "Median Home Value by State, New England",
    fontsize=16,
    fontweight="bold",
    color="#222222",
    pad=8,
    loc="left",
)
ax.text(
    0, 1.025,
    "2020–2024 American Community Survey 5-Year Estimates",
    transform=ax.transAxes,
    fontsize=10,
    color="#666666",
    ha="left",
    va="bottom",
)

# ---------------------------------------------------------------------------
# Source line at bottom
# ---------------------------------------------------------------------------
fig.text(
    0.18, 0.02,
    "Source: U.S. Census Bureau QuickFacts",
    fontsize=8,
    color="#888888",
    ha="left",
)

# ---------------------------------------------------------------------------
# Clean magazine aesthetic – remove top/right spines, light horizontal grid
# ---------------------------------------------------------------------------
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color("#cccccc")
ax.spines["bottom"].set_color("#cccccc")

ax.xaxis.grid(True, linestyle="--", alpha=0.3, color="#aaaaaa", zorder=0)
ax.set_axisbelow(True)

ax.tick_params(axis="y", left=False)  # remove y-axis ticks, keep labels

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_path = "/home/pi/Documents/code/quortol/backend/blogs/images/new-england-homes_state_values.png"
fig.savefig(output_path, dpi=150, facecolor="white")
plt.close(fig)
print(f"Chart saved to {output_path}")
