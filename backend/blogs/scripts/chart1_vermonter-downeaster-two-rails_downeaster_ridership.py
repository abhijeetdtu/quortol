#!/usr/bin/env python3
"""
Chart 1: Downeaster Annual Ridership (FY03-FY25)
Line chart with area fill — magazine-style.

Output: 1200x720 px PNG at 150 DPI, lets-plot.
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────
df = pd.DataFrame({
    "year": [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012,
             2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022,
             2023, 2024, 2025],
    "ridership": [223287, 221252, 212955, 291734, 298487, 388352, 407288,
                  406273, 444809, 471237, 497483, 520790, 438364, 500100,
                  526100, 535100, 552500, 268100, 204100, 444684, 542639,
                  591948, 549120],
})

# ── Axis helpers ──────────────────────────────────────────────────────
x_breaks = list(range(2003, 2026, 2))
x_labels = [f"FY{str(y)[2:]}" for y in x_breaks]

y_breaks = [0, 200_000, 400_000, 600_000]
y_labels = ["0", "200K", "400K", "600K"]

# ── Build plot ────────────────────────────────────────────────────────
p = (
    ggplot(df, aes(x="year", y="ridership"))
    # Area fill
    + geom_area(fill="#AABBCC", alpha=0.3)
    # Line
    + geom_line(color="#4477AA", size=1.3)
    # Markers
    + geom_point(color="#4477AA", size=2.8)
    # ── Milestone vertical lines ──
    + geom_vline(xintercept=2012.5, linetype="dashed",
                 color="#888888", size=0.5)
    + geom_vline(xintercept=2020.25, linetype="dashed",
                 color="#888888", size=0.5)
    + geom_vline(xintercept=2024.5, linetype="dashed",
                 color="#888888", size=0.5)
    # ── Segment connectors from line to labels ──
    + geom_segment(x=2012.5, xend=2012.5, y=552_000, yend=630_000,
                   linetype="dotted", color="#888888", size=0.3)
    + geom_segment(x=2020.25, xend=2020.25, y=250_000, yend=630_000,
                   linetype="dotted", color="#888888", size=0.3)
    + geom_segment(x=2024.5, xend=2024.5, y=575_000, yend=630_000,
                   linetype="dotted", color="#888888", size=0.3)
    # ── Milestone labels ──
    + geom_text(x=2012.5, y=640_000, label="Brunswick\nExtension",
                hjust=0.5, vjust=0, size=8, color="#555555")
    + geom_text(x=2020.25, y=640_000, label="COVID-19",
                hjust=0.5, vjust=0, size=8, color="#555555")
    + geom_text(x=2024.5, y=640_000, label="Record:\n598,426",
                hjust=0.5, vjust=0, size=8, color="#555555")
    # ── Scales ──
    + scale_x_continuous(breaks=x_breaks, labels=x_labels)
    + scale_y_continuous(breaks=y_breaks, labels=y_labels,
                         limits=[0, 700_000], expand=[0, 0, 0.02, 5000])
    # ── Labels ──
    + ggtitle(
        "Downeaster Annual Ridership, FY2003\u2013FY2025",
        subtitle="From Boston to Brunswick \u2014 "
                 "10.6 million passengers since 2001",
    )
    + xlab("Fiscal Year")
    + ylab("Annual Ridership")
    + labs(caption="Sources: NNEPRA, Amtrak, Rail Passengers Association")
    # ── Theme ──
    + theme_minimal()
    + theme(
        plot_title=element_text(size=16, face="bold"),
        plot_subtitle=element_text(size=11, color="#555555"),
        plot_caption=element_text(size=8, color="#888888"),
        axis_title_x=element_text(size=10, color="#555555"),
        axis_title_y=element_text(size=10, color="#555555"),
        axis_text_x=element_text(size=9, angle=0, hjust=0.5),
        axis_text_y=element_text(size=9),
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#EEEEEE", size=0.3),
        panel_grid_minor=element_blank(),
        axis_line=element_line(color="#CCCCCC", size=0.3),
        plot_margin=[20, 25, 15, 20],
    )
)

# ── Save ──────────────────────────────────────────────────────────────
out_path = ("/home/pi/Documents/code/quortol/backend/blogs/images/"
            "vermonter-downeaster-two-rails_downeaster_ridership.png")
ggsave(p, out_path, w=8, h=4.8, unit="in", dpi=150)
print(f"Chart 1 saved: {out_path}")
