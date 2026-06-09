#!/usr/bin/env python3
"""
chart3_pnw-reinvention_income_shift.py

Grouped vertical bar chart: Sources of Personal Income on the Oregon Coast,
2003 vs. 2021. Highlights the dramatic rise in transfer payments.

Data source: Oregon Coast Visitors Association / OCZMA Sources of Income Study, 2021

Output: PNG at 1200×720 px, 150 DPI (8 × 4.8 in).
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
# Reshape from wide (pivot) to long format for grouped bar chart.
data = pd.DataFrame({
    "source": [
        "Net earnings (jobs)",
        "Net earnings (jobs)",
        "Investment income (dividends, rent, pensions)",
        "Investment income (dividends, rent, pensions)",
        "Transfer payments (Social Security, Medicare, assistance)",
        "Transfer payments (Social Security, Medicare, assistance)",
    ],
    "year": ["2003", "2021", "2003", "2021", "2003", "2021"],
    "pct":  [53, 46, 23, 17, 24, 37],
})

# Ensure correct ordering of sources for the chart (as given: earnings, investment, transfer)
source_order = [
    "Net earnings (jobs)",
    "Investment income (dividends, rent, pensions)",
    "Transfer payments (Social Security, Medicare, assistance)",
]
data["source"] = pd.Categorical(data["source"], categories=source_order, ordered=True)

# ── Colorblind-safe palette ──────────────────────────────────────────────────
# Based on Okabe-Ito: light sky-blue for 2003, orange for 2021.
year_colors = {
    "2003": "#56B4E9",   # sky blue
    "2021": "#E69F00",   # orange
}

# ── Build the plot ────────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="source", y="pct", fill="year"))
    + geom_bar(stat="identity", position="dodge", width=0.7, color="white", size=0.3)
    + geom_text(
        aes(label="pct"),
        position=position_dodge(width=0.7),
        size=11,
        vjust=-0.6,
        fontface="bold",
        show_legend=False,
    )
    + scale_fill_manual(
        values=year_colors,
        name="",
    )
    + scale_y_continuous(
        name="Percent of total personal income",
        limits=[0, 62],
        breaks=[0, 10, 20, 30, 40, 50, 60],
        labels=["0%", "10%", "20%", "30%", "40%", "50%", "60%"],
        expand=[0, 0],
    )
    + scale_x_discrete(
        expand=[0.18, 0],
    )
    + labs(
        title="The New Economy on the Oregon Coast: Sources of Personal Income, 2003 vs. 2021",
        subtitle=(
            "Transfer payments — Social Security, Medicare, public assistance — "
            "now make up the largest source of personal income growth on the coast."
        ),
        x="",
        y="Percent of total personal income",
        caption="Source: Oregon Coast Visitors Association / OCZMA Sources of Income Study, 2021",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(
            size=11, color="#555555", hjust=0, margin=[0, 0, 18, 0],
        ),
        plot_caption=element_text(
            size=9, color="#888888", hjust=0, margin=[10, 0, 0, 0],
        ),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=12, margin=[0, 8, 0, 0]),
        axis_text_x=element_text(size=12, face="bold"),
        axis_text_y=element_text(size=11),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=12),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[12, 20, 10, 14],
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
    )
)

# ── Output paths ──────────────────────────────────────────────────────────────
script_dir = Path(__file__).parent.resolve()
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_path = images_dir / "pnw-reinvention_income_shift.png"
print(f"Saving chart → {output_path}")

# 1200 × 720 px at 150 DPI = 8 × 4.8 inches
ggsave(p, str(output_path), w=8, h=4.8, unit="in", dpi=150)

print("Done.")
