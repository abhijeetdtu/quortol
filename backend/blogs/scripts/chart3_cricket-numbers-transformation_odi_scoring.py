"""
Chart: ODI Scoring Inflation, 1970s–2020s
===========================================
Horizontal bar chart showing average total runs per ODI match
across decades, with a 1970s baseline reference line and +20% annotation.

Source: Anantha Narayanan, ESPNcricinfo
https://www.espncricinfo.com/story/anantha-narayanan-more-runs-boundaries-wickets-fewer-no-balls-matches-run-outs-a-look-at-51-years-of-men-s-odis-1305819

Output: 1200×720 px, 150 DPI, PNG
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "decade": ["1970s", "1980s", "1990s", "2000s", "2015-2022"],
    "avg_runs": [385, 410, 435, 455, 463],
    "bar_label": ["385", "410", "435", "455", "463"],
})

# Chronological order — first category at bottom of horizontal chart
df["decade"] = pd.Categorical(
    df["decade"],
    categories=["1970s", "1980s", "1990s", "2000s", "2015-2022"],
    ordered=True,
)

# ---------------------------------------------------------------------------
# Annotation data frames — use same aesthetics so they align on the
# categorical y-axis naturally
# ---------------------------------------------------------------------------
baseline_annot = pd.DataFrame({
    "decade": pd.Categorical(
        ["2015-2022"],
        categories=df["decade"].cat.categories,
        ordered=True,
    ),
    "avg_runs": [388],
    "label": ["1970s baseline"],
})

pct_annot = pd.DataFrame({
    "decade": pd.Categorical(
        ["2015-2022"],
        categories=df["decade"].cat.categories,
        ordered=True,
    ),
    "avg_runs": [478],
    "label": ["+20%"],
})

# ---------------------------------------------------------------------------
# Color — colorblind-safe teal (Wong, 2011)
# ---------------------------------------------------------------------------
TEAL = "#009E73"

# ---------------------------------------------------------------------------
# Build the plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(y="decade", x="avg_runs"))
    # Horizontal bars
    + geom_bar(stat="identity", fill=TEAL, width=0.55, alpha=0.90)
    # Run-value labels at the end of each bar
    + geom_text(
        aes(label="bar_label"),
        hjust=-0.4, size=9.5, color="#222222",
        family="sans-serif",
    )
    # Vertical dashed reference line at 1970s baseline
    + geom_vline(
        xintercept=385, linetype="dashed",
        color="#666666", size=0.8,
    )
    # "1970s baseline" label near the reference line (top of chart)
    + geom_text(
        data=baseline_annot,
        mapping=aes(label="label"),
        hjust=0, vjust=-0.8, size=9, color="#666666",
        family="sans-serif",
    )
    # "+20%" annotation at the 2015-2022 bar
    + geom_text(
        data=pct_annot,
        mapping=aes(label="label"),
        hjust=0, size=12, color="#0072B2",
        fontface="bold", family="sans-serif",
    )
    # X-axis scale
    + scale_x_continuous(
        limits=[350, 500],
        breaks=[350, 375, 400, 425, 450, 475, 500],
        expand=[0, 0],
    )
    # Labels
    + labs(
        title="ODI Scoring Inflation, 1970s–2020s",
        subtitle="Average total runs per match — a 20% increase over 50 years",
        x="Average Match Runs",
        y="",
        caption="Source: Anantha Narayanan, ESPNcricinfo",
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold",
                                hjust=0.5, color="#111111"),
        plot_subtitle=element_text(size=12, hjust=0.5,
                                   color="#555555"),
        axis_text_x=element_text(size=10, color="#333333"),
        axis_text_y=element_text(size=11, color="#333333"),
        axis_title_x=element_text(size=11, color="#444444"),
        axis_ticks=element_blank(),
        panel_grid_major_x=element_line(color="#E0E0E0",
                                        size=0.4),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        plot_caption=element_text(size=9, color="#777777",
                                  hjust=0),
        plot_margin=[15, 30, 10, 20],
    )
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
png_path = output_dir / "cricket-numbers-transformation_odi_scoring.png"

ggsave(p, str(png_path), dpi=150, w=1200, h=720, unit="px")

print(f"Chart saved to: {png_path}")
print("Done.")
