#!/usr/bin/env python3
"""
Chart: The Race for Precision — Timekeeping Accuracy, 1500 BCE – 2025 CE
=========================================================================
Log-scale line chart showing how timekeeping accuracy has improved
by ~18 orders of magnitude over 3,500 years.

Key leaps highlighted: the pendulum clock (1656) — first true order-of-magnitude
leap from 300 sec/day to 10 sec/day.

Sources:
  - NIST "A Walk Through Time"
  - Marrison, Bell System Technical Journal (1948)
  - Essen & Parry, Nature (1955)

Output: 1200×720 px PNG @ 150 DPI, colorblind-safe palette.
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

image_path = IMAGE_DIR / "the-sociology-of-time_accuracy_leap.png"

# ---------------------------------------------------------------------------
# Data (source: NIST, Bell Labs)
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "year": [
        -1500, -500, 1300, 1600, 1656, 1721, 1761,
        1889, 1921, 1927, 1940, 1955, 1965, 1995, 2025,
    ],
    "technology": [
        "Water clock (Egypt)", "Sundial",
        "Verge & foliot clock", "Improved verge clock",
        "Huygens pendulum", "Graham pendulum",
        "Harrison H4",
        "Riefler clock", "Shortt clock",
        "Marrison quartz", "Precision quartz",
        "Essen caesium", "HP caesium standard",
        "Hydrogen maser", "NIST optical lattice",
    ],
    "error_per_day": [
        900.0, 600.0, 900.0, 300.0, 10.0, 1.0, 0.2,
        0.01, 0.001, 0.2, 0.004, 0.00001, 0.000001,
        1e-10, 1e-16,
    ],
    "era": [
        "Ancient", "Ancient", "Medieval", "Medieval", "Pendulum",
        "Pendulum", "Chronometer", "Free pendulum", "Free pendulum",
        "Quartz", "Quartz", "Atomic", "Atomic", "Atomic", "Optical",
    ],
})

# Log of error for annotation positioning
df["log_err"] = np.log10(df["error_per_day"])

# ---------------------------------------------------------------------------
# Label positions — manually tuned to avoid overlap, especially in the
# dense 20th-century cluster. Each entry is (label_x, label_y, hjust).
# ---------------------------------------------------------------------------
label_map = {
    -1500: (-1850, 900, 1),     # far left of point, right-aligned
    -500:  (-750,  600, 1),     # left of point, right-aligned
    1300:  (1420,  900, 0),     # right of point, left-aligned
    1600:  (1670,  300, 0),
    1656:  (1720,  10,  0),
    1721:  (1780,  1.5, 0),     # lift above the ref-line
    1761:  (1810,  0.08, 0),    # drop below 0.2 to separate from 1927
    1889:  (1918,  0.02, 0),
    1921:  (1895,  0.004, 1),   # left-of-point, right-aligned
    1927:  (1960,  0.5,  0),    # right-of-point, left-aligned, lift above 0.2
    1940:  (1970,  0.002, 0),   # right
    1955:  (1978,  6e-6, 0),
    1965:  (1992,  3e-6, 0),
    1995:  (2020,  3e-10, 0),
    2025:  (2060,  3e-16, 0),
}

df["label_x"]   = df["year"].map({k: v[0] for k, v in label_map.items()})
df["label_y"]   = df["year"].map({k: v[1] for k, v in label_map.items()})
df["label_h"]   = df["year"].map({k: v[2] for k, v in label_map.items()})
df["label_hc"]  = df["label_h"].astype(str)  # string version for aes mapping

# ---------------------------------------------------------------------------
# Aesthetics — colorblind-safe (Wong 2011 blue)
# ---------------------------------------------------------------------------
LINE_COLOR  = "#0072B2"
POINT_COLOR = "#004D73"
REF_COLOR   = "#CC3333"

# ---------------------------------------------------------------------------
# Build chart
# ---------------------------------------------------------------------------

# X-axis breaks — BCE years get descriptive labels
x_breaks = [-1500, -1000, -500, 0, 500, 1000, 1500, 2000]
x_labels = [
    "1500\nBCE", "1000\nBCE", "500\nBCE",
    "0", "500", "1000", "1500", "2000",
]

# Y-axis breaks — powers of 10 with clean unicode superscript labels
y_breaks = [1e-16, 1e-14, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 0.01, 1, 100, 1000]
y_labels = [
    "10\u207b\u00b9\u2076",  # 10⁻¹⁶
    "10\u207b\u00b9\u2074",  # 10⁻¹⁴
    "10\u207b\u00b9\u00b2",  # 10⁻¹²
    "10\u207b\u00b9\u2070",  # 10⁻¹⁰
    "10\u207b\u2078",        # 10⁻⁸
    "10\u207b\u2076",        # 10⁻⁶
    "10\u207b\u2074",        # 10⁻⁴
    "10\u207b\u00b2",        # 10⁻²
    "1",
    "10\u00b2",              # 10²
    "10\u00b3",              # 10³
]

p = (
    ggplot(df, aes(x="year", y="error_per_day"))
    # --- Reference line: 1 second error ---
    + geom_hline(yintercept=1.0, linetype="dashed",
                 color=REF_COLOR, size=0.6, alpha=0.45)
    + geom_text(
        label="1 second\nerror per day",
        x=2022, y=1.0,
        color=REF_COLOR, size=7.5, alpha=0.55,
        hjust=1, vjust=-0.3,
        fontface="italic", lineheight=0.9,
        show_legend=False,
    )
    # --- Main line ---
    + geom_line(color=LINE_COLOR, size=1.8)
    # --- Data points ---
    + geom_point(color=POINT_COLOR, size=4.5, alpha=0.9)
    # --- Technology labels (split by hjust to respect alignment) ---
    # Right-aligned labels (BCE era, left-of-point)
    + geom_text(
        data=df[df["label_h"] == 1],
        mapping=aes(x="label_x", y="label_y", label="technology"),
        size=7.0, color="#222222",
        hjust=1, vjust=0.5, lineheight=0.85,
        show_legend=False,
    )
    # Left-aligned labels (most points, right-of-point)
    + geom_text(
        data=df[df["label_h"] == 0],
        mapping=aes(x="label_x", y="label_y", label="technology"),
        size=7.0, color="#222222",
        hjust=0, vjust=0.5, lineheight=0.85,
        show_legend=False,
    )
    # --- Highlight annotation: first pendulum leap ---
    + geom_text(
        label="Pendulum →\n10× leap",
        x=1660, y=40,
        color="#0072B2", size=8,
        fontface="bold", hjust=1, vjust=1,
        lineheight=0.9, alpha=0.75,
        show_legend=False,
    )
    + geom_curve(
        x=1668, y=35, xend=1658, yend=12,
        color="#0072B2", size=0.5, alpha=0.5,
        curvature=0.3,
        show_legend=False,
    )
    # --- Scales ---
    + scale_x_continuous(
        breaks=x_breaks,
        labels=x_labels,
        limits=[-1900, 2120],
    )
    + scale_y_log10(
        breaks=y_breaks,
        labels=y_labels,
        limits=[3e-17, 2000],
    )
    # --- Labels ---
    + labs(
        title="The Race for Precision: Timekeeping Accuracy, 1500 BCE \u2013 2025 CE",
        subtitle=(
            "From water clocks losing 15 minutes a day to atomic clocks "
            "losing 1 second in 30 billion years"
        ),
        x="Year",
        y="Error per day (seconds)",
        caption=(
            "Sources: NIST \u201cA Walk Through Time\u201d; "
            "Marrison, Bell System Technical Journal (1948); "
            "Essen & Parry, Nature (1955)"
        ),
    )
    # --- Theme ---
    + theme_minimal()
    + theme(
        plot_title=element_text(
            size=20, face="bold", hjust=0, margin=[0, 0, 6, 0],
        ),
        plot_subtitle=element_text(
            size=11, color="#555555", hjust=0, margin=[0, 0, 18, 0],
        ),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_title_y=element_text(size=12, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=10),
        axis_text_y=element_text(size=9),
        plot_caption=element_text(
            size=8.5, color="#888888", hjust=0, margin=[16, 0, 0, 0],
        ),
        panel_grid_major=element_line(color="#E8E8E8", size=0.4),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 30, 10, 10],
    )
)

# ---------------------------------------------------------------------------
# Save  (1200×720 @ 150 DPI)
# ---------------------------------------------------------------------------
ggsave(p, str(image_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart saved: {image_path}")

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
img = Image.open(image_path)
arr = np.array(img)
n_colors = len(np.unique(arr.reshape(-1, arr.shape[2]), axis=0))
print(f"Validation: {arr.shape[1]}×{arr.shape[0]} px, "
      f"{n_colors} unique colours, "
      f"{image_path.stat().st_size / 1024:.1f} KB")
print("Done.")
