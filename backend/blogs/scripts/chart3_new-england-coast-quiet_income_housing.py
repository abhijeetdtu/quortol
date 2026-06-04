#!/usr/bin/env python3
"""
chart3_new-england-coast-quiet_income_housing.py

Scatter plot: Median household income vs. median home value for six New England states.
Data from U.S. Census Bureau, ACS 2020-2024 5-Year Estimates (2024 dollars).

Output: 1200×720 px PNG at 150 DPI.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "state": [
        "Connecticut", "Maine", "Massachusetts",
        "New Hampshire", "Rhode Island", "Vermont",
    ],
    "income":      [95781, 74733, 103960, 99031, 87796, 81203],
    "home_value":  [366900, 296600, 562100, 402500, 404200, 316600],
})

# U.S. median reference values (ACS 2020-2024, 2024 dollars)
US_MEDIAN_INCOME     = 81604   # per user specification
US_MEDIAN_HOME_VALUE = 332700  # Census Bureau QuickFacts 2020-2024

# ── Colorblind-safe palette (Okabe-Ito derived) ──────────────────────────────
state_colors = {
    "Connecticut":    "#0072B2",   # blue
    "Maine":           "#009E73",   # green
    "Massachusetts":   "#E69F00",   # orange
    "New Hampshire":   "#56B4E9",   # sky blue
    "Rhode Island":    "#D55E00",   # vermillion
    "Vermont":         "#CC79A7",   # pink
}

# ── Label offsets to avoid overlap ────────────────────────────────────────────
# Manual nudge per state ensures clean separation between labels.
# Offsets are in data coordinates (dollars).
label_offsets = pd.DataFrame({
    "state": [
        "Connecticut", "Maine", "Massachusetts",
        "New Hampshire", "Rhode Island", "Vermont",
    ],
    "nudge_x": [ 7000,  -5000,   6000,  7000, -5000, -6000],
    "nudge_y": [-20000, -20000,  22000, 20000, -20000, 20000],
    "hjust":   [  0,      1,      0,     0,     1,      1  ],  # 0=left, 1=right
    "vjust":   [  1,      1,      0,     0,     1,      0  ],  # 0=top, 1=bottom
})
data = data.merge(label_offsets, on="state")

# ── Reference line annotations ────────────────────────────────────────────────
ref_labels = pd.DataFrame({
    "x":      [US_MEDIAN_INCOME,  125000],
    "y":      [255000,            US_MEDIAN_HOME_VALUE],
    "label":  ["US median income  →", "← US median home value"],
    "hjust":  [0,                    1],
})

# ── Dollar formatting for axes ────────────────────────────────────────────────
# We use manual labels with "$" and "," for readability.
x_breaks = [60000, 70000, 80000, 90000, 100000, 110000, 120000]
x_labels = ["$60,000", "$70,000", "$80,000", "$90,000", "$100,000",
            "$110,000", "$120,000"]

y_breaks = [250000, 300000, 350000, 400000, 450000, 500000, 550000, 600000]
y_labels = ["$250,000", "$300,000", "$350,000", "$400,000", "$450,000",
            "$500,000", "$550,000", "$600,000"]

# ── Build the plot ────────────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="income", y="home_value"))
    # Points
    + geom_point(aes(color="state"), size=4.5, alpha=0.9)
    # State labels with manual nudge to avoid overlap
    + geom_text(
        aes(
            label="state", color="state",
            x="income + nudge_x", y="home_value + nudge_y",
            hjust="hjust", vjust="vjust",
        ),
        size=10, show_legend=False,
    )
    # U.S. median reference lines
    + geom_vline(
        xintercept=US_MEDIAN_INCOME,
        linetype="dashed", color="#777777", size=0.7,
    )
    + geom_hline(
        yintercept=US_MEDIAN_HOME_VALUE,
        linetype="dashed", color="#777777", size=0.7,
    )
    # Reference line labels
    + geom_text(
        aes(x="x", y="y", label="label", hjust="hjust"),
        data=ref_labels, size=8.5, color="#555555",
    )
    # Scales
    + scale_x_continuous(
        limits=[55000, 130000],
        breaks=x_breaks,
        labels=x_labels,
        expand=[0, 0],
    )
    + scale_y_continuous(
        limits=[230000, 610000],
        breaks=y_breaks,
        labels=y_labels,
        expand=[0, 0],
    )
    + scale_color_manual(values=state_colors)
    # Labels
    + labs(
        title="Income vs. Home Values in New England",
        subtitle="Six New England states compared to U.S. medians",
        x="Median Household Income (2024 dollars)",
        y="Median Home Value (2024 dollars)",
        caption="Source: U.S. Census Bureau, ACS 2020–2024",
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0.5),
        plot_subtitle=element_text(
            size=11, color="#555555", hjust=0.5,
            margin=[0, 0, 15, 0],
        ),
        plot_caption=element_text(
            size=9, color="#888888", hjust=1,
            margin=[10, 0, 0, 0],
        ),
        axis_title=element_text(size=13),
        axis_text=element_text(size=11),
        legend_title=element_blank(),
        legend_text=element_text(size=11),
        legend_position="right",
        panel_grid_major=element_line(color="#e0e0e0", size=0.4),
        panel_grid_minor=element_blank(),
        plot_margin=[15, 20, 15, 15],
    )
)

# ── Output paths ──────────────────────────────────────────────────────────────
script_dir = Path(__file__).parent.resolve()
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_path = images_dir / "new-england-coast-quiet_income_housing.png"
print(f"Saving chart → {output_path}")

# 1200×720 px at 150 DPI → 8 × 4.8 inches
ggsave(p, str(output_path), w=8, h=4.8, unit="in", dpi=150)

print("Done.")
