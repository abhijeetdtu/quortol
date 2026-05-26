#!/usr/bin/env python3
"""
Chart: What the IPL Pays — Bench vs. Playing XI vs. Domestic Cricket
Output: ../images/ipl_bench_earnings_gap.png  (1200 × 720 px, 150 DPI)

Horizontal bar chart comparing annual earnings for three cricket
professional profiles in India, using a colorblind-safe palette.

Data:
  - IPL base price uncapped:  ₹30L (Sportstar, 2025)
  - IPL match fee:             ₹7.5L/match (ESPNcricinfo)
  - Domestic Ranji earnings:   ₹20L (Gully Cricket, GK365)
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA
# ============================================================================
df = pd.DataFrame({
    "category": [
        "IPL Uncapped Player\n(bench, 0 matches)",
        "IPL Uncapped Player\n(regular, 14 matches)",
        "Senior Domestic\nRanji Cricketer",
    ],
    "salary": [30_00_000, 1_35_00_000, 20_00_000],
})

# Add a formatted label column for annotations
def fmt_salary(val):
    """Format salary in lakh/crore notation."""
    if val >= 1_00_00_000:
        return f"₹{val / 1_00_00_000:.2f}Cr"
    else:
        return f"₹{val // 1_00_000:.0f}L"

df["label"] = df["salary"].apply(fmt_salary)

# ============================================================================
# 2. Y-AXIS ORDERING
# ============================================================================
# Horizontal bar chart: top row should be the first category in the data.
# In lets-plot, the first factor level appears at the bottom of the y-axis,
# so reverse the order to put "bench" on top.
category_order = df["category"].tolist()[::-1]  # domestic → regular → bench
df["category"] = pd.Categorical(
    df["category"],
    categories=category_order,
    ordered=True,
)

# ============================================================================
# 3. COLORBLIND-SAFE PALETTE
# ============================================================================
# Adapted from Okabe-Ito (Wong 2011). The three hues are distinguishable
# under common forms of colour vision deficiency.
bar_colors = {
    "IPL Uncapped Player\n(bench, 0 matches)":        "#00747A",   # deep teal
    "IPL Uncapped Player\n(regular, 14 matches)":      "#D4942A",   # warm amber
    "Senior Domestic\nRanji Cricketer":                "#7A8A8A",   # slate gray
}

# ============================================================================
# 4. BUILD THE PLOT
# ============================================================================

p = (
    ggplot(df, aes(x="salary", y="category", fill="category"))
    + geom_bar(stat="identity", width=0.55)

    # ---- Value labels on bars (inside, right-aligned) ----
    + geom_text(
        aes(label="label"),
        hjust=-0.15,
        size=11,
        color="#333333",
        family="sans",
    )

    # ---- Colour scale ----
    + scale_fill_manual(values=bar_colors, guide="none")

    # ---- Axes ----
    + scale_x_continuous(
        breaks=[0, 30_00_000, 60_00_000, 90_00_000, 1_20_00_000, 1_50_00_000],
        labels=[
            "₹0", "₹30L", "₹60L", "₹90L", "₹1.2Cr", "₹1.5Cr"
        ],
        limits=(0, 1_60_00_000),       # room for label on longest bar
        expand=[0, 0],
    )

    # ---- Labels & title ----
    + labs(
        title="What the IPL Pays — Bench vs. Playing XI vs. Domestic Cricket",
        subtitle="Annual earnings for an uncapped Indian player at base price",
        x="Annual Earnings (INR)",
        y="",
        caption=(
            "Sources: ESPNcricinfo (match fees), Sportstar (base price), "
            "Gully Cricket (domestic salaries), GK365 (MCA contracts)"
        ),
    )

    # ---- Theme ----
    + theme_minimal()
    + theme(
        # Y-axis: category labels
        axis_text_y       = element_text(size=12, color="#222222"),
        axis_text_x       = element_text(size=10, color="#555555"),
        axis_title_x      = element_text(size=12, color="#333333",
                                         margin=[8, 0, 0, 0]),

        # Title block
        plot_title        = element_text(size=18, face="bold",
                                         color="#1a1a1a", margin=[0, 0, 4, 0]),
        plot_subtitle     = element_text(size=13, color="#666666",
                                         margin=[0, 0, 16, 0]),
        plot_caption      = element_text(
            size=8, color="#999999", margin=[12, 0, 0, 0]
        ),

        # Grid lines — only horizontal (across the chart, not the bars)
        panel_grid_major_x = element_blank(),
        panel_grid_minor_x = element_blank(),
        panel_grid_major_y = element_line(color="#e6e6e6", size=0.35),
        panel_grid_minor_y = element_blank(),

        # Background — white
        panel_background   = element_blank(),
        plot_background    = element_blank(),

        # Margins (top, right, bottom, left)
        plot_margin       = [15, 25, 10, 15],
    )
)

# ============================================================================
# 5. SAVE PNG  — 1200 × 720 px @ 150 DPI  →  8 × 4.8 in
# ============================================================================
output_path = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "ipl_bench_earnings_gap.png"
)
ggsave(p, output_path, w=8, h=4.8, unit="in", dpi=150)

print(f"✓ Chart saved to {output_path}")
print(f"  Dimensions: 1200 × 720 px  @  150 DPI")
