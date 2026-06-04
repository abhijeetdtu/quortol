#!/usr/bin/env python3
"""
RCB's Multi-Dimensional Attack: IPL 2026 — Two-Panel Horizontal Bar Chart
==========================================================================
Left panel:   Top 5 run-scorers (red gradient)
Right panel:  Top 6 wicket-takers (blue gradient)

Shows how Royal Challengers Bengaluru built title-winning depth across
both batting and bowling departments in IPL 2026.

Data: Wikipedia — 2026 Royal Challengers Bengaluru season
      https://en.wikipedia.org/wiki/2026_Royal_Challengers_Bengaluru_season

Output: ../images/rcb-back-to-back-champions_contributors.png  (1200 × 720 px, 150 DPI)
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. PATHS
# ============================================================================
OUTPUT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "rcb-back-to-back-champions_contributors.png"

# 1200 × 720 px @ 150 DPI  →  w = 1200/150 = 8 in,  h = 720/150 = 4.8 in
W, H, DPI = 8, 4.8, 150

# ============================================================================
# 2. DATA
# ============================================================================

# Top-5 run-scorers
runs_df = pd.DataFrame({
    "player": ["Virat Kohli", "Rajat Patidar", "Devdutt Padikkal",
               "Tim David", "Krunal Pandya"],
    "value":  [675, 501, 464, 305, 226],
    "panel":  "Top Run-Scorers",
})

# Top-6 wicket-takers
wickets_df = pd.DataFrame({
    "player": ["Bhuvneshwar Kumar", "Rasikh Salam", "Josh Hazlewood",
               "Krunal Pandya", "Suyash Sharma", "Jacob Duffy"],
    "value":  [28, 19, 15, 14, 9, 9],
    "panel":  "Top Wicket-Takers",
})

# Sort both dataframes in place ascending by value so the gradient
# colours align with the sorted data passed to the chart.
runs_df = runs_df.sort_values("value", ascending=True).reset_index(drop=True)
wickets_df = wickets_df.sort_values("value", ascending=True).reset_index(drop=True)

# ------------------------------------------------------------------
# Build a global factor order that satisfies **both** panels' needs.
# In a horizontal bar chart (y = discrete, x = value):
#   - first factor level  →  bottom of y-axis  →  lowest value
#   - last factor level   →  top of y-axis      →  highest value
#
# Therefore we need ascending-by-value ordering within each panel.
# The complication: Krunal Pandya appears in BOTH panels.
#
# Wickets ascending:  Suyash(9), Jacob(9), Krunal(14),
#                     Josh(15), Rasikh(19), Bhuvi(28)
# Runs ascending:     Krunal(226), Tim(305), Devdutt(464),
#                     Rajat(501), Virat(675)
#
# Interleaved factor that respects both partial orders:
#   [Suyash, Jacob] < Krunal < [Tim, Devdutt, Rajat, Virat, Josh,
#                               Rasikh, Bhuvi]
# ------------------------------------------------------------------
runs_asc = runs_df["player"].tolist()
wkts_asc = wickets_df["player"].tolist()

# Split wickets ordering around Krunal
krunal_idx = wkts_asc.index("Krunal Pandya")
pre_krunal  = wkts_asc[:krunal_idx]      # players below Krunal in wickets
post_krunal = wkts_asc[krunal_idx + 1:]  # players above Krunal in wickets

# Factor: pre-Krunal + runs-ascending (includes Krunal) + post-Krunal
factor_order = pre_krunal + runs_asc + post_krunal

# Combine data (already sorted ascending)
data = pd.concat([runs_df, wickets_df], ignore_index=True)

# Shared ordered factor
data["player"] = pd.Categorical(
    data["player"],
    categories=factor_order,
    ordered=True,
)

# Annotation label
data["label"] = data["value"].astype(str)

# ============================================================================
# 3. GRADIENT FILL COLOURS  (colorblind-safe sequential palettes)
# ============================================================================

def _gradient_colors(values, light_rgb, dark_rgb):
    """Interpolate hex colours from *light_rgb* to *dark_rgb* across *values*."""
    lo, hi = values.min(), values.max()
    span = hi - lo
    out = []
    for v in values:
        t = (v - lo) / span if span != 0 else 0.5
        r = int(light_rgb[0] + t * (dark_rgb[0] - light_rgb[0]))
        g = int(light_rgb[1] + t * (dark_rgb[1] - light_rgb[1]))
        b = int(light_rgb[2] + t * (dark_rgb[2] - light_rgb[2]))
        out.append(f"#{r:02x}{g:02x}{b:02x}")
    return out

# Colourblind-safe reds:  #FCAE91 (light) → #CB181D (dark)
runs_fill = _gradient_colors(
    runs_df["value"], (252, 174, 145), (203, 24, 29),
)

# Colourblind-safe blues: #C6DBEF (light) → #08519C (dark)
wickets_fill = _gradient_colors(
    wickets_df["value"], (198, 219, 239), (8, 81, 156),
)

data["fill"] = None
data.loc[data["panel"] == "Top Run-Scorers", "fill"] = runs_fill
data.loc[data["panel"] == "Top Wicket-Takers", "fill"] = wickets_fill

# ============================================================================
# 4. BUILD THE PLOT
# ============================================================================

p = (
    ggplot(data, aes(y="player", x="value"))
    # ---- horizontal bars ----
    + geom_bar(
        aes(fill="fill"),
        stat="identity",
        width=0.55,
        show_legend=False,
    )
    # ---- value labels at bar ends (per-panel nudging for consistent gap) ----
    + geom_text(
        aes(label="label"),
        data=data[data["panel"] == "Top Run-Scorers"],
        hjust=0, nudge_x=12, size=10, color="#333333",
    )
    + geom_text(
        aes(label="label"),
        data=data[data["panel"] == "Top Wicket-Takers"],
        hjust=0, nudge_x=0.5, size=10, color="#333333",
    )
    + scale_fill_identity()
    # ---- faceted panels with independent scales ----
    + facet_grid(
        ". ~ panel",
        scales="free",
    )
    # ---- labels ----
    + labs(
        title="RCB's Multi-Dimensional Attack: IPL 2026",
        subtitle=(
            "Runs and wickets across the squad — "
            "a team built on depth, not superstars"
        ),
        x="",
        y="",
        caption="Source: Wikipedia / 2026 Royal Challengers Bengaluru season",
    )
    # ---- theme ----
    + theme_minimal()
    + theme(
        # Canvas — light gray
        plot_background=element_rect(fill="#F5F5F5", color=None),
        panel_background=element_rect(fill="#F5F5F5", color=None),
        # Title
        plot_title=element_text(
            size=17, hjust=0.5, face="bold", margin=[0, 0, 4, 0],
        ),
        plot_subtitle=element_text(
            size=10, hjust=0.5, color="#666666", margin=[2, 0, 20, 0],
        ),
        # Caption
        plot_caption=element_text(
            size=7.5, color="#888888", hjust=0.5, margin=[14, 0, 0, 0],
        ),
        # Axes
        axis_title_x=element_blank(),
        axis_title_y=element_blank(),
        axis_text_y=element_text(size=10, color="#333333"),
        axis_text_x=element_text(size=9, color="#666666"),
        axis_line_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_y=element_blank(),
        # Grid
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.25),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        # Facet strip labels
        strip_text=element_text(size=12, face="bold", color="#333333"),
        strip_background=element_rect(fill="#E8E8E8", color=None),
        # Margin
        plot_margin=[18, 25, 12, 25],
    )
)

# ============================================================================
# 5. SAVE AS PNG  (1200 × 720 px @ 150 DPI)
# ============================================================================
ggsave(p, str(OUTPUT_FILE), w=W, h=H, unit="in", dpi=DPI)
print(f"\u2713  Chart saved  \u2192  {OUTPUT_FILE}")
print(f"    Dimensions   \u2192  {int(W * DPI)} \u00d7 {int(H * DPI)} px @ {DPI} DPI")
