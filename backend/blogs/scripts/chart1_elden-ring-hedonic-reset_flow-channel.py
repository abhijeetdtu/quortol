#!/usr/bin/env python3
"""
Chart: The Flow Channel — Where Elden Ring Lives
=================================================
Conceptual 2D diagram of Csikszentmihalyi's flow theory applied to
Elden Ring as a high-skill, high-challenge experience that sits
at the upper-right edge of the flow channel.

Zones:
  1. Anxiety (top-left)     — high challenge, low skill
  2. Flow Channel (diagonal) — challenge ≈ skill
  3. Boredom (bottom-right)  — low challenge, high skill

Output: ../images/elden-ring-hedonic-reset_flow-channel.png
          1200 × 720 px  @  150 DPI
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import ScaledTranslation
from pathlib import Path

# ==============================================================================
# 1. STYLING CONSTANTS — colorblind-safe (Wong, 2011)
# ==============================================================================

# Zone fills
ORANGE_ZONE    = "#D4775C"   # Anxiety (warm orange)
BLUE_ZONE      = "#5C8BD4"   # Boredom  (steel blue)
GREEN_ZONE     = "#7AAF7A"   # Flow Channel (sage green)

# Zone borders
GREEN_BORDER   = "#4A8A5E"

# Zone label colours
ORANGE_LABEL   = "#B85A3F"
BLUE_LABEL     = "#3F6DB8"
GREEN_LABEL    = "#3A7A4E"

# Elden Ring marker
GOLD_STAR      = "#D4A017"
GOLD_EDGE      = "#B8860B"
GOLD_TEXT      = "#8B6914"

# "Most games" dots
PURPLE_DOT     = "#8B7AA8"

# Structural
TEXT_COLOR     = "#2C2C2C"
GRID_COLOR     = "#D8D8D8"
SPINE_COLOR    = "#BBBBBB"
SOURCE_COLOR   = "#888888"
BG_COLOR       = "#FFFFFF"
DIAG_COLOR     = "#AAAAAA"   # faint 45° reference line
LOW_HI_COLOR   = "#999999"   # Low / High endpoint labels

# ==============================================================================
# 2. BUILD FIGURE  —  exactly 1200 × 720 px
# ==============================================================================

W_INCH = 8.0
H_INCH = 4.8
DPI_VAL = 150

fig = plt.figure(figsize=(W_INCH, H_INCH), dpi=DPI_VAL)
fig.patch.set_facecolor(BG_COLOR)

# Leave room for the source line at the bottom by adjusting subplot rect
# [left, bottom, right, top] in figure-fraction coordinates
fig.subplots_adjust(left=0.10, bottom=0.15, right=0.97, top=0.90)

ax = fig.add_subplot(111)
ax.set_facecolor(BG_COLOR)

# ----- 2a. Plot area limits & aspect -----
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect("equal")

# ----- 2b. Title -----
ax.set_title(
    "The Flow Channel: Where Elden Ring Lives",
    fontsize=18, fontweight="bold", pad=10, color=TEXT_COLOR,
)

# ----- 2c. Axis labels -----
ax.set_xlabel(
    "Player Skill  →",
    fontsize=12, fontweight="bold", color=TEXT_COLOR, labelpad=6,
)
ax.set_ylabel(
    "Challenge Level  →",
    fontsize=12, fontweight="bold", color=TEXT_COLOR, labelpad=6,
)

# ==============================================================================
# 3. CHANNEL GEOMETRY
# ==============================================================================

x = np.linspace(0, 10, 1500)

# The flow channel narrows at the high end (top-tier flow requires
# more precise skill–challenge matching).  A gentle sine wave adds
# visual interest so the band isn't a rigid straight corridor.
width = 1.60 - 0.035 * x                # 1.60 → 1.25
curve = 0.25 * np.sin(x * np.pi / 10)   # one gentle hump

y_upper = x + width + curve
y_lower = x - width + curve

# ==============================================================================
# 4. SHADED ZONES
# ==============================================================================

# 4a. Flow channel
ax.fill_between(x, y_lower, y_upper,
                color=GREEN_ZONE, alpha=0.30, zorder=1,
                label="_nolegend_")

# 4b. Anxiety — above the upper boundary, clipped to y ≤ 10
ax.fill_between(x, y_upper, 10,
                where=(y_upper <= 10),
                color=ORANGE_ZONE, alpha=0.22, zorder=1,
                label="_nolegend_")

# 4c. Boredom — below the lower boundary, clipped to y ≥ 0
ax.fill_between(x, 0, y_lower,
                where=(y_lower >= 0),
                color=BLUE_ZONE, alpha=0.22, zorder=1,
                label="_nolegend_")

# ==============================================================================
# 5. CHANNEL BOUNDARY LINES
# ==============================================================================

ax.plot(x, y_upper, color=GREEN_BORDER, linewidth=1.0, alpha=0.50, zorder=2)
ax.plot(x, y_lower, color=GREEN_BORDER, linewidth=1.0, alpha=0.50, zorder=2)

# ----- 5a. Faint 45° reference line (y = x) -----
ax.plot([0, 10], [0, 10],
        color=DIAG_COLOR, linewidth=0.5, linestyle=":", alpha=0.35, zorder=0)

# ==============================================================================
# 6. ZONE LABELS
# ==============================================================================

ax.text(1.8, 8.3, "ANXIETY",
        fontsize=12, fontweight="bold", color=ORANGE_LABEL,
        ha="center", va="center", style="italic", zorder=3)

ax.text(8.2, 1.7, "BOREDOM",
        fontsize=12, fontweight="bold", color=BLUE_LABEL,
        ha="center", va="center", style="italic", zorder=3)

ax.text(4.5, 5.4, "FLOW\nCHANNEL",
        fontsize=14, fontweight="bold", color=GREEN_LABEL,
        ha="center", va="center", zorder=3)

# ==============================================================================
# 7. ELDEN RING MARKER & ANNOTATION
# ==============================================================================

er_x, er_y = 7.8, 8.2      # within the upper-right portion of the channel

ax.scatter([er_x], [er_y], s=260, marker="*",
           color=GOLD_STAR, edgecolors=GOLD_EDGE, linewidths=1.5,
           zorder=6, label="_nolegend_")

ax.annotate(
    "ELDEN RING",
    xy=(er_x, er_y),
    xytext=(5.8, 9.4),
    fontsize=12, fontweight="bold", color=GOLD_TEXT,
    ha="center", va="center",
    arrowprops=dict(
        arrowstyle="->", color=GOLD_TEXT, lw=1.6,
        connectionstyle="arc3,rad=0.22",
    ),
    zorder=6,
)

ax.text(er_x + 0.15, er_y - 0.40,
        "high skill · high challenge",
        fontsize=7.5, color=GOLD_TEXT, ha="center", va="top",
        style="italic", zorder=5)

# ==============================================================================
# 8. "MOST GAMES" DOTS
# ==============================================================================

games_pts = [(2.8, 2.8), (3.8, 3.6), (4.6, 5.0)]
for gx, gy in games_pts:
    ax.scatter([gx], [gy], s=50, marker="o",
               color=PURPLE_DOT, alpha=0.60, zorder=4,
               label="_nolegend_")

ax.text(3.8, 2.15, "Most games",
        fontsize=9, color=PURPLE_DOT,
        ha="center", va="center", style="italic", zorder=3)

# ==============================================================================
# 9. GRID & SPINES
# ==============================================================================

ax.grid(True, which="major", axis="both",
        color=GRID_COLOR, linewidth=0.4, alpha=0.6)
ax.set_axisbelow(True)

ax.set_xticks([])
ax.set_yticks([])

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color(SPINE_COLOR)
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_color(SPINE_COLOR)
ax.spines["bottom"].set_linewidth(0.6)

# ==============================================================================
# 10. AXIS ENDPOINT LABELS  (Low / High)
# ==============================================================================

# Placed relative to axes so they stay inside the figure
ax.text(0.00, -0.055, "Low",
        fontsize=8.5, color=LOW_HI_COLOR, ha="left", va="top",
        transform=ax.transAxes)
ax.text(1.00, -0.055, "High",
        fontsize=8.5, color=LOW_HI_COLOR, ha="right", va="top",
        transform=ax.transAxes)

ax.text(-0.055, 0.00, "Low",
        fontsize=8.5, color=LOW_HI_COLOR, ha="right", va="bottom",
        transform=ax.transAxes)
ax.text(-0.055, 1.00, "High",
        fontsize=8.5, color=LOW_HI_COLOR, ha="right", va="top",
        transform=ax.transAxes)

# ==============================================================================
# 11. SOURCE LINE
# ==============================================================================

fig.text(
    0.50, 0.035,
    "Model adapted from Csikszentmihalyi (1990)",
    fontsize=8, color=SOURCE_COLOR,
    ha="center", va="center", fontstyle="italic",
)

# ==============================================================================
# 12. SAVE
# ==============================================================================

script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_png = images_dir / "elden-ring-hedonic-reset_flow-channel.png"

fig.savefig(
    output_png,
    dpi=DPI_VAL,
    # Note: bbox_inches="tight" omitted intentionally.
    # The figure size (8×4.8 in @ 150 DPI) already gives exactly 1200×720 px.
    # Using bbox_inches="tight" crops the layout and undershoots the target.
    facecolor=BG_COLOR,
    edgecolor="none",
)
plt.close(fig)

# Verify
from PIL import Image
verify = Image.open(output_png)
actual_w, actual_h = verify.size

print(f"✓ Chart saved to {output_png}")
print(f"  Requested:  {int(W_INCH * DPI_VAL)} × {int(H_INCH * DPI_VAL)} px")
print(f"  Actual:     {actual_w} × {actual_h} px")
print(f"  Done.")
