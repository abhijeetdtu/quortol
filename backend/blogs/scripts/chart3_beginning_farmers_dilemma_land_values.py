#!/usr/bin/env python3
"""
Chart: U.S. Farm Real Estate Values by Region (2025)
Horizontal bar chart using lets-plot.

Data source: USDA NASS, Land Values 2025 Summary
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────
data = {
    "region": [
        "Corn Belt", "Pacific", "Northeast", "Lake States", "Southeast",
        "Appalachian", "Delta States", "Northern Plains", "Southern Plains",
        "Mountain",
    ],
    "value": [8250, 8210, 7300, 6690, 5750, 5590, 3930, 3200, 2880, 1660],
}
df = pd.DataFrame(data)

# Sort ascending so the highest value appears at top after coord_flip
df = df.sort_values("value", ascending=True).reset_index(drop=True)
df["region"] = pd.Categorical(
    df["region"], categories=df["region"].tolist(), ordered=True
)

# Formatted dollar labels for each bar
df["dollar_label"] = df["value"].apply(lambda x: f"${x:,.0f}")

# ── Color assignment ──────────────────────────────────────────────────────
def value_to_blue(val):
    """Map a value to a sequential blue gradient (light → dark, low → high)."""
    v_min, v_max = 1660, 8250
    t = (val - v_min) / (v_max - v_min)
    r = int(0xF7 + (0x08 - 0xF7) * t)  # F7..08
    g = int(0xFB + (0x30 - 0xFB) * t)  # FB..30
    b = int(0xFF + (0x6B - 0xFF) * t)  # FF..6B
    return f"#{r:02X}{g:02X}{b:02X}"

df["bar_color"] = df.apply(
    lambda row: "#E8A05E" if row["region"] == "Mountain"
    else value_to_blue(row["value"]),
    axis=1,
)

# ── Build plot ────────────────────────────────────────────────────────────
p = (
    ggplot(df, aes(x="region", y="value"))
    + geom_bar(
        aes(fill="bar_color"), stat="identity", width=0.7, show_legend=False
    )
    + scale_fill_identity()
    + geom_text(
        aes(label="dollar_label"),
        hjust=-0.1,
        size=10.5,
        color="#333333",
    )
    # Reference line at the national average
    + geom_hline(
        yintercept=4350, color="#D62728", linetype="dashed", size=0.8
    )
    # Annotation label for the reference line (via a separate DataFrame)
    + geom_text(
        aes(label="lbl"),
        data=pd.DataFrame({
            "region": pd.Categorical(["Corn Belt"],
                                     categories=df["region"].cat.categories,
                                     ordered=True),
            "value": [4350],
            "lbl": ["U.S. Average: $4,350"],
        }),
        color="#D62728",
        hjust=-0.1,
        vjust=-1.5,
        size=9.5,
    )
    + coord_flip()
    + scale_y_continuous(
        labels=lambda bx: [f"${v:,.0f}" for v in bx],
    )
    + labs(
        title="U.S. Farm Real Estate Values by Region (2025)",
        subtitle="Average value of land and buildings per acre",
        x="",
        y="Dollars per Acre",
        caption="Source: USDA NASS, Land Values 2025 Summary",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", margin=[0, 0, 5, 0]),
        plot_subtitle=element_text(
            size=13, color="#555555", margin=[0, 0, 20, 0]
        ),
        axis_text_y=element_text(size=12, face="bold", color="#333333"),
        axis_text_x=element_text(size=11, color="#555555"),
        axis_title_x=element_text(size=13, margin=[8, 0, 0, 0]),
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.5),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        legend_position="none",
        plot_margin=[20, 30, 10, 25],
        plot_caption=element_text(
            size=9, color="#888888", margin=[10, 0, 0, 0]
        ),
        plot_background=element_rect(fill="#FAFAFA", color=None),
    )
)

# ── Save ──────────────────────────────────────────────────────────────────
img_dir = Path(
    "/home/pi/Documents/code/quortol/backend/blogs/images"
)
img_dir.mkdir(parents=True, exist_ok=True)
img_path = (
    img_dir / "beginning-farmers-dilemma_land_values.png"
)

ggsave(p, str(img_path), dpi=150, w=1200, h=720, unit="px")

print(f"✓ Chart saved: {img_path}")
print(f"  Dimensions: 1200×720 px @ 150 DPI")
