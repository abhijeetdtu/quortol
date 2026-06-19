"""
New England House Price Index, Q1 2020–Q1 2026
FHFA All-Transactions Index (1980:Q1 = 100)

Data source: Federal Housing Finance Agency via FRED (CNEWSTHPI)
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
from datetime import datetime
from pathlib import Path

# ── Okabe-Ito palette (colorblind-safe) ───────────────────────────────────────
OKABE_ITO = {
    "orange":   "#E69F00",
    "skyblue":  "#56B4E9",
    "green":    "#009E73",
    "yellow":   "#F0E442",
    "blue":     "#0072B2",
    "vermillion": "#D55E00",
    "pink":     "#CC79A7",
    "grey":     "#999999",
}
LINE_COLOR = OKABE_ITO["blue"]
REF_COLOR  = OKABE_ITO["vermillion"]
PANDEMIC_COLOR = OKABE_ITO["grey"]

# ── Data ───────────────────────────────────────────────────────────────────────
data = [
    ("2020-01-01", 622.87),
    ("2020-04-01", 629.95),
    ("2020-07-01", 642.96),
    ("2020-10-01", 659.63),
    ("2021-01-01", 676.43),
    ("2021-04-01", 713.71),
    ("2021-07-01", 754.66),
    ("2021-10-01", 773.45),
    ("2022-01-01", 795.13),
    ("2022-04-01", 846.99),
    ("2022-07-01", 860.43),
    ("2022-10-01", 852.86),
    ("2023-01-01", 865.67),
    ("2023-04-01", 903.44),
    ("2023-07-01", 925.19),
    ("2023-10-01", 928.55),
    ("2024-01-01", 942.22),
    ("2024-04-01", 977.39),
    ("2024-07-01", 989.68),
    ("2024-10-01", 995.37),
    ("2025-01-01", 1006.68),
    ("2025-04-01", 1031.69),
    ("2025-07-01", 1039.29),
    ("2025-10-01", 1047.15),
    ("2026-01-01", 1056.68),
]

dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in data]
values = [v for _, v in data]

# ── Calculate the 69.6% increase reference ─────────────────────────────────────
base_val = values[0]   # 622.87 (Q1 2020)
final_val = values[-1]  # 1056.68 (Q1 2026)
pct_increase = (final_val / base_val - 1) * 100  # ≈ 69.6%
ref_line_val = base_val * (1 + 69.6 / 100)  # same as final_val approximately

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 12,
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

# ── Pandemic highlight (Q1 2020 – Q1 2021) ────────────────────────────────────
pandemic_start = datetime(2020, 1, 1)
pandemic_end   = datetime(2021, 4, 1)  # extends a bit into Q2 2021

ax.axvspan(pandemic_start, pandemic_end,
           color=PANDEMIC_COLOR, alpha=0.12, zorder=0,
           label="Pandemic period")

# Add a small "Pandemic" label in the shaded region
mid_pandemic = datetime(2020, 7, 1)
ax.text(mid_pandemic, 610, "Pandemic\nonset",
        ha="center", va="top", fontsize=8.5, color="#777777",
        style="italic", linespacing=1.2)

# ── Horizontal reference line for 69.6% increase ───────────────────────────────
ax.axhline(y=ref_line_val, color=REF_COLOR, linestyle="--", linewidth=1.0,
           alpha=0.65, zorder=1)

# Label for reference line: positioned near the right edge
ax.text(dates[-1], ref_line_val + 12,
        f"+{69.6:.1f}%  (Q1 2020→Q1 2026)",
        color=REF_COLOR, fontsize=10, fontweight="bold",
        ha="right", va="bottom")

# ── Main line ──────────────────────────────────────────────────────────────────
ax.plot(dates, values, color=LINE_COLOR, linewidth=2.25,
        solid_capstyle="round", zorder=3)

# ── Data point markers ─────────────────────────────────────────────────────────
ax.scatter(dates, values, color=LINE_COLOR, s=45,
           edgecolors="white", linewidth=0.6, zorder=4)

# ── End-of-line annotation ─────────────────────────────────────────────────────
ax.annotate(
    f"{final_val:,.2f}",
    xy=(dates[-1], final_val),
    xytext=(18, 0),
    textcoords="offset points",
    fontsize=11, fontweight="bold", color=LINE_COLOR,
    ha="left", va="center",
    arrowprops=dict(arrowstyle="->", color=LINE_COLOR, lw=1.0),
)

# ── Axes ───────────────────────────────────────────────────────────────────────
# X-axis: quarterly data, show year ticks
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.set_xlim(dates[0] - np.timedelta64(45, "D"),
            dates[-1] + np.timedelta64(90, "D"))

ax.tick_params(axis="x", which="major", length=6, pad=6, labelsize=11)
ax.tick_params(axis="x", which="minor", length=3)
plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

# Y-axis: start at 600
y_min = 600
y_max = max(values) * 1.12
ax.set_ylim(y_min, y_max)

ax.set_ylabel("Index (1980:Q1 = 100)", fontsize=12, labelpad=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.yaxis.set_major_locator(mticker.MultipleLocator(100))

# Grid: light horizontal lines only
ax.yaxis.grid(True, linestyle="-", alpha=0.25, color="#999999", zorder=0)
ax.set_axisbelow(True)

# ── Title & subtitle ───────────────────────────────────────────────────────────
ax.set_title("New England House Price Index, Q1 2020–Q1 2026",
             fontsize=20, fontweight="bold", pad=8, color="#111111")

# Subtitle
ax.text(0.0, 1.02,
        "FHFA All-Transactions Index, 1980:Q1 = 100",
        transform=ax.transAxes, fontsize=12, color="#555555",
        ha="left", va="bottom")

# ── Source line ────────────────────────────────────────────────────────────────
fig.text(0.5, -0.01,
         "Source: FHFA via FRED",
         ha="center", va="top",
         fontsize=10, color="#777777",
         transform=ax.transAxes)

# ── Adjust layout ──────────────────────────────────────────────────────────────
fig.tight_layout(rect=[0, 0.04, 1, 1])

# ── Save ───────────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "new-england-homes_price_index.png"
fig.savefig(output_path, dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
plt.close(fig)

print(f"Chart saved → {output_path.resolve()}")
print(f"  Dimensions:  1200 × 720 px @ 150 DPI")
print(f"  Format:      PNG")
print(f"  Data points: {len(values)}")
print(f"  Q1 2020:     {values[0]}")
print(f"  Q1 2026:     {values[-1]}")
print(f"  Increase:    {pct_increase:.1f}%")
