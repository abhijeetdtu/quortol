"""
Chart 1: Coffee Shops per 100,000 Residents — Top U.S. Cities vs. National Average
Horizontal bar chart using lets-plot 4.9.0.
Colorblind-safe palette; Portland highlighted in dark orange; national average in gray.
1200 × 720 px, 150 DPI.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "city": [
        "National Average",
        "Seattle, WA",
        "San Francisco, CA",
        "Denver, CO",
        "San Diego, CA",
        "Las Vegas, NV",
        "Portland, OR",
        "San Jose, CA",
    ],
    "shops_per_100k": [12.6, 17.4, 17.4, 20.5, 20.8, 25.9, 27.8, 29.6],
})

# Sort ascending: national average first, highest last
df = df.sort_values("shops_per_100k", ascending=True).reset_index(drop=True)

# Preserve order on the y-axis (top = national avg, bottom = highest)
df["city"] = pd.Categorical(df["city"], categories=df["city"].tolist(), ordered=True)

# ---------------------------------------------------------------------------
# Color palette (colorblind-safe, Wong 2011 modified)
# ---------------------------------------------------------------------------
color_map = {
    "National Average":       "#999999",   # gray
    "Seattle, WA":            "#0072B2",   # blue
    "San Francisco, CA":      "#56B4E9",   # light blue
    "Denver, CO":             "#009E73",   # green
    "San Diego, CA":          "#E69F00",   # amber
    "Las Vegas, NV":          "#CC79A7",   # pink
    "Portland, OR":           "#D55E00",   # dark orange — highlight
    "San Jose, CA":           "#F0E442",   # yellow
}

# ---------------------------------------------------------------------------
# Reference-line label data (single row for annotation)
# ---------------------------------------------------------------------------
ref_label = df.iloc[[0]].copy()  # "National Average" row, value = 12.6
ref_label["label_text"] = "National Avg: 12.6"

# ---------------------------------------------------------------------------
# Build chart
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="city", y="shops_per_100k", fill="city"))
    + geom_bar(stat="identity", width=0.65, alpha=0.9)
    # Vertical reference line at national average (geom_hline becomes vertical after coord_flip)
    + geom_hline(yintercept=12.6, color="#555555", size=0.55, linetype="dashed")
    # Reference line label — uses the National Average data row; label appears
    # at x="National Average" (category) and y=12.6 (value). After coord_flip
    # this becomes y="National Average" on the vertical axis, x=12.6 on horizontal.
    + geom_text(
        data=ref_label,
        mapping=aes(x="city", y="shops_per_100k", label="label_text"),
        size=9, color="#555555", fontface="bold",
        hjust=-0.15, vjust=-1.5,
        inherit_aes=False,
    )
    # Value labels at end of each bar
    + geom_text(
        mapping=aes(label="shops_per_100k"),
        stat="identity", hjust=-0.25, size=10.5, color="#333333", fontface="bold",
    )
    + scale_fill_manual(values=color_map, guide="none")
    + coord_flip()
    + labs(
        title="Coffee Shops per 100,000 Residents, 2024",
        subtitle="Portland has 27.8 coffee shops per 100K — more than double the national average",
        x="",
        y="Coffee shops per 100,000 residents",
        caption="Source: ListWithClever 2024",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_y=element_blank(),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11, face="bold"),
        plot_caption=element_text(size=9, color="#888888", hjust=0, margin=[12, 0, 0, 0]),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
    )
    # Expand the value axis (y before flip, x after flip) to leave room for labels
    + scale_y_continuous(limits=[0, 37], expand=[0, 0])
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "portland-coffee-capital_chart1_density.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 1 saved to: {output_path}")
