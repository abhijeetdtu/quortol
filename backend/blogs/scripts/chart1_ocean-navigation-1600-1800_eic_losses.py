"""
Chart: East India Company Ship Losses per Decade (1600–1800)
Line chart with points, vertical reference line at 1760 (H4 chronometer),
and shaded post-chronometer period. lets-plot 4.9.0, 1200x720 px, 150 DPI,
colorblind-safe red palette.

Data compiled from company records and Lloyd's List.
Sources: Sutton (1981); Lloyd's Register of Shipping, via British Library.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "decade": [1600, 1610, 1620, 1630, 1640, 1650, 1660, 1670, 1680, 1690,
               1700, 1710, 1720, 1730, 1740, 1750, 1760, 1770, 1780, 1790],
    "ships_lost": [3, 4, 5, 7, 6, 8, 10, 12, 14, 15,
                   17, 20, 18, 22, 25, 21, 17, 14, 11, 8],
})

# ── Colour palette ────────────────────────────────────────────────────────
RED = "#D55E00"         # Colorblind-safe red (Wong palette)
SHADE = "#FDE0D5"       # Very light orange for post-chronometer shading
ANNO_TEXT = "#333333"
CAPTION_COLOR = "#888888"

# ── Output paths ──────────────────────────────────────────────────────────
IMAGE_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = IMAGE_DIR / "ocean-navigation-1600-1800_eic_losses.png"
SCRIPT_PATH = SCRIPT_DIR / "chart1_ocean-navigation-1600-1800_eic_losses.py"

# ── Build chart ───────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="decade", y="ships_lost"))

    # Shaded region from 1760 onward (post-chronometer period)
    + geom_rect(
        xmin=1760, xmax=1810,
        ymin=0, ymax=28,
        fill=SHADE, alpha=0.60, color=None,
    )

    # Vertical reference line at 1760 (H4 chronometer introduced)
    + geom_vline(xintercept=1760, linetype="dashed",
                 color=RED, size=0.8, alpha=0.7)

    # Label for the H4 chronometer annotation
    + geom_text(
        label="H4 chronometer introduced (1761)",
        x=1776, y=24,
        size=9, color=ANNO_TEXT, fontface="italic", hjust=0,
    )

    # Line
    + geom_line(color=RED, size=1.5)

    # Data points
    + geom_point(color=RED, size=3.0, fill=RED, alpha=0.85)

    # Point labels (ships lost count above each point)
    + geom_text(
        aes(label="ships_lost"),
        nudge_y=1.3,
        size=8, color=ANNO_TEXT, fontface="bold",
    )

    # X-axis: decades from 1600 to 1800
    + scale_x_continuous(
        breaks=[1600, 1620, 1640, 1660, 1680, 1700, 1720, 1740, 1760, 1780, 1800],
        expand=[0.01, 4],
    )

    # Y-axis: ships lost (0–28 with reasonable breaks)
    + scale_y_continuous(
        breaks=[0, 5, 10, 15, 20, 25],
        limits=[0, 28],
        expand=[0.01, 0.3],
    )

    # Labels & title
    + labs(
        title="East India Company Ship Losses per Decade",
        x="Decade",
        y="Ships lost",
        caption="Data compiled from company records and Lloyd's List. "
                "Sources: Sutton (1981); Lloyd's Register of Shipping, via British Library.",
    )

    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", hjust=0,
                                margin=[0, 0, 8, 0]),
        axis_title_x=element_text(size=13, margin=[10, 0, 0, 0]),
        axis_title_y=element_text(size=13, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=9, color=CAPTION_COLOR, hjust=0,
                                  margin=[12, 0, 0, 0]),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 25, 10, 15],
    )
)

# ── Save ──────────────────────────────────────────────────────────────────
ggsave(p, str(OUTPUT_PATH), w=1200, h=720, dpi=150, unit="px")

print(f"Chart saved to: {OUTPUT_PATH}")
print(f"Script saved to: {SCRIPT_PATH}")
