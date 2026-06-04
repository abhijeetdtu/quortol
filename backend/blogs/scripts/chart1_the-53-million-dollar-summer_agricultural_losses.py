#!/usr/bin/env python3
"""Chart: Agricultural Losses from Extreme Weather in Northern New England

Horizontal bar chart for a magazine article about drought losses.

Output: backend/blogs/images/the-53-million-dollar-summer_agricultural_losses.png
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ==============================================================
# DATA
# ==============================================================
df = pd.DataFrame({
    "category": [
        "Maine wild blueberries\n(2025 drought)",
        "Vermont flooding (2023)",
        "Vermont agriculture\n(2025 drought)",
        "Vermont flooding (2024)",
        "Maine apples (2025 drought)",
    ],
    "loss": [30.0, 16.0, 15.9, 15.0, 10.0],
    "type": ["drought", "flood", "drought", "flood", "drought"],
})

# Sort ascending so horizontal bars render largest at top
df = df.sort_values("loss", ascending=True).reset_index(drop=True)

# Dollar labels
df["label"] = df["loss"].apply(lambda v: f"${v:,.1f}M")

print("Data preview:")
print(df.to_string(index=False))

# ==============================================================
# COLORS
# ==============================================================
# Drought → orange-red (Tol bright), Flood → blue (Tol bright)
# Both are colorblind-safe and distinguishable in the Tol scheme.
fill_colors = {"drought": "#D55E00", "flood": "#0072B2"}

# ==============================================================
# CHART
# ==============================================================
p = (
    ggplot(df, aes(x="loss", y="category"))
    + geom_bar(aes(fill="type"), stat="identity", width=0.65)
    + geom_text(
        aes(label="label"),
        hjust=-0.12,
        size=10,
        color="#333333",
        family="sans-serif",
    )
    + scale_fill_manual(values=fill_colors)
    + scale_x_continuous(limits=[0, 40])
    + labs(
        title="Agricultural Losses from Extreme Weather in Northern New England",
        subtitle="Estimated economic damage by event, 2023\u20132025 (US$ millions)",
        x="Losses (US$ millions)",
        y="",
        caption=(
            "Sources: Wild Blueberry Commission of Maine, "
            "VT Agency of Agriculture, Maine Pomological Society"
        ),
    )
    + theme(
        # Titles
        plot_title=element_text(size=16, face="bold", hjust=0),
        plot_subtitle=element_text(size=12, hjust=0, color="#555555"),
        plot_caption=element_text(size=8, hjust=0, color="#888888"),
        # Axis
        axis_text_y=element_text(size=11),
        axis_text_x=element_text(size=10),
        axis_title_x=element_text(size=11),
        axis_title_y=element_text(size=11),
        axis_ticks_y=element_blank(),
        # Grid
        panel_grid_major_x=element_line(color="#EEEEEE", size=0.4),
        panel_grid_major_y=element_blank(),
        # Legend
        legend_position="bottom",
        legend_title=element_blank(),
        legend_text=element_text(size=10),
        # Background
        panel_background=element_blank(),
        plot_background=element_blank(),
        # Margins: top, right, bottom, left
        plot_margin=margin(15, 25, 10, 10),
    )
    + ggsize(1200, 720)
)

# ==============================================================
# SAVE
# ==============================================================
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
try:
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nDirectory ready: {output_dir}")
except OSError as exc:
    print(f"ERROR creating directory {output_dir}: {exc}")
    raise

output_path = output_dir / "the-53-million-dollar-summer_agricultural_losses.png"
ggsave(p, str(output_path), w=1200, h=720, unit="px", dpi=150)
print(f"\nChart saved: {output_path}")
