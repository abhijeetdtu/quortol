#!/usr/bin/env python3
"""
Vertical bar chart: India's Food Processing Market Growth ($ Billion).

Data sourced from IBEF Food Processing Industry Report (Feb 2026) and
USDA FAS GAIN Report IN2026-0016 (March 2026).
"""

import io
import os
import textwrap

import matplotlib
matplotlib.use("Agg")  # no-display backend

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Configuration ──────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "images")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "indian-food-history-future_market_growth.png")

DPI = 150
WIDTH, HEIGHT = 1200, 720  # px

# ── Data ────────────────────────────────────────────────────────────────────
years = ["2020", "2021", "2022", "2023", "2024", "2026*"]
values = [290, 305, 320, 337, 355, 535]

# Colour palette (colourblind-safe blues)
# Base bars: soft-to-mid blue
BASE_COLOR = "#4A7FB5"
# Emphasis bars for 2024 and 2026 (from specific sources)
EMPH_COLOR = "#1B3A5C"

bar_colors = [EMPH_COLOR if y in ("2024", "2026*") else BASE_COLOR for y in years]

# ── Plot ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)

x = np.arange(len(years))

bars = ax.bar(x, values, color=bar_colors, width=0.55, zorder=3)

# ── Data labels on top of each bar ─────────────────────────────────────────
for i, (bar, val) in enumerate(zip(bars, values)):
    label_text = f"${val}B"
    # offset slightly above bar top
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 8,
        label_text,
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        color="#1B3A5C" if years[i] in ("2024", "2026*") else "#2C5F8A",
    )

# ── Axis labels & formatting ───────────────────────────────────────────────
ax.set_xlabel("Year", fontsize=13, labelpad=10)
ax.set_ylabel("US$ Billion", fontsize=13, labelpad=10)
ax.set_title(
    "India's Food Processing Market Growth ($ Billion)",
    fontsize=17,
    fontweight="bold",
    pad=18,
)

ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=12)

# Y-axis: start at 0, go to ~580 with reasonable ticks
ax.set_ylim(0, 600)
ax.yaxis.set_major_locator(mticker.MultipleLocator(50))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(25))
ax.tick_params(axis="y", labelsize=11)

# Grid lines (horizontal only, light)
ax.grid(axis="y", linestyle="--", alpha=0.25, zorder=0)
ax.set_axisbelow(True)

# Remove top/right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#CCCCCC")
ax.spines["bottom"].set_color("#CCCCCC")

# ── Note below 2026* label ─────────────────────────────────────────────────
# Place small text under the last tick label
ax.text(
    x[-1],
    -34,
    "*Projected",
    ha="center",
    va="top",
    fontsize=9,
    fontstyle="italic",
    color="#666666",
)

# ── Source line at bottom ───────────────────────────────────────────────────
source_text = (
    "Sources: IBEF Food Processing Report (Feb 2026); USDA FAS GAIN Report"
)
ax.text(
    0.5,
    -0.13,
    source_text,
    transform=fig.transFigure,
    ha="center",
    va="top",
    fontsize=8,
    color="#888888",
    fontstyle="italic",
)

# ── Tight layout & save ────────────────────────────────────────────────────
fig.tight_layout(rect=[0, 0.04, 1, 1])  # leave room for source line

os.makedirs(OUTPUT_DIR, exist_ok=True)
fig.savefig(OUTPUT_FILE, dpi=DPI, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"✓ Chart saved → {OUTPUT_FILE}")
