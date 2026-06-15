"""
Chart 1: Micro-Adventure Behavioral Data
Horizontal bar chart showing what Americans do with a free hour.
Colorblind-safe sequential blue palette.
"""
from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "Metric": [
        "Feel proud after 1-hour micro-adventure",
        "Prefer walk/easy hike near home",
        "Would travel 1\u20133 miles from home",
        "Feel guilty/anxious staying inside",
        "Mental health is primary motivation (under $50K)",
        "Friend asking would make them go",
        "Spend free hour scrolling on phone",
    ],
    "Percentage": [88.0, 72.0, 45.0, 44.0, 42.0, 33.0, 32.5],
})

# Order from lowest → highest so coord_flip shows highest at the top
metric_order = data.sort_values("Percentage", ascending=True)["Metric"].tolist()
data["Metric"] = pd.Categorical(data["Metric"], categories=metric_order, ordered=True)

# ── Plot ──────────────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="Metric", y="Percentage", fill="Percentage"))
    + geom_bar(stat="identity", width=0.7, color="#ffffff", size=0.3)
    + geom_text(
        aes(label="Percentage"),
        stat="identity",
        nudge_x=0.18,
        size=11,
        color="#1a1a2e",
        family="sans-serif",
        fontface="bold",
        va="middle",
        ha="left",
        format=".0f",
    )
    + scale_fill_gradient(low="#deebf7", high="#08306b")
    + coord_flip()
    + labs(
        title="The Micro-Adventure Data: What Americans Do (and Don't Do) With a Free Hour",
        subtitle="Survey of 1,000 U.S. adults \u2014 percentage who agree with each statement",
        x="",
        y="% of respondents",
        fill="%",
        caption="Source: Retrospec/Stacker survey of 1,000 U.S. adults, Jan. 2026",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold", color="#1a1a2e", hjust=0.5),
        plot_subtitle=element_text(size=11, color="#555555", hjust=0.5, margin=[0, 0, 15, 0]),
        axis_text_y=element_text(size=11, color="#333333"),
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
    + scale_y_continuous(limits=[0, 100], breaks=[0, 20, 40, 60, 80, 100])
)

# ── Save ──────────────────────────────────────────────────────────────────
output_dir = Path(__file__).resolve().parent.parent / "images"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = str(output_dir / "one-hour-adventure_behavioral_data.png")

ggsave(p, output_path, w=8, h=4.8, unit="in", dpi=150, scale=1.0)
print(f"\u2713 Saved: {output_path}")
