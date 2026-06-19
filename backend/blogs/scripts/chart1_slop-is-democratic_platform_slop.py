"""
Chart: AI Slop Prevalence Across Digital Platforms
---------------------------------------------------
Horizontal bar chart showing the percentage of AI-generated low-quality
content observed on major social media platforms (2025–2026).

Quantified data sources:
  - TikTok (For You feed, new users): 59% — Kapwing TikTok AI Slop Report, Jun 2026
  - TikTok (Kids category):            57% — Kapwing TikTok AI Slop Report, Jun 2026
  - YouTube Shorts (new users):        21% — Kapwing YouTube AI Slop Report, Dec 2025
  - YouTube (fastest-growing channels,
    AI-only):                          10% — The Guardian analysis cited in Kapwing report

Qualitative-only data (Facebook complaints, Instagram Reels user reports)
are explicitly excluded per user request.

Uses lets-plot with a warm-to-cool colorblind-safe gradient.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Build the data frame — quantified data points only
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "platform": [
        "TikTok\n(For You feed, new users)",
        "TikTok\n(Kids category)",
        "YouTube Shorts\n(new users)",
        "YouTube\n(fastest-growing channels,\nAI-only)",
    ],
    "slop_pct": [59, 57, 21, 10],
})

# Sort descending so highest prevalence appears at the top of the chart
df = df.sort_values("slop_pct", ascending=False)

# Lock factor order so lets-plot respects the sort
df["platform"] = pd.Categorical(
    df["platform"],
    categories=df["platform"].tolist(),
    ordered=True,
)

# ---------------------------------------------------------------------------
# 2. Build the horizontal bar chart
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="slop_pct", y="platform", fill="slop_pct"))
    + geom_bar(stat="identity", width=0.55, color="white", size=0.4)
    # Data labels positioned beyond each bar's end
    + geom_text(
        aes(label="slop_pct"),
        hjust=-0.45,
        size=13,
        color="#333333",
        family="sans-serif",
        fontface="bold",
    )
    # Warm-to-cool colorblind-safe gradient: cool blue → warm red
    + scale_fill_gradient(low="#4E79A7", high="#E15759")
    + scale_x_continuous(
        limits=[0, 78],
        breaks=[0, 20, 40, 60, 80],
        labels=["0%", "20%", "40%", "60%", "80%"],
    )
    + labs(
        title='How Much of Your Feed Is "AI Slop"?',
        subtitle="Percentage of AI-generated low-quality content across platforms, 2025–2026",
        x="Share of content observed as AI-generated",
        y="",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=22, face="bold", hjust=0),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0),
        axis_text_y=element_text(size=12),
        axis_text_x=element_text(size=11),
        axis_title_x=element_text(size=12),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.5),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        legend_position="none",
        plot_margin=[10, 50, 10, 10],
    )
)

# ---------------------------------------------------------------------------
# 3. Save outputs — 8 × 4.8 inches × 150 DPI = 1200 × 720 px
# ---------------------------------------------------------------------------
img_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
img_dir.mkdir(parents=True, exist_ok=True)

script_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
script_dir.mkdir(parents=True, exist_ok=True)

png_path = img_dir / "slop-is-democratic_platform_slop.png"

ggsave(p, str(png_path), dpi=150, w=8, h=4.8)

# ---------------------------------------------------------------------------
# 4. Verification
# ---------------------------------------------------------------------------
if png_path.exists():
    print(f"✅ PNG saved → {png_path.resolve()}")
    print(f"   File size: {png_path.stat().st_size / 1024:.1f} KB")
    print(f"   Dimensions: 1200 × 720 px @ 150 DPI")
else:
    print(f"❌ ERROR: PNG was not created at {png_path.resolve()}")
