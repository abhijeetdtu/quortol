#!/usr/bin/env python3
"""
Horizontal lollipop timeline: "The Human-Fungal Relationship: A Timeline"
Key milestones in the human-fungi relationship from 18700 BCE to 2026 CE.

Output: PNG at 1200×960 px, 150 DPI.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
# (year, label, category)
# BCE years are stored as negative numbers.
RAW_DATA = [
    (-18700, "Earliest mushroom consumption (El Mirón Cave)", "Consumption"),
    (-8000,  "Saharan rock art: psychoactive mushrooms",       "Ritual"),
    (-6000,  "Maya mushroom stones",                          "Ritual"),
    (-5300,  "Ötzi carries medicinal fungi",                   "Medicine"),
    (-4000,  "Selva Pascuala: Psilocybe mural",                "Ritual"),
    (-1550,  "Hearst Papyrus: moldy bread poultices",         "Medicine"),
    (-200,   "Lingzhi in Shennong Bencao Jing",               "Medicine"),
    (600,    "First cultivated mushroom (Auricularia)",        "Food"),
    (1680,   "Leeuwenhoek observes yeast",                     "Science"),
    (1928,   "Fleming discovers penicillin",                   "Medicine"),
    (1970,   "Cyclosporine discovered",                        "Medicine"),
    (2007,   "Ecovative: mycelium packaging",                  "Materials"),
    (2026,   "FDA accelerates psilocybin therapies",           "Medicine"),
]

# Sort chronologically (earliest at top of chart)
RAW_DATA.sort(key=lambda x: x[0])

years  = [d[0] for d in RAW_DATA]
labels = [d[1] for d in RAW_DATA]
cats   = [d[2] for d in RAW_DATA]

# ---------------------------------------------------------------------------
# Colorblind-safe palette
# ---------------------------------------------------------------------------
COLORS = {
    "Consumption": "#1f77b4",   # blue
    "Ritual":      "#9467bd",   # purple
    "Medicine":    "#2ca02c",   # green
    "Food":        "#ff7f0e",   # orange
    "Science":     "#17becf",   # teal
    "Materials":   "#8c564b",   # brown
}

# ---------------------------------------------------------------------------
# BCE / CE helpers
# ---------------------------------------------------------------------------
def fmt_year(num):
    """Return a string like '18700 BCE' or '600 CE'."""
    if num < 0:
        return f"{abs(num)} BCE"
    return f"{num} CE"

# Y-axis tick labels: "18700 BCE — Earliest mushroom consumption …"
ytick_labels = [f"{fmt_year(y)} — {lbl}" for y, lbl in zip(years, labels)]

# ---------------------------------------------------------------------------
# Build figure
# ---------------------------------------------------------------------------
WIDTH_IN  = 1200 / 150   # 8 in
HEIGHT_IN = 960  / 150   # 6.4 in
DPI        = 150

plt.style.use("seaborn-v0_8-whitegrid")

fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI)
fig.patch.set_facecolor("white")

y_pos = np.arange(len(RAW_DATA))  # 0 … N-1 from top to bottom
XMIN  = -19000
XMAX  = 2030

# ---------------------------------------------------------------------------
# Draw lollipops
# ---------------------------------------------------------------------------
for i, (yr, cat) in enumerate(zip(years, cats)):
    c = COLORS[cat]
    # Stem — uniform light gray to reduce visual noise
    ax.plot([XMIN, yr], [i, i], color="#cccccc", linewidth=2.2,
            solid_capstyle="round", zorder=2)
    # Dot (head) — colored by category
    ax.plot(yr, i, "o", color=c, markersize=10, markeredgecolor="white",
            markeredgewidth=0.5, zorder=3)

# ---------------------------------------------------------------------------
# Axes
# ---------------------------------------------------------------------------
ax.set_yticks(y_pos)
ax.set_yticklabels(ytick_labels, fontsize=8.5)
ax.set_ylim(-1.0, len(RAW_DATA) - 0.3)
ax.invert_yaxis()  # earliest event at top

# X-axis limits and ticks
ax.set_xlim(XMIN, XMAX)
ax.set_xlabel("Year", fontsize=9)

# Format x-axis ticks as BCE/CE
def x_fmt(val, _pos):
    if val < 0:
        return f"{abs(int(val))} BCE"
    elif val == 0:
        return "1 BCE / 1 CE"
    return f"{int(val)} CE"

ax.xaxis.set_major_formatter(ticker.FuncFormatter(x_fmt))
ax.tick_params(axis="x", labelsize=8)
# Rotate x labels for readability
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

# ---------------------------------------------------------------------------
# Title & subtitle
# ---------------------------------------------------------------------------
ax.set_title(
    "The Human-Fungal Relationship: A Timeline",
    fontsize=14, fontweight="bold", pad=12
)

# ---- Source line (at bottom, outside data area) ----
source_text = (
    "Sources: PLOS One, Nature, Cambridge Mycological Research, "
    "FDA, peer-reviewed literature"
)
fig.text(
    0.5, -0.02, source_text, ha="center", va="top",
    fontsize=6.5, fontstyle="italic", color="gray"
)

# ---------------------------------------------------------------------------
# Legend
# ---------------------------------------------------------------------------
legend_handles = [
    plt.Line2D([], [], color=COLORS[cat], marker="o", linestyle="-",
               linewidth=2, markersize=7, label=cat)
    for cat in ["Consumption", "Ritual", "Medicine", "Food", "Science", "Materials"]
]
ax.legend(
    handles=legend_handles,
    title="Category",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.10),
    ncol=6,
    fontsize=7.5,
    title_fontsize=8,
    framealpha=0.9,
    edgecolor="lightgray",
)

# ---------------------------------------------------------------------------
# Layout & save
# ---------------------------------------------------------------------------
plt.subplots_adjust(left=0.25)
plt.tight_layout(rect=[0, 0.06, 1, 0.93])

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

out_path = output_dir / "human-fungi-relationship_timeline.png"
fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"✓ Chart saved to: {out_path}")
print(f"  Dimensions: 1200×960 px @ {DPI} DPI")
