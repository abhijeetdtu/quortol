"""
Chart 2: The Creativity Paradox — Individual Gains vs. Collective Narrowing
Horizontal bar chart comparing effect sizes from multiple peer-reviewed studies.
lets-plot 4.9.0, 1200×720 px, 150 DPI, colorblind-safe palette.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# --- Data ---
data = pd.DataFrame({
    "metric": [
        "Individual creative productivity (art)",
        "Artwork value (favorites per view)",
        "Story novelty (with 5 AI ideas)",
        "Story usefulness (with 5 AI ideas)",
        "Professional writing speed",
        "Professional writing quality",
        "Book releases (market-level)",
        "Story similarity to other AI stories",
        "AI-detected books (share of releases)",
    ],
    "pct_change": [25, 50, 8.1, 9.0, 40, 18, 200, 10.7, 60],
    "source": [
        "Zhou & Lee (2024)",
        "Zhou & Lee (2024)",
        "Doshi & Hauser (2024)",
        "Doshi & Hauser (2024)",
        "Noy & Zhang (2023)",
        "Noy & Zhang (2023)",
        "Reimers & Waldfogel (2026)",
        "Doshi & Hauser (2024)",
        "Reimers & Waldfogel (2026)",
    ],
    "category": [
        "individual", "individual", "individual", "individual",
        "individual", "individual", "individual",
        "collective", "collective",
    ],
})

# Sort descending by percentage so largest bars are at top in horizontal layout
data = data.sort_values("pct_change", ascending=True).reset_index(drop=True)
data["metric"] = pd.Categorical(data["metric"], categories=data["metric"].tolist(), ordered=True)

# Colorblind-safe palette
# Blue for individual/productivity gains, orange for collective/conformity metrics
color_map = {
    "individual": "#1f77b4",
    "collective": "#ff7f0e",
}

# Format label text with + sign and source
data["label"] = "+" + data["pct_change"].astype(str) + "%"

# --- Build chart ---
p = (
    ggplot(data, aes(x="metric", y="pct_change", fill="category"))
    + geom_bar(stat="identity", width=0.65, alpha=0.9)
    + geom_hline(yintercept=0, size=0.3, color="#333333")
    + scale_fill_manual(
        values=color_map,
        labels={"individual": "Individual / Productivity gains",
                "collective": "Collective narrowing / conformity"},
        name="",
    )
    + coord_flip()
    + labs(
        title="The Creativity Paradox: Individual Gains vs. Collective Narrowing",
        subtitle=(
            "Percentage change in creative output measures after AI tool adoption"
        ),
        x="",
        y="Percentage Change (%)",
        caption=(
            "Sources: Doshi & Hauser (2024), Zhou & Lee (2024), "
            "Noy & Zhang (2023), Reimers & Waldfogel (2026)"
        ),
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 4, 0]),
        plot_subtitle=element_text(size=12, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_y=element_blank(),
        axis_title_x=element_text(size=12, margin=[10, 0, 0, 0]),
        axis_text_x=element_text(size=11),
        axis_text_y=element_text(size=11),
        axis_ticks_y=element_blank(),
        plot_caption=element_text(size=9, color="#888888", hjust=0, margin=[12, 0, 0, 0]),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_x=element_line(color="#E0E0E0", size=0.4),
        plot_margin=[20, 20, 10, 10],
        legend_position="bottom",
        legend_text=element_text(size=10),
        legend_spacing=8,
    )
    # Value labels at end of each bar
    + geom_text(
        mapping=aes(label="label"),
        stat="identity",
        hjust=-0.1,
        size=10.5,
        color="#333333",
        fontface="bold",
    )
    # Source labels below value labels
    + geom_text(
        mapping=aes(label="source"),
        stat="identity",
        hjust=-0.1,
        size=7,
        color="#888888",
        vjust=2.8,
    )
    # Expand x-axis (now y after coord_flip) to fit labels
    + ylim(0, 250)
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "the-creativity-paradox_creativity_paradox.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart saved to: {output_path}")
