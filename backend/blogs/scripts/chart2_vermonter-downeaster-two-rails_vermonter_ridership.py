#!/usr/bin/env python3
"""
Chart 2: Vermonter Ridership Recovery (FY19-FY25)
Bar chart — magazine-style.

Output: 1200x720 px PNG at 150 DPI, lets-plot.
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────
# FY20 has no reliable data (service suspended) → use 0 for bar gap.
df = pd.DataFrame({
    "year": [2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "ridership": [99_280, 0, 18_585, 87_282, 99_974, 114_566, 115_940],
    "label_yn": ["", "", "yes", "", "", "", "yes"],  # which bars get annotation
})

# Annotations data frame
annot_df = pd.DataFrame({
    "x": [2021, 2025],
    "y": [38_000, 133_000],
    "label": ["\u221281% from FY19", "Busiest since 2005"],
})

# Service-suspension annotation
suspend_df = pd.DataFrame({
    "x": [2020],
    "y": [58_000],
    "label": ["Service\nSuspended"],
})

# ── Axis helpers ──────────────────────────────────────────────────────
x_breaks = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
x_labels = ["FY19", "FY20", "FY21", "FY22", "FY23", "FY24", "FY25"]

y_breaks = [0, 25_000, 50_000, 75_000, 100_000, 125_000]
y_labels = ["0", "25K", "50K", "75K", "100K", "125K"]

# ── Build plot ────────────────────────────────────────────────────────
p = (
    ggplot(df, aes(x="year", y="ridership"))
    # Bars (stat_identity)
    + geom_bar(stat="identity", fill="#228833", width=0.55, alpha=0.9)
    # Suspension zone: gray rect + label (separate data so it sits behind bars)
    + geom_rect(xmin=2019.5, xmax=2020.5, ymin=0, ymax=130_000,
                fill="#F2F2F2", color="#F2F2F2")
    + geom_text(aes(x="x", y="y", label="label"), data=suspend_df,
                hjust=0.5, vjust=0.5, size=7.5, color="#888888")
    # Annotation arrows / labels
    + geom_text(aes(x="x", y="y", label="label"), data=annot_df,
                hjust=0.5, vjust=0, size=8, color="#228833")
    # ── Scales ──
    + scale_x_continuous(breaks=x_breaks, labels=x_labels)
    + scale_y_continuous(breaks=y_breaks, labels=y_labels,
                         limits=[0, 150_000])
    # ── Labels ──
    + ggtitle(
        "Vermonter Ridership Recovery, FY2019\u2013FY2025",
        subtitle="From pandemic low of 18,585 to 115,940",
    )
    + xlab("Fiscal Year")
    + ylab("Annual Ridership")
    + labs(caption="Sources: Amtrak, Wikipedia; does not include riders south of New Haven")
    # ── Theme ──
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold"),
        plot_subtitle=element_text(size=11, color="#555555"),
        plot_caption=element_text(size=8, color="#888888"),
        axis_title_x=element_text(size=10, color="#555555"),
        axis_title_y=element_text(size=10, color="#555555"),
        axis_text_x=element_text(size=9, angle=0, hjust=0.5),
        axis_text_y=element_text(size=9),
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#EEEEEE", size=0.3),
        panel_grid_minor=element_blank(),
        axis_line=element_line(color="#CCCCCC", size=0.3),
        plot_margin=[20, 25, 15, 20],
    )
)

# ── Save ──────────────────────────────────────────────────────────────
out_path = ("/home/pi/Documents/code/quortol/backend/blogs/images/"
            "vermonter-downeaster-two-rails_vermonter_ridership.png")
ggsave(p, out_path, w=8, h=4.8, unit="in", dpi=150)
print(f"Chart 2 saved: {out_path}")
