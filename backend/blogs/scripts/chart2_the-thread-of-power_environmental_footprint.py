#!/usr/bin/env python3
"""Chart 2: The Environmental Cost of What We Wear — Horizontal bar chart (two panels).

Creates a magazine-style horizontal bar chart using lets-plot showing
environmental impact metrics of the global textile industry across two panels:
  Panel A — Scale of Impact (absolute figures in various units)
  Panel B — Waste & Circularity (percentages)

Output: 1200×720 px PNG at 150 DPI.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. DATA
# ---------------------------------------------------------------------------
# Metrics in visual order (top → bottom within each panel).
metrics_top_to_bottom = [
    # ── Panel A: Scale of Impact ──
    "GHG emissions:\ntextile production",
    "GHG emissions:\nflights & shipping (comparison)",
    "Annual water\nconsumption",
    "Microplastic fibers\nreleased to ocean annually",
    "Value lost: underutilization\n& lack of recycling",
    # ── Panel B: Waste & Circularity ──
    "Textile waste sent to\nlandfill or incineration",
    "Industrial water pollution\nfrom textile dyeing",
    "Clothing recycled back\ninto new clothing",
    "Industry circularity rate\n(recycled material input)",
]

# For the y-axis, lets-plot places the first factor level at the BOTTOM.
# Reverse the visual order to get correct top-to-bottom display.
y_order = metrics_top_to_bottom[::-1]

values = [
    # Panel A
    1.2, 1.0, 93, 0.5, 500,
    # Panel B
    61, 20, 1.0, 0.3,
]

display_labels = [
    # Panel A
    "1.2 billion tonnes CO\u2082e / year",
    "1.0 billion tonnes CO\u2082e / year",
    "93 billion m\u00b3 / year",
    "0.5 million tonnes / year",
    "$500 billion / year",
    # Panel B
    "61%",
    "20%",
    "<1%",
    "0.3%",
]

panels = ["A: Scale of Impact"] * 5 + ["B: Waste & Circularity"] * 4

# Color assignment (all negative impacts — deep red family)
#   Main impacts:      dark red   #8B0000
#   Comparison metric: firebrick  #B22222  (different shade for contrast)
#   Very-low metrics:  indianred  #CD5C5C  (lighter, for <1% type values)
bar_colors = [
    "#8B0000",  # GHG textile        – dark red
    "#B22222",  # GHG comparison     – firebrick (distinct)
    "#8B0000",  # Water              – dark red
    "#8B0000",  # Microplastics      – dark red
    "#8B0000",  # Value lost         – dark red
    "#8B0000",  # Waste              – dark red
    "#8B0000",  # Water pollution    – dark red
    "#CD5C5C",  # Recycled clothing  – indianred (lighter)
    "#CD5C5C",  # Circularity rate   – indianred (lighter)
]

df = pd.DataFrame(
    {
        "metric": pd.Categorical(
            metrics_top_to_bottom, categories=y_order, ordered=True
        ),
        "value": values,
        "label": display_labels,
        "panel": pd.Categorical(
            panels,
            categories=["A: Scale of Impact", "B: Waste & Circularity"],
            ordered=True,
        ),
        "color": bar_colors,
    }
)

# ---------------------------------------------------------------------------
# 2. PLOT
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(y="metric", x="value"))
    # Horizontal bars
    + geom_bar(aes(fill="color"), stat="identity", width=0.65)
    # Value labels at end of each bar
    + geom_text(
        aes(label="label"),
        hjust=0,
        size=3.2,  # ≈ 9 pt (lets-plot uses mm for geom text)
        color="#333333",
        family="sans-serif",
        fontface="plain",
    )
    # Two vertical panels with independent axes
    + facet_grid(
        y="panel",
        scales="free",
    )
    + scale_fill_identity()
    # Leave room on the right for text labels
    + scale_x_continuous(expand=[0.18, 0])
    # Labels & captions
    + labs(
        title="The Environmental Cost of What We Wear",
        subtitle=(
            "Textile production emits more CO\u2082 than aviation and "
            "shipping combined \u2014 and almost nothing is recycled"
        ),
        caption=(
            "Sources: "
            "Ellen MacArthur Foundation (2017); "
            "UNEP (2020); "
            "Circularity Gap Report Textiles (2024)"
        ),
        x="",
        y="",
    )
    # ── Theme ──
    + theme(
        # Title: 16 pt bold
        plot_title=element_text(
            size=16, face="bold", hjust=0, family="sans-serif"
        ),
        # Subtitle: 12 pt
        plot_subtitle=element_text(
            size=12, hjust=0, color="#555555", family="sans-serif"
        ),
        # Caption at bottom: 9 pt
        plot_caption=element_text(
            size=9, hjust=0, color="#888888", family="sans-serif",
            margin=[6, 0, 0, 0],
        ),
        # Y-axis metric labels: 11 pt
        axis_text_y=element_text(
            size=11, family="sans-serif", hjust=1, vjust=0.5
        ),
        # Hide x-axis labels (values are shown as bar labels)
        axis_text_x=element_blank(),
        axis_ticks=element_blank(),
        axis_title=element_blank(),
        # Subtle gray grid lines (x-direction only, where bars extend)
        panel_grid_major_x=element_line(color="#D0D0D0", size=0.3),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_blank(),
        panel_grid_minor_y=element_blank(),
        # White backgrounds
        panel_background=element_rect(fill="white", color=None),
        plot_background=element_rect(fill="white"),
        # Panel headers (strip)
        strip_background=element_rect(fill="#F4F4F4", color="#D8D8D8"),
        strip_text_y=element_text(
            size=13, face="bold", hjust=0, family="sans-serif",
            margin=[4, 0, 4, 8],
        ),
        # Margins
        plot_margin=[12, 25, 10, 12],
        # No legend (colors are directly assigned)
        legend_position="none",
    )
)

# ---------------------------------------------------------------------------
# 3. SAVE
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-thread-of-power_environmental_footprint.png"

ggsave(
    p,
    str(output_path),
    w=8,
    h=4.8,
    unit="in",
    dpi=150,
    scale=1.0,
)

print(f"Chart saved to: {output_path.resolve()}")
