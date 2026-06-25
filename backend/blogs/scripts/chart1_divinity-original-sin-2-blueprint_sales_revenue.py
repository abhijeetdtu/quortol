"""
Divinity: Original Sin 2 — Commercial Performance Milestones
-----------------------------------------------------------
lets-plot chart showing cumulative copies sold (bars) and revenue milestones (labeled points).
Uses Okabe-Ito inspired colorblind-safe palette.

Output: 1200×720 px PNG at 150 DPI
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# =====================================================================
# DATA
# =====================================================================

df = pd.DataFrame({
    "milestone": [
        "Kickstarter\nSep 2015",
        "Launch +4d\nSep 2017",
        "2.5 Months\nNov 2017",
        "Launch Year\nDec 2017",
        "Total Lifetime\nJan 2026",
        "Steam Only\nJun 2026",
    ],
    "cumulative_units_m": [0.0, 0.5, 1.0, 1.0, 7.5, 5.5],
    "revenue_m": [2.03, None, None, 85.0, None, 172.9],
    "bar_type": [
        "Funding",
        "Sales Milestone",
        "Sales Milestone",
        "Sales Milestone",
        "Sales Milestone",
        "Platform Breakdown",
    ],
})

# --- Subset: bars with positive units get a label ---
df_units_label = df[df["cumulative_units_m"] > 0].copy()
df_units_label["units_label"] = df_units_label["cumulative_units_m"].apply(
    lambda x: f"{x:.1f}M" if x >= 1 else f"{int(x * 1000)}K"
)

# --- Subset: rows that have revenue data ---
df_rev = df.dropna(subset=["revenue_m"]).copy()

# Scale revenue to fit on the primary axis (leave ~18 % headroom)
MAX_UNITS = 8.0
MAX_REVENUE = df_rev["revenue_m"].max()  # 172.9
REV_SCALE = (MAX_UNITS * 0.82) / MAX_REVENUE

df_rev["rev_y"] = df_rev["revenue_m"] * REV_SCALE
df_rev["rev_label"] = df_rev["revenue_m"].apply(lambda x: f"${x:.1f}M")

# =====================================================================
# PALETTE  (Okabe-Ito derived, colorblind-safe)
# =====================================================================

C_SALES  = "#0072B2"   # blue          – sales milestones
C_FUND   = "#999999"   # gray          – Kickstarter funding
C_STEAM  = "#E69F00"   # orange        – platform breakdown
C_REV    = "#D55E00"   # vermillion    – revenue markers

# =====================================================================
# CHART
# =====================================================================

p = (
    ggplot()

    # --- Bars: cumulative copies sold ---
    + geom_bar(
        aes(x="milestone", y="cumulative_units_m", fill="bar_type"),
        data=df,
        stat="identity",
        width=0.60,
        alpha=0.88,
    )

    # --- Unit labels on bars ---
    + geom_text(
        aes(x="milestone", y="cumulative_units_m", label="units_label"),
        data=df_units_label,
        vjust=-0.5,
        size=10,
        fontface="bold",
        color="#333333",
    )

    # --- Revenue markers (filled circles) ---
    + geom_point(
        aes(x="milestone", y="rev_y"),
        data=df_rev,
        fill=C_REV,
        color=C_REV,
        size=5,
    )

    # --- Revenue value labels ---
    + geom_text(
        aes(x="milestone", y="rev_y", label="rev_label"),
        data=df_rev,
        vjust=-1.0,
        size=9,
        fontface="bold",
        color=C_REV,
    )

    # --- Scales -------------------------------------------------
    + scale_fill_manual(
        values=[C_SALES, C_STEAM, C_FUND],
        name="",
        breaks=["Sales Milestone", "Platform Breakdown", "Funding"],
    )

    + scale_y_continuous(
        name="Cumulative Copies Sold",
        limits=[0, MAX_UNITS * 1.30],
        breaks=list(range(0, 9)),
        labels=["0", "1M", "2M", "3M", "4M", "5M", "6M", "7M", "8M"],
    )

    # --- Labels -------------------------------------------------
    + labs(
        title="Divinity: Original Sin 2 — Commercial Performance Milestones",
        subtitle="Bars = cumulative copies sold  ·  ◆  = revenue milestone",
        caption="Sources: Kickstarter, TechSpot, DSOGaming, SuperData, Raijin.gg, GamingBolt",
    )

    # --- Theme -------------------------------------------------
    + theme_minimal()

    + theme(
        plot_title    =element_text(size=18, face="bold", hjust=0.5, margin=[0, 0, 5, 0]),
        plot_subtitle =element_text(size=10, hjust=0.5, color="#666666", margin=[0, 0, 18, 0]),
        axis_text_x   =element_text(size=10, hjust=0.5, color="#444444"),
        axis_text_y   =element_text(size=10, color="#444444"),
        axis_title_x  =element_blank(),
        axis_title_y  =element_text(size=12, margin=[0, 8, 0, 0]),
        plot_caption  =element_text(size=8, hjust=0, color="#888888", margin=[12, 0, 0, 0]),
        panel_grid_major=element_line(color="#E8E8E8", size=0.30),
        panel_grid_minor=element_blank(),
        plot_margin   =[25, 30, 10, 25],
        axis_ticks    =element_blank(),
        legend_position="bottom",
        legend_title  =element_blank(),
        legend_text   =element_text(size=9),
    )
)

# =====================================================================
# SAVE
# =====================================================================

output_dir  = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

filename = "divinity-original-sin-2-blueprint_sales_revenue.png"

ggsave(
    p,
    filename,
    path  = str(output_dir),
    w     = 8.0,
    h     = 4.8,
    unit  = "in",
    dpi   = 150,
    scale = 1.0,
)

output_path = output_dir / filename
print(f"✅  Chart saved: {output_path}")

# Quick verification
from PIL import Image
img = Image.open(output_path)
print(f"    Dimensions  : {img.width} × {img.height} px")
print(f"    DPI         : {img.info.get('dpi', 'not set')}")
