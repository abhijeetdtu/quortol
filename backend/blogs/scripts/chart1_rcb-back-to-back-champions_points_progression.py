#!/usr/bin/env python3
"""
Chart: RCB's Points Progression — IPL 2026 League Stage
Output: ../images/rcb-back-to-back-champions_points_progression.png  (1200 × 720 px, 150 DPI)

Line chart showing Royal Challengers Bengaluru's cumulative points across 14
league matches in IPL 2026, with win/loss annotations at each match.

Data: Wikipedia — 2026 Royal Challengers Bengaluru season (league progression table)
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ============================================================================
# 1. DATA
# ============================================================================

df = pd.DataFrame({
    "match":    [1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14],
    "points":   [2,  4,  4,  6,  8,  8, 10, 12, 12, 12, 14, 16, 18, 18],
    "result":   ["W","W","L","W","W","L","W","W","L","L","W","W","W","L"],
    "opponent": ["SRH","CSK","RR","MI","LSG","DC","GT","DC","GT","LSG",
                 "MI","KKR","PBKS","SRH"],
})

# Build match labels (e.g. "W vs SRH")
df["match_label"] = df["result"] + " vs " + df["opponent"]

# --- Annotation positioning ---
# Triangles sit close to the main markers (offset ±1.0)
df["tri_y"] = df["points"] + df["result"].map({"W": 1.0, "L": -1.0})

# Text labels sit further out (offset ±2.8) to avoid overlapping triangles
# For consecutive wins or losses, stagger x slightly to prevent text overlap
df["label_y"] = df["points"] + df["result"].map({"W": 2.8, "L": -2.8})

# Determine if the previous match had the same result → stagger x
prev_same = df["result"].eq(df["result"].shift(1))
df["label_x"] = df["match"].astype(float)
df.loc[prev_same & (df["result"] == "W"), "label_x"] += 0.12
df.loc[prev_same & (df["result"] == "L"), "label_x"] -= 0.12

# Triangle colour and shape
# 24 = filled upward triangle, 25 = filled downward triangle
df["tri_shape"] = df["result"].map({"W": 24, "L": 25})
df["tri_color"] = df["result"].map({"W": "#2E8B57", "L": "#CC0000"})

# ============================================================================
# 2. BUILD THE PLOT
# ============================================================================

p = (
    ggplot(df, aes(x="match", y="points"))

    # ---- Main line & circular markers ----
    + geom_line(color="#CC0000", size=1.3)
    + geom_point(color="#CC0000", fill="#CC0000", size=5, shape=19)

    # ---- Win triangles (green, upward) ----
    + geom_point(
        aes(x="match", y="tri_y", shape="tri_shape",
            fill="tri_color", color="tri_color"),
        data=df[df["result"] == "W"],
        size=4,
        stroke=0.3,
    )

    # ---- Loss triangles (red, downward) ----
    + geom_point(
        aes(x="match", y="tri_y", shape="tri_shape",
            fill="tri_color", color="tri_color"),
        data=df[df["result"] == "L"],
        size=4,
        stroke=0.3,
    )

    # Use identity scales so the hex colour / shape values pass through
    + scale_shape_identity()
    + scale_fill_identity()
    + scale_color_identity()

    # ---- Match-result text labels ----
    + geom_text(
        aes(x="label_x", y="label_y", label="match_label"),
        size=3.0,
        color="#444444",
        family="sans-serif",
    )

    # ---- Playoff qualification threshold (dashed line) ----
    + geom_hline(
        yintercept=16,
        color="#777777",
        size=0.7,
        linetype="dashed",
    )

    # ---- Playoff label ----
    + geom_text(
        data=pd.DataFrame({"x": [13.6], "y": [16], "label": ["Playoff qualification"]}),
        mapping=aes(x="x", y="y", label="label"),
        color="#777777",
        size=4.0,
        hjust="right",
        vjust="bottom",
    )

    # ---- Axes ----
    + scale_x_continuous(
        breaks=list(range(1, 15)),
        labels=[str(i) for i in range(1, 15)],
        limits=(0.3, 14.7),
        expand=[0.01, 0],
    )
    + scale_y_continuous(
        breaks=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        limits=(0, 21),
        expand=[0.01, 0],
    )

    # ---- Titles & captions ----
    + labs(
        title="RCB\u2019s Path to the Top: IPL 2026 League Stage",
        subtitle="Points progression across 14 league matches",
        x="Match Number",
        y="Cumulative Points",
        caption="Source: Wikipedia / 2026 Royal Challengers Bengaluru season",
    )

    # ---- Theme ----
    + theme_minimal()
    + theme(
        # Title block
        plot_title    = element_text(size=20, face="bold", color="#1a1a1a",
                                     hjust=0, margin=[0, 0, 4, 0]),
        plot_subtitle = element_text(size=13, color="#666666",
                                     hjust=0, margin=[0, 0, 18, 0]),
        plot_caption  = element_text(size=9, color="#999999",
                                     hjust=0, margin=[14, 0, 0, 0]),

        # Axis labels & ticks
        axis_title_x  = element_text(size=13, color="#444444",
                                     margin=[10, 0, 0, 0]),
        axis_title_y  = element_text(size=13, color="#444444",
                                     margin=[0, 10, 0, 0]),
        axis_text_x   = element_text(size=11, color="#555555"),
        axis_text_y   = element_text(size=11, color="#555555"),
        axis_ticks    = element_blank(),

        # Grid lines
        panel_grid_major_x = element_line(color="#E0E0E0", size=0.3),
        panel_grid_major_y = element_line(color="#E0E0E0", size=0.3),
        panel_grid_minor   = element_blank(),

        # Background
        panel_background = element_rect(fill="#F5F5F5", color=None),
        plot_background  = element_rect(fill="#F5F5F5", color=None),

        # Margins (top, right, bottom, left)
        plot_margin = [20, 30, 12, 18],
    )
)

# ============================================================================
# 3. SAVE PNG  — 1200 × 720 px @ 150 DPI  →  8 × 4.8 in
# ============================================================================

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "rcb-back-to-back-champions_points_progression.png"
ggsave(p, str(output_path), w=8, h=4.8, unit="in", dpi=150)

print(f"✓ Chart saved to {output_path}")
print(f"  Dimensions: 1200 × 720 px  @  150 DPI")
