"""
Chart 2: The Micro-Adventure Economy — Frequency and Rental Growth
Faceted grouped bar chart with free scales.
Colorblind-safe categorical palette.
"""
from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "category": [
        "Micro-Adventure\nParticipants",
        "Legacy Vacation\nTravelers",
        "REI Gear\nRentals",
    ],
    "value": [3.0, 1.0, 54.0],
    "panel": [
        "Annual Return Frequency (trips/year)",
        "Annual Return Frequency (trips/year)",
        "REI Rental Growth (YoY %)",
    ],
    "color_group": [
        "Micro-Adventure\nParticipants",
        "Legacy Vacation\nTravelers",
        "REI Gear\nRentals",
    ],
})

# Sort panels so frequency comes first
data["panel"] = pd.Categorical(
    data["panel"],
    categories=["Annual Return Frequency (trips/year)", "REI Rental Growth (YoY %)"],
    ordered=True,
)

# Colorblind-safe palette (blue, vermillion, green)
palette = {
    "Micro-Adventure\nParticipants": "#0072B2",
    "Legacy Vacation\nTravelers": "#D55E00",
    "REI Gear\nRentals": "#009E73",
}

# ── Plot ──────────────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="category", y="value", fill="color_group"))
    + geom_bar(stat="identity", width=0.55, color="#ffffff", size=0.3)
    + geom_text(
        aes(label="value"),
        stat="identity",
        nudge_y=2.5,
        size=12,
        color="#1a1a2e",
        family="sans-serif",
        fontface="bold",
        va="bottom",
        ha="center",
        format=".0f",
    )
    + scale_fill_manual(values=palette)
    + facet_wrap(facets="panel", scales="free", ncol=2)
    + labs(
        title="The Micro-Adventure Economy: Frequency and Growth",
        subtitle="Return frequency and gear-rental trends driving the micro-adventure boom",
        x="",
        y="",
        fill="",
        caption="Sources: Industry data (artfasad.com, May 2026); REI Co-op 2025 Financial Results",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold", color="#1a1a2e", hjust=0.5),
        plot_subtitle=element_text(size=11, color="#555555", hjust=0.5, margin=[0, 0, 15, 0]),
        axis_text_x=element_text(size=10, color="#333333"),
        axis_text_y=element_text(size=10, color="#555555"),
        axis_title_x=element_blank(),
        axis_title_y=element_blank(),
        strip_text_x=element_text(size=12, face="bold", color="#1a1a2e"),
        strip_background=element_rect(fill="#f5f5f5", color=None, size=0),
        panel_grid_major_y=element_line(color="#e0e0e0", size=0.3),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        legend_position="none",
        plot_caption=element_text(size=8, color="#888888", hjust=1, margin=[8, 0, 0, 0]),
        plot_margin=[10, 20, 10, 10],
    )
)

# ── Save ──────────────────────────────────────────────────────────────────
output_dir = Path(__file__).resolve().parent.parent / "images"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = str(output_dir / "one-hour-adventure_economics.png")

ggsave(p, output_path, w=8, h=4.8, unit="in", dpi=150, scale=1.0)
print(f"\u2713 Saved: {output_path}")
