#!/usr/bin/env python3
"""
Ocean Depth Zones — Clean Matplotlib Profile
=============================================
Minimalist depth profile: ocean zone bands on the left, deepest-point markers on
the right. No features, no stat box, no extra decoration.
Uses matplotlib for fine-grained control over layout and overlap.

Output: 1200 × 720 px PNG at 150 DPI
"""

import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# PATHS
# ============================================================
OUTPUT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
OUTPUT_FILE = OUTPUT_DIR / "ocean_depth_zones.png"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1200 × 720 px @ 150 DPI  →  w = 1200 / 150 = 8 in,  h = 720 / 150 = 4.8 in
W, H, DPI = 8, 4.8, 150

# ============================================================
# DATA — Ocean Zones  (depth in metres; negative = below sea level)
# ============================================================
# (label, top_depth, bottom_depth, hex_color)
ZONES = [
    ("Sunlight\n(Epipelagic)",   0,     -200,   "#CAE0F0"),
    ("Twilight\n(Mesopelagic)",  -200,  -1000,  "#8BB8D6"),
    ("Midnight\n(Bathypelagic)", -1000, -4000,  "#4A7FB5"),
    ("Abyssal",                  -4000, -6000,  "#1B4F8A"),
    ("Hadal",                    -6000, -11000, "#0A2342"),
]

# ============================================================
# DATA — Deepest Points by Ocean
# ============================================================
# (trench_name, depth_m)
DEEPEST = [
    ("Mariana Trench",      -10935),
    ("Puerto Rico Trench",  -8376),
    ("South Sandwich Trench", -7434),
    ("Java Trench",         -7192),
    ("Molloy Deep",         -5551),
]

# ============================================================
# BUILD PLOT
# ============================================================
fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
fig.patch.set_facecolor("white")

# ---------- axes limits ----------
ax.set_xlim(-0.10, 1.35)
ax.set_ylim(-11500, 1500)

# ---------- layout constants (data coordinates) ----------
ZONE_L, ZONE_R = 0.0, 0.50         # horizontal extent of zone rectangles
ZONE_CX = (ZONE_L + ZONE_R) / 2     # centre for zone-name text
MARKER_X = 0.72                     # x-position of deepest-point triangles
LABEL_X = 0.77                      # x-position of deepest-point text

# ---------- ocean zone rectangles ----------
for label, top, bottom, color in ZONES:
    rect = plt.Rectangle(
        (ZONE_L, bottom),
        ZONE_R - ZONE_L,
        top - bottom,
        facecolor=color,
        edgecolor="#2A2A2A",
        linewidth=0.4,
        zorder=2,
    )
    ax.add_patch(rect)

# ---------- zone name labels ----------
for label, top, bottom, color in ZONES:
    y_mid = (top + bottom) / 2
    # Light backgrounds  →  dark text; dark backgrounds  →  white text
    text_color = "#1A1A2E" if color in ("#CAE0F0", "#8BB8D6") else "#FFFFFF"
    ax.text(
        ZONE_CX, y_mid, label,
        ha="center", va="center",
        fontsize=9, fontweight="bold", color=text_color,
        zorder=4,
    )

# ---------- zone boundary lines (light dotted) ----------
for boundary in (-200, -1000, -4000, -6000):
    ax.axhline(y=boundary, color="#BBBBBB", linestyle=":", linewidth=0.4, zorder=1)

# ---------- sea-level reference line ----------
ax.axhline(y=0, color="#777777", linestyle="--", linewidth=0.6, zorder=1)

# ---------- deepest-point markers & labels ----------
for trench, depth in DEEPEST:
    # filled triangle pointing down
    ax.plot(
        MARKER_X, depth,
        marker="v", color="#D55E00", markersize=6,
        clip_on=False, zorder=3,
    )
    # trench name + formatted depth
    label_text = f"{trench} ({abs(depth):,} m)"
    ax.text(
        LABEL_X, depth, label_text,
        ha="left", va="center",
        fontsize=7, color="#D55E00", fontweight="bold",
        zorder=4,
    )

# ---------- left y-axis ----------
ax.set_ylabel("Depth (m)", fontsize=9, labelpad=8)
ax.set_yticks([0, -200, -1000, -4000, -6000, -11000])
ax.set_yticklabels(["0", "200", "1,000", "4,000", "6,000", "11,000"])
ax.tick_params(axis="y", labelsize=7.5, pad=4)

# ---------- right y-axis (subtle depth reference) ----------
secax = ax.secondary_yaxis("right")
secax.set_yticks([0, -200, -1000, -4000, -6000, -11000])
secax.set_yticklabels(["0", "200", "1,000", "4,000", "6,000", "11,000"])
secax.tick_params(
    axis="y", labelsize=5.5, colors="#AAAAAA",
    pad=2, length=3, width=0.3,
)
# Make the secondary spine very faint
secax.spines["right"].set_color("#DDDDDD")
secax.spines["right"].set_linewidth(0.3)

# ---------- hide top x-axis / show only left spine ----------
ax.xaxis.set_visible(False)
for spine_name in ("top", "right", "bottom"):
    ax.spines[spine_name].set_visible(False)
ax.spines["left"].set_color("#CCCCCC")
ax.spines["left"].set_linewidth(0.5)

# ---------- title ----------
ax.set_title(
    "The Vertical Ocean: Depth Zones and the Deepest Points",
    fontsize=14, fontweight="bold", pad=14, loc="center",
)

# ---------- source note ----------
fig.text(
    0.5, 0.01,
    "Sources: NOAA Ocean Exploration; Five Deeps Expedition (fivedeeps.com); "
    "WHOI Hadal Zone",
    ha="center", fontsize=6.5, color="#999999",
)

# ---------- margins ----------
fig.subplots_adjust(left=0.10, right=0.88, top=0.92, bottom=0.06)

# ============================================================
# SAVE
# ============================================================
fig.savefig(OUTPUT_FILE, dpi=DPI, facecolor="white")
plt.close(fig)
print(f"✓ Chart saved  →  {OUTPUT_FILE}")
print(f"  Dimensions   →  {int(W * DPI)} × {int(H * DPI)} px @ {DPI} DPI")
