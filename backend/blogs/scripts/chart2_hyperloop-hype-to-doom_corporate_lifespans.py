#!/usr/bin/env python3
"""
Horizontal Gantt-style chart: hyperloop company lifespans.

Each company is drawn as a horizontal bar spanning founding year → end year
(dead companies end at shutdown; survivors are extended through 2026).
Dead companies are colored Okabe-Ito blue, alive companies Okabe-Ito green,
and the state program vermillion. A diamond marker sits at each bar's end
year, annotated with the year (or "2026+" for survivors).

Output: 1200x720 px PNG at 150 DPI.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────

data = {
    "company": [
        "HyperloopTT (US)",
        "Hyperloop One (US)",
        "TransPod (CA)",
        "Arrivo (US)",
        "Hardt Hyperloop (NL)",
        "Zeleros (ES)",
        "CASIC T-Flight (CN)",
    ],
    "founded": [2013, 2014, 2015, 2016, 2016, 2016, 2019],
    "ended": [2026, 2023, 2026, 2018, 2026, 2026, 2026],
    "status": [
        "Alive",
        "Dead",
        "Alive",
        "Dead",
        "Dead",
        "Dead",
        "State program",
    ],
}

df = pd.DataFrame(data)

# Survivors carry an "ongoing" marker at the end of the chart
df["end_label"] = [
    "2026+" if s != "Dead" else str(y)
    for s, y in zip(df["status"], df["ended"])
]

# ── Y-axis order: by founding year (oldest at top) ───────────────────────────

company_order_asc = df.sort_values("founded", ascending=True)["company"].tolist()

# ── Color palette (Okabe-Ito, by status) ─────────────────────────────────────

status_colors = {
    "Dead": "#0072B2",
    "Alive": "#009E73",
    "State program": "#D55E00",
}

# ── Build plot ────────────────────────────────────────────────────────────────

p = (
    ggplot(df, aes(x="founded", xend="ended", y="company", yend="company"))
    + geom_segment(
        aes(color="status"),
        size=8,
        lineend="round",
    )
    + geom_point(
        aes(x="ended", y="company", color="status"),
        shape=18,
        size=4,
    )
    + geom_text(
        aes(x="ended", y="company", label="end_label"),
        hjust=-0.2,
        size=7.5,
        color="#2d2d2d",
        family="sans-serif",
    )
    + scale_y_discrete(limits=company_order_asc)
    + scale_color_manual(values=status_colors)
    + scale_x_continuous(
        limits=[2012, 2036],
        breaks=[2014, 2016, 2018, 2020, 2022, 2024, 2026],
    )
    + labs(
        title="A Decade of Hyperloop Companies, and Where They Ended",
        subtitle="Company lifespans from founding to shutdown; survivors shown through 2026",
        x="Year",
        y="",
        color="Status",
        caption="Sources: TechCrunch (2023); The Verge (2018); Hardt Group statement (2026); Railway Gazette (2026); Bloomberg (2023); Renewables Now (2026)",
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

out_path = out_dir / "hyperloop-hype-to-doom_corporate_lifespans.png"
ggsave(
    p,
    str(out_path),
    w=8.0,
    h=4.8,
    unit="in",
    dpi=150,
)

print(f"Chart saved: {out_path}")
