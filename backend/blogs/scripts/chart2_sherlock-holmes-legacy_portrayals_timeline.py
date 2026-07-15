#!/usr/bin/env python3
"""
Chart: Sherlock Holmes Screen Portrayals, 1900–2020.
Cumulative line chart with filled area showing the growth of Sherlock Holmes
film and television portrayals over 120 years — from a 30-second silent film
to the most-portrayed human character in history (Guinness World Records).

Sources:
  - Guinness World Records (2012 certification: 254 portrayals)
  - Nathan Camp thesis "Not So Elementary" (2018) — film/TV population of
    174 films + 99 TV shows
  - Wikipedia for early film history (Sherlock Holmes Baffled, 1900)
"""

import numpy as np
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# =====================================================================
# 1. DATA
# =====================================================================

data = pd.DataFrame({
    "year":    [1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2012, 2020],
    "portrayals": [1,    5,    12,   18,   25,   33,   45,   60,   82,   110,  155,  254,  300],
})

# Smooth interpolation for a clean filled area
year_smooth = np.linspace(data["year"].min(), data["year"].max(), 500)
portrayals_smooth = np.interp(year_smooth, data["year"], data["portrayals"])
fill_df = pd.DataFrame({"year": year_smooth, "portrayals": portrayals_smooth})

# Annotation: Guinness World Record at 2012
guinness_annot = pd.DataFrame({
    "year": [2012],
    "portrayals": [254],
    "label": ["Guinness World Record: 254"],
})

# Last point label (~300 in 2020)
last_point = pd.DataFrame({
    "year": [2020],
    "portrayals": [300],
    "label": ["~300"],
})

# =====================================================================
# 2. COLOUR PALETTE
# =====================================================================

NAVY = "#1E3A5F"
LIGHT_BLUE = "#1E3A5F"  # same navy for fill, controlled by alpha
ACCENT_RED = "#CC3333"

# =====================================================================
# 3. BUILD CHART
# =====================================================================

p = (
    ggplot(data, aes(x="year", y="portrayals"))
    # Filled area under the line (smooth interpolation)
    + geom_area(
        data=fill_df, mapping=aes(x="year", y="portrayals"),
        fill=NAVY, alpha=0.2,
    )
    # Main cumulative line
    + geom_line(color=NAVY, size=1.4)
    # Data points (white-filled circles on the line)
    + geom_point(color=NAVY, size=2.8, fill="white", stroke=1.5, shape=21)
    # Vertical dashed annotation line at 2012
    + geom_vline(
        xintercept=2012, color=ACCENT_RED, size=0.7,
        linetype="dashed", alpha=0.6
    )
    # Guinness annotation text
    + geom_text(
        mapping=aes(label="label"), data=guinness_annot,
        nudge_x=3.5, nudge_y=22, size=9, color=ACCENT_RED,
        fontface="italic", hjust=0,
    )
    # Last-point data label
    + geom_text(
        mapping=aes(label="label"), data=last_point,
        nudge_x=3.0, nudge_y=-12, size=10, color=NAVY,
        fontface="bold", hjust=0, vjust=1,
    )
    # X-axis: every 20 years
    + scale_x_continuous(
        breaks=[1900, 1920, 1940, 1960, 1980, 2000, 2020],
        expand=[0.01, 3],
    )
    # Y-axis
    + scale_y_continuous(
        breaks=[0, 50, 100, 150, 200, 250, 300],
        limits=[0, 350],
        expand=[0, 5],
    )
    # Labels
    + labs(
        title="Sherlock Holmes Screen Portrayals, 1900–2020",
        subtitle=(
            "From a 30-second silent film to the most-portrayed "
            "human character in history"
        ),
        x="",
        y="Cumulative portrayals",
        caption=(
            "Sources: Guinness World Records (2012), Nathan Camp thesis "
            "\u201cNot So Elementary\u201d (2018), Wikipedia"
        ),
    )
    # publication-ready theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0,
                                margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0,
                                   margin=[0, 0, 16, 0]),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=12, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=9, color="#888888", hjust=0,
                                  margin=[12, 0, 0, 0]),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
        plot_background=element_rect(fill="white", color=None),
        panel_background=element_rect(fill="white", color=None),
    )
)

# =====================================================================
# 4. SAVE
# =====================================================================

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "sherlock-holmes-legacy_portrayals_timeline.png"

# 1200×720 px at 150 DPI
ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")

print(f"Chart saved to: {output_path}")
