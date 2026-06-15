"""
Chart 2: U.S. Podcast Advertising Revenue Growth (2015–2026)
Vertical bar chart showing IAB/PwC podcast ad revenue data.
lets-plot 4.9.0, 1200×720 px, 150 DPI, colorblind-safe.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data ---
data = pd.DataFrame({
    "year": [2015, 2022, 2023, 2024, 2025, 2026],
    "revenue": [0.106, 1.80, 2.10, 2.40, 2.86, 3.00],
})

data["year_str"] = data["year"].astype(str)

# Flag 2026 as projected
data["type"] = ["Actual"] * 5 + ["Projected"]

# --- Color configuration ---
actual_color = "#0D9488"       # dark teal
projected_color = "#99CBC6"    # lighter teal for projected
actual_fill = "#E6F7F5"       # very light teal fill for actual bars
projected_fill = "#F0FBFA"    # very light teal fill for projected bar

# --- Label text ---
data["label"] = data["revenue"].apply(lambda v: f"${v:.1f}B")

# --- Build chart ---
p = (
    ggplot(data, aes(x="year_str", y="revenue"))
    # Bars with outline and fill
    + geom_bar(
        mapping=aes(fill="type", color="type"),
        stat="identity",
        size=1.2,
        width=0.65,
    )
    # Data labels
    + geom_text(
        mapping=aes(label="label"),
        nudge_y=0.08,
        size=12,
        color="#1A1A1A",
        fontface="bold",
        va="bottom",
    )
    # Color scales
    + scale_fill_manual(
        values={"Actual": actual_color, "Projected": projected_color},
        guide="none",
    )
    + scale_color_manual(
        values={"Actual": actual_color, "Projected": projected_color},
        guide="none",
    )
    # Axes
    + scale_y_continuous(
        limits=[0, 3.6],
        breaks=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
        labels=["$0", "$0.5B", "$1.0B", "$1.5B", "$2.0B", "$2.5B", "$3.0B", "$3.5B"],
        expand=[0, 0],
    )
    + scale_x_discrete()
    # Labels
    + labs(
        title="U.S. Podcast Ad Revenue: From $100M to $3B in Eleven Years",
        subtitle="IAB/PwC measured podcast advertising revenue — note the eight-year gap (2015→2022) in official tracking",
        x="",
        y="Revenue ($ billions USD)",
        caption="Source: IAB/PwC Internet Advertising Revenue Report",
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", hjust=0, margin=[0, 0, 4, 0]),
        plot_subtitle=element_text(size=11, color="#666666", hjust=0, margin=[0, 0, 20, 0]),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=13, margin=[0, 12, 0, 0], hjust=0.5),
        axis_text_x=element_text(size=13, color="#333333"),
        axis_text_y=element_text(size=11, color="#444444"),
        plot_caption=element_text(size=10, color="#888888", hjust=0, margin=[16, 0, 0, 0]),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.5),
        panel_background=element_blank(),
        plot_margin=[24, 30, 12, 18],
        axis_ticks_x=element_line(color="#CCCCCC", size=0.3),
        axis_ticks_y=element_blank(),
        axis_line_x=element_line(color="#CCCCCC", size=0.5),
    )
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-podcast-in-your-ear_ad_revenue.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 2 saved to: {output_path}")
