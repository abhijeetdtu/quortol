#!/usr/bin/env python3
"""
Horizontal bar chart: Film & TV Portrayals of Major Literary Characters
=====================================================================
Generates a publication-ready 1200×720 PNG using lets-plot.

Data source: Guinness World Records, 2012
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
data = {
    "character": [
        "Dracula",
        "Sherlock Holmes",
        "Hamlet",
        "Cinderella",
        "Robin Hood",
        "Romeo",
        "Tarzan",
    ],
    "portrayals": [272, 254, 206, 136, 127, 101, 85],
}

df = pd.DataFrame(data)

# Append "(non-human)" to Dracula's display label
df["display"] = df["character"].copy()
df.loc[df["character"] == "Dracula", "display"] = "Dracula (non-human)"

# Sort ascending so that Tarzan (lowest) is at the bottom and Dracula
# (highest) is at the top when mapped to the y-axis in a horizontal bar.
df = df.sort_values("portrayals", ascending=True).reset_index(drop=True)

# Lock the y-axis order via a pandas Categorical
df["display"] = pd.Categorical(
    df["display"], categories=df["display"].tolist(), ordered=True
)

# Colour grouping: highlight only Sherlock Holmes with gold; grey for others
df["colour_group"] = df["character"].apply(
    lambda c: "Sherlock Holmes" if c == "Sherlock Holmes" else "Other"
)

# ---------------------------------------------------------------------------
# 2. Build chart
# ---------------------------------------------------------------------------
palette = {"Sherlock Holmes": "#D4A017", "Other": "#888888"}

p = (
    ggplot(df, aes(y="display", x="portrayals", fill="colour_group"))
    + geom_bar(stat="identity", width=0.65)
    + geom_text(
        aes(label="portrayals"),
        hjust=-0.30,  # place label slightly to the right of bar end
        size=11,
        color="#333333",
    )
    + scale_fill_manual(values=palette, guide="none")
    # Start x at 0 and give enough headroom for text labels (max 272 → 310)
    + scale_x_continuous(limits=[0, 310])
    + labs(
        title="Film & TV Portrayals of Major Literary Characters",
        subtitle="Sherlock Holmes leads among human characters | Source: Guinness World Records, 2012",
        x="Number of portrayals",
        y="",
        caption="Source: Guinness World Records, 2012",
    )
    + theme_minimal()
    + theme(
        plot_background=element_rect(fill="white", color=None),
        panel_background=element_rect(fill="white", color=None),
        axis_text_y=element_text(size=12, color="#333333"),
        axis_text_x=element_text(size=10, color="#555555"),
        axis_title_x=element_text(size=12, color="#333333"),
        plot_title=element_text(size=18, face="bold", color="#222222"),
        plot_subtitle=element_text(size=12, color="#555555"),
        plot_caption=element_text(size=9, color="#888888", hjust=0),
        panel_grid_major_x=element_line(color="#e8e8e8", size=0.4),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_blank(),
        panel_grid_minor_y=element_blank(),
        axis_line_x=element_line(color="#cccccc", size=0.5),
        axis_ticks_x=element_line(color="#cccccc", size=0.5),
        axis_ticks_y=element_blank(),
        plot_margin=[10, 20, 10, 10],
    )
    + ggsize(768, 461)  # yields 1200×720 px at 150 DPI with scale=1
)

# ---------------------------------------------------------------------------
# 3. Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs")
img_path = output_dir / "images" / "sherlock-holmes-legacy_portrayals_comparison.png"
script_path = (
    output_dir
    / "scripts"
    / "chart1_sherlock-holmes-legacy_portrayals_comparison.py"
)

ggsave(p, str(img_path), dpi=150, scale=1)

print(f"✅ Image  → {img_path}")
print(f"✅ Script → {script_path}")
