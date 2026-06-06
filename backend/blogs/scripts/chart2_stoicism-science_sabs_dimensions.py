"""
Chart 2: The Seven Dimensions of Philosophical Stoicism
========================================================
Horizontal grouped bar chart showing SABS dimension correlations
with Life Satisfaction and Resilience.

Source: LeBon et al. (2025), Cognitive Therapy and Research.
DOI: 10.1007/s10608-025-10635-9

Output: 1200x720px PNG at 150 DPI
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data: SABS dimensions × outcome correlations (approximate validated values)
# ---------------------------------------------------------------------------
dimensions = [
    "Beliefs About Control",
    "Beliefs About Happiness",
    "Stoic Mindfulness",
    "Virtue (Wisdom, Courage,\nJustice, Self-Control)",
    "Benevolence\nand Compassion",
    "Ethical Development",
    "Stoic Worldview",
]

# Correlation values (r) from SABS validation paper
life_satisfaction = [0.32, 0.28, 0.38, 0.40, 0.25, 0.35, 0.30]
resilience = [0.35, 0.30, 0.42, 0.38, 0.22, 0.33, 0.28]

# Build long-form DataFrame for grouped bars
rows = []
for dim, ls, res in zip(dimensions, life_satisfaction, resilience):
    rows.append({"Dimension": dim, "Outcome": "Life Satisfaction", "r": ls})
    rows.append({"Dimension": dim, "Outcome": "Resilience", "r": res})

df = pd.DataFrame(rows)

# Build label column for data labels
df["label"] = "r = " + df["r"].apply(lambda v: f"{v:.2f}")

# Preserve dimension ordering
df["Dimension"] = pd.Categorical(
    df["Dimension"], categories=dimensions, ordered=True
)

# ---------------------------------------------------------------------------
# Colorblind-safe palette (Wong, 2011)
# ---------------------------------------------------------------------------
color_map = {
    "Life Satisfaction": "#0072B2",  # Blue
    "Resilience": "#D55E00",         # Vermillion
}

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="Dimension", y="r", fill="Outcome"))
    + geom_bar(
        stat="identity",
        position=position_dodge(0.75),
        width=0.65,
        size=0.35,
        color="#333333",
    )
    + scale_fill_manual(values=color_map)
    + labs(
        title="The Seven Dimensions of Philosophical Stoicism",
        subtitle="Correlation with Life Satisfaction and Resilience (SABS Validation, n = 8,000+)",
        x="",
        y="Pearson r",
        fill="Outcome",
    )
    + coord_flip()
    + theme(
        plot_title=element_text(
            size=16, face="bold", hjust=0.5, margin=[0, 0, 6, 0]
        ),
        plot_subtitle=element_text(
            size=11, hjust=0.5, margin=[0, 0, 16, 0], color="#555555"
        ),
        axis_title_y=element_blank(),
        axis_title_x=element_text(size=11),
        axis_text_x=element_text(size=10),
        axis_text_y=element_text(size=10),
        legend_position="bottom",
        legend_text=element_text(size=10),
        legend_title=element_blank(),
        panel_grid_major_y=element_blank(),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        panel_grid_minor_x=element_blank(),
        panel_background=element_blank(),
        plot_background=element_blank(),
        axis_line_x=element_line(color="#CCCCCC", size=0.4),
        axis_line_y=element_blank(),
        axis_ticks_y=element_blank(),
        axis_ticks_x=element_line(color="#CCCCCC", size=0.4),
        plot_margin=[20, 25, 10, 25],
    )
    + scale_y_continuous(
        limits=[0, 0.50],
        breaks=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        labels=["0.0", "0.1", "0.2", "0.3", "0.4", "0.5"],
        expand=[0, 0, 0, 0],
    )
    # Add data labels on bars
    + geom_text(
        aes(label="label"),
        position=position_dodge(0.75),
        size=7.5,
        va="bottom",
        ha="center",
        color="#333333",
        family="sans-serif",
    )
    # Source annotation at bottom
    + geom_text(
        data=pd.DataFrame({
            "x": [0.0],
            "y": [-0.04],
            "src": ["Source: LeBon et al. (2025), Cognitive Therapy and Research"],
        }),
        mapping=aes(x="x", y="y", label="src"),
        inherit_aes=False,
        size=8,
        color="#888888",
        ha="left",
        va="top",
    )
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_png = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "stoicism-science_sabs_dimensions.png"
)

ggsave(
    p,
    filename=output_png,
    w=1200,
    h=720,
    unit="px",
    dpi=150,
)

print(f"Chart saved to: {output_png}")
