#!/usr/bin/env python3
"""
Chart: The Great Lead Decline
Shows the dramatic reduction in US blood lead levels following the phaseout of
leaded gasoline and lead-based paint (NHANES data, 1976–2016).

Output: 1200×720 px @ 150 DPI
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

# ---- Data -----------------------------------------------------------------
years = [1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016]
bll   = [12.8, 9.2, 5.8, 3.7, 2.3, 1.7, 1.3, 1.1, 0.95, 0.85, 0.82]

# ---- Figure setup ---------------------------------------------------------
DPI = 150
W_INCHES = 1200 / DPI   # 8.0
H_INCHES = 720 / DPI    # 4.8

fig, ax = plt.subplots(figsize=(W_INCHES, H_INCHES), dpi=DPI)
fig.subplots_adjust(bottom=0.17, left=0.09, right=0.97, top=0.92)

DARK_BLUE = "#1f3a6b"       # colorblind-safe, strong line

# ---- Y limit: leave headroom for annotation above peak value ---------------
ax.set_ylim(0, 15.5)

# ---- Shaded region: leaded gasoline phaseout (1973–1995) -------------------
ax.axvspan(1973, 1995, color="#e0e0e0", alpha=0.5, zorder=0)

# Label for the shaded region (centered above the band)
ax.text(
    1973 + (1995 - 1973) / 2,   # midpoint = 1984
    14.8,                         # near top of y-limit
    "Leaded gasoline\nphaseout",
    ha="center",
    va="top",
    fontsize=11,
    color="#666666",
    style="italic",
    fontfamily="serif",
)

# ---- Line + markers -------------------------------------------------------
ax.plot(
    years, bll,
    color=DARK_BLUE,
    linewidth=2.5,
    marker="o",
    markersize=6,
    zorder=3,
)

# ---- Percentage-decline annotation ----------------------------------------
ax.annotate(
    "93.6% decline",
    xy=(2016, 0.82),
    xytext=(2022, 4.5),
    fontsize=13,
    color="#b22222",
    weight="bold",
    fontfamily="serif",
    ha="center",
    arrowprops=dict(
        arrowstyle="->",
        color="#b22222",
        lw=1.8,
        connectionstyle="arc3,rad=0.25",
    ),
    bbox=dict(boxstyle="round,pad=0.35", fc="#fff5f5", ec="#b22222", lw=1),
)

# ---- Axes labels & title --------------------------------------------------
ax.set_ylabel("Blood Lead Level (mcg/dL)", fontsize=13, fontfamily="serif")
ax.set_xlabel("Year", fontsize=13, fontfamily="serif")
ax.set_title(
    "The Great Lead Decline",
    fontsize=20,
    fontweight="bold",
    fontfamily="serif",
    pad=10,
)

# ---- Ticks -----------------------------------------------------------------
ax.set_xticks(years)
ax.tick_params(axis="both", labelsize=11)

# ---- Grid ------------------------------------------------------------------
ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

# ---- Source line (bottom of figure, below axes) ---------------------------
fig.text(
    0.5, 0.035,
    "Source: CDC National Health and Nutrition Examination Survey (NHANES), 1976–2016",
    ha="center",
    fontsize=9.5,
    color="#666666",
    fontfamily="serif",
    style="italic",
)

# ---- Save -----------------------------------------------------------------
out_png = Path(__file__).resolve().parent.parent / "images" / "once-safe-now-toxic_lead_decline.png"
out_png.parent.mkdir(parents=True, exist_ok=True)

fig.savefig(out_png, dpi=DPI)
plt.close(fig)
print(f"Chart saved → {out_png}")
