#!/usr/bin/env python3
"""
Chart 1: Global Fiber Production, 1975–2030
Stacked area chart showing synthetic, cotton, and other natural fiber production
in million tonnes over time.

Sources:
  - Textile Exchange Materials Market Report 2025
  - UNCTAD Fibre Trade Report 2025
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "Year": [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023, 2024, 2030],
    "Synthetic": [10, 15, 18, 22, 28, 35, 42, 52, 66, 72, 89, 94, 120],
    "Cotton": [12, 14, 16, 18, 19, 20, 23, 24, 25, 26, 25, 24, 28],
    "Other Natural": [6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 10],
})

# Melt to long format for ggplot
df_long = df.melt(id_vars="Year", var_name="Fiber Type", value_name="Production")

# Set stacking order: bottom → top: Other Natural, Cotton, Synthetic
df_long["Fiber Type"] = pd.Categorical(
    df_long["Fiber Type"],
    categories=["Other Natural", "Cotton", "Synthetic"],
    ordered=True,
)

# ---------------------------------------------------------------------------
# Compute end-of-line label positions for the final year (2030)
# In a stacked area chart, each label sits at the vertical midpoint of its
# category's segment at the last year.
# ---------------------------------------------------------------------------
df_last = df_long[df_long["Year"] == 2030].sort_values("Fiber Type")
cum = 0
label_rows = []
for _, row in df_last.iterrows():
    mid = cum + row["Production"] / 2
    label_rows.append({
        "Year": 2030,
        "Fiber Type": row["Fiber Type"],
        "Production": row["Production"],
        "label_y": mid,
        "label_text": f"{row['Fiber Type']} {int(row['Production'])}",
    })
    cum += row["Production"]

df_labels = pd.DataFrame(label_rows)

# ---------------------------------------------------------------------------
# Build the chart
# ---------------------------------------------------------------------------
p = (
    ggplot()
    # Stacked areas
    + geom_area(
        data=df_long,
        mapping=aes(x="Year", y="Production", fill="Fiber Type"),
        position="stack",
        alpha=0.88,
    )
    # Value labels at the right edge
    + geom_text(
        data=df_labels,
        mapping=aes(x="Year", y="label_y", label="label_text"),
        hjust=0,
        nudge_x=1.8,
        size=11,
        family="sans-serif",
        color="#333333",
        fontface="bold",
    )
    # Colorblind-safe palette
    + scale_fill_manual(
        values={
            "Synthetic": "#006D6F",      # dark teal
            "Cotton": "#D4A017",          # warm amber
            "Other Natural": "#9CAF88",   # soft sage
        }
    )
    # X-axis: show "2030e" for the forecast year
    + scale_x_continuous(
        breaks=[1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024, 2030],
        labels=["1975", "1980", "1985", "1990", "1995", "2000", "2005", "2010", "2015", "2020", "2024", "2030e"],
    )
    # Y-axis
    + scale_y_continuous(
        limits=(0, 170),
        expand=(0, 0),
    )
    # Labels
    + labs(
        title="Global Fiber Production, 1975–2030",
        subtitle="Synthetic fibers now account for nearly three-quarters of total production",
        x="Year",
        y="Million Tonnes",
        caption="Sources: Textile Exchange Materials Market Report 2025; UNCTAD Fibre Trade Report 2025",
    )
    # Theme
    + theme_classic()
    + theme(
        plot_title=element_text(size=16, hjust=0.5, face="bold", family="sans-serif"),
        plot_subtitle=element_text(size=12, hjust=0.5, color="#555555", family="sans-serif"),
        axis_title_x=element_text(size=11, family="sans-serif"),
        axis_title_y=element_text(size=11, family="sans-serif"),
        axis_text_x=element_text(size=11, angle=45, hjust=1, family="sans-serif"),
        axis_text_y=element_text(size=11, family="sans-serif"),
        axis_line=element_line(color="#CCCCCC", size=0.5),
        axis_ticks=element_line(color="#CCCCCC", size=0.3),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.3),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        plot_background=element_blank(),
        panel_background=element_blank(),
        legend_position="right",
        legend_title=element_text(size=11, family="sans-serif", face="bold"),
        legend_text=element_text(size=11, family="sans-serif"),
        plot_caption=element_text(
            size=9, color="#888888", hjust=0.5, family="sans-serif",
        ),
        plot_margin=[10, 30, 10, 10],
    )
)

# ---------------------------------------------------------------------------
# Save — 1200 × 720 px at 150 DPI  →  8 × 4.8 inches
# ---------------------------------------------------------------------------
script_dir = Path(__file__).resolve().parent
out_dir = script_dir.parent / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "the-thread-of-power_fiber_production.png"

ggsave(p, str(out_path), w=8, h=4.8, unit="in", dpi=150)

# Verify
if out_path.exists():
    print(f"Saved: {out_path}")
    print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
    print(f"  Dimensions: 1200 × 720 px at 150 DPI")
else:
    print(f"ERROR: file was not created at {out_path}")
