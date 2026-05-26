#!/usr/bin/env python3
"""
IPL Squad Structure — Horizontal Stacked Bar Chart
===================================================
Shows how a 25-player IPL squad maps to match-day participation:
11 starters (Playing XI), 1 Impact Player, and 13 on the bench.

Uses lets-plot with a colourblind-safe palette.
Output: 1200 × 720 px PNG at 150 DPI

Requirements:
    pip install lets-plot pandas
"""

import pandas as pd
from pathlib import Path
from lets_plot import *  # noqa: F401, F403 — includes margin but we use list syntax

LetsPlot.setup_html()

# ============================================================
# PATHS
# ============================================================
OUTPUT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "ipl_squad_structure_bars.png"

# 1200 × 720 px @ 150 DPI  →  w = 1200 / 150 = 8 in,  h = 720 / 150 = 4.8 in
W, H, DPI = 8, 4.8, 150

# ============================================================
# DATA
# ============================================================
# Bar segments (order determines left-to-right stack order)
bar_data = pd.DataFrame({
    "group": ["Squad"] * 3,
    "segment": pd.Categorical(
        ["Playing XI", "Impact Player", "Bench (Reserves)"],
        categories=["Playing XI", "Impact Player", "Bench (Reserves)"],
        ordered=True,
    ),
    "count": [11, 1, 13],
})

# Text labels — positioned at the centre of each stacked segment
label_data = pd.DataFrame({
    "segment": ["Playing XI", "Impact Player", "Bench (Reserves)"],
    "group": ["Squad"] * 3,
    "x_centre": [5.5, 11.5, 18.5],   # cumulative segment centres
    "label": ["11 (44%)", "1 (4%)", "13 (52%)"],
    "text_color": ["#FFFFFF", "#FFFFFF", "#222222"],  # white on dark, near-black on gray
})

# ============================================================
# COLOURBLIND-SAFE PALETTE  (Okabe-Ito inspired)
# ============================================================
# Playing XI    → deep blue    (distinct from green/red)
# Impact Player → warm amber   (pops against blue/gray)
# Bench         → neutral gray (recedes visually)
COLORS = {
    "Playing XI": "#0072B2",
    "Impact Player": "#E69F00",
    "Bench (Reserves)": "#B0B0B0",
}

# ============================================================
# BUILD PLOT
# ============================================================
p = (
    ggplot()
    # ---- horizontal stacked bar ----
    + geom_bar(
        aes(x="count", y="group", fill="segment"),
        data=bar_data,
        stat="identity",
        width=0.35,            # bar thickness relative to category spacing
    )
    # ---- segment labels (three calls for per-label colour control) ----
    + geom_text(
        aes(x="x_centre", y="group", label="label"),
        data=label_data.query("segment == 'Playing XI'"),
        color="#FFFFFF", size=12, fontweight="bold",
    )
    + geom_text(
        aes(x="x_centre", y="group", label="label"),
        data=label_data.query("segment == 'Impact Player'"),
        color="#FFFFFF", size=9.5, fontweight="bold",
    )
    + geom_text(
        aes(x="x_centre", y="group", label="label"),
        data=label_data.query("segment == 'Bench (Reserves)'"),
        color="#333333", size=12, fontweight="bold",
    )
    # ---- fill / axis scales ----
    + scale_fill_manual(values=COLORS, name="Squad Role")
    + scale_x_continuous(
        limits=[0, 26.5],
        breaks=list(range(0, 26, 5)),
    )
    # ---- labels ----
    + labs(
        title="The IPL Bench: 25 Players, 11 Spots",
        subtitle="How a 25-player squad maps to match-day participation",
        x="Number of players",
        y="",
        caption=(
            "Over a 14-match season, 7\u20139 players typically see zero or near-zero game time per team.\n"
            "Sources: IPL Governing Council Regulations 2025\u201327, Sporting News, CricTracker"
        ),
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
        # caption / annotation + source
        plot_caption=element_text(
            size=7.5, color="#888888", hjust=0.5,
            margin=[16, 0, 0, 0],
        ),
        # axes
        axis_title_x=element_text(size=9.5, color="#555555"),
        axis_text_x=element_text(size=9, color="#666666"),
        axis_text_y=element_blank(),
        axis_title_y=element_blank(),
        axis_line_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_y=element_blank(),
        # grid
        panel_grid_major_x=element_line(color="#EEEEEE", size=0.25),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        # legend
        legend_position="bottom",
        legend_direction="horizontal",
        legend_text=element_text(size=9, color="#555555"),
        legend_spacing=8,
        # outer margin
        plot_margin=[18, 25, 12, 25],
    )
)

# ============================================================
# SAVE AS PNG  (1200 × 720 px @ 150 DPI)
# ============================================================
ggsave(p, str(OUTPUT_FILE), w=W, h=H, unit="in", dpi=DPI)
print(f"\u2713  Chart saved  \u2192  {OUTPUT_FILE}")
print(f"    Dimensions   \u2192  {int(W * DPI)} \u00d7 {int(H * DPI)} px @ {DPI} DPI")
