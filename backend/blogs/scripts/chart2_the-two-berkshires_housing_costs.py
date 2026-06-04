#!/usr/bin/env python3
"""
Chart: The Berkshire Housing Squeeze
Two-bar chart showing median home price escalation in Berkshire County, MA.

Data: UMass Donahue Institute / The Warren Group
- 2014 median sale price: $225,260 (2024 dollars)
- 2024 median sale price: $318,000 (2024 dollars)
- Rent increase: 35% between Jan 2021 and Oct 2024

Output: 1200×720 px PNG at 150 DPI.

Design fixes over lets-plot version:
  - Moved rent annotation to UPPER LEFT corner (was overlapping chart edge)
  - Increased gap between dollar label and "+41% adjusted" annotation
  - Wider bars (0.65 vs 0.55) for better proportion with 2 bars
  - Explicit axes position prevents caption/subtitle clipping
  - Uses matplotlib for precise manual label positioning
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

years = ["2014", "2024"]
prices = [225_260, 318_000]
colors = ["#EF8A62", "#B2182B"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIGURE SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)

# Canvas background
fig.patch.set_facecolor("white")

# Explicit axes position (left, bottom, width, height) in figure coords.
# Leaves room at top for title/subtitle and at bottom for caption.
ax.set_position([0.09, 0.07, 0.87, 0.78])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BARS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

bar_width = 0.65
x_pos = [0, 1]

bars = ax.bar(
    x_pos,
    prices,
    width=bar_width,
    color=colors,
    edgecolor="#333333",
    linewidth=0.6,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DOLLAR LABELS ABOVE BARS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

dollar_y_off = 18_000  # points above bar top

for x, price in zip(x_pos, prices):
    ax.text(
        x,
        price + dollar_y_off,
        f"${price:,}",
        ha="center",
        va="bottom",
        fontsize=13,
        fontweight="bold",
        color="#333333",
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PERCENTAGE ANNOTATION ABOVE 2024 BAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Generous gap (72_000 vs dollar_y_off of 18_000 = 54_000 pts of clearance)

pct_y_off = 72_000

ax.text(
    1,
    prices[1] + pct_y_off,
    "+41% adjusted",
    ha="center",
    va="bottom",
    fontsize=9.5,
    fontweight="bold",
    color="#B2182B",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RENT ANNOTATION — UPPER LEFT CORNER (axes coordinates)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Using axes coords so it stays in the upper-left plot corner regardless of
# data values.

ax.text(
    0.03,
    0.88,
    "Rents rose 35%\nJan 2021 – Oct 2024",
    transform=ax.transAxes,
    ha="left",
    va="top",
    fontsize=9.5,
    color="#8D4B2B",
    bbox=dict(
        boxstyle="round,pad=0.35",
        facecolor="#FFF3E0",
        edgecolor="#CC9966",
        linewidth=0.8,
        alpha=0.95,
    ),
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AXES SCALES & FORMATTING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ax.set_xlim(-0.6, 1.6)
ax.set_ylim(0, 420_000)

ax.set_xticks(x_pos)
ax.set_xticklabels(years, fontsize=13, fontweight="bold", color="#333333")

ax.set_yticks([0, 100_000, 200_000, 300_000, 400_000])
ax.set_yticklabels(
    ["$0", "$100K", "$200K", "$300K", "$400K"],
    fontsize=11,
    color="#555555",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LABELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ax.set_ylabel(
    "Median Sale Price (2024 $)",
    fontsize=12,
    color="#555555",
    labelpad=10,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TITLE & SUBTITLE (figure-level text for precise placement)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fig.text(
    0.5,
    0.97,
    "The Berkshire Housing Squeeze",
    ha="center",
    va="top",
    fontsize=20,
    fontweight="bold",
    color="#1a1a1a",
)

fig.text(
    0.5,
    0.92,
    "Median home price up 41% (inflation-adjusted) • Rents up 35% since 2021",
    ha="center",
    va="top",
    fontsize=11,
    color="#666666",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CAPTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fig.text(
    0.09,
    0.025,
    "Source: The Warren Group via UMass Donahue Institute",
    fontsize=9,
    color="#999999",
    ha="left",
    va="bottom",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GRID
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ax.grid(axis="y", color="#E8E8E8", linewidth=0.35)
ax.grid(axis="x", visible=False)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SPINES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#CCCCCC")
ax.spines["left"].set_linewidth(0.5)
ax.spines["bottom"].set_color("#CCCCCC")
ax.spines["bottom"].set_linewidth(0.5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BACKGROUND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ax.set_facecolor("#FCFCFC")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

script_dir = Path(__file__).parent.resolve()
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

png_path = images_dir / "the-two-berkshires_housing_costs.png"

fig.savefig(
    png_path,
    dpi=150,
    facecolor="white",
    edgecolor="none",
    bbox_inches=None,   # use explicit axes positioning instead of auto-fit
)

plt.close(fig)

print(f"Chart saved to: {png_path}")
print(f"Script:       {__file__}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if png_path.exists() and png_path.stat().st_size > 0:
    size_kb = png_path.stat().st_size / 1024

    from PIL import Image

    img = Image.open(str(png_path))
    w, h = img.size
    print(f"Verified: {size_kb:.1f} KB — {w}×{h} px")

    # Scan middle band for expected bar colours (dithering allowed ±2)
    has_light = False
    has_dark = False
    for px in range(0, w, 10):
        for py in range(h // 3, 2 * h // 3, 10):
            r, g, b = img.getpixel((px, py))[:3]
            if abs(r - 239) <= 2 and abs(g - 138) <= 2 and abs(b - 98) <= 2:
                has_light = True
            if abs(r - 178) <= 2 and abs(g - 24) <= 2 and abs(b - 43) <= 2:
                has_dark = True

    print(f"Verified: Light bar (#EF8A62) present: {has_light}")
    print(f"Verified: Dark bar (#B2182B) present: {has_dark}")

    if not (has_light and has_dark):
        raise RuntimeError("ERROR: Bar colours not found in rendered image")
else:
    raise RuntimeError(f"ERROR: Chart file not found or zero-size: {png_path}")
