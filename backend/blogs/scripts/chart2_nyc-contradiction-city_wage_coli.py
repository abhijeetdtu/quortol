#!/usr/bin/env python3
"""
Chart 2: The Wage Premium vs. The Cost Burden
Dual-axis grouped bar chart comparing mean hourly wages vs. cost of living
for major U.S. metro areas.

Sources: BLS OEWS May 2025; C2ER Cost of Living Index Q3 2025.

Note: lets-plot 4.9.0 does not natively support sec_axis. This chart uses
scaled COLI values plotted on the primary wage axis, with actual COLI index
values shown as bar labels and right-side annotations — a transparent
alternative that preserves all information without dual-axis distortion.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Colorblind-safe palette (Wong 2011) ─────────────────────────────────
WAGE_COLOR = "#4477AA"  # blue (matches project convention)
COLI_COLOR = "#D55E00"  # vermillion red — distinct from blue for all CB types

# ── Output paths ─────────────────────────────────────────────────────────
IMAGE_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = IMAGE_DIR / "nyc-contradiction-city_wage_coli.png"

# ── Data ─────────────────────────────────────────────────────────────────
metro_order = [
    "National Average",
    "Chicago-Naperville-Elgin",
    "Los Angeles-Long Beach-Anaheim",
    "New York-Newark-Jersey City",
]

df = pd.DataFrame({
    "metro": metro_order,
    "wage": [33.54, 34.42, 36.64, 41.50],
    "coli": [100.0, 120.0, 150.6, 232.5],
})

# ── Scale COLI onto wage axis ────────────────────────────────────────────
# max(wage) = 41.50, max(coli) = 232.5 → scale_factor ≈ 0.1785
scale_factor = df["wage"].max() / df["coli"].max()
df["scaled_coli"] = df["coli"] * scale_factor

# ── Melt to long form for grouped bars ───────────────────────────────────
df_melt = df.melt(
    id_vars=["metro", "coli"],
    value_vars=["wage", "scaled_coli"],
    var_name="metric",
    value_name="value",
)

df_melt["display_label"] = df_melt["metric"].map({
    "wage": "Mean Hourly Wage ($)",
    "scaled_coli": "Cost of Living Index",
})

# Preserve metro order as ordered categorical
df_melt["metro"] = pd.Categorical(
    df_melt["metro"], categories=metro_order, ordered=True,
)

# ── Bar labels: actual values shown on each bar ──────────────────────────
def format_label(row):
    if row["metric"] == "wage":
        return f"${row['value']:.2f}"
    # COLI — strip trailing .0 for clean display
    v = row["coli"]
    return f"{v:g}"

df_melt["bar_label"] = df_melt.apply(format_label, axis=1)

# ── Right-side COLI scale annotations (simulates secondary axis) ────────
coli_breaks = [100, 150, 200, 250]
right_ann = pd.DataFrame({
    "x": 4.4,
    "y": [b * scale_factor for b in coli_breaks],
    "label": [str(b) for b in coli_breaks],
})

# ── Theme (consistent with project style) ────────────────────────────────
LETS_PLOT_THEME = theme(
    plot_title=element_text(size=18, face="bold", hjust=0),
    plot_subtitle=element_text(size=11.5, hjust=0, color="#555555"),
    axis_title_x=element_text(size=12),
    axis_title_y=element_text(size=12, face="bold"),
    axis_text_x=element_text(size=10),
    axis_text_y=element_text(size=10),
    axis_ticks=element_blank(),
    plot_caption=element_text(size=8.5, color="#888888", hjust=0),
    panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
    panel_grid_major_x=element_blank(),
    panel_grid_minor=element_blank(),
    panel_background=element_rect(fill="#FAFAFA"),
    plot_background=element_rect(fill="white"),
    legend_position="bottom",
    legend_text=element_text(size=11),
    legend_title=element_blank(),
    plot_margin=[20, 65, 10, 20],  # extra right margin for COLI scale annotations
)

# ── Build chart ──────────────────────────────────────────────────────────
p = (
    ggplot(df_melt, aes(x="metro", y="value", fill="display_label"))
    + geom_bar(stat="identity", position="dodge", width=0.65)
    # Value labels on bars
    + geom_text(
        aes(label="bar_label"),
        position=position_dodge(width=0.65),
        vjust=-0.4,
        size=8.5,
        color="#333333",
        fontface="bold",
        show_legend=False,
    )
    # Right-side COLI break labels ("100", "150", "200", "250")
    + geom_text(
        data=right_ann,
        mapping=aes(x="x", y="y", label="label"),
        size=9,
        color=COLI_COLOR,
        hjust=0,
        fontface="bold",
        show_legend=False,
    )
    # Right-side COLI axis title
    + geom_text(
        x=4.55,
        y=24.5,
        label="Cost of Living Index\n(National Avg = 100)",
        size=9,
        color=COLI_COLOR,
        fontface="bold",
        hjust=0.5,
        show_legend=False,
    )
    # Fill colors
    + scale_fill_manual(
        values=[WAGE_COLOR, COLI_COLOR],
        labels=["Mean Hourly Wage ($)", "Cost of Living Index"],
    )
    # Y-axis with room for bar labels
    + scale_y_continuous(
        name="Mean Hourly Wage ($)",
        limits=[0, 54],
        breaks=[0, 10, 20, 30, 40, 50],
        expand=[0, 0],
    )
    # X-axis with extra expansion on right for COLI annotations
    + scale_x_discrete(expand=[0.08, 0.5])
    # Labels
    + labs(
        title="The Wage Premium vs. The Cost Burden",
        subtitle=(
            "NYC earns 24% more, but Manhattan costs 132% more "
            "than the national average"
        ),
        x="",
        y="",
        caption=(
            "Sources: BLS OEWS May 2025; C2ER Cost of Living Index Q3 2025. "
            "NYC wage is metro-wide; NYC COLI is for Manhattan."
        ),
    )
    + LETS_PLOT_THEME
)

# ── Save ─────────────────────────────────────────────────────────────────
ggsave(p, str(OUTPUT_PATH), w=1200, h=720, dpi=150, unit="px")

# ── Validate ─────────────────────────────────────────────────────────────
if OUTPUT_PATH.exists():
    from PIL import Image
    img = Image.open(OUTPUT_PATH)
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Chart saved to: {OUTPUT_PATH}")
    print(f"Dimensions: {img.width} x {img.height} px @ 150 DPI")
    print(f"File size: {size_kb:.1f} KB")
else:
    print(f"ERROR: Chart was not saved to {OUTPUT_PATH}")
    raise SystemExit(1)
