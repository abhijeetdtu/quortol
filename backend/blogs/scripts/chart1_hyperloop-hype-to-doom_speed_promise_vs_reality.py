#!/usr/bin/env python3
"""
Horizontal bar chart: The hyperloop's speed promise vs. achieved test runs.

Bars sorted by speed (fastest at top). The single "Promised" bar (2013
whitepaper design speed) is colored Okabe-Ito vermillion; all "Achieved"
documented test-run speeds are colored Okabe-Ito blue. Each bar annotated
with its speed in km/h.

Output: 1200x720 px PNG at 150 DPI.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────

data = {
    "label": [
        "2013 Musk whitepaper promise",
        "2024 CASIC T-Flight (China)",
        "2018 SpaceX competition pod",
        "2017 DevLoop unmanned test",
        "2020 First passenger ride",
        "2018 Boring Co. test tunnel",
    ],
    "speed_kmh": [1220, 623, 457, 387, 172, 64],
    "category": [
        "Promised",
        "Achieved",
        "Achieved",
        "Achieved",
        "Achieved",
        "Achieved",
    ],
}

df = pd.DataFrame(data)

# ── Y-axis order: ascending speed → slowest at bottom, fastest at top ────────

speed_order_asc = df.sort_values("speed_kmh", ascending=True)["label"].tolist()

# ── Color palette (Okabe-Ito: promised vs achieved) ───────────────────────────

palette = {
    "Promised": "#D55E00",
    "Achieved": "#0072B2",
}

# ── Build plot ────────────────────────────────────────────────────────────────

p = (
    ggplot(df, aes(x="speed_kmh", y="label"))
    + geom_bar(
        aes(fill="category"),
        stat="identity",
        width=0.75,
    )
    + geom_text(
        aes(label="speed_kmh"),
        hjust=-0.2,
        size=7.5,
        color="#2d2d2d",
        family="sans-serif",
    )
    + scale_y_discrete(limits=speed_order_asc)
    + scale_fill_manual(values=palette)
    + scale_x_continuous(
        limits=[0, 1360],
        breaks=[0, 200, 400, 600, 800, 1000, 1200],
    )
    + labs(
        title="The Hyperloop's Speed Gap: Promised vs. Delivered",
        subtitle="Design speed from the 2013 whitepaper vs. every documented test run",
        x="Speed (km/h)",
        y="",
        fill="",
        caption="Sources: SpaceX Hyperloop Alpha (2013); Virgin Hyperloop One press release (2017); BBC (2018); NYT (2020); Curbed LA (2018); CASIC via RailMarket (2024)",
    )
    + theme(
        plot_title=element_text(size=15, face="bold", hjust=0, color="#1a1a1a"),
        plot_subtitle=element_text(size=10.5, hjust=0, color="#555555"),
        plot_caption=element_text(size=7, hjust=0, color="#888888"),
        axis_text_y=element_text(size=7.5),
        axis_text_x=element_text(size=8),
        axis_title_x=element_text(size=9.5),
        legend_title=element_text(size=9),
        legend_text=element_text(size=8),
        legend_position="right",
        legend_background=element_blank(),
        panel_grid_major_x=element_line(color="#e8e8e8", size=0.3),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_blank(),
        panel_background=element_rect(fill="#ffffff"),
        plot_background=element_rect(fill="#ffffff"),
        axis_line_x=element_line(color="#cccccc", size=0.4),
        axis_ticks_y=element_blank(),
        plot_margin=[10, 20, 5, 5],
    )
)

# ── Save PNG ──────────────────────────────────────────────────────────────────

out_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "hyperloop-hype-to-doom_speed_promise_vs_reality.png"
ggsave(
    p,
    str(out_path),
    w=8.0,
    h=4.8,
    unit="in",
    dpi=150,
)

print(f"Chart saved: {out_path}")
