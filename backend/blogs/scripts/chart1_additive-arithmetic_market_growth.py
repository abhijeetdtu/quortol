#!/usr/bin/env python3
"""
Chart: Global Additive Manufacturing Market Revenue, 1995–2025
==============================================================
Line chart with filled area showing the growth of the 3D printing market.

Data source: Wohlers Reports 2001–2026, Wohlers Associates/ASTM International
Output: ../images/additive-arithmetic_market_growth.png  (1200 × 720 px, 150 DPI)
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA
# ============================================================================
df = pd.DataFrame({
    "year":   [1995, 2000, 2010, 2011, 2012, 2013, 2014, 2015, 2020, 2024, 2025],
    "revenue": [0.295, 0.7, 1.3, 1.7, 2.275, 3.07, 4.1, 5.165, 12.8, 21.9, 24.2],
})

# ============================================================================
# 2. STYLE CONSTANTS
# ============================================================================
BLUE = "#2563EB"
TEXT_COLOR = "#2C2C2C"
SOURCE_COLOR = "#888888"
GRID_COLOR = "#E0E0E0"
BG_COLOR = "#FFFFFF"

# ============================================================================
# 3. CREATE THE CHART
# ============================================================================
p = (
    ggplot(df, aes(x="year", y="revenue"))
    # Filled area under the curve (subtle transparency)
    + geom_area(fill=BLUE, alpha=0.12)
    # Solid line
    + geom_line(color=BLUE, size=1.5)
    # Data point markers (white-filled circles with blue stroke)
    + geom_point(shape=21, fill="white", color=BLUE, size=4, stroke=1.2)
    # Scales
    + scale_x_continuous(
        breaks=[1995, 2000, 2005, 2010, 2015, 2020, 2025],
        labels=["1995", "2000", "2005", "2010", "2015", "2020", "2025"],
    )
    + scale_y_continuous(
        breaks=[0, 5, 10, 15, 20, 25],
        labels=["$0B", "$5B", "$10B", "$15B", "$20B", "$25B"],
    )
    # Labels
    + labs(
        title="Global Additive Manufacturing Market Revenue, 1995–2025",
        x="Year",
        y="Revenue (US$ billions)",
        caption="Source: Wohlers Reports 2001–2026, Wohlers Associates/ASTM International",
    )
    # Minimal theme with subtle gridlines
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
        axis_title_x=element_text(size=12, color=TEXT_COLOR, margin=[8, 0, 0, 0]),
        axis_title_y=element_text(size=12, color=TEXT_COLOR, margin=[0, 8, 0, 0]),
        axis_text_x=element_text(size=11, color=TEXT_COLOR),
        axis_text_y=element_text(size=11, color=TEXT_COLOR),
        plot_caption=element_text(
            size=9, color=SOURCE_COLOR, hjust=0, face="italic",
            margin=[10, 0, 0, 0],
        ),
        plot_margin=[10, 15, 10, 10],
    )
)

# ============================================================================
# 4. SAVE  — 8 in × 4.8 in @ 150 DPI = 1200 × 720 px
# ============================================================================
script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)
output_png = images_dir / "additive-arithmetic_market_growth.png"

ggsave(p, str(output_png), dpi=150, w=8, h=4.8)

print(f"✓ Chart saved to {output_png}")
print(f"  Dimensions: {8 * 150} × {int(4.8 * 150)} px  @  150 DPI")
