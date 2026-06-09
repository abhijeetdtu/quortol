"""
Chart 2: Additive Manufacturing Revenue by Segment, 2025
Horizontal bar chart showing breakdown of $24.2B global AM revenue.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe palette.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data ---
data = pd.DataFrame({
    "segment": ["Printing Services", "System Sales & Servicing", "Materials", "Software"],
    "revenue": [11.7, 6.2, 4.9, 1.4],
    "pct": [48, 26, 20, 6],
})

# Sort ascending so largest bar appears at top after coord_flip
data["segment"] = pd.Categorical(
    data["segment"],
    categories=data.sort_values("revenue", ascending=True)["segment"].tolist(),
    ordered=True,
)

# Build label: dollar amount + percentage
data["label"] = data.apply(lambda r: f"${r['revenue']}B ({r['pct']}%)", axis=1)

# Colorblind-safe palette (distinct hues)
segment_colors = {
    "Printing Services": "#2563EB",
    "System Sales & Servicing": "#059669",
    "Materials": "#D97706",
    "Software": "#DC2626",
}

# --- Build chart ---
p = (
    ggplot(data, aes(x="segment", y="revenue", fill="segment"))
    + geom_bar(stat="identity", width=0.65, color="white", size=0.3)
    + geom_text(
        aes(label="label"),
        nudge_y=0.35,
        size=10.5,
        color="#222222",
        fontface="bold",
        hjust=0,
    )
    + scale_fill_manual(values=segment_colors)
    + scale_y_continuous(
        limits=[0, 14.5],
        breaks=[0, 2, 4, 6, 8, 10, 12, 14],
        expand=[0, 0],
    )
    + coord_flip()
    + labs(
        title="Additive Manufacturing Revenue by Segment, 2025",
        subtitle="Total: $24.2 Billion",
        x="",
        y="USD Billions",
        caption="Source: Wohlers Report 2026, Wohlers Associates/ASTM International",
        fill="",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=12, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_title_y=element_blank(),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=12, face="bold"),
        plot_caption=element_text(size=9, color="#888888", hjust=0, margin=[12, 0, 0, 0]),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 20, 10, 10],
        legend_position="none",
    )
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "additive-arithmetic_revenue_segments.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart saved to: {output_path}")
