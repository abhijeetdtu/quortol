"""
New Hampshire Accommodation GDP, 2020–2024
Line chart with filled area — lets-plot 4.9.0

Source: U.S. Bureau of Economic Analysis, FRED
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
df = pd.DataFrame({
    "Year": [2020, 2021, 2022, 2023, 2024],
    "GDP":  [670.9, 974.3, 1716.2, 2167.8, 2156.6],
})
# Pre-compute data labels for geom_text
df["label"] = df["GDP"].apply(lambda v: f"${v:.1f}M")

# ── Chart ─────────────────────────────────────────────────────────────────────
# Colorblind-safe teal palette
LINE_COLOR = "#008080"      # teal
FILL_COLOR = "#e0f0f0"      # very light teal
LABEL_COLOR = "#004040"     # dark teal for labels

p = (
    ggplot(df, aes(x="Year", y="GDP"))
    + geom_area(fill=FILL_COLOR, alpha=0.7)
    + geom_line(color=LINE_COLOR, size=1.5)
    + geom_point(color=LINE_COLOR, size=3.5)
    # Data labels positioned above each point
    + geom_text(
        aes(label="label"),
        vjust=-1.2,
        size=10,
        color=LABEL_COLOR,
        family="sans-serif",
    )
    # ── Scales ──
    + scale_x_continuous(
        breaks=[2020, 2021, 2022, 2023, 2024],
        labels=["2020", "2021", "2022", "2023", "2024"],
    )
    + scale_y_continuous(
        expand=[0, 0],
        limits=[0, 2500],
    )
    # ── Labels ──
    + ggtitle("New Hampshire Accommodation GDP, 2020–2024")
    + xlab("")
    + ylab("GDP (Millions of Dollars)")
    # ── Theme ──
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0.5),
        axis_title_y=element_text(size=13),
        axis_text=element_text(size=11),
        axis_text_x=element_text(angle=0, hjust=0.5),
        panel_grid_major_x=element_blank(),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_line(color="#e0e0e0", size=0.4),
        panel_grid_minor_y=element_blank(),
        panel_background=element_rect(fill="#fafafa"),
        plot_background=element_rect(fill="white"),
        axis_line=element_line(color="#cccccc"),
        axis_ticks=element_line(color="#cccccc"),
        plot_margin=[20, 25, 40, 15],
    )
    # Source caption at bottom
    + labs(
        caption="Source: U.S. Bureau of Economic Analysis, FRED"
    )
    + theme(
        plot_caption=element_text(
            size=9, color="#666666", hjust=0, margin=[12, 0, 0, 0]
        )
    )
)

# ── Export ─────────────────────────────────────────────────────────────────────
output_png = "/home/pi/Documents/code/quortol/backend/blogs/images/new-hampshire-bed-and-breakfasts_accommodation_gdp.png"

ggsave(
    p,
    output_png,
    w=8,
    h=4.8,
    unit="in",
    dpi=150,
)

print(f"Chart saved to: {output_png}")
