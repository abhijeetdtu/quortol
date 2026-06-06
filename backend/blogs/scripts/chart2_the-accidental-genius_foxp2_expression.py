#!/usr/bin/env python3
"""
FoxP2 Expression in Budgerigar Vocal Learning Circuitry
=======================================================
Grouped bar chart (3 faceted panels) comparing FoxP2 protein expression
in young adult vs. older adult budgerigars across MMSt, VSP, and their ratio.

Key finding: The MMSt/VSP ratio does NOT differ between age groups (p = 0.40),
indicating persistent FoxP2 downregulation — the molecular signature of
open-ended vocal learning — throughout the budgerigar lifespan.

Data: Moussaoui et al. 2024, BMC Neuroscience
      https://people.nmsu.edu/wrightlab/_files/publications/Moussaouietal2024BMCNeuroscience_AgeFoxP2.pdf

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

OUTPUT_FILE = OUTPUT_DIR / "the-accidental-genius_foxp2_expression.png"

# 1200 × 720 px @ 150 DPI  →  w = 8 in,  h = 4.8 in
W, H, DPI = 8, 4.8, 150

# ================================================================
# DATA  (Moussaoui et al. 2024, BMC Neuroscience, Table 1)
# ================================================================
df = pd.DataFrame({
    "metric": ["MMSt"] * 2 + ["VSP"] * 2 + ["MMSt/VSP Ratio"] * 2,
    "age_group": ["Young Adult", "Older Adult"] * 3,
    "mean": [0.309, 0.371, 0.441, 0.480, 0.744, 0.811],
    "se":   [0.014, 0.025, 0.024, 0.034, 0.049, 0.061],
})

df["ymin"] = df["mean"] - df["se"]
df["ymax"] = df["mean"] + df["se"]

# Ordered factor so panels appear left → right
metric_order = ["MMSt", "VSP", "MMSt/VSP Ratio"]
df["metric"] = pd.Categorical(df["metric"], categories=metric_order, ordered=True)

# Ensure age_group order for dodging
age_order = ["Young Adult", "Older Adult"]
df["age_group"] = pd.Categorical(df["age_group"], categories=age_order, ordered=True)

# ================================================================
# COLORBLIND-SAFE PALETTE  (Wong / Okabe-Ito)
# ================================================================
# Young Adult: #D55E00 (vermillion — reddish, warm)
# Older Adult: #0072B2 (blue — cool, contrasting)
COLORS = {"Young Adult": "#D55E00", "Older Adult": "#0072B2"}

# ================================================================
# ANNOTATION DATA  (ratio panel only)
# ================================================================
# Horizontal reference line at 1.0 (equal expression)
hline_df = pd.DataFrame({
    "metric": pd.Categorical(["MMSt/VSP Ratio"], categories=metric_order, ordered=True),
    "yintercept": [1.0],
})

# p-value callout  (placed above the Older Adult bar)
pval_df = pd.DataFrame({
    "metric": pd.Categorical(["MMSt/VSP Ratio"], categories=metric_order, ordered=True),
    "age_group": pd.Categorical(["Older Adult"], categories=age_order, ordered=True),
    "mean": [1.02],   # above the hline; will be nudged by geom_text positioning
    "ymax": [1.02],
    "label": ["MMSt/VSP ratio: p = 0.40\n(not significant)"],
})

# Note about downregulation  (placed in lower portion of ratio panel)
note_df = pd.DataFrame({
    "metric": pd.Categorical(["MMSt/VSP Ratio"], categories=metric_order, ordered=True),
    "age_group": pd.Categorical(["Young Adult"], categories=age_order, ordered=True),
    "mean": [0.63],
    "ymax": [0.63],
    "label": ["Values below 1.0 = FoxP2\ndownregulation in MMSt\n(persistent vocal learning)"],
})

# Mean-value labels on top of each bar
label_df = df.copy()
label_df["label"] = label_df["mean"].apply(lambda v: f"{v:.3f}")

# ================================================================
# BUILD PLOT
# ================================================================
p = (
    ggplot()
    # ── Grouped bars ────────────────────────────────────────────
    + geom_bar(
        aes(x="age_group", y="mean", fill="age_group"),
        data=df,
        stat="identity",
        position=position_dodge(width=0.7),
        width=0.55,
        color="#333333",
        size=0.35,
    )
    # ── Error bars ──────────────────────────────────────────────
    + geom_errorbar(
        aes(x="age_group", ymin="ymin", ymax="ymax"),
        data=df,
        position=position_dodge(width=0.7),
        width=0.12,
        size=0.55,
        color="#333333",
    )
    # ── Mean-value labels on bars ───────────────────────────────
    + geom_text(
        aes(x="age_group", y="ymax", label="label"),
        data=label_df,
        position=position_dodge(width=0.7),
        vjust=-0.55,
        size=7.5,
        color="#333333",
        fontweight="bold",
    )
    # ── Horizontal reference line (ratio panel only) ────────────
    + geom_hline(
        aes(yintercept="yintercept"),
        data=hline_df,
        linetype="dashed",
        color="#888888",
        size=0.5,
    )
    # ── "y = 1.0" label next to the reference line ──────────────
    + geom_text(
        aes(x="x", y="yintercept", label="label"),
        data=hline_df.copy().assign(
            x=pd.Categorical(["Older Adult"], categories=age_order, ordered=True),
            label="y = 1.0",
        ),
        vjust=-0.5,
        hjust=-0.2,
        size=6.5,
        color="#888888",
        fontstyle="italic",
    )
    # ── p-value annotation ──────────────────────────────────────
    + geom_text(
        aes(x="age_group", y="ymax", label="label"),
        data=pval_df,
        # Position above the reference line
        vjust=0,
        size=7,
        color="#555555",
        fontstyle="italic",
    )
    # ── Downregulation note ─────────────────────────────────────
    + geom_text(
        aes(x="age_group", y="mean", label="label"),
        data=note_df,
        vjust=1,
        size=6.5,
        color="#666666",
        lineheight=0.92,
    )
    # ── Facets (3 panels, independent y scales) ─────────────────
    + facet_wrap(
        facets="metric",
        ncol=3,
        scales="free_y",
    )
    # ── Scales ──────────────────────────────────────────────────
    + scale_fill_manual(values=COLORS, name="")
    + scale_x_discrete(labels=["Young\nAdult", "Older\nAdult"])
    # ── Labels ──────────────────────────────────────────────────
    + labs(
        title="FoxP2 Expression Across Age Groups in Budgerigar Vocal Circuitry",
        subtitle=(
            "Young adult (6–12 months) vs. older adult (≥3 years) budgerigars. "
            "Mean proportion of cells expressing FoxP2\u00B1SE."
        ),
        x="",
        y="Proportion FoxP2+ cells / Ratio",
        caption="Data: Moussaoui et al. 2024, BMC Neuroscience",
    )
    # ── Clean magazine-style theme ──────────────────────────────
    + theme_minimal()
    + theme(
        # White canvas
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
        # Title / subtitle / caption
        plot_title=element_text(
            size=16, hjust=0, face="bold",
            margin=[0, 0, 2, 0],
        ),
        plot_subtitle=element_text(
            size=9.5, hjust=0, color="#666666",
            margin=[2, 0, 20, 0],
        ),
        plot_caption=element_text(
            size=7.5, color="#999999", hjust=0,
            margin=[10, 0, 0, 0],
        ),
        # X axis — no title, compact labels
        axis_title_x=element_blank(),
        axis_text_x=element_text(size=8.5, color="#555555"),
        # Y axis
        axis_title_y=element_text(size=9.5, color="#555555", margin=[0, 6, 0, 0]),
        axis_text_y=element_text(size=8, color="#666666"),
        axis_line_x=element_line(color="#CCCCCC", size=0.35),
        axis_ticks_x=element_line(color="#CCCCCC", size=0.35),
        axis_line_y=element_blank(),
        axis_ticks_y=element_line(color="#CCCCCC", size=0.25),
        # Grid — minimal
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#EEEEEE", size=0.25),
        panel_grid_minor=element_blank(),
        # Facet strip labels (panel titles)
        strip_text_x=element_text(
            size=11, face="bold", color="#333333",
            margin=[0, 0, 4, 0],
        ),
        strip_background=element_rect(
            fill="#F6F6F6", color="#DDDDDD", size=0.4,
        ),
        # Legend — horizontal at bottom
        legend_position="bottom",
        legend_direction="horizontal",
        legend_text=element_text(size=9, color="#555555"),
        legend_spacing=10,
        legend_margin=[0, 0, 6, 0],
        # Outer margin
        plot_margin=[16, 24, 10, 18],
    )
)

# ================================================================
# SAVE AS PNG  (1200 × 720 px @ 150 DPI)
# ================================================================
ggsave(p, str(OUTPUT_FILE), w=W, h=H, unit="in", dpi=DPI)
print(f"✓  Chart saved  →  {OUTPUT_FILE}")
print(f"   Dimensions   →  {int(W * DPI)} × {int(H * DPI)} px @ {DPI} DPI")


