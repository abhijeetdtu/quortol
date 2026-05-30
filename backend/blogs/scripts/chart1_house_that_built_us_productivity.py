#!/usr/bin/env python3
"""
Chart 1: The Rise and Fall of American Homebuilding Productivity
Line chart with shaded area showing homes per construction worker (1900–2020),
indexed to 1970 = 100.

Sources: D'Amico et al. (2024), Goolsbee & Syverson (2023), Richmond Fed (2025)
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "Year": [1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020],
    "Productivity": [95, 92, 90, 88, 100, 160, 200, 220, 175, 155, 140, 115, 80],
})

# ---------------------------------------------------------------------------
# Annotation data frames
# ---------------------------------------------------------------------------
peak_label = pd.DataFrame({
    "Year": [1970],
    "Productivity": [220],
    "label": ["Peak productivity — then 50 years of decline"],
})

end_label = pd.DataFrame({
    "Year": [2020],
    "Productivity": [80],
    "label": ["-64% from peak"],
})

# ---------------------------------------------------------------------------
# Build plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="Year", y="Productivity"))
    # Shaded area under the line
    + geom_area(fill="#D1E5F0", alpha=0.7)
    # Line and points
    + geom_line(color="#2166AC", size=1.5)
    + geom_point(color="#2166AC", size=2.5)
    # Horizontal dashed reference line at 100 (1970 baseline)
    + geom_hline(yintercept=100, linetype="dashed", color="#888888", size=0.6)
    # Peak annotation
    + geom_text(
        aes(x="Year", y="Productivity", label="label"),
        data=peak_label,
        nudge_y=18,
        size=7.5,
        color="#222222",
        fontface="italic",
    )
    # End annotation
    + geom_text(
        aes(x="Year", y="Productivity", label="label"),
        data=end_label,
        nudge_y=-15,
        size=7.5,
        color="#222222",
        fontface="italic",
    )
    # Scales
    + scale_x_continuous(breaks=df["Year"].tolist())
    + scale_y_continuous(limits=(0, 260))
    # Labels
    + labs(
        title="The Rise and Fall of American Homebuilding Productivity",
        subtitle="Homes per construction worker, indexed to 1970 peak",
        x="Year",
        y="Productivity Index (1970 = 100)",
        caption="Sources: D'Amico et al. (2024), Goolsbee & Syverson (2023), Richmond Fed (2025)",
    )
    # Theme
    + theme_classic()
    + theme(
        plot_title=element_text(size=16, hjust=0.5, face="bold"),
        plot_subtitle=element_text(size=12, hjust=0.5, color="#555555"),
        axis_text_x=element_text(angle=45, hjust=1, size=9),
        axis_text_y=element_text(size=9),
        axis_title_x=element_text(size=11),
        axis_title_y=element_text(size=11),
        plot_caption=element_text(size=8, color="#555555", hjust=0, face="italic"),
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#EEEEEE", size=0.3),
        panel_grid_minor=element_blank(),
        axis_line=element_line(color="#CCCCCC"),
    )
)

# ---------------------------------------------------------------------------
# Save — 1200 × 720 px at 150 DPI  →  8 × 4.8 inches
# ---------------------------------------------------------------------------
script_dir = Path(__file__).resolve().parent
out_dir = script_dir.parent / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "house-that-built-us_productivity.png"

ggsave(p, str(out_path), w=8, h=4.8, unit="in", dpi=150)

# Verify
if out_path.exists():
    print(f"Saved: {out_path}")
    print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
else:
    print(f"ERROR: file was not created at {out_path}")
