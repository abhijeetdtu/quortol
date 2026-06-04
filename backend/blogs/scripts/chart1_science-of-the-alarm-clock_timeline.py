#!/usr/bin/env python3
"""
Chart: 2,400 Years of Alarm Clock Innovation — Timeline
Output: ../images/science-of-the-alarm-clock_timeline.png  (1200 × 720 px, 150 DPI)

Lollipop-style timeline of 18 milestones from Plato's hydraulic alarm clock
(427 BCE) to wearable sleep tracking guidelines (2025 CE), coloured by
technology category. BCE years are plotted as negative values on a
linear x-axis spanning -500 to 2030.

Sources: Kotsanas Museum, Vitruvius, Concord Monitor, Bibnum PSL,
         ClockHistory.com, Nobel Foundation, RAND Corporation, Oura,
         PMLR, World Sleep Society
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# =============================================================================
# 1. DATA  (year, label, category)
#    BCE years stored as negative integers (astronomical year numbering).
# =============================================================================
events = [
    (-427, "Plato invents hydraulic\nalarm clock (whistling water clock)", "Ancient"),
    (-270, "Ctesibius develops feedback-\ncontrolled water clock at Alexandria", "Ancient"),
    (1787, "Levi Hutchins builds first\nAmerican alarm clock (fixed 4 a.m.)", "Mechanical"),
    (1847, "Antoine Redier patents first\nadjustable mechanical alarm clock", "Mechanical"),
    (1876, "Seth Thomas mass-produces\nbedside alarm clock", "Mechanical"),
    (1900, "Wind-up alarm clocks become\nwidely affordable", "Mechanical"),
    (1931, "Westclox Chime Alarm:\n\"First he whispers, then he shouts\"", "Electric"),
    (1946, "Telechron Musalarm 8H59 —\nfirst clock radio", "Electric"),
    (1949, "Westclox Moonbeam —\nflashing light alarm", "Electric"),
    (1956, "GE-Telechron Snooz-Alarm —\nfirst snooze button", "Electric"),
    (1971, "Konopka & Benzer discover\nperiod gene in fruit flies", "Circadian Science"),
    (1984, "Hall, Rosbash & Young\nclone the period gene", "Circadian Science"),
    (1994, "Young discovers timeless\ngene (TIM protein)", "Circadian Science"),
    (2017, "Nobel Prize in Medicine\nfor circadian mechanism", "Circadian Science"),
    (2016, "RAND: $411B annual cost\nof sleep deprivation", "Economics"),
    (2024, "Oura Ring Gen3 validated vs\npolysomnography (94.4% sensitivity)", "Smart Alarm"),
    (2025.15, "WatchSleepNet open-source deep\nlearning sleep staging (PMLR)", "Smart Alarm"),  # slight x-jitter
    (2024.85, "World Sleep Society issues\nwearable sleep tracker guidelines", "Smart Alarm"),  # slight x-jitter
]

# Sort by year
events.sort(key=lambda x: x[0])
years = [e[0] for e in events]
labels = [e[1] for e in events]
categories = [e[2] for e in events]
n = len(events)  # 18

# Category → colour mapping (colorblind-safe palette)
CAT_COLORS = {
    "Ancient":          "#8B7355",   # olive
    "Mechanical":       "#D2691E",   # chocolate / orange-brown
    "Electric":         "#4682B4",   # steel blue
    "Circadian Science": "#6A0DAD",  # royal purple
    "Economics":        "#DC143C",   # crimson
    "Smart Alarm":      "#2E8B57",   # sea green
}

# Marker styling per category
CAT_MARKER = {
    "Ancient":          "s",    # square
    "Mechanical":       "o",    # circle
    "Electric":         "^",    # triangle up
    "Circadian Science": "D",   # diamond
    "Economics":        "v",    # triangle down
    "Smart Alarm":      "*",    # star
}

# =============================================================================
# 2. STYLE
# =============================================================================
plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         10,
    "axes.titlesize":    16,
    "axes.labelsize":    12,
    "xtick.labelsize":   10,
    "ytick.labelsize":   0,        # y-tick labels hidden
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.spines.bottom": True,
    "axes.edgecolor":    "#444444",
    "grid.color":        "#cccccc",
    "grid.alpha":        0.45,
    "axes.facecolor":    "#fafafa",
    "figure.facecolor":  "white",
})

# =============================================================================
# 3. FIGURE
# =============================================================================
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

# ── Y positions: evenly spaced, slightly padded from edges ────────────────
y_base = np.linspace(0.8, n - 0.8, n)   # 0.8 … 17.2

# ── Timeline baseline ─────────────────────────────────────────────────────
ax.axhline(y=0, color="#444444", linewidth=1.8, zorder=1)

# ── Plot each event ───────────────────────────────────────────────────────
for i in range(n):
    yr  = years[i]
    lbl = labels[i]
    cat = categories[i]
    y   = y_base[i]
    clr = CAT_COLORS[cat]
    mkr = CAT_MARKER[cat]

    # Vertical stem (dashed for Ancient, solid otherwise)
    ls = "dashed" if cat == "Ancient" else "solid"
    ax.plot(
        [yr, yr], [0, y],
        color=clr, linewidth=1.0, alpha=0.45,
        linestyle=ls, zorder=2,
    )

    # Marker
    ax.scatter(
        [yr], [y],
        color=clr, marker=mkr, s=80,
        edgecolors="white", linewidth=0.6,
        zorder=5, clip_on=False,
    )

    # Label: alternate above / below to prevent overlap
    va     = "bottom" if i % 2 == 0 else "top"
    y_offs = 10 if i % 2 == 0 else -10

    ax.annotate(
        lbl,
        xy=(yr, y),
        xytext=(0, y_offs),
        textcoords="offset points",
        ha="center",
        va=va,
        fontsize=9.5,
        color="#222222",
        linespacing=1.5,
        zorder=6,
    )

# =============================================================================
# 4. AXES
# =============================================================================
ax.set_xlim(-560, 2060)
ax.set_ylim(-1.2, n + 0.5)

# ── X-axis ticks (BCE / CE labels) ────────────────────────────────────────
# Astronomical year < 0 → BCE label (take absolute value)
def year_label(y):
    if y < 0:
        return f"{abs(y)} BCE"
    elif y == 0:
        return "1 BCE"            # astronomical year 0 = 1 BCE
    else:
        return f"{y} CE"

major_ticks = [-500, 0, 500, 1000, 1500, 2000]
ax.set_xticks(major_ticks)
ax.set_xticklabels([year_label(t) for t in major_ticks])

# Minor ticks every 100 years
ax.set_xticks(np.arange(-500, 2001, 100), minor=True)

# ── Grid ───────────────────────────────────────────────────────────────────
ax.grid(which="major", axis="x", linewidth=0.7)
ax.grid(which="minor", axis="x", linewidth=0.3, alpha=0.3)

# ── No y-axis (ordinal positioning only) ───────────────────────────────────
ax.yaxis.set_visible(False)

# ── Bottom spine as baseline ───────────────────────────────────────────────
ax.spines["bottom"].set_position(("data", 0))
ax.spines["bottom"].set_linewidth(1.8)

# =============================================================================
# 5. TITLE  (main + subtitle)
# =============================================================================
fig.suptitle(
    "2,400 Years of Alarm Clock Innovation",
    fontsize=18,
    fontweight="bold",
    y=0.96,
    color="#1a1a1a",
)

ax.set_title(
    "From Plato\u2019s water clock (427 BCE) to AI-powered sleep staging (2025 CE)\n"
    "18 milestones across six technology eras",
    fontsize=11,
    fontweight="normal",
    pad=10,
    color="#555555",
    loc="left",
)

# =============================================================================
# 6. LEGEND
# =============================================================================
handles = []
for cat in ["Ancient", "Mechanical", "Electric", "Circadian Science", "Economics", "Smart Alarm"]:
    h = plt.Line2D(
        [], [],
        color=CAT_COLORS[cat],
        marker=CAT_MARKER[cat],
        linestyle="None",
        markersize=9,
        label=cat,
    )
    handles.append(h)

legend = ax.legend(
    handles=handles,
    loc="upper left",
    fontsize=9.5,
    framealpha=0.90,
    edgecolor="#bbbbbb",
    facecolor="white",
    ncol=3,                     # 3 × 2 grid
    columnspacing=1.5,
    handletextpad=0.6,
)

# =============================================================================
# 7. SOURCE LINE
# =============================================================================
fig.text(
    0.5, 0.005,
    "Sources: Kotsanas Museum, Vitruvius, Concord Monitor, Bibnum PSL, "
    "ClockHistory.com, Nobel Foundation, RAND Corporation, Oura, PMLR, "
    "World Sleep Society",
    ha="center",
    va="bottom",
    fontsize=7.5,
    color="#888888",
    style="italic",
)

# =============================================================================
# 8. LAYOUT & SAVE
# =============================================================================
fig.tight_layout(rect=[0.02, 0.04, 0.98, 0.92])

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "science-of-the-alarm-clock_timeline.png"

fig.savefig(
    output_path,
    dpi=150,
    facecolor="white",
    edgecolor="none",
)
plt.close(fig)

print(f"\u2713 Chart saved \u2192 {output_path.resolve()}")
print(f"  Dimensions: 1200 \u00d7 720 px  @  150 DPI")
print(f"  Events plotted: {n}")
