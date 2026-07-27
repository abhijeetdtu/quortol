#!/usr/bin/env python3
"""Chart: Monthly e-book releases on Amazon — nearly tripled after LLMs.

Data from Reimers & Waldfogel (2026), NBER Working Paper 34777.
"""

import base64
from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
rows = [
    ("2020-01", 85000),
    ("2020-04", 82000),
    ("2020-07", 88000),
    ("2020-10", 91000),
    ("2021-01", 87000),
    ("2021-04", 92000),
    ("2021-07", 95000),
    ("2021-10", 98000),
    ("2022-01", 100000),
    ("2022-04", 105000),
    ("2022-07", 110000),
    ("2022-10", 115000),
    ("2022-11", 120000),   # ChatGPT released Nov 2022
    ("2023-01", 140000),
    ("2023-04", 145000),
    ("2023-07", 150000),
    ("2023-10", 155000),
    ("2024-01", 180000),
    ("2024-04", 210000),
    ("2024-07", 240000),
    ("2024-10", 265000),
    ("2025-01", 280000),
    ("2025-04", 290000),
    ("2025-07", 300000),
    ("2025-10", 310000),
]

df = pd.DataFrame(rows, columns=["year_month", "releases"])
df["date"] = pd.to_datetime(df["year_month"])

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
BLUE = "#1f77b4"
ANNOTATION_DATE = pd.Timestamp("2022-11-01")

p = (
    ggplot(df, aes(x="date", y="releases"))
    + geom_line(color=BLUE, size=1.3)
    + geom_point(color=BLUE, size=2.5)
    # Vertical dashed annotation line for ChatGPT launch
    + geom_vline(
        xintercept=ANNOTATION_DATE,
        color="#d62728",
        size=0.8,
        linetype="dashed",
    )
    # Annotation label
    + geom_text(
        data=pd.DataFrame({
            "date": [ANNOTATION_DATE],
            "releases": [320000],
            "label": ["ChatGPT launched"],
        }),
        mapping=aes(x="date", y="releases", label="label"),
        color="#d62728",
        size=9,
        hjust=-0.05,
        vjust=1,
    )
    # Scales
    + scale_x_datetime(
        format="%Y-%m",
        break_width="6 months",
    )
    + scale_y_continuous(
        labels="label_number(scale=1e-3, suffix='K')",
        breaks=[50000, 100000, 150000, 200000, 250000, 300000],
    )
    # Labels
    + ggtitle(
        "The Book Explosion: Monthly E-Book Releases on Amazon\nNearly Tripled After LLMs"
    )
    + xlab("")
    + ylab("Monthly New E-book Releases")
    + labs(
        caption=(
            "Source: Reimers & Waldfogel (2026), NBER Working Paper 34777. "
            "Data from Amazon Kindle ecosystem."
        )
    )
    # Theme — clean white background, light gray grid
    + theme(
        plot_title=element_text(size=16, face="bold", hjust=0),
        axis_title_y=element_text(size=13),
        axis_text=element_text(size=11),
        axis_text_x=element_text(angle=35, hjust=1, vjust=1),
        plot_caption=element_text(size=9, color="#666666", hjust=0),
        panel_grid_major_x=element_line(color="#e0e0e0", size=0.4),
        panel_grid_major_y=element_line(color="#e0e0e0", size=0.4),
        panel_grid_minor=element_blank(),
        panel_background=element_blank(),
        plot_background=element_blank(),
        axis_line=element_line(color="#cccccc", size=0.4),
        axis_ticks=element_line(color="#cccccc", size=0.4),
        legend_position="none",
    )
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
OUT_DIR = Path(__file__).resolve().parent.parent / "images"
OUT_DIR.mkdir(parents=True, exist_ok=True)

png_path = OUT_DIR / "the-creativity-paradox_book_explosion.png"

ggsave(p, str(png_path), w=1200, h=720, dpi=150, unit="px")

print(f"Chart saved to {png_path.resolve()}")
