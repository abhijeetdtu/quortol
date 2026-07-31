#!/usr/bin/env python3
"""
Vertical bar chart: Average daily screen time by age group (2024).
Generates: digital-slot-machine_screen_time_age.png

Data sources:
  - Common Sense Media 2024
  - Pew Research Center 2024
  - Statista 2024
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
data = {
    "age_group": [
        "Ages 2–10",
        "Ages 11–14",
        "Ages 15–18",
        "Ages 16–25",
        "Ages 25–34",
        "Ages 35–44",
        "Ages 45–54",
        "Ages 55–64",
    ],
    "hours": [2.5, 9.0, 7.5, 7.53, 7.1, 6.65, 6.12, 5.27],
}
df = pd.DataFrame(data)

# Color: orange for the highlighted teen group, blue for the rest
df["fill_color"] = df["age_group"].apply(
    lambda g: "#F59E0B" if g == "Ages 11–14" else "#2563EB"
)

# Preserve explicit order
df["age_group"] = pd.Categorical(df["age_group"], categories=df["age_group"], ordered=True)

# Pre-formatted label
df["label"] = df["hours"].apply(lambda v: f"{v:.1f}h")

# ---------------------------------------------------------------------------
# 2. Plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="age_group", y="hours"))
    + geom_bar(stat="identity", width=0.65, fill="fill_color", alpha=0.85)
    + geom_text(
        aes(label="label"),
        stat="identity",
        vjust=-0.4,
        size=10,
        color="#222222",
    )
    + scale_y_continuous(expand=[0.05, 0, 0.15, 0], limits=[0, 11])
    + labs(
        title="Average Daily Screen Time by Age Group (2024)",
        x="Age Group",
        y="Hours per Day",
        caption=(
            "Sources: Common Sense Media 2024  |  Pew Research Center 2024  |  Statista 2024"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title        = element_text(size=16, face="bold", hjust=0.5),
        axis_title_x      = element_text(size=12),
        axis_title_y      = element_text(size=12),
        axis_text_y       = element_text(size=10),
        axis_text_x       = element_text(size=10, angle=30, hjust=1),
        plot_caption      = element_text(size=8, hjust=0, color="#555555"),
        panel_grid_major_x= element_blank(),
        panel_grid_minor  = element_blank(),
    )
)

# ---------------------------------------------------------------------------
# 3. Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

png_path = output_dir / "digital-slot-machine_screen_time_age.png"
ggsave(p, str(png_path), w=1200, h=720, unit="px", dpi=150)

print(f"✓ Chart saved: {png_path}")
