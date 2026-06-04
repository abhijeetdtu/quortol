#!/usr/bin/env python3
"""
Chart: The $680 Billion Cost of Sleep Deprivation
Output: ../images/science-of-the-alarm-clock_gdp_loss.png  (1200 × 720 px, 150 DPI)

Horizontal bar chart showing annual economic losses from sleep deprivation
across five OECD countries, with working-days-lost annotations.

Data: RAND Corporation, Why Sleep Matters (RR1791, 2016)
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# =============================================================================
# 1. DATA  (sorted largest-to-smallest loss; US at top)
# =============================================================================
countries = [
    "United States",
    "Japan",
    "Germany",
    "United Kingdom",
    "Canada",
]

loss_billions = [411.0, 138.0, 60.0, 50.0, 21.4]   # US$ billions
pct_gdp       = [2.28, 2.92, 1.56, 1.86, 1.35]      # % of GDP
work_days     = [1.23, 0.604, 0.209, 0.207, 0.078]   # million working days lost/year

work_days_labels = [
    "1,230,000 working days",
    "604,000 working days",
    "209,000 working days",
    "207,000 working days",
    "78,000 working days",
]

total_loss = sum(loss_billions)  # $680.4B

# Y-axis positions (0 = top)
y_pos = np.arange(len(countries))

# =============================================================================
# 2. STYLE
# =============================================================================
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size":   11,
    "axes.titlesize":  16,
    "axes.labelsize":  12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 11,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   True,
    "axes.spines.bottom": True,
    "axes.edgecolor": "#555555",
    "grid.color":    "#d5d5d5",
    "grid.alpha":     0.5,
    "axes.facecolor": "#fafafa",
    "figure.facecolor": "white",
})

# =============================================================================
# 3. FIGURE
# =============================================================================
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

# -- Colormap: single-hue sequential (colorblind-safe) -----------------------
# Normalise loss values to [0, 1] for colormap lookup
norm = plt.Normalize(min(loss_billions), max(loss_billions))
cmap = plt.cm.Blues
bar_colors = [cmap(0.35 + 0.55 * norm(v)) for v in loss_billions]  # range 0.35→0.90

bars = ax.barh(
    y_pos,
    loss_billions,
    height=0.55,
    color=bar_colors,
    edgecolor="white",
    linewidth=0.8,
    zorder=3,
)

# =============================================================================
# 4. BAR LABELS  (dollar amount + % of GDP)
# =============================================================================
for i, (loss, pct) in enumerate(zip(loss_billions, pct_gdp)):
    label = f"${loss:,.1f}B  ({pct:.2f}% of GDP)"
    ax.text(
        loss + 2.5,
        y_pos[i],
        label,
        va="center",
        ha="left",
        fontsize=10,
        fontweight="bold",
        color="#1a1a1a",
    )

# =============================================================================
# 5. WORKING DAYS ANNOTATIONS  (right margin)
# =============================================================================
# We'll place these to the right of the bar labels, using a secondary x-position
# that sits further out. Use an invisible offset so they align neatly.
right_margin_x = max(loss_billions) * 1.38  # right-aligned annotation position

for i, (wdl, country) in enumerate(zip(work_days_labels, countries)):
    ax.annotate(
        "",
        xy=(loss_billions[i], y_pos[i]),
        xytext=(right_margin_x, y_pos[i]),
        arrowprops=dict(
            arrowstyle="->",
            color="#888888",
            lw=0.6,
            connectionstyle="arc3,rad=0",
        ),
        zorder=2,
    )
    ax.text(
        right_margin_x + 2,
        y_pos[i],
        wdl,
        va="center",
        ha="left",
        fontsize=8.5,
        color="#555555",
        style="italic",
    )

# =============================================================================
# 6. AXES
# =============================================================================
ax.set_yticks(y_pos)
ax.set_yticklabels(countries)
ax.set_xlabel("Annual Economic Loss (US$ billions)", fontsize=12, color="#2c3e50")

# X-axis: extend to accommodate annotations
x_max = max(loss_billions) * 1.85
ax.set_xlim(0, x_max)

# Grid: vertical only
ax.xaxis.set_major_locator(mticker.MultipleLocator(50))
ax.xaxis.set_minor_locator(mticker.MultipleLocator(25))
ax.grid(which="major", axis="x", linewidth=0.6)
ax.grid(which="minor", axis="x", linewidth=0.3, alpha=0.35)

# =============================================================================
# 7. TITLE & SUBTITLE
# =============================================================================
fig.suptitle(
    f"The ${total_loss:.0f} Billion Cost of Sleep Deprivation",
    fontsize=18,
    fontweight="bold",
    y=0.97,
    color="#1a1a1a",
)

ax.set_title(
    "Annual economic losses across five OECD countries (RAND Corporation, 2016)",
    fontsize=11,
    fontweight="normal",
    pad=8,
    color="#555555",
    loc="left",
)

# =============================================================================
# 8. NOTE & SOURCE LINE
# =============================================================================
fig.text(
    0.5, 0.005,
    "Source: RAND Corporation, Why Sleep Matters (RR1791, 2016)",
    ha="center", va="bottom",
    fontsize=9,
    color="#888888",
    style="italic",
)

# Footnote about scenario
fig.text(
    0.5, 0.022,
    "Scenario 1 (highest estimates) shown. Losses include mortality risk, "
    "reduced productivity, and lost labor supply.",
    ha="center", va="bottom",
    fontsize=8,
    color="#999999",
)

# =============================================================================
# 9. LAYOUT & SAVE
# =============================================================================
fig.tight_layout(rect=[0, 0.04, 0.82, 0.93])

output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "science-of-the-alarm-clock_gdp_loss.png"

fig.savefig(
    output_path,
    dpi=150,
    facecolor="white",
    edgecolor="none",
)
plt.close(fig)

print(f"✓ Chart saved → {output_path.resolve()}")
print(f"  Dimensions: 1200 × 720 px  @  150 DPI")
print(f"  Total annual loss shown: ${total_loss:.1f}B")
