"""Horizontal bar chart: Top AI Agent Frameworks by GitHub Stars (May 2026).

Uses lets-plot 4.9.0+ to produce a publication-style horizontal bar chart.
Saves to PNG at 1200×720 px, 150 DPI.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
data = {
    "Framework": [
        "n8n",
        "AutoGPT",
        "LangChain",
        "browser-use",
        "AutoGen (Microsoft)",
        "CrewAI",
        "LlamaIndex",
        "LangGraph",
        "smolagents (Hugging Face)",
        "OpenAI Agents SDK",
    ],
    "GitHub Stars": [
        187791,
        184295,
        136707,
        93857,
        58025,
        51380,
        49399,
        32027,
        27302,
        26290,
    ],
}

df = pd.DataFrame(data)

# Sort descending so the top bar (n8n) appears at the top of the horizontal chart
df = df.sort_values("GitHub Stars", ascending=True).reset_index(drop=True)

# Pre-compute formatted label for geom_text
df["Star Label"] = df["GitHub Stars"].apply(lambda x: f"{x:,}")

# ---------------------------------------------------------------------------
# 2. Styling constants
# ---------------------------------------------------------------------------
WIDTH, HEIGHT, DPI = 1200, 720, 150
OUTPUT_DIR = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
OUTPUT_PATH = OUTPUT_DIR / "scaling-the-harness_github_stars.png"

# Colorblind-safe palette – 10 distinct hues, perceptually uniform
# Based on the Wong / Tol colour schemes, adjusted for 10 categories
COLORS = [
    "#0072B2",  # blue
    "#D55E00",  # orange
    "#009E73",  # green
    "#CC79A7",  # pink
    "#56B4E9",  # sky blue
    "#E69F00",  # yellow-orange
    "#F0E442",  # yellow
    "#000000",  # black
    "#999999",  # grey
    "#882255",  # magenta
]

# Map each framework to a colour
color_map = {fw: COLORS[i] for i, fw in enumerate(df["Framework"])}

# ---------------------------------------------------------------------------
# 3. Build chart
# ---------------------------------------------------------------------------
LetsPlot.setup_html()

# Sort factor levels so the plot respects the sorted DataFrame order
df["Framework"] = pd.Categorical(df["Framework"], categories=df["Framework"], ordered=True)

p = (
    ggplot(df, aes(x="Framework", y="GitHub Stars"))
    + geom_bar(
        aes(fill="Framework"),
        stat="identity",
        width=0.75,
    )
    + scale_fill_manual(values=color_map, guide="none")  # no legend needed
    # Flip coordinates to make it horizontal
    + coord_flip()
    # Labels on the bars themselves, right-aligned to bar end
    + geom_text(
        aes(label="Star Label"),
        hjust=-0.1,
        size=12,
        color="#333333",
        family="sans-serif",
    )
    # Titles and labels
    + ggtitle("Top AI Agent Frameworks by GitHub Stars (May 2026)")
    + xlab("")
    + ylab("GitHub Stars")
    # Source note – rendered via labs(caption=...)
    + labs(caption="Source: Presenc AI, GitHub public API, May 2026")
    # Theme tweaks
    + theme_minimal()
    + theme(
        plot_title=element_text(size=22, hjust=0.5, face="bold"),
        axis_text_y=element_text(size=14, hjust=1),
        axis_text_x=element_text(size=13),
        axis_title_x=element_text(size=15),
        axis_title_y=element_text(size=15),
        plot_caption=element_text(size=11, color="#666666", hjust=1, margin=[10, 0, 0, 0]),
        plot_margin=[20, 50, 20, 20],
    )
    # Ensure bars don't get clipped by the label
    + scale_y_continuous(expand=[0.05, 0.15])
)

# ---------------------------------------------------------------------------
# 4. Save
# ---------------------------------------------------------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ggsave(p, str(OUTPUT_PATH.name), path=str(OUTPUT_DIR), w=WIDTH / DPI, h=HEIGHT / DPI, dpi=DPI, scale=1.0)

print(f"Chart saved to {OUTPUT_PATH}")
