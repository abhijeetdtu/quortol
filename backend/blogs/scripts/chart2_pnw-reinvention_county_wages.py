#!/usr/bin/env python3
"""
Chart: The Rural Wage Gap — Average Weekly Wages in Washington Counties, Q1 2025

Horizontal bar chart using lets-plot.
Highlights King County (metro giant) and Wahkiakum (lowest rural county).
Includes a vertical dashed line for the national average.
Colorblind-safe blue-orange palette.

Source: Bureau of Labor Statistics, QCEW Q1 2025
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
data = {
    "county": [
        "Wahkiakum",
        "Ferry",
        "Grays Harbor",
        "Whatcom",
        "Cowlitz",
        "Kitsap",
        "Snohomish",
        "King (Seattle area)",
    ],
    "wage": [903, 1088, 1118, 1322, 1324, 1425, 1643, 2675],
}
df = pd.DataFrame(data)

# Sort ascending so lowest wage appears at bottom, highest at top.
# This matches the horizontal-bar convention: strongest bar at top.
df["county"] = pd.Categorical(
    df["county"], categories=df["county"].tolist(), ordered=True
)

# Category for manual colour mapping
def classify(county: str) -> str:
    if county == "King (Seattle area)":
        return "King"
    if county == "Wahkiakum":
        return "Wahkiakum"
    return "Other"

df["fill_group"] = df["county"].apply(classify)

# Pre-formatted dollar labels (no overlap, placed at bar ends)
df["label"] = df["wage"].apply(lambda w: f"${w:,}")

# ---------------------------------------------------------------------------
# Colour palette — colorblind-safe diverging blue / orange
# ---------------------------------------------------------------------------
fill_colors = {
    "King": "#0077BB",      # saturated blue
    "Wahkiakum": "#EE7733",  # vibrant orange
    "Other": "#BBBBBB",      # neutral gray
}

# ---------------------------------------------------------------------------
# Build the chart
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(y="county", x="wage", fill="fill_group"))
    + geom_bar(stat="identity", width=0.65, color="#FFFFFF", size=0.3)
    # National-average reference line
    + geom_vline(
        xintercept=1589,
        linetype="dashed",
        color="#555555",
        size=0.9,
    )
    # Dollar label at the end of each bar
    + geom_text(
        aes(label="label"),
        hjust=-0.1,
        size=10.5,
        color="#333333",
        family="sans-serif",
    )
    # "National Avg." label above the top bar (separate data geom)
    + geom_text(
        data=pd.DataFrame({
            "x": [1589],
            "y": [8.5],
            "lab": ["National Avg. $1,589"],
        }),
        mapping=aes(x="x", y="y", label="lab"),
        color="#555555",
        size=9,
        hjust=0.5,
        family="sans-serif",
    )
    + scale_fill_manual(values=fill_colors)
    + scale_x_continuous(
        limits=[0, 3100],
        expand=[0, 0],
        breaks=[0, 500, 1000, 1500, 2000, 2500, 3000],
    )
    + labs(
        title="The Rural Wage Gap: Average Weekly Wages in Washington Counties, Q1 2025",
        x="Average Weekly Wage ($)",
        y="",
        caption="Source: Bureau of Labor Statistics, QCEW Q1 2025",
    )
    + theme_minimal()
    + theme(
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
        text=element_text(color="#333333", family="sans-serif"),
        axis_text_y=element_text(size=12, color="#333333"),
        axis_text_x=element_text(size=10, color="#555555"),
        axis_title_x=element_text(size=11, color="#333333"),
        plot_title=element_text(size=16, face="bold", color="#222222"),
        plot_caption=element_text(
            size=8.5, hjust=0, color="#888888", margin=12
        ),
        legend_position="none",
        panel_grid_major_x=element_line(color="#EEEEEE", size=0.5),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        axis_ticks_y=element_blank(),
        axis_ticks_x=element_blank(),
        axis_line_x=element_line(color="#DDDDDD", size=0.4),
    )
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
out_dir.mkdir(parents=True, exist_ok=True)

png_path = out_dir / "pnw-reinvention_county_wages.png"
ggsave(p, str(png_path), w=8, h=4.8, unit="in", dpi=150)

print(f"✓ Saved PNG  → {png_path}")
print(f"  Dimensions  → 1200 × 720 px @ 150 DPI")
