#!/usr/bin/env python3
"""
Chart: Biggest Living Organisms — Mass and Area comparison.
Horizontal bar chart with two side-by-side plots using lets-plot + gggrid.

Source attributions (metadata / footnote):
  - Armillaria mass (35,000 tons): Oregon Encyclopedia / USDA Forest Service
  - Pando mass (6,000 tons): USFS Fishlake NF / Wikipedia Pando
  - General Sherman trunk mass (1,400 tons): National Park Service
  - Blue Whale mass (190 tons): Guinness World Records / NOAA
  - Posidonia area (200 km²): Edgeloe et al. (2022) Proc. R. Soc. B
  - Armillaria area (9.65 km²): Ferguson et al. (2003) Can. J. Forest Res.
  - Pando area (0.428 km²): DeWoody et al. (2008) West. N. Am. Naturalist
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# =====================================================================
# 1. DATA
# =====================================================================

# --- Mass data (4 organisms, sorted largest -> smallest) ---
mass = pd.DataFrame({
    "organism": [
        "Armillaria ostoyae",
        "Pando",
        "General Sherman",
        "Blue Whale",
    ],
    "value": [35000, 6000, 1400, 190],
})

# --- Area data (3 organisms, sorted largest -> smallest) ---
area = pd.DataFrame({
    "organism": [
        "Posidonia australis",
        "Armillaria ostoyae",
        "Pando",
    ],
    "value": [200, 9.65, 0.428],
})


# =====================================================================
# 2. HELPERS
# =====================================================================

def fmt(v):
    """Pretty-print a value: whole numbers with commas, decimals without
    trailing zeros."""
    if v == int(v):
        return f"{int(v):,}"
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s


mass["label"] = mass["value"].apply(fmt)
area["label"] = area["value"].apply(fmt)

# Set organism as ordered categorical (largest -> smallest top of y-axis)
mass["organism"] = pd.Categorical(
    mass["organism"],
    categories=mass["organism"].tolist(),   # sorted descending above
    ordered=True,
)
area["organism"] = pd.Categorical(
    area["organism"],
    categories=area["organism"].tolist(),
    ordered=True,
)


# =====================================================================
# 3. COLOR PALETTE (Wong / colorblind-safe, 5 colours)
# =====================================================================

COLORS = {
    "Armillaria ostoyae":  "#0072B2",   # blue
    "Pando":                "#009E73",   # green
    "General Sherman":      "#D55E00",   # vermillion
    "Blue Whale":           "#CC79A7",   # pink
    "Posidonia australis":  "#E69F00",   # orange
}

# Make sure all organisms present in each df have a colour assigned
assert all(o in COLORS for o in mass["organism"]), "Missing colour for mass"
assert all(o in COLORS for o in area["organism"]), "Missing colour for area"


# =====================================================================
# 4. SHARED THEME BASELINE
# =====================================================================

base_theme = theme(
    # Grid ---
    panel_grid_minor="blank",
    panel_grid_major_x=element_line(color="#E8E8E8", size=0.35),
    panel_grid_major_y="blank",
    # Axes ---
    axis_title_y="blank",
    axis_text_y=element_text(size=10, color="#333333"),
    axis_text_x=element_text(size=9, color="#555555"),
    # Background ---
    panel_background=element_rect(fill="white", color=None),
    plot_background=element_rect(fill="white", color=None),
    # Legend ---
    legend_position="bottom",
    legend_text=element_text(size=9),
)

# =====================================================================
# 5. MASS PANEL
# =====================================================================

p_mass = (
    ggplot(mass, aes(y="organism", x="value", fill="organism"))
    + geom_bar(stat="identity", width=0.6)
    + geom_text(
        aes(label="label"),
        hjust=-0.15,
        size=10,
        color="#333333",
    )
    + scale_fill_manual(values=COLORS)
    + scale_x_continuous(
        name="Mass (metric tons)",
        expand=[0.05, 0],
    )
    + ggtitle("Mass (metric tons)")
    + theme_minimal()
    + base_theme
)

# =====================================================================
# 6. AREA PANEL
# =====================================================================

p_area = (
    ggplot(area, aes(y="organism", x="value", fill="organism"))
    + geom_bar(stat="identity", width=0.6)
    + geom_text(
        aes(label="label"),
        hjust=-0.15,
        size=10,
        color="#333333",
    )
    + scale_fill_manual(values=COLORS)
    + scale_x_continuous(
        name="Area (km\u00b2)",
        expand=[0.05, 0],
    )
    + ggtitle("Area (km\u00b2)")
    + theme_minimal()
    + base_theme
    # Suppress duplicate legend on the area panel
    + guides(fill="none")
)

# =====================================================================
# 7. COMBINE WITH GGGrid
# =====================================================================

# Use gggrid to place both panels side by side.
# We'll overlay title/subtitle/caption via the GridPlot's labs().
grid = gggrid(
    [p_mass, p_area],
    ncol=2,
) + labs(
    title="The Biggest Living Organisms: Mass and Area",
    subtitle=(
        "How the contenders compare by dry-weight mass and areal extent"
    ),
    caption=(
        "Sources: USDA Forest Service, NPS, NOAA Fisheries, "
        "Guinness World Records, Edgeloe et al. (2022) Proc. R. Soc. B"
    ),
) + theme(
    # Title / subtitle / caption on the outer grid container ---
    plot_title=element_text(size=15, face="bold"),
    plot_subtitle=element_text(
        size=11, color="#666666"
    ),
    plot_caption=element_text(
        size=7.5, color="#999999"
    ),
    plot_margin=[10, 25, 10, 10],
    plot_background=element_rect(fill="white", color=None),
)

# =====================================================================
# 8. SAVE
# =====================================================================

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
png_path = output_dir / "biggest-living-organism_mass_area.png"

script_path = Path(
    "/home/pi/Documents/code/quortol/backend/blogs/scripts"
    "/chart1_biggest-living-organism_mass_area.py"
)

# 1200 x 800 px at 150 DPI  ->  8 x 5.333 in
ggsave(grid, str(png_path), w=8, h=5.333, unit="in", dpi=150)

print(f"Chart saved to: {png_path}")
print(f"Script: {script_path}")
