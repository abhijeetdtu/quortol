"""
Chart 3: U.S. Travel Spending Landscape (2026)
Horizontal bar chart showing components of the $1.37 trillion total.
Colorblind-safe sequential blue palette.
"""
from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "Category": [
        "Domestic Leisure Travel",
        "Business Travel",
        "International Inbound",
        "Domestic Group Travel",
    ],
    "Spending_B": [909.0, 319.0, 178.0, 118.0],
})

# Order from lowest → highest so coord_flip shows highest at the top
cat_order = data.sort_values("Spending_B", ascending=True)["Category"].tolist()
data["Category"] = pd.Categorical(data["Category"], categories=cat_order, ordered=True)

# Dollar labels for bar annotations
data["label"] = data["Spending_B"].apply(lambda v: f"${v:.0f}B")

# ── Plot ──────────────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="Category", y="Spending_B", fill="Spending_B"))
    + geom_bar(stat="identity", width=0.6, color="#ffffff", size=0.3)
    + geom_text(
        aes(label="label"),
        stat="identity",
        nudge_x=0.15,
        size=12,
        color="#1a1a2e",
        family="sans-serif",
        fontface="bold",
        va="middle",
        ha="left",
    )
    + scale_fill_gradient(low="#deebf7", high="#08306b")
    + coord_flip()
    + labs(
        title="U.S. Travel Spending by Segment, 2026 (inflation-adjusted)",
        subtitle="Total: $1.37 trillion across all travel segments",
        x="",
        y="Spending ($ billions)",
        fill="$B",
        caption="Source: U.S. Travel Association, Spring 2026 Forecast",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold", color="#1a1a2e", hjust=0.5),
        plot_subtitle=element_text(size=11, color="#555555", hjust=0.5, margin=[0, 0, 15, 0]),
        axis_text_y=element_text(size=12, color="#333333"),
        axis_text_x=element_text(size=10, color="#555555"),
        axis_title_x=element_text(size=11, color="#555555", margin=[8, 0, 0, 0]),
        axis_title_y=element_blank(),
        panel_grid_major_x=element_line(color="#e0e0e0", size=0.3),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        legend_position="none",
        plot_caption=element_text(size=8, color="#888888", hjust=1, margin=[8, 0, 0, 0]),
        plot_margin=[10, 20, 10, 10],
    )
    + scale_y_continuous(
        limits=[0, 1050],
        breaks=[0, 200, 400, 600, 800, 1000],
        labels=["$0B", "$200B", "$400B", "$600B", "$800B", "$1000B"],
    )
)

# ── Save ──────────────────────────────────────────────────────────────────
output_dir = Path(__file__).resolve().parent.parent / "images"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = str(output_dir / "one-hour-adventure_travel_spending.png")

ggsave(p, output_path, w=8, h=4.8, unit="in", dpi=150, scale=1.0)
print(f"\u2713 Saved: {output_path}")
