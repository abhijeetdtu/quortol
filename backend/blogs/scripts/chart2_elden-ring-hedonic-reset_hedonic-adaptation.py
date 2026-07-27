#!/usr/bin/env python3
"""
Chart: Hedonic Adaptation — The Elden Ring Effect
==================================================
Line chart showing hedonic adaptation after a peak gaming experience,
modeled on Brickman, Coates & Janoff-Bulman (1978).

The chart depicts three trajectories:
  1. Happiness Baseline — a stable set-point (dashed gray line)
  2. Elden Ring Experience — sharp rise during gameplay, gradual decline
  3. Enjoyment of Other Games — drops below baseline after the peak
     (contrast effect), then slowly recovers

Output: ../images/elden-ring-hedonic-reset_hedonic-adaptation.png
         1200 × 720 px @ 150 DPI
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from pathlib import Path

# ==============================================================================
# 1. DATA GENERATION (smooth curves via dense sampling)
# ==============================================================================

# Dense time axis for smooth curves (weeks relative to Elden Ring release)
t_dense = np.linspace(-8, 24, 500)

# -- Baseline (constant) --
baseline = np.full_like(t_dense, 50)

# -- Elden Ring Experience --
# Anticipation builds from -8 to 0 (sigmoid), peaks around week 1,
# then decays exponentially back to baseline.
def elden_ring_curve(t):
    base = 50.0
    peak_amplitude = 45.0  # rises to 95

    # Anticipation: logistic rise from -8 to 0 (centered at -3)
    anticipation = peak_amplitude / (1.0 + np.exp(-0.9 * (t + 3.0)))

    # Decay: exponential after peak at t=1
    decay = peak_amplitude * np.exp(-0.45 * np.maximum(t - 1.0, 0.0))

    # Combine
    result = np.where(
        t <= 1.0,
        base + anticipation,      # build-up phase
        base + decay              # decay phase
    )
    # Ensure smooth transition around t=1 by blending
    blend_region = (t > 0.5) & (t < 1.5)
    anticipation_val = base + peak_amplitude / (1.0 + np.exp(-0.9 * (t + 3.0)))
    decay_val = base + peak_amplitude * np.exp(-0.45 * (t - 1.0))
    weight = (t - 0.5) / 1.0  # 0 to 1 over [0.5, 1.5]
    result[blend_region] = (1 - weight[blend_region]) * anticipation_val[blend_region] \
                           + weight[blend_region] * decay_val[blend_region]
    return np.clip(result, base, 100.0)


elden_ring = elden_ring_curve(t_dense)

# -- Enjoyment of Other Games --
# Stays at baseline until release, then drops steeply to a trough around
# week 4–6, then gradually recovers back to baseline by week 24.
def other_games_curve(t):
    base = 50.0
    trough = 18.0        # minimum enjoyment
    drop_depth = base - trough  # 32

    # Drop: logistic decline centered at t=1.5
    drop = drop_depth / (1.0 + np.exp(-1.2 * (t - 1.5)))

    # Recovery: logistic rise centered at t=9
    recovery = drop_depth / (1.0 + np.exp(-0.35 * (t - 9.0)))

    result = base - drop + recovery
    return np.clip(result, trough - 2, base + 2)


other_games = other_games_curve(t_dense)

# ==============================================================================
# 2. STYLING CONSTANTS — colorblind-safe (Wong, 2011)
# ==============================================================================
GOLD          = "#FFB000"   # Elden Ring
GOLD_DARK     = "#CC8C00"   # darker gold for peak marker edge
BLUE          = "#648FFF"   # Other Games
BLUE_DARK     = "#4A6FD4"   # darker blue for annotation
GRAY_BASELINE = "#AAAAAA"   # baseline line
GRAY_LABEL    = "#666666"
TEXT_COLOR    = "#2C2C2C"
SOURCE_COLOR  = "#888888"
GRID_COLOR    = "#E0E0E0"
BG_COLOR      = "#FFFFFF"
SHADE_ELDEN   = "#FFB000"   # same as GOLD
SHADE_OTHER   = "#648FFF"   # same as BLUE

# ==============================================================================
# 3. BUILD FIGURE
# ==============================================================================
fig, ax = plt.subplots(figsize=(8, 4.8))  # 8 × 4.8 in = 1200 × 720 px @ 150 DPI
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# Manually adjust margins so all labels fit without tight_layout cropping
fig.subplots_adjust(left=0.09, right=0.96, top=0.88, bottom=0.18)

# ----- 3a. Baseline (dashed gray) -----
ax.plot(t_dense, baseline, color=GRAY_BASELINE, linewidth=1.5,
        linestyle="--", zorder=3, label="Happiness Baseline",
        dash_capstyle="round")

# ----- 3b. Shaded regions -----

# Contrast effect region: between Other Games and Baseline where Other < Baseline
ax.fill_between(t_dense, other_games, baseline,
                where=(other_games < baseline),
                color=BLUE, alpha=0.10, zorder=1,
                label="Contrast Effect")

# Subtle glow under Elden Ring curve (above baseline only)
ax.fill_between(t_dense, baseline, elden_ring,
                where=(elden_ring >= baseline),
                color=GOLD, alpha=0.05, zorder=1)

# ----- 3c. Elden Ring Experience line -----
ax.plot(t_dense, elden_ring, color=GOLD, linewidth=2.8,
        zorder=5, label="Elden Ring Experience",
        solid_capstyle="round")

# ----- 3d. Other Games line -----
ax.plot(t_dense, other_games, color=BLUE, linewidth=2.5,
        zorder=4, label="Enjoyment of Other Games",
        solid_capstyle="round")

# ----- 3e. Peak marker -----
# Find the actual peak from the dense curve
peak_idx = np.argmax(elden_ring)
peak_x = t_dense[peak_idx]
peak_y = elden_ring[peak_idx]

ax.scatter([peak_x], [peak_y], color=GOLD, s=100, zorder=6,
           edgecolors=GOLD_DARK, linewidths=1.5, rasterized=False)

# ==============================================================================
# 4. ANNOTATIONS
# ==============================================================================

# 4a. "Peak Experience" annotation (top-center, pointing to peak)
ax.annotate(
    "Peak Experience",
    xy=(peak_x, peak_y),
    xytext=(peak_x + 3.2, peak_y + 11),
    fontsize=10.5, fontweight="bold", color=TEXT_COLOR,
    ha="center",
    arrowprops=dict(
        arrowstyle="->", color=TEXT_COLOR, lw=1.2,
        connectionstyle="arc3,rad=-0.15",
    ),
    bbox=dict(
        boxstyle="round,pad=0.35", facecolor="#FFF8E1",
        edgecolor=GOLD, lw=0.8, alpha=0.95,
    ),
)

# 4b. "Dopamine prediction error / Flow state" — small sub-annotation near peak
ax.annotate(
    "Dopamine prediction error\n+ Flow state",
    xy=(peak_x, peak_y),
    xytext=(peak_x - 4.0, peak_y + 7),
    fontsize=7.5, color=TEXT_COLOR, ha="center",
    fontstyle="italic",
    arrowprops=dict(
        arrowstyle="->", color=TEXT_COLOR, lw=0.8,
        connectionstyle="arc3,rad=0.15",
    ),
)

# 4c. "Hedonic adaptation" — on the downward slope of the Elden Ring curve
# Pick a point around week 4-5 where the decline is visible
adapt_x = 4.5
adapt_y = np.interp(adapt_x, t_dense, elden_ring)
ax.annotate(
    "Hedonic\nadaptation",
    xy=(adapt_x, adapt_y),
    xytext=(adapt_x - 1.5, adapt_y - 17),
    fontsize=9, fontstyle="italic", color=TEXT_COLOR, ha="center",
    arrowprops=dict(
        arrowstyle="->", color=TEXT_COLOR, lw=1.0,
        connectionstyle="arc3,rad=0.2",
    ),
)

# 4d. "Recalibrated reference point" — near trough of Other Games curve
trough_idx = np.argmin(other_games)
trough_x = t_dense[trough_idx]
trough_y = other_games[trough_idx]
ax.annotate(
    "Recalibrated\nreference point",
    xy=(trough_x, trough_y),
    xytext=(trough_x + 5.5, trough_y - 7),
    fontsize=9, color=TEXT_COLOR, ha="center",
    arrowprops=dict(
        arrowstyle="->", color=TEXT_COLOR, lw=1.0,
        connectionstyle="arc3,rad=-0.2",
    ),
    bbox=dict(
        boxstyle="round,pad=0.3", facecolor="#F0F4FF",
        edgecolor=BLUE, lw=0.8, alpha=0.9,
    ),
)

# 4e. "Contrast Effect" label — placed inside the shaded region
# Pick a spot around week 6-7, midway between baseline and other_games
label_t = 7.5
baseline_at_t = 50.0
other_at_t = np.interp(label_t, t_dense, other_games)
mid_y = (baseline_at_t + other_at_t) / 2 + 2  # slightly above midpoint

ax.text(
    label_t, mid_y,
    "Contrast Effect\n(diminished enjoyment)",
    fontsize=8.5, color=BLUE_DARK, ha="center", va="center",
    fontstyle="italic", fontweight="semibold",
    bbox=dict(
        boxstyle="round,pad=0.25", facecolor="#F5F8FF",
        edgecolor=BLUE, lw=0.6, alpha=0.85,
    ),
)

# ==============================================================================
# 5. LABELS AND TITLE
# ==============================================================================

ax.set_title(
    "Hedonic Adaptation: The Elden Ring Effect",
    fontsize=18, fontweight="bold", pad=14, color=TEXT_COLOR,
)

ax.set_xlabel(
    "Time (weeks relative to Elden Ring release)",
    fontsize=11, color=TEXT_COLOR, labelpad=8,
)
ax.set_ylabel(
    "Perceived Enjoyment / Happiness (0–100)",
    fontsize=11, color=TEXT_COLOR, labelpad=8,
)

# ----- 5a. X-axis ticks -----
xtick_positions = np.array([-8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 16, 20, 24])
xtick_labels = [
    "8 wks\nbefore", "6 wks\nbefore", "4 wks\nbefore", "2 wks\nbefore",
    "Release", "Week 2", "Week 4", "Week 6", "Week 8", "Week 10",
    "Week 12", "Week 16", "Week 20", "Week 24",
]
ax.set_xticks(xtick_positions)
ax.set_xticklabels(xtick_labels, fontsize=7.5, color=TEXT_COLOR, ha="center")

# ----- 5b. Y-axis -----
ax.set_ylim(0, 108)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.tick_params(axis="y", labelsize=9.5, color=TEXT_COLOR)

# ==============================================================================
# 6. GRID AND SPINES
# ==============================================================================

ax.grid(True, which="major", axis="both", color=GRID_COLOR, linewidth=0.4)
ax.grid(True, which="minor", axis="both", color="#EEEEEE", linewidth=0.2)
ax.set_axisbelow(True)

# Remove top and right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color(GRID_COLOR)
ax.spines["left"].set_linewidth(0.5)
ax.spines["bottom"].set_color(GRID_COLOR)
ax.spines["bottom"].set_linewidth(0.5)

# ==============================================================================
# 7. LEGEND
# ==============================================================================

legend = ax.legend(
    loc="lower right", fontsize=8.5,
    framealpha=0.92, edgecolor="#D0D0D0",
    markerscale=0.8,
)
legend.get_frame().set_facecolor(BG_COLOR)
legend.get_frame().set_linewidth(0.6)

# ==============================================================================
# 8. SOURCE LINE
# ==============================================================================

ax.text(
    0.0, -0.14,
    "Modeled after Brickman, Coates & Janoff-Bulman (1978); adapted for gaming context",
    transform=ax.transAxes, fontsize=7.5, color=SOURCE_COLOR,
    ha="left", va="top", fontstyle="italic",
)

# ==============================================================================
# 9. SAVE
# ==============================================================================

script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_png = images_dir / "elden-ring-hedonic-reset_hedonic-adaptation.png"

fig.savefig(
    output_png,
    dpi=150,
    facecolor=BG_COLOR,
    edgecolor="none",
)
plt.close(fig)

print(f"✓ Chart saved to {output_png}")
print(f"  Dimensions: {8 * 150} × {int(4.8 * 150)} px  @  150 DPI")
print("  Done.")
