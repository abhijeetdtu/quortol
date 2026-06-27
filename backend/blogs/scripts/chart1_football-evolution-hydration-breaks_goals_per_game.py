#!/usr/bin/env python3
"""
Chart: World Cup Goals Per Game, 1930–2022
Output: ../images/football-evolution-hydration-breaks_goals_per_game.png
        (1200 × 720 px, 150 DPI)

Line chart showing average goals per match at each FIFA World Cup
from 1930 to 2022, with annotations for key rule changes, a reference
line at the all-time average (2.82), and a highlighted record low (1990).
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA
# ============================================================================

df = pd.DataFrame({
    "year": [
        1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974,
        1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014,
        2018, 2022,
    ],
    "goals_per_game": [
        3.89, 4.12, 4.67, 4.00, 5.38, 3.60, 2.78, 2.78, 2.97, 2.55,
        2.68, 2.81, 2.54, 2.21, 2.71, 2.67, 2.52, 2.30, 2.27, 2.67,
        2.64, 2.69,
    ],
})

ALL_TIME_AVG = 2.82
CB_BLUE = "#4472C4"      # colorblind-safe blue for the line
ANNOT_GRAY = "#777777"    # gray for annotation elements
HIGHLIGHT_RED = "#BB4444"  # muted red for the record-low label

# ============================================================================
# 2. ANNOTATION DATA FRAMES
# ============================================================================

# Vertical dashed lines for rule changes
rule_vlines = pd.DataFrame({
    "x": [1992, 2014, 2020],
    "label": [
        "Back-pass rule\nintroduced",
        "Goal-line technology\nintroduced",
        "5 substitutes\n(COVID)",
    ],
})

# 1925 rule change — appears left of the data series (top-left corner)
pre_series_note = pd.DataFrame({
    "x": [1925],
    "y": [5.7],
    "label": ["Offside rule changed\n(3→2 defenders)"],
})

# Record-low label near the 1990 data point (2.21)
record_low_label = pd.DataFrame({
    "x": [1991.5],
    "y": [2.50],
    "label": ["Record low\n2.21"],
    "hjust": [0.0],
})

# ============================================================================
# 3. BUILD THE PLOT
# ============================================================================

p = (
    ggplot(df, aes(x="year", y="goals_per_game"))

    # ---- Reference line: all-time average ----
    + geom_hline(
        yintercept=ALL_TIME_AVG,
        color=ANNOT_GRAY,
        linetype="dashed",
        size=0.7,
    )
    + geom_text(
        data=pd.DataFrame({
            "x": [2026],
            "y": [ALL_TIME_AVG + 0.08],
            "label": [f"All-time average ({ALL_TIME_AVG})"],
        }),
        mapping=aes(x="x", y="y", label="label"),
        color=ANNOT_GRAY,
        size=8.5,
        hjust=1,
        family="sans",
    )

    # ---- Rule-change vertical lines (behind data) ----
    + geom_vline(
        data=rule_vlines,
        mapping=aes(xintercept="x"),
        color=ANNOT_GRAY,
        linetype="dashed",
        size=0.7,
    )

    # ---- Rule-change labels (near top of chart) ----
    + geom_text(
        data=rule_vlines,
        mapping=aes(x="x", label="label"),
        y=5.8,
        size=7.5,
        color=ANNOT_GRAY,
        family="sans",
        hjust=0.5,
        vjust=0,
        lineheight=0.9,
    )

    # ---- Pre-series note (1925, top left) ----
    + geom_text(
        data=pre_series_note,
        mapping=aes(x="x", y="y", label="label"),
        size=8,
        color=ANNOT_GRAY,
        family="sans",
        hjust=0,
        vjust=1,
        lineheight=0.9,
    )

    # ---- Record-low annotation (near 1990) ----
    + geom_text(
        data=record_low_label,
        mapping=aes(x="x", y="y", label="label"),
        size=8.5,
        color=HIGHLIGHT_RED,
        family="sans",
        hjust=0,
        vjust=0.5,
        lineheight=0.9,
    )

    # ---- Main line and points ----
    + geom_line(color=CB_BLUE, size=1.8)
    + geom_point(color=CB_BLUE, size=4.5)

    # ---- Axes ----
    + scale_x_continuous(
        breaks=list(range(1930, 2023, 4)),
        limits=(1918, 2030),
        expand=[0, 0],
    )
    + scale_y_continuous(
        limits=(1.5, 6.0),
        breaks=[1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0],
        expand=[0, 0],
    )

    # ---- Labels ----
    + labs(
        title="World Cup Goals Per Game, 1930–2022",
        subtitle=(
            "The 1990 nadir triggered the back-pass rule; "
            "the modern game has stabilized near 2.7"
        ),
        x="",
        y="Goals per match",
        caption=(
            "Source: FIFA / Statista\n"
            "The 1990 World Cup in Italy produced 2.21 goals per match — "
            "the lowest in history. The back-pass rule (1992) and "
            "three-points-for-a-win (1994) helped restore attacking play."
        ),
    )

    # ---- Theme ----
    + theme_minimal()
    + theme(
        axis_text_x=element_text(angle=45, hjust=1, size=10, color="#555555"),
        axis_text_y=element_text(size=10, color="#555555"),
        axis_title_y=element_text(
            size=12, color="#333333", margin=[0, 8, 0, 0]
        ),

        plot_title=element_text(
            size=18, face="bold", color="#1a1a1a", margin=[0, 0, 4, 0]
        ),
        plot_subtitle=element_text(
            size=13, color="#666666", margin=[0, 0, 16, 0]
        ),
        plot_caption=element_text(
            size=8, color="#999999", margin=[12, 0, 0, 0]
        ),

        panel_grid_major_x=element_blank(),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_line(color="#e6e6e6", size=0.35),
        panel_grid_minor_y=element_blank(),

        panel_background=element_blank(),
        plot_background=element_blank(),

        plot_margin=[15, 25, 10, 15],
    )
)

# ============================================================================
# 4. SAVE PNG  — 1200 × 720 px @ 150 DPI  →  8 × 4.8 in
# ============================================================================
output_path = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "football-evolution-hydration-breaks_goals_per_game.png"
)
ggsave(p, output_path, w=8, h=4.8, unit="in", dpi=150)

print(f"✓ Chart saved to {output_path}")
print(f"  Dimensions: 1200 × 720 px  @  150 DPI")
