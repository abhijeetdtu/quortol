#!/usr/bin/env python3
"""
Chart: Milestones in the Sociology of Time
===========================================
Horizontal lollipop / dot chart showing key milestones in timekeeping
history and their social/economic impact, arranged by year on a
horizontal axis.

The chart communicates that timekeeping technology accelerated
dramatically after 1656 (the pendulum), and that its social applications
shifted from coordinating small groups (monasteries, workshops) to
synchronizing global systems (GPS, internet).

Output: 1200x720 px PNG @ 150 DPI, colorblind-safe palette.

Sources:
  - NIST "A Walk Through Time"
  - Englund, JESHO (1988)
  - International Meridian Conference Protocols (1884)
  - Cambridge Digital Library Board of Longitude Papers
"""

from pathlib import Path

import numpy as np
import pandas as pd
from lets_plot import *
from PIL import Image

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
IMAGE_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

image_path = IMAGE_DIR / "the-sociology-of-time_milestones.png"

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "year": [
        -3000, -1500, -500, 1283, 1330, 1656, 1759,
        1800, 1884, 1927, 1955, 1967, 1990, 2020,
    ],
    "milestone": [
        "Sumerian administrative calendars",
        "Egyptian water clocks",
        "Greek sundials",
        "First mechanical clock (Dunstable)",
        "Richard of Wallingford's astronomical clock",
        "Huygens pendulum clock",
        "Harrison H4 chronometer",
        "Factory whistles & time clocks",
        "International Meridian Conference",
        "First quartz clock (Marrison/Horton)",
        "First caesium atomic clock (Essen)",
        "SI second redefined by atomic transition",
        "GPS atomic clock network",
        "Optical lattice clocks",
    ],
    "impact": [
        "First coordinated labor scheduling",
        "Work-hour regulation in tomb building",
        "Civic time in agoras",
        "Monastic prayer coordination",
        "Astronomical modeling",
        "10× accuracy leap, longitude goal",
        "Global navigation, empire",
        "Industrial work discipline",
        "Global time zones, railway sync",
        "100× improvement over pendulum",
        "Redefinition of the second",
        "Universal time standard",
        "Consumer location, relativistic corrections",
        "10⁻¹⁶ precision, fundamental physics",
    ],
    "category": [
        "Administration",
        "Coordination",
        "Civic",
        "Monastic",
        "Scientific",
        "Scientific",
        "Navigation",
        "Industrial",
        "Standardization",
        "Scientific",
        "Scientific",
        "Standardization",
        "Consumer",
        "Scientific",
    ],
})

# Sort by year ascending and assign y position (earliest at top)
df = df.sort_values("year", ascending=True).reset_index(drop=True)
df["y"] = df.index  # 0 = earliest (top), 13 = latest (bottom)

# ---------------------------------------------------------------------------
# Colour & label helpers
# ---------------------------------------------------------------------------
FORMAT_YEAR = lambda y: f"{-y} BCE" if y < 0 else str(y)
df["display_year"] = df["year"].apply(FORMAT_YEAR)
df["y_label"] = df["milestone"]  # milestone name on y-axis (year is on x-axis)
# Position impact labels: right of each point
# For BCE milestones, push further right to clear y-axis labels
df["label_x"] = df["year"].apply(
    lambda y: max(y + 80, -100) if y < 0 else y + 55
)

# ---------------------------------------------------------------------------
# Colorblind-safe palette (Wong 2011 extended with I Want Hue)
# ---------------------------------------------------------------------------
CATEGORY_COLORS = {
    "Administration":   "#0077BB",   # blue
    "Coordination":     "#009E73",   # green
    "Civic":            "#E69F00",   # orange
    "Monastic":         "#CC79A7",   # pink / purple-ish
    "Scientific":       "#D55E00",   # vermillion (red-orange)
    "Navigation":       "#44AA99",   # teal
    "Industrial":       "#885533",   # brown
    "Standardization":  "#CC6677",   # rose
    "Consumer":         "#DDCC44",   # mustard yellow
}

# ---------------------------------------------------------------------------
# X-axis
# ---------------------------------------------------------------------------
BASE_X = -3600  # origin for lollipop stems (well left of earliest milestone to clear y-axis labels)

