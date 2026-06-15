"""
Chart: Lifetime Literary Earnings — Alcott vs. Contemporaries
Horizontal bar chart comparing 19th-century American authors' lifetime earnings.
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
df = pd.DataFrame({
    "author": ["Louisa May Alcott", "Henry James", "Walt Whitman"],
    "earnings": [200_000, 25_000, 10_000],
    "label": ["$200,000", "$25,000", "$10,000"],
})

# Assign colors — Alcott distinct, others muted
df["color_hex"] = ["#8B1A1A", "#888888", "#888888"]
df["label_color"] = ["white", "#444444", "#444444"]

# ── Chart ─────────────────────────────────────────────────────────────────────
# Sort so Alcott appears at top
df = df.sort_values("earnings", ascending=True).reset_index(drop=True)

p = (
    ggplot(df, aes(x="earnings", y="author"))
    + geom_bar(aes(fill="author"), stat="identity", width=0.6)
    + geom_text(
        aes(label="label", color="author"),
        hjust=1.05,            # nudge inside bar from right edge
        size=11,
    )
    # Manual fill + color scales
    + scale_fill_manual(
        values={
            "Louisa May Alcott": "#8B1A1A",
            "Henry James": "#888888",
            "Walt Whitman": "#888888",
        }
    )
    + scale_color_manual(
        values={
            "Louisa May Alcott": "white",
            "Henry James": "#444444",
            "Walt Whitman": "#444444",
        }
    )
    # Labels
    + ggtitle(
        "Lifetime Literary Earnings: Alcott and Her Contemporaries",
        subtitle=(
            "Louisa May Alcott earned eight times as much as Henry James "
            "and twenty times as much as Walt Whitman"
        ),
    )
    + xlab("Earnings (nominal USD)")
    + ylab("")
    + labs(
        caption="Source: ALA / The Journals of Louisa May Alcott"
    )
    # Theme & appearance
    + theme_minimal()
    + theme(
        plot_background=element_rect(fill="white", color=None),
        panel_background=element_rect(fill="white", color=None),
        panel_grid_major_x=element_blank(),
        panel_grid_minor_x=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0", size=0.4),
        axis_line_x=element_line(color="#CCCCCC", size=0.3),
        axis_ticks_x=element_line(color="#CCCCCC"),
        axis_text_y=element_text(size=12, hjust=1),
        axis_text_x=element_text(size=10),
        plot_title=element_text(size=16, face="bold"),
        plot_subtitle=element_text(size=11, color="#555555"),
        plot_caption=element_text(size=9, color="#888888", hjust=0),
        legend_position="none",
    )
    # Scales
    + scale_x_continuous(
        labels=["$0", "$50,000", "$100,000", "$150,000", "$200,000"],
        breaks=[0, 50_000, 100_000, 150_000, 200_000],
        expand=[0.02, 0.02],
    )
    + coord_cartesian()
)

# ── Save ──────────────────────────────────────────────────────────────────────
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "what-louisa-earned_earnings_comparison.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")

print(f"✅ Chart saved to {output_path}")
