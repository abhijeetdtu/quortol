#!/usr/bin/env python3
"""
Chart 2: Oregon's Coffee Economy — Industry Growth
Clustered bar chart (no facets — avoids lets-plot ggsave facet bug).
1200 × 720 px @ 150 DPI.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

IMG_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Build data: each metric-year combo is its own row.
# We place all bars side-by-side by using a combined x-axis label.
df = pd.DataFrame({
    "group":       ["Market Size ($B)", "Market Size ($B)",
                    "Establishments",   "Establishments",
                    "Employees",        "Employees"],
    "year":        ["2021", "2026"] * 3,
    "value":       [1.37, 1.40, 1900, 2294, 19000, 23070],
    "label":       ["$1.37B", "$1.40B",
                    "1,900", "2,294",
                    "19,000", "23,070"],
})

# Build a single categorical x-axis that interleaves: "Market Size ($B)\n2021", etc.
df["x_label"] = df["group"] + "\n" + df["year"]

# Ensure order: Market Size -> Establishments -> Employees, 2021 then 2026 within each
order = []
for g in ["Market Size ($B)", "Establishments", "Employees"]:
    order.append(f"{g}\n2021")
    order.append(f"{g}\n2026")
df["x_label"] = pd.Categorical(df["x_label"], categories=order, ordered=True)

COLORS = {"2021": "#0072B2", "2026": "#D55E00"}

p = (
    ggplot(df, aes(x="x_label", y="value", fill="year"))
    + geom_bar(stat="identity", width=0.6)
    + geom_text(
        aes(label="label"),
        vjust=-0.4, size=10, color="#333333",
    )
    + scale_fill_manual(values=COLORS, guide="none")
    + scale_y_continuous(expand=[0.18, 0])
    + labs(
        title="Oregon's Coffee Economy, 2021\u20132026",
        subtitle=(
            "Coffee & Snack Shops: $1.4B market, 2,294 establishments, 23,070 employees | "
            "Coffee Production (2026): $369.5M, 805 businesses"
        ),
        x="", y="",
        caption="Source: IBISWorld 2026",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=19, face="bold", hjust=0.5, color="#222222",
                                margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=11, hjust=0.5, color="#666666",
                                   margin=[0, 0, 16, 0]),
        plot_caption=element_text(size=9, color="#999999", hjust=0.5,
                                  margin=[6, 0, 0, 0]),
        axis_text_x=element_text(size=11, face="bold", color="#333333", hjust=0.5),
        axis_text_y=element_text(size=10, color="#555555"),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.35),
        plot_margin=[10, 15, 10, 15],
        panel_background=element_rect(fill="white", color=None),
        plot_background=element_rect(fill="white", color=None),
    )
    + ggsize(1200, 720)
)

out = IMG_DIR / "portland-coffee-capital_chart2_industry.png"
ggsave(p, str(out), dpi=150)
print(f"Chart 2 saved: {out}")
