#!/usr/bin/env python3
"""
Chart 3: Coffee Price Pressures, 2020–2025
Clean single-axis bar chart: Coffee CPI YoY % Change with tariff annotation.
No dual-axis — import price overlay was removed to avoid clutter.
1200 × 720 px @ 150 DPI.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

IMG_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Coffee CPI YoY % Change (U.S. city average, all urban consumers)
cpi_records = [
    ("2020-01-01",  0.5),
    ("2020-07-01", -1.2),
    ("2021-01-01",  1.8),
    ("2021-07-01",  4.2),
    ("2022-01-01",  8.5),
    ("2022-07-01", 15.3),
    ("2023-01-01", 11.7),
    ("2023-07-01",  3.1),
    ("2024-01-01", -0.8),
    ("2024-07-01",  2.4),
    ("2025-01-01",  8.9),
    ("2025-07-01", 18.2),
    ("2025-10-01", 21.0),
]
df = pd.DataFrame(cpi_records, columns=["date", "cpi_yoy"])
df["date"] = pd.to_datetime(df["date"])

# Bar fill: blue for positive, red for negative, accent red for peak
PEAK_COLOR = "#CC0000"
POS_COLOR = "#0072B2"
NEG_COLOR = "#D55E00"

df["fill"] = df["cpi_yoy"].apply(lambda v: POS_COLOR if v >= 0 else NEG_COLOR)
df.loc[df["cpi_yoy"] == df["cpi_yoy"].max(), "fill"] = PEAK_COLOR

# Tariff event: April 2025
tariff_date = pd.Timestamp("2025-04-01")
tariff_label_df = pd.DataFrame({
    "date": [pd.Timestamp("2025-09-01")],
    "label": ["10% Tariff on\nCoffee Imports"],
    "y": [24],
})

p = (
    ggplot(df, aes(x="date", y="cpi_yoy"))

    # Bars
    + geom_bar(aes(fill="fill"), stat="identity", width=0.55, show_legend=False)
    + scale_fill_identity()

    # Value labels on select bars (only annotate notable ones)
    + geom_text(
        data=df[df["cpi_yoy"].isin([-1.2, 15.3, 21.0])],
        mapping=aes(label="cpi_yoy"),
        stat="identity",
        size=10,
        color="#333333",
        fontface="bold",
        vjust=(-1.5 if -1.2 else -0.8),
        hjust=0.5,
    )

    # Peak callout
    + geom_label(
        data=df[df["cpi_yoy"] == 21.0],
        mapping=aes(label="cpi_yoy"),
        fill=PEAK_COLOR, color="white", size=11, fontface="bold",
        nudge_y=4.5, label_padding=6, label_r=3,
    )

    # Tariff vertical line
    + geom_vline(xintercept=tariff_date, color=PEAK_COLOR, linetype="dashed", size=0.9)

    # Tariff label
    + geom_text(
        data=tariff_label_df,
        mapping=aes(x="date", y="y", label="label"),
        color=PEAK_COLOR, size=9, fontface="bold", hjust=0.5, vjust=0,
    )

    # Scales
    + scale_y_continuous(
        name="Coffee CPI (YoY % Change)",
        limits=[-5.5, 30],
        breaks=[-5, 0, 5, 10, 15, 20, 25, 30],
        labels=["\u22125%", "0%", "5%", "10%", "15%", "20%", "25%", "30%"],
        expand=[0, 0],
    )
    + scale_x_datetime(
        format="%Y",
        break_width="1 year",
        limits=[pd.Timestamp("2019-06-01"), pd.Timestamp("2026-03-01")],
        expand=[0.02, 0],
    )

    # Labels
    + labs(
        title="Coffee Price Pressures, 2020\u20132025",
        subtitle=(
            "Coffee prices rose 21% year-over-year by October 2025, "
            "driven by supply shortages and new tariffs"
        ),
        x="",
        caption="Source: U.S. Bureau of Labor Statistics CPI; KATU",
    )

    # Clean theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=22, face="bold", margin=[0, 0, 5, 0]),
        plot_subtitle=element_text(size=13, color="#555555", margin=[0, 0, 25, 0]),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=12, margin=[0, 8, 0, 0]),
        axis_text_x=element_text(size=12, color="#333333"),
        axis_text_y=element_text(size=11, color="#555555"),
        axis_ticks=element_blank(),
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.3),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.4),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 30, 10, 25],
        plot_caption=element_text(size=9, color="#888888", margin=[10, 0, 0, 0]),
        plot_background=element_rect(fill="#FAFAFA", color=None),
    )
    + ggsize(1200, 720)
)

out = IMG_DIR / "portland-coffee-capital_chart3_prices.png"
ggsave(p, str(out), dpi=150)
print(f"Chart 3 saved: {out}")
