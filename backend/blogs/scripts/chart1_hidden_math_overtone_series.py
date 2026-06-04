#!/usr/bin/env python3
"""
Chart: The Overtone Series — frequency spectrum bar chart
showing first 8 harmonics of a cello's low A string (110 Hz).

Output: 1200 × 720 px PNG, 150 DPI
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "harmonic": [1, 2, 3, 4, 5, 6, 7, 8],
    "frequency": [110, 220, 330, 440, 550, 660, 770, 880],
    "interval": [
        "Fundamental (A\u2082)",
        "Octave (A\u2083)",
        "Perfect Fifth (E\u2084)",
        "Double Octave (A\u2084)",
        "Major Third (C\u266f\u2085)",
        "Perfect Fifth (E\u2085)",
        "Minor Seventh (G\u2085)",
        "Triple Octave (A\u2085)",
    ],
    "ratio": [
        "1:1",
        "2:1",
        "3:2",
        "4:1",
        "5:4",
        "3:1",
        "7:4",
        "8:1",
    ],
})

# Create x-axis labels
df["harmonic_label"] = [f"Harmonic {i}" for i in range(1, 9)]

# Combined annotation: interval name on one line, ratio below
df["annotation"] = [
    f"{interval}\n{ratio}"
    for interval, ratio in zip(df["interval"], df["ratio"])
]

# Y-position for text labels: 55 Hz above each bar's top
df["y_text"] = df["frequency"] + 55

# Preserve categorical order for the x-axis
df["harmonic_label"] = pd.Categorical(
    df["harmonic_label"],
    categories=df["harmonic_label"].tolist(),
    ordered=True,
)

# ---------------------------------------------------------------------------
# Color palette: Wong / Okabe-Ito colorblind-safe (8 colours)
# ---------------------------------------------------------------------------
COLORS = [
    "#E69F00",  # Orange       — Harmonic 1
    "#56B4E9",  # Sky Blue     — Harmonic 2
    "#009E73",  # Bluish Green — Harmonic 3
    "#F0E442",  # Yellow       — Harmonic 4
    "#0072B2",  # Blue         — Harmonic 5
    "#D55E00",  # Vermillion   — Harmonic 6
    "#CC79A7",  # Reddish Purple — Harmonic 7
    "#999999",  # Grey         — Harmonic 8
]

# ---------------------------------------------------------------------------
# Build plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="harmonic_label", y="frequency", fill="harmonic_label"))
    # Bars with subtle white stroke for separation
    + geom_bar(stat="identity", width=0.72, color="#FFFFFF", size=0.6)
    # Colorblind-safe fill
    + scale_fill_manual(values=COLORS)
    # Annotation: interval name + ratio above each bar
    + geom_text(
        aes(x="harmonic_label", y="y_text", label="annotation"),
        size=9,
        color="#222222",
        ha="center",
        va="bottom",
        lineheight=0.92,
    )
    # Y-axis from 0 to 1020 (leaves ~140 Hz headroom for annotations above
    # the tallest bar at 880 Hz)
    + scale_y_continuous(
        limits=(0, 1020),
        breaks=[0, 110, 220, 330, 440, 550, 660, 770, 880],
        expand=[0, 0],
    )
    # Labels
    + labs(
        title="The Overtone Series: A Single Note Contains Many",
        subtitle="Cello A\u2082 = 110 Hz fundamental with its first eight overtones",
        x="",
        y="Frequency (Hz)",
        caption="Data: Physics of the overtone series",
    )
    # Clean theme
    + theme_minimal()
    + theme(
        # Title
        plot_title=element_text(size=18, hjust=0.5, face="bold",
                                color="#1a1a1a"),
        # Subtitle
        plot_subtitle=element_text(size=12, hjust=0.5,
                                   color="#555555"),
        # X-axis labels
        axis_text_x=element_text(size=11, color="#333333"),
        # Y-axis labels
        axis_text_y=element_text(size=10, color="#555555"),
        # Y-axis title
        axis_title_y=element_text(size=12, color="#333333"),
        # Caption / source line
        plot_caption=element_text(size=9, color="#888888",
                                  hjust=0, face="italic"),
        # Grid: only horizontal light lines
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#EEEEEE", size=0.35),
        panel_grid_minor=element_blank(),
        # Axes
        axis_line=element_line(color="#CCCCCC"),
        axis_ticks=element_line(color="#CCCCCC"),
        # Background
        panel_background=element_rect(fill="#FAFAFA", color=None),
        plot_background=element_rect(fill="white", color=None),
        # No legend (color encodes harmonic number, labeled on x-axis)
        legend_position="none",
        # Margins: top, right, bottom, left
        plot_margin=[10, 25, 5, 15],
    )
)

# ---------------------------------------------------------------------------
# Save — 1200 × 720 px at 150 DPI  →  8 × 4.8 inches
# ---------------------------------------------------------------------------
script_dir = Path(__file__).resolve().parent
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

png_path = images_dir / "hidden-math-in-what-you-hear_overtone_series.png"

ggsave(p, str(png_path), w=8, h=4.8, unit="in", dpi=150)

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
if png_path.exists():
    size_kb = png_path.stat().st_size / 1024
    print(f"Saved: {png_path}")
    print(f"  Dimensions: 1200 × 720 px @ 150 DPI")
    print(f"  File size:  {size_kb:.1f} KB")
else:
    print(f"ERROR: file was not created at {png_path}")
