"""
Horizontal bar chart: Q4 2024 transit ridership across major U.S. systems
Uses lets-plot 4.9.0+
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---- Data ----
data = {
    "system": [
        "NYC MTA - New York City Transit (Subway)",
        "Chicago CTA (Rail + Bus)",
        "LA Metro (Rail + Bus)",
        "Washington WMATA (Rail + Bus)",
        "NYC MTA - Bus Company (Bus)",
        "Chicago Metra (Commuter Rail)",
        "NYC MTA - Staten Island Railway (Light Rail)",
    ],
    "ridership_millions": [550.8, 78.0, 68.1, 41.2, 30.1, 8.3, 1.4],
}

df = pd.DataFrame(data)

# Mark whether a system is an NYC entity
nyc_systems = [
    "NYC MTA - New York City Transit (Subway)",
    "NYC MTA - Bus Company (Bus)",
    "NYC MTA - Staten Island Railway (Light Rail)",
]
df["group"] = df["system"].apply(lambda s: "NYC" if s in nyc_systems else "Other")

# Preserve original order (largest to smallest) for the y-axis factor levels
df["system"] = pd.Categorical(df["system"], categories=df["system"].tolist(), ordered=True)

# Label text (e.g. "550.8M" for the main value)
df["label"] = df["ridership_millions"].apply(lambda v: f"{v:,.1f}")

# ---- Color palette ----
# Blue for NYC, teal-gray for other cities (colorblind-safe)
color_map = {"NYC": "#2B5F8A", "Other": "#6B8F8F"}
fill_map = {"NYC": "#2B5F8A", "Other": "#6B8F8F"}

# ---- Build plot ----
p = (
    ggplot(df, aes(x="ridership_millions", y="system", fill="group"))
    + geom_bar(stat="identity", width=0.7, color="white", size=0.3)
    # Value labels at the end of each bar
    + geom_text(
        aes(label="label"),
        nudge_x=6,  # offset so label sits just past bar end
        hjust=0,
        size=11,
        color="#333333",
        family="sans-serif",
    )
    # Title / subtitle / caption
    + ggtitle(
        "America's Transit Systems: A Tale of One Giant",
        subtitle=(
            "Quarterly ridership (Q4 2024) — NYC subway alone carries "
            "more riders than all other systems combined"
        ),
    )
    + xlab("Unlinked Passenger Trips (millions)")
    + ylab("")
    + labs(caption="Source: American Public Transportation Association, Q4 2024 Ridership Report")
    # Manual fill scale
    + scale_fill_manual(
        values=fill_map,
        guide=guide_legend(title="System Group"),
    )
    # Expand x-axis so labels fit comfortably
    + xlim(0, 630)
    # Theme tweaks
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0, margin=[0, 0, 18, 0]),
        axis_title_x=element_text(size=13),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=10, color="#888888", hjust=1, margin=[12, 0, 0, 0]),
        legend_position="top",
        legend_direction="horizontal",
        legend_title=element_text(size=11),
        legend_text=element_text(size=11),
        panel_grid_major_y=element_blank(),
        panel_grid_minor_x=element_blank(),
        axis_line_x=element_line(color="#cccccc", size=0.4),
    )
)

# ---- Save ----
output_dir = "/home/pi/Documents/code/quortol/backend/blogs/images"
output_file = "nyc-contradiction-city_transit_ridership.png"
output_path = ggsave(
    p,
    output_file,
    path=output_dir,
    w=8,
    h=4.8,
    dpi=150,
)

print(f"Chart saved to: {output_path}")
