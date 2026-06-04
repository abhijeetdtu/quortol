#!/usr/bin/env python3
"""
chart3_the-citation-economy_ctr_collapse.py

Line chart: Organic CTR when Google AI Overviews are present.
Monthly data from Seer Interactive (5.47M queries, 53 brands).

Exact study data points: Jan 2025, Jun 2025, Dec 2025, Feb 2026.
Intermediate months interpolated for visual clarity.

Output: 1200×720 px PNG at 150 DPI
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime

# ── Data ──────────────────────────────────────────────────────────────────────
# Months as datetime objects
months = pd.date_range(start="2025-01-01", periods=14, freq="MS")  # Jan 2025 – Feb 2026

ctr_values = [
    3.19,   # Jan 2025  — baseline (exact)
    3.00,   # Feb 2025  — interpolated
    2.80,   # Mar 2025  — interpolated
    2.60,   # Apr 2025  — interpolated
    2.40,   # May 2025  — interpolated (AI Overviews expanded)
    2.10,   # Jun 2025  — (exact)
    1.90,   # Jul 2025  — interpolated
    1.70,   # Aug 2025  — interpolated
    1.55,   # Sep 2025  — interpolated
    1.45,   # Oct 2025  — interpolated
    1.38,   # Nov 2025  — interpolated
    1.31,   # Dec 2025  — floor (exact)
    1.80,   # Jan 2026  — partial recovery (interpolated)
    2.36,   # Feb 2026  — (exact)
]

df = pd.DataFrame({"month": months, "ctr": ctr_values})

# ── Colour palette ────────────────────────────────────────────────────────────
LINE_COLOR      = "#C0392B"   # deep red
FILL_COLOR      = "#FADBD8"   # light pink/red for area fill
GRID_COLOR      = "#E5E5E5"
TEXT_COLOR      = "#2C3E50"
SOURCE_COLOR    = "#888888"
ANNOTATION_ARROW = "#8B0000"  # dark red
VLINECOL_REF    = "#E67E22"   # orange for reference line

# ── Build chart ───────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4.8))  # 1200×720 px at 150 DPI

# 1. Shaded area beneath the line
ax.fill_between(df["month"], df["ctr"], 0,
                color=FILL_COLOR, alpha=0.9, zorder=1)

# 2. Main line
ax.plot(df["month"], df["ctr"],
        color=LINE_COLOR, linewidth=2.75, solid_capstyle="round", zorder=3)

# 3. Dots at exact data points
exact_mask = [True, False, False, False, True, False, False,
              False, False, False, False, True, False, True]
exact_df = df[exact_mask]
ax.scatter(exact_df["month"], exact_df["ctr"],
           color=LINE_COLOR, s=60, zorder=4, edgecolors="white", linewidth=0.8)

# ── Annotations ───────────────────────────────────────────────────────────────

# Annotation: Baseline at Jan 2025
jan_point = df.iloc[0]
ax.annotate(
    "Baseline: 3.19%",
    xy=(jan_point["month"], jan_point["ctr"]),
    xytext=(pd.Timestamp("2025-02-15"), 3.65),
    fontsize=11, fontweight="bold", color=TEXT_COLOR,
    arrowprops=dict(arrowstyle="->", color=ANNOTATION_ARROW, lw=1.5),
    verticalalignment="center",
)

# Annotation: Floor at Dec 2025
dec_point = df.iloc[11]
ax.annotate(
    "Floor: 1.31%",
    xy=(dec_point["month"], dec_point["ctr"]),
    xytext=(pd.Timestamp("2025-10-01"), 0.55),
    fontsize=11, fontweight="bold", color=TEXT_COLOR,
    arrowprops=dict(arrowstyle="->", color=ANNOTATION_ARROW, lw=1.5),
    verticalalignment="center",
)

# Vertical reference line at May 2025
may_date = pd.Timestamp("2025-05-01")
ax.axvline(x=may_date, color=VLINECOL_REF, linewidth=1.2, linestyle="--", zorder=2)
ax.text(may_date, 4.08, "AI Overviews expansion",
        fontsize=9.5, color=VLINECOL_REF, fontstyle="italic",
        ha="center", va="bottom",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                  edgecolor=VLINECOL_REF, alpha=0.85))

# ── Axis limits ───────────────────────────────────────────────────────────────
ax.set_ylim(0, 4.2)
ax.set_xlim(pd.Timestamp("2024-12-15"), pd.Timestamp("2026-03-01"))

# ── Tick formatting ───────────────────────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 3, 5, 7, 9, 11]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
ax.set_xticks([pd.Timestamp(f"2025-{m:02d}-01") for m in [1, 3, 5, 7, 9, 11]] +
              [pd.Timestamp("2026-01-01")])

ax.set_yticks([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}%"))

# ── Labels & titles ──────────────────────────────────────────────────────────
ax.set_title("Organic CTR When Google AI Overviews Are Present",
             fontsize=19, fontweight="bold", color=TEXT_COLOR, pad=16)
ax.set_ylabel("Click-through rate (%)", fontsize=13, color=TEXT_COLOR)
ax.set_xlabel("")

# Subtitle via fig.suptitle at a lower position
fig.text(0.5, 0.92,
         "Monthly click-through rate, Jan 2025 – Feb 2026  |  Source: Seer Interactive",
         fontsize=9.5, color=SOURCE_COLOR, ha="center", fontstyle="italic")

# ── Grid & spines ─────────────────────────────────────────────────────────────
ax.grid(axis="y", color=GRID_COLOR, linewidth=0.6, zorder=0)
ax.grid(axis="x", color=GRID_COLOR, linewidth=0.4, zorder=0)
ax.set_axisbelow(True)

# Remove top/right spines
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color(GRID_COLOR)
ax.spines["bottom"].set_color(GRID_COLOR)

# ── Tick style ────────────────────────────────────────────────────────────────
ax.tick_params(axis="x", colors=TEXT_COLOR, labelsize=11)
ax.tick_params(axis="y", colors=TEXT_COLOR, labelsize=11)

# ── Tight layout ──────────────────────────────────────────────────────────────
fig.tight_layout(rect=[0, 0, 1, 0.92])

# ── Save ──────────────────────────────────────────────────────────────────────
output_path = "/home/pi/Documents/code/quortol/backend/blogs/images/the-citation-economy_ctr_collapse.png"

fig.savefig(
    output_path,
    dpi=150,
    facecolor="white",
    edgecolor="none",
)

plt.close(fig)
print(f"✅ Chart saved → {output_path}")
