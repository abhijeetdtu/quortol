#!/usr/bin/env python3
"""
chart3_ocean-navigation-1600-1800_voyage_times.py

Vertical bar chart: Average westbound Atlantic crossing time from Europe to
North America per decade, 1600–1800. Colorblind-safe blue-green sequential
gradient emphasises the steady improvement (10 → 5 weeks).

Output: 1200×720 px PNG at 150 DPI.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
data = {
    "Decade": [1600, 1620, 1640, 1660, 1680, 1700, 1720, 1740, 1760, 1780, 1800],
    "Weeks":  [10.0,  9.5,  9.0,  8.5,  8.0,  7.5,  7.0,  6.5,  6.0,  5.5,  5.0],
}
df = pd.DataFrame(data)

# ── Trend annotation arrow (pointing down from first bar to last) ────────────
# Arrow starts above the 1600 bar and ends below the 1800 bar
trend_arrow = pd.DataFrame({
    "x":    [1598, 1802],
    "y":    [10.6,  4.4],
})

# Label positioned mid-way above the arrow
trend_label = pd.DataFrame({
    "x": [1700],
    "y": [11.3],
    "label": ["Voyage time halved over 200 years"],
})

# ── Colour-blind safe sequential blue-green gradient ─────────────────────────
# Dark  → #08306b  (deep navy blue)
# Light → #c4e6d0  (pale sea-green)
CB_BLUE_GREEN_LOW  = "#c4e6d0"
CB_BLUE_GREEN_HIGH = "#08306b"

# ── Build the plot ───────────────────────────────────────────────────────────
p = (
    ggplot(df, aes(x="Decade", y="Weeks", fill="Weeks"))
    # Bars
    + geom_bar(stat="identity", width=16, color="white", size=0.4, alpha=0.92)
    # Trend arrow
    + geom_segment(
        aes(x="x", y="y", xend="x", yend="y"),
        data=trend_arrow,
        arrow=arrow(length=0.18, type="closed"),
        color="#333333", size=0.9, show_legend=False,
    )
    # Trend label
    + geom_text(
        aes(x="x", y="y", label="label"),
        data=trend_label, size=9.5, color="#222222", hjust=0.5, fontface="italic",
    )
    # Scales
    + scale_fill_gradient(low=CB_BLUE_GREEN_LOW, high=CB_BLUE_GREEN_HIGH)
    + scale_x_continuous(
        breaks=[1600, 1620, 1640, 1660, 1680, 1700, 1720, 1740, 1760, 1780, 1800],
    )
    + scale_y_continuous(
        limits=[0, 12.5],
        breaks=[0, 2, 4, 6, 8, 10, 12],
        expand=[0, 0],
    )
    # Labels
    + labs(
        title="Average Atlantic Crossing Time, Europe to North America",
        subtitle="Westbound voyage duration from Western Europe to Eastern North America, 1600–1800",
        x="Decade",
        y="Weeks",
        caption="Sources: Davis (1962); Parry (1966); Lloyd's Register data.",
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title      = element_text(size=17, face="bold", hjust=0.5),
        plot_subtitle   = element_text(size=10.5, color="#666666", hjust=0.5,
                                       margin=[0, 0, 14, 0]),
        plot_caption    = element_text(size=9, color="#999999", hjust=0,
                                       margin=[12, 0, 0, 0]),
        axis_title      = element_text(size=12),
        axis_text       = element_text(size=10),
        legend_position = "none",
        panel_grid_major = element_line(color="#e0e0e0", size=0.35),
        panel_grid_minor = element_blank(),
        axis_line       = element_line(color="#cccccc", size=0.4),
    )
)

# ── Output paths ──────────────────────────────────────────────────────────────
script_dir = Path(__file__).parent.resolve()
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

png_path = images_dir / "ocean-navigation-1600-1800_voyage_times.png"
print(f"Saving chart → {png_path}")

# 1200 / 150 = 8 in wide, 720 / 150 = 4.8 in tall
ggsave(p, str(png_path), w=8, h=4.8, unit="in", dpi=150)

print("Done.")
