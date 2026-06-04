"""
Chart: Google Search Referral Traffic Decline by Publisher Size
---------------------------------------------------------------
Horizontal bar chart showing the percent decline in Google Search
referral traffic over two years, segmented by publisher size.

Data source: Chartbeat via Reuters Institute 2026 Trends Report.

Uses lets-plot library with a colorblind-safe sequential blue palette
(dark blue for most impacted → light blue for least impacted).
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Build the data frame
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "Publisher Size": [
        "Small\n(1,000–10,000 daily views)",
        "Medium\n(10,000–100,000 daily views)",
        "Large\n(100,000+ daily views)",
    ],
    "decline_pct": [60, 47, 22],
})

# Sort descending so most-impacted (small) appears at the top
df = df.sort_values("decline_pct", ascending=False)

# Lock factor order so lets-plot respects the sort
df["Publisher Size"] = pd.Categorical(
    df["Publisher Size"],
    categories=df["Publisher Size"].tolist(),
    ordered=True,
)

# ---------------------------------------------------------------------------
# 2. Build the horizontal bar chart
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="decline_pct", y="Publisher Size", fill="decline_pct"))
    + geom_bar(stat="identity", width=0.6, color="white", size=0.3)
    # Data labels positioned just beyond each bar's end
    + geom_text(
        aes(label="decline_pct"),
        hjust=-0.35,
        size=12,
        color="#333333",
        family="sans-serif",
        fontface="bold",
    )
    # Colorblind-safe sequential blue palette: light blue → dark blue
    + scale_fill_gradient(low="#9ECAE1", high="#08519C")
    + scale_x_continuous(
        limits=[0, 80],
        breaks=[0, 20, 40, 60, 80],
        labels=["0%", "20%", "40%", "60%", "80%"],
    )
    + labs(
        title="Google Search Referral Traffic Decline by Publisher Size",
        subtitle="% decline over two years | Source: Chartbeat via Reuters Institute 2026",
        x="Percent decline",
        y="",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", hjust=0),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0),
        axis_text_y=element_text(size=12),
        axis_text_x=element_text(size=11),
        axis_title_x=element_text(size=12),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.5),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        legend_position="none",
        plot_margin=[10, 45, 10, 10],
    )
)

# ---------------------------------------------------------------------------
# 3. Save outputs
# ---------------------------------------------------------------------------
img_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
img_dir.mkdir(parents=True, exist_ok=True)

script_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
script_dir.mkdir(parents=True, exist_ok=True)

png_path = img_dir / "the-citation-economy_traffic_decline.png"

# 8 in × 4.8 in × 150 DPI = 1200 × 720 px
ggsave(p, str(png_path), dpi=150, w=8, h=4.8)

print(f"PNG saved → {png_path.resolve()}")
