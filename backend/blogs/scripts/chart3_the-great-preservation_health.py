"""
The Great Preservation — Chart 3: Health Benefits of Nature Prescription Programs
Horizontal bar chart showing effect sizes of nature-based interventions on key health outcomes.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe green (#52b788).
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────
data = pd.DataFrame({
    "outcome": [
        "Daily Step\nIncrease",
        "Systolic BP\nReduction",
        "Diastolic BP\nReduction",
        "Anxiety\n(SMD post)",
        "Depression\n(SMD post)",
    ],
    # Absolute effect magnitude (all benefits shown as positive)
    "magnitude": [900, 4.82, 3.82, 0.57, 0.50],
    # Full label with sign and unit
    "label_text": [
        "+900 steps/day",
        "\u22124.82 mmHg",
        "\u22123.82 mmHg",
        "\u22120.57 SMD",
        "\u22120.50 SMD",
    ],
    # Dummy column for zero baseline
    "zero": [0, 0, 0, 0, 0],
})

# Sort by magnitude descending for horizontal bar (largest at top)
data = data.sort_values("magnitude", ascending=True).reset_index(drop=True)
data["outcome"] = pd.Categorical(
    data["outcome"],
    categories=data["outcome"].tolist(),
    ordered=True,
)

# ── Colour palette ────────────────────────────────────────────────────
GREEN = "#52b788"
DARK_TEXT = "#333333"
MUTED_TEXT = "#777777"

# ── Build chart ───────────────────────────────────────────────────────
p = (
    ggplot(data, aes(x="outcome", y="magnitude"))
    # Horizontal reference line at 0
    + geom_hline(yintercept=0, size=0.5, color="#666666")
    # Horizontal bars — use geom_segment with a zero column for the baseline
    # The data column "zero" provides the yend reference
    + geom_segment(
        mapping=aes(xend="outcome", y="zero", yend="magnitude"),
        color=GREEN, size=5, alpha=0.7,
    )
    # Value labels with units
    + geom_text(
        mapping=aes(label="label_text"),
        hjust=-0.08, size=9, color=DARK_TEXT, fontface="bold",
    )
    # Flip to horizontal
    + coord_flip()
    # Y axis: expand to fit labels
    + scale_y_continuous(
        expand=[0.1, 0],
    )
    # Labels & title
    + labs(
        title="Health Benefits of Nature Prescription Programs",
        subtitle=(
            "Effect sizes of nature-based interventions on cardiometabolic, "
            "mental health, and physical activity outcomes"
        ),
        x="",
        y="Effect magnitude",
        caption=(
            "Source: Nguyen et al., \"Effect of nature prescriptions on cardiometabolic and "
            "mental health, and physical activity: a systematic review,\" "
            "Monash University, 2023  |  "
            "Note: BP = blood pressure; SMD = Standardised Mean Difference; "
            "negative values indicate beneficial reductions"
        ),
    )
    # Magazine-style theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=12, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_title_y=element_blank(),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11),
        plot_caption=element_text(size=9, color=MUTED_TEXT, hjust=0, margin=[12, 0, 0, 0]),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
    )
)

# ── Save ──────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-great-preservation_health.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 3 saved to: {output_path}")
