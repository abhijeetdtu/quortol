"""
Chart: Prospect Theory Probability Weighting Function π(p)
Data source: Kahneman & Tversky (1979), Econometrica, 47(2), 263–291. Figure 4.
"""

import numpy as np
import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Colors ─────────────────────────────────────────────────────────────────────
BLUE  = "#4472C4"   # colorblind-safe blue for weighting function
GRAY  = "#888888"   # gray for rational line and references
FILL  = "#4472C4"   # ribbon fill (same blue, with alpha)

# ── Raw data from Kahneman & Tversky (1979), Figure 4 ─────────────────────────
p_raw = [0.00, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.00]
w_raw = [0.00, 0.05, 0.12, 0.17, 0.30, 0.45, 0.60, 0.75, 0.83, 0.95, 1.00]

df_pt = pd.DataFrame({"p": p_raw, "w": w_raw})               # Prospect Theory points
df_rational = pd.DataFrame({"p": [0, 1], "w": [0, 1]})       # Rational diagonal

# ── Fine grid for shaded ribbon (linear interpolation) ─────────────────────────
p_dense = np.linspace(0, 1, 1001)
w_dense = np.interp(p_dense, p_raw, w_raw)

df_ribbon = pd.DataFrame({
    "p": p_dense,
    "w": w_dense,
    "rational": p_dense,
    "ymin": np.minimum(p_dense, w_dense),   # lower envelope
    "ymax": np.maximum(p_dense, w_dense),   # upper envelope
})

# ── Build chart ────────────────────────────────────────────────────────────────
p = (
    ggplot()
    # Shaded region between the two curves
    + geom_ribbon(
        data=df_ribbon,
        mapping=aes(x="p", ymin="ymin", ymax="ymax"),
        fill=FILL,
        alpha=0.12,
    )
    # Rational diagonal (expected utility)
    + geom_line(
        data=df_rational,
        mapping=aes(x="p", y="w"),
        color=GRAY,
        size=0.9,
        linetype="dashed",
    )
    # Prospect Theory weighting function
    + geom_line(
        data=df_pt,
        mapping=aes(x="p", y="w"),
        color=BLUE,
        size=1.6,
    )
    # Data markers
    + geom_point(
        data=df_pt,
        mapping=aes(x="p", y="w"),
        color=BLUE,
        size=3.5,
    )
    # Horizontal reference line at y = 0.5
    + geom_hline(
        yintercept=0.5,
        color=GRAY,
        size=0.5,
        linetype="dotted",
    )
    # Vertical reference line at x = 0.5
    + geom_vline(
        xintercept=0.5,
        color=GRAY,
        size=0.5,
        linetype="dotted",
    )
    # Label for rational diagonal (placed near top-right)
    + geom_text(
        data=pd.DataFrame({"p": [0.85], "w": [0.80], "label": ["π(p) = p (Rational)"]}),
        mapping=aes(x="p", y="w", label="label"),
        color=GRAY,
        size=8.5,
        hjust=0,
        angle=38,
    )
    # Label for weighting function (placed below the curve near the right)
    + geom_text(
        data=pd.DataFrame({"p": [0.68], "w": [0.56], "label": ["Prospect Theory\nweighting function"]}),
        mapping=aes(x="p", y="w", label="label"),
        color=BLUE,
        size=8.5,
        hjust=0,
        lineheight=1.2,
    )
    # Label for over-weighting region (lower-left, above diagonal)
    + geom_text(
        data=pd.DataFrame({"p": [0.12], "w": [0.28], "label": ["Overweighting\nπ(p) > p"]}),
        mapping=aes(x="p", y="w", label="label"),
        color=BLUE,
        size=7.5,
        hjust=0.5,
        lineheight=1.2,
    )
    # Label for under-weighting region (upper-right, below diagonal)
    + geom_text(
        data=pd.DataFrame({"p": [0.82], "w": [0.34], "label": ["Underweighting\nπ(p) < p"]}),
        mapping=aes(x="p", y="w", label="label"),
        color=BLUE,
        size=7.5,
        hjust=0.5,
        lineheight=1.2,
    )
    # Label for x=0.5 reference line
    + geom_text(
        data=pd.DataFrame({"p": [0.50], "w": [0.015], "label": ["p = 0.5"]}),
        mapping=aes(x="p", y="w", label="label"),
        color=GRAY,
        size=7,
        hjust=0.5,
    )
    # Label for y=0.5 reference line
    + geom_text(
        data=pd.DataFrame({"p": [0.015], "w": [0.50], "label": ["π(p) = 0.5"]}),
        mapping=aes(x="p", y="w", label="label"),
        color=GRAY,
        size=7,
        vjust=0,
        angle=90,
    )
    # Axis scales
    + scale_x_continuous(
        limits=[-0.02, 1.02],
        breaks=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        expand=True,
    )
    + scale_y_continuous(
        limits=[-0.02, 1.02],
        breaks=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        expand=True,
    )
    # Titles
    + ggtitle(
        "How Humans Distort Probability",
        subtitle="The Prospect Theory Weighting Function (Kahneman & Tversky, 1979)",
    )
    + xlab("Stated Probability p")
    + ylab("Decision Weight π(p)")
    # Source caption
    + labs(
        caption="Data source: Kahneman & Tversky (1979), Econometrica, 47(2), 263–291. Figure 4."
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=20, face="bold", margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=13, color="#555555", margin=[0, 0, 12, 0]),
        axis_title_x=element_text(size=13),
        axis_title_y=element_text(size=13),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 20, 10, 20],
        plot_caption=element_text(size=9, color="#999999", margin=[12, 0, 0, 0]),
        legend_position="none",  # we use direct labels instead of a legend
    )
)

# ── Save ───────────────────────────────────────────────────────────────────────
output_png = "/home/pi/Documents/code/quortol/backend/blogs/images/the-entropy-of-knowing_prospect_theory_weighting.png"

ggsave(
    p,
    output_png,
    w=1200,
    h=720,
    unit="px",
    dpi=150,
)

print(f"Chart saved to: {output_png}")
