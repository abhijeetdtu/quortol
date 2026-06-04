"""
Chart 2: "The Freight Rate Rollercoaster: Baltic Dry vs. Containerized Freight"
Indexed line chart (2021 = 100) showing the 5-year trend of Baltic Dry Index
and Containerized Freight Index with raw-value annotations at the 2026 endpoint.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe (Wong 2011).

Data source: Baltic Exchange / Trading Economics / Freightos Baltic Index
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
years = [2021, 2022, 2023, 2024, 2025, 2026]

bdi_raw = [3000, 2100, 1600, 1900, 2200, 3100]   # Baltic Dry Index
cfi_raw = [3800, 2500, 1400, 2200, 1900, 2570]   # Containerized Freight Index

df = pd.DataFrame({
    "year": years,
    "bdi": bdi_raw,
    "cfi": cfi_raw,
})

# Indexed values (2021 = 100)
base_bdi = df["bdi"].iloc[0]   # 3000
base_cfi = df["cfi"].iloc[0]   # 3800
df["bdi_index"] = df["bdi"] / base_bdi * 100
df["cfi_index"] = df["cfi"] / base_cfi * 100

# ---------------------------------------------------------------------------
# Reshape to long form
# ---------------------------------------------------------------------------
df_long = pd.melt(
    df,
    id_vars=["year", "bdi", "cfi"],
    value_vars=["bdi_index", "cfi_index"],
    var_name="metric",
    value_name="indexed",
)

metric_labels = {"bdi_index": "Baltic Dry Index", "cfi_index": "Containerized Freight Index"}
df_long["metric_label"] = df_long["metric"].map(metric_labels)

# Compute annotation helpers
df_long["idx_rd"] = df_long["indexed"].round(1)
df_long["raw_value"] = np.where(
    df_long["metric"] == "bdi_index",
    df_long["bdi"],
    df_long["cfi"],
)
df_long["label_raw"] = df_long.apply(
    lambda r: f"{r['raw_value']:,.0f} pts", axis=1,
)

# ---------------------------------------------------------------------------
# Colorblind-safe palette (Wong 2011)
# BDI = blue #0072B2, CFI = orange #E69F00
# ---------------------------------------------------------------------------
palette = {"Baltic Dry Index": "#0072B2", "Containerized Freight Index": "#E69F00"}

# ---------------------------------------------------------------------------
# Build chart
# ---------------------------------------------------------------------------

# Red Sea Crisis shaded region: late 2023 onward
red_sea_start = 2023.75  # ~October 2023
red_sea_end = 2026.5

# Annotation data for 2026 endpoint
bdi_2026 = df_long[(df_long["metric"] == "bdi_index") & (df_long["year"] == 2026)]
cfi_2026 = df_long[(df_long["metric"] == "cfi_index") & (df_long["year"] == 2026)]

p = (
    ggplot(df_long, aes(x="year", y="indexed", color="metric_label"))
    # --- Red Sea Crisis shaded region ---
    + geom_rect(
        xmin=red_sea_start, xmax=red_sea_end,
        ymin=-np.inf, ymax=np.inf,
        fill="#FFF3E0", alpha=0.35,
        color=None,
    )
    + geom_text(
        label="Red Sea Crisis",
        x=red_sea_start + 0.15,
        y=98,
        size=9,
        color="#CC6600",
        fontface="italic",
        hjust=0,
        show_legend=False,
    )
    # --- Line and points ---
    + geom_line(size=1.5)
    + geom_point(size=4, alpha=0.85)
    + geom_hline(yintercept=100, linetype="dashed", color="#999999", size=0.5)
    # --- 2021 start labels ---
    + geom_text(
        data=df_long[df_long["year"] == 2021],
        mapping=aes(label="idx_rd"),
        nudge_x=-0.25,
        size=9,
        fontface="bold",
        show_legend=False,
    )
    # --- 2026 endpoint labels (BDI) ---
    + geom_text(
        data=bdi_2026,
        mapping=aes(label="label_raw"),
        nudge_x=0.35,
        nudge_y=3,
        size=9,
        fontface="bold",
        show_legend=False,
        hjust=0,
        color="#0072B2",
    )
    # --- 2026 endpoint labels (CFI) ---
    + geom_text(
        data=cfi_2026,
        mapping=aes(label="label_raw"),
        nudge_x=0.35,
        nudge_y=-3,
        size=9,
        fontface="bold",
        show_legend=False,
        hjust=0,
        color="#E69F00",
    )
    # --- Scales ---
    + scale_x_continuous(breaks=years, limits=[2020.5, 2027.2])
    + scale_y_continuous(
        name="Index (2021 = 100)",
        limits=[25, 120],
        breaks=[30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
    )
    + scale_color_manual(values=palette)
    # --- Labels ---
    + labs(
        title="The Freight Rate Rollercoaster: Baltic Dry vs. Containerized Freight",
        subtitle=(
            "Annual average, indexed to 2021 = 100. "
            "Raw index-point values shown at the 2026 endpoint."
        ),
        x="",
        y="",
        color="",
        caption="Sources: Baltic Exchange / Trading Economics / Freightos Baltic Index",
    )
    # --- Theme ---
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(
            size=11.5, color="#555555", hjust=0, margin=[0, 0, 16, 0]
        ),
        axis_title_y=element_text(size=11, margin=[0, 10, 0, 0]),
        axis_text_x=element_text(size=12),
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
output_path = output_dir / "redrawing-the-map_freight_volatility.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart 2 saved to: {output_path}")

# Validate
from PIL import Image
import numpy as np
img = Image.open(output_path)
arr = np.array(img)
n_colors = len(np.unique(arr.reshape(-1, arr.shape[2]), axis=0))
print(f"Validation: {arr.shape[1]}×{arr.shape[0]} px, {n_colors} colors, "
      f"{output_path.stat().st_size / 1024:.1f} KB")
