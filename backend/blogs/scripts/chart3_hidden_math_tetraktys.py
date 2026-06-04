#!/usr/bin/env python3
"""
Chart 3: Pythagorean Tetraktys Diagram
=======================================
Generates a clean, elegant diagram of the tetraktys — the ancient Greek symbol
of cosmic mathematical order — using lets-plot.

The tetraktys is a triangular arrangement of ten dots in four rows:
  Row 1: 1 dot
  Row 2: 2 dots
  Row 3: 3 dots
  Row 4: 4 dots

Each row is centered, forming an equilateral triangle pointing upward.

Color palette: warm cream parchment (#F5F0E8), dark ink dots (#2C1810).

Output: 800 × 800 px PNG, 150 DPI
"""

from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------
script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_png = images_dir / "hidden-math-in-what-you-hear_tetraktys.png"

# ── Constants ─────────────────────────────────────────────────────────────
INK      = "#2C1810"   # dark brown / ancient ink
PARCHMENT = "#F5F0E8"  # warm cream background
BORDER   = "#C4A97D"   # tan border
CORNER   = "#A08060"   # corner bracket colour

# ---------------------------------------------------------------------------
# Geometry — equilateral triangle
# ---------------------------------------------------------------------------
# With unit horizontal spacing between dot centres, the vertical distance
# between rows must be sqrt(3)/2 to preserve equilateral proportions.
D = 3 ** 0.5 / 2.0          # ≈ 0.866

dots = []
for row, count in enumerate([1, 2, 3, 4], start=1):
    y = (4 - row) * D        # row 1 at y = 3D (top), row 4 at y = 0 (bottom)
    for i in range(count):
        x = i - (count - 1) / 2.0
        dots.append({"x": x, "y": y, "row": row})

df_dots = pd.DataFrame(dots)

# ---------------------------------------------------------------------------
# Row labels (right of each row)
# ---------------------------------------------------------------------------
df_labels = pd.DataFrame({
    "x": 2.7,
    "y": [(4 - r) * D for r in range(1, 5)],
    "label": [str(r) for r in range(1, 5)],
})

# ---------------------------------------------------------------------------
# Decorative corner brackets — subtle manuscript-border feel
# ---------------------------------------------------------------------------
corner_sz = 0.35
# Coordinates for four L-shaped brackets: one at each corner of the text area
# (inside the viewport but framing the composition).
corners = pd.DataFrame({
    "x": [
        # top-left corner: ┐ shape (horizontal then vertical)
        -3.2, -2.6,
        -3.2, -3.2 + corner_sz,
        # top-right corner: ┌ shape
        3.7,  3.1,
        3.7 - corner_sz, 3.7,
        # bottom-left corner: ┘ shape
        -3.2, -2.6,
        -3.2, -3.2 + corner_sz,
        # bottom-right corner: └ shape
        3.7,  3.1,
        3.7 - corner_sz, 3.7,
    ],
    "y": [
        # top-left
        3.55, 3.55,
        3.55, 3.55 - corner_sz,
        # top-right
        3.55, 3.55,
        3.55, 3.55 - corner_sz,
        # bottom-left
        -2.0, -2.0,
        -2.0, -2.0 + corner_sz,
        # bottom-right
        -2.0, -2.0,
        -2.0, -2.0 + corner_sz,
    ],
    "group": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8],
})

# ---------------------------------------------------------------------------
# Text labels below triangle
# ---------------------------------------------------------------------------
df_title = pd.DataFrame({
    "x": [0],
    "y": [-1.0],
    "label": ["The Tetraktys: 1 + 2 + 3 + 4 = 10"],
})

df_subtitle = pd.DataFrame({
    "x": [0],
    "y": [-1.7],
    "label": ["Contains the ratios of musical consonance: 2:1, 3:2, 4:3"],
})

