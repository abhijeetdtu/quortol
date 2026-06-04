"""
Chart 3: The Great Crossover — Manufacturing vs Tourism in Berkshire County
Dual-axis line chart showing the decline of manufacturing employment share (1957-2011)
and the rise of tourism visitor spending (2017-2024), with projected extensions
showing where the two lines cross.

matplotlib, 1200×720 px, 150 DPI, publication-quality styling.
Output: the-two-berkshires_mfg_vs_tourism.png
"""

import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Data ──────────────────────────────────────────────────────────────────────
# Manufacturing share of nonagricultural employment (%)
mfg_years = np.array([1957, 1977, 2011])
mfg_pct   = np.array([59.3, 39.5, 8.8])

# Tourism visitor spending ($ millions)
tour_years = np.array([2017, 2019, 2022, 2024])
tour_spend = np.array([517, 674, 862, 839])

# Colors (from spec)
MFG_COLOR   = "#B2182B"   # warm red
TOUR_COLOR  = "#4C72B0"   # warm blue
GRID_COLOR  = "#D8D8D8"
TEXT_COLOR  = "#333333"
MUTED_TEXT  = "#777777"
BG_COLOR    = "#FAFAFA"

# ── Figure setup (no constrained_layout — it conflicts with twinx()) ──────────
fig, ax_left = plt.subplots(figsize=(8, 4.8))
fig.patch.set_facecolor("white")

# Manual layout: give room for rotated labels, title, source
fig.subplots_adjust(left=0.095, right=0.87, top=0.82, bottom=0.18)

ax_right = ax_left.twinx()

# ── Projected / interpolated data for shading and dashed extensions ───────────
# Manufacturing: extrapolate forward from 1977–2011 slope
mfg_slope = (mfg_pct[-1] - mfg_pct[-2]) / (mfg_years[-1] - mfg_years[-2])  # % per year
mfg_ext_years = np.array([2011, 2017, 2019, 2022, 2024])
mfg_ext_pct = mfg_pct[-1] + mfg_slope * (mfg_ext_years - mfg_years[-1])
mfg_ext_pct = np.maximum(mfg_ext_pct, 0.5)  # floor at 0.5 %

# Tourism: extrapolate backward from 2017–2019 slope
tour_slope = (tour_spend[1] - tour_spend[0]) / (tour_years[1] - tour_years[0])  # $M per year
tour_ext_years = np.array([1957, 1977, 2011])
tour_ext_spend = tour_spend[0] + tour_slope * (tour_ext_years - tour_years[0])
tour_ext_spend = np.maximum(tour_ext_spend, 0)

# Dense grid for shading (from 1977 to 2024)
x_dense = np.linspace(1977, 2024, 1000)
all_mfg_x = np.concatenate([mfg_years, mfg_ext_years])
all_mfg_y = np.concatenate([mfg_pct, mfg_ext_pct])
sort_idx = np.argsort(all_mfg_x)
all_mfg_x = all_mfg_x[sort_idx]
all_mfg_y = all_mfg_y[sort_idx]

all_tour_x = np.concatenate([tour_ext_years, tour_years])
all_tour_y = np.concatenate([tour_ext_spend, tour_spend])
sort_idx = np.argsort(all_tour_x)
all_tour_x = all_tour_x[sort_idx]
all_tour_y = all_tour_y[sort_idx]

mfg_dense = np.interp(x_dense, all_mfg_x, all_mfg_y)
tour_dense = np.interp(x_dense, all_tour_x, all_tour_y)

# Normalize to 0–1 for comparison
mfg_norm = np.clip(mfg_dense / 70.0, 0, 1)
tour_norm = np.clip(tour_dense / 1000.0, 0, 1)

above = tour_norm > mfg_norm
cross_points = np.where(np.diff(above.astype(int)) != 0)[0]

if len(cross_points) > 0:
    cross_start_idx = cross_points[0] + 1
else:
    cross_start_idx = 0

# ── Solid data lines ───────────────────────────────────────────────────────────
ax_left.plot(
    mfg_years, mfg_pct,
    color=MFG_COLOR, linewidth=3.2, solid_capstyle="round", zorder=7,
    marker="o", markersize=9, markerfacecolor=MFG_COLOR,
    markeredgecolor="white", markeredgewidth=1.5,
)
ax_right.plot(
    tour_years, tour_spend,
    color=TOUR_COLOR, linewidth=3.2, solid_capstyle="round", zorder=7,
    marker="s", markersize=9, markerfacecolor=TOUR_COLOR,
    markeredgecolor="white", markeredgewidth=1.5,
)

# ── Dashed projection lines (thinner, lighter — clearly secondary) ────────────
ax_left.plot(
    mfg_ext_years, mfg_ext_pct,
    color=MFG_COLOR, linewidth=1.2, linestyle="--", dashes=(6, 4),
    solid_capstyle="round", zorder=6, alpha=0.5,
)
ax_right.plot(
    tour_ext_years, tour_ext_spend,
    color=TOUR_COLOR, linewidth=1.2, linestyle="--", dashes=(6, 4),
    solid_capstyle="round", zorder=6, alpha=0.5,
)

# ── Subtle shaded region between lines after crossover ────────────────────────
if cross_start_idx < len(x_dense):
    tour_in_mfg_axis = tour_norm * 70.0
    mfg_in_mfg_axis = mfg_dense
    ax_left.fill_between(
        x_dense[cross_start_idx:],
        mfg_in_mfg_axis[cross_start_idx:],
        tour_in_mfg_axis[cross_start_idx:],
        color=TOUR_COLOR, alpha=0.06, zorder=2,
    )

