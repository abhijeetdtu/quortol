#!/usr/bin/env python3
"""
Horizontal bar chart: documented hyperloop funding raised.

Bars sorted by funding (largest at top), all in a single Okabe-Ito blue.
Each bar annotated with its documented funding in USD millions.

Output: 1200x720 px PNG at 150 DPI.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────

data = {
    "company": [
        "Hyperloop One",
        "HyperloopTT",
        "Zeleros",
        "Hardt Hyperloop",
        "TransPod",
    ],
    "funding_usd_m": [462, 100, 16, 16, 15],
}

df = pd.DataFrame(data)

# ── Y-axis order: ascending funding → smallest at bottom, largest at top ─────

funding_order_asc = df.sort_values(
    "funding_usd_m", ascending=True
)["company"].tolist()

# ── Build plot ────────────────────────────────────────────────────────────────

p = (
    ggplot(df, aes(x="funding_usd_m", y="company"))
    + geom_bar(
        fill="#0072B2",
        stat="identity",
        width=0.75,
    )
    + geom_text(
        aes(label="funding_usd_m"),
        hjust=-0.2,
        size=7.5,
        color="#2d2d2d",
        family="sans-serif",
    )
    + scale_y_discrete(limits=funding_order_asc)
    + scale_x_continuous(
        limits=[0, 540],
        breaks=[0, 100, 200, 300, 400, 500],
    )
    + labs(
        title="Half a Billion for a One-Second Dream: Documented Hyperloop Funding",
        subtitle="Documented minimums; several firms announced larger commitments never delivered in full",
        x="Documented funding (USD millions)",
        y="",
        caption="Sources: Forge; TechCrunch (2016); TransPod press release (2016); Rolling Stock Agency (2026); Bits&Chips (2026)",
    )
    + theme(
        plot_title=element_text(size=15, face="bold", hjust=0, color="#1a1a1a"),
        plot_subtitle=element_text(size=10.5, hjust=0, color="#555555"),
        plot_caption=element_text(size=7, hjust=0, color="#888888"),
        axis_text_y=element_text(size=7.5),
        axis_text_x=element_text(size=8),
        axis_title_x=element_text(size=9.5),
        legend_position="none",
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

out_path = out_dir / "hyperloop-hype-to-doom_documented_funding.png"
ggsave(
    p,
    str(out_path),
    w=8.0,
    h=4.8,
    unit="in",
    dpi=150,
)

print(f"Chart saved: {out_path}")
