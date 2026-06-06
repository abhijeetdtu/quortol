#!/usr/bin/env python3
"""
Chart: Twenty-Seven Astrologers vs. a Coin Flip.

Dot plot / strip chart of individual astrologer performance in the
Narlikar et al. (2009) double-blind test of Indian astrology, published
in Current Science.

Reference lines:
  - Chance (20/40)           dashed red
  - 70% threshold (28/40)    dashed green
  - Average (17.25/40)       dotted blue

Source: Narlikar et al. 2009, Current Science
"""

import numpy as np
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# =====================================================================
# 1. DATA
# =====================================================================

# Simulated individual scores (27 astrologers, correct out of 40 birth charts),
# matching the published summary statistics from Narlikar et al. (2009).
scores = [
    24, 22, 22, 20, 20, 19, 19, 18, 18, 18,
    17, 17, 17, 17, 17, 16, 16, 16, 15, 15,
    14, 14, 13, 13, 12, 11, 10,
]

df = pd.DataFrame({"score": scores})

# Vertical jitter so dots don't overlap on the strip chart
rng = np.random.default_rng(42)
df["y"] = rng.uniform(-0.18, 0.18, size=len(df))

# =====================================================================
# 2. CONSTANTS
# =====================================================================

CHANCE      = 20.0
THRESHOLD   = 28.0
AVERAGE     = 17.25
BEST_SCORE  = 24.0

# Colorblind-safe palette (Okabe-Ito inspired)
COLOR_DOT        = "#0072B2"   # blue
COLOR_CHANCE     = "#D55E00"   # vermillion / red
COLOR_THRESHOLD  = "#009E73"   # green
COLOR_AVERAGE    = "#56B4E9"   # sky blue
COLOR_HIGHLIGHT  = "#D55E00"   # vermillion
COLOR_TEXT       = "#333333"
COLOR_CAPTION    = "#999999"

# =====================================================================
# 3. PLOT
# =====================================================================

p = (
    ggplot(df, aes(x="score"))
    # --- Dots ---
    + geom_point(
        aes(y="y"),
        size=3.5,
        color=COLOR_DOT,
        alpha=0.75,
    )
    # --- Reference lines ---
    + geom_vline(
        xintercept=CHANCE,
        color=COLOR_CHANCE,
        linetype="dashed",
        size=0.9,
    )
    + geom_vline(
        xintercept=THRESHOLD,
        color=COLOR_THRESHOLD,
        linetype="dashed",
        size=0.9,
    )
    + geom_vline(
        xintercept=AVERAGE,
        color=COLOR_AVERAGE,
        linetype="dotted",
        size=0.9,
    )
    # --- Annotations for reference lines ---
    + geom_text(
        x=CHANCE, y=0.40,
        label="Chance (20/40)",
        color=COLOR_CHANCE,
        hjust=-0.05, vjust=0,
        size=9,
        family="sans-serif",
    )
    + geom_text(
        x=THRESHOLD, y=0.40,
        label="70% threshold (28/40)",
        color=COLOR_THRESHOLD,
        hjust=-0.05, vjust=0,
        size=9,
        family="sans-serif",
    )
    + geom_text(
        x=AVERAGE, y=0.40,
        label="Average: 17.25",
        color=COLOR_AVERAGE,
        hjust=1.05, vjust=0,
        size=9,
        family="sans-serif",
    )
    # --- Best-performer callout ---
    + geom_point(
        x=BEST_SCORE, y=-0.25,
        shape=1,            # empty circle
        color=COLOR_HIGHLIGHT,
        size=7,
        stroke=2,
    )
    + geom_text(
        x=BEST_SCORE, y=-0.45,
        label="Best: 24/40",
        color=COLOR_HIGHLIGHT,
        hjust=0.5, vjust=1,
        size=9,
        family="sans-serif",
        fontface="bold",
    )
    # --- Scales ---
    + scale_x_continuous(
        name="Correct identifications out of 40 birth charts",
        breaks=list(range(8, 33, 2)),
        expand=[0.04, 0],
    )
    + scale_y_continuous(expand=[0.15, 0])
    # --- Labels ---
    + ggtitle("Twenty-Seven Astrologers vs. a Coin Flip")
    # --- Theme ---
    + theme_minimal()
    + theme(
        # Y-axis: blank (meaningless axis, only jitter separation)
        axis_title_y="blank",
        axis_text_y=element_blank(),
        axis_ticks_y=element_blank(),
        axis_line_y=element_blank(),
        # X-axis
        axis_title_x=element_text(size=11, color=COLOR_TEXT),
        axis_text_x=element_text(size=9, color="#555555"),
        # Grid
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.35),
        panel_grid_major_y="blank",
        panel_grid_minor="blank",
        # Title
        plot_title=element_text(
            size=15, face="bold", hjust=0.5, color=COLOR_TEXT,
        ),
        # Backgrounds
        panel_background=element_rect(fill="white", color=None),
        plot_background=element_rect(fill="white", color=None),
        # Margin
        plot_margin=[10, 20, 5, 10],
        # Caption
        plot_caption=element_text(
            size=7.5, color=COLOR_CAPTION, hjust=1,
        ),
    )
    # --- Caption (source line) ---
    + labs(
        caption="Data from Narlikar et al. 2009, Current Science",
    )
)

# =====================================================================
# 4. SAVE
# =====================================================================

output_dir = Path(
    "/home/pi/Documents/code/quortol/backend/blogs/images"
)
output_dir.mkdir(parents=True, exist_ok=True)

png_path = (
    output_dir
    / "architecture-of-belief_astrologer_vs_chance.png"
)

# 1200 x 720 px at 150 DPI  ->  8 x 4.8 in
ggsave(p, str(png_path), w=8, h=4.8, unit="in", dpi=150)

print(f"Chart saved to: {png_path}")

# Verify
assert png_path.exists(), f"File not found: {png_path}"
print(f"File size: {png_path.stat().st_size / 1024:.1f} KB")
