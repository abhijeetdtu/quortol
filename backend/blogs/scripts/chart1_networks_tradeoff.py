"""
Chart 1: "The Network Architect's Trade-Off"
Comparative positioning chart — grouped horizontal bar.
Efficiency vs. relative cost across biological and human-engineered networks.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe (Wong 2011).
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data ---
# Five network types with efficiency (0-1, Delaunay = 1.0) and relative cost (0-1)
data = pd.DataFrame({
    "network": [
        "Minimum Spanning\nTree (MST)",
        "Ant Gallery\nNetworks",
        "Fungal Mycorrhizal\nNetwork (AM fungi)",
        "Human Road\nNetwork (city streets)",
        "Delaunay\nTriangulation (DT)",
    ],
    "efficiency": [0.0, 0.45, 0.5, 0.6, 1.0],
    "cost": [0.0, 0.15, 0.15, 0.20, 1.0],
    "network_short": ["MST", "Ant", "Fungal", "Roads", "DT"],
})

# Sort by efficiency ascending so MST appears at bottom of horizontal chart
data = data.sort_values("efficiency", ascending=True).reset_index(drop=True)
network_order = data["network"].tolist()
data["network"] = pd.Categorical(data["network"], categories=network_order, ordered=True)

# Melt to long form for grouped bars
data_long = pd.melt(
    data,
    id_vars=["network", "network_short"],
    value_vars=["efficiency", "cost"],
    var_name="metric",
    value_name="value",
)

# Colorblind-safe palette (Wong 2011)
# Efficiency = blue #0072B2, Cost = orange #E69F00
metric_colors = {"efficiency": "#0072B2", "cost": "#E69F00"}
metric_labels = {"efficiency": "Efficiency", "cost": "Relative Cost"}

# --- Build chart ---
p = (
    ggplot(data_long, aes(x="network", y="value", fill="metric"))
    + geom_bar(stat="identity", position=position_dodge(0.7), width=0.6, alpha=0.9)
    + geom_hline(yintercept=0, size=0.3, color="#333333")
    + scale_fill_manual(
        values=metric_colors,
        labels=list(metric_labels.values()),
    )
    + coord_flip()
    + labs(
        title="The Network Architect's Trade-Off",
        subtitle=(
            "Efficiency vs. relative cost: Fungal networks rival human road networks "
            "at substantially lower cost"
        ),
        x="",
        y="Relative scale (Delaunay triangulation = 1.0)",
        fill="",
        caption=(
            "Sources: Oyarte Galvez et al. 2025 Nature; Bebber et al. 2007 Proc. R. Soc. B; "
            "Cardillo et al. 2006 Phys. Rev. E; Buhl et al. 2004; Wong 2011 colorblind-safe palette"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=12, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_y=element_blank(),
        axis_title_x=element_text(size=11, margin=[10, 0, 0, 0]),
        axis_text_x=element_text(size=10),
        axis_text_y=element_text(size=10.5),
        plot_caption=element_text(size=8.5, color="#888888", hjust=0, margin=[12, 0, 0, 0]),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=11),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
    )
    # Value labels on bars (only show for efficiency, positioned on top of bars)
    + geom_text(
        data=data_long[data_long["metric"] == "efficiency"],
        mapping=aes(label="value", group="metric"),
        stat="identity",
        position=position_dodge(0.7),
        hjust=-0.15,
        size=10,
        color="#333333",
        fontface="bold",
    )
    + geom_text(
        data=data_long[data_long["metric"] == "cost"],
        mapping=aes(label="value", group="metric"),
        stat="identity",
        position=position_dodge(0.7),
        hjust=-0.15,
        size=9,
        color="#555555",
    )
    + ylim(0, 1.25)
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "networks_chart1_tradeoff.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 1 saved to: {output_path}")
