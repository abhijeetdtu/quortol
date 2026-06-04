"""
Chart 2: Pages Crawled Per Referral
Horizontal bar chart with log scale showing how many pages AI platforms crawl
for every single referral (visitor) they send back to a publisher site.
Data from Cloudflare via SearchSignal 2026 benchmark.
lets-plot 4.9.0, 1200x720 px, 150 DPI, colorblind-safe.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "platform": pd.Categorical(
        ["Google", "ChatGPT", "Perplexity", "Claude"],
        categories=["Claude", "Perplexity", "ChatGPT", "Google"],
        ordered=True,
    ),
    "pages_per_referral": [5.4, 1091, 2500, 38066],
})

# Formatted labels for display on bars
df["label"] = df["pages_per_referral"].apply(
    lambda x: f"{x:,.0f}" if x >= 1000 else str(x)
)

# Position labels at the right end of each bar (multiplicative nudge for log scale)
df["label_x"] = df["pages_per_referral"] * 1.35

# ---------------------------------------------------------------------------
# Colorblind-safe palette (Wong / IBM palette)
# ---------------------------------------------------------------------------
palette = {
    "Google":     "#0072B2",   # Blue
    "ChatGPT":    "#E69F00",   # Orange
    "Perplexity": "#009E73",   # Green
    "Claude":     "#CC79A7",   # Pink
}

# ---------------------------------------------------------------------------
# Build chart
# ---------------------------------------------------------------------------
# Reference line annotation (place text next to Google's bar at the reference line)
annot_ref = pd.DataFrame({
    "platform": pd.Categorical(
        ["Google"], categories=["Claude", "Perplexity", "ChatGPT", "Google"],
        ordered=True,
    ),
    "ref_val": [7.0],       # horizontal position (log value, just right of ref line)
    "label":   ["Google baseline: 5.4"],
})

p = (
    ggplot(df, aes(x="platform", y="pages_per_referral", fill="platform"))
    # Bars
    + geom_bar(stat="identity", width=0.65)
    # Vertical reference line at Google's 5.4 (appears vertical after coord_flip)
    + geom_hline(
        yintercept=5.4, linetype="dashed",
        color="#0072B2", size=0.9, alpha=0.5
    )
    # Label for the reference line (placed near Google bar, horizontal=x pos, vertical=platform)
    + geom_text(
        data=annot_ref,
        mapping=aes(x="ref_val", y="platform", label="label"),
        color="#0072B2", size=8, fontface="italic",
        angle=0, hjust=0,
    )
    # Data labels on bars
    + geom_text(
        aes(x="platform", y="label_x", label="label"),
        color="#333333", size=10, fontface="bold",
        hjust=0,
    )
    # Log scale on horizontal (x after coord_flip)
    + scale_y_log10(
        breaks=[5, 10, 50, 100, 500, 1000, 5000, 10000, 50000],
        labels=["5", "10", "50", "100", "500", "1K", "5K", "10K", "50K"],
        expand=[0, 0],
    )
    # Color
    + scale_fill_manual(values=palette)
    # Flip to horizontal bars
    + coord_flip()
    # Labels & titles
    + labs(
        title="Pages Crawled Per Referral",
        subtitle=(
            "How many pages AI platforms consume for every visitor they send back  |  "
            "Source: Cloudflare 2025"
        ),
        x="",
        y="Pages crawled per referral (log scale)",
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title       =element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle    =element_text(size=12, color="#555555", hjust=0, margin=[0, 0, 20, 0]),
        axis_title_x     =element_text(size=12, margin=[10, 0, 0, 0]),
        axis_title_y     =element_blank(),
        axis_text_x      =element_text(size=11),
        axis_text_y      =element_text(size=13, face="bold"),
        legend_position  ="none",
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_blank(),
        panel_grid_minor_y=element_blank(),
        plot_margin      =[20, 20, 15, 15],
    )
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
img_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
img_dir.mkdir(parents=True, exist_ok=True)
img_path = img_dir / "the-citation-economy_crawl_ratio.png"

ggsave(p, str(img_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart saved to: {img_path}")
