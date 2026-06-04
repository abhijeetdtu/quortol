#!/usr/bin/env python3
"""
chart3_ai-consumer-hardware-race_price_vram_scatter.py

Scatter plot: Price (USD, log scale) vs VRAM (GB) for consumer GPUs.
Bubble size represents memory bandwidth (GB/s).
Color-coded by manufacturer (NVIDIA, AMD, Apple).

Output: 1200×720 px PNG at 150 DPI.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
data = {
    "GPU": [
        "RTX 3060 12GB", "RX 9060 XT 16GB", "RTX 5060 Ti 16GB",
        "RTX 5070", "RX 9070", "RX 9070 XT", "RTX 3090 (used)",
        "RTX 5070 Ti", "RTX 5080", "RX 7900 XTX", "RTX 4090",
        "RTX 5090", "DGX Spark", "Mac M4 Max 128GB",
    ],
    "Price": [249, 349, 429, 549, 549, 599, 850, 749, 999, 900, 1600, 1999, 3000, 3950],
    "VRAM": [12, 16, 16, 12, 16, 16, 24, 16, 16, 24, 24, 32, 128, 128],
    "Bandwidth": [360, 320, 288, 672, 640, 640, 936, 896, 960, 960, 1008, 1792, 273, 546],
    "Manufacturer": [
        "NVIDIA", "AMD", "NVIDIA", "NVIDIA", "AMD", "AMD", "NVIDIA",
        "NVIDIA", "NVIDIA", "AMD", "NVIDIA", "NVIDIA", "NVIDIA", "Apple",
    ],
}
df = pd.DataFrame(data)

# ── Color palette ─────────────────────────────────────────────────────────────
color_map = {"NVIDIA": "#76B900", "AMD": "#ED1C24", "Apple": "#A2AAAD"}

# ── Annotation data frames ────────────────────────────────────────────────────
# Reference-line labels (offset slightly above each threshold line)
ref_labels = pd.DataFrame({
    "x": [195, 195, 195],
    "y": [13.0, 25.0, 49.0],
    "label": ["12 GB (Entry)", "24 GB (Enthusiast)", "48 GB (70B sweet spot)"],
})

# Top-right interpretive annotation
annotation = pd.DataFrame({
    "x": [4200],
    "y": [115],
    "label": ["↑ Higher & rightward =\nMore VRAM for less money"],
})

# ── Build the plot ────────────────────────────────────────────────────────────
p = (
    ggplot()
    # Bubble layer
    + geom_point(
        aes(x="Price", y="VRAM", color="Manufacturer", size="Bandwidth"),
        data=df, alpha=0.85,
    )
    # GPU name labels (nudged above points, hidden from legend)
    + geom_text(
        aes(x="Price", y="VRAM", label="GPU"),
        data=df, nudge_y=4.5, size=8, show_legend=False, alpha=0.85,
    )
    # VRAM threshold reference lines
    + geom_hline(yintercept=12, linetype="dashed", color="#888888", size=0.5)
    + geom_hline(yintercept=24, linetype="dashed", color="#888888", size=0.5)
    + geom_hline(yintercept=48, linetype="dashed", color="#888888", size=0.5)
    # Reference line labels
    + geom_text(
        aes(x="x", y="y", label="label"),
        data=ref_labels, size=7.5, color="#888888", hjust=0,
    )
    # Top-right annotation
    + geom_text(
        aes(x="x", y="y", label="label"),
        data=annotation, size=8.5, color="#333333", hjust=1, fontface="italic",
    )
    # Scales
    + scale_x_log10(
        limits=[175, 5000],
        breaks=[200, 500, 1000, 2000, 4000],
        labels=["$200", "$500", "$1,000", "$2,000", "$4,000"],
    )
    + scale_y_continuous(
        limits=[0, 138],
        breaks=[0, 12, 16, 24, 32, 48, 64, 96, 128],
    )
    + scale_color_manual(values=color_map)
    + scale_size(
        range=[4, 18],
        name="Memory Bandwidth\n(GB/s)",
        breaks=[288, 546, 960, 1792],
    )
    # Labels
    + labs(
        title="Price vs. VRAM: The Local AI Buyer's Map",
        subtitle=(
            "Bubble size represents memory bandwidth — "
            "the real speed determinant for LLM inference"
        ),
        x="Price (USD, log scale)",
        y="VRAM (GB)",
        caption="Sources: NVIDIA, AMD, Apple official specs; street prices mid-2026",
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold", hjust=0),
        plot_subtitle=element_text(size=11, color="#555555", hjust=0, margin=[0, 0, 12, 0]),
        plot_caption=element_text(size=9, color="#999999", hjust=1, margin=[10, 0, 0, 0]),
        axis_title=element_text(size=12),
        axis_text=element_text(size=10),
        legend_title=element_text(size=11, face="bold"),
        legend_text=element_text(size=10),
        legend_position="right",
        panel_grid_major=element_line(color="#e0e0e0", size=0.4),
        panel_grid_minor=element_blank(),
    )
)

# ── Output paths ──────────────────────────────────────────────────────────────
script_dir = Path(__file__).parent.resolve()
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

png_path = images_dir / "ai-consumer-hardware-race_price_vram_scatter.png"
print(f"Saving chart → {png_path}")

# ── Save at 1200×720 px, 150 DPI ─────────────────────────────────────────────
# 1200 / 150 = 8 inches wide, 720 / 150 = 4.8 inches tall
ggsave(p, str(png_path), w=8, h=4.8, unit="in", dpi=150)

print("Done.")
