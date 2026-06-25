#!/usr/bin/env python3
"""
Horizontal bar chart: Clinical effect sizes of video game-based therapeutic interventions.
Generates: video-games-as-therapy_effect_sizes.png

Data sources:
  - Pediatrics meta-analysis 2023 (PMID: 36862162)
  - JAMA Pediatrics 2024
  - BJPsych Open 2024
  - Smith & Basak, PLOS ONE 2023
  - JMIR Serious Games 2024
  - Frontiers in Psychology 2024
  - BMC Public Health 2024
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
data = {
    "condition": [
        "ADHD (game-based DTx vs control)",
        "Depression (gamified DMHIs vs control)",
        "Youth Depression (gaming vs control)",
        "Overall Cognition (video game training)",
        "Attention/Perception",
        "Higher-order Cognition",
        "MCI/Alzheimer's (MMSE)",
        "MCI/Alzheimer's (MoCA)",
        "Digital tech for youth mental health",
        "College mental health (AVGs)",
    ],
    "effect_size": [0.28, 0.28, 0.54, 0.25, 0.27, 0.31, 2.11, 2.75, 0.43, 0.35],
    "lower_ci":    [0.14, 0.08, 0.08, 0.12, 0.08, 0.10, 1.42, 1.98, None, None],
    "upper_ci":    [0.41, 0.47, 1.00, 0.39, 0.45, 0.51, 2.80, 3.51, None, None],
}
df = pd.DataFrame(data)

# Sort ascending so that after coord_flip() the largest effect is at the top
df = df.sort_values("effect_size", ascending=True).reset_index(drop=True)

# Preserve sort order as a categorical
df["condition"] = pd.Categorical(df["condition"], categories=df["condition"], ordered=True)

# Pre-formatted label for bar-end annotation
df["label"] = df["effect_size"].apply(lambda v: f"{v:.2f}")

# ---------------------------------------------------------------------------
# 2. Plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="condition", y="effect_size"))
    + geom_bar(aes(fill="condition"), stat="identity", width=0.7, show_legend=False)
    + geom_errorbar(
        aes(ymin="lower_ci", ymax="upper_ci"),
        width=0.2,
        size=0.8,
        color="#444444",
        na_rm=True,          # silently skip rows without CIs
    )
    + geom_text(
        aes(label="label"),
        stat="identity",
        hjust=-0.35,
        size=9,
        color="#222222",
    )
    + scale_fill_viridis(option="D")
    + scale_y_continuous(expand=[0.05, 0, 0.30, 0])
    + coord_flip()
    + labs(
        title="Clinical Effect Sizes of Video Game-Based Therapeutic Interventions",
        x="Condition / Outcome",
        y="Effect Size (Hedges' g / SMD)",
        caption=(
            "Sources:  Pediatrics 2023 (PMID: 36862162)  |  JAMA Pediatrics 2024  |  "
            "BJPsych Open 2024  |  Smith & Basak, PLOS ONE 2023  |  "
            "JMIR Serious Games 2024  |  Frontiers in Psychology 2024  |  BMC Public Health 2024"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title       =element_text(size=16, face="bold", hjust=0.5),
        axis_title_x     =element_text(size=12),
        axis_title_y     =element_text(size=12),
        axis_text_y      =element_text(size=10),
        axis_text_x      =element_text(size=10),
        plot_caption     =element_text(size=8, hjust=0, color="#555555"),
        panel_grid_major_y=element_blank(),
        panel_grid_minor =element_blank(),
    )
)

# ---------------------------------------------------------------------------
# 3. Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

png_path = output_dir / "video-games-as-therapy_effect_sizes.png"
ggsave(p, str(png_path), w=1200, h=720, unit="px", dpi=150)

print(f"✓ Chart saved: {png_path}")
