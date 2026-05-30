#!/usr/bin/env python3
"""
Chart 2: How Long Buildings Last — A Comparison Across Eras
Horizontal bar chart of approximate building lifespans for different
construction technologies, sorted longest to shortest.

Sources: PNAS (2014), Science Advances (2023), American Mineralogist (2017),
         Bayliss et al. (2015)
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data — sorted from longest to shortest lifespan
# ---------------------------------------------------------------------------
data = {
    "Building": [
        "Roman marine concrete (harbor)",
        "Roman concrete (Pantheon)",
        "Medieval timber-frame house (England)",
        "Modern steel-frame skyscraper",
        "Modern Portland cement concrete structure",
        "Çatalhöyük mudbrick house",
    ],
    "Lifespan": [2000, 1900, 500, 100, 75, 50],
}

df = pd.DataFrame(data)

# Preserve display order: longest at top
df["Building"] = pd.Categorical(
    df["Building"],
    categories=df["Building"].tolist(),
    ordered=True,
)

# ---------------------------------------------------------------------------
# Build plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="Lifespan", y="Building", fill="Lifespan"))
    # Horizontal bars
    + geom_bar(stat="identity", width=0.65, color="white", size=0.3)
    # Data labels at the end of each bar
    + geom_text(
        aes(label="Lifespan"),
        hjust=-0.25,
        size=9.5,
        color="#222222",
    )
    # Sequential warm-to-cool gradient (warm = high, cool = low)
    + scale_fill_gradient(low="#4393C3", high="#D73027")
    # Make room for right-side labels
    + scale_x_continuous(limits=(0, 2400))
    # Labels
    + labs(
        title="How Long Buildings Last",
        subtitle="Approximate service life of construction technologies, in years",
        x="Years",
        y="",
        caption=(
            "Sources: PNAS (2014), Science Advances (2023), "
            "American Mineralogist (2017), Bayliss et al. (2015)"
        ),
    )
    # Theme
    + theme_classic()
    + theme(
        plot_title=element_text(size=16, hjust=0.5, face="bold"),
        plot_subtitle=element_text(size=12, hjust=0.5, color="#555555"),
        axis_text_y=element_text(size=9.5),
        axis_text_x=element_text(size=9),
        axis_title_x=element_text(size=11),
        plot_caption=element_text(size=8, color="#555555", hjust=0, face="italic"),
        panel_grid_major_x=element_line(color="#EEEEEE", size=0.3),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        axis_line=element_line(color="#CCCCCC"),
        # Colour legend is redundant because values are labelled directly
        legend_position="none",
    )
)

# ---------------------------------------------------------------------------
# Save — 1200 × 720 px at 150 DPI  →  8 × 4.8 inches
# ---------------------------------------------------------------------------
script_dir = Path(__file__).resolve().parent
out_dir = script_dir.parent / "images"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "house-that-built-us_lifespan.png"

ggsave(p, str(out_path), w=8, h=4.8, unit="in", dpi=150)

# Verify
if out_path.exists():
    print(f"Saved: {out_path}")
    print(f"  Size: {out_path.stat().st_size / 1024:.1f} KB")
else:
    print(f"ERROR: file was not created at {out_path}")
