#!/usr/bin/env python3
"""
Chart: The Shrinking Transistor — From Microns to the Atomic Limit
Output: ../images/atomic-printing_transistor_scaling.png  (1200 × 720 px, 150 DPI)

Semilog line chart showing transistor feature size (nm) by year (1970–2030),
with historical nodes, projected nodes, atomic-scale limit line, and
Moore's Law end-zone shading.

Data: Industry roadmaps, IEEE IRDS, historical node data
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA  —  transistor feature size (nm) by year
# ============================================================================
df = pd.DataFrame({
    "year": [
        1970, 1975, 1980, 1985, 1990, 1995,
        1998, 2001, 2004, 2006, 2008, 2010,
        2012, 2014, 2016, 2018, 2020, 2022,
        2024, 2026, 2028, 2030,
    ],
    "feature_size_nm": [
        10000, 5000, 3000, 1500, 800, 350,
        250, 180, 130, 90, 65, 45,
        32, 22, 14, 10, 7, 5,
        3, 2, 1.4, 0.5,
    ],
    "projected": [False] * 19 + [True] * 3,  # 2026, 2028, 2030 are projected
})

# Node labels — abbreviate very old nodes to save space
df["node_label"] = [
    "10µ", "5µ", "3µ", "1.5µ",       # abbreviated for 1970–1985
    "0.8µm", "0.35µm",
    "0.25µm", "180nm", "130nm", "90nm", "65nm", "45nm",
    "32nm", "22nm", "14nm", "10nm", "7nm", "5nm",
    "3nm", "2nm*", "1.4nm*", "0.5nm*",
]

# ---- Staggered label positioning ----
# Even-indexed historical rows → label above; odd-indexed → label below.
# Projected points: 2026, 2028 above; 2030 (atomic limit) below.
vjust_vals = []
hjust_vals = []
for i, (_, row) in enumerate(df.iterrows()):
    if row["year"] in (2026, 2028):
        vjust_vals.append(-1.2)
        hjust_vals.append(0)   # left-aligned
    elif row["year"] == 2030:
        vjust_vals.append(1.5)
        hjust_vals.append(1)   # right-aligned
    else:
        # Historical: even index → above, odd index → below
        if i % 2 == 0:
            vjust_vals.append(-1.2)
            hjust_vals.append(0)   # left-aligned
        else:
            vjust_vals.append(1.5)
            hjust_vals.append(1)   # right-aligned

df["vjust_val"] = vjust_vals
df["hjust_val"] = hjust_vals

# ============================================================================
# 2. ANNOTATION DATA
# ============================================================================

# -- Atomic limit reference line label --
atomic_label_df = pd.DataFrame({
    "x": [1972],
    "y": [0.5],
    "label": ["Atomic Scale Limit  (~0.5 nm, ~2 Si atoms)"],
})

# -- Moore's Law End Zone label --
endzone_label_df = pd.DataFrame({
    "x": [2027.5],
    "y": [12000],  # near top of chart
    "label": ["Moore's Law\nEnd Zone"],
})

# -- Arrow pointing to the 2030 atomic limit point --
# Arrow starts above-right of the 2030 point and points down-left to it
arrow_df = pd.DataFrame({
    "x": [2032.5],
    "y": [2.5],
    "xend": [2030.3],
    "yend": [0.7],
})

# ============================================================================
# 3. Y-AXIS BREAKS & LABELS
# ============================================================================
y_breaks = [10000, 1000, 100, 10, 1, 0.5]
y_labels = ["10 µm", "1 µm", "100 nm", "10 nm", "1 nm", "0.5 nm"]

# ============================================================================
# 4. BUILD THE PLOT
# ============================================================================
p = (
    ggplot(df)

    # ---- Moore's Law End Zone shading (2025–2030) ----
    + geom_rect(
        xmin=2025, xmax=2030,
        ymin=0.1, ymax=20000,
        fill="#FFB6C1", alpha=0.25,
    )
    + geom_text(
        aes(x="x", y="y", label="label"),
        data=endzone_label_df,
        color="#CC5555", size=10, hjust=0.5, vjust=1,
        family="sans", lineheight=1.2,
    )

    # ---- Main data line ----
    + geom_line(
        aes(x="year", y="feature_size_nm"),
        color="#0072B2", size=1.2,
    )

    # ---- Historical nodes (solid circles) ----
    + geom_point(
        aes(x="year", y="feature_size_nm"),
        data=df[~df["projected"]],
        color="#0072B2", size=2.5,
    )

    # ---- Projected nodes (open circles) ----
    + geom_point(
        aes(x="year", y="feature_size_nm"),
        data=df[df["projected"]],
        color="#0072B2", size=2.5,
        shape=1,  # open circle
        stroke=1.2,
    )

    # ---- Node labels (staggered to avoid overlap) ----
    + geom_text(
        aes(x="year", y="feature_size_nm", label="node_label",
            vjust="vjust_val", hjust="hjust_val"),
        data=df,
        color="#333333", size=6.0,
        family="sans",
    )

    # ---- Atomic limit reference line ----
    + geom_hline(
        yintercept=0.5,
        linetype="dashed", color="#D55E00", size=0.9,
    )
    + geom_text(
        aes(x="x", y="y", label="label"),
        data=atomic_label_df,
        color="#D55E00", size=9, hjust=0, vjust=-0.5,
        family="sans", fontface="italic",
    )

    # ---- Arrow pointing to 2030 atomic limit point ----
    + geom_segment(
        aes(x="x", y="y", xend="xend", yend="yend"),
        data=arrow_df,
        color="#D55E00", size=0.7,
        arrow=arrow(length=10, type="closed", angle=25),
    )

    # ---- Scales ----
    + scale_x_continuous(
        breaks=list(range(1970, 2036, 5)),
        limits=(1968, 2035),
        expand=[0, 0],
    )
    + scale_y_log10(
        breaks=y_breaks,
        labels=y_labels,
        limits=(0.08, 22000),
    )

    # ---- Labels ----
    + labs(
        title="The Shrinking Transistor: From Microns to the Atomic Limit",
        subtitle="Semiconductor feature size (nm) by year — historical nodes and industry projections",
        x="Year",
        y="Feature Size (log scale)",
        caption="Source: Industry roadmaps, IEEE IRDS, historical node data",
    )

    # ---- Theme ----
    + theme_minimal()
    + theme(
        # Title block
        plot_title       = element_text(size=20, face="bold", margin=[0, 0, 4, 0]),
        plot_subtitle    = element_text(size=12, color="#555555", margin=[0, 0, 12, 0]),
        plot_caption     = element_text(size=9, color="#888888", margin=[8, 0, 0, 0]),

        # Axes
        axis_title_x     = element_text(size=12, margin=[8, 0, 0, 0]),
        axis_title_y     = element_text(size=12, margin=[0, 8, 0, 0]),
        axis_text_x      = element_text(size=10, angle=0),
        axis_text_y      = element_text(size=10),

        # Grid lines — light gray
        panel_grid_major_x = element_line(color="#e0e0e0", size=0.4),
        panel_grid_minor_x = element_line(color="#f0f0f0", size=0.2),
        panel_grid_major_y = element_line(color="#e0e0e0", size=0.4),
        panel_grid_minor_y = element_line(color="#f0f0f0", size=0.2),

        # Margins (top, right, bottom, left) — increased right margin
        plot_margin      = [15, 40, 10, 15],

        # Legend (none — all annotations are inline)
        legend_position  = "none",
    )
)

# ============================================================================
# 5. SAVE PNG  —  1200 × 720 px @ 150 DPI  →  8 × 4.8 in
# ============================================================================
# Save as SVG first (more reliable export), then convert to PNG
svg_path = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "atomic-printing_transistor_scaling.svg"
)
output_path = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "atomic-printing_transistor_scaling.png"
)

# Save as SVG
ggsave(p, svg_path, w=8, h=4.8, unit="in", dpi=150)
print(f"✓ SVG saved to {svg_path}")

# Convert SVG to PNG using rsvg-convert
import subprocess
result = subprocess.run(
    ["rsvg-convert", "-w", "1200", "-h", "720",
     "-o", str(output_path), str(svg_path)],
    capture_output=True, text=True,
)
if result.returncode == 0:
    print(f"✓ Converted to PNG via rsvg-convert: {output_path}")
else:
    print(f"✗ rsvg-convert failed: {result.stderr}")

# Verify the PNG
import struct
with open(output_path, "rb") as f:
    data = f.read()
    print(f"  PNG file size: {len(data)} bytes")
    if data[12:16] == b'IHDR':
        w, h = struct.unpack('>II', data[16:24])
        print(f"  Dimensions: {w} × {h} px")
    # IEND is the last chunk: 4-byte length (0) + "IEND" + 4-byte CRC = 8 bytes at end
    if data[-8:-4] == b'IEND':
        print("  IEND chunk found — valid PNG")
    else:
        print("  WARNING: IEND chunk not found — file may be truncated")
