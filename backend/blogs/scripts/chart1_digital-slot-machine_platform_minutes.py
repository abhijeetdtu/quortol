#!/usr/bin/env python3
"""
Horizontal bar chart: Average daily minutes spent on each platform (2024).
Generates: digital-slot-machine_platform_minutes.png

Data sources:
  - Statista Digital Market Outlook 2024
  - DataReportal Global Digital Overview 2024
  - Pew Research Center 2024
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
data = {
    "platform": [
        "TikTok",
        "YouTube",
        "X (Twitter)",
        "Facebook",
        "Instagram",
        "Snapchat",
        "Reddit",
    ],
    "minutes": [67, 48.7, 34.1, 39, 31, 30, 24.1],
}
df = pd.DataFrame(data)

# Sort ascending so after coord_flip() the largest bar is at the top
df = df.sort_values("minutes", ascending=True).reset_index(drop=True)

# Preserve sort order as a categorical
df["platform"] = pd.Categorical(df["platform"], categories=df["platform"], ordered=True)

# Pre-formatted label for bar-end annotation
df["label"] = df["minutes"].apply(lambda v: f"{v:.1f}")

# ---------------------------------------------------------------------------
# 2. Plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="platform", y="minutes"))
    + geom_bar(stat="identity", width=0.65, fill="#2563EB", alpha=0.85)
    + geom_text(
        aes(label="label"),
        stat="identity",
        hjust=-0.35,
        size=10,
        color="#222222",
    )
    + scale_y_continuous(expand=[0.05, 0, 0.20, 0])
    + coord_flip()
    + labs(
        title="Average Daily Minutes Spent on Each Platform (2024)",
        x="Platform",
        y="Minutes per Day",
        caption=(
            "Sources: Statista Digital Market Outlook 2024  |  "
            "DataReportal Global Digital Overview 2024  |  Pew Research Center 2024"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title        = element_text(size=16, face="bold", hjust=0.5),
        axis_title_x      = element_text(size=12),
        axis_title_y      = element_text(size=12),
        axis_text_y       = element_text(size=11),
        axis_text_x       = element_text(size=10),
        plot_caption      = element_text(size=8, hjust=0, color="#555555"),
        panel_grid_major_y= element_blank(),
        panel_grid_minor  = element_blank(),
    )
)

# ---------------------------------------------------------------------------
# 3. Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

png_path = output_dir / "digital-slot-machine_platform_minutes.png"
ggsave(p, str(png_path), w=1200, h=720, unit="px", dpi=150)

print(f"✓ Chart saved: {png_path}")
