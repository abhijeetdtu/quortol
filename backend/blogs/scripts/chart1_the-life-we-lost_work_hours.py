"""
Chart 1: Daily Work/Subsistence Hours Across Four Eras
Horizontal bar chart showing work hours per day across human history.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe.
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data ---
data = pd.DataFrame({
    "era": [
        "Hunter-Gatherer\n(Hadza, both sexes)",
        "Pre-Industrial\nEngland (~1750)",
        "Industrial\nRevolution (~1800)",
        "Modern US,\nEmployed (2024)",
        "Modern US,\nAll Adults (2024)",
    ],
    "hours": [4.9, 6.8, 9.5, 7.6, 3.4],
    "note": [
        "Kraft et al. 2021",
        "Voth 1998",
        "Voth 2001",
        "BLS ATUS 2024",
        "BLS ATUS 2024",
    ],
})

# Colorblind-safe palette (Wong 2011 modified)
color_map = {
    "Hunter-Gatherer\n(Hadza, both sexes)": "#009E73",   # green-teal
    "Pre-Industrial\nEngland (~1750)": "#E69F00",         # amber
    "Industrial\nRevolution (~1800)": "#D55E00",          # red
    "Modern US,\nEmployed (2024)": "#0072B2",             # blue
    "Modern US,\nAll Adults (2024)": "#56B4E9",           # light blue
}

# Sort: ascending for horizontal bar (industrial at top)
data = data.sort_values("hours", ascending=True).reset_index(drop=True)
data["era"] = pd.Categorical(data["era"], categories=data["era"].tolist(), ordered=True)

# --- Build chart ---
p = (
    ggplot(data, aes(x="era", y="hours", fill="era"))
    + geom_bar(stat="identity", width=0.65, alpha=0.9)
    + geom_hline(yintercept=0, size=0.3, color="#333333")
    + scale_fill_manual(values=color_map, guide=None)
    + coord_flip()
    + labs(
        title="Daily Work Hours Across Four Eras",
        subtitle="Hours per day spent on work or subsistence activities",
        x="",
        y="Hours per day",
        caption="Sources: Kraft et al. 2021 Science; Voth 1998, 2001 J. Econ. History; BLS ATUS 2024",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_y=element_blank(),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=9, color="#888888", hjust=0, margin=[12, 0, 0, 0]),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
    )
    # Value labels at end of each bar
    + geom_text(
        mapping=aes(label="hours"),
        stat="identity", hjust=-0.15, size=11, color="#333333", fontface="bold",
    )
    + geom_text(
        mapping=aes(label="note"),
        stat="identity", hjust=-0.15, size=7.5, color="#888888", vjust=2.5,
    )
    # Expand y-axis to fit labels
    + ylim(0, 12.5)
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-life-we-lost_chart1_work_hours.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 1 saved to: {output_path}")
