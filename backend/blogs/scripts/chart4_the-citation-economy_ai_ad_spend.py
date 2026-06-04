"""
Chart: AI Search Ad Spending — Total Market vs. OpenAI Projections
------------------------------------------------------------------
Combined area chart (total US AI search ad spend) with an overlaid
dashed line (OpenAI projected ad revenue).

Data:
  - Total market: eMarketer (US, 2025–2029)
  - OpenAI: PYMNTS / Reuters, investor projections (2026–2030)

Uses lets-plot 4.9.0. Output: 1200×720 px, 150 DPI.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
total_market = pd.DataFrame({
    "year":  [2025, 2026, 2027, 2028, 2029],
    "value": [1.1, 2.08, 5.5, 12.0, 25.93],
    "label": ["$1.1B", "$2.1B", "$5.5B", "$12.0B", "$25.9B"],
    "series": "Total US AI Search Ad Spend",
})

openai = pd.DataFrame({
    "year":  [2026, 2027, 2028, 2029, 2030],
    "value": [2.5, 11.0, 25.0, 53.0, 100.0],
    "label": ["$2.5B", "$11B", "$25B", "$53B", "$100B"],
    "series": "OpenAI Ad Revenue (projected)",
})

# ---------------------------------------------------------------------------
# 2. Colour palette
# ---------------------------------------------------------------------------
BLUE   = "#4A90D9"
ORANGE = "#E68A2E"

# ---------------------------------------------------------------------------
# 3. Build the chart
# ---------------------------------------------------------------------------
p = (
    ggplot()
    # ---- Total market: area fill ----
    + geom_area(
        data=total_market,
        mapping=aes(x="year", y="value", fill="series"),
        alpha=0.20,
    )
    # ---- Total market: line + points ----
    + geom_line(
        data=total_market,
        mapping=aes(x="year", y="value", color="series", linetype="series"),
        size=1.5,
    )
    + geom_point(
        data=total_market,
        mapping=aes(x="year", y="value", color="series"),
        size=3.5,
    )
    # ---- OpenAI: line (dashed) + points ----
    + geom_line(
        data=openai,
        mapping=aes(x="year", y="value", color="series", linetype="series"),
        size=1.5,
    )
    + geom_point(
        data=openai,
        mapping=aes(x="year", y="value", color="series"),
        size=3.5,
    )
    # ---- Data labels: total market ----
    + geom_text(
        data=total_market,
        mapping=aes(x="year", y="value", label="label", color="series"),
        nudge_y=3.0,
        size=9,
        fontface="bold",
        show_legend=False,
    )
    # ---- Data labels: OpenAI ----
    + geom_text(
        data=openai,
        mapping=aes(x="year", y="value", label="label", color="series"),
        nudge_y=5.0,
        size=9,
        fontface="bold",
        show_legend=False,
    )
    # ---- Scales ----
    + scale_color_manual(
        values={
            "Total US AI Search Ad Spend": BLUE,
            "OpenAI Ad Revenue (projected)": ORANGE,
        },
    )
    + scale_fill_manual(
        values={
            "Total US AI Search Ad Spend": BLUE,
        },
    )
    + scale_linetype_manual(
        values={
            "Total US AI Search Ad Spend": "solid",
            "OpenAI Ad Revenue (projected)": "dashed",
        },
    )
    + scale_x_continuous(
        breaks=[2025, 2026, 2027, 2028, 2029, 2030],
        expand=[0.02, 0.2],
    )
    + scale_y_continuous(
        name="US dollars (billions)",
        limits=[0, 115],
        breaks=[0, 20, 40, 60, 80, 100],
        expand=[0, 0],
    )
    # ---- Labels ----
    + labs(
        title="AI Search Ad Spending: Total Market vs. OpenAI Projections",
        subtitle="US market data from eMarketer; OpenAI from investor reports",
        x="",
        y="US dollars (billions)",
    )
    # ---- Theme ----
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_x=element_blank(),
        axis_title_y=element_text(size=12, margin=[0, 8, 0, 0]),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=11),
        legend_title=element_blank(),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[10, 20, 10, 10],
    )
)

# ---------------------------------------------------------------------------
# 4. Save outputs
# ---------------------------------------------------------------------------
img_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
img_dir.mkdir(parents=True, exist_ok=True)

png_path = img_dir / "the-citation-economy_ai_ad_spend.png"

# 1200 × 720 px at 150 DPI → 8 in × 4.8 in
ggsave(p, str(png_path), dpi=150, w=8, h=4.8)

print(f"PNG saved → {png_path.resolve()}")
