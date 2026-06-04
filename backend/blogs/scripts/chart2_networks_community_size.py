"""
Chart 2: "Community Size in Social vs Biological Networks"
Lollipop chart comparing optimal community/cluster sizes across domains.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe (Wong 2011).
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data ---
data = pd.DataFrame({
    "network": [
        # Biological / Protein Networks
        "Yeast PPI Network",
        "Human PPI Network",
        "Fungal Mycorrhizal\nNetwork",
        # Social Networks
        "Hadza Hunter-\nGatherer Camps",
        "Facebook Networks\n(avg cluster)",
        "Dunbar's Support\nClique",
        "Dunbar's Sympathy\nGroup",
        "Dunbar's Band",
        "Dunbar's\nCommunity",
    ],
    "domain": [
        "Biological / Protein Networks",
        "Biological / Protein Networks",
        "Biological / Protein Networks",
        "Social Networks",
        "Social Networks",
        "Social Networks",
        "Social Networks",
        "Social Networks",
        "Social Networks",
    ],
    "community_size": [10, 10, 10, 40, 100, 5, 15, 50, 150],
    "citation": [
        "ASONAM 2014",
        "ASONAM 2014",
        "Ajaz et al. 2026 New Phytol.",
        "Apicella et al. 2012 Nature",
        "ASONAM 2014",
        "Hill & Dunbar 2003",
        "Hill & Dunbar 2003",
        "Hill & Dunbar 2003",
        "Hill & Dunbar 2003",
    ],
})

# Sort: biological first (by size), then social (by size)
type_order = ["Biological / Protein Networks", "Social Networks"]
data["domain"] = pd.Categorical(data["domain"], categories=type_order, ordered=True)
data = data.sort_values(["domain", "community_size"]).reset_index(drop=True)
data["network"] = pd.Categorical(data["network"], categories=data["network"].tolist(), ordered=True)

# Colorblind-safe palette (Wong 2011)
# Biological = green #009E73, Social = blue #0072B2
domain_colors = {
    "Biological / Protein Networks": "#009E73",
    "Social Networks": "#0072B2",
}

# --- Build chart (clean horizontal bar chart with lollipop-like styling) ---
p = (
    ggplot(data, aes(x="network", y="community_size", color="domain"))
    # Bars as thin columns (lollipop stems)
    + geom_bar(stat="identity", width=0.2, alpha=0.4, fill="#888888", show_legend=False)
    # Lollipop heads
    + geom_point(size=5, alpha=0.9)
    + geom_hline(yintercept=0, size=0.3, color="#333333")
    + scale_color_manual(values=domain_colors)
    + coord_flip()
    + labs(
        title="Community Size in Social vs. Biological Networks",
        subtitle=(
            "Optimal community / cluster sizes differ by an order of magnitude — "
            "biological networks cluster at ~10, social networks at 30–150"
        ),
        x="",
        y="Community size",
        color="Domain",
        caption=(
            "Sources: How Do Biological Networks Differ from Social Networks? ASONAM 2014; "
            "Ajaz et al. 2026 New Phytologist; Apicella et al. 2012 Nature; "
            "Hill & Dunbar 2003 Human Nature; Wong 2011 colorblind-safe palette"
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
    # Value labels
    + geom_text(
        mapping=aes(label="community_size"),
        hjust=-0.4,
        size=10,
        color="#333333",
        fontface="bold",
    )
    + ylim(0, 200)
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "networks_chart2_community_size.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 2 saved to: {output_path}")
