"""
chart2_atomic-printing_milestones.py
======================================
Horizontal timeline / milestone chart for atomic-precision manufacturing (APM).
Companion visual for magazine feature article.

Output: 1200x720 px PNG at 150 DPI
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# 1. DATA
# ---------------------------------------------------------------------------
data = [
    (1959, 'Feynman: "Plenty of Room\nat the Bottom" lecture',
     "Conceptual"),
    (1981, "Binnig & Rohrer invent\nSTM (Nobel 1986)",
     "Tool"),
    (1989, 'Eigler & Schweizer arrange\n35 Xe atoms \u2192 "IBM"',
     "Demonstration"),
    (1990, "Eigler & Schweizer: atom\npositioning in Nature",
     "Demonstration"),
    (2006, "Zyvex Labs founded for\natomic-precision mfg",
     "Industry"),
    (2012, "First single-atom transistor\n(UNSW / M. Simmons)",
     "Device"),
    (2018, "National Quantum\nInitiative Act ($1.2B)",
     "Policy"),
    (2021, "APAM for Si quantum\ncomputing (Sandia + Zyvex)",
     "Technique"),
    (2024, "UCL: 97%+ single-atom\nplacement with arsenic",
     "Technique"),
    (2025, "NIST atom-scale device\nprogram + ML automation",
     "Tool"),
    (2025, "Sandia integrates APAM\ninto CMOS manufacturing",
     "Integration"),
    (2025, "11-qubit atomic processor\nin silicon (Nature / SQC)",
     "Device"),
    (2026, "NIST $20M Quantum Mfg\nEngineering Center",
     "Policy"),
]

df = pd.DataFrame(data, columns=["year", "milestone", "category"])

# Category order: top to bottom on the y-axis
cat_order = [
    "Conceptual",
    "Tool",
    "Demonstration",
    "Industry",
    "Device",
    "Technique",
    "Integration",
    "Policy",
]

# Numeric y positions (Conceptual = top = 7, Policy = bottom = 0)
cat_to_y = {cat: len(cat_order) - 1 - i for i, cat in enumerate(cat_order)}
df["y_pos"] = df["category"].map(cat_to_y).astype(float)

# Baseline column for stems (workaround: lets-plot struggles with
# constant y=0 in geom_segment, so use a column)
df["y_zero"] = 0.0

# Pre-compute text y positions with small vertical nudges
# for same-category adjacent points (1989 / 1990)
df["text_y"] = df["y_pos"].copy()
df.loc[(df["year"] == 1989) & (df["category"] == "Demonstration"), "text_y"] = 5.3
df.loc[(df["year"] == 1990) & (df["category"] == "Demonstration"), "text_y"] = 4.7

# y-axis labels
y_labels = [
    "Conceptual",
    "Tool",
    "Demonstration",
    "Industry",
    "Device",
    "Technique",
    "Integration",
    "Policy",
]
y_breaks = [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0]

# ---------------------------------------------------------------------------
# 2. COLORBLIND-SAFE PALETTE  (Tol / Wong inspired)
# ---------------------------------------------------------------------------
colors = {
    "Conceptual": "#4477AA",
    "Tool": "#66CCEE",
    "Demonstration": "#228833",
    "Industry": "#CCBB44",
    "Device": "#EE6677",
    "Technique": "#AA3377",
    "Integration": "#BBBBBB",
    "Policy": "#000000",
}

# ---------------------------------------------------------------------------
# 3. BUILD THE CHART
# ---------------------------------------------------------------------------

p = (
    ggplot(df)
    # ---- vertical stems from each point down to near the x-axis ----
    + geom_segment(
        aes(x="year", xend="year", y="y_zero", yend="y_pos", color="category"),
        size=0.45,
        alpha=0.30,
    )
    # ---- points ----
    + geom_point(aes(x="year", y="y_pos", color="category"), size=4.5)
    # ---- milestone annotations ----
    + geom_text(
        aes(x="year", y="text_y", label="milestone"),
        hjust=0,
        vjust=0.5,
        size=6.5,
        nudge_x=0.4,
        lineheight=0.85,
        color="#222222",
    )
    # ---- custom colors ----
    + scale_color_manual(name="Category", values=colors)
    # ---- x-axis: years ----
    + scale_x_continuous(
        breaks=[1955, 1960, 1965, 1970, 1975, 1980, 1985, 1990, 1995,
                2000, 2005, 2010, 2015, 2020, 2025, 2030, 2035],
        limits=[1955, 2045],
    )
    # ---- y-axis: categories as labelled continuous scale ----
    + scale_y_continuous(
        breaks=y_breaks,
        labels=y_labels,
        limits=[-0.6, 7.5],
    )
    # ---- labels ----
    + labs(
        title="The Road to Atomic Precision: Six Decades of Milestones",
        x="Year",
        caption="Sources: NIST, Nature, UNSW, IBM Research, DOE, Zyvex Labs",
    )
    # ---- clean magazine-style theme ----
    + theme_minimal()
    + theme(
        # White background
        panel_background=element_blank(),
        plot_background=element_blank(),
        # Grid lines — only vertical guides
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.35),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_blank(),
        # Axis lines
        axis_line_x=element_line(color="#333333", size=0.5),
        axis_line_y=element_blank(),
        axis_ticks=element_blank(),
        # Text elements
        axis_text_y=element_text(size=11, face="bold"),
        axis_text_x=element_text(size=10),
        axis_title_x=element_text(size=11, margin=[8, 0, 0, 0]),
        # Title
        plot_title=element_text(
            size=17, face="bold", hjust=0.5, margin=[0, 0, 10, 0]
        ),
        # Caption (source line)
        plot_caption=element_text(
            size=8.5, color="#666666", hjust=1, margin=[6, 0, 0, 0]
        ),
        # Legend
        legend_position="none",
        # Plot margins
        plot_margin=[10, 30, 5, 5],
    )
)

# ---------------------------------------------------------------------------
# 4. SAVE  — 8 in × 4.8 in @ 150 DPI = 1200 × 720 px
# ---------------------------------------------------------------------------
out_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "atomic-printing_milestones.png"
ggsave(
    p,
    filename=str(out_path),
    dpi=150,
    w=8,
    h=4.8,
)

print(f"Chart saved to: {out_path.resolve()}")
print(f"Dimensions: 1200 \u00d7 720 px @ 150 DPI")
