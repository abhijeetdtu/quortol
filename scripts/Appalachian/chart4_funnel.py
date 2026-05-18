import base64
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Chart 4: Thru-Hiker Funnel — "One in Four"
# ---------------------------------------------------------------------------
df4 = pd.DataFrame({
    "stage": ["Register Interest", "Start at Springer\nMountain, GA", "Reach Harpers\nFerry, WV", "Reach Katahdin,\nME"],
    "count": [3000, 2500, 1250, 800],
    "pct": ["100%", "~83%", "~42%", "~27%"]
})

# Create numeric y positions (1-indexed from top)
df4["y_pos"] = [4, 3, 2, 1]
df4["xmin"] = -(df4["count"] / 2)
df4["xmax"] = df4["count"] / 2
df4["ymin"] = df4["y_pos"] - 0.35
df4["ymax"] = df4["y_pos"] + 0.35

# Create stage labels for y-axis tick marks
stage_labels = dict(zip(df4["y_pos"], df4["stage"]))

# Segment connectors between bars
connectors = pd.DataFrame({
    "y_start": [3.35, 2.35, 1.35],
    "y_end":   [3.65, 2.65, 1.65],
    "x_start_left": [-1250, -625, -400],
    "x_end_left":   [-1250, -625, -400],
    "x_start_right": [1250, 625, 400],
    "x_end_right":   [1250, 625, 400],
})

# Funnel chart as horizontal bars centered at x=0
p4 = (
    ggplot(df4)
    + geom_rect(aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax", fill="count"),
                data=df4, alpha=0.9)
    # Labels: count on top, percentage below
    + geom_text(aes(x=0, y="y_pos", label="count"), data=df4,
                size=10, color="white", face="bold", vjust=-0.8)
    + geom_text(aes(x=0, y="y_pos", label="pct"), data=df4,
                size=8, color="white", alpha=0.85, vjust=1.8)
    # Gradient: warm at top, cool at bottom
    + scale_fill_gradient(low="#4A6FA5", high="#D4933A", guide="none")
    + scale_y_continuous(breaks=list(stage_labels.keys()),
                         labels=list(stage_labels.values()),
                         expand=[0.1, 0.1])
    + scale_x_continuous(expand=[0.05, 0.05])
    + labs(
        title="One in Four: The AT Thru-Hiker Funnel",
        subtitle="Of ~3,000 who register intent each year, roughly 25\u201333% complete the full 2,197.9 miles",
        x=None,
        y=None
    )
    + theme_minimal()
    + theme(
        axis_text_y=element_text(size=9, hjust=1, face="bold"),
        axis_text_x=element_blank(),
        axis_title_x=element_blank(),
        axis_title_y=element_blank(),
        plot_title=element_text(size=14, face="bold", color="#1a1a1a"),
        plot_subtitle=element_text(size=9, color="#555555"),
        panel_grid_major=element_blank(),
        panel_grid_minor=element_blank(),
        panel_background=element_blank(),
        plot_margin=[20, 20, 10, 20]
    )
)

p4.to_png("chart4_funnel.png", w=9, h=5.5, unit="in", dpi=200)

# Encode
png_data = Path("chart4_funnel.png").read_bytes()
encoded = base64.b64encode(png_data).decode("utf-8")
data_uri = f"data:image/png;base64,{encoded}"

Path("chart4_b64.txt").write_text(data_uri, encoding="utf-8")
print("Chart 4 done")
print(f"Base64 length: {len(encoded)} chars")
