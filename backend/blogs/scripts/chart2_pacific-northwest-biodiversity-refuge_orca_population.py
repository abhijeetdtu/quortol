#!/usr/bin/env python3
"""
Chart: Southern Resident Killer Whale annual population census (1974-2025)
Line chart with filled area under curve, annotated with peak reference,
ESA listing marker, and key data labels.

Sources:
  - NOAA Fisheries 2024 Stock Assessment
  - Center for Whale Research
  - Puget Sound Partnership
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# =====================================================================
# 1. DATA
# =====================================================================

data = [
    (1974, 71), (1975, 71), (1976, 68), (1977, 70), (1978, 72), (1979, 73),
    (1980, 76), (1981, 78), (1982, 77), (1983, 76), (1984, 77), (1985, 79),
    (1986, 80), (1987, 82), (1988, 84), (1989, 85), (1990, 87), (1991, 89),
    (1992, 92), (1993, 96), (1994, 97), (1995, 99), (1996, 97), (1997, 95),
    (1998, 92), (1999, 89), (2000, 88), (2001, 79), (2002, 80), (2003, 82),
    (2004, 83), (2005, 84), (2006, 89), (2007, 87), (2008, 85), (2009, 83),
    (2010, 86), (2011, 87), (2012, 84), (2013, 82), (2014, 79), (2015, 81),
    (2016, 80), (2017, 76), (2018, 75), (2019, 73), (2020, 72), (2021, 74),
    (2022, 73), (2023, 75), (2024, 73), (2025, 74),
]

df = pd.DataFrame(data, columns=["year", "population"])

# Data labels for three key years
label_df = df[df["year"].isin([1995, 2001, 2024])].copy()

# Annotation data frames for standalone text
peak_label_df = pd.DataFrame({
    "x": [1974.5],
    "y": [101.0],
    "label": ["Peak: 99 (1995)"],
})

esa_label_df = pd.DataFrame({
    "x": [2005.0],
    "y": [62.0],
    "label": ["ESA Listing\n(2005)"],
})

# =====================================================================
# 2. BUILD CHART
# =====================================================================

# Dimensions: 1200 × 720 px @ 150 DPI → 8 × 4.8 in

p = (
    ggplot(df, aes(x="year", y="population"))
    # Area fill under the curve — light blue
    + geom_area(fill="#B3D9E8", alpha=0.60)
    # Line on top — deep teal (colorblind-safe)
    + geom_line(color="#1A6B8A", size=1.3)
    # Points on line
    + geom_point(color="#1A6B8A", size=2.2)
    # Horizontal dashed reference line at 1995 peak (99)
    + geom_hline(yintercept=99, linetype="dashed", color="#CC6677", size=0.7)
    + geom_text(
        aes(x="x", y="y", label="label"),
        data=peak_label_df,
        hjust=0, vjust=0,
        size=9.5,
        color="#CC6677",
        fontface="italic",
    )
    # Vertical dashed line for ESA listing year (2005)
    + geom_vline(xintercept=2005, linetype="dashed", color="#777777", size=0.6)
    + geom_text(
        aes(x="x", y="y", label="label"),
        data=esa_label_df,
        hjust=0.5, vjust=1,
        size=8.5,
        color="#555555",
        fontface="italic",
    )
    # Data labels for peak (1995), post-decline low (2001), recent (2024)
    + geom_text(
        aes(label="population"),
        data=label_df,
        nudge_y=3.5,
        size=10.5,
        color="#1A6B8A",
        fontface="bold",
    )
    # Scales
    + scale_x_continuous(
        name=None,
        breaks=list(range(1975, 2026, 5)),
        limits=[1973, 2026],
        expand=[0.005, 0.005],
    )
    + scale_y_continuous(
        name="Population Size (individuals)",
        limits=[58, 106],
        breaks=list(range(60, 106, 5)),
        expand=[0, 0],
    )
    # Labels
    + labs(
        title="Southern Resident Killer Whales: A Population in Decline",
        subtitle="From 99 in 1995 to 73 in 2024 \u2014 a 26% decline in three decades",
        caption="Sources: NOAA Fisheries Stock Assessment (2024), Center for Whale Research, Puget Sound Partnership",
    )
    # Theme — clean, magazine-style
    + theme_minimal()
    + theme(
        # Title / subtitle / caption
        plot_title=element_text(
            size=18, face="bold", hjust=0, color="#111111",
            margin=[0, 0, 5, 0],
        ),
        plot_subtitle=element_text(
            size=11, color="#555555", hjust=0,
            margin=[0, 0, 15, 0],
        ),
        plot_caption=element_text(
            size=7.5, color="#999999", hjust=0,
            margin=[8, 0, 0, 0],
        ),
        # Grid
        panel_grid_minor="blank",
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.35),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.35),
        # Axes
        axis_title_y=element_text(size=12, color="#333333"),
        axis_text_x=element_text(size=10, color="#555555"),
        axis_text_y=element_text(size=10, color="#555555"),
        axis_ticks=element_line(color="#CCCCCC", size=0.3),
        axis_ticks_length=5,
        # Background — white
        panel_background=element_rect(fill="white", color=None),
        plot_background=element_rect(fill="white", color=None),
        # Margin: top, right, bottom, left
        plot_margin=[15, 25, 10, 15],
        # Hide legend (all annotations are directly labelled)
        legend_position="none",
    )
)

# =====================================================================
# 3. SAVE
# =====================================================================

image_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
image_dir.mkdir(parents=True, exist_ok=True)

script_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
script_dir.mkdir(parents=True, exist_ok=True)

png_path = image_dir / "pacific-northwest-biodiversity-refuge_orca_population.png"
script_path = script_dir / "chart2_pacific-northwest-biodiversity-refuge_orca_population.py"

ggsave(p, str(png_path), w=8, h=4.8, unit="in", dpi=150)

print(f"Chart saved to: {png_path}")
print(f"Script:        {script_path}")
