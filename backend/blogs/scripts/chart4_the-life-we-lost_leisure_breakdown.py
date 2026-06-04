"""
Chart 4: Composition of 5.07 Hours of Daily Leisure (US, 2024)
Horizontal stacked bar chart showing how US adults spend their leisure time.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe.
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data ---
data = pd.DataFrame({
    "activity": [
        "Watching TV",
        "Socializing &\ncommunicating",
        "Games & computer\nuse (leisure)",
        "Relaxing &\nthinking",
        "Sports, exercise,\nrecreation",
        "Reading for\npersonal interest",
        "Other leisure\ndiscretionary",
    ],
    "hours": [2.60, 0.59, 0.56, 0.36, 0.28, 0.20, 0.48],
    "minutes": [156, 35, 34, 22, 17, 12, 29],
    "pct": [51.3, 11.6, 11.0, 7.1, 5.5, 3.9, 9.5],
})

# Sort by hours descending (TV at top of horizontal bar)
data = data.sort_values("hours", ascending=True).reset_index(drop=True)
data["activity"] = pd.Categorical(
    data["activity"],
    categories=data["activity"].tolist(),
    ordered=True,
)

# Format pct labels
data["pct_label"] = data["pct"].round(1).astype(str) + "%"

# Colorblind-safe distinct palette (Wong 2011 extended)
color_map = {
    "Watching TV": "#D55E00",
    "Socializing &\ncommunicating": "#E69F00",
    "Games & computer\nuse (leisure)": "#0072B2",
    "Relaxing &\nthinking": "#009E73",
    "Sports, exercise,\nrecreation": "#56B4E9",
    "Reading for\npersonal interest": "#CC79A7",
    "Other leisure\ndiscretionary": "#999999",
}

# Single stacked bar
bar_data = data.copy()
bar_data["total"] = "5.07 hours daily leisure"

# Compute cumulative positions for label placement
bar_data["label_pos"] = bar_data["hours"].cumsum() - bar_data["hours"] / 2

# --- Build chart ---
p = (
    ggplot(bar_data, aes(x="total", y="hours", fill="activity"))
    + geom_bar(stat="identity", width=0.4, alpha=0.92, color="white", size=0.5)
    + geom_text(
        mapping=aes(label="pct_label", y="label_pos"),
        size=10, color="white", fontface="bold",
    )
    + scale_fill_manual(values=color_map, name="Activity")
    + coord_flip()
    + labs(
        title="Where the 5.07 Daily Leisure Hours Go (US Adults, 2024)",
        subtitle=(
            "Television consumes more than half of all leisure time. "
            "Face-to-face socializing: 35 minutes."
        ),
        x="",
        y="Hours per day",
        caption="Source: BLS American Time Use Survey, 2024",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=12, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_y=element_blank(),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_text_x=element_text(size=10),
        axis_text_y=element_text(size=12, color="#333333"),
        plot_caption=element_text(size=9, color="#888888", hjust=0, margin=[12, 0, 0, 0]),
        legend_position="right",
        legend_text=element_text(size=10),
        legend_title=element_text(size=11, face="bold"),
        panel_grid_major=element_blank(),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 20, 10, 10],
    )
    + scale_y_continuous(
        limits=[0, 5.5],
        breaks=list(np.arange(0, 5.6, 1)),
        expand=[0, 0],
    )
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-life-we-lost_chart4_leisure_breakdown.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 4 saved to: {output_path}")
