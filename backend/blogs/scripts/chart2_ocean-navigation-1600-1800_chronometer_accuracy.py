#!/usr/bin/env python3
"""
Chart 2: Ocean Navigation 1600–1800 — Chronometer Accuracy
===========================================================
Line chart showing improvement in marine timekeeper accuracy (seconds per day drift)
from Harrison's H1 (1735) to production chronometers (1800).

lets-plot 4.9.0, 1200×720 px, 150 DPI, colorblind-safe blue palette.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "year": [1735, 1741, 1759, 1761, 1766, 1772, 1782, 1795, 1800],
    "drift": [60.0, 15.0, 10.0, 0.5, 1.5, 1.0, 0.8, 0.5, 0.3],
    "device": [
        "Harrison H1", "Harrison H2", "Harrison H3", "Harrison H4",
        "Le Roy", "Harrison H5", "Berthoud No.24",
        "Earnshaw production", "Arnold production",
    ],
})

# Manually positioned labels (label_x, label_y in data coords) to avoid overlap
# on the log-scaled y-axis where lower values cluster tightly.
label_positions = pd.DataFrame({
    "year": [1735, 1741, 1759, 1761, 1766, 1772, 1782, 1795, 1800],
    "drift": [60.0, 15.0, 10.0, 0.5, 1.5, 1.0, 0.8, 0.5, 0.3],
    "device": [
        "Harrison H1", "Harrison H2", "Harrison H3", "Harrison H4",
        "Le Roy", "Harrison H5", "Berthoud No.24",
        "Earnshaw production", "Arnold production",
    ],
    "label_x": [1735.0, 1741.0, 1759.0, 1766.0, 1766.0, 1775.0, 1782.0, 1798.0, 1805.0],
    "label_y": [85.0, 22.0, 14.0, 0.08, 4.5, 0.15, 2.2, 0.08, 0.07],
})

# Segment endpoints: from label tip back toward data point
segments = label_positions.copy()
segments["seg_xend"] = segments["year"]
segments["seg_yend"] = segments["drift"]

# ── Plot ──────────────────────────────────────────────────────────────────────

p = (
    ggplot(data, aes(x="year", y="drift"))
    # Improvement line
    + geom_line(color="#2563EB", size=1.6, alpha=0.85)
    # Data points (filled circles with stroke)
    + geom_point(
        color="#2563EB", fill="#1E40AF",
        size=4.5, stroke=1.2, shape=21, alpha=0.95,
    )
    # Leader lines from label to data point
    + geom_segment(
        data=segments,
        mapping=aes(x="label_x", y="label_y", xend="seg_xend", yend="seg_yend"),
        color="#6B8BAE",
        size=0.5,
        alpha=0.55,
    )
    # Device labels at computed positions
    + geom_text(
        data=label_positions,
        mapping=aes(x="label_x", y="label_y", label="device"),
        size=9,
        color="#1E3A5F",
        fontface="bold",
        hjust="left",
        vjust="middle",
    )
    # Log scale Y (drift spans 60 → 0.3 seconds/day)
    + scale_y_log10(
        breaks=[0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 100],
        limits=[0.06, 120],
    )
    # Linear scale X with decade breaks
    + scale_x_continuous(
        breaks=list(range(1730, 1810, 10)),
        limits=[1728, 1815],
        format="d",
    )
    # ── Labels ──
    + labs(
        title="Improvement in Marine Timekeeper Accuracy",
        subtitle=(
            "From Harrison\u2019s H1 to production chronometers: "
            "seconds per day drift"
        ),
        x="Year",
        y="Seconds per day drift (log scale)",
        caption="Sources: Gould (1923); Royal Observatory Greenwich archives.",
    )
    # ── Theme ──
    + theme(
        text=element_text(family="sans-serif"),
        plot_title=element_text(size=18, face="bold", margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=12, color="#555555", margin=[0, 0, 14, 0]),
        plot_caption=element_text(size=9, color="#888888", margin=[14, 0, 0, 0]),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_title_y=element_text(size=12, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=10),
        axis_text_y=element_text(size=10),
        axis_line_x=element_line(color="#CCCCCC"),
        axis_line_y=element_line(color="#CCCCCC"),
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.4),
        panel_grid_minor=element_blank(),
        plot_background=element_rect(fill="#FAFAFA"),
        panel_background=element_rect(fill="#FFFFFF"),
        plot_margin=[20, 20, 10, 10],
        axis_ticks=element_line(color="#CCCCCC"),
    )
)

# ── Save ──────────────────────────────────────────────────────────────────────

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "ocean-navigation-1600-1800_chronometer_accuracy.png"

ggsave(p, str(output_path), w=8, h=4.8, dpi=150, unit="in")
print(f"Chart saved: {output_path.resolve()}")