# ── Axes styling ──────────────────────────────────────────────────────────────
ax_left.set_ylabel(
    "Manufacturing Share of Employment (%)",
    fontsize=13, color=MFG_COLOR, fontweight="bold", labelpad=10,
)
ax_left.set_ylim(-2, 72)
ax_left.set_yticks([0, 10, 20, 30, 40, 50, 60, 70])
ax_left.tick_params(axis="y", colors=MFG_COLOR, labelsize=11)
ax_left.yaxis.set_tick_params(width=0)

ax_right.set_ylabel(
    "Visitor Spending ($ millions)",
    fontsize=13, color=TOUR_COLOR, fontweight="bold", labelpad=10,
)
ax_right.set_ylim(-30, 1050)
ax_right.set_yticks([0, 200, 400, 600, 800, 1000])
ax_right.tick_params(axis="y", colors=TOUR_COLOR, labelsize=11)
ax_right.yaxis.set_tick_params(width=0)

# X-axis — rotated 45° to prevent overlap
all_xticks = [1957, 1977, 2011, 2017, 2019, 2022, 2024]
ax_left.set_xticks(all_xticks)
ax_left.set_xticklabels(
    [str(y) for y in all_xticks],
    fontsize=10.5, color=TEXT_COLOR,
    rotation=45, ha="right",
)
ax_left.set_xlim(1950, 2032)
ax_left.xaxis.set_ticks_position("none")

# ── Spines ────────────────────────────────────────────────────────────────────
ax_left.spines["top"].set_visible(False)
ax_right.spines["top"].set_visible(False)

ax_left.spines["left"].set_color(MFG_COLOR)
ax_left.spines["left"].set_linewidth(1.2)
ax_left.spines["left"].set_position(("outward", 8))

ax_right.spines["right"].set_color(TOUR_COLOR)
ax_right.spines["right"].set_linewidth(1.2)
ax_right.spines["right"].set_position(("outward", 8))

ax_left.spines["bottom"].set_color("#CCCCCC")
ax_left.spines["bottom"].set_linewidth(0.8)
ax_left.spines["bottom"].set_position(("outward", 8))

# ── Grid ──────────────────────────────────────────────────────────────────────
ax_left.grid(axis="y", color=GRID_COLOR, linewidth=0.5, alpha=0.6)
ax_left.grid(axis="x", color=GRID_COLOR, linewidth=0.5, alpha=0.3)
ax_left.set_axisbelow(True)

# ── Title and subtitle ─────────────────────────────────────────────────────────
ax_left.text(
    0.5, 1.04, "The Great Crossover",
    transform=ax_left.transAxes,
    fontsize=22, fontweight="bold", ha="center", va="bottom",
    color=TEXT_COLOR, fontfamily="sans-serif",
)
ax_left.text(
    0.5, 0.995,
    "From a manufacturing economy to a tourism economy — Berkshire County, 1957–2024",
    transform=ax_left.transAxes,
    fontsize=12, color=MUTED_TEXT, ha="center", va="top",
    fontfamily="sans-serif", fontstyle="italic",
)

# ── Line labels (clean text-only, no arrows, inside plot area) ─────────────────
# Manufacturing label — placed near the first data point, inside axes
ax_left.text(
    1958, 60,
    "Manufacturing\nshare of employment",
    fontsize=10.5, color=MFG_COLOR, fontweight="bold",
    ha="left", va="bottom",
)

# Tourism label — placed near the last data point, inside axes
ax_right.text(
    2021.5, 820,
    "Visitor spending\n($ millions)",
    fontsize=10.5, color=TOUR_COLOR, fontweight="bold",
    ha="right", va="top",
)

# ── Crossover annotation (minimal — just a small text label, no vertical line) ─
if cross_start_idx < len(x_dense):
    cross_year = x_dense[cross_start_idx]
    ax_left.text(
        cross_year, 65,
        f"≈{int(round(cross_year))}",
        fontsize=10, color="#666666", ha="center", va="bottom",
        fontstyle="italic", alpha=0.7,
    )

# ── Source line ───────────────────────────────────────────────────────────────
ax_left.text(
    0, -0.12,
    "Sources: Mass. State Archives • Dean Runyan Associates (MOTT) • UMass Donahue Institute",
    transform=ax_left.transAxes,
    fontsize=8, color=MUTED_TEXT, ha="left", va="top",
    fontfamily="sans-serif",
)

# ── Background fill for the plot area ─────────────────────────────────────────
ax_left.patch.set_facecolor(BG_COLOR)
ax_right.patch.set_facecolor(BG_COLOR)

# ── Export ────────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-two-berkshires_mfg_vs_tourism.png"

fig.savefig(
    output_path,
    dpi=150,
    facecolor="white",
    edgecolor="none",
)
plt.close(fig)
print(f"Chart saved to: {output_path}")

# ── Verification ──────────────────────────────────────────────────────────────
if output_path.exists():
    size_kb = output_path.stat().st_size / 1024
    from PIL import Image
    img = Image.open(output_path)
    w, h = img.size
    print(f"Verified: {output_path.name} — {size_kb:.1f} KB, {w}×{h} px")
else:
    print("ERROR: File was not created!")
    raise SystemExit(1)
