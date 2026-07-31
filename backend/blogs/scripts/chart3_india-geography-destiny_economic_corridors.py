#!/usr/bin/env python3
"""
India's Economic Corridors — Investment Scale (USD Billions)
Chart for the "Geography Shaped India" blog post.

Vertical bar chart, sorted largest to smallest, with value labels on top.
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# --- Data (sorted largest → smallest) ---
data = {
    "Corridor": [
        "Delhi-Mumbai Industrial Corridor",
        "Chennai-Bengaluru Industrial Corridor",
        "Amritsar-Kolkata Industrial Corridor",
        "Vizag-Chennai Industrial Corridor",
        "Hybrid Multi-Modal Corridor",
        "Bengaluru-Mumbai Economic Corridor",
        "Hyderabad-Nagpur Industrial Corridor",
        "Kalinganagar Industrial Corridor",
    ],
    "Investment (USD Bn)": [90, 25, 20, 15, 12, 10, 8, 5],
}

df = pd.DataFrame(data)

# Use corridor name as ordered factor so bars stay sorted
df["Corridor"] = pd.Categorical(
    df["Corridor"], categories=df["Corridor"][::-1], ordered=True
)

# --- Colour-blind-safe teal ---
TEAL = "#007C7A"

# --- Build chart ---
p = (
    ggplot(df, aes(x="Corridor", y="Investment (USD Bn)"))
    + geom_bar(stat="identity", fill=TEAL, width=0.7)
    + geom_text(
        aes(label="Investment (USD Bn)"),
        va="bottom",
        nudge_y=1.5,
        size=12,
        fontface="bold",
        color="#333333",
    )
    + scale_x_discrete(expand=[0.08, 0.08])
    + scale_y_continuous(expand=[0, 0, 0.12, 0])
    + ggsize(1200, 720)
    + ggtitle("India's Economic Corridors: Investment Scale (USD Billions)")
    + xlab("")
    + ylab("Investment (USD Billions)")
    + labs(
        caption="Source: NICDC, Delhi-Mumbai Industrial Corridor Development Corporation, 2024"
    )
    + theme(
        plot_background=element_rect(fill="white", color="white"),
        panel_background=element_rect(fill="white", color="white"),
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#e0e0e0", size=0.5),
        axis_text_x=element_text(size=10, angle=25, hjust=1, color="#333333"),
        axis_text_y=element_text(size=11, color="#555555"),
        axis_title_y=element_text(size=12, color="#333333"),
        plot_title=element_text(size=16, face="bold", color="#222222"),
        axis_line_y=element_line(color="#cccccc"),
        axis_line_x=element_line(color="#cccccc"),
        axis_ticks_y=element_blank(),
        axis_ticks_x=element_blank(),
        plot_caption=element_text(size=8, color="#888888"),
        plot_margin=[0.5, 0.4, 0.3, 0.4],
    )
)

out = "/home/pi/Documents/code/quortol/backend/blogs/images/india-geography-destiny_economic_corridors.png"
# 1200 px ÷ 150 dpi = 8 inches;  720 px ÷ 150 dpi = 4.8 inches
ggsave(p, path="/home/pi/Documents/code/quortol/backend/blogs/images",
       filename="india-geography-destiny_economic_corridors.png",
       w=8, h=4.8, dpi=150, scale=1)
print(f"Saved → {out}")
