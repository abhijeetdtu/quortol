#!/usr/bin/env python3
"""
Horizontal bar chart: America's six largest cities — population and density.
U.S. Census Bureau Vintage 2025 population estimates.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ─────────────────────────────────────────────────────────────────────
data = {
    "city": [
        "New York City",
        "Los Angeles",
        "Chicago",
        "Houston",
        "Phoenix",
        "Philadelphia",
    ],
    "population": [8_584_629, 3_869_089, 2_731_585, 2_397_315, 1_665_481, 1_574_281],
    "density": [29_303, 8_304, 12_060, 3_598, 3_213, 11_937],
}

df = pd.DataFrame(data)

# Preserve order — NYC first (largest), Philadelphia last
df["city"] = pd.Categorical(df["city"], categories=df["city"], ordered=True)

# Format density annotation text: "29,303/sq mi"
df["density_label"] = df["density"].apply(lambda v: f"{v:,}/sq mi")

# Population in millions for axis labels
df["pop_millions"] = df["population"] / 1_000_000

# ── Build chart ──────────────────────────────────────────────────────────────
# Colorblind-safe medium blue
CB_BLUE = "#4477AA"

# Background / layout
LETS_PLOT_THEME = theme(
    plot_title=element_text(size=20, face="bold", hjust=0),
    plot_subtitle=element_text(size=13, hjust=0, color="#555555"),
    axis_title_x=element_text(size=13, face="bold"),
    axis_text=element_text(size=11),
    axis_text_y=element_text(size=12, face="bold"),
    axis_ticks=element_blank(),
    plot_caption=element_text(size=9, color="#888888", hjust=0),
    panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
    panel_grid_major_y=element_blank(),
    panel_grid_minor=element_blank(),
    panel_background=element_rect(fill="#FAFAFA"),
    plot_background=element_rect(fill="white"),
    plot_margin=[20, 30, 10, 20],
)

p = (
    ggplot(df, aes(x="pop_millions", y="city"))
    + geom_bar(stat="identity", fill=CB_BLUE, width=0.65)
    # Density annotation at the end of each bar
    + geom_text(
        aes(label="density_label"),
        hjust=-0.05,  # slight offset to the right
        size=10,
        color="#333333",
        va="center",
    )
    + scale_x_continuous(
        limits=[0, 10.5],  # a bit past NYC's 8.58M for text space
        breaks=[0, 2, 4, 6, 8, 10],
        labels=["0", "2M", "4M", "6M", "8M", "10M"],
        expand=[0, 0],
    )
    + scale_y_discrete()  # preserve city order
    + labs(
        title="America's Six Largest Cities: Population and Density",
        subtitle="2025 Census Bureau estimates",
        x="Population",
        y="",
        caption="Source: U.S. Census Bureau, Vintage 2025 Population Estimates",
    )
    + LETS_PLOT_THEME
)

# ── Save ─────────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

png_path = output_dir / "nyc-contradiction-city_population_density.png"

ggsave(p, str(png_path), w=1200, h=720, unit="px", dpi=150)

print(f"Chart saved to {png_path.resolve()}")
