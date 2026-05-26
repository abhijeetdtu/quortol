#!/usr/bin/env python3
"""
Chart 3: Ocean Species Discovery — Clean, minimalist redesign.
Uses matplotlib. 1200×720 px @ 150 DPI.

Layout:
  ┌──────────────────────────────────────────────────────┐
  │  TITLE LINE                                          │
  │  SUBTITLE LINE                                       │
  ├──────────────────────┬───────────────────────────────┤
  │  Bar chart           │  Donut chart                  │
  │  (annual discovered) │  (known vs unknown)           │
  │                      │                               │
  ├──────────────────────┴───────────────────────────────┤
  │  3 annotation bullets (compact row or 2+1)           │
  ├──────────────────────────────────────────────────────┤
  │  Source line                                          │
  └──────────────────────────────────────────────────────┘
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# COLOUR PALETTE  (colorblind-safe, Wong 2011)
# ---------------------------------------------------------------------------
SKY_BLUE   = "#56B4E9"   # baseline bar
TEAL       = "#009E73"   # year 2 bar / known slice
DARK_BLUE  = "#0072B2"   # year 3 bar
ORANGE     = "#E69F00"   # accent highlights
GRAY_LIGHT = "#CCCCCC"   # unknown slice
GRAY_MED   = "#999999"   # secondary text / subtle lines
GRAY_DARK  = "#333333"   # body text
WHITE      = "#FFFFFF"
BG_PANEL   = "#F2F3F5"   # annotation panel background

# ---------------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------------
cat_labels = [
    "Pre-Ocean Census\nBaseline",
    "Ocean Census\nYear 2",
    "Ocean Census\nYear 3",
]
values = [1900, 900, 1121]
bar_colors = [SKY_BLUE, TEAL, DARK_BLUE]

known   = 250_000
unknown = 2_000_000
total   = known + unknown
known_pct  = known / total * 100    # ≈ 11.1
unknown_pct = unknown / total * 100  # ≈ 88.9

# ---------------------------------------------------------------------------
# FIGURE SETUP
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(8, 4.8), dpi=150)
fig.patch.set_facecolor(WHITE)

# --- Title & subtitle ---
fig.text(0.50, 0.980,
         "Discovering the Ocean\u2019s Hidden Life",
         ha="center", va="top",
         fontsize=17, fontweight="bold", color=GRAY_DARK)

fig.text(0.50, 0.955,
         "Annual marine species discoveries are accelerating, but 90% remain unknown",
         ha="center", va="top",
         fontsize=9.5, color=GRAY_MED, fontstyle="italic")

# ---------------------------------------------------------------------------
# LAYOUT COORDINATES  (all normalised figure coords)
# ---------------------------------------------------------------------------
chart_left   = 0.075
chart_right  = 0.935
chart_bottom = 0.26
chart_top    = 0.935

bar_left  = chart_left
bar_right = 0.505
bar_width  = bar_right - bar_left          # 0.430

donut_left  = 0.555
donut_width  = chart_right - donut_left   # 0.380

ann_top    = 0.230
ann_bottom = 0.055

src_y = 0.015

# --- Axes ---
ax_bar   = fig.add_axes([bar_left,  chart_bottom, bar_width,  chart_top - chart_bottom])
ax_donut = fig.add_axes([donut_left, chart_bottom, donut_width, chart_top - chart_bottom])

# --- Separator line (vertical, between panels) ---
sep_x = (bar_right + donut_left) / 2   # ≈ 0.530
fig.lines.append(plt.Line2D(
    [sep_x, sep_x],
    [chart_bottom + 0.015, chart_top - 0.015],
    transform=fig.transFigure,
    color="#D5D7DB", linewidth=0.7, zorder=0,
))

# ============================================================================
# PANEL 1 — BAR CHART
# ============================================================================
ax_bar.grid(axis="y", alpha=0.18, linestyle="--")
ax_bar.set_axisbelow(True)

bars = ax_bar.bar(
    cat_labels, values,
    color=bar_colors, width=0.55,
    edgecolor=WHITE, linewidth=0.7,
    zorder=3,
)

# Value labels ABOVE bars at a safe distance
for b, v in zip(bars, values):
    ax_bar.text(
        b.get_x() + b.get_width() / 2,
        b.get_height() + 40,                      # safe offset above bar
        f"{v:,}",
        ha="center", va="bottom",
        fontsize=10, fontweight="bold", color=GRAY_DARK,
    )

# Percentage-change callouts INSIDE bar tops (white bbox)
pct_labels = ["", "+38%", "+54%"]
pct_colors = [GRAY_DARK, ORANGE, ORANGE]
pct_bbox   = dict(boxstyle="round,pad=0.15", fc=WHITE, ec="none", alpha=0.90)
for b, pct, clr in zip(bars, pct_labels, pct_colors):
    if pct:
        ax_bar.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() * 0.88,               # inside top of bar
            pct,
            ha="center", va="center",
            fontsize=7, fontweight="bold", color=clr,
            bbox=pct_bbox,
        )

# Baseline dashed reference line at 1900
ax_bar.axhline(y=1900, color=SKY_BLUE, linewidth=1.1, linestyle="--",
               alpha=0.45, zorder=2)

# Baseline label in top-right corner of the panel
ax_bar.text(
    0.97, 0.94, "Baseline: ~1,900/yr",
    fontsize=7, color=SKY_BLUE, fontweight="bold",
    transform=ax_bar.transAxes,
    ha="right", va="top",
)

ax_bar.set_title("Annual Marine Species Discovered",
                 fontsize=12.5, pad=6, fontweight="bold")
ax_bar.set_ylabel("New Species per Year", fontsize=9.5)
ax_bar.set_ylim(0, 2200)
ax_bar.spines["left"].set_visible(False)
ax_bar.tick_params(left=False)

# ============================================================================
# PANEL 2 — DONUT CHART
# ============================================================================
sizes      = [known, unknown]
donut_cols = [TEAL, GRAY_LIGHT]

wedges, _ = ax_donut.pie(
    sizes,
    labels=None,
    colors=donut_cols,
    startangle=90,
    explode=(0.02, 0.0),
    wedgeprops={"linewidth": 0.8, "edgecolor": WHITE},
)

# Centre hole (larger for a cleaner donut look)
centre = plt.Circle((0, 0), 0.60, fc=WHITE, ec=WHITE, linewidth=0)
ax_donut.add_artist(centre)

# Centre label
ax_donut.text(0, 0,
              f"~{known_pct:.0f}% Known",
              ha="center", va="center",
              fontsize=15, fontweight="bold", color=TEAL)

# External labels with leader lines — increased radius for zero overlap
label_r = 1.35
leader_r = 0.60   # start of leader line close to wedge

# --- Known label ---
angle_deg  = 90.0 + 360.0 * known / total / 2.0
angle_rad  = np.deg2rad(angle_deg)
lx = label_r * np.cos(angle_rad)
ly = label_r * np.sin(angle_rad)

# leader line
ax_donut.plot(
    [leader_r * np.cos(angle_rad), lx],
    [leader_r * np.sin(angle_rad), ly],
    color=TEAL, linewidth=0.5, alpha=0.5,
)

ax_donut.text(lx, ly,
              "Known   250,000  (11%)",
              ha="center", va="center",
              fontsize=7, color=TEAL, fontweight="bold")

# --- Unknown label ---
angle_deg2 = (
    90.0
    + 360.0 * known / total
    + 360.0 * unknown / total / 2.0
)
angle_rad2 = np.deg2rad(angle_deg2)
lx2 = label_r * np.cos(angle_rad2)
ly2 = label_r * np.sin(angle_rad2)

ax_donut.plot(
    [leader_r * np.cos(angle_rad2), lx2],
    [leader_r * np.sin(angle_rad2), ly2],
    color=GRAY_MED, linewidth=0.5, alpha=0.5,
)

ax_donut.text(lx2, ly2,
              "Unknown  ~2,000,000  (89%)",
              ha="center", va="center",
              fontsize=7, color=GRAY_MED, fontweight="bold")

ax_donut.set_title("The Scale of the Unknown",
                   fontsize=12.5, pad=6, fontweight="bold")

# ============================================================================
# PANEL 3 — BOTTOM ANNOTATIONS (3 items, compact row layout)
# ============================================================================
ax_ann = fig.add_axes([chart_left, ann_bottom,
                       chart_right - chart_left, ann_top - ann_bottom])
ax_ann.set_facecolor(BG_PANEL)
ax_ann.patch.set_edgecolor("#E0E2E6")
ax_ann.patch.set_linewidth(0.4)
ax_ann.set_zorder(-1)
ax_ann.axis("off")

# Three annotation items in a single horizontal row
items = [
    ("Collection to description",
     "Traditional time from collection to formal description: 13.5 years",
     SKY_BLUE),
    ("Ocean Census goal",
     "100,000 new species in 10 years",
     TEAL),
    ("MEER Project",
     "7,564 microbial species found in Mariana Trench sediment \u2014 89% new to science",
     ORANGE),
]

n_items = len(items)
for i, (label, text, colour) in enumerate(items):
    # Centre of each annotation segment
    x_centre = (i + 0.5) / n_items     # 0.1667, 0.5000, 0.8333
    y_line   = 0.60

    # Bullet dot
    ax_ann.plot(x_centre, y_line,
                marker="o", color=colour, markersize=5,
                transform=ax_ann.transAxes, clip_on=False)

    # Bold label
    ax_ann.text(x_centre, y_line - 0.40, label,
                fontsize=7, fontweight="bold", color=colour,
                ha="center", va="top",
                transform=ax_ann.transAxes)

    # Description text
    ax_ann.text(x_centre, y_line + 0.40, text,
                fontsize=6.5, color=GRAY_DARK,
                ha="center", va="bottom",
                transform=ax_ann.transAxes)

# Thin separator line above the annotation panel (subtle)
fig.lines.append(plt.Line2D(
    [chart_left + 0.01, chart_right - 0.01],
    [ann_top, ann_top],
    transform=fig.transFigure,
    color="#D5D7DB", linewidth=0.5, zorder=0,
))

# ============================================================================
# SOURCE LINE
# ============================================================================
fig.text(
    0.50, src_y,
    "Sources: Ocean Census (oceancensus.org); NOAA Ocean Exploration; "
    "Census of Marine Life (coml.org); Schmidt Ocean Institute; Cell (2025)",
    ha="center", fontsize=6.5, color=GRAY_MED, fontstyle="italic",
)

# ============================================================================
# SAVE
# ============================================================================
out_dir = Path(__file__).resolve().parents[1] / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "ocean_species_discovery.png"

fig.savefig(out_path, dpi=150, facecolor=WHITE, edgecolor="none")
plt.close(fig)

print(f"Saved: {out_path}")
print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
print(f"  Dimensions: 1200 x 720 px @ 150 DPI")
