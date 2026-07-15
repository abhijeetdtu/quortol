"""
Chart: Two Thousand Years of European Lead Pollution, Recorded in Arctic Ice
Line chart with filled area showing relative lead pollution levels from 200 BCE to 2010 CE.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe blue/teal (#1a6b8a).

Data source: McConnell et al. (2019), PNAS; data from 13 Arctic ice cores
"""

import numpy as np
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "year": [
        -200, -150, -100, -50, -15, 50, 100, 150, 165, 180, 200, 250,
        300, 400, 500, 550, 600, 650, 700, 750, 770, 790, 815, 850,
        900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1348, 1352,
        1400, 1450, 1500, 1550, 1600, 1650, 1700, 1750, 1800, 1820, 1840,
        1850, 1860, 1880, 1900, 1910, 1915, 1920, 1930, 1935, 1940, 1950,
        1960, 1965, 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010,
    ],
    "lead": [
        0.20, 0.45, 0.30, 0.10, 0.20, 0.45, 0.50, 0.48, 0.40, 0.12, 0.10, 0.08,
        0.08, 0.08, 0.09, 0.09, 0.12, 0.15, 0.20, 0.25, 0.28, 0.30, 0.25, 0.15,
        0.12, 0.14, 0.20, 0.25, 0.28, 0.30, 0.35, 0.38, 0.40, 0.35, 0.10,
        0.15, 0.18, 0.22, 0.25, 0.30, 0.28, 0.50, 0.70, 1.50, 2.00, 2.50,
        3.00, 4.00, 5.00, 7.00, 9.00, 10.00, 12.00, 14.00, 12.00, 18.00, 25.00,
        32.00, 36.00, 40.00, 38.00, 32.00, 25.00, 20.00, 16.00, 13.00, 11.00, 10.00,
    ],
})

# Interpolate for a smooth area fill
years_smooth = np.linspace(data["year"].min(), data["year"].max(), 1000)
lead_smooth = np.interp(years_smooth, data["year"], data["lead"])
fill_df = pd.DataFrame({"year": years_smooth, "lead": lead_smooth})

# ── Colour palette ────────────────────────────────────────────────────────
TEAL = "#1a6b8a"
ROMAN_FILL = "#F2C4C4"      # light red/pink for Roman Empire
PLAGUE_ANTONINE = "#E8A0A0"  # medium red for Antonine Plague
PLAGUE_BLACK = "#D47878"     # darker red for Black Death
GRAY_LIGHT = "#E8E8E8"       # light gray for Industrial Revolution

# ── Output paths ──────────────────────────────────────────────────────────
IMAGE_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = IMAGE_DIR / "frozen-archives_lead_pollution.png"
SCRIPT_PATH = SCRIPT_DIR / "chart1_frozen-archives_lead_pollution.py"

# ── Annotation data frames ────────────────────────────────────────────────
# Text labels positioned manually to avoid overlap
text_labels = pd.DataFrame({
    "x":      [75,      172.5,   1350,      1860,     1970],
    "y":      [0.60,    1.80,    1.80,      0.40,     55],
    "label":  ["Pax Romana", "Antonine\nPlague", "Black\nDeath",
               "Industrial\nRevolution", "1970s\nPeak"],
    "color":  ["#8B0000", "#8B0000", "#8B0000", "#555555", TEAL],
    "hjust":  [0.5,     0.5,     0.5,       0,        0.5],
    "vjust":  [0.5,     0.5,     0.5,       0.5,      0.5],
    "size":   [10,       8.5,     8.5,       9.5,      10],
    "fontface": ["italic", "italic", "italic", "bold", "bold"],
})

# ── Build chart ───────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="year", y="lead"))

    # ── Background rectangles for historical periods ──
    # Roman Empire (15 BCE - 165 CE) — light red/pink
    + geom_rect(
        xmin=-15, xmax=165,
        ymin=0.001, ymax=np.inf,
        fill=ROMAN_FILL, alpha=0.30, color=None,
    )
    # Antonine Plague (165-180 CE) — darker red
    + geom_rect(
        xmin=165, xmax=180,
        ymin=0.001, ymax=np.inf,
        fill=PLAGUE_ANTONINE, alpha=0.45, color=None,
    )
    # Black Death (1348-1352 CE) — darker red
    + geom_rect(
        xmin=1348, xmax=1352,
        ymin=0.001, ymax=np.inf,
        fill=PLAGUE_BLACK, alpha=0.50, color=None,
    )
    # Industrial Revolution (1850 onward) — light gray
    + geom_rect(
        xmin=1850, xmax=2020,
        ymin=0.001, ymax=np.inf,
        fill=GRAY_LIGHT, alpha=0.30, color=None,
    )

    # ── Baseline: Medieval baseline at y=1 ──
    + geom_hline(yintercept=1.0, linetype="dashed",
                 color="#777777", size=0.7)
    + geom_text(
        label="Medieval baseline",
        x=-185, y=1.3,
        size=8, color="#777777", fontface="italic", hjust=0,
    )

    # ── Filled area under curve (smoothed) ──
    + geom_area(
        data=fill_df, mapping=aes(x="year", y="lead"),
        fill=TEAL, alpha=0.20,
    )

    # ── Main line ──
    + geom_line(color=TEAL, size=1.5)

    # ── Data points ──
    + geom_point(color=TEAL, size=2.0, alpha=0.6)

    # ── Text annotations for historical periods ──
    + geom_text(
        data=text_labels,
        mapping=aes(x="x", y="y", label="label", color="color",
                    hjust="hjust", vjust="vjust", size="size"),
        fontface="bold",
        show_legend=False,
    )
    # Override colour to use literal values from the column
    + scale_color_identity()
    + scale_size_identity()

    # ── X-axis ──
    + scale_x_continuous(
        breaks=[-200, 0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000],
        labels=["200 BCE", "0", "200", "400", "600", "800", "1000", "1200",
                "1400", "1600", "1800", "2000"],
        expand=[0.005, 5],
    )

    # ── Y-axis (log scale) ──
    + scale_y_log10(
        breaks=[0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50],
        labels=["0.05", "0.1", "0.2", "0.5", "1", "2", "5", "10", "20", "50"],
        expand=[0.02, 0.01],
    )

    # ── Labels & title ──
    + labs(
        title="Two Thousand Years of European Lead Pollution, Recorded in Arctic Ice",
        x="Year CE",
        y="Lead Pollution (relative to early medieval baseline)",
        caption="Source: McConnell et al. (2019), PNAS; data from 13 Arctic ice cores",
    )

    # ── Theme ──
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0,
                                margin=[0, 0, 6, 0]),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_title_y=element_text(size=12, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=10),
        axis_text_y=element_text(size=10),
        plot_caption=element_text(size=9, color="#888888", hjust=0,
                                  margin=[12, 0, 0, 0]),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
    )
)

# ── Save ──────────────────────────────────────────────────────────────────
ggsave(p, str(OUTPUT_PATH), w=1200, h=720, dpi=150, unit="px")

print(f"Chart saved to: {OUTPUT_PATH}")
print(f"Script saved to: {SCRIPT_PATH}")
