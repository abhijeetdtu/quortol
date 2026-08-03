#!/usr/bin/env python3
"""
chart2_youtube-thumbnail-absurdity_policy_timeline.py
=====================================================
Horizontal lollipop timeline of six milestones in YouTube's escalating
fight over clickbait packaging: research, platform/product changes and
policy, 2017-2025.

Milestone label text sits on the y-axis, year position on the x-axis.
Points are colour-coded by category (Okabe-Ito palette); the two 2024
milestones are jittered by +-0.15 on the y position so dots and labels
stay clearly separated.

Output: 1200x720 px PNG at 150 DPI, colorblind-safe.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *
from PIL import Image

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Output path
# ---------------------------------------------------------------------------
IMAGE_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
image_path = IMAGE_DIR / "youtube-thumbnail-absurdity_policy_timeline.png"

# ---------------------------------------------------------------------------
# Data -- milestones: (year, y-axis label (wrapped), category)
# ---------------------------------------------------------------------------
milestones = [
    (2017,
     "Webis Clickbait Corpus released: 38,517\nposts, ~24% judged clickbait (2017)",
     "Research"),
    (2019,
     "YouTube blog announces recommendation shift\n"
     "to 'viewer satisfaction' (Jan 25, 2019)",
     "Platform/Product"),
    (2021,
     "ML clickbait detectors reach ~93\u201395%\naccuracy on curated datasets",
     "Research"),
    (2024,
     "YouTube launches 'Test & Compare' A/B\ntesting for titles & thumbnails",
     "Platform/Product"),
    (2024,
     "'Egregious clickbait' enforcement announced;\nrollout begins in India (Dec 18)",
     "Policy"),
    (2025,
     "'Repetitious content' policy renamed 'inauthentic\n"
     "content'; mass-produced AI content covered (Jul 15)",
     "Policy"),
]

df = pd.DataFrame(milestones, columns=["year", "milestone", "category"])

# Chronological rows: 2017 at top (y = 0) ... 2025 at bottom (y = 5)
df = df.sort_values("year", kind="stable").reset_index(drop=True)
df["y"] = df.index.astype(float)

# Jitter the two 2024 milestones by +-0.15 so their dots stay separated
df.loc[(df["year"] == 2024) & (df["category"] == "Platform/Product"), "y"] = 2.85
df.loc[(df["year"] == 2024) & (df["category"] == "Policy"), "y"] = 4.15

# Stems start at the left edge of the time axis
df["x_start"] = 2017

# ---------------------------------------------------------------------------
# Okabe-Ito palette by category
# ---------------------------------------------------------------------------
CAT_COLORS = {
    "Research": "#0072B2",        # blue
    "Platform/Product": "#E69F00",  # orange
    "Policy": "#D55E00",          # vermillion / red
}

# ---------------------------------------------------------------------------
# Build the chart
# ---------------------------------------------------------------------------
p = (
    ggplot(df)
    # Lollipop stems: from 2017 to each milestone year
    + geom_segment(
        aes(x="x_start", xend="year", y="y", yend="y", color="category"),
        size=0.8,
        alpha=0.35,
        show_legend=False,
    )
    # Points, colour-coded by category
    + geom_point(
        aes(x="year", y="y", color="category"),
        size=5.5,
    )
    # Year axis (2017-2025) and milestone-label axis
    + scale_x_continuous(
        breaks=[2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
        limits=[2016, 2026],
    )
    + scale_y_continuous(
        breaks=[0, 1, 2, 3, 4, 5],
        labels=list(df["milestone"]),
        limits=[-0.6, 5.6],
        trans="reverse",  # oldest milestone (2017, y=0) on top
    )
    + scale_color_manual(name="Category", values=CAT_COLORS)
    + labs(
        title="YouTube's Escalating War on Its Own Packaging",
        x="Year",
        y="",
        caption=(
            "Sources: Webis-Clickbait-17; YouTube Blog (Jan 25, 2019); "
            "arXiv 2107.12791 & 2112.08611;\n"
            "YouTube Help (Test & Compare); Google India Blog (Dec 18, 2024); "
            "YouTube Help \u2014 channel monetization policies (Jul 15, 2025)"
        ),
    )
    + theme_minimal()
    + theme(
        # White background
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
        # Vertical year guides only
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.35),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        # Axis lines
        axis_line_x=element_line(color="#333333", size=0.5),
        axis_line_y=element_blank(),
        axis_ticks=element_blank(),
        # Text elements
        axis_text_x=element_text(size=10),
        axis_text_y=element_text(
            size=8.5, hjust=1, margin=[0, 8, 0, 0],
        ),
        axis_title_x=element_text(size=11, margin=[8, 0, 0, 0]),
        axis_title_y=element_blank(),
        # Title
        plot_title=element_text(
            size=22, face="bold", hjust=0, margin=[0, 0, 10, 0]
        ),
        # Source line
        plot_caption=element_text(
            size=8, color="#777777", hjust=0, margin=[16, 0, 0, 0],
        ),
        # Legend
        legend_position="right",
        legend_title=element_text(size=10, face="bold"),
        legend_text=element_text(size=9.5),
        plot_margin=[15, 25, 5, 5],
    )
)

# ---------------------------------------------------------------------------
# Save -- 8 in x 4.8 in @ 150 DPI = 1200 x 720 px
# ---------------------------------------------------------------------------
ggsave(p, str(image_path), w=1200, h=720, dpi=150, unit="px")

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
img = Image.open(image_path)
print(f"Chart saved: {image_path}")
print(f"Dimensions: {img.width}x{img.height} px "
      f"({image_path.stat().st_size / 1024:.1f} KB)")
assert img.size == (1200, 720)
print("Done.")
