#!/usr/bin/env python3
"""
Horizontal faceted bar chart: One Year of NYC Congestion Pricing — What Changed.
Uses lets-plot 4.9.0+.

Option A: two-panel faceted chart
  - Left panel: percentage-based metrics (4 horizontal bars)
  - Right panel: revenue & investment metrics (2 horizontal bars)

Data source: MTA Congestion Pricing One-Year Anniversary Report, January 2026.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────

df = pd.DataFrame({
    "metric": [
        # Percentage panel — order from bottom to top
        "Weekend subway ridership increase",
        "Subway ridership increase (entering CRZ)",
        "Express bus ridership increase",
        "Traffic reduction in CRZ",
        # Revenue panel — order from bottom to top
        "Net Revenue (Year 1)",
        "Transit Projects Enabled",
    ],
    "value": [
        # Percentage panel
        12,
        9,
        7.8,
        -11,
        # Revenue panel (in $billions for consistent axis scaling)
        0.55,
        15,
    ],
    "value_label": [
        "+12%",
        "+9%",
        "+7.8%",
        "-11%",
        "$550M",
        "$15B",
    ],
    "category": [
        "Transit",
        "Transit",
        "Transit",
        "Traffic",
        "Revenue",
        "Revenue",
    ],
    "panel": [
        "Percentage Change",
        "Percentage Change",
        "Percentage Change",
        "Percentage Change",
        "Revenue & Investment",
        "Revenue & Investment",
    ],
})

# ── Factor ordering ───────────────────────────────────────────────────────────

# Panel order (left / right in facet_wrap)
df["panel"] = pd.Categorical(
    df["panel"],
    categories=["Percentage Change", "Revenue & Investment"],
    ordered=True,
)

# Metric order (y-axis: first = bottom)
df["metric"] = pd.Categorical(
    df["metric"],
    categories=df["metric"].tolist(),  # preserves order above
    ordered=True,
)

# Position value labels: negative values → place to the left, positive → right
df["label_x"] = df["value"].apply(
    lambda v: v - 2.0 if v < 0 else v + 0.8
)
df["hjust"] = df["value"].apply(lambda v: 1 if v < 0 else 0)

# ── Color palette (colorblind-safe — Okabe-Ito) ──────────────────────────────

COLOR_MAP = {
    "Traffic": "#009E73",  # bluish-green
    "Transit": "#0072B2",  # blue
    "Revenue": "#E69F00",  # orange
}

# ── Build chart ───────────────────────────────────────────────────────────────

p = (
    ggplot(df, aes(x="value", y="metric", fill="category"))
    + geom_bar(stat="identity", width=0.65, color="white", size=0.3)
    # Value labels at computed positions
    + geom_text(
        aes(label="value_label", x="label_x", hjust="hjust"),
        size=11,
        color="#333333",
        family="sans-serif",
    )
    # Facet into two panels with independent scales
    + facet_wrap(facets="panel", scales="free", ncol=2)
    # Colorblind-safe fill
    + scale_fill_manual(values=COLOR_MAP, name="Category")
    # Expand axis slightly so labels aren't clipped
    + scale_x_continuous(expand=[0.2, 0])
    # Labels / title
    + labs(
        title="One Year of Congestion Pricing: What Changed",
        subtitle="January 5, 2025 — January 5, 2026",
        x="",
        y="",
        caption=(
            "Source: MTA, Governor's Office, January 2026. "
            "27M fewer vehicles is cumulative vs. 2024 baseline."
        ),
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0.5),
        plot_subtitle=element_text(
            size=13, hjust=0.5, color="#555555", margin=[0, 0, 18, 0]
        ),
        plot_caption=element_text(
            size=9, color="#888888", hjust=0, margin=[12, 0, 0, 0]
        ),
        axis_text_y=element_text(size=11),
        axis_text_x=element_text(size=10, color="#666666"),
        axis_ticks=element_blank(),
        panel_grid_major_y=element_blank(),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.35),
        strip_text=element_text(size=13, face="bold"),
        strip_background=element_rect(fill="#F0F0F0"),
        legend_position="bottom",
        legend_direction="horizontal",
        legend_title=element_text(size=11),
        legend_text=element_text(size=11),
        panel_spacing=25,
        plot_margin=[15, 20, 10, 15],
    )
)

# ── Save ──────────────────────────────────────────────────────────────────────

script_dir = Path(__file__).resolve().parent
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

png_path = images_dir / "nyc-contradiction-city_congestion_pricing.png"

ggsave(p, str(png_path), w=1200, h=720, unit="px", dpi=150)

print(f"Chart saved to: {png_path.resolve()}")
