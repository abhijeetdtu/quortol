#!/usr/bin/env python3
"""
Chart: New Hampshire Meals & Rentals Tax Revenue, FY2020–FY2024
Vertical bar chart using lets-plot.

Data sources:
  - NH Department of Revenue Administration (Joint Economic Briefing Jan 2025)
  - NH Business Review: https://www.nhbr.com/will-canada-chatter-cool-nhs-tourism/
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "fiscal_year": ["FY2020", "FY2021", "FY2022", "FY2023", "FY2024"],
    "revenue_m":  [310.0, 368.4, 392.5, 448.5, 458.5],
})

# Colorblind-safe warm amber/orange (Okabe & Ito / Wong compatible)
BAR_FILL = "#E67E22"       # warm orange
BAR_EDGE = "#CC5500"       # darker edge for definition

# ── Plot ──────────────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="fiscal_year", y="revenue_m"))
    + geom_bar(
        stat="identity",
        fill=BAR_FILL,
        color=BAR_EDGE,
        width=0.6,
        size=0.4,
    )
    # Data labels on top of each bar
    + geom_text(
        aes(label="revenue_m"),
        stat="identity",
        nudge_y=8.0,             # push label above bar top
        size=10,                 # ~10 pt
        color="#333333",
        fontface="bold",
        ha="center",
        va="bottom",
        format=".1f",            # one decimal
    )
    # Labels & title
    + ggtitle("New Hampshire Meals & Rentals Tax Revenue, FY2020–FY2024")
    + xlab("")
    + ylab("Tax Revenue (Millions of Dollars)")
    # Source footnote via caption
    + labs(
        caption="Sources: NH Department of Revenue Administration; NH Business Review"
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=15, hjust=0.5, face="bold", margin=10),
        axis_title_y=element_text(size=12, margin=10),
        axis_text_x=element_text(size=11, angle=0, hjust=0.5),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=8, hjust=0.5, color="#777777",
                                  margin=[10, 0, 0, 0]),
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
    # Expand y-axis so labels fit
    + scale_y_continuous(expand=[0, 0.08])
)

# ── Save ──────────────────────────────────────────────────────────────────
out_dir = Path(__file__).resolve().parents[1] / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "new-hampshire-bed-and-breakfasts_meals_rentals_tax.png"

# 1200 x 720 px @ 150 DPI → 8 x 4.8 inches
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
