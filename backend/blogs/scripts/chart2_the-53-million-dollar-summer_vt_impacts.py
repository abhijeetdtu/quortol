#!/usr/bin/env python3
"""Chart: Vermont 2025 Agricultural Drought Survey Results

Horizontal bar chart for a magazine article about drought losses.

Output: backend/blogs/images/the-53-million-dollar-summer_vt_impacts.png
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ==============================================================
# DATA
# ==============================================================
df = pd.DataFrame({
    "category": [
        "Lower crop yields or total crop failure",
        "Feed shortages going into winter",
        "Worst drought they had ever seen",
        "Insufficient pasture for forage",
        "Purchased/hauled water for first time",
    ],
    "percentage": [85, 63, 59, 51, 30],
})

# Sort ascending so horizontal bars render largest at top
df = df.sort_values("percentage", ascending=True).reset_index(drop=True)

# Percentage labels
df["label"] = df["percentage"].apply(lambda v: f"{v}%")

print("Data preview:")
print(df.to_string(index=False))

# ==============================================================
# COLORS
# ==============================================================
# Use a single drought-appropriate color (Tol bright orange/amber)
fill_color = "#D55E00"

# ==============================================================
# CHART
# ==============================================================
p = (
    ggplot(df, aes(x="percentage", y="category"))
    + geom_bar(fill=fill_color, stat="identity", width=0.65)
    + geom_text(
        aes(label="label"),
        hjust=-0.15,
        size=11,
        color="#333333",
        family="sans-serif",
    )
    + scale_x_continuous(limits=[0, 100])
    + labs(
        title="How Vermont's 2025 Drought Hit Farms",
        subtitle="Share of surveyed agricultural businesses reporting each impact",
        x="Percentage of respondents",
        y="",
        caption=(
            "Source: Vermont Agency of Agriculture, Food & Markets, "
            "2025 Agricultural Drought Survey (n=198 businesses, all 14 counties)"
        ),
    )
    + theme(
        plot_title=element_text(size=16, face="bold", hjust=0),
        plot_subtitle=element_text(size=12, hjust=0, color="#555555"),
        plot_caption=element_text(size=8, hjust=0, color="#888888"),
        axis_text_y=element_text(size=11),
        axis_text_x=element_text(size=10),
        axis_title_x=element_text(size=11),
        axis_title_y=element_text(size=11),
        axis_ticks_y=element_blank(),
        panel_grid_major_x=element_line(color="#EEEEEE", size=0.4),
        panel_grid_major_y=element_blank(),
        legend_position="none",
        panel_background=element_blank(),
        plot_background=element_blank(),
        plot_margin=margin(15, 30, 10, 10),
    )
    + ggsize(1200, 720)
)

# ==============================================================
# SAVE
# ==============================================================
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "the-53-million-dollar-summer_vt_impacts.png"
ggsave(p, str(output_path), w=1200, h=720, unit="px", dpi=150)
print(f"\nChart saved: {output_path}")
