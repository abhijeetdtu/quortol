#!/usr/bin/env python3
"""
chart3_new_hampshire_bed_and_breakfasts_ownership_structure.py

Horizontal bar chart: B&B establishments in New Hampshire by ownership type.
Data from SmartScraper/Rentech Digital — April 2026.

Output: 1200×720 px PNG at 150 DPI
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "category": ["Single-owner B&Bs", "Branded/chain B&Bs"],
    "count":    [178, 30],
    "pct":      ["85.58%", "14.42%"],
    # colour assignment: green for single-owner, blue for branded
    "fill_col": ["#2E7D32", "#1565C0"],
})

# ── Build horizontal bar chart ────────────────────────────────────────────────
# For a horizontal bar chart, we map category to y and count to x.
# We also build a label combining count and percentage.

data["label"] = data["count"].astype(str) + "  (" + data["pct"] + ")"

p = (
    ggplot(data, aes(x="count", y="category", fill="category"))
    + geom_bar(stat="identity", width=0.55, color="white", size=0.4)
    # Colour-blind safe: green (#2E7D32) for single-owner, blue (#1565C0) for branded
    + scale_fill_manual(values={
        "Single-owner B&Bs": "#2E7D32",
        "Branded/chain B&Bs": "#1565C0",
    })
    # Labels at the end of each bar
    + geom_text(
        aes(label="label"),
        hjust=-0.08,           # nudge right so text sits outside the bar
        size=10,               # ~10pt font
        color="#2C3E50",
        fontstyle="bold",
    )
    # Titles and labels
    + ggtitle("New Hampshire Bed & Breakfasts by Ownership Type")
    + xlab("Number of Establishments")
    + ylab("")
    # Source line — lets-plot doesn't have a built-in footnote, so we use subtitle
    + labs(subtitle="Source: Rentech Digital / SmartScraper, April 2026")
    # Tweak limits to make room for labels
    + xlim(0, 230)
    # Theme polish
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, hjust=0.5, face="bold"),
        plot_subtitle=element_text(size=8, color="#777777", hjust=0.5,
                                   face="italic"),
        axis_text_y=element_text(size=11, face="bold"),
        axis_text_x=element_text(size=10),
        axis_title_x=element_text(size=11),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_blank(),
        legend_position="none",
        plot_margin=[15, 20, 30, 10],
    )
)

# ── Save ──────────────────────────────────────────────────────────────────────
output_path = "/home/pi/Documents/code/quortol/backend/blogs/images/new-hampshire-bed-and-breakfasts_ownership_structure.png"
ggsave(
    p,
    filename=output_path,
    w=8,
    h=4.8,
    dpi=150,
)

print(f"✅ Chart saved → {output_path}")
