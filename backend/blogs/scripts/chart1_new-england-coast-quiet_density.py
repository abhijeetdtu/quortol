#!/usr/bin/env python3
"""
Chart: Population Density of New England States
Horizontal bar chart of people per square mile for six NE states plus US
average, using a colorblind-safe palette.

Source: U.S. Census Bureau, 2020 Census (QuickFacts)
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# =====================================================================
# 1. DATA
# =====================================================================

df = pd.DataFrame({
    "state": [
        "Rhode Island",
        "Massachusetts",
        "Connecticut",
        "New Hampshire",
        "Vermont",
        "Maine",
        "United States",
    ],
    "density": [1061.4, 901.2, 744.7, 153.9, 69.8, 44.2, 93.8],
})

# Sorting descending so RI (highest) appears at the top of the
# horizontal bar chart.
df = df.sort_values("density", ascending=False).reset_index(drop=True)

# Categorical ordering: top row = first in list = highest density
df["state"] = pd.Categorical(
    df["state"],
    categories=df["state"].tolist(),
    ordered=True,
)

# Format display labels with one decimal place
df["label"] = df["density"].apply(lambda v: f"{v:,.1f}")

# Marker for distinct styling of the US average bar
df["bar_type"] = ["State"] * 6 + ["US Average"]

# =====================================================================
# 2. COLOR PALETTE (Tol "bright" / colorblind-safe, 7 colours)
# =====================================================================
# Paul Tol's "bright" scheme — distinguishable for up to 12 categories
# and designed for colour-vision deficiency accessibility.
# The US average is assigned a contrasting warm grey to stand apart
# from the six state colours.

FILL_COLORS = {
    "Rhode Island":   "#4477AA",   # blue
    "Massachusetts":  "#EE6677",   # red
    "Connecticut":    "#228833",   # green
    "New Hampshire":  "#CCBB44",   # yellow
    "Vermont":        "#66CCEE",   # cyan
    "Maine":          "#AA3377",   # purple
    "United States":  "#BBBBBB",   # warm grey (distinct)
}

# =====================================================================
# 3. BUILD CHART
# =====================================================================

# Dimensions: 1200 × 720 px @ 150 DPI → 8 × 4.8 in
p = (
    ggplot(df, aes(y="state", x="density"))
    + geom_bar(
        aes(fill="state", linetype="bar_type"),
        stat="identity",
        width=0.65,
        color="#555555",
        size=0.5,
    )
    + geom_text(
        aes(label="label"),
        hjust=-0.2,
        size=10.5,
        color="#333333",
    )
    + scale_fill_manual(values=FILL_COLORS)
    # Dashed outline only for the US Average bar; no outline for states
    + scale_linetype_manual(values={"State": "blank", "US Average": "dashed"})
    + scale_x_continuous(
        name="People per square mile",
        expand=[0.05, 0.18],   # extra right padding for data labels
    )
    + scale_y_discrete(name=None)
    + labs(
        title="Population Density of New England States",
        caption="Source: U.S. Census Bureau, 2020 Census",
    )
    + theme_minimal()
    + theme(
        # Grid ---
        panel_grid_minor="blank",
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.35),
        panel_grid_major_y="blank",
        # Axes ---
        axis_title_x=element_text(size=12, color="#333333"),
        axis_text_y=element_text(size=11, color="#333333"),
        axis_text_x=element_text(size=10, color="#555555"),
        # Background ---
        panel_background=element_rect(fill="white", color=None),
        plot_background=element_rect(fill="white", color=None),
        # Title / caption ---
        plot_title=element_text(size=16, face="bold", hjust=0),
        plot_caption=element_text(size=8, color="#999999", hjust=0),
        # Layout ---
        plot_margin=[10, 25, 10, 10],
        # Hide legends (y-axis labels are self-explanatory)
        legend_position="none",
    )
)

# =====================================================================
# 4. SAVE
# =====================================================================

image_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
image_dir.mkdir(parents=True, exist_ok=True)

png_path = image_dir / "new-england-coast-quiet_density.png"
script_path = Path(
    "/home/pi/Documents/code/quortol/backend/blogs/scripts"
    "/chart1_new-england-coast-quiet_density.py"
)

ggsave(p, str(png_path), w=8, h=4.8, unit="in", dpi=150)

print(f"Chart saved to: {png_path}")
print(f"Script:       {script_path}")
