"""
Ocean Floor Mapping Progress Chart
====================================
Line chart showing yearly progress of global seafloor mapping (2017–2026)
using data from the Nippon Foundation-GEBCO Seabed 2030 Project.

Output: backend/blogs/images/ocean_mapping_progress.png (1200×720 px, 150 DPI)
"""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
pct =   [6.0,  8.0,  12.0, 15.0, 19.0, 21.0, 23.0, 26.1, 27.3, 28.7]

# ---------------------------------------------------------------------------
# Colour palette (colorblind-safe)
# ---------------------------------------------------------------------------
NAVY  = "#1a3a5c"
FILL  = "#c8dce8"
GRID  = "#d8d8d8"
GRAY  = "#777777"

# ---------------------------------------------------------------------------
# Figure setup — 1200×720 px @ 150 DPI  =>  8 × 4.8 inches
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.8))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ---------------------------------------------------------------------------
# Area fill under the curve
# ---------------------------------------------------------------------------
ax.fill_between(years, pct, 0, color=FILL, alpha=0.75, zorder=1)

# ---------------------------------------------------------------------------
# Line
# ---------------------------------------------------------------------------
ax.plot(years, pct, color=NAVY, linewidth=2.0, solid_capstyle="round", zorder=3)

# ---------------------------------------------------------------------------
# Points (area ≈ 40 → s=40 in matplotlib scatter)
# ---------------------------------------------------------------------------
ax.scatter(years, pct, color=NAVY, s=40, zorder=4, edgecolors="white",
           linewidths=0.5)

# ---------------------------------------------------------------------------
# Data labels — stagger to avoid overlap; skip some years if needed
# Years shown: 2017, 2019, 2021, 2023, 2024, 2025, 2026
#   (skip 2018, 2020, 2022 to prevent crowding)
# Nudge: even-indexed in this list get nudge_up=1.0, odd get nudge_up=1.8
#   to stagger vertical position
# ---------------------------------------------------------------------------
label_years = [2017, 2019, 2021, 2023, 2024, 2025, 2026]
label_pcts  = [6.0,  12.0, 19.0, 23.0, 26.1, 27.3, 28.7]
label_offsets = [1.8, 1.2, 1.8, 1.2, 1.0, 1.0, 1.0]

for yr, pv, off in zip(label_years, label_pcts, label_offsets):
    ax.text(yr, pv + off, f"{pv:.1f}%",
            fontsize=7, ha="center", va="bottom",
            color=NAVY, fontfamily="sans-serif")

# ---------------------------------------------------------------------------
# Y-axis — range 0–35 with clean breaks
# ---------------------------------------------------------------------------
ax.set_ylim(0, 35)
ax.set_yticks([0, 5, 10, 15, 20, 25, 30, 35])
ax.set_yticklabels(["0%", "5%", "10%", "15%", "20%", "25%", "30%", "35%"],
                   fontsize=8.5, color=GRAY)

# X-axis — every year labelled
ax.set_xlim(2016.5, 2026.5)
ax.set_xticks(years)
ax.set_xticklabels([str(y) for y in years], fontsize=8.5, color=GRAY)

# ---------------------------------------------------------------------------
# Spines — keep left and bottom, very thin
# ---------------------------------------------------------------------------
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color(GRID)
ax.spines["left"].set_linewidth(0.5)
ax.spines["bottom"].set_color(GRID)
ax.spines["bottom"].set_linewidth(0.5)

# ---------------------------------------------------------------------------
# Grid — horizontal only, light gray
# ---------------------------------------------------------------------------
ax.grid(axis="y", color=GRID, linewidth=0.4, linestyle="-")
ax.grid(axis="x", visible=False)
ax.set_axisbelow(True)

# ---------------------------------------------------------------------------
# Ticks
# ---------------------------------------------------------------------------
ax.tick_params(axis="both", which="both", length=0, pad=6)

# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------
ax.set_ylabel("Percentage of seafloor mapped", fontsize=9, color=GRAY,
              labelpad=10)

# ---------------------------------------------------------------------------
# Title & subtitle via ax.set_title so layout auto-adjusts
# ---------------------------------------------------------------------------
ax.set_title(
    "The Ocean Floor: Mapping Progress Toward 2030",
    fontsize=18, fontweight="bold", color=NAVY,
    loc="left", pad=6,
)

# Subtitle: place with fig.text for more control (anchored to axes left)
fig.text(
    0.125, 0.895,                                    # axes coords
    "Percentage of global seafloor mapped to modern high-resolution standards  |  "
    "Source: Nippon Foundation-GEBCO Seabed 2030 Project",
    fontsize=7.5, color=GRAY, ha="left", va="top",
)

# ---------------------------------------------------------------------------
# Footnote — below the plot bounding box
# ---------------------------------------------------------------------------
fig.text(
    0.125, 0.02,
    "Data: Seabed 2030 Project (gebco.org); Frontiers in Marine Science (2025)",
    fontsize=6.5, color="#aaaaaa", ha="left", va="bottom",
)

# ---------------------------------------------------------------------------
# Tight layout & save
# ---------------------------------------------------------------------------
OUTPUT_PATH = "/home/pi/Documents/code/quortol/backend/blogs/images/ocean_mapping_progress.png"

plt.subplots_adjust(left=0.105, right=0.98, top=0.88, bottom=0.12)
plt.savefig(OUTPUT_PATH, dpi=150, facecolor="white", edgecolor="none")
plt.close(fig)

print(f"Chart saved -> {OUTPUT_PATH}")
print(f"Dimensions: 1200 × 720 px @ 150 DPI")