# Break positions and labels for the year axis
x_breaks = [-3000, -2000, -1000, 0, 1000, 1500, 1656, 1750, 1884, 1927, 1967, 2020]
x_labels = [
    "3000\nBCE", "2000\nBCE", "1000\nBCE",
    "0", "1000", "1500",
    "1656", "1750", "1884", "1927", "1967", "2020",
]

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

# Background fill for the "acceleration" era (post-1656)
ACCEL_XMIN = 1656
ACCEL_XMAX = 2100

# Aesthetics
STEM_COLOR  = "#AAAAAA"
LINE_SIXTEEN = "#CC3333"
ACCEL_BG    = "#F5F0E8"   # warm parchment

p = (
    ggplot(df, aes(x="year", y="y"))
    # --- Acceleration era background ---
    + geom_rect(
        xmin=ACCEL_XMIN, xmax=ACCEL_XMAX,
        ymin=-0.6, ymax=13.6,
        fill=ACCEL_BG, alpha=0.35,
        show_legend=False,
    )
    # --- Lollipop stems ---
    + geom_segment(
        mapping=aes(y="y", yend="y", xend="year"),
        x=BASE_X,
        color=STEM_COLOR, size=0.65, alpha=0.4,
        show_legend=False,
    )
    # --- Vertical reference line: pendulum (1656) ---
    + geom_vline(
        xintercept=1656,
        linetype="dashed", color=LINE_SIXTEEN, size=0.7, alpha=0.5,
        show_legend=False,
    )
    # --- Reference annotation ---
    + geom_text(
        label="Pendulum → Acceleration",
        x=1660, y=12.8,
        color=LINE_SIXTEEN, size=8.5, alpha=0.7,
        hjust=0, vjust=0.5,
        fontface="italic", show_legend=False,
    )
    # --- Points (colored by category) ---
    + geom_point(
        aes(color="category"),
        size=5.5, alpha=0.92,
    )
    # --- Impact labels to the right of each point ---
    + geom_text(
        aes(label="impact", x="label_x"),
        size=7.5, color="#222222",
        hjust=0, vjust=0.5, lineheight=0.82,
        show_legend=False,
    )
    # --- Scales ---
    + scale_x_continuous(
        breaks=x_breaks,
        labels=x_labels,
        limits=[-3700, 2100],
    )
    + scale_y_continuous(
        breaks=list(df["y"]),
        labels=list(df["y_label"]),
        limits=[-0.6, 13.6],
    )
    + scale_color_manual(
        values=CATEGORY_COLORS,
        name="Category",
    )
    # --- Labels ---
    + labs(
        title="Milestones in the Sociology of Time",
        subtitle=(
            "How timekeeping technology shaped civilization across 5,000 years"
        ),
        x="Year",
        y="",
        caption=(
            "Sources: NIST; Englund, JESHO (1988); "
            "International Meridian Conference Protocols (1884); "
            "Cambridge Digital Library Board of Longitude Papers"
        ),
    )
    # --- Theme ---
    + theme_minimal()
    + theme(
        plot_title=element_text(
            size=22, face="bold", hjust=0, margin=[0, 0, 6, 0],
        ),
        plot_subtitle=element_text(
            size=12, color="#555555", hjust=0, margin=[0, 0, 20, 0],
        ),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_title_y=element_blank(),
        axis_text_x=element_text(size=9),
        axis_text_y=element_text(
            size=8.5, hjust=1, margin=[0, 6, 0, 0],
        ),
        plot_caption=element_text(
            size=8, color="#888888", hjust=0, margin=[20, 0, 0, 0],
        ),
        panel_grid_major=element_line(color="#E8E8E8", size=0.35),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_blank(),
        plot_margin=[20, 25, 10, 10],
        legend_position="right",
        legend_title=element_text(size=10, face="bold"),
        legend_text=element_text(size=8.5),
        legend_spacing=4,
    )
)

# ---------------------------------------------------------------------------
# Save (1200x720 @ 150 DPI)
# ---------------------------------------------------------------------------
ggsave(p, str(image_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart saved: {image_path}")

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
img = Image.open(image_path)
arr = np.array(img)
n_colors = len(np.unique(arr.reshape(-1, arr.shape[2]), axis=0))
print(f"Validation: {arr.shape[1]}x{arr.shape[0]} px, "
      f"{n_colors} unique colours, "
      f"{image_path.stat().st_size / 1024:.1f} KB")
print("Done.")
