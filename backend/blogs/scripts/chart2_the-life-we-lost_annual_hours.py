"""
Chart 2: The Inverted U — Annual Working Hours (1750–2025)
Line chart with shaded area showing the rise and fall of annual working hours.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe.
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data ---
data = pd.DataFrame({
    "year": [1760, 1800, 1830, 1870, 1900, 1938, 1950, 2000, 2024],
    "hours": [2576, 3328, 3356, 2950, 2660, 2050, 1950, 1832, 1790],
    "source": [
        "Voth 2001", "Voth 2001", "Voth 2001",
        "Ramey & Francis 2009",
        "Ramey & Francis 2009",
        "Ramey & Francis 2009",
        "Ramey & Francis 2009",
        "BLS ATUS",
        "BLS ATUS 2024",
    ],
})

data["year"] = pd.to_numeric(data["year"])
data["hours"] = pd.to_numeric(data["hours"])

# Generate smooth interpolation for the area fill
years_smooth = np.linspace(data["year"].min(), data["year"].max(), 300)
hours_smooth = np.interp(years_smooth, data["year"], data["hours"])
fill_df = pd.DataFrame({"year": years_smooth, "hours": hours_smooth})

# Filter for key point labels
key_points = data[data["year"].isin([1760, 1830, 1900, 2024])]

# --- Build chart ---
p = (
    ggplot(data, aes(x="year", y="hours"))
    # Shaded area under the line
    + geom_area(
        data=fill_df, mapping=aes(x="year", y="hours"),
        fill="#0072B2", alpha=0.18,
    )
    # Line
    + geom_line(color="#003366", size=1.4)
    # Points on actual data
    + geom_point(color="#003366", size=2.8, fill="white", stroke=1.5, shape=21)
    # Labels for key points
    + geom_text(
        mapping=aes(label="hours"), data=key_points,
        nudge_y=180, size=9.5, color="#333333", fontface="bold",
    )
    + geom_text(
        mapping=aes(label="source"), data=key_points,
        nudge_y=-200, size=7, color="#888888",
    )
    + scale_x_continuous(
        breaks=[1760, 1800, 1830, 1870, 1900, 1938, 1950, 2000, 2024],
        expand=[0.01, 8],
    )
    + scale_y_continuous(
        limits=[1000, 3800],
        breaks=list(np.arange(1000, 3801, 500)),
        expand=[0, 0],
    )
    + labs(
        title="Annual Working Hours, 1760–2024: The Inverted U",
        subtitle=(
            "From pre-industrial lows to industrial peak to modern moderation — "
            "but the 'leisure society' never materialized"
        ),
        x="",
        y="Annual hours per worker",
        caption=(
            "Sources: Voth 2001 J. Econ. History (1760–1830); "
            "Ramey & Francis 2009 AEJ:Macro (1870–1950); "
            "BLS ATUS 2024 (2000–2024)  |  "
            "Note: UK data 1760–1870, US data 1900–2024"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=12, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=12, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=10, angle=35, hjust=1),
        axis_text_y=element_text(size=10),
        plot_caption=element_text(size=9, color="#888888", hjust=0, margin=[12, 0, 0, 0]),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
    )
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-life-we-lost_chart2_annual_hours.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 2 saved to: {output_path}")
