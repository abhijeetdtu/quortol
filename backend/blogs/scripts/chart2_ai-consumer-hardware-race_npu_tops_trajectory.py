"""
Chart: NPU & AI Accelerator Performance — TOPS Over Generations
=================================================================
Multi-line chart showing INT8 TOPS trajectory for Intel NPU,
Apple Neural Engine, Qualcomm Hexagon NPU, and NVIDIA GPUs.

Output: PNG 1200×720 @ 150 DPI
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────

intel = pd.DataFrame({
    "generation": [
        "Meteor Lake (NPU 3)", "Lunar Lake (NPU 4)", "Arrow Lake (NPU 3)",
        "Panther Lake (NPU 5)", "Nova Lake (NPU 6)"
    ],
    "year":  [2023, 2024, 2024, 2026, 2027],
    "tops":  [11.5, 48.0, 13.0, 50.0, 74.0],
})
intel["manufacturer"] = "Intel NPU"

apple = pd.DataFrame({
    "generation": ["M1", "M2", "M3", "M4"],
    "year":       [2020, 2022, 2023, 2024],
    "tops":       [11.0, 15.8, 18.0, 38.0],
})
apple["manufacturer"] = "Apple Neural Engine"

qualcomm = pd.DataFrame({
    "generation": ["Snapdragon X Elite", "Snapdragon X2 Elite"],
    "year":       [2024, 2026],
    "tops":       [45.0, 80.0],
})
qualcomm["manufacturer"] = "Qualcomm Hexagon NPU"

nvidia = pd.DataFrame({
    "generation": ["RTX 3090 (Ampere)", "RTX 4090 (Ada)", "RTX 5090 (Blackwell)"],
    "year":       [2020, 2022, 2025],
    "tops":       [238.0, 660.0, 988.0],
})
nvidia["manufacturer"] = "NVIDIA AI TOPS"

df = pd.concat([intel, apple, qualcomm, nvidia], ignore_index=True)

# Label rows — latest generation per manufacturer for annotation
latest_labels = df.loc[
    df.groupby("manufacturer")["year"].idxmax()
].copy()
latest_labels["label"] = latest_labels.apply(
    lambda r: f"{r['generation']}\n{r['tops']:.0f} TOPS", axis=1
)

# ── Aesthetics ────────────────────────────────────────────────────────────────

COLORS = {
    "Intel NPU":           "#0071C5",  # blue
    "Apple Neural Engine": "#A2AAAD",  # gray
    "Qualcomm Hexagon NPU":"#9B4DCA",  # purple
    "NVIDIA AI TOPS":      "#76B900",  # green
}
SHAPES = {
    "Intel NPU":           16,  # filled circle
    "Apple Neural Engine": 15,  # filled square
    "Qualcomm Hexagon NPU":18,  # filled diamond
    "NVIDIA AI TOPS":      17,  # filled triangle
}
LINETYPES = {
    "Intel NPU":           "solid",
    "Apple Neural Engine": "dashed",
    "Qualcomm Hexagon NPU":"dotted",
    "NVIDIA AI TOPS":      "dotdash",
}

# ── Plot ──────────────────────────────────────────────────────────────────────

p = (
    ggplot(df, aes(x="year", y="tops", color="manufacturer",
                   shape="manufacturer", linetype="manufacturer"))
    + geom_line(size=1.2)
    + geom_point(size=3.5)
    # Annotations for latest generation per manufacturer
    + geom_label(
        data=latest_labels,
        mapping=aes(x="year", y="tops", label="label", color="manufacturer"),
        size=2.8,
        fill="#ffffff",
        alpha=0.85,
        nudge_x=0.35,
        nudge_y=25,
        show_legend=False,
        label_padding=4.5,
        label_r=3,
    )
    # ── Scales ────────────────────────────────────────────────────────────────
    + scale_x_continuous(
        breaks=list(range(2020, 2029)),
        limits=[2019.5, 2028.5],
        format="d",
    )
    + scale_y_log10(
        breaks=[10, 20, 40, 80, 160, 320, 640, 1280],
        limits=[8, 1500],
    )
    + scale_color_manual(
        values=COLORS,
        guide=guide_legend(
            title=None,
            ncol=1,
        ),
    )
    + scale_shape_manual(
        values=SHAPES,
        guide=guide_legend(title=None, ncol=1),
    )
    + scale_linetype_manual(
        values=LINETYPES,
        guide=guide_legend(title=None, ncol=1),
    )
    # ── Labels ────────────────────────────────────────────────────────────────
    + labs(
        title="NPU & AI Accelerator Performance: TOPS Over Generations",
        subtitle="Measured in INT8 trillion operations per second (TOPS)",
        x="Year",
        y="TOPS (INT8)",
        caption="Sources: Intel, Apple, Qualcomm, NVIDIA official specs and product announcements",
    )
    # ── Theme ─────────────────────────────────────────────────────────────────
    + theme(
        text=element_text(family="sans-serif"),
        plot_title=element_text(size=16, face="bold", margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=11, color="#555555", margin=[0, 0, 12, 0]),
        plot_caption=element_text(size=8, color="#888888", margin=[10, 0, 0, 0]),
        axis_title_x=element_text(size=11),
        axis_title_y=element_text(size=11),
        axis_text_x=element_text(size=9, angle=0),
        axis_text_y=element_text(size=9),
        legend_position="right",
        legend_text=element_text(size=10),
        legend_background=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        plot_background=element_rect(fill="#FAFAFA"),
        panel_background=element_rect(fill="#FFFFFF"),
        axis_line_x=element_line(color="#CCCCCC"),
        axis_line_y=element_line(color="#CCCCCC"),
    )
)

# ── Save ──────────────────────────────────────────────────────────────────────

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
png_path = output_dir / "ai-consumer-hardware-race_npu_tops_trajectory.png"

ggsave(p, str(png_path), path=str(output_dir), w=8, h=4.8, dpi=150, unit="in")
print(f"Chart saved: {png_path.resolve()}")
