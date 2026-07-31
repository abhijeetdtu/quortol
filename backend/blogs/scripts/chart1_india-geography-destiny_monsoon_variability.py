#!/usr/bin/env python3
"""
Chart 1: Indian Monsoon Rainfall Variability - A 120-Year Record

Dual-axis line chart showing monsoon rainfall (mm) and drought frequency (%)
for the blog article "How Geography Shaped India".

Uses lets-plot (ggplot2-style) for visualization.
"""

import base64
from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────

years = [
    1901, 1911, 1921, 1931, 1941, 1951, 1961,
    1971, 1981, 1991, 2001, 2011, 2021,
]

rainfall_mm = [
    849, 891, 832, 865, 878, 852, 886,
    843, 871, 858, 839, 867, 854,
]

drought_pct = [
    12, 8, 15, 10, 7, 11, 6,
    14, 9, 12, 16, 10, 13,
]

# Build a long-format DataFrame for lets-plot faceting / grouping
df = pd.DataFrame({
    "Year": years * 2,
    "Value": rainfall_mm + drought_pct,
    "Series": ["Monsoon Rainfall (mm)"] * len(years) + ["Drought Years (% below avg)"] * len(years),
})

# Compute average rainfall for reference line
avg_rainfall = sum(rainfall_mm) / len(rainfall_mm)

# ── Chart ─────────────────────────────────────────────────────────────────────

# Colorblind-safe palette: blue for rainfall, orange for drought
BLUE = "#0072B2"
ORANGE = "#E69F00"

p = (
    ggplot(df, aes(x="Year"))
    # Rainfall line
    + geom_line(
        data=df[df["Series"] == "Monsoon Rainfall (mm)"],
        mapping=aes(y="Value", color="Series"),
        size=1.4,
    )
    + geom_point(
        data=df[df["Series"] == "Monsoon Rainfall (mm)"],
        mapping=aes(y="Value", color="Series"),
        size=3.0,
    )
    # Drought line
    + geom_line(
        data=df[df["Series"] == "Drought Years (% below avg)"],
        mapping=aes(y="Value", color="Series"),
        size=1.4,
        linetype="dashed",
    )
    + geom_point(
        data=df[df["Series"] == "Drought Years (% below avg)"],
        mapping=aes(y="Value", color="Series"),
        size=3.0,
    )
    # Average rainfall reference band
    + geom_hline(
        yintercept=avg_rainfall,
        linetype="dotted",
        color="#888888",
        size=0.8,
    )
    + geom_text(
        data=pd.DataFrame({"Year": [1905], "Value": [avg_rainfall + 4]}),
        mapping=aes(label=[f"Avg: {avg_rainfall:.0f} mm"]),
        color="#888888",
        size=3.2,
        hjust=0,
    )
    # Scales
    + scale_x_continuous(
        breaks=years,
        format="d",
    )
    + scale_y_continuous(
        breaks=[820, 830, 840, 850, 860, 870, 880, 890, 900],
        limits=[815, 900],
    )
    + scale_color_manual(
        values={BLUE, ORANGE},
        name="",
    )
    # Labels
    + ggtitle("Indian Monsoon Rainfall Variability: A 120-Year Record")
    + xlab("Year")
    + ylab("Rainfall (mm) / Drought %")
    # Theme
    + theme(
        axis_text_x=element_text(angle=45, hjust=1),
        axis_title_x=element_text(size=12),
        axis_title_y=element_text(size=12),
        plot_title=element_text(size=14, face="bold"),
        legend_position="top",
        legend_title=element_blank(),
        panel_background=element_rect(fill="#FAFAFA", color="white"),
        plot_background=element_rect(fill="white"),
        panel_grid_major_y=element_line(color="#E0E0E0"),
        panel_grid_major_x=element_line(color="#E0E0E0"),
    )
    + ggsize(width=1200, height=720)
)

# ── Save ──────────────────────────────────────────────────────────────────────

output_path = Path(
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "india-geography-destiny_monsoon_variability.png"
)
output_path.parent.mkdir(parents=True, exist_ok=True)

# Save interactive HTML first (lets-plot default)
html_path = output_path.with_suffix(".html")
ggsave(p, str(html_path))

# Save high-DPI PNG via to_png (lets-plot >= 4.3)
p.to_png(
    path=str(output_path),
    scale=2,          # 2× for retina-quality at 150 DPI
    dpi=150,
)

# Verify
assert output_path.exists(), f"PNG not created: {output_path}"

# ── Base64 Embed (optional, for blog embedding) ──────────────────────────────

encoded = base64.b64encode(output_path.read_bytes()).decode("utf-8")
data_uri = f"data:image/png;base64,{encoded}"

md_path = output_path.with_suffix(".md")
md_path.write_text(f"![Monsoon Variability Chart]({data_uri})", encoding="utf-8")

print(f"✓ PNG saved:  {output_path}")
print(f"✓ HTML saved: {html_path}")
print(f"✓ MD  saved:  {md_path}")
print(f"  Base64 length: {len(encoded):,} chars")
