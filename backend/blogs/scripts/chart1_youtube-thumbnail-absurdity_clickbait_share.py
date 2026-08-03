#!/usr/bin/env python3
"""
chart1_youtube-thumbnail-absurdity_clickbait_share.py
=====================================================
Single horizontal 100%-stacked bar showing the share of clickbait vs
non-clickbait headlines in the Webis Clickbait Corpus (Webis-Clickbait-17).

Magazine-style companion visual for the "YouTube thumbnail/title clickbait
economics" article.

Output: 1200x720 px PNG at 150 DPI, colorblind-safe (Okabe-Ito palette).
"""

from pathlib import Path

import pandas as pd
from lets_plot import *
from PIL import Image

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Output path
# ---------------------------------------------------------------------------
IMAGE_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
image_path = IMAGE_DIR / "youtube-thumbnail-absurdity_clickbait_share.png"

# ---------------------------------------------------------------------------
# Data -- exact values from Webis-Clickbait-17 (38,517 headlines)
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "category": ["Not clickbait", "Clickbait"],
    "count":    [29241, 9276],
    "pct":      [75.9, 24.1],
})

# Single horizontal 100% stack drawn natively (NO coord_flip): the "Not
# clickbait" segment sits on the left, "Clickbait" on the right.
df["segment"] = "All 38,517 posts"
df["cum"] = df["pct"].cumsum()            # 75.9, 100.0
df["mid"] = df["cum"] - df["pct"] / 2.0   # 37.95, 87.95

# Inside-bar labels: SINGLE LINE per segment (no newlines -- avoids the
# multi-line + lineheight overlap bug), percentage followed by count.
df["bar_label"] = df.apply(
    lambda r: f"{r['pct']:.1f}% \u00b7 {r['count']:,}", axis=1
)

# Per-segment text colour (white on blue, dark on orange for contrast)
df["label_color"] = df["category"].map(
    {"Not clickbait": "#FFFFFF", "Clickbait": "#3B2F00"}
)

# ---------------------------------------------------------------------------
# Okabe-Ito palette
# ---------------------------------------------------------------------------
OKABE_BLUE = "#0072B2"    # blue
OKABE_ORANGE = "#E69F00"  # orange

# ---------------------------------------------------------------------------
# Build the chart
# ---------------------------------------------------------------------------
p = (
    ggplot(df)
    # 100% stacked bar laid out horizontally WITHOUT coord_flip:
    # y = single category, x = pct, segments run left -> right.
    + geom_bar(
        aes(y="segment", x="pct", fill="category"),
        stat="identity",
        width=0.45,
        position="stack",
    )
    # Percentage + count label centred inside each segment
    + geom_text(
        aes(x="mid", y="segment", label="bar_label", color="label_color"),
        size=8.5,
        hjust=0.5,
        vjust=0.5,
        show_legend=False,
    )
    + scale_fill_manual(
        values={"Not clickbait": OKABE_BLUE, "Clickbait": OKABE_ORANGE},
        name=None,
    )
    + scale_color_identity()
    + scale_x_continuous(limits=[0, 100], expand=[0, 0])
    + labs(
        title="One in Four Headlines Is Clickbait",
        subtitle=(
            "Webis Clickbait Corpus (2017) \u2014 38,517 posts, each linking to a "
            "news headline, from 27 US news publishers, Nov 2016\u2013Jun 2017, each "
            "rated by five annotators on a four-point scale; majority vote shown."
        ),
        x="",
        y="",
        caption="Source: Webis-Clickbait-17 (webis.de; DOI 10.5281/zenodo.5530410)",
    )
    + theme_minimal()
    + theme(
        # White background, no grid or axes (single-bar chart)
        plot_background=element_rect(fill="#FFFFFF", color=None),
        panel_background=element_rect(fill="#FFFFFF", color=None),
        panel_grid=element_blank(),
        axis_line=element_blank(),
        axis_text=element_blank(),
        axis_ticks=element_blank(),
        # Title
        plot_title=element_text(
            size=24, face="bold", hjust=0, margin=[0, 0, 8, 0]
        ),
        # Subtitle / caption
        plot_subtitle=element_text(
            size=11.5, color="#555555", hjust=0, margin=[0, 0, 22, 0],
        ),
        plot_caption=element_text(
            size=8.5, color="#777777", hjust=0, margin=[18, 0, 0, 0]
        ),
        # Legend
        legend_position="right",
        legend_title=element_blank(),
        legend_text=element_text(size=11.5),
        plot_margin=[15, 25, 5, 5],
    )
)

# ---------------------------------------------------------------------------
# Save -- 8 in x 4.8 in @ 150 DPI = 1200 x 720 px
# ---------------------------------------------------------------------------
ggsave(p, str(image_path), w=1200, h=720, dpi=150, unit="px")

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
img = Image.open(image_path)
print(f"Chart saved: {image_path}")
print(f"Dimensions: {img.width}x{img.height} px "
      f"({image_path.stat().st_size / 1024:.1f} KB)")
assert img.size == (1200, 720)
print("Done.")
