#!/usr/bin/env python3
"""
Chart: Brain Entropy Under Cognitive Load
==========================================
Grouped bar chart comparing regional Brain Entropy (BEN) index values
between Resting State and Task Engaged conditions across six key
brain networks. Conceptual representation based on findings from the
Human Connectome Project.

Output: ../images/the-entropy-of-knowing_brain_entropy_comparison.png
        (1200 × 720 px, 150 DPI)

Data sources:
  - Omidvarnia et al. (2022), Entropy, 24(8), 1148
  - Wang et al. (2023), PMC
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Colorblind-safe palette ──
RESTING_COLOR = "#0072B2"   # Cool blue
TASK_COLOR    = "#E69F00"   # Warm orange
DARK_TEXT      = "#222222"
MID_TEXT       = "#555555"
LIGHT_TEXT     = "#888888"
GRID_COLOR     = "#E0E0E0"

# ── Paths ──
img_dir     = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
scripts_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
img_dir.mkdir(parents=True, exist_ok=True)
scripts_dir.mkdir(parents=True, exist_ok=True)

output_path = img_dir / "the-entropy-of-knowing_brain_entropy_comparison.png"

# ═══════════════════════════════════════════════════════════════════════
# 1. DATA
# ═══════════════════════════════════════════════════════════════════════

# Conceptual BEN index values (0–1) based on HCP findings
regions = [
    "Visual\nCortex",
    "Default Mode\nNetwork",
    "Frontoparietal",
    "Dorsal\nAttention",
    "Sensorimotor",
    "Limbic\nSystem",
]

resting_vals = [0.85, 0.82, 0.78, 0.75, 0.72, 0.65]
task_vals    = [0.55, 0.48, 0.60, 0.62, 0.68, 0.58]

# Build long-format DataFrame
df = pd.DataFrame({
    "region": regions + regions,
    "ben":    resting_vals + task_vals,
    "state":  (["Resting State"] * 6) + (["Task Engaged"] * 6),
})

# Preserve region ordering
df["region"] = pd.Categorical(df["region"], categories=regions, ordered=True)

# Label position (slightly above bar top)
df["label_y"] = df["ben"] + 0.025

# ═══════════════════════════════════════════════════════════════════════
# 2. BUILD THE CHART
# ═══════════════════════════════════════════════════════════════════════

p = (
    ggplot(df, aes(x="region", y="ben", fill="state"))
    # Grouped bars
    + geom_bar(
        stat="identity",
        position=position_dodge(0.75),
        width=0.65,
        size=0.35,
        color="#ffffff",
    )
    # Value labels
    + geom_text(
        aes(label="ben", y="label_y"),
        position=position_dodge(0.75),
        stat="identity",
        size=10,
        color=DARK_TEXT,
        fontstyle="bold",
        va="bottom",
        ha="center",
    )
    # Fill colours
    + scale_fill_manual(
        values={"Resting State": RESTING_COLOR, "Task Engaged": TASK_COLOR},
        name="",
    )
    # Y-axis
    + scale_y_continuous(
        name="Brain Entropy Index (BEN)",
        limits=[0, 1.0],
        breaks=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        expand=[0, 0.04],
    )
    # X-axis
    + scale_x_discrete(name="")
    # Labels
    + labs(
        title    ="Brain Entropy Under Cognitive Load",
        subtitle =(
            "Regional BEN Suppression During Task Performance "
            "(Human Connectome Project)"
        ),
        caption  =(
            "Data adapted from Omidvarnia et al. (2022), Entropy, 24(8), 1148; "
            "Wang et al. (2023), PMC. Conceptual representation."
        ),
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(
            size=20, face="bold", color=DARK_TEXT,
            hjust=0, margin=[0, 0, 6, 0],
        ),
        plot_subtitle=element_text(
            size=12, color=MID_TEXT,
            hjust=0, margin=[0, 0, 14, 0],
        ),
        axis_title_y=element_text(
            size=14, color=DARK_TEXT, margin=[0, 8, 0, 0],
        ),
        axis_text_x=element_text(
            size=12, color="#444444", vjust=0.6,
        ),
        axis_text_y=element_text(
            size=11, color="#444444",
        ),
        plot_caption=element_text(
            size=9, color=LIGHT_TEXT,
            hjust=0, margin=[6, 0, 0, 0],
        ),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=13),
        legend_spacing=10,
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color=GRID_COLOR, size=0.4),
        plot_margin=[10, 15, 8, 12],
        panel_background=element_blank(),
        plot_background=element_blank(),
    )
)

# ═══════════════════════════════════════════════════════════════════════
# 3. SAVE PNG — 1200 × 720 px @ 150 DPI
# ═══════════════════════════════════════════════════════════════════════

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")

# Confirm
import os
size_kb = os.path.getsize(output_path) / 1024
print(f"✓ Chart saved to {output_path}")
print(f"  Dimensions: 1200 × 720 px @ 150 DPI")
print(f"  File size:   {size_kb:.1f} KB")
