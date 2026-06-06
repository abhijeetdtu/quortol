#!/usr/bin/env python3
"""
Budgerigar brain schematic — coronal section showing the "core and shell"
song system unique to parrots.

Each nucleus has an inner core (homologous to songbird/hummingbird song nuclei)
and an outer shell ring (parrot-specific expansion).

Nuclei shown:
  - AAC  : central nucleus of the anterior arcopallium (posterior pathway)
  - NLC  : central nucleus of the lateral nidopallium  (analogous to HVC)
  - MO   : oval nucleus of the mesopallium             (anterior pathway)
  - NAO  : oval nucleus of the anterior nidopallium    (anterior pathway)

Output: 1200×720 px PNG @ 150 DPI, colorblind-safe palette with hatching.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, PathPatch
from matplotlib.path import Path

# ── Output paths ──────────────────────────────────────────────────────────
CHART_PATH = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "the-accidental-genius_core_shell_brain.png"
)

# ── Figure setup ──────────────────────────────────────────────────────────
# Target: 1200×720 px @ 150 DPI → 8 × 4.8 inches
FIG_W, FIG_H = 8.0, 4.8
DPI = 150

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
fig.patch.set_facecolor("white")

# Data coordinate space — matches 8×4.8 inch aspect at 150 DPI
ax.set_xlim(-9, 9)
ax.set_ylim(-5.5, 6.5)
ax.set_aspect("equal")
ax.axis("off")

# ── Colorblind-safe palette (Color Universal Design) ─────────────────────
# Core = dark, saturated; Shell = lighter hue + hatch pattern
PALETTE = {
    "NLC": {"core": "#0072B2", "shell": "#92C5DE"},   # blue
    "AAC": {"core": "#D55E00", "shell": "#F4A582"},   # vermillion/orange
    "MO":  {"core": "#009E73", "shell": "#B2DF8A"},   # green
    "NAO": {"core": "#CC79A7", "shell": "#F1B6DA"},   # pink
}

HATCH = "///"  # hatch pattern for shell rings
BRAIN_FACE = "#F0F0F0"
BRAIN_EDGE = "#444444"
LABEL_FONT = {"family": "sans-serif", "weight": "bold", "size": 12}
NUCLEUS_FONT = {"family": "sans-serif", "weight": "bold", "size": 12}
DESCRIPTION_FONT = {"family": "sans-serif", "size": 8.5}
TITLE_FONT = {"family": "sans-serif", "weight": "bold", "size": 16}
SOURCE_FONT = {"family": "sans-serif", "size": 8, "style": "italic"}

# ── Draw brain outline (coronal section) ─────────────────────────────────
# Approximate a forebrain coronal view using two overlapping ellipses
# (mimicking left & right hemispheres) plus a brainstem hint.
left_hemi = Ellipse(
    xy=(-2.2, 0.5), width=7.8, height=10.5, angle=0,
    facecolor=BRAIN_FACE, edgecolor=BRAIN_EDGE, linewidth=2.0, zorder=1,
)
right_hemi = Ellipse(
    xy=(2.2, 0.5), width=7.8, height=10.5, angle=0,
    facecolor=BRAIN_FACE, edgecolor=BRAIN_EDGE, linewidth=2.0, zorder=1,
)
ax.add_patch(left_hemi)
ax.add_patch(right_hemi)

# Midline fissure — a thin vertical line to suggest the separation
ax.plot([0, 0], [4.8, -4.5], color=BRAIN_EDGE, linewidth=1.0,
        linestyle=":", alpha=0.4, zorder=2)

# Brainstem hint (bottom)
brainstem = FancyBboxPatch(
    (-1.2, -5.2), 2.4, 2.5,
    boxstyle="round,pad=0.3,rounding_size=0.4",
    facecolor=BRAIN_FACE, edgecolor=BRAIN_EDGE, linewidth=1.8, zorder=1,
)
ax.add_patch(brainstem)

# ── Helper: draw a core + shell nucleus ──────────────────────────────────
def draw_nucleus(ax, cx, cy, core_r, shell_r, name, colors):
    """Draw a concentric core-shell nucleus and label it."""
    # ── Shell ring (outer circle with hatch) ──
    shell = Circle(
        (cx, cy), radius=shell_r,
        facecolor=colors["shell"], edgecolor=colors["core"],
        linewidth=1.8, hatch=HATCH, zorder=3,
    )
    ax.add_patch(shell)

    # ── Core (solid inner circle) ──
    core = Circle(
        (cx, cy), radius=core_r,
        facecolor=colors["core"], edgecolor="white",
        linewidth=1.2, zorder=4,
    )
    ax.add_patch(core)

    # ── Label ──
    # Place the abbreviation above the shell, with a thin pointer line
    label_y = cy + shell_r + 0.65
    ax.annotate(
        name, xy=(cx, cy + shell_r * 0.75),
        xytext=(cx, label_y),
        fontfamily="sans-serif", fontweight="bold", fontsize=13,
        ha="center", va="bottom",
        arrowprops=dict(
            arrowstyle="-", color="#666666", linewidth=0.8,
        ),
        zorder=5,
    )

    # Return y-position for description text
    return cy - shell_r - 0.45


# ── Nucleus positions (data coords, stylised coronal layout) ─────────────
# NLC — dorsal / lateral left   (analogous to HVC)
# AAC — ventral / lateral left  (posterior pathway → brainstem)
# MO  — dorsal / medial right   (anterior forebrain pathway)
# NAO — mid / medial right       (anterior forebrain pathway)

nuclei = [
    {"name": "NLC", "cx": -3.8, "cy": 4.0,  "core_r": 0.55, "shell_r": 0.95},
    {"name": "AAC", "cx": -2.9, "cy": -1.5, "core_r": 0.50, "shell_r": 0.90},
    {"name": "MO",  "cx":  3.5, "cy": 3.2,  "core_r": 0.50, "shell_r": 0.90},
    {"name": "NAO", "cx":  3.4, "cy": 0.5,  "core_r": 0.50, "shell_r": 0.85},
]

descriptions = {
    "NLC": "lateral nidopallium · analogous to HVC",
    "AAC": "anterior arcopallium · projects to brainstem",
    "MO":  "oval nucleus of mesopallium · anterior pathway",
    "NAO": "oval nucleus of ant. nidopallium · anterior pathway",
}

for nuc in nuclei:
    desc_y = draw_nucleus(
        ax, nuc["cx"], nuc["cy"],
        nuc["core_r"], nuc["shell_r"],
        nuc["name"], PALETTE[nuc["name"]],
    )
    # Description text below each nucleus
    ax.text(
        nuc["cx"], desc_y - 0.35,
        descriptions[nuc["name"]],
        fontdict=DESCRIPTION_FONT,
        color="#555555",
        ha="center", va="top",
        zorder=5,
    )

# ── Legend (core vs shell) ───────────────────────────────────────────────
legend_x, legend_y = 7.5, 5.8

# Legend box
legend_box = FancyBboxPatch(
    (legend_x - 1.6, legend_y - 2.5),
    3.2, 2.8,
    boxstyle="round,pad=0.15,rounding_size=0.2",
    facecolor="#FAFAFA", edgecolor="#CCCCCC", linewidth=1.0, zorder=6,
)
ax.add_patch(legend_box)

ax.text(
    legend_x, legend_y - 0.25, "Legend",
    fontdict={"family": "sans-serif", "weight": "bold", "size": 11},
    ha="center", va="top", zorder=7,
)

# Core sample
core_legend = Circle(
    (legend_x - 0.6, legend_y - 1.1), radius=0.25,
    facecolor="#555555", edgecolor="none", zorder=7,
)
ax.add_patch(core_legend)
ax.text(
    legend_x + 0.15, legend_y - 1.1, "Core",
    fontdict={"family": "sans-serif", "size": 10},
    ha="left", va="center", zorder=7,
)

# Shell sample
shell_legend = Circle(
    (legend_x - 0.6, legend_y - 2.0), radius=0.30,
    facecolor="#BBBBBB", edgecolor="#555555",
    linewidth=1.2, hatch=HATCH, zorder=7,
)
ax.add_patch(shell_legend)
ax.text(
    legend_x + 0.15, legend_y - 2.0, "Shell",
    fontdict={"family": "sans-serif", "size": 10},
    ha="left", va="center", zorder=7,
)

# ── Pathway arrows (schematic connections) ───────────────────────────────
# Light grey dashed arrows to suggest posterior vs anterior pathways

# Posterior pathway: NLC → AAC (left side)
ax.annotate(
    "", xy=(-3.0, -0.8), xytext=(-3.6, 2.8),
    arrowprops=dict(
        arrowstyle="->", color="#999999", linewidth=1.5,
        linestyle="dashed", connectionstyle="arc3,rad=-0.3",
    ),
    zorder=2,
)
ax.text(
    -4.3, 1.0, "posterior\npathway",
    fontdict={"family": "sans-serif", "size": 8, "style": "italic"},
    color="#888888", ha="center", va="center", zorder=2,
)

# Anterior pathway: MO → NAO (right side)
ax.annotate(
    "", xy=(3.5, 1.2), xytext=(3.5, 2.5),
    arrowprops=dict(
        arrowstyle="->", color="#999999", linewidth=1.5,
        linestyle="dashed", connectionstyle="arc3,rad=0.3",
    ),
    zorder=2,
)
ax.text(
    4.8, 1.8, "anterior\npathway",
    fontdict={"family": "sans-serif", "size": 8, "style": "italic"},
    color="#888888", ha="center", va="center", zorder=2,
)

# ── Title ────────────────────────────────────────────────────────────────
ax.text(
    0, 6.2,
    "The Budgerigar's Core-and-Shell Song System",
    fontdict=TITLE_FONT,
    ha="center", va="top", zorder=10,
)
ax.text(
    0, 5.7,
    "Coronal section · forebrain song nuclei with parrot-specific shell domains",
    fontdict={"family": "sans-serif", "size": 11, "color": "#666666"},
    ha="center", va="top", zorder=10,
)

# ── Source line ──────────────────────────────────────────────────────────
ax.text(
    0, -5.3,
    "Based on: PLOS One 2015; Chakraborty et al.",
    fontdict=SOURCE_FONT,
    color="#888888",
    ha="center", va="top", zorder=10,
)

# ── Orientation labels ───────────────────────────────────────────────────
ax.text(-8.3, 0, "L", fontdict={"family": "sans-serif", "size": 10, "color": "#999999"},
        ha="center", va="center", zorder=1)
ax.text(8.3, 0, "R", fontdict={"family": "sans-serif", "size": 10, "color": "#999999"},
        ha="center", va="center", zorder=1)
ax.text(0, 6.3, "D", fontdict={"family": "sans-serif", "size": 10, "color": "#999999"},
        ha="center", va="center", zorder=1)
ax.text(0, -5.35, "V", fontdict={"family": "sans-serif", "size": 10, "color": "#999999"},
        ha="center", va="center", zorder=1)

# ── Save ─────────────────────────────────────────────────────────────────
# Save at exact target dimensions (1200×720 = 8×4.8 in @ 150 DPI)
fig.savefig(CHART_PATH, dpi=DPI, facecolor="white", edgecolor="none")
plt.close(fig)

print(f"Chart saved: {CHART_PATH}")
print("Done.")
