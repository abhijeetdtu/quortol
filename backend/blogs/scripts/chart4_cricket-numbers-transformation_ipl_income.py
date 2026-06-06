#!/usr/bin/env python3
"""
IPL Income Growth, 2013–2025
=============================
Vertical bar chart with connected trend line overlay showing IPL total income
from 2013–14 to 2024–25 (₹ Crore), with annotations for key milestones.

Source: FACTLY analysis of BCCI annual reports
https://factly.in/broadcast-deals-dominate-ipl-finances-as-income-crosses-%E2%82%B912000-crore/
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# =====================================================================
# PATHS
# =====================================================================
OUTPUT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "cricket-numbers-transformation_ipl_income.png"

# 1200 × 720 px @ 150 DPI  →  w = 1200 / 150 = 8 in,  h = 720 / 150 = 4.8 in
W, H, DPI = 8, 4.8, 150

# =====================================================================
# DATA
# =====================================================================
df = pd.DataFrame({
    "season": [
        "2013-14", "2014-15", "2015-16", "2016-17", "2017-18",
        "2018-19", "2019-20", "2020-21", "2021-22", "2022-23",
        "2023-24", "2024-25",
    ],
    "income": [1195, 1400, 1600, 1900, 2200, 3800, 4200, 4000, 4800, 5600, 9200, 12005],
})

# Mark seasons that coincide with new media rights cycles
df["media_rights"] = df["season"].isin(["2018-19", "2023-24"])

# =====================================================================
# COLORBLIND-SAFE PALETTE
# =====================================================================
# Purple bars (Okabe-Ito inspired: #882E72 is a robust purple for CB-safe)
# Dark blue line (strong contrast against purple)
BAR_COLOR = "#882E72"
LINE_COLOR = "#1F4E79"

# =====================================================================
# ANNOTATION DATA FRAMES
# =====================================================================

# Bar-top label for the final season
top_bar_label = pd.DataFrame({
    "season": ["2024-25"],
    "income": [12400],
    "label": ["₹12,005 cr"],
})

# "10x growth" callout at the top of the chart
tenx_label = pd.DataFrame({
    "season": ["2024-25"],
    "income": [13400],
    "label": ["10x growth"],
})

# "New media rights cycle" labels for the two affected seasons
media_label_df = pd.DataFrame({
    "season": ["2018-19", "2023-24"],
    "income": [4300, 9850],
    "label": ["New media\nrights cycle", "New media\nrights cycle"],
})

# =====================================================================
# BUILD PLOT
# =====================================================================
p = (
    ggplot(df, aes(x="season", y="income"))
    # ---- Vertical bars ----
    + geom_bar(stat="identity", fill=BAR_COLOR, width=0.68)
    # ---- Trend line (group=1 connects points across categorical x) ----
    + geom_line(aes(group=1), color=LINE_COLOR, size=1.1)
    + geom_point(color=LINE_COLOR, size=3.2)
    # ---- Annotation: bar-top value label ----
    + geom_text(
        aes(label="label"),
        data=top_bar_label,
        size=9,
        color="#333333",
        fontweight="bold",
    )
    # ---- Annotation: "10x growth" ----
    + geom_text(
        aes(label="label"),
        data=tenx_label,
        size=12,
        color=LINE_COLOR,
        fontweight="bold",
    )
    # ---- Annotation: media rights cycle markers ----
    + geom_text(
        aes(label="label"),
        data=media_label_df,
        size=7.2,
        color=BAR_COLOR,
        fontweight="bold",
        lineheight=0.9,
    )
    # ---- Scales ----
    + scale_y_continuous(
        name="Income (₹ Crore)",
        limits=[0, 14000],
        expand=[0, 0],
        breaks=[0, 2000, 4000, 6000, 8000, 10000, 12000, 14000],
    )
    + scale_x_discrete(name="Season")
    # ---- Titles & caption ----
    + labs(
        title="IPL Income Growth, 2013–2025",
        subtitle="From ₹1,195 crore to ₹12,005 crore — tenfold growth in 11 years",
        caption="Source: FACTLY / BCCI annual reports",
    )
    # ---- Minimal theme with custom overrides ----
    + theme_minimal()
    + theme(
        # White canvas
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
        # Title / subtitle
        plot_title=element_text(
            size=17, hjust=0.5, face="bold", margin=[0, 0, 2, 0],
        ),
        plot_subtitle=element_text(
            size=10, hjust=0.5, color="#666666", margin=[2, 0, 22, 0],
        ),
        # Caption (source line)
        plot_caption=element_text(
            size=7.5, color="#888888", hjust=0.5, margin=[16, 0, 0, 0],
        ),
        # Axis titles
        axis_title_x=element_text(size=9.5, color="#555555"),
        axis_title_y=element_text(size=9.5, color="#555555"),
        # Axis text — x labels angled 45° to avoid overlap
        axis_text_x=element_text(size=8.5, color="#555555", angle=45, hjust=1),
        axis_text_y=element_text(size=8.5, color="#555555"),
        # Axis lines
        axis_line_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_x=element_blank(),
        # Grid — only horizontal guide lines
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#EEEEEE", size=0.25),
        panel_grid_minor=element_blank(),
        # Outer margin
        plot_margin=[18, 28, 12, 22],
    )
)

# =====================================================================
# SAVE AS PNG  (1200 × 720 px @ 150 DPI)
# =====================================================================
ggsave(p, str(OUTPUT_FILE), w=W, h=H, unit="in", dpi=DPI)
print(f"\u2713  Chart saved  \u2192  {OUTPUT_FILE}")
print(f"    Dimensions   \u2192  {int(W * DPI)} \u00d7 {int(H * DPI)} px @ {DPI} DPI")
