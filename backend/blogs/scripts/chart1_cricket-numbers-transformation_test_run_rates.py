"""
Chart: Test Cricket Run Rate Evolution, 1877–2022
Data source: Anantha Narayanan, ESPNcricinfo
https://www.espncricinfo.com/story/anantha-narayanan-everything-you-wanted-to-know-about-run-rates-in-test-cricket-1336987
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
df = pd.DataFrame({
    "era_display": [
        "Pre-WWI\n(1877–1900)",
        "Pre-WWI\n(1901–1914)",
        "Inter-war\n(1919–1939)",
        "Post-war\n(1946–1970)",
        "Post-war\n(1971–1990)",
        "Pre-millennium\n(1991–2000)",
        "Modern\n(2001–2022)",
    ],
    "era_sort": range(7),
    "runs_per_over": [2.70, 2.85, 2.72, 2.62, 2.80, 2.89, 3.20],
})

# ── Plot ──────────────────────────────────────────────────────────────────────
blue = "#4472C4"  # colorblind-safe blue

p = (
    ggplot(df, aes(x="era_sort", y="runs_per_over"))
    + geom_line(color=blue, size=1.8)
    + geom_point(color=blue, size=4.5)
    # Reference line – historical average (1877–2000)
    + geom_hline(
        yintercept=2.80,
        color="#555555",
        size=0.9,
        linetype="dashed",
    )
    # Label for reference line (manually placed via single-row DF)
    + geom_text(
        data=pd.DataFrame({"x": [5.8], "y": [2.815], "label": ["Historical average (1877–2000)"]}),
        mapping=aes(x="x", y="y", label="label"),
        color="#555555",
        size=9,
        hjust=1,
    )
    # Axis scale
    + scale_x_continuous(
        breaks=df["era_sort"],
        labels=df["era_display"],
    )
    + scale_y_continuous(
        limits=[2.0, 3.5],
        breaks=[2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4],
    )
    # Titles
    + ggtitle(
        "Test Cricket Run Rate Evolution, 1877–2022",
        subtitle=(
            "Runs per over across seven eras — "
            "more than a century of stability, then acceleration"
        ),
    )
    + xlab("")
    + ylab("Runs per Over")
    # Theme
    + theme_minimal()
    + theme(
        axis_text_x=element_text(angle=45, hjust=1, size=10),
        axis_text_y=element_text(size=10),
        axis_title_y=element_text(size=12),
        plot_title=element_text(size=18, face="bold"),
        plot_subtitle=element_text(size=12, color="#555555"),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 20, 20, 20],
    )
)

# ── Add source caption ────────────────────────────────────────────────────────
p = p + labs(
    caption="Source: Anantha Narayanan, ESPNcricinfo"
)

# ── Save ──────────────────────────────────────────────────────────────────────
output_png = "/home/pi/Documents/code/quortol/backend/blogs/images/chart1_cricket-numbers-transformation_test_run_rates.png"

ggsave(
    p,
    output_png,
    w=1200,
    h=720,
    unit="px",
    dpi=150,
)

print(f"Chart saved to: {output_png}")
