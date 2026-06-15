#!/usr/bin/env python3
"""
Chart: Global Podcast Listeners Growth (2019–2027)
Line chart with filled area beneath the line.

Output: the-podcast-in-your-ear_listeners_growth.png (1200×720 px @ 150 DPI)
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "year":      [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027],
    "listeners": [274.8, 333.2, 383.7, 424.2, 464.7, 504.9, 584.1, 619.2, 651.7],
})

# Split so we can style actual (solid) vs projected (dashed)
df_actual    = df[df["year"] <= 2026]          # 2019 – 2026
df_projected = df[df["year"] >= 2026].copy()   # 2026 – 2027 (overlap at 2026 for continuity)

# ---------------------------------------------------------------------------
# Annotation helper
# ---------------------------------------------------------------------------
annotation_label = pd.DataFrame({
    "x": [2023.8], "y": [682], "label": ["651.7M projected"],
})
annotation_seg   = pd.DataFrame({
    "x": [2023.8], "y": [682], "xend": [2026.9], "yend": [653.5],
})

# ---------------------------------------------------------------------------
# Build chart
# ---------------------------------------------------------------------------
p = (
    ggplot()
    # Filled area under the whole series
    + geom_area(
        data=df, mapping=aes(x="year", y="listeners"),
        fill="#DBEAFE", alpha=0.85,
    )
    # Solid line for actual data (2019–2026)
    + geom_line(
        data=df_actual, mapping=aes(x="year", y="listeners"),
        color="#2563EB", size=1.5,
    )
    # Dashed line for projected (2026–2027, overlapping at 2026)
    + geom_line(
        data=df_projected, mapping=aes(x="year", y="listeners"),
        color="#2563EB", size=1.5, linetype="dashed",
    )
    # Data-point markers
    + geom_point(
        data=df, mapping=aes(x="year", y="listeners"),
        color="#2563EB", size=2.5,
    )
    # Annotation — text label
    + geom_text(
        data=annotation_label, mapping=aes(x="x", y="y", label="label"),
        color="#2563EB", size=9, hjust=0,
    )
    # Annotation — pointing arrow
    + geom_segment(
        data=annotation_seg, mapping=aes(x="x", y="y", xend="xend", yend="yend"),
        color="#2563EB", size=0.6,
        arrow=arrow(length=0.15, type="closed"),
    )
    # Labels / title / source
    + ggtitle("Global Podcast Listeners Have More Than Doubled Since 2019")
    + xlab("")
    + ylab("Listeners (millions)")
    + labs(caption="Source: eMarketer, Priori Data, Backlinko")
    # Scales
    + scale_x_continuous(breaks=list(range(2019, 2028)))
    + scale_y_continuous(
        limits=[0, 750],
        breaks=[0, 100, 200, 300, 400, 500, 600, 700],
    )
    # Theme – clean publication-ready look
    + theme_minimal()
    + theme(
        plot_title       = element_text(size=18, face="bold", hjust=0.5,
                                        margin=[0, 0, 10, 0]),
        axis_title_y     = element_text(size=13, margin=[0, 8, 0, 0]),
        axis_text        = element_text(size=11, color="#374151"),
        plot_caption     = element_text(size=10, hjust=0, color="#6B7280",
                                        margin=[10, 0, 0, 0]),
        panel_grid_major_x = element_blank(),
        panel_grid_major_y = element_line(color="#F3F4F6", size=0.4),
        panel_grid_minor   = element_blank(),
        axis_line_x      = element_line(color="#D1D5DB", size=0.5),
        axis_ticks_x     = element_line(color="#D1D5DB", size=0.5),
        axis_ticks_y     = element_blank(),
        plot_margin      = [15, 25, 10, 15],
    )
)

# ---------------------------------------------------------------------------
# Export — 1200×720 px at 150 DPI → 8 × 4.8 in
# ---------------------------------------------------------------------------
output_path = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "the-podcast-in-your-ear_listeners_growth.png"
)
ggsave(p, output_path, dpi=150, w=8, h=4.8, unit="in")
print(f"✓ Chart saved → {output_path}")
