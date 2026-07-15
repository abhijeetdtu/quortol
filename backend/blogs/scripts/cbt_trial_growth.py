"""
CBT Cumulative RCT Growth Chart (1970–2025)
============================================
Smooth S-curve interpolation through key reference points,
rendered with lets-plot at 300 DPI, 800×500 px.
"""

import numpy as np
import pandas as pd
from lets_plot import *


# ---------------------------------------------------------------------------
# Simple monotonic cubic Hermite interpolation (PCHIP-like)
# No scipy dependency needed.
# ---------------------------------------------------------------------------
def pchip_interpolate(x_known, y_known, x_fine):
    """Monotonic piecewise cubic Hermite interpolation."""
    n = len(x_known)
    # Compute slopes at known points (centred differences, clamped at ends)
    h = np.diff(x_known)
    delta = np.diff(y_known) / h
    # Slope at interior points: weighted harmonic mean of adjacent deltas
    m = np.zeros(n)
    m[0] = delta[0]
    m[-1] = delta[-1]
    for i in range(1, n - 1):
        if delta[i - 1] * delta[i] <= 0:
            m[i] = 0.0
        else:
            w1 = 2 * h[i] + h[i - 1]
            w2 = h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / delta[i - 1] + w2 / delta[i])

    # Evaluate Hermite basis for each segment
    y_fine = np.zeros_like(x_fine, dtype=float)
    for i in range(n - 1):
        x0, x1 = x_known[i], x_known[i + 1]
        y0, y1 = y_known[i], y_known[i + 1]
        m0, m1 = m[i], m[i + 1]
        mask = (x_fine >= x0) & (x_fine <= x1)
        t = (x_fine[mask] - x0) / (x1 - x0)
        t2 = t * t
        t3 = t2 * t
        h00 = 2 * t3 - 3 * t2 + 1
        h10 = t3 - 2 * t2 + t
        h01 = -2 * t3 + 3 * t2
        h11 = t3 - t2
        y_fine[mask] = (
            h00 * y0
            + h10 * (x1 - x0) * m0
            + h01 * y1
            + h11 * (x1 - x0) * m1
        )
    return y_fine

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. Reference points from published meta-analyses
# ---------------------------------------------------------------------------
ref_years = np.array([1970, 1985, 1995, 2005, 2012, 2024])
ref_counts = np.array([0, 15, 60, 180, 350, 441])

# ---------------------------------------------------------------------------
# 2. Smooth monotonic interpolation (S-curve preserving)
# ---------------------------------------------------------------------------
# PCHIP keeps monotonicity — ideal for cumulative counts.
fine_years = np.arange(1970, 2026, 1)
fine_counts = pchip_interpolate(ref_years, ref_counts, fine_years)

df = pd.DataFrame({"year": fine_years, "cumulative_rcts": fine_counts})

# Mark the reference points for overlay
df_ref = pd.DataFrame({"year": ref_years, "cumulative_rcts": ref_counts})

# ---------------------------------------------------------------------------
# 3. Build the chart
# ---------------------------------------------------------------------------
# Deep teal accent — warm but refined
ACCENT = "#1A7A6C"      # deep teal
ACCENT_LIGHT = "#B2DFDB"  # light teal for area fill
ACCENT_POINT = "#0D5C50"  # darker teal for the annotation point

p = (
    ggplot(df, aes(x="year", y="cumulative_rcts"))
    # Shaded area under the curve
    + geom_area(fill=ACCENT_LIGHT, alpha=0.45)
    # Smooth line
    + geom_line(color=ACCENT, size=1.5)
    # Reference point dots (small, semi-transparent)
    + geom_point(
        data=df_ref,
        mapping=aes(x="year", y="cumulative_rcts"),
        color=ACCENT,
        size=2.5,
        alpha=0.6,
    )
    # Final-value labelled point
    + geom_point(
        data=df_ref.loc[df_ref["year"] == 2024],
        mapping=aes(x="year", y="cumulative_rcts"),
        color=ACCENT_POINT,
        size=5,
    )
    + geom_label(
        data=df_ref.loc[df_ref["year"] == 2024],
        mapping=aes(x="year", y="cumulative_rcts"),
        label="441 RCTs (2024)",
        hjust=0,
        vjust=-0.6,
        size=10,
        color=ACCENT_POINT,
        fill="#ffffff",
        label_size=0,
        alpha=0.85,
    )
    # Scales
    + scale_x_continuous(
        breaks=list(range(1970, 2026, 5)),
        limits=[1968, 2030],
        expand=[0, 0],
    )
    + scale_y_continuous(
        limits=[0, 520],
        expand=[0, 10],
    )
    # Labels
    + labs(
        title="Growth of Cognitive Behavioral Therapy Clinical Trials",
        subtitle="441 RCTs, 33,881 patients across 8 disorders (1970–2025)",
        caption="Sources: Hofmann et al. 2012; Van Zyl et al. 2023 umbrella review",
        x="Year",
        y="Cumulative Number of Published RCTs",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold", hjust=0),
        plot_subtitle=element_text(size=11, color="#555555", hjust=0, margin=[0, 0, 20, 0]),
        plot_caption=element_text(size=8, color="#888888", hjust=0, margin=[10, 0, 0, 0]),
        axis_title_x=element_text(size=11),
        axis_title_y=element_text(size=11),
        axis_text=element_text(size=9),
        plot_margin=[10, 20, 25, 10],
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.4),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.4),
        panel_grid_minor=element_blank(),
        axis_line=element_line(color="#CCCCCC", size=0.5),
    )
)

# ---------------------------------------------------------------------------
# 4. Save at 300 DPI, ~800 × 500 px
# ---------------------------------------------------------------------------
output_path = "/home/pi/Documents/code/quortol/backend/blogs/images/cbt-trial-growth.png"

ggsave(
    p,
    output_path,
    dpi=300,
    w=800 / 300,    # inches
    h=500 / 300,
    unit="in",
    scale=1.0,
)

print(f"Chart saved to: {output_path}")
