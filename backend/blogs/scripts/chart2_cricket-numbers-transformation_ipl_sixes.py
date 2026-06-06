#!/usr/bin/env python3
"""
The IPL Six-Hitting Revolution — Vertical Bar Chart
====================================================
Shows average sixes per match from 2008 to 2025.

Uses lets-plot with a colourblind-safe amber/orange gradient fill.
Output: 1200 × 720 px PNG at 150 DPI

Data source: CricMind.ai IPL six-hitting database
(42,847 sixes across 1,169 matches)
https://www.cricmind.ai/news/ipl-six-hitting-revolution-2008-to-2025-statistics

Requirements:
    pip install lets-plot pandas
"""

import pandas as pd
from pathlib import Path
from lets_plot import *  # noqa: F401, F403

LetsPlot.setup_html()

# ============================================================
# PATHS
# ============================================================
OUTPUT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "cricket-numbers-transformation_ipl_sixes.png"
SCRIPT_FILE = SCRIPT_DIR / "chart2_cricket-numbers-transformation_ipl_sixes.py"

# 1200 × 720 px @ 150 DPI  →  w = 1200 / 150 = 8 in,  h = 720 / 150 = 4.8 in
W, H, DPI = 8, 4.8, 150

# ============================================================
# DATA  (from CricMind.ai)
# ============================================================
data = pd.DataFrame({
    "season": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015,
               2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023,
               2024, 2025],
    "sixes_per_match": [3.1, 4.2, 5.2, 6.2, 6.4, 8.1, 8.0, 8.3,
                        8.9, 9.2, 9.5, 10.4, 9.7, 10.3, 10.9, 11.9,
                        13.3, 14.3],
})

# ============================================================
# COLOURBLIND-SAFE GRADIENT  (light amber → deep orange)
# ============================================================
MIN_COLOR = "#FDE0B2"   # very light amber
MAX_COLOR = "#E65100"   # deep orange

# ============================================================
# BUILD PLOT
# ============================================================
p = (
    ggplot(data, aes(x="season", y="sixes_per_match", fill="sixes_per_match"))
    # ---- bars with white stroke for clean separation ----
    + geom_bar(stat="identity", width=0.75, color="#FFFFFF", size=0.35)
    # ---- gradient fill (continuous, no legend needed) ----
    + scale_fill_gradient(low=MIN_COLOR, high=MAX_COLOR, guide=None)
    # ---- scales ----
    + scale_x_continuous(
        breaks=list(range(2008, 2026)),
        labels=[str(y) for y in range(2008, 2026)],
    )
    + scale_y_continuous(limits=[0, 16], breaks=list(range(0, 17, 2)))
    # ---- annotation arrow pointing to the 2025 bar ----
    + geom_segment(
        x=2025.4, y=14.8,
        xend=2025.0, yend=14.3,
        arrow=arrow(length=0.15, type="closed"),
        color="#222222", size=0.5,
    )
    + geom_text(
        x=2025.5, y=14.8,
        label="14.3 sixes/match",
        hjust=0, size=8.5, color="#222222",
        fontweight="bold",
    )
    # ---- "361% increase" near top right ----
    + geom_text(
        x=2024, y=15.5,
        label="361% increase",
        hjust=1, size=8, color="#C62828",
        fontweight="bold",
    )
    # ---- labels ----
    + labs(
        title="The IPL Six-Hitting Revolution, 2008\u20132025",
        subtitle=(
            "Average sixes per match \u2014 "
            "from 3.1 to 14.3, a 361% increase"
        ),
        x="Season",
        y="Sixes per Match",
        caption="Source: CricMind.ai",
    )
    # ---- clean minimal theme ----
    + theme_minimal()
    + theme(
        # white canvas
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
        # title
        plot_title=element_text(
            size=18, hjust=0.5, face="bold",
            margin=[0, 0, 2, 0],
        ),
        plot_subtitle=element_text(
            size=10.5, hjust=0.5, color="#666666",
            margin=[2, 0, 22, 0],
        ),
        # caption / source line
        plot_caption=element_text(
            size=8, color="#888888", hjust=0.5,
            margin=[16, 0, 0, 0],
        ),
        # axes
        axis_title_x=element_text(size=10, color="#555555"),
        axis_text_x=element_text(
            size=8, color="#666666",
            angle=45, hjust=1, vjust=1,
        ),
        axis_title_y=element_text(size=10, color="#555555"),
        axis_text_y=element_text(size=8.5, color="#666666"),
        # grid — keep horizontal for readability, remove vertical
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#EEEEEE", size=0.25),
        panel_grid_minor=element_blank(),
        axis_line_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_y=element_line(color="#CCCCCC", size=0.35),
        # no legend — gradient is self-explanatory
        legend_position="none",
        # outer margin
        plot_margin=[18, 25, 12, 25],
    )
)

# ============================================================
# SAVE AS PNG  (1200 × 720 px @ 150 DPI)
# ============================================================
ggsave(p, str(OUTPUT_FILE), w=W, h=H, unit="in", dpi=DPI)
print(f"✓  Chart saved  →  {OUTPUT_FILE}")
print(f"    Dimensions   →  {int(W * DPI)} × {int(H * DPI)} px @ {DPI} DPI")
