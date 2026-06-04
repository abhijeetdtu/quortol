#!/usr/bin/env python3
"""
Chart 3: Smart Textiles Market, 2025–2030
========================================
Stacked vertical bar chart showing projected market growth by application
segment for the global smart textiles industry.

Data sources:
  - MarketsandMarkets Smart Textiles Market Report 2025-2030
  - Grand View Research Smart Fabrics Market 2030
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------
script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_png = images_dir / "the-thread-of-power_smart_textiles_market.png"

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
# The "Total" column from the source includes minor application segments
# beyond the three shown here.  We preserve the official total for labels
# and add a subtle "Other" segment so the stacked bar reaches that total.
df = pd.DataFrame({
    "Year":                [2025, 2026, 2027, 2028, 2029, 2030],
    "Sensing":             [1.21, 1.41, 1.64, 1.91, 2.21, 2.56],
    "Energy Harvesting":   [0.43, 0.51, 0.60, 0.71, 0.83, 0.97],
    "Luminescence &\nAesthetics":  [0.77, 0.90, 1.04, 1.21, 1.41, 1.63],
})

# Official totals from source (includes segments not broken out)
df["Total_Official"] = [2.41, 2.82, 3.29, 3.83, 4.45, 5.56]

# Compute "Other" as the difference (rounded to avoid floating-point noise)
df["Other"] = (
    df["Total_Official"]
    - df["Sensing"]
    - df["Energy Harvesting"]
    - df["Luminescence &\nAesthetics"]
).round(2)

# Melt to long format for ggplot
df_long = df.melt(
    id_vars=["Year", "Total_Official"],
    var_name="Segment",
    value_name="Value",
)

# Keep only the four segments used for stacking
df_long = df_long[
    df_long["Segment"].isin([
        "Sensing",
        "Energy Harvesting",
        "Luminescence &\nAesthetics",
        "Other",
    ])
]

# Stacking order: bottom → top
segment_order = [
    "Other",
    "Energy Harvesting",
    "Luminescence &\nAesthetics",
    "Sensing",
]
df_long["Segment"] = pd.Categorical(
    df_long["Segment"],
    categories=segment_order,
    ordered=True,
)

# Colorblind-safe palette (Paul Tol scheme) + light gray for "Other"
colors = {
    "Sensing":              "#0072B2",   # blue
    "Energy Harvesting":    "#E69F00",   # orange
    "Luminescence &\nAesthetics": "#CC79A7",   # purple
    "Other":                "#C8C8C8",   # light gray
}

# ---------------------------------------------------------------------------
# CAGR annotation — small inset in the upper‑right corner
# ---------------------------------------------------------------------------
df_cagr = pd.DataFrame({
    "x":      [2029.15],
    "y":      [6.25],
    "label":  ["▲  CAGR 18.2%\n2025 – 2030"],
})

# ---------------------------------------------------------------------------
# Build the chart
# ---------------------------------------------------------------------------
p = (
    ggplot()
    # ── Stacked bars ──────────────────────────────────────────────────────
    + geom_bar(
        data=df_long,
        mapping=aes(x="Year", y="Value", fill="Segment"),
        stat="identity",
        position="stack",
        width=0.65,
        color="white",
        size=0.3,
    )
    # ── Total value labels on top of each bar ─────────────────────────────
    + geom_text(
        data=df,
        mapping=aes(x="Year", y="Total_Official"),
        label=[f"{v:.2f}" for v in df["Total_Official"]],
        nudge_y=0.18,
        size=11,
        family="sans-serif",
        color="#222222",
        fontface="bold",
        hjust=0.5,
        vjust=0,
    )
    # ── CAGR annotation ──────────────────────────────────────────────────
    + geom_label(
        data=df_cagr,
        mapping=aes(x="x", y="y", label="label"),
        fill="#F5F5F5",
        color="#333333",
        size=9,
        family="sans-serif",
        fontface="bold",
        hjust=1,
        vjust=1,
        label_size=0.5,
    )
    # ── Fill scale ────────────────────────────────────────────────────────
    + scale_fill_manual(values=colors)
    # ── X-axis (discrete year labels) ─────────────────────────────────────
    + scale_x_continuous(
        breaks=[2025, 2026, 2027, 2028, 2029, 2030],
        labels=["2025", "2026", "2027", "2028", "2029", "2030"],
    )
    # ── Y-axis ────────────────────────────────────────────────────────────
    + scale_y_continuous(
        limits=(0, 6.8),
        expand=(0, 0),
        breaks=[0, 1, 2, 3, 4, 5, 6],
    )
    # ── Titles and labels ─────────────────────────────────────────────────
    + labs(
        title    ="Smart Textiles Market, 2025–2030",
        subtitle ="Projected to grow from $2.4 billion to $5.6 billion at 18.2% CAGR",
        x        ="Year",
        y        ="USD Billion",
        caption  ="Sources: MarketsandMarkets (2025); Grand View Research (2023)",
    )
    # ── Theme ─────────────────────────────────────────────────────────────
    + theme_classic()
    + theme(
        plot_title          =element_text(size=16, hjust=0.5, face="bold",
                                          family="sans-serif"),
        plot_subtitle       =element_text(size=12, hjust=0.5, color="#555555",
                                          family="sans-serif"),
        axis_title_x        =element_text(size=11, family="sans-serif"),
        axis_title_y        =element_text(size=11, family="sans-serif"),
        axis_text_x         =element_text(size=11, family="sans-serif"),
        axis_text_y         =element_text(size=11, family="sans-serif"),
        axis_line           =element_line(color="#CCCCCC", size=0.5),
        axis_ticks          =element_line(color="#CCCCCC", size=0.3),
        panel_grid_major_y  =element_line(color="#E8E8E8", size=0.3),
        panel_grid_major_x  =element_blank(),
        panel_grid_minor    =element_blank(),
        plot_background     =element_blank(),
        panel_background    =element_blank(),
        legend_position     ="right",
        legend_title        =element_text(size=11, family="sans-serif",
                                          face="bold"),
        legend_text         =element_text(size=11, family="sans-serif"),
        plot_caption        =element_text(size=9, color="#888888",
                                          hjust=0.5, family="sans-serif"),
        plot_margin         =[10, 30, 10, 10],
    )
)

# ---------------------------------------------------------------------------
# Save — 1200 × 720 px at 150 DPI  →  8 × 4.8 inches
# ---------------------------------------------------------------------------
ggsave(p, str(output_png), w=8, h=4.8, unit="in", dpi=150)

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
if output_png.exists():
    from PIL import Image
    size_kb = output_png.stat().st_size / 1024
    with Image.open(output_png) as img:
        actual_size = img.size
    print(f"Saved: {output_png}")
    print(f"  File size:  {size_kb:.1f} KB")
    print(f"  Dimensions: {actual_size[0]} × {actual_size[1]} px @ 150 DPI")
else:
    print(f"ERROR: file was not created at {output_png}")
