#!/usr/bin/env python3
"""
Chart: 800,000 Years of Atmospheric CO₂ from Antarctic Ice Cores

Shows natural CO₂ variation across eight glacial cycles (173–300 ppm)
from EPICA Dome C, Vostok, and other Antarctic ice cores, compiled by
Lüthi et al. (2008) and Bereiter et al. (2015).  The last five data
points capture the anthropogenic spike after the Industrial Revolution.

Output: 1200×720 px PNG at 150 DPI
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# =====================================================================
# 1. DATA — 800 kyr of CO₂ from Antarctic ice cores
# =====================================================================

data = [
    (800, 195), (795, 200), (790, 210), (785, 220), (780, 240),
    (775, 260), (770, 275), (765, 280), (760, 270), (755, 250),
    (750, 230), (745, 210), (740, 195), (735, 190), (730, 185),
    (725, 180), (720, 178), (715, 180), (710, 185), (705, 190),
    (700, 195), (695, 200), (690, 210), (685, 220), (680, 235),
    (675, 250), (670, 265), (667, 173.7), (665, 175), (660, 180),
    (655, 185), (650, 190), (645, 210), (640, 230), (635, 250),
    (630, 270), (625, 285), (620, 275), (615, 260), (610, 245),
    (605, 225), (600, 210), (595, 195), (590, 185), (585, 180),
    (580, 185), (575, 190), (570, 200), (565, 210), (560, 225),
    (555, 240), (550, 260), (545, 275), (540, 285), (535, 280),
    (530, 265), (525, 250), (520, 230), (515, 215), (510, 200),
    (505, 190), (500, 185), (495, 180), (490, 185), (485, 190),
    (480, 200), (475, 215), (470, 230), (465, 250), (460, 270),
    (455, 280), (450, 290), (445, 280), (440, 265), (435, 245),
    (430, 225), (425, 210), (420, 195), (415, 185), (410, 180),
    (405, 185), (400, 195), (395, 210), (390, 225), (385, 245),
    (380, 265), (375, 280), (370, 290), (365, 280), (360, 265),
    (355, 245), (350, 225), (345, 210), (340, 195), (335, 185),
    (330, 180), (325, 185), (320, 190), (315, 200), (310, 215),
    (305, 230), (300, 250), (295, 270), (290, 285), (285, 290),
    (280, 280), (275, 265), (270, 245), (265, 225), (260, 210),
    (255, 195), (250, 185), (245, 180), (240, 185), (235, 190),
    (230, 200), (225, 215), (220, 235), (215, 255), (210, 275),
    (205, 290), (200, 280), (195, 265), (190, 245), (185, 225),
    (180, 210), (175, 195), (170, 185), (165, 180), (160, 185),
    (155, 190), (150, 200), (145, 215), (140, 230), (135, 250),
    (130, 270), (125, 285), (120, 275), (115, 260), (110, 240),
    (105, 220), (100, 205), (95, 190), (90, 185), (85, 180),
    (80, 185), (75, 190), (70, 200), (65, 215), (60, 230),
    (55, 250), (50, 270), (45, 285), (40, 280), (35, 260),
    (30, 240), (25, 215), (20, 195), (15, 190), (12, 265),
    (11, 270), (10, 265), (9, 260), (8, 275), (7, 280),
    (6, 285), (5, 290), (4, 285), (3, 280), (2, 280),
    (1, 285), (0.8, 280), (0.6, 278), (0.4, 275), (0.2, 280),
    (0.1, 285), (0.05, 310), (0.02, 380), (0.01, 360),
    (0.005, 390), (0.002, 410), (0.001, 420),
]

df = pd.DataFrame(data, columns=["kyr_BP", "CO2_ppm"])

# Mark the industrial-era spike: last 5 data points
MODERN_N = 5
df["era"] = "Natural"
df.iloc[-MODERN_N:, df.columns.get_loc("era")] = "Modern"

# =====================================================================
# 2. COLOR PALETTE (colorblind-safe)
# =====================================================================

COLOR_BASELINE = "#2a7a5a"   # teal/green for natural variation
COLOR_MODERN   = "#d62728"   # red/orange for anthropogenic spike
COLOR_HLINE    = "#777777"   # grey dashed reference lines
COLOR_HLINE_LBL = "#666666"  # reference line label color

# =====================================================================
# 3. BUILD PLOT
# =====================================================================

# Annotation data for text labels placed at specific coordinates
#   x in kyr BP (reversed: 800 = left, 0 = right)
#   y in ppm

annot_cycles = pd.DataFrame({
    "x": [420], "y": [405],
    "label": ["Eight glacial cycles"],
})

annot_spike  = pd.DataFrame({
    "x": [2], "y": [445],
    "label": ["Industrial spike"],
})

hline_280    = pd.DataFrame({
    "x": [620], "y": [288],
    "label": ["Pre-industrial level (280 ppm)"],
})

hline_174    = pd.DataFrame({
    "x": [620], "y": [180],
    "label": ["Record low (MIS 16)"],
})

p = (
    ggplot()
    # --- Filled area under the full curve (teal, semi-transparent) ---
    + geom_area(
        data=df,
        mapping=aes(x="kyr_BP", y="CO2_ppm"),
        fill=COLOR_BASELINE,
        alpha=0.3,
    )
    # --- Baseline line for the full record (teal) ---
    + geom_line(
        data=df,
        mapping=aes(x="kyr_BP", y="CO2_ppm"),
        color=COLOR_BASELINE,
        size=0.85,
    )
    # --- Overlaid line for the anthropogenic spike (last 5 points, red) ---
    + geom_line(
        data=df[df["era"] == "Modern"],
        mapping=aes(x="kyr_BP", y="CO2_ppm"),
        color=COLOR_MODERN,
        size=1.15,
    )
    # --- Horizontal reference lines ---
    + geom_hline(
        yintercept=280,
        color=COLOR_HLINE,
        linetype="dashed",
        size=0.55,
    )
    + geom_hline(
        yintercept=173.7,
        color=COLOR_HLINE,
        linetype="dashed",
        size=0.55,
    )
    # --- Reference line labels ---
    + geom_text(
        data=hline_280,
        mapping=aes(x="x", y="y", label="label"),
        hjust=0, size=8.5, color=COLOR_HLINE_LBL,
    )
    + geom_text(
        data=hline_174,
        mapping=aes(x="x", y="y", label="label"),
        hjust=0, size=8.5, color=COLOR_HLINE_LBL,
    )
    # --- Annotations ---
    + geom_text(
        data=annot_cycles,
        mapping=aes(x="x", y="y", label="label"),
        size=11, color=COLOR_BASELINE,
        fontstyle="italic",
    )
    + geom_label(
        data=annot_spike,
        mapping=aes(x="x", y="y", label="label"),
        size=9, color="#b31515",
        fill="#fff5f0",
        label_size=0.4,
        label_padding=0.35,
    )
    # --- Axes ---
    + scale_x_reverse(
        name="Thousands of Years Before Present (kyr BP)",
        breaks=[800, 600, 400, 200, 0],
        expand=[0.008, 0],
    )
    + scale_y_continuous(
        name="CO\u2082 Concentration (ppm)",
        limits=[140, 460],
        breaks=[150, 200, 250, 300, 350, 400, 450],
        expand=[0.005, 0],
    )
    # --- Titles & caption ---
    + labs(
        title="800,000 Years of Atmospheric CO\u2082 from Antarctic Ice Cores",
        subtitle=(
            "Natural CO\u2082 ranged from 173 to 300 ppm \u2014 "
            "until the Industrial Revolution"
        ),
        caption=(
            "Sources: L\u00fcthi et al. (2008), Nature; "
            "Bereiter et al. (2015), GRL; NOAA Mauna Loa"
        ),
    )
    # --- Theme ---
    + theme_minimal()
    + theme(
        plot_title       = element_text(size=16, face="bold"),
        plot_subtitle    = element_text(size=10.5, color="#555555"),
        plot_caption     = element_text(size=7.5, color="#999999"),
        axis_title_x     = element_text(size=10.5),
        axis_title_y     = element_text(size=10.5),
        axis_text        = element_text(size=9),
        plot_margin      = [15, 20, 10, 10],
        panel_grid_major_x = element_line(color="#E8E8E8", size=0.35),
        panel_grid_minor = "blank",
        panel_background = element_rect(fill="#FAFAFA", color=None),
        plot_background  = element_rect(fill="white", color=None),
    )
    # Remove legend (colors are self-explanatory from labels)
    + guides(color="none", fill="none")
)

# =====================================================================
# 4. SAVE
# =====================================================================

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

png_path = output_dir / "frozen-archives_co2_800kyr.png"

# 1200 × 720 px at 150 DPI  →  8 × 4.8 inches
ggsave(p, str(png_path), w=8, h=4.8, unit="in", dpi=150)

print(f"Chart saved to: {png_path}")
