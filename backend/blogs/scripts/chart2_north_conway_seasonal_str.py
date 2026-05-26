"""
Chart: Seasonal Short-Term Rental Performance — North Conway, NH
Dual-axis bar (occupancy) + line (ADR) chart
Data source: StaySTRA North Conway Market Report 2024–2025
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# ── Data ──────────────────────────────────────────────────────────────────
months = [
    "Jul '24", "Aug '24", "Sep '24", "Oct '24", "Nov '24", "Dec '24",
    "Jan '25", "Feb '25", "Mar '25", "Apr '25", "May '25", "Jun '25",
]
occupancy = [70.0, 80.7, 36.5, 46.7, 30.0, 38.7, 38.7, 56.0, 25.8, 25.9, 25.8, 40.0]
adr = [357, 362, 342, 361, 351, 362, 378, 392, 373, 315, 323, 334]
revenue = [6082, 6818, 2717, 4307, 2675, 3679, 3944, 5051, 2940, 2001, 2203, 3252]

N = len(months)
x = np.arange(N)
bar_width = 0.55

# ── Style ─────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 15,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.edgecolor": "#555555",
    "grid.color": "#d5d5d5",
    "grid.alpha": 0.6,
    "axes.facecolor": "#fafafa",
    "figure.facecolor": "white",
})

# ── Figure ────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

# Bar: Occupancy (left axis)
bars = ax1.bar(
    x,
    occupancy,
    width=bar_width,
    color="#3498DB",
    edgecolor="white",
    linewidth=0.6,
    zorder=3,
    label="Occupancy",
)

ax1.set_ylabel("Occupancy Rate (%)", fontsize=12, color="#2c3e50")
ax1.set_ylim(0, 90)
ax1.yaxis.set_major_locator(mticker.MultipleLocator(10))
ax1.tick_params(axis="y", colors="#2c3e50")

# Data labels on bars
for bar_obj, val in zip(bars, occupancy):
    ax1.text(
        bar_obj.get_x() + bar_obj.get_width() / 2,
        bar_obj.get_height() + 1.2,
        f"{val:.1f}%",
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold",
        color="#2c3e50",
    )

# Line: ADR (right axis)
ax2 = ax1.twinx()
(line,) = ax2.plot(
    x,
    adr,
    color="#E74C3C",
    linewidth=2.5,
    marker="o",
    markersize=7,
    markeredgecolor="white",
    markeredgewidth=1.2,
    zorder=4,
    label="ADR",
)
ax2.set_ylabel("Average Daily Rate (USD)", fontsize=12, color="#2c3e50")
ax2.set_ylim(0, 450)
ax2.yaxis.set_major_locator(mticker.MultipleLocator(50))
ax2.tick_params(axis="y", colors="#2c3e50")

# ── X-axis ticks ──────────────────────────────────────────────────────────
ax1.set_xticks(x)
ax1.set_xticklabels(months, rotation=30, ha="right", fontsize=9)
ax1.set_xlim(-0.6, N - 1 + 0.6)

# ── Title / subtitle ──────────────────────────────────────────────────────
fig.suptitle(
    "Seasonal Short-Term Rental Performance — North Conway, NH",
    fontsize=16,
    fontweight="bold",
    y=0.97,
    color="#1a1a1a",
)
ax1.set_title(
    "Monthly occupancy rate and average daily rate  |  Source: StaySTRA 2024–2025",
    fontsize=10,
    fontweight="normal",
    pad=8,
    color="#555555",
    loc="left",
)

# ── Legend (merged) ───────────────────────────────────────────────────────
bars_line = plt.Rectangle((0, 0), 1, 1, facecolor="#3498DB", edgecolor="white")
lines_line = plt.Line2D((0, 1), (0, 0), color="#E74C3C", linewidth=2.5, marker="o",
                        markerfacecolor="#E74C3C", markeredgecolor="white", markeredgewidth=1.2)
leg = fig.legend(
    [bars_line, lines_line],
    ["Occupancy (%)", "ADR (USD)"],
    loc="upper right",
    bbox_to_anchor=(0.93, 0.93),
    frameon=True,
    edgecolor="#cccccc",
    fontsize=10,
)

# ── Source line ───────────────────────────────────────────────────────────
fig.text(
    0.5, 0.01,
    "Data: StaySTRA North Conway Market Report 2024–2025",
    ha="center", va="bottom",
    fontsize=9,
    color="#888888",
    style="italic",
)

# ── Layout ────────────────────────────────────────────────────────────────
fig.tight_layout(rect=[0, 0.035, 1, 0.93])

# ── Save ──────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "north_conway_seasonal_str.png"

fig.savefig(
    output_path,
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
    edgecolor="none",
)
plt.close(fig)

print(f"Chart saved → {output_path.resolve()}")
print(f"Dimensions: 1200 × 720 px @ 150 DPI")
