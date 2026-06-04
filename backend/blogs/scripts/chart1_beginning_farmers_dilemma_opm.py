"""
Chart: U.S. Farms at High Financial Risk, by Type (2023)
--------------------------------------------------------
Horizontal bar chart showing the percentage of farms operating in the
"high-risk" zone (Operating Profit Margin < 10%) by farm type.

Data source: USDA ERS, America's Farms and Ranches at a Glance,
2024 Edition (EIB-283), Figure 3.

Uses lets-plot library for a clean, magazine-style design with a
colorblind-safe sequential palette (dark red → light orange).
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Build the data frame
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "Farm Type": [
        "Retirement\n(small family)",
        "Off-farm occupation\n(small family)",
        "Low-sales\n(small family)",
        "Moderate-sales\n(small family)",
        "Nonfamily farms",
        "Midsize family farms",
        "Large family farms",
        "Very large family farms",
    ],
    "pct": [85, 70, 65, 52, 53, 39, 34, 29],
})

# Sort descending so Retirement (highest risk) appears at the top
df = df.sort_values("pct", ascending=False)

# Lock factor order so lets-plot respects the sort
df["Farm Type"] = pd.Categorical(
    df["Farm Type"],
    categories=df["Farm Type"].tolist(),
    ordered=True,
)

# ---------------------------------------------------------------------------
# 2. Build the horizontal bar chart
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="pct", y="Farm Type", fill="pct"))
    + geom_bar(stat="identity", width=0.7, color="white", size=0.3)
    # Data labels positioned just beyond each bar's end
    + geom_text(
        aes(label="pct"),
        hjust=-0.35,
        size=11,
        color="#333333",
        family="sans-serif",
    )
    # Colorblind-safe sequential gradient: dark red (high risk) → light orange (low risk)
    + scale_fill_gradient(low="#FDAE61", high="#A50F15")
    + scale_x_continuous(limits=[0, 100], breaks=[0, 20, 40, 60, 80, 100])
    + labs(
        title="U.S. Farms at High Financial Risk, by Type (2023)",
        subtitle="Percentage of farms with Operating Profit Margin below 10%",
        x="Percentage of Farms at High-Risk OPM (<10%)",
        y="",
        caption=(
            "Source: USDA ERS, America's Farms and Ranches at a Glance,"
            " 2024 Edition (EIB-283)"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0),
        axis_text_y=element_text(size=12),
        axis_text_x=element_text(size=11),
        axis_title_x=element_text(size=12),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.5),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        plot_caption=element_text(
            size=9.5, color="#888888", hjust=0, margin=[12, 0, 0, 0]
        ),
        legend_position="none",
        plot_margin=[10, 35, 10, 10],
    )
)

# ---------------------------------------------------------------------------
# 3. Save outputs
# ---------------------------------------------------------------------------
img_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
img_dir.mkdir(parents=True, exist_ok=True)

script_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
script_dir.mkdir(parents=True, exist_ok=True)

png_path = img_dir / "beginning-farmers-dilemma_high_risk_opm.png"

# 8 in × 4.8 in × 150 DPI = 1200 × 720 px
# (w/h parameters are in inches by default in lets-plot)
ggsave(p, str(png_path), dpi=150, w=8, h=4.8)

print(f"PNG saved → {png_path.resolve()}")
