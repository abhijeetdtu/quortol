"""
Chart: Cognitive Behavioral Therapy — Evidence from 409 Trials
==============================================================
Compares CBT response/remission rates vs control conditions and
effect sizes (CBT vs control, CBT vs medication at 6–12 mo f/u).

Source: Cuijpers, P. et al. (2023). World Psychiatry, 22(1), 105-115.
DOI: 10.1002/wps.21069

Output: 1200×720 px, 150 DPI, PNG
"""

import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Build the data frame
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "measure": [
        "Response Rate", "Response Rate",
        "Remission Rate", "Remission Rate",
        "vs control", "vs medication\n(6\u201312 mo f/u)",
    ],
    "value": [42, 19, 36, 15, 0.79, 0.34],
    "panel": [
        "Short-term outcomes", "Short-term outcomes",
        "Short-term outcomes", "Short-term outcomes",
        "Effect size (g)", "Effect size (g)",
    ],
    "group": [
        "CBT", "Control",
        "CBT", "Control",
        "CBT", "CBT",
    ],
    "bar_label": [
        "42%", "19%",
        "36%", "15%",
        "g = 0.79", "g = 0.34",
    ],
})

df["measure"] = pd.Categorical(
    df["measure"],
    categories=["Response Rate", "Remission Rate",
                "vs control", "vs medication\n(6\u201312 mo f/u)"],
    ordered=True,
)
df["panel"] = pd.Categorical(
    df["panel"],
    categories=["Short-term outcomes", "Effect size (g)"],
    ordered=True,
)

# ---------------------------------------------------------------------------
# Colorblind-safe palette (Wong, 2011)
# ---------------------------------------------------------------------------
cb_palette = {
    "CBT": "#0072B2",       # blue
    "Control": "#D55E00",   # vermillion / orange
}

# ---------------------------------------------------------------------------
# Build the plot
# ---------------------------------------------------------------------------
p = (
    ggplot(df, aes(x="measure", y="value", fill="group"))
    + geom_bar(stat="identity", position=position_dodge(0.75),
               width=0.65, alpha=0.90)
    + geom_text(
        aes(label="bar_label"),
        position=position_dodge(0.75),
        va="bottom", ha="center",
        size=10, color="#222222",
        family="sans-serif",
    )
    + facet_wrap(facets="panel", scales="free", ncol=2)
    + scale_fill_manual(values=cb_palette, name="")
    + scale_x_discrete()
    + labs(
        title="Cognitive Behavioral Therapy: Evidence from 409 Trials",
        subtitle=(
            "Response rates, remission rates, and effect sizes "
            "in the largest CBT meta-analysis (n = 52\u202f702)"
        ),
        x="",
        y="",
        caption="Source: Cuijpers et al. (2023), World Psychiatry",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold",
                                hjust=0.5, color="#111111"),
        plot_subtitle=element_text(size=11, hjust=0.5,
                                   color="#555555"),
        axis_text_x=element_text(size=10, color="#333333"),
        axis_text_y=element_text(size=9, color="#555555"),
        axis_ticks=element_blank(),
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#E0E0E0",
                                        size=0.4),
        panel_grid_minor=element_blank(),
        strip_text_x=element_text(size=12, face="bold",
                                  color="#222222"),
        strip_background=element_rect(fill="#F5F5F5",
                                      color=None,
                                      size=0),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=10, color="#333333"),
        plot_caption=element_text(size=9, color="#777777",
                                  hjust=0),
        plot_margin=[10, 20, 10, 20],
    )
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
png_path = output_dir / "stoicism-science_cbt_efficacy.png"

ggsave(p, str(png_path), dpi=150, w=1200, h=720, unit="px")

print(f"Chart saved to: {png_path}")
print("Done.")
