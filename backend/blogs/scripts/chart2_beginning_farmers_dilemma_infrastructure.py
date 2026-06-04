#!/usr/bin/env python3
"""
What a Self-Sufficient Homestead Actually Costs
================================================
Stacked horizontal bar chart showing mid-point infrastructure costs
for three tiers of homestead startup (Bare Bones / Comfortable / Full Setup).

Data sources: USDA NASS Land Values 2025; NREL 2024 ATB;
EPA Rainwater Harvesting; HomeGuide 2026.

Output: 1200 × 720 px PNG at 150 DPI
"""

import pandas as pd
from pathlib import Path
from lets_plot import *  # noqa: F401, F403

LetsPlot.setup_html()

# ================================================================
# PATHS
# ================================================================
OUTPUT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
SCRIPT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "beginning-farmers-dilemma_infrastructure_tiers.png"

# 1200 × 720 px @ 150 DPI  →  w = 8 in,  h = 4.8 in
W, H, DPI = 8, 4.8, 150

# ================================================================
# RAW DATA  (mid-point costs in USD)
# ================================================================
tier_labels = [
    "Bare Bones\n(DIY)",
    "Comfortable\n(Modest)",
    "Full Setup\n(Turnkey)",
]

# ── Main bar data ──────────────────────────────────────────────
bar_data = pd.DataFrame({
    "tier": tier_labels * 4,  # repeat for each category
    "category": (
        ["Land"]   * 3
        + ["Water"]  * 3
        + ["Energy"] * 3
        + ["Shelter"] * 3
    ),
    "cost": [
        # Land
        12500, 32500, 65000,
        # Water
        5000, 11500, 20000,
        # Energy
        11000, 20000, 60000,
        # Shelter
        10000, 75000, 225000,
    ],
})

cat_order = ["Land", "Water", "Energy", "Shelter"]
bar_data["category"] = pd.Categorical(
    bar_data["category"], categories=cat_order, ordered=True,
)

# ── Totals per tier ────────────────────────────────────────────
tier_totals = bar_data.groupby("tier", sort=False)["cost"].sum().reset_index()
tier_totals["total_label"] = tier_totals["cost"].apply(lambda v: f"${v:,.0f}")
# Position label at a proportional offset past the bar end:
# 8% beyond each bar's own total (relative offset works for all magnitudes)
tier_totals["label_x"] = tier_totals["cost"] * 1.08

# ── Segment-label positions (centre of each stacked segment) ───
bar_data = bar_data.sort_values(["tier", "category"])
bar_data["cumsum"] = bar_data.groupby("tier", sort=False)["cost"].cumsum()
bar_data["segment_centre"] = bar_data["cumsum"] - bar_data["cost"] / 2

# Format segment labels — use compact "$X.XK" for larger values
def seg_label(v):
    """Return short label for segments >= $8000; hide smaller ones."""
    if v >= 8_000:
        if v >= 1_000_000:
            return f"${v / 1_000_000:.1f}M"
        return f"${v:,.0f}"
    return ""

bar_data["seg_label"] = bar_data["cost"].apply(seg_label)

# Determine text colour per segment (dark text on lighter fills)
# Amber (#E8A838) is light enough for dark text; all others use white.
bar_data["text_color"] = bar_data["category"].apply(
    lambda c: "#333333" if c == "Energy" else "#FFFFFF"
)

# ================================================================
# COLOURBLIND-SAFE PALETTE  (Okabe-Ito inspired / custom)
# ================================================================
# Land:   earthy brown   — distinct from blue/amber/gray
# Water:  blue
# Energy: warm amber/orange
# Shelter: neutral gray
COLORS = {
    "Land":    "#8B5E3C",   # brown
    "Water":   "#4A90D9",   # blue
    "Energy":  "#E8A838",   # amber/orange
    "Shelter": "#6B6B6B",   # gray/charcoal
}

# ================================================================
# BUILD PLOT
# ================================================================

