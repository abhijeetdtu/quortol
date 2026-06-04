#!/usr/bin/env python3
"""
Chart: The Biggest Living Organisms — Age and Height
====================================================
Horizontal bar chart with two panels comparing the age and physical
stature of five contenders for "biggest living organism on Earth."

Output: PNG (1200×800 px @ 150 DPI)
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

OUTPUT_PATH = str(IMAGE_DIR / "biggest-living-organism_age_length.png")

# --- Color map (colourblind-safe) -----------------------------------------
COLORS = {
    "Armillaria ostoyae": "#D55E00",
    "Pando": "#0072B2",
    "Posidonia australis": "#009E73",
    "General Sherman": "#56B4E9",
    "Blue Whale": "#CC79A7",
}

# ==========================================================================
# 1. AGE DATA  (sorted ascending so largest bar sits at top of the chart)
# ==========================================================================
age_order = [
    "Blue Whale",               # smallest → bottom
    "General Sherman",
    "Posidonia australis",
    "Armillaria ostoyae",
    "Pando",                    # largest  → top
]

age_df = pd.DataFrame({
    "organism": pd.Categorical(
        ["Pando", "Armillaria ostoyae", "Posidonia australis",
         "General Sherman", "Blue Whale"],
        categories=age_order,
        ordered=True,
    ),
    "value": [80_000, 8_650, 4_500, 2_700, 90],
})
age_df["label"] = age_df["value"].apply(lambda x: f"{x:,}")

# ==========================================================================
# 2. LENGTH / HEIGHT DATA  (sorted ascending so largest bar at top)
# ==========================================================================
length_order = [
    "Blue Whale",               # smallest → bottom
    "General Sherman",          # largest  → top
]

length_df = pd.DataFrame({
    "organism": pd.Categorical(
        ["General Sherman", "Blue Whale"],
        categories=length_order,
        ordered=True,
    ),
    "value": [83.8, 33.6],
})
length_df["label"] = length_df["value"].apply(lambda x: f"{x}")

# ==========================================================================
# 3. THEME SHARED BY BOTH PLOTS
# ==========================================================================
base_theme = theme_minimal() + theme(
    # Clean white background
    plot_background=element_rect(fill="white", color=None),
    panel_background=element_rect(fill="white", color=None),
    # Minimal grid — only major vertical
    panel_grid_major_x=element_line(color="#EEEEEE", size=0.4),
    panel_grid_major_y=element_blank(),
    panel_grid_minor_x=element_blank(),
    panel_grid_minor_y=element_blank(),
    # Axis styling
    axis_text_y=element_text(size=10, hjust=1, color="#333333"),
    axis_text_x=element_text(size=9, color="#444444"),
    axis_title_x=element_text(size=10, color="#444444"),
    axis_ticks=element_blank(),
    axis_line=element_blank(),
    # Panel titles (facet titles, one per sub-plot)
    plot_title=element_text(size=13, face="bold", color="#333333"),
    # No legend
    legend_position="none",
)

# ==========================================================================
# 4. AGE PLOT — horizontal bars, log10 x-scale
# ==========================================================================
p_age = (
    ggplot(age_df, aes(y="organism", x="value"))
    + geom_bar(aes(fill="organism"), stat="identity", width=0.6)
    + geom_text(
        aes(label="label"),
        hjust=-0.15,
        size=10,
        color="#333333",
    )
    + scale_fill_manual(values=COLORS)
    + scale_x_log10(
        expand=[0.2, 0],
    )
    + labs(
        title="Age",
        x="Age (years, log scale)",
        y="",
    )
    + base_theme
)

# ==========================================================================
# 5. LENGTH / HEIGHT PLOT — horizontal bars, linear x-scale
# ==========================================================================
p_length = (
    ggplot(length_df, aes(y="organism", x="value"))
    + geom_bar(aes(fill="organism"), stat="identity", width=0.35)
    + geom_text(
        aes(label="label"),
        hjust=-0.15,
        size=10,
        color="#333333",
    )
    + scale_fill_manual(values=COLORS)
    + scale_x_continuous(
        expand=[0.3, 0],
    )
    + labs(
        title="Length / Height",
        x="Length/Height (meters)",
        y="",
    )
    + base_theme
)

# ==========================================================================
# 6. COMBINE VIA GGBUNCH  +  GLOBAL TITLE / CAPTION
# ==========================================================================
regions = [
    # (x, y, width, height) — relative to plot area after title/subtitle
    (0.0, 0.0, 0.5, 1.0),   # left half  — Age
    (0.5, 0.0, 0.5, 1.0),   # right half — Length/Height
]

combined = (
    ggbunch([p_age, p_length], regions)
    + ggtitle("The Biggest Living Organisms: Age and Height")
    + labs(
        subtitle=(
            "How the contenders compare by maximum estimated age "
            "and physical stature"
        ),
        caption=(
            "Sources: Pineau et al. (2024) NSF; Ferguson et al. (2003); "
            "Edgeloe et al. (2022); NPS; Guinness World Records"
        ),
    )
    + theme(
        # Global title
        plot_title=element_text(
            size=17, face="bold", hjust=0.5, color="#222222"
        ),
        # Subtitle
        plot_subtitle=element_text(
            size=12, hjust=0.5, color="#666666"
        ),
        # Caption (source line at the bottom)
        plot_caption=element_text(
            size=8, hjust=0.5, color="#888888",
        ),
        # White background for whole figure
        plot_background=element_rect(fill="white", color=None),
    )
    + ggsize(1200, 800)
)

# ==========================================================================
# 7. SAVE PNG  (1200×800 px @ 150 DPI)
# ==========================================================================
saved_path = ggsave(
    combined,
    OUTPUT_PATH,
    w=1200,
    h=800,
    unit="px",
    dpi=150,
)
print(f"✓  Chart saved → {saved_path}")
