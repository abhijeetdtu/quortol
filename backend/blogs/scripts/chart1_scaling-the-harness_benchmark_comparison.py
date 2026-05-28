"""
AI Agent Framework Benchmarks (2026)
=====================================
Grouped bar chart comparing LangGraph, CrewAI, and AutoGen across
four key performance metrics (latency, cost, tokens, success rate).

Source: AI Agent Engineering, March 2026
  https://ai-agent-engineering.org/news/ai-agent-frameworks-benchmarked-langchain-vs-crewai-vs-autogen-in-2026

Output: backend/blogs/images/scaling-the-harness_benchmark_comparison.png (1200×720 px, 150 DPI)
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Okabe-Ito colorblind-safe palette (first 3 colours for 3 frameworks)
# ---------------------------------------------------------------------------
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73"]

# ---------------------------------------------------------------------------
# Data — wide format
# ---------------------------------------------------------------------------
df_wide = pd.DataFrame({
    "Framework": ["LangGraph", "CrewAI", "AutoGen"],
    "Latency (ms)":          [350,  1400,  3500],
    "Cost per query ($)":    [0.18, 0.12,  0.35],
    "Tokens per query":      [12400, 14000, 24200],
    "Success rate (%)":      [94,   89,    85],
})

# ---------------------------------------------------------------------------
# Melt to long format — one row per (Framework, Metric) combination
# ---------------------------------------------------------------------------
df_long = df_wide.melt(
    id_vars=["Framework"],
    var_name="Metric",
    value_name="Value",
)

# Guarantee a consistent ordering for the facets
metric_order = ["Latency (ms)", "Cost per query ($)", "Tokens per query", "Success rate (%)"]
df_long["Metric"] = pd.Categorical(df_long["Metric"], categories=metric_order, ordered=True)

# Build formatted label strings for bar labels
def fmt_label(row):
    v = row["Value"]
    m = row["Metric"]
    if "Cost" in m:
        return f"${v:.2f}"
    elif "Latency" in m:
        return f"{v:.0f} ms"
    elif "Tokens" in m:
        return f"{v:,.0f}"
    elif "Success" in m:
        return f"{v:.0f}%"
    return str(v)

df_long["Label"] = df_long.apply(fmt_label, axis=1)

# ---------------------------------------------------------------------------
# Build the plot
# ---------------------------------------------------------------------------

# Each facet shows one metric; within each facet the three frameworks are
# compared side-by-side.  'scales="free"' gives each metric its own y-axis
# range so that small-cost and high-token scales are each readable.

p = (
    ggplot(df_long, aes(x="Framework", y="Value", fill="Framework"))
    + geom_bar(stat="identity", width=0.7, color="white", size=0.3)
    + geom_text(
        aes(label="Label"),
        va="bottom",
        size=9,
        color="#444444",
    )
    + scale_fill_manual(values=OKABE_ITO, name="")
    + facet_wrap(facets="Metric", scales="free", ncol=2)
    + labs(
        title="AI Agent Framework Benchmarks (2026)",
        subtitle="LangGraph · CrewAI · AutoGen  —  Latency, Cost, Tokens & Success Rate",
        caption="Source: AI Agent Engineering, 2026 — ai-agent-engineering.org/news/ai-agent-frameworks-benchmarked-langchain-vs-crewai-vs-autogen-in-2026",
    )
    + ggsize(1200, 720)
    + theme(
        # White background all around
        panel_background=element_rect(fill="white", color=None),
        plot_background=element_rect(fill="white"),
        # Grid — horizontal only, light
        panel_grid_major_x=element_blank(),
        panel_grid_major_y=element_line(color="#eeeeee", size=0.35),
        panel_grid_minor=element_blank(),
        # Axes
        axis_title_x=element_blank(),
        axis_title_y=element_blank(),
        axis_line_x=element_line(color="#cccccc", size=0.4),
        axis_line_y=element_line(color="#cccccc", size=0.4),
        axis_ticks=element_blank(),
        axis_text_x=element_text(size=10, color="#444444"),
        axis_text_y=element_text(size=9, color="#777777"),
        # Legend
        legend_position="bottom",
        legend_text=element_text(size=10),
        legend_spacing=10,
        # Titles
        plot_title=element_text(size=18, face="bold", color="#222222", hjust=0.5, margin=[0, 0, 2, 0]),
        plot_subtitle=element_text(size=10, color="#777777", hjust=0.5, margin=[0, 0, 12, 0]),
        # Facet strip labels
        strip_text=element_text(size=11, face="bold", color="#444444"),
        strip_background=element_rect(fill="#f5f5f5", color="#dddddd", size=0.5),
        # Caption (source line at bottom)
        plot_caption=element_text(size=7, color="#aaaaaa", hjust=0),
        # Margins: top, right, bottom, left
        plot_margin=[15, 20, 10, 20],
    )
)

# ---------------------------------------------------------------------------
# Save — 1200 × 720 px @ 150 DPI
# ---------------------------------------------------------------------------
OUTPUT_PATH = "/home/pi/Documents/code/quortol/backend/blogs/images/scaling-the-harness_benchmark_comparison.png"

p.to_png(OUTPUT_PATH, dpi=150, w=1200, h=720, unit="px")

print(f"Chart saved -> {OUTPUT_PATH}")
print(f"Dimensions: 1200 × 720 px @ 150 DPI")
