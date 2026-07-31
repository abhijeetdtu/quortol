#!/usr/bin/env python3
"""
Chart: AI's Democratizing Effect — Grouped Bar Chart
Output: ../images/the-creativity-paradox_democratization.png (1200 × 720 px, 150 DPI)

Shows productivity/quality gains from AI assistance across three studies,
comparing less-skilled/novice workers with more-skilled/experienced workers.

Data compiled from:
  - Brynjolfsson et al. (2023) NBER — Customer Support
  - Doshi & Hauser (2024) Science Advances — Short Story Writing
  - Dell'Acqua et al. (2023) HBS — BCG Consulting
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA
# ============================================================================
df = pd.DataFrame({
    "Study": [
        "Customer Support\n(Brynjolfsson 2023)",
        "Customer Support\n(Brynjolfsson 2023)",
        "Short Story Writing\n(Doshi & Hauser 2024)",
        "Short Story Writing\n(Doshi & Hauser 2024)",
        "BCG Consulting\n(Dell'Acqua 2023)",
        "BCG Consulting\n(Dell'Acqua 2023)",
    ],
    "Skill Level": [
        "Less skilled / novice",
        "More skilled / experienced",
        "Less skilled / novice",
        "More skilled / experienced",
        "Less skilled / novice",
        "More skilled / experienced",
    ],
    "Gain": [34, 2, 10.7, 0, 43, 17],
})

# ============================================================================
# 2. STYLE CONSTANTS
# ============================================================================
LIGHT_BLUE = "#4fa3d1"
DARK_BLUE = "#1f4e79"
TEXT_COLOR = "#2c2c2c"
SOURCE_COLOR = "#888888"
BG_COLOR = "#ffffff"
GRID_COLOR = "#eaeaea"

# ============================================================================
# 3. BUILD THE CHART
# ============================================================================
p = (
    ggplot(df, aes(x="Study", y="Gain", fill="Skill Level"))
    + geom_bar(stat="identity", position=position_dodge(0.85), width=0.7)
    + geom_text(
        aes(label="Gain"),
        position=position_dodge(0.85),
        size=11,
        va="bottom",
        color=TEXT_COLOR,
    )
    + scale_fill_manual(values=[LIGHT_BLUE, DARK_BLUE])
    + ggtitle("AI's Democratizing Effect: Less Skilled Workers Gain the Most")
    + xlab("")
    + ylab("Productivity / Quality Gain (%)")
    + labs(fill="")
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold", color=TEXT_COLOR, hjust=0.5),
        axis_title_y=element_text(size=13, color=TEXT_COLOR),
        axis_text_x=element_text(size=11, color=TEXT_COLOR),
        axis_text_y=element_text(size=11, color=TEXT_COLOR),
        legend_title=element_blank(),
        legend_text=element_text(size=12, color=TEXT_COLOR),
        panel_background=element_rect(fill=BG_COLOR, color=None),
        plot_background=element_rect(fill=BG_COLOR, color=None),
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color=GRID_COLOR, size=0.5),
        panel_grid_minor=element_blank(),
        axis_line_x=element_line(color="#cccccc", size=0.5),
        axis_line_y=element_line(color="#cccccc", size=0.5),
        axis_ticks=element_blank(),
    )
    + scale_y_continuous(limits=[0, 50], expand=[0, 2])
)

# ============================================================================
# 4. SAVE
# ============================================================================
script_dir = Path(__file__).resolve().parent
output_dir = script_dir.parent / "images"
output_path = output_dir / "the-creativity-paradox_democratization.png"

ggsave(p, str(output_path), w=1200, h=720, unit="px", dpi=150)

print(f"Chart saved to: {output_path}")
print(f"Dimensions: 1200 × 720 px @ 150 DPI")
