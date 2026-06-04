#!/usr/bin/env python3
"""
Horizontal bar chart: VRAM capacity across consumer GPUs in 2026.

Generates a horizontal bar chart sorted by VRAM (largest at top),
color-coded by manufacturer with brand colors. Top 3 GPUs highlighted
via full opacity (others slightly faded). Each bar annotated with VRAM value.

Output: 1200x720 px PNG at 150 DPI.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────

data = {
    "GPU": [
        "RTX 5050", "RTX 5060", "RTX 4060 Ti", "RTX 5060 Ti 8GB",
        "RX 9060 XT 8GB", "RTX 3060 12GB", "RTX 4070", "RTX 5070",
        "RX 9060 XT 16GB", "RTX 5060 Ti 16GB", "RTX 4070 Ti Super",
        "RTX 5070 Ti", "RTX 5080", "RX 9070", "RX 9070 XT",
        "RTX 4080 Super", "RTX 3090", "RTX 4090", "RX 7900 XTX",
        "RTX 5090", "Mac M4 Max 128GB", "DGX Spark",
    ],
    "VRAM_GB": [
        8, 8, 8, 8, 8,
        12, 12, 12,
        16, 16, 16, 16, 16, 16, 16, 16,
        24, 24, 24,
        32,
        128, 128,
    ],
    "Manufacturer": [
        "NVIDIA", "NVIDIA", "NVIDIA", "NVIDIA", "AMD",
        "NVIDIA", "NVIDIA", "NVIDIA",
        "AMD", "NVIDIA", "NVIDIA", "NVIDIA", "NVIDIA", "AMD", "AMD",
        "NVIDIA",
        "NVIDIA", "NVIDIA", "AMD",
        "NVIDIA",
        "Apple", "NVIDIA",
    ],
}

df = pd.DataFrame(data)

# ── Compute highlight flag (top 3 by VRAM) ────────────────────────────────────

# Sort descending by VRAM to identify top 3
df_sorted = df.sort_values("VRAM_GB", ascending=False).reset_index(drop=True)
df_sorted["highlight"] = ["Top 3" if i < 3 else "Other" for i in range(len(df_sorted))]

# ── Y-axis order: ascending VRAM → smallest at bottom, largest at top ────────

gpu_order_asc = df_sorted.sort_values("VRAM_GB", ascending=True)["GPU"].tolist()

# ── Color palette (brand colors) ──────────────────────────────────────────────

brand_colors = {
    "NVIDIA": "#76B900",
    "AMD": "#ED1C24",
    "Apple": "#A2AAAD",
}

# ── Build plot ────────────────────────────────────────────────────────────────

p = (
    ggplot(df_sorted, aes(x="VRAM_GB", y="GPU"))
    + geom_bar(
        aes(fill="Manufacturer", alpha="highlight"),
        stat="identity",
        width=0.75,
    )
    + geom_text(
        aes(label="VRAM_GB"),
        hjust=-0.2,
        size=7.5,
        color="#2d2d2d",
        family="sans-serif",
    )
    + scale_y_discrete(limits=gpu_order_asc)
    + scale_fill_manual(values=brand_colors)
    + scale_alpha_manual(
        values={"Top 3": 1.0, "Other": 0.60},
        guide="none",
    )
    + scale_x_continuous(
        limits=[0, 148],
        breaks=[0, 8, 12, 16, 24, 32, 64, 128],
    )
    + labs(
        title="Consumer AI Hardware: VRAM Capacity, 2026",
        subtitle="VRAM determines which AI models you can run locally",
        x="VRAM (GB)",
        y="",
        fill="Manufacturer",
        caption="Sources: NVIDIA, AMD, Apple official specs; street prices as of mid-2026",
    )
    + theme(
        plot_title=element_text(size=15, face="bold", hjust=0, color="#1a1a1a"),
        plot_subtitle=element_text(size=10.5, hjust=0, color="#555555"),
        plot_caption=element_text(size=7, hjust=0, color="#888888"),
        axis_text_y=element_text(size=7.5),
        axis_text_x=element_text(size=8),
        axis_title_x=element_text(size=9.5),
        legend_title=element_text(size=9),
        legend_text=element_text(size=8),
        legend_position="right",
        legend_background=element_blank(),
        panel_grid_major_x=element_line(color="#e8e8e8", size=0.3),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_blank(),
        panel_background=element_blank(),
        plot_background=element_blank(),
        axis_line_x=element_line(color="#cccccc", size=0.4),
        axis_ticks_y=element_blank(),
        plot_margin=[10, 20, 5, 5],
    )
)

# ── Save PNG ──────────────────────────────────────────────────────────────────

out_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "ai-consumer-hardware-race_vram_comparison.png"
ggsave(
    p,
    str(out_path),
    w=8.0,
    h=4.8,
    unit="in",
    dpi=150,
)

print(f"Chart saved: {out_path}")
