"""
Chart 3: The Decarbonization Gap
Grouped horizontal bar chart showing alternative-fuel readiness:
active fleet vs. orderbook (% of tonnage).
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe.
Source: UNCTAD Review of Maritime Transport 2025 (Overview)
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data (long format) ---
data = pd.DataFrame({
    "fleet": ["Active Fleet", "Active Fleet", "Orderbook", "Orderbook"],
    "fuel":  ["Conventional", "Alternative", "Conventional", "Alternative"],
    "pct":   [92, 8, 47, 53],
})

# Sort so Conventional appears first in each group
data["fuel"] = pd.Categorical(
    data["fuel"],
    categories=["Conventional", "Alternative"],
    ordered=True,
)

# Preserve fleet order for the y-axis (Active Fleet on top)
data["fleet"] = pd.Categorical(
    data["fleet"],
    categories=["Active Fleet", "Orderbook"],
    ordered=True,
)

# --- Colorblind-safe palette ---
# Green for alternative, neutral blue-gray for conventional
color_map = {
    "Conventional": "#6C7A89",   # muted blue-gray
    "Alternative":  "#2ECC71",   # green (colorblind-visible)
}

# --- Build chart ---
p = (
    ggplot(data, aes(x="fleet", y="pct", fill="fuel"))
    + geom_bar(
        stat="identity",
        position=position_dodge(width=0.7),
        width=0.6,
        alpha=0.92,
        color=None,
    )
    + geom_hline(yintercept=0, size=0.3, color="#333333")
    + scale_fill_manual(
        values=color_map,
        name="Fuel Type",
    )
    + scale_y_continuous(
        limits=[0, 108],
        breaks=[0, 20, 40, 60, 80, 100],
        expand=[0, 0],
    )
    + coord_flip()
    + labs(
        title="The Gap Between Ambition and Reality: Alternative-Fuel Ships",
        subtitle="Percent of tonnage, active fleet vs. orderbook (May 2025)",
        x="",
        y="Percent of tonnage",
        caption="Source: UNCTAD Review of Maritime Transport 2025 (Overview)",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0, margin=[0, 0, 18, 0]),
        axis_title_y=element_blank(),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0], color="#444444"),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=13, face="bold"),
        axis_ticks_x=element_line(color="#CCCCCC", size=0.3),
        axis_ticks_y=element_blank(),
        plot_caption=element_text(size=9.5, color="#888888", hjust=0, margin=[14, 0, 0, 0]),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_x=element_line(color="#E6E6E6", size=0.35),
        panel_grid_minor_x=element_blank(),
        plot_margin=[20, 20, 10, 10],
        legend_position="bottom",
        legend_title=element_text(size=11, face="bold"),
        legend_text=element_text(size=11),
        legend_spacing=[0, 0, 10, 0],
    )
    # Percentage labels on bars (position_dodge adjusted)
    + geom_text(
        mapping=aes(label="pct"),
        stat="identity",
        position=position_dodge(width=0.7),
        # hjust depends on bar direction — since we coord_flip:
        # horizontal bars: positive hjust pushes right of bar end
        hjust=-0.25,
        size=12,
        color="#222222",
        fontface="bold",
    )
    + geom_text(
        mapping=aes(label="'%'"),
        stat="identity",
        position=position_dodge(width=0.7),
        hjust=-0.55,
        size=9,
        color="#666666",
    )
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "redrawing-the-map_fleet_green_gap.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 3 saved to: {output_path}")
