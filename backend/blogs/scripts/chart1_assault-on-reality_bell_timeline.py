"""
Chart: The Rising Certainty — Bell Test Violations Across Four Decades
Dot plot with error bars showing CHSH Bell S-parameter values across landmark experiments,
with reference lines for the local realist bound (S=2) and Tsirelson bound (S=2√2).
lets-plot 4.9.0, 1200×720 px, 150 DPI, colorblind-safe palette.

Data sources:
- Aspect, Dalibard & Roger (1982): Phys. Rev. Lett. 49, 1804
- Weihs, Zeilinger et al. (1998): Phys. Rev. Lett. 81, 5039
- Hensen, Hanson et al. (Delft, 2015): Nature 526, 682
"""

import numpy as np
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "experiment": [
        "Aspect, Dalibard & Roger",
        "Weihs, Zeilinger et al.",
        "Hensen, Hanson et al. (Delft)",
    ],
    "label": [
        "Aspect (1982)",
        "Weihs (1998)",
        "Hensen (2015)",
    ],
    "year": [1982, 1998, 2015],
    "s_value": [2.697, 2.73, 2.42],
    "error": [0.015, 0.02, 0.20],
})

data["s_min"] = data["s_value"] - data["error"]
data["s_max"] = data["s_value"] + data["error"]
data["label_y"] = data["s_value"] + 0.055  # position for value labels

# ── Colour palette (colorblind-safe) ──────────────────────────────────────
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
RED = "#CC0000"
DARK_BLUE = "#204A87"
GRAY_NEUTRAL = "#888888"
FILL_SHADE = "#D6E8D6"  # subtle green-gray for quantum nonlocality region

# ── Output paths ──────────────────────────────────────────────────────────
IMAGE_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = IMAGE_DIR / "assault-on-reality_bell_timeline.png"
SCRIPT_PATH = SCRIPT_DIR / "chart1_assault-on-reality_bell_timeline.py"

# ── Constants ──────────────────────────────────────────────────────────────
LOCAL_REALIST_BOUND = 2.0
TSIRELSON_BOUND = 2.0 * np.sqrt(2)  # ≈ 2.828

# X-range for background shapes — covers all years with padding
X_MIN = 1975
X_MAX = 2022

# ── Build chart ───────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="year", y="s_value"))

    # ── Shaded region: Quantum Nonlocality (S=2 to S=2.828) ──
    + geom_rect(
        xmin=X_MIN, xmax=X_MAX,
        ymin=LOCAL_REALIST_BOUND, ymax=TSIRELSON_BOUND,
        fill=FILL_SHADE, alpha=0.35, color=None,
    )
    + geom_text(
        label="Quantum Nonlocality",
        x=1975.5, y=2.42,
        size=9, color="#3A6B3A", fontface="italic", alpha=0.7,
        hjust=0, vjust=0.5,
    )

    # ── Local realist bound: S = 2.0 ──
    + geom_hline(yintercept=LOCAL_REALIST_BOUND, linetype="dashed",
                 color=RED, size=0.8)
    + geom_text(
        label="Local Realist Bound (S = 2)",
        x=1975.5, y=LOCAL_REALIST_BOUND + 0.02,
        size=9.5, color=RED, fontface="italic", hjust=0, vjust=0,
    )

    # ── Tsirelson bound: S = 2√2 ≈ 2.828 ──
    + geom_hline(yintercept=TSIRELSON_BOUND, linetype="dashed",
                 color=DARK_BLUE, size=0.8)
    + geom_text(
        label="Tsirelson Bound (S = 2√2 ≈ 2.828)",
        x=1975.5, y=TSIRELSON_BOUND - 0.02,
        size=9.5, color=DARK_BLUE, fontface="italic", hjust=0, vjust=1,
    )

    # ── Connecting line (temporal progression) ──
    + geom_line(color="#555555", size=0.9, linetype="solid")

    # ── Error bars (coloured by experiment) ──
    + geom_errorbar(
        aes(ymin="s_min", ymax="s_max", color="label"),
        width=2.5, size=1.3,
    )

    # ── Data points (coloured by experiment) ──
    + geom_point(
        aes(color="label"),
        size=5.5, stroke=1.5,
    )

    # ── S-value labels slightly above points ──
    + geom_text(
        aes(label="s_value", y="label_y", color="label"),
        size=9.5, fontface="bold", hjust=0.5, vjust=0,
        show_legend=False,
    )

    # ── Annotation: "Any value > 2 rules out local realism" ──
    + geom_text(
        label="Any value > 2 rules out local realism",
        x=1975.5, y=1.58,
        size=8.5, color="#666666", fontface="italic", hjust=0,
    )

    # ── Colour scale (colorblind-safe) ──
    + scale_color_manual(
        values=[BLUE, ORANGE, GREEN],
        breaks=["Aspect (1982)", "Weihs (1998)", "Hensen (2015)"],
    )

    # ── Y-axis: 1.5 to 3.0 ──
    + scale_y_continuous(
        limits=[1.5, 3.0],
        breaks=[1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00],
        labels=["1.50", "1.75", "2.00", "2.25", "2.50", "2.75", "3.00"],
        expand=[0.0, 0.0],
    )

    # ── X-axis: years with experiment labels ──
    + scale_x_continuous(
        breaks=[1982, 1998, 2015],
        labels=["Aspect\n(1982)", "Weihs\n(1998)", "Hensen\n(2015)"],
        limits=[X_MIN, X_MAX],
        expand=[0.0, 0],
    )

    # ── Labels & title ──
    + labs(
        title="The Rising Certainty: Bell Test Violations Across Four Decades",
        x="",
        y="CHSH S-Parameter",
        caption="Data from original papers: Phys. Rev. Lett. 49, 1804 (1982); "
                "Phys. Rev. Lett. 81, 5039 (1998); Nature 526, 682 (2015)",
    )

    # ── Theme ──
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", hjust=0,
                                margin=[0, 0, 10, 0]),
        axis_title_x=element_text(size=12, margin=[8, 0, 0, 0]),
        axis_title_y=element_text(size=13, margin=[0, 8, 0, 0]),
        axis_text_x=element_text(size=11, face="bold"),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=8.5, color=GRAY_NEUTRAL, hjust=0,
                                  margin=[14, 0, 0, 0]),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 25, 10, 15],
        legend_position="none",
    )
)

# ── Save ──────────────────────────────────────────────────────────────────
ggsave(p, str(OUTPUT_PATH), w=1200, h=720, dpi=150, unit="px")

print(f"Chart saved to: {OUTPUT_PATH}")
print(f"Script saved to: {SCRIPT_PATH}")
