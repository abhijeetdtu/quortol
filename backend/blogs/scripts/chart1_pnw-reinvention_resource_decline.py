"""
Chart: What Was Lost — The Disappearing Resource Economy in Wahkiakum County, WA
Faceted bar chart: three paired metrics (before vs. after).
lets-plot 4.9.0 | 1200×720 px | 150 DPI | Colorblind-safe (blue/orange)
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "metric": [
        "Logging Jobs",
        "Logging Jobs",
        "Civilian Labor Force",
        "Civilian Labor Force",
        "Retirement-Age\nPop. Share",
        "Retirement-Age\nPop. Share",
    ],
    "period": [
        "1998", "2024",
        "1999", "2024",
        "2000", "2024",
    ],
    "period_type": [
        "Before", "After",
        "Before", "After",
        "Before", "After",
    ],
    "value": [
        160, 30,
        1957, 1242,
        25, 45,
    ],
    "label": [
        "160", "30",
        "1,957", "1,242",
        "25%", "45%",
    ],
})

metric_order = [
    "Logging Jobs",
    "Civilian Labor Force",
    "Retirement-Age\nPop. Share",
]
data["metric"] = pd.Categorical(
    data["metric"], categories=metric_order, ordered=True
)
data["period_type"] = pd.Categorical(
    data["period_type"], categories=["Before", "After"], ordered=True
)
data["period"] = pd.Categorical(
    data["period"], categories=["1998", "1999", "2000", "2024"], ordered=True
)

# ── Colorblind-safe palette ───────────────────────────────────────────
# Blue (Wong "Blue" #0072B2) for before, Orange (Wong "Orange" #E69F00) for after
fill_colors = {"Before": "#0072B2", "After": "#E69F00"}

# ── Build chart ───────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="period", y="value", fill="period_type"))
    + geom_bar(stat="identity", width=0.55, alpha=0.9, color="#333333", size=0.15)
    + facet_wrap(facets="metric", scales="free_y", ncol=3)
    + scale_fill_manual(
        values=fill_colors,
        guide=guide_legend(title=""),
    )
    + labs(
        title="What Was Lost: The Disappearing Resource Economy",
        subtitle="Wahkiakum County, WA \u2014 three measures of economic transformation",
        x="",
        y="",
        caption="Sources: Washington State employment data; U.S. Census Bureau via FRED; The Columbian",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(
            size=18, face="bold", hjust=0.5, margin=[0, 0, 6, 0], color="#1a1a1a"
        ),
        plot_subtitle=element_text(
            size=12, color="#555555", hjust=0.5, margin=[0, 0, 16, 0]
        ),
        axis_text_x=element_text(size=12, face="bold", color="#333333"),
        axis_text_y=element_text(size=10, color="#555555"),
        axis_title_y=element_text(size=11, color="#555555", margin=[0, 8, 0, 0]),
        axis_ticks_x=element_blank(),
        axis_ticks_y=element_blank(),
        plot_caption=element_text(
            size=9, color="#777777", hjust=0, margin=[12, 0, 0, 0]
        ),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.4),
        panel_spacing=25,
        strip_text=element_text(
            size=12, face="bold", hjust=0.5, color="#1a1a1a", margin=[0, 0, 6, 0]
        ),
        plot_background=element_rect(fill="#FFFFFF", color=None),
        plot_margin=[20, 20, 10, 20],
        legend_position="bottom",
        legend_direction="horizontal",
        legend_justification=0.5,
        legend_text=element_text(size=11, color="#333333"),
    )
    + geom_text(
        aes(label="label"),
        stat="identity",
        size=12,
        color="#333333",
        fontface="bold",
        vjust=-0.65,
        hjust=0.5,
    )
    # Ensure room for labels above bars (no bottom expansion, 18% top expansion)
    + scale_y_continuous(expand=[0, 0, 0.18, 0])
)

# ── Export PNG ────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "pnw-reinvention_resource_decline.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart saved to: {output_path}")
