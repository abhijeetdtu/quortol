#!/usr/bin/env python3
"""
Chart: Median Home Prices in the Catskills, 2019–2025
======================================================
Multi-line chart showing median home prices in three Catskills counties
(Sullivan, Greene, Ulster) compared against the U.S. national median.

Data source: Hudson Valley Pattern for Progress, 2025 Q4 & Annual Housing Report
Output: ../images/catskills-next-act_home_prices.png  (1200 × 720 px, 150 DPI)
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA  —  wide → long format for lets-plot
# ============================================================================
df_wide = pd.DataFrame({
    "year":     [2019, 2020,   2021,    2022, 2023, 2024,  2025],
    "Sullivan": [144.9, 199.05, 250,    275,  289,  324,   350],
    "Greene":   [196,   240,    287.825, 325,  315,  350,   379],
    "Ulster":   [248,   285,    339,     370,  400,  442.6, 450],
})

df = df_wide.melt(id_vars=["year"], var_name="county", value_name="price_k")

# Single-row DataFrame for the US median annotation label
us_median_label = pd.DataFrame({
    "x": [2024.7],
    "y": [352],
    "label": ["U.S. Median ~$340K (2024)"],
})

# ============================================================================
# 2. COLOR PALETTE  —  colorblind-safe (Blue / Orange / Teal)
# ============================================================================
SULLIVAN = "#0077BB"
GREENE   = "#EE7733"
ULSTER   = "#009988"
GRAY     = "#999999"
TEXT_COLOR = "#2C2C2C"
SOURCE_COLOR = "#888888"
GRID_COLOR   = "#E0E0E0"
BG_COLOR     = "#F5F5F5"

# ============================================================================
# 3. CREATE THE CHART
# ============================================================================
p = (
    ggplot(df, aes(x="year", y="price_k", color="county"))
    # --- US median reference line ---
    + geom_hline(
        yintercept=340,
        linetype="dashed",
        color=GRAY,
        size=0.9,
    )
    # --- County lines (thick, 3pt) ---
    + geom_line(size=3)
    # --- Data point markers (white fill + colored stroke) ---
    + geom_point(
        shape=21,
        fill="white",
        size=4,
        stroke=1.5,
    )
    # --- US median annotation ---
    + geom_text(
        data=us_median_label,
        mapping=aes(x="x", y="y", label="label"),
        color=GRAY,
        size=9.5,
        hjust=1,
        family="sans-serif",
        fontface="italic",
    )
    # --- Scales ---
    + scale_x_continuous(
        breaks=[2019, 2020, 2021, 2022, 2023, 2024, 2025],
        labels=["2019", "2020", "2021", "2022", "2023", "2024", "2025"],
    )
    + scale_y_continuous(
        breaks=[150, 200, 250, 300, 350, 400, 450],
        labels=["$150K", "$200K", "$250K", "$300K", "$350K", "$400K", "$450K"],
    )
    + scale_color_manual(
        values=[SULLIVAN, GREENE, ULSTER],
        breaks=["Sullivan", "Greene", "Ulster"],
    )
    # --- Labels ---
    + labs(
        title="Median Home Prices in the Catskills, 2019–2025",
        x="Year",
        y="Median Sale Price ($ thousands)",
        color="County",
        caption="Source: Hudson Valley Pattern for Progress",
    )
    # --- Theme ---
    + theme_minimal()
    + theme(
        plot_background=element_rect(fill=BG_COLOR, color=None),
        panel_grid_major_x=element_line(color=GRID_COLOR, size=0.4),
        panel_grid_major_y=element_line(color=GRID_COLOR, size=0.4),
        panel_grid_minor=element_blank(),
        axis_line=element_blank(),
        axis_ticks=element_blank(),
        plot_title=element_text(
            size=20, face="bold", color=TEXT_COLOR, hjust=0,
            margin=[10, 0, 8, 0],
        ),
        axis_title_x=element_text(
            size=12, color=TEXT_COLOR, margin=[8, 0, 0, 0],
        ),
        axis_title_y=element_text(
            size=12, color=TEXT_COLOR, margin=[0, 8, 0, 0],
        ),
        axis_text_x=element_text(size=11, color=TEXT_COLOR),
        axis_text_y=element_text(size=11, color=TEXT_COLOR),
        plot_caption=element_text(
            size=9, color=SOURCE_COLOR, hjust=0, face="italic",
            margin=[10, 0, 0, 0],
        ),
        legend_position="right",
        legend_title=element_text(size=12, color=TEXT_COLOR, face="bold"),
        legend_text=element_text(size=11, color=TEXT_COLOR),
        plot_margin=[10, 15, 10, 10],
    )
)

# ============================================================================
# 4. SAVE  —  8 in × 4.8 in @ 150 DPI = 1200 × 720 px
# ============================================================================
script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)
output_png = images_dir / "catskills-next-act_home_prices.png"

ggsave(p, str(output_png), dpi=150, w=8, h=4.8)

print(f"✓ Chart saved to {output_png}")
print(f"  Dimensions: {8 * 150} × {int(4.8 * 150)} px  @  150 DPI")
