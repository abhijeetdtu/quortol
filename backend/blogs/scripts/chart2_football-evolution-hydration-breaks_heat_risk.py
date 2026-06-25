#!/usr/bin/env python3
"""
Chart 2: Heat Risk at 2026 World Cup Host Cities
=================================================
Horizontal grouped bar chart showing percentage of June/July days where
Wet Bulb Globe Temperature (WBGT) exceeds 28°C — the threshold for match
postponement. Two scenarios: average year and hot year.

Data source: Mullan et al. (2025), Queen's University Belfast /
International Journal of Biometeorology

Output: ../images/football-evolution-hydration-breaks_heat_risk.png
(1200 × 720 px, 150 DPI, colorblind-safe palette)
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA — Wide format, then reshape to long for grouped bars
# ============================================================================

wide = pd.DataFrame({
    "city": [
        "Miami", "Dallas", "Houston", "Monterrey", "Kansas City",
        "Philadelphia", "Boston", "New York", "Atlanta", "Los Angeles",
        "San Francisco", "Seattle", "Toronto", "Vancouver", "Mexico City",
    ],
    "avg_year": [85, 82, 80, 55, 35, 30, 25, 22, 18, 5, 3, 2, 1, 0, 0],
    "hot_year": [95, 93, 91, 72, 58, 52, 48, 45, 40, 15, 10, 8, 5, 2, 1],
})

# Melt to long format: city | type | percentage
df = wide.melt(
    id_vars=["city"],
    value_vars=["avg_year", "hot_year"],
    var_name="type",
    value_name="percentage",
).replace({"type": {"avg_year": "Average Year", "hot_year": "Hot Year"}})

# Sort cities by avg_year ascending so hottest city appears at the top
# (first factor level = bottom of y-axis, last level = top)
city_order = wide.sort_values("avg_year", ascending=True)["city"].tolist()
df["city"] = pd.Categorical(df["city"], categories=city_order, ordered=True)

# Keep the type order consistent for the legend
df["type"] = pd.Categorical(
    df["type"], categories=["Average Year", "Hot Year"], ordered=True
)

# ============================================================================
# 2. COLORBLIND-SAFE PALETTE
# ============================================================================
# #4472C4 (blue)  — distinguishable for all common color vision deficiencies
# #E87722 (orange) — distinguishable from blue even in grayscale reproduction

fill_colors = {"Average Year": "#4472C4", "Hot Year": "#E87722"}

# ============================================================================
# 3. ANNOTATION DATAFRAME for the reference line label
# ============================================================================
ref_label = pd.DataFrame({"city": ["Miami"], "x": [53], "label": ["Half of days"]})

# ============================================================================
# 4. BUILD CHART
# ============================================================================

p = (
    ggplot(df, aes(y="city", x="percentage", fill="type"))
    # --- Bars ---
    + geom_bar(stat="identity", position=position_dodge(width=0.75), width=0.65)
    # --- Color ---
    + scale_fill_manual(values=fill_colors)
    # --- Axes ---
    + scale_x_continuous(
        limits=[0, 108],
        breaks=[0, 20, 40, 60, 80, 100],
        expand=[0, 0],
    )
    # --- Vertical reference line at 50 % ---
    + geom_vline(xintercept=50, linetype="dashed", color="#444444", size=0.6)
    + geom_text(
        aes(y="city", x="x", label="label"),
        data=ref_label,
        hjust=0,
        vjust=-0.4,
        size=9,
        color="#444444",
        fontface="italic",
    )
    # --- Labels ---
    + labs(
        title="Heat Risk at 2026 World Cup Host Cities",
        subtitle=(
            "Percentage of June/July days where WBGT exceeds 28°C — "
            "the threshold for match postponement"
        ),
        x="Percentage of days",
        y="",
        fill="",
        caption=(
            "Source: Mullan et al. (2025), Queen's University Belfast / "
            "International Journal of Biometeorology\n"
            "14 of 16 host cities could experience dangerous heat. "
            "Miami and Monterrey, which lack air-conditioned stadiums, "
            "face the greatest risk."
        ),
    )
    # --- Theme ---
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(
            size=11, color="#555555", hjust=0, margin=[0, 0, 16, 0]
        ),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_title_y=element_blank(),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11, face="bold"),
        plot_caption=element_text(
            size=8.5, color="#666666", hjust=0, margin=[12, 0, 0, 0]
        ),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 25, 10, 10],
        legend_position="bottom",
        legend_direction="horizontal",
        legend_text=element_text(size=11),
    )
)

# ============================================================================
# 5. SAVE
# ============================================================================

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "football-evolution-hydration-breaks_heat_risk.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart saved to: {output_path}")
