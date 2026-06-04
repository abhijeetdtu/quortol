#!/usr/bin/env python3
"""
Chart: Demographic Composition of New England States
Grouped bar chart using lets-plot.

Data source:
  U.S. Census Bureau QuickFacts, 2020–2024 American Community Survey estimates.
  White alone (not Hispanic) derived as White alone minus Hispanic.

Notes:
  - Categories are NOT mutually exclusive (Hispanic can be any race).
    Both racial categories AND Hispanic are shown to give the full picture.
  - "White alone (not Hispanic)" is calculated as White alone minus
    Hispanic or Latino per ACS overlap conventions.
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
states_long = ["Connecticut", "Maine", "Massachusetts",
               "New Hampshire", "Rhode Island", "Vermont"]
states_short = ["CT", "ME", "MA", "NH", "RI", "VT"]

# Percentages from U.S. Census Bureau ACS 2020–2024
data = pd.DataFrame({
    "state_short": states_short,
    "state_long":  states_long,
    "White alone (not Hispanic)": [62.2, 91.3, 67.6, 88.1, 68.0, 91.0],
    "Black alone":                [13.3,  2.5,  9.9,  2.1,  9.5,  1.7],
    "Asian alone":                 [5.5,  1.5,  8.3,  3.2,  4.1,  2.3],
    "Hispanic or Latino":         [19.2,  2.4, 14.0,  5.0, 18.8,  2.7],
    "Two or More Races":           [2.9,  2.0,  3.0,  2.0,  3.2,  2.3],
})

# Melt to long format for grouped bars
plot_df = data.melt(
    id_vars=["state_short", "state_long"],
    var_name="category",
    value_name="percentage",
)

# Preserve category ordering
cat_order = [
    "White alone (not Hispanic)",
    "Black alone",
    "Asian alone",
    "Hispanic or Latino",
    "Two or More Races",
]
plot_df["category"] = pd.Categorical(
    plot_df["category"], categories=cat_order, ordered=True,
)

# ── Colorblind-safe palette (Okabe & Ito / Wong compatible) ──────────────
# Blue, Vermillion, Green, Orange, Pink
CB_PALETTE = {
    "White alone (not Hispanic)": "#0072B2",
    "Black alone":                "#D55E00",
    "Asian alone":                "#009E73",
    "Hispanic or Latino":         "#E69F00",
    "Two or More Races":          "#CC79A7",
}

# ── Plot ──────────────────────────────────────────────────────────────────
p = (
    ggplot(plot_df, aes(x="state_short", y="percentage", fill="category"))
    + geom_bar(stat="identity", position=position_dodge(0.85),
               width=0.75, size=0.3, color="white")
    # Data labels above each bar
    + geom_text(
        aes(label="percentage"),
        stat="identity",
        position=position_dodge(0.85),
        size=8,                     # ~8 pt
        color="#333333",
        va="bottom",
        ha="center",
        format=".1f",
    )
    # Title & axis labels
    + ggtitle("Demographic Composition of New England States")
    + xlab("State")
    + ylab("Percentage of population")
    # Source caption
    + labs(
        caption="Source: U.S. Census Bureau, ACS 2020–2024",
        fill="Category",
    )
    # Fill scale — colorblind-safe
    + scale_fill_manual(values=CB_PALETTE)
    # Expand y-axis so labels fit
    + scale_y_continuous(expand=[0, 0.12])
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, hjust=0.5, face="bold", margin=10),
        axis_title_x=element_text(size=13, margin=8),
        axis_title_y=element_text(size=13, margin=10),
        axis_text_x=element_text(size=12, angle=0, hjust=0.5),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=9, hjust=0.5, color="#777777",
                                  margin=[10, 0, 0, 0]),
        legend_title=element_text(size=11, face="bold"),
        legend_text=element_text(size=10),
        legend_position="right",
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.3),
        axis_line_x=element_line(color="#333333", size=0.4),
        axis_line_y=element_line(color="#333333", size=0.4),
        axis_ticks_x=element_line(color="#333333", size=0.4),
        axis_ticks_y=element_line(color="#333333", size=0.4),
        plot_background=element_rect(fill="white", color=None),
        panel_background=element_rect(fill="white", color=None),
    )
)

# ── Save ──────────────────────────────────────────────────────────────────
out_dir = Path(__file__).resolve().parents[1] / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "new-england-coast-quiet_demographics.png"

# 1200 × 720 px @ 150 DPI  →  8 × 4.8 inches
saved = ggsave(
    p,
    filename=str(out_path),
    w=8,
    h=4.8,
    unit="in",
    dpi=150,
)

print(f"Saved: {saved}")
print(f"  Path: {out_path.resolve()}")
print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
