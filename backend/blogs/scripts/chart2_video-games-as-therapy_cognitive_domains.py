#!/usr/bin/env python3
"""
Horizontal bar chart: Cognitive transfer effect sizes across domains
from Smith & Basak (2023) PLOS ONE meta-analysis.

Generates: video-games-as-therapy_cognitive_domains.png

Data source:
  Smith, E.T. & Basak, C. (2023). Video game training and transfer
  to cognitive domains: A meta-analysis. PLOS ONE, 18(8), e0285925.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
data = {
    "domain": [
        "Higher-order Cognition",
        "Attention / Perception",
        "Overall Cognition",
        "Psychosocial",
        "Memory",
    ],
    "effect_size": [0.31, 0.27, 0.25, 0.06, -0.14],
    "lower_ci":    [0.10, 0.08, 0.12, -0.41, -0.36],
    "upper_ci":    [0.51, 0.45, 0.39,  0.53,  0.06],
    "significant": [True, True, True, False, False],
}
df = pd.DataFrame(data)

# Sort ascending so that after coord_flip() the largest effect is at the top
df = df.sort_values("effect_size", ascending=True).reset_index(drop=True)

# Preserve sort order as a categorical
df["domain"] = pd.Categorical(df["domain"], categories=df["domain"], ordered=True)

# Pre-formatted label for bar-end annotation
df["label"] = df["effect_size"].apply(lambda v: f"{v:+.2f}")

# Color mapping: teal for significant, gray for non-significant
df["color_group"] = df["significant"].map({True: "Significant", False: "Non-significant"})

# ---------------------------------------------------------------------------
# 2. Plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="domain", y="effect_size"))
    # Bars colored by significance group
    + geom_bar(aes(fill="color_group"), stat="identity", width=0.7, show_legend=True)
    # Error bars
    + geom_errorbar(
        aes(ymin="lower_ci", ymax="upper_ci"),
        width=0.2,
        size=0.8,
        color="#444444",
        na_rm=True,
    )
    # Value labels at bar ends
    + geom_text(
        aes(label="label"),
        stat="identity",
        hjust=-0.4,
        size=10,
        color="#222222",
    )
    # Reference line at g = 0
    + geom_hline(yintercept=0, linetype="dashed", color="#666666", size=0.6)
    # Color-blind safe palette: teal for significant, gray for non-significant
    + scale_fill_manual(
        values={"Significant": "#2A9D8F", "Non-significant": "#A0A0A0"},
        labels={"Significant": "Significant (p < 0.01)", "Non-significant": "Non-significant"},
        name="Significance",
    )
    # Y-axis (horizontal after flip) with room for labels
    + scale_y_continuous(expand=[0.05, 0, 0.25, 0])
    + coord_flip()
    + ggtitle("Cognitive Transfer from Video Game Training")
    + labs(
        subtitle=(
            "Meta-analytic effect sizes across cognitive domains "
            "(Smith & Basak, PLOS ONE 2023, N = 2,079)"
        ),
        caption="Source: Smith, E.T. & Basak, C. (2023). PLOS ONE, 18(8), e0285925.",
    )
    + xlab("")
    + ylab("Hedges' g")
    + theme_minimal()
    + theme(
        plot_title      =element_text(size=18, face="bold", hjust=0.5),
        plot_subtitle   =element_text(size=12, hjust=0.5, color="#555555"),
        axis_title_x    =element_text(size=13),
        axis_text_y     =element_text(size=12),
        axis_text_x     =element_text(size=11),
        plot_caption    =element_text(size=9, hjust=0, color="#777777"),
        panel_grid_major_y=element_blank(),
        panel_grid_minor =element_blank(),
        legend_position ="bottom",
        legend_text     =element_text(size=11),
        legend_title    =element_blank(),
    )
)

# ---------------------------------------------------------------------------
# 3. Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

png_path = output_dir / "video-games-as-therapy_cognitive_domains.png"
ggsave(p, str(png_path), w=1200, h=720, unit="px", dpi=150)

print(f"✓ Chart saved: {png_path}")