# ---------------------------------------------------------------------------
# Build the plot
# ---------------------------------------------------------------------------
p = (
    ggplot()
    # ── Ten dots of the tetraktys ───────────────────────────────────────
    + geom_point(
        data=df_dots,
        mapping=aes(x="x", y="y"),
        shape=19,              # solid circle
        size=13,
        color=INK,
    )
    # ── Row number labels (right side) ──────────────────────────────────
    + geom_text(
        data=df_labels,
        mapping=aes(x="x", y="y", label="label"),
        family="serif",
        size=11,
        color=INK,
        hjust=0,
        vjust=0.5,
    )
    # ── Primary label below the triangle ────────────────────────────────
    + geom_text(
        data=df_title,
        mapping=aes(x="x", y="y", label="label"),
        family="serif",
        size=13,
        color=INK,
        hjust=0.5,
        vjust=1,
    )
    # ── Secondary label — musical ratios ────────────────────────────────
    + geom_text(
        data=df_subtitle,
        mapping=aes(x="x", y="y", label="label"),
        family="serif",
        size=9,
        color=INK,
        hjust=0.5,
        vjust=1,
        fontface="italic",
    )
    # ── Decorative corner brackets ──────────────────────────────────────
    + geom_line(
        data=corners,
        mapping=aes(x="x", y="y", group="group"),
        color=CORNER,
        size=0.6,
    )
    # ── Clean theme — no axes, parchment background ─────────────────────
    + theme_void()
    + theme(
        plot_background=element_rect(
            fill=PARCHMENT,
            color=BORDER,
            size=1.5,
        ),
        plot_margin=0,
    )
    # Fixed aspect ratio → equilateral triangle stays equilateral
    + coord_fixed(ratio=1)
    # Viewport — room for labels below and space around
    + xlim(-3.5, 4.0)
    + ylim(-2.3, 3.8)
)

# ---------------------------------------------------------------------------
# Save — 800 × 800 px at 150 DPI  →  5.333 × 5.333 inches
# ---------------------------------------------------------------------------
inch = 800.0 / 150.0

# Save at slightly larger size, then crop/resize precisely to 800×800
tmp_png = images_dir / "_tmp_tetraktys.png"
ggsave(p, str(tmp_png), w=inch, h=inch, unit="in", dpi=150)

# ---------------------------------------------------------------------------
# Post-process: RGBA → RGB, fill any transparency, enforce exact 800×800
# ---------------------------------------------------------------------------
# Parse the parchment hex colour into an RGB tuple for PIL
bg_rgb = tuple(int(PARCHMENT.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
bg_rgba = bg_rgb + (255,)

with Image.open(tmp_png) as img:
    # Convert RGBA to RGB, filling transparent pixels with parchment colour
    if img.mode == "RGBA":
        background = Image.new("RGBA", img.size, bg_rgba)
        background.paste(img, mask=img.split()[3])  # use alpha as mask
        img = background.convert("RGB")
    else:
        img = img.convert("RGB")

    # Resize to exactly 800×800 if off by 1–2 px
    if img.size != (800, 800):
        img = img.resize((800, 800), Image.LANCZOS)

    img.save(output_png, dpi=(150, 150))

# Clean up temp file
tmp_png.unlink(missing_ok=True)

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
if output_png.exists():
    size_kb = output_png.stat().st_size / 1024
    with Image.open(output_png) as v:
        actual_size = v.size
        actual_mode = v.mode
        # Verify background is parchment at a corner
        px = v.getpixel((0, 0))
        bg_ok = px[:3] == (245, 240, 232)
    print(f"Saved: {output_png}")
    print(f"  Dimensions: {actual_size[0]} × {actual_size[1]} px @ 150 DPI")
    print(f"  Mode:       {actual_mode}")
    print(f"  File size:  {size_kb:.1f} KB")
    print(f"  Background: {'✓ parchment' if bg_ok else '⚠ unexpected'}")
else:
    print(f"ERROR: file was not created at {output_png}")
