"""
Chart 3: Social Time vs. Screen Time in America (2003–2024)
Dual-axis line chart showing face-to-face socializing declining and digital media rising.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe.

Note: lets-plot does not support sec_axis natively, so screen time is plotted
at 1/10 scale on the primary axis. Right-side annotations indicate actual
screen time values.
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Social time data (minutes/day) ---
social_data = pd.DataFrame({
    "year": [2003, 2005, 2010, 2014, 2015, 2020, 2022, 2024],
    "minutes": [42, 41, 40, 43, 40, 33, 32, 35],
    "metric": "Face-to-face socializing",
})

# --- Screen time data (minutes/day) ---
# Scale by 1/10 so both series fit on same primary axis
screen_data = pd.DataFrame({
    "year": [2010, 2013, 2015, 2018, 2020, 2022, 2024],
    "minutes_actual": [330, 390, 420, 480, 516, 510, 516],
    "minutes": [33.0, 39.0, 42.0, 48.0, 51.6, 51.0, 51.6],
    "metric": "Digital media",
})

# Filter for text labels
social_labels = social_data[social_data["year"].isin([2003, 2020, 2024])].copy()
screen_labels = screen_data[screen_data["year"].isin([2010, 2024])].copy()

# Right-side annotation data for screen time (actual values)
right_labels = pd.DataFrame({
    "year": [2010, 2024],
    "label": ["330 min", "516 min"],
    "y": [33.0, 51.6],
})

# --- Build chart ---
p = (
    ggplot()
    # Social line
    + geom_line(
        data=social_data, mapping=aes(x="year", y="minutes", color="metric"),
        size=1.5,
    )
    + geom_point(
        data=social_data, mapping=aes(x="year", y="minutes", color="metric"),
        size=3,
    )
    + geom_text(
        data=social_labels,
        mapping=aes(x="year", y="minutes", label="minutes", color="metric"),
        nudge_y=3.5, size=8.5, fontface="bold", show_legend=False,
    )
    # Screen time line (scaled)
    + geom_line(
        data=screen_data, mapping=aes(x="year", y="minutes", color="metric"),
        size=1.5,
    )
    + geom_point(
        data=screen_data, mapping=aes(x="year", y="minutes", color="metric"),
        size=3,
    )
    + geom_text(
        data=screen_labels,
        mapping=aes(x="year", y="minutes", label="minutes_actual", color="metric"),
        nudge_y=3.5, size=8.5, fontface="bold", show_legend=False,
    )
    # Right-side screen time value annotations
    + geom_text(
        data=right_labels,
        mapping=aes(x="year", y="y", label="label"),
        nudge_y=3.0, size=7, color="#0072B2", hjust=0.5,
        show_legend=False,
    )
    # Vertical dotted line for 2013
    + geom_vline(xintercept=2013, linetype="dashed", color="#666666", size=0.7, alpha=0.6)
    + geom_text(
        x=2013, y=58,
        label="Smartphone adoption\npasses 50% (2013)",
        size=8, color="#666666", hjust=0.5, vjust=0,
    )
    # Colorblind-safe palette
    + scale_color_manual(
        values={
            "Face-to-face socializing": "#E69F00",
            "Digital media": "#0072B2",
        },
        name="",
    )
    + scale_x_continuous(
        breaks=[2003, 2005, 2010, 2013, 2015, 2018, 2020, 2022, 2024],
        expand=[0.008, 0.5],
    )
    # Single primary axis
    + scale_y_continuous(
        name="Minutes per day",
        limits=[0, 62],
        breaks=list(np.arange(0, 61, 10)),
    )
    + labs(
        title="The Great Swap: Social Time vs. Screen Time",
        subtitle=(
            "Minutes per day (US adults). Screen time plotted at 1/10 scale; "
            "actual values labeled on points."
        ),
        x="",
        y="Minutes per day",
        caption=(
            "Sources: BLS American Time Use Survey; "
            "eMarketer US Time Spent With Media 2025"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=12, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=12, margin=[0, 8, 0, 0]),
        axis_text_x=element_text(size=10, angle=35, hjust=1),
        axis_text_y=element_text(size=10),
        plot_caption=element_text(size=9, color="#888888", hjust=0, margin=[0, 0, 0, 0]),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=11),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[10, 20, 10, 10],
    )
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-life-we-lost_chart3_social_vs_screen.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 3 saved to: {output_path}")
