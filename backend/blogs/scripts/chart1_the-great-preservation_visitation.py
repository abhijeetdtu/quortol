"""
The Great Preservation — Chart 1: NPS Visitation Growth (1904–2024)
Line chart with filled area showing annual recreation visits to U.S. National Park Service units.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe green (#2d6a4f).
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "year": [1904, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2016, 2020, 2024],
    "visitors": [120690, 173416, 1022091, 3038935, 16410148, 32706172, 71586000, 168135100, 220463211, 255581467, 285891275, 281303769, 330971689, 237064332, 331863358],
})

data["year"] = pd.to_numeric(data["year"])
data["visitors"] = pd.to_numeric(data["visitors"])

# Smooth interpolation for a clean filled area
years_smooth = np.linspace(data["year"].min(), data["year"].max(), 500)
visitors_smooth = np.interp(years_smooth, data["year"], data["visitors"])
fill_df = pd.DataFrame({"year": years_smooth, "visitors": visitors_smooth})

# Annotation data point for 2020 COVID drop
annot = pd.DataFrame({
    "year": [2020],
    "visitors": [237064332],
    "label": ["COVID-19 pandemic"],
})

# ── Colour palette ────────────────────────────────────────────────────
NPS_GREEN = "#2d6a4f"
RED_ACCENT = "#CC3333"

# ── Build chart ───────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="year", y="visitors"))
    # Filled area under the line
    + geom_area(
        data=fill_df, mapping=aes(x="year", y="visitors"),
        fill=NPS_GREEN, alpha=0.15,
    )
    # Main line
    + geom_line(color=NPS_GREEN, size=1.4)
    # Data points
    + geom_point(color=NPS_GREEN, size=2.8, fill="white", stroke=1.5, shape=21)
    # Vertical reference for 2020 COVID drop
    + geom_vline(xintercept=2020, color=RED_ACCENT, size=0.7, linetype="dashed", alpha=0.5)
    # Annotation label
    + geom_text(
        mapping=aes(label="label"), data=annot,
        nudge_x=2.8, nudge_y=28e6, size=9, color=RED_ACCENT, fontface="italic",
        hjust=0,
    )
    # X axis
    + scale_x_continuous(
        breaks=[1900, 1920, 1940, 1960, 1980, 2000, 2020],
        expand=[0.01, 3],
    )
    # Y axis with millions formatting
    + scale_y_continuous(
        breaks=[0, 50e6, 100e6, 150e6, 200e6, 250e6, 300e6, 350e6],
        labels=["0", "50M", "100M", "150M", "200M", "250M", "300M", "350M"],
        expand=[0, 5e6],
    )
    # Labels & title
    + labs(
        title="NPS Visitation Growth, 1904–2024",
        subtitle="Annual recreation visits to U.S. National Park Service units",
        x="",
        y="Annual recreation visits",
        caption="Source: National Park Service, Social Science Program, Annual Visitation Reports  |  nps.gov/aboutus/visitation-numbers.htm",
    )
    # Magazine-style theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=12, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=11),
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
output_path = output_dir / "the-great-preservation_visitation.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 1 saved to: {output_path}")
