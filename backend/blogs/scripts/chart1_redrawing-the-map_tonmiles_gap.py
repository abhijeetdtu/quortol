"""
Chart 1: "The Distance Paradox: Trade Volume vs. Ton-Miles"
Line chart showing the widening gap between seaborne trade volume growth
and distance-adjusted ton-mile growth (2018–2025).
lets-plot 4.9.0, 1200×720 px, 150 DPI, colorblind-safe (Wong 2011).

Data source: UNCTAD Review of Maritime Transport 2025

Note: lets-plot does not natively support sec_axis. This chart uses indexed
values on a single axis with raw-value annotation labels — a cleaner
alternative that avoids dual-axis distortion.
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

# Trade volume in million tons (projected for 2025)
volume = [12180, 12100, 11550, 12050, 12100, 12450, 12720, 12784]

# Ton-miles in billion ton-miles (projected for 2025)
tonmiles = [58500, 58200, 55800, 58100, 59200, 63000, 66781, 66980]

df = pd.DataFrame({
    "year": years,
    "volume_mt": volume,
    "tonmiles_btm": tonmiles,
})

# Indexed values (2018 = 100)
base_volume = df["volume_mt"].iloc[0]       # 12180
base_tonmiles = df["tonmiles_btm"].iloc[0]  # 58500
df["volume_index"] = df["volume_mt"] / base_volume * 100
df["tonmiles_index"] = df["tonmiles_btm"] / base_tonmiles * 100

# ---------------------------------------------------------------------------
# Reshape to long form
# ---------------------------------------------------------------------------
df_long = pd.melt(
    df,
    id_vars=["year", "volume_mt", "tonmiles_btm"],
    value_vars=["volume_index", "tonmiles_index"],
    var_name="metric",
    value_name="indexed",
)

metric_labels = {"volume_index": "Trade Volume", "tonmiles_index": "Ton-Miles"}
df_long["metric_label"] = df_long["metric"].map(metric_labels)

# Pre-compute all annotation columns
df_long["idx_rd"] = df_long["indexed"].round(1)
df_long["raw_value"] = np.where(
    df_long["metric"] == "volume_index",
    df_long["volume_mt"],
    df_long["tonmiles_btm"],
)
df_long["label_raw"] = df_long.apply(
    lambda r: f"{r['raw_value']:,.0f}"
    + (" mt" if r["metric"] == "volume_index" else " btm"),
    axis=1,
)

# ---------------------------------------------------------------------------
# Colorblind-safe palette (Wong 2011)
# Volume = blue #0072B2, Ton-miles = orange #E69F00
# ---------------------------------------------------------------------------
palette = {"Trade Volume": "#0072B2", "Ton-Miles": "#E69F00"}

# ---------------------------------------------------------------------------
# Pre-compute gap annotation values
# ---------------------------------------------------------------------------
gap_vol = df_long.loc[
    (df_long["metric"] == "volume_index") & (df_long["year"] == 2025), "indexed"
].values[0]
gap_tm = df_long.loc[
    (df_long["metric"] == "tonmiles_index") & (df_long["year"] == 2025), "indexed"
].values[0]
gap_value = round(gap_tm - gap_vol, 1)
gap_mid = (gap_vol + gap_tm) / 2

# ---------------------------------------------------------------------------
# Build chart
# ---------------------------------------------------------------------------
p = (
    # --- Base layers ---
    ggplot(df_long, aes(x="year", y="indexed", color="metric_label"))
    + geom_line(size=1.5)
    + geom_point(size=4, alpha=0.85)
    + geom_hline(yintercept=100, linetype="dashed", color="#999999", size=0.5)
    # --- 2018 start labels ---
    + geom_text(
        data=df_long[df_long["year"] == 2018],
        mapping=aes(label="idx_rd"),
        nudge_x=-0.3,
        size=9,
        fontface="bold",
        show_legend=False,
    )
    # --- 2024 labels (ton-miles) ---
    + geom_text(
        data=df_long[
            (df_long["metric"] == "tonmiles_index") & (df_long["year"] == 2024)
        ],
        mapping=aes(label="label_raw"),
        nudge_x=-0.3,
        nudge_y=1.2,
        size=8,
        show_legend=False,
    )
    # --- 2024 labels (volume) ---
    + geom_text(
        data=df_long[
            (df_long["metric"] == "volume_index") & (df_long["year"] == 2024)
        ],
        mapping=aes(label="label_raw"),
        nudge_x=-0.3,
        nudge_y=-1.2,
        size=8,
        show_legend=False,
    )
    # --- 2025 end labels (ton-miles, right-aligned) ---
    + geom_text(
        data=df_long[
            (df_long["metric"] == "tonmiles_index") & (df_long["year"] == 2025)
        ],
        mapping=aes(label="label_raw"),
        nudge_x=0.4,
        nudge_y=1.5,
        size=9,
        fontface="bold",
        show_legend=False,
        hjust=0,
    )
    # --- 2025 end labels (volume, right-aligned) ---
    + geom_text(
        data=df_long[
            (df_long["metric"] == "volume_index") & (df_long["year"] == 2025)
        ],
        mapping=aes(label="label_raw"),
        nudge_x=0.4,
        nudge_y=-1.5,
        size=9,
        fontface="bold",
        show_legend=False,
        hjust=0,
    )
    # --- 2023 inflection label (ton-miles) ---
    + geom_text(
        data=df_long[
            (df_long["metric"] == "tonmiles_index") & (df_long["year"] == 2023)
        ],
        mapping=aes(label="label_raw"),
        nudge_x=-0.3,
        nudge_y=0.8,
        size=8,
        show_legend=False,
    )
    # --- Gap annotation ---
    + geom_text(
        label=f"Gap: {gap_value} pts",
        x=2025.7,
        y=gap_mid,
        size=8.5,
        color="#CC3333",
        fontface="bold",
    )
    # --- Scales ---
    + scale_x_continuous(breaks=years, limits=[2017.2, 2026.8])
    + scale_y_continuous(
        name="Index (2018 = 100)",
        limits=[90, 120],
        breaks=[92, 96, 100, 104, 108, 112, 116],
    )
    + scale_color_manual(values=palette)
    # --- Labels ---
    + labs(
        title="The Distance Paradox: Trade Volume vs. Ton-Miles",
        subtitle=(
            "Seaborne trade volume and distance-adjusted ton-miles, indexed to 2018 = 100. "
            "Raw values shown in annotation labels (mt = million tons, btm = billion ton-miles). "
            "The gap widens sharply from 2023 as Red Sea rerouting inflates sailing distances."
        ),
        x="",
        y="",
        color="",
        caption="Source: UNCTAD Review of Maritime Transport 2025",
    )
    # --- Theme ---
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(
            size=11.5, color="#555555", hjust=0, margin=[0, 0, 16, 0]
        ),
        axis_title_y=element_text(size=11, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=10),
        plot_caption=element_text(
            size=9, color="#888888", hjust=0, margin=[14, 0, 0, 0]
        ),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=12),
        panel_grid_major=element_line(color="#E8E8E8", size=0.4),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 30, 10, 10],
    )
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "redrawing-the-map_tonmiles_gap.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 1 saved to: {output_path}")

# Validate
from PIL import Image
import numpy as np
img = Image.open(output_path)
arr = np.array(img)
n_colors = len(np.unique(arr.reshape(-1, arr.shape[2]), axis=0))
print(f"Validation: {arr.shape[1]}×{arr.shape[0]} px, {n_colors} colors, "
      f"{output_path.stat().st_size / 1024:.1f} KB")
