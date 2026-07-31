#!/usr/bin/env python3
"""
Horizontal bar chart: British Colonial Railway Expansion in India, 1853–1947
Uses lets-plot for headless rendering.

Output: 1200×720 px at 150 DPI
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
# Ordered from earliest to latest; oldest displayed at top via factor reorder.
decades = [
    "1853–1860",
    "1860–1870",
    "1870–1880",
    "1880–1890",
    "1890–1900",
    "1900–1910",
    "1910–1920",
    "1920–1930",
    "1930–1940",
    "1940–1947",
]

cumulative_km = [
    32,
    4320,
    9900,
    17400,
    24300,
    32100,
    40200,
    46800,
    53200,
    55700,
]

# Build DataFrame
df = pd.DataFrame({
    "Decade": pd.Categorical(decades, categories=decades, ordered=True),
    "Cumulative Route km": cumulative_km,
})

# ── Colorblind-safe steel blue ───────────────────────────────────────────────
STEEL_BLUE = "#4682B4"

# ── Plot ──────────────────────────────────────────────────────────────────────
p = (
    ggplot(df, aes(x="Decade", y="Cumulative Route km"))
    + geom_bar(stat="identity", fill=STEEL_BLUE, width=0.7)
    + coord_flip()
    # Reverse factor order so oldest decade appears at top after coord_flip
    + scale_x_discrete(limits=decades[::-1])
    + scale_y_continuous(
        labels=lambda vals: [f"{int(v):,}" for v in vals],
        expand=(0, 0, 0.05, 0),
    )
    + labs(
        title="Colonial Railway Expansion: Route Kilometers (km) by Decade",
        subtitle="Cumulative railway track length across British India",
        x=None,
        y="Cumulative Route (km)",
        caption="Source: Indian Railways Historical Data; Fenske & Kala, Journal of Development Economics, 2023",
    )
    + theme(
        axis_text_y=element_text(size=11, color="#333333"),
        axis_text_x=element_text(size=10, color="#555555"),
        axis_title_x=element_text(size=12, color="#333333"),
        plot_title=element_text(size=15, face="bold", color="#222222"),
        plot_subtitle=element_text(size=11, color="#555555"),
        plot_caption=element_text(size=8, color="#777777", hjust=0),
        panel_background=element_rect(fill="white", color=None),
        panel_grid_major_x=element_line(color="#e0e0e0", size=0.4),
        panel_grid_major_y=element_blank(),
        axis_line_x=element_line(color="#cccccc", size=0.5),
        axis_line_y=element_line(color="#cccccc", size=0.5),
        plot_margin=0.02,
    )
)

# ── Save ──────────────────────────────────────────────────────────────────────
output_path = "/home/pi/Documents/code/quortol/backend/blogs/images/india-geography-destiny_railway_expansion.png"

ggsave(
    p,
    output_path,
    w=1200,
    h=720,
    dpi=150,
    unit="px",
)

print(f"Chart saved to {output_path}")
