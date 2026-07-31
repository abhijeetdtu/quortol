#!/usr/bin/env python3
"""
Chart: Telegraph Line Expansion in British India, 1850–1857

Horizontal bar chart showing the growth of the electric telegraph network
from experimental line to full operational network at the outbreak of the
Indian Rebellion of 1857.

Uses lets-plot for visualization.
"""

import base64
from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────

df = pd.DataFrame({
    "year": ["1850", "1853", "1854", "1855", "1857"],
    "miles": [30, 30, 800, 2000, 4555],
    "milestone": [
        "Experimental line Calcutta–Diamond Harbour",
        "Dalhousie authorizes full network",
        "Calcutta–Agra main line completed",
        "Connections to Bombay and Madras operational",
        "Full network at outbreak of rebellion",
    ],
})

# Keep chronological order for y-axis display
df["year"] = pd.Categorical(df["year"], categories=df["year"], ordered=True)

# ── Color palette ──────────────────────────────────────────────────────────────
# Colorblind-safe sequential teal palette (light → dark as mileage increases)
TEAL_LIGHT = "#C2F0F0"
TEAL_DARK = "#0A4D4D"

# ── Chart ─────────────────────────────────────────────────────────────────────

p = (
    ggplot(df, aes(x="miles", y="year"))
    + geom_bar(
        aes(fill="miles"),
        stat="identity",
        width=0.55,
        color="#FFFFFF",
        size=0.3,
    )
    # Milestone annotations to the right of each bar
    + geom_text(
        aes(label="milestone"),
        hjust=0,
        nudge_x=65,
        size=9,
        family="Liberation Sans",
        color="#333333",
    )
    # Sequential fill: lighter for smaller values, darker for larger
    + scale_fill_gradient(low=TEAL_LIGHT, high=TEAL_DARK)
    # X-axis: leave room for annotations
    + scale_x_continuous(
        limits=[0, 6200],
        breaks=[0, 1000, 2000, 3000, 4000, 5000],
        expand=[0, 50],
    )
    # Labels
    + ggtitle(
        "The Accursed String: Telegraph Line Expansion in British India, 1850–1857"
    )
    + xlab("Miles of Telegraph Wire")
    + ylab("")
    # Clean professional theme
    + theme_minimal()
    + theme(
        # White background
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
        # Subtle vertical gridlines only
        panel_grid_major_x=element_line(color="#E8E8E8", size=0.4),
        panel_grid_major_y=element_blank(),
        panel_grid_minor=element_blank(),
        # Axis styling
        axis_line=element_blank(),
        axis_ticks=element_blank(),
        axis_text_y=element_text(size=12, family="Liberation Sans", color="#333333"),
        axis_text_x=element_text(size=10, family="Liberation Sans", color="#666666"),
        axis_title_x=element_text(size=11, family="Liberation Sans", color="#555555"),
        # Title
        plot_title=element_text(
            size=15, family="Liberation Sans", face="bold", color="#1A1A1A", hjust=0
        ),
        # No legend
        legend_position="none",
        # Margins [top, right, bottom, left]
        plot_margin=[16, 30, 16, 10],
        # Bottom caption area
        plot_caption=element_text(
            size=8, family="Liberation Sans", color="#999999", hjust=0
        ),
    )
    + ggsize(width=1200, height=720)
    # Source line at bottom via caption
    + labs(
        caption="Sources: PK Porthcurno Telegraph Museum; USI Journal"
    )
)

# ── Save images & script ──────────────────────────────────────────────────────

images_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
scripts_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
images_dir.mkdir(parents=True, exist_ok=True)
scripts_dir.mkdir(parents=True, exist_ok=True)

png_path = images_dir / "telegraph-indian-mutiny-1857_expansion.png"
html_path = images_dir / "telegraph-indian-mutiny-1857_expansion.html"
md_path = images_dir / "telegraph-indian-mutiny-1857_expansion.md"
script_path = scripts_dir / "chart1_telegraph-indian-mutiny-1857_expansion.py"

# Save interactive HTML
ggsave(p, str(html_path))
print(f"✓ HTML saved: {html_path}")

# Save high-DPI PNG via to_png (lets-plot >= 4.3)
p.to_png(
    path=str(png_path),
    scale=2,        # 2× for sharp output at 150 DPI
    dpi=150,
)

# Verify
assert png_path.exists(), f"PNG not created: {png_path}"
file_size_kb = png_path.stat().st_size / 1024
print(f"✓ PNG saved:  {png_path} ({file_size_kb:.0f} KB)")

# ── Base64 Embed (for blog embedding) ─────────────────────────────────────────

encoded = base64.b64encode(png_path.read_bytes()).decode("utf-8")
data_uri = f"data:image/png;base64,{encoded}"

md_path.write_text(f"![Telegraph Expansion Chart]({data_uri})", encoding="utf-8")
print(f"✓ MD  saved:  {md_path}")
print(f"  Base64 length: {len(encoded):,} chars")

# ── Copy script to scripts directory ──────────────────────────────────────────
# (Script is already at the script path since we're writing it there)
print(f"✓ Script:     {script_path}")
print("✅ Done — all files created successfully.")
