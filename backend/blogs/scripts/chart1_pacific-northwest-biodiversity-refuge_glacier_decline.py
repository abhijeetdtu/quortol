#!/usr/bin/env python3
"""
Chart: Mount Rainier Glacier Decline (1896-2021)
================================================
Dual-axis line chart showing glacier area (km²) and ice volume (km³) over
125 years of observed retreat.

Output: PNG (1200×720 px @ 150 DPI)
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Paths -----------------------------------------------------------------
OUTPUT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs")
IMAGE_DIR = OUTPUT_DIR / "images"
SCRIPT_DIR = OUTPUT_DIR / "scripts"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = str(
    IMAGE_DIR / "pacific-northwest-biodiversity-refuge_glacier_decline.png"
)

# ==========================================================================
# 1. DATA  (Beason et al., 2023 — NPS Natural Resource Report NPS/MORA/NRR-2023/2524)
# ==========================================================================
df = pd.DataFrame({
    "year":   [1896, 1913, 1971, 1994, 2009, 2015, 2021],
    "area":   [129.3076, 111.9504, 91.5827, 89.8820, 80.2221, 78.7580, 75.4956],
    "volume": [7.2586, 5.7608, 4.5255, 4.4631, 3.8900, 3.6915, 3.5162],
})

# Percentage losses from 1896 baseline
area_loss_pct = (df["area"].iloc[0] - df["area"].iloc[-1]) / df["area"].iloc[0] * 100
vol_loss_pct  = (df["volume"].iloc[0] - df["volume"].iloc[-1]) / df["volume"].iloc[0] * 100

# Colourblind-safe palette
AREA_COLOR   = "#0072B2"   # blue
VOLUME_COLOR = "#D55E00"   # orange-red

# ==========================================================================
# 2. ANNOTATION DATAFRAMES
# ==========================================================================
# Area annotations (on the area y-scale)
area_ann = pd.DataFrame({
    "x": [1896, 2021],
    "y": [df["area"].iloc[0], df["area"].iloc[-1]],
    "label": [
        "Glacier Area",
        f"\u2212{area_loss_pct:.1f}%",
    ],
    "hj": [1.05, -0.2],
    "vj": [-1.2, 0.5],
})

# Volume annotations (on the volume y-scale)
vol_ann = pd.DataFrame({
    "x": [1896, 2021],
    "y": [df["volume"].iloc[0], df["volume"].iloc[-1]],
    "label": [
        "Ice Volume",
        f"\u2212{vol_loss_pct:.1f}%",
    ],
    "hj": [1.05, -0.2],
    "vj": [1.6, 1.5],
})

# ==========================================================================
# 3. COMMON THEME SHARED BY BOTH PLOTS
# ==========================================================================
base_theme = theme_minimal() + theme(
    plot_background=element_rect(fill="white", color=None),
    panel_background=element_rect(fill="white", color=None),
    # Subtle horizontal grid lines only
    panel_grid_major_x=element_blank(),
    panel_grid_major_y=element_line(color="#EEEEEE", size=0.4),
    panel_grid_minor_x=element_blank(),
    panel_grid_minor_y=element_blank(),
    # Axis ticks and lines
    axis_ticks=element_line(color="#CCCCCC", size=0.3),
    axis_ticks_length=4,
    axis_line_x=element_line(color="#CCCCCC", size=0.3),
    axis_line_y=element_line(color="#CCCCCC", size=0.3),
    # Axis text
    axis_text_x=element_text(size=11, color="#444444"),
    axis_text_y=element_text(size=10, color="#444444"),
    # Title defaults (will be overridden at ggbunch level)
    plot_title=element_text(
        size=20, face="bold", hjust=0.0, color="#222222",
    ),
    plot_subtitle=element_text(
        size=12, hjust=0.0, color="#666666",
    ),
    plot_caption=element_text(
        size=8, hjust=0.0, color="#999999",
    ),
)

# ==========================================================================
# 4. PLOT 1 — AREA (primary left axis)
# ==========================================================================
p1 = (
    ggplot(df, aes(x="year", y="area"))
    + geom_line(color=AREA_COLOR, size=1.5)
    + geom_point(color=AREA_COLOR, size=3.5)
    # Annotation: area line label
    + geom_text(
        aes(x="x", y="y", label="label", hjust="hj", vjust="vj"),
        data=area_ann,
        color=AREA_COLOR,
        size=9,
    )
    + scale_x_continuous(
        breaks=[1896, 1913, 1971, 1994, 2009, 2015, 2021],
        expand=[0.05, 0],
    )
    + scale_y_continuous(
        name="Glacier Area (km\u00b2)",
        position="left",
        limits=[50, 145],
        breaks=[50, 60, 70, 80, 90, 100, 110, 120, 130, 140],
    )
    + labs(x="")
    + base_theme
    + theme(
        axis_title_y=element_text(
            size=12, color=AREA_COLOR, face="bold",
        ),
    )
)

# ==========================================================================
# 5. PLOT 2 — VOLUME (secondary right axis) overlaid on plot 1
# ==========================================================================
p2 = (
    ggplot(df, aes(x="year", y="volume"))
    + geom_line(color=VOLUME_COLOR, size=1.5)
    + geom_point(color=VOLUME_COLOR, size=3.5)
    # Annotation: volume line label
    + geom_text(
        aes(x="x", y="y", label="label", hjust="hj", vjust="vj"),
        data=vol_ann,
        color=VOLUME_COLOR,
        size=9,
    )
    + scale_x_continuous(
        breaks=[1896, 1913, 1971, 1994, 2009, 2015, 2021],
        expand=[0.05, 0],
    )
    + scale_y_continuous(
        name="Ice Volume (km\u00b3)",
        position="right",
        limits=[2.5, 8.5],
        breaks=[2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5],
    )
    + labs(x="", y="")
    + base_theme
    + theme(
        axis_title_y=element_text(
            size=12, color=VOLUME_COLOR, face="bold",
        ),
        # Hide x-axis elements from overlay (p1 provides them)
        axis_text_x=element_blank(),
        axis_title_x=element_blank(),
        axis_ticks_x=element_blank(),
        axis_line_x=element_blank(),
        # Transparent background so plot 1 shows through
        panel_background=element_rect(fill="transparent", color=None),
        plot_background=element_rect(fill="transparent", color=None),
        # Suppress grid lines in overlay
        panel_grid_major_y=element_blank(),
        # Hide global elements overlay
        plot_caption=element_blank(),
        plot_title=element_blank(),
        plot_subtitle=element_blank(),
    )
)

# ==========================================================================
# 6. COMBINE VIA GGBUNCH  +  GLOBAL TITLES
# ==========================================================================
combined = (
    ggbunch([p1, p2], [(0.0, 0.0, 1.0, 1.0), (0.0, 0.0, 1.0, 1.0)])
    + ggtitle("Mount Rainier Glaciers: 125 Years of Decline")
    + labs(
        subtitle=(
            f"Area lost: {area_loss_pct:.1f}% since 1896"
            f"  |  Volume lost: {vol_loss_pct:.1f}% since 1896"
        ),
        caption=(
            "Source: NPS Natural Resource Report NPS/MORA/NRR-2023/2524"
        ),
    )
    + theme(
        plot_background=element_rect(fill="white", color=None),
        plot_title=element_text(
            size=20, face="bold", hjust=0.0, color="#222222",
        ),
        plot_subtitle=element_text(
            size=12, hjust=0.0, color="#666666",
        ),
        plot_caption=element_text(
            size=8, hjust=0.0, color="#999999",
        ),
    )
    + ggsize(1200, 720)
)

# ==========================================================================
# 7. SAVE PNG  (1200×720 px @ 150 DPI)
# ==========================================================================
saved_path = ggsave(
    combined,
    OUTPUT_PATH,
    w=1200,
    h=720,
    unit="px",
    dpi=150,
)
print(f"✓ Chart saved → {saved_path}")

# Quick sanity check
import os
file_size = os.path.getsize(OUTPUT_PATH)
print(f"  File size: {file_size:,} bytes")
print(f"  Dimensions: 1200 × 720 px @ 150 DPI")
print(f"  Area loss: {area_loss_pct:.1f}% | Volume loss: {vol_loss_pct:.1f}%")
