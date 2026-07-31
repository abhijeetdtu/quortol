#!/usr/bin/env python3
"""
Line chart with points: YouTube average daily viewing time growth (2019–2026).
Generates: digital-slot-machine_youtube_growth.png

Data sources:
  - Statista Digital Market Outlook
  - eMarketer / Insider Intelligence
  - YouTube official reports
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
data = {
    "year": [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
    "minutes": [39.7, 43.7, 45.0, 46.2, 47.5, 48.7, 50.2, 51.6],
}
df = pd.DataFrame(data)

# Pre-formatted label for point annotations
df["label"] = df["minutes"].apply(lambda v: f"{v:.1f}")

# ---------------------------------------------------------------------------
# 2. Plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="year", y="minutes"))
    + geom_line(size=1.5, color="#DC2626", alpha=0.85)
    + geom_point(size=3.5, color="#DC2626", alpha=0.9)
    + geom_text(
        aes(label="label"),
        nudge_y=1.2,
        size=9,
        color="#333333",
    )
    + scale_y_continuous(expand=[0.05, 0, 0.20, 0], limits=[37, 56])
    + scale_x_continuous(breaks=df["year"].tolist())
    + labs(
        title="YouTube Average Daily Viewing Time (2019–2026)",
        x="Year",
        y="Minutes per Day",
        caption=(
            "Sources: Statista Digital Market Outlook  |  "
            "eMarketer / Insider Intelligence  |  YouTube official reports"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title        = element_text(size=16, face="bold", hjust=0.5),
        axis_title_x      = element_text(size=12),
        axis_title_y      = element_text(size=12),
        axis_text_y       = element_text(size=10),
        axis_text_x       = element_text(size=10),
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

png_path = output_dir / "digital-slot-machine_youtube_growth.png"
ggsave(p, str(png_path), w=1200, h=720, unit="px", dpi=150)

print(f"✓ Chart saved: {png_path}")