# Separate geom_text calls so each segment gets its own text colour.
# We use three calls (one per colour variant needed).
#   - White text: Land, Water, Shelter
#   - Dark text:  Energy

p = (
    ggplot()
    # ── Stacked horizontal bars ────────────────────────────────
    + geom_bar(
        aes(x="cost", y="tier", fill="category"),
        data=bar_data,
        stat="identity",
        position="stack",
        width=0.55,
        color="#FFFFFF",
        size=0.6,
    )
    # ── Segment labels (white text — Land, Water, Shelter) ─────
    + geom_text(
        aes(x="segment_centre", y="tier", label="seg_label"),
        data=bar_data[bar_data["text_color"] == "#FFFFFF"],
        color="#FFFFFF",
        size=8,
        fontweight="bold",
    )
    # ── Segment labels (dark text — Energy) ────────────────────
    + geom_text(
        aes(x="segment_centre", y="tier", label="seg_label"),
        data=bar_data[bar_data["text_color"] == "#333333"],
        color="#333333",
        size=8,
        fontweight="bold",
    )
    # ── Total labels at end of each bar ────────────────────────
    + geom_text(
        aes(x="label_x", y="tier", label="total_label"),
        data=tier_totals,
        color="#222222",
        size=9.5,
        fontweight="bold",
    )
    # ── Fill / axis scales ─────────────────────────────────────
    + scale_fill_manual(
        values=COLORS,
        breaks=cat_order,
        name="",
    )
    + scale_x_continuous(
        breaks=[0, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000],
        labels=["$0", "$50,000", "$100,000", "$150,000", "$200,000",
                "$250,000", "$300,000", "$350,000", "$400,000"],
        expand=[0.02, 0.25],
    )
    # ── Labels ─────────────────────────────────────────────────
    + labs(
        title="What a Self-Sufficient Homestead Actually Costs",
        subtitle=(
            "Mid-point infrastructure investment by tier "
            "(land, water, energy, shelter)"
        ),
        x="Cost (USD)",
        y="",
        caption=(
            "Sources: USDA NASS Land Values 2025; NREL 2024 ATB; "
            "EPA Rainwater Harvesting; HomeGuide 2026"
        ),
    )
    # ── Clean, magazine-style theme ────────────────────────────
    + theme_minimal()
    + theme(
        # white canvas
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
        # title / subtitle / caption
        plot_title=element_text(
            size=18, hjust=0, face="bold",
            margin=[0, 0, 2, 0],
        ),
        plot_subtitle=element_text(
            size=10.5, hjust=0, color="#666666",
            margin=[2, 0, 24, 0],
        ),
        plot_caption=element_text(
            size=7.5, color="#999999", hjust=0,
            margin=[14, 0, 0, 0],
        ),
        # axes
        axis_title_x=element_text(size=10, color="#555555", margin=[6, 0, 0, 0]),
        axis_title_y=element_blank(),
        axis_text_x=element_text(size=9, color="#666666"),
        axis_text_y=element_text(size=11, face="bold", color="#333333"),
        axis_line_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_y=element_blank(),
        axis_line_y=element_blank(),
        # grid — minimal
        panel_grid_major_x=element_line(color="#EEEEEE", size=0.25),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        # legend — horizontal bottom
        legend_position="bottom",
        legend_direction="horizontal",
        legend_text=element_text(size=9.5, color="#555555"),
        legend_spacing=12,
        # outer margin
        plot_margin=[18, 30, 12, 20],
    )
)

# ================================================================
# SAVE AS PNG  (1200 × 720 px @ 150 DPI)
# ================================================================
ggsave(p, str(OUTPUT_FILE), w=W, h=H, unit="in", dpi=DPI)
print(f"✓  Chart saved  →  {OUTPUT_FILE}")
print(f"   Dimensions   →  {int(W * DPI)} × {int(H * DPI)} px @ {DPI} DPI")
