"""
The Great Preservation — Chart 2: Global Terrestrial Protected Area Coverage (1990–2024)
Line chart with filled area showing the percentage of global terrestrial land area that is protected.
Includes a dashed reference line for the 2030 30×30 target.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe blue (#1b4965).
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "year": [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024],
    "pct":   [5.5, 7.8, 10.2, 12.1, 14.0, 15.5, 16.8, 17.6],
})

data["year"] = pd.to_numeric(data["year"])
data["pct"] = pd.to_numeric(data["pct"])

# Smooth interpolation for clean filled area
years_smooth = np.linspace(data["year"].min(), data["year"].max(), 300)
pct_smooth = np.interp(years_smooth, data["year"], data["pct"])
fill_df = pd.DataFrame({"year": years_smooth, "pct": pct_smooth})

# Annotation for 30×30 target label
target_label = pd.DataFrame({
    "x": [1990.5],
    "y": [31.0],
    "label": ["2030 Target (30\u00d730)"],
})

# ── Colour palette ────────────────────────────────────────────────────
BLUE = "#1b4965"
RED_ACCENT = "#CC3333"

# ── Build chart ───────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="year", y="pct"))
    # Filled area under the line
    + geom_area(
        data=fill_df, mapping=aes(x="year", y="pct"),
        fill=BLUE, alpha=0.15,
    )
    # Main line
    + geom_line(color=BLUE, size=1.4)
    # Data points
    + geom_point(color=BLUE, size=2.8, fill="white", stroke=1.5, shape=21)
    # 30×30 Target reference line
    + geom_hline(yintercept=30, color=RED_ACCENT, size=0.8, linetype="dashed")
    # Target annotation label
    + geom_text(
        mapping=aes(x="x", y="y", label="label"), data=target_label,
        size=9, color=RED_ACCENT, fontface="italic", hjust=0,
    )
    # Arrow annotation showing the gap (optional, using text-based arrow)
    + geom_text(
        mapping=aes(x="x", y="y"), data=pd.DataFrame({"x": [2021], "y": [23.5]}),
        label="\u2191 12.4 pp gap", size=8, color=RED_ACCENT, fontface="italic", hjust=0.5,
    )
    # X axis
    + scale_x_continuous(
        breaks=[1990, 1995, 2000, 2005, 2010, 2015, 2020],
        expand=[0.01, 0.5],
    )
    # Y axis
    + scale_y_continuous(
        limits=[0, 35],
        breaks=[0, 5, 10, 15, 20, 25, 30],
        expand=[0, 0.5],
    )
    # Labels & title
    + labs(
        title="Global Terrestrial Protected Area Coverage, 1990\u20132024",
        subtitle="Percentage of global terrestrial land area designated as protected",
        x="",
        y="% of terrestrial land area",
        caption="Source: World Database on Protected Areas (WDPA), UNEP-WCMC and IUCN, Protected Planet Report 2024  |  digitalreport.protectedplanet.net",
    )
    # Magazine-style theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=12, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=11, angle=35, hjust=1),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=9, color="#888888", hjust=0, margin=[12, 0, 0, 0]),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
    )
)

# ── Save ──────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-great-preservation_protected_area.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 2 saved to: {output_path}")
