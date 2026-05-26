#!/usr/bin/env python3
"""
chart3_north_conway_snowfall.py

Bar chart: Historical snowfall at Cranmore Mountain Resort, North Conway, NH.
Data from OnTheSnow — Cranmore Mountain Resort Snow History.

Output: 1200x720 px PNG at 150 DPI
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Data ──────────────────────────────────────────────────────────────────────
seasons = [
    "2012-13", "2013-14", "2014-15", "2015-16", "2016-17",
    "2017-18", "2018-19", "2019-20", "2020-21", "2021-22",
    "2022-23", "2023-24", "2024-25",
]
snowfall = [88, 93, 84, 29, 141, 120, 67, 73, 48, 89, 117, 102, 66]
average = 86.0

# ── Colour palette (colorblind-safe) ──────────────────────────────────────────
BAR_COLOR = "#3498DB"
AVG_COLOR = "#D62728"     # distinct red, visible to most colour vision deficiencies
AVG_LABEL_COLOR = "#A02020"

# ── Figure setup ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)

x = np.arange(len(seasons))
bars = ax.bar(x, snowfall, width=0.62, color=BAR_COLOR, edgecolor="white",
              linewidth=0.5, zorder=3)

# ── Average line ──────────────────────────────────────────────────────────────
ax.axhline(y=average, color=AVG_COLOR, linestyle="--", linewidth=1.5,
           zorder=4, alpha=0.85)

# Annotate "Avg: 86"" to the right of the line, near the last bar
label_x = len(seasons) - 1 + 0.5  # just past the last season tick
ax.annotate(
    f"Avg: {int(average)}\u2033",
    xy=(label_x, average + 1),
    fontsize=9, fontweight="semibold",
    color=AVG_LABEL_COLOR,
    va="bottom", ha="left",
    zorder=5,
)

# ── Data labels on top of each bar ────────────────────────────────────────────
for i, (s, v) in enumerate(zip(seasons, snowfall)):
    ax.text(
        i, v + 2.5, f"{v}",
        ha="center", va="bottom",
        fontsize=6.5, fontweight="bold",
        color="#2C3E50",
        zorder=6,
    )

# ── Axes styling ──────────────────────────────────────────────────────────────
ax.set_xlim(-0.6, len(seasons) - 1 + 0.6)
ax.set_ylim(0, 160)

ax.set_xticks(x)
ax.set_xticklabels(seasons, rotation=45, ha="right", fontsize=8.5)
ax.set_ylabel("Snowfall (inches)", fontsize=10, labelpad=8)
ax.set_title(
    "Cranmore Mountain — Annual Snowfall by Season\n"
    "Total snowfall in inches  |  Source: OnTheSnow historical data",
    fontsize=14, fontweight="bold", pad=14, linespacing=1.4,
)

# ── Grid & spines ─────────────────────────────────────────────────────────────
ax.yaxis.set_major_locator(mticker.MultipleLocator(20))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(10))
ax.grid(axis="y", which="major", color="#DDDDDD", linewidth=0.6, zorder=0)
ax.grid(axis="y", which="minor", color="#EEEEEE", linewidth=0.3, zorder=0)
ax.set_axisbelow(True)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["bottom", "left"]:
    ax.spines[spine].set_color("#CCCCCC")
    ax.spines[spine].set_linewidth(0.8)

ax.tick_params(axis="y", labelsize=8.5, length=3)
ax.tick_params(axis="x", length=3)

# ── Source line at bottom ─────────────────────────────────────────────────────
fig.text(
    0.5, -0.03,
    "Data: OnTheSnow — Cranmore Mountain Resort Snow History",
    ha="center", va="top",
    fontsize=7.5, color="#777777",
    fontstyle="italic",
)

plt.tight_layout()

# ── Save ──────────────────────────────────────────────────────────────────────
output_path = "/home/pi/Documents/code/quortol/backend/blogs/images/north_conway_snowfall.png"
fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"✅ Chart saved → {output_path}")
