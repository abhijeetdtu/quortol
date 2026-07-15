#!/usr/bin/env python3
"""
Vertical bar chart: Membership of Major Sherlock Holmes Societies Worldwide
Output: PNG at 1200×720 px, 150 DPI
Uses: lets-plot
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ── Data ─────────────────────────────────────────────────────────────────────
df = pd.DataFrame({
    "Society": [
        "Sherlock Holmes Society of London",
        "Japan Sherlock Holmes Club",
        "Baker Street Irregulars",
        "Société Sherlock Holmes de France",
        "Deutsche Sherlock-Holmes-Gesellschaft",
        "Uno Studio in Holmes",
        "Baskerville Hall Club",
    ],
    "Founded": [1951, 1977, 1934, 1993, 2010, 1987, 1979],
    "Members":   [1400, 1000, 300, 150, 120, 100, 80],
})

# Preserve order (largest first)
df["Society"] = pd.Categorical(
    df["Society"],
    categories=df["Society"].tolist(),
    ordered=True,
)

# Colorblind-safe palette — one distinct colour per society
color_map = {
    "Sherlock Holmes Society of London":   "#D4A017",   # gold
    "Japan Sherlock Holmes Club":          "#1E3A5F",   # navy
    "Baker Street Irregulars":             "#1B8A6B",   # teal
    "Société Sherlock Holmes de France":   "#8B1A4A",   # burgundy
    "Deutsche Sherlock-Holmes-Gesellschaft": "#2E7D32", # forest
    "Uno Studio in Holmes":                "#4A6FA5",   # slate
    "Baskerville Hall Club":               "#A0522D",   # rust
}

# ── Annotation data (positioned at top-right of plot area) ────────────────────
annot_df = pd.DataFrame({
    "x": [6.5],
    "y": [1320],
    "label": ["400+ active societies worldwide\nacross 6 continents"],
})

# ── Build chart ──────────────────────────────────────────────────────────────
p = (
    ggplot(df, aes(x="Society", y="Members", fill="Society"))
    + geom_bar(stat="identity", width=0.72, color="white", size=0.4)
    + scale_fill_manual(values=color_map, guide="none")
    + geom_text(
        aes(label="Members"),
        size=10,
        vjust=-0.6,
        color="#222222",
        family="sans-serif",
    )
    # Inset annotation
    + geom_text(
        data=annot_df,
        mapping=aes(x="x", y="y", label="label"),
        size=9,
        color="#555555",
        family="sans-serif",
        fontface="italic",
        hjust=0.5,
        vjust=1,
    )
    # Titles
    + ggtitle(
        "Major Sherlock Holmes Societies Worldwide",
        subtitle=(
            "Estimated membership of the largest Holmesian organizations  •  "
            "Sources: Wikipedia, BSI, SH Society of London"
        ),
    )
    + xlab("")
    + ylab("Members")
    + ggsize(768, 461)   # yields 1200×720 px at 150 DPI (ggsize uses 96 DPI base)
    + theme(
        plot_title       = element_text(size=18, face="bold", hjust=0.5),
        plot_subtitle    = element_text(size=10.5, color="#555555", hjust=0.5),
        axis_text_x      = element_text(angle=40, hjust=1, size=9.5),
        axis_text_y      = element_text(size=9.5),
        axis_title_y     = element_text(size=11),
        axis_line        = element_line(color="#cccccc", size=0.5),
        axis_ticks       = element_blank(),
        panel_grid_major_x = element_blank(),
        panel_grid_major_y = element_line(color="#e8e8e8", size=0.4),
        panel_grid_minor   = element_blank(),
        panel_background   = element_blank(),
        plot_background    = element_blank(),
        plot_caption       = element_text(size=8, color="#999999", hjust=0.5),
    )
    + labs(
        caption=(
            "Sources: Wikipedia (Sherlock Holmes fandom page), "
            "Baker Street Irregulars official site, Sherlock Holmes Society of London"
        ),
    )
)

# ── Save ─────────────────────────────────────────────────────────────────────
img_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
scr_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
img_dir.mkdir(parents=True, exist_ok=True)
scr_dir.mkdir(parents=True, exist_ok=True)

png_path = img_dir / "sherlock-holmes-legacy_societies_membership.png"
script_path = scr_dir / "chart3_sherlock-holmes-legacy_societies_membership.py"

ggsave(p, str(png_path), dpi=150)

print(f"Chart saved to:  {png_path}")
print(f"Script saved to: {script_path}")
print(f"Dimensions: 1200×720 px at 150 DPI")
