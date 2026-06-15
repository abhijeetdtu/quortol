#!/usr/bin/env python3
"""
Grouped bar chart: "Unskilled and Unaware of It"
================================================
Actual vs. self-estimated performance percentiles by quartile,
replicating the Dunning-Kruger effect from Kruger & Dunning (1999),
Journal of Personality and Social Psychology, 77(6), 1121–1134.

Output: ../images/the-entropy-of-knowing_dunning_kruger_calibration.png
        1200 × 720 px @ 150 DPI
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA  (Kruger & Dunning 1999, Studies 1-4: humor, grammar, logic)
# ============================================================================
# Actual test performance percentiles vs. self-estimated percentiles
df = pd.DataFrame({
    "quartile_label": ["Q1 (Bottom)", "Q2", "Q3", "Q4 (Top)"] * 2,
    "group":          (["Actual Performance"] * 4) + (["Self-Estimated Performance"] * 4),
    "percentile":     [12, 38, 62, 86, 62, 58, 65, 70],
})

# Ensure categorical ordering
df["quartile_label"] = pd.Categorical(
    df["quartile_label"],
    categories=["Q1 (Bottom)", "Q2", "Q3", "Q4 (Top)"],
    ordered=True,
)
df["group"] = pd.Categorical(
    df["group"],
    categories=["Actual Performance", "Self-Estimated Performance"],
    ordered=True,
)

# ============================================================================
# 2. COLOR PALETTE  (colorblind-safe blue and orange)
# ============================================================================
ACTUAL_BLUE    = "#1E6F9F"   # deep blue
ESTIMATED_ORANGE = "#E69F00" # orange (colorblind-safe)
TEXT_COLOR     = "#2C2C2C"
SOURCE_COLOR   = "#888888"
GRID_COLOR     = "#E0E0E0"
BG_COLOR       = "#FFFFFF"
HALF_LINE_COLOR = "#888888"

# ============================================================================
# 3. BUILD THE CHART
# ============================================================================

# -- Helper: position dodge so text aligns with bar centers --
dodge = position_dodge(0.9)

p = (
    ggplot(df, aes(x="quartile_label", y="percentile", fill="group"))
    # Grouped bars
    + geom_bar(stat="identity", position=dodge, width=0.7, color="white", size=0.3)
    # Value labels on top of each bar
    + geom_text(
        aes(label="percentile"),
        position=dodge,
        size=10,
        va="bottom",
        color=TEXT_COLOR,
        fontstyle="bold",
    )
    # Horizontal reference line at the 50th percentile ("average")
    + geom_hline(yintercept=50, linetype="dashed", color=HALF_LINE_COLOR, size=0.7)
    # Scales
    + scale_fill_manual(
        values=[ACTUAL_BLUE, ESTIMATED_ORANGE],
        labels=["Actual Performance", "Self-Estimated Performance"],
    )
    + scale_y_continuous(
        breaks=list(range(0, 101, 10)),
        limits=[0, 105],
        expand=False,
    )
    + scale_x_discrete()
    # Labels
    + labs(
        title="Unskilled and Unaware of It",
        subtitle="Actual vs. Self-Estimated Performance by Quartile (Kruger & Dunning, 1999)",
        x="Performance Quartile",
        y="Percentile",
        fill=None,
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_background=element_rect(fill=BG_COLOR, color=None),
        # Grid: light gray on y-axis only
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color=GRID_COLOR, size=0.35),
        panel_grid_minor=element_blank(),
        axis_line=element_blank(),
        axis_ticks=element_blank(),
        # Title
        plot_title=element_text(
            size=22, face="bold", color=TEXT_COLOR, hjust=0,
            margin=[10, 0, 4, 0],
        ),
        plot_subtitle=element_text(
            size=13, color=TEXT_COLOR, hjust=0,
            margin=[0, 0, 12, 0],
        ),
        # Axis titles
        axis_title_x=element_text(size=13, color=TEXT_COLOR, margin=[10, 0, 0, 0]),
        axis_title_y=element_text(size=13, color=TEXT_COLOR, margin=[0, 8, 0, 0]),
        # Axis tick labels
        axis_text_x=element_text(size=12, color=TEXT_COLOR),
        axis_text_y=element_text(size=11, color=TEXT_COLOR),
        # Legend at top
        legend_position="top",
        legend_direction="horizontal",
        legend_justification=[0.5, 0],
        legend_text=element_text(size=12, color=TEXT_COLOR),
        legend_key_size=18,
        legend_spacing=10,
        plot_margin=[10, 15, 10, 10],
    )
    # -- Caption / source line --
    + labs(
        caption="Data source: Kruger & Dunning (1999), JPSP, 77(6), 1121–1134. Studies 1–4 (humor, grammar, logic)."
    )
    + theme(
        plot_caption=element_text(
            size=9, color=SOURCE_COLOR, hjust=0, face="italic",
            margin=[8, 0, 0, 0],
        ),
    )
)

# ============================================================================
# 4. SAVE  — 8 in × 4.8 in @ 150 DPI = 1200 × 720 px
# ============================================================================
script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_png = images_dir / "the-entropy-of-knowing_dunning_kruger_calibration.png"

ggsave(p, str(output_png), dpi=150, w=8, h=4.8)

print(f"✓ Chart saved to {output_png}")
print(f"  Dimensions: {8 * 150} × {int(4.8 * 150)} px  @  150 DPI")
