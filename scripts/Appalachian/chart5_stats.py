import base64
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Chart 5: The AT by the Numbers  —  Stat Card Grid
# ---------------------------------------------------------------------------
stats = [
    ("2,197.9", "Total Miles", 0, 0),
    ("464,500 ft", "Cumulative\nElevation Gain", 0, 1),
    ("14", "States\nTraversed", 0, 2),
    ("~5 million", "Estimated Steps\nfor a Thru-Hike", 0, 3),
    
    ("16.9M", "Annual Recreation\nVisits", 1, 0),
    ("~3,000", "Annual Thru-Hike\nAttempts", 1, 1),
    ("25\u201333%", "Completion\nRate", 1, 2),
    ("176,504", "Volunteer Hours\nper Year", 1, 3),
    
    ("250+", "Three-Sided\nShelters", 2, 0),
    ("30", "Trail-Maintaining\nClubs", 2, 1),
    ("30.4 lbs", "Average Pack\nWeight", 2, 2),
    ("152 days", "Average Thru-Hike\nDuration", 2, 3),
]

df5 = pd.DataFrame(stats, columns=["value", "label", "row", "col"])
df5["x"] = df5["col"] * 2.5 + 1.25
df5["y"] = -(df5["row"] * 2.5 + 1.25)  # negative so row 0 is at top

# Also create a data frame for the background rectangles
df5["xmin"] = df5["x"] - 0.95
df5["xmax"] = df5["x"] + 0.95
df5["ymin"] = df5["y"] - 0.95
df5["ymax"] = df5["y"] + 0.95

# Create the blank canvas
canvas = pd.DataFrame({"x": [0, 10], "y": [-7.5, 0]})

deep_green = "#2D6A4F"
light_bg = "#F5F5F0"

p5 = (
    ggplot(canvas, aes(x="x", y="y"))
    + geom_blank()
    # Card backgrounds (light green tint)
    + geom_rect(aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax"),
                data=df5, fill=deep_green, alpha=0.07)
    # Card borders
    + geom_rect(aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax"),
                data=df5, color=deep_green, size=0.4, alpha=0.3, fill=None)
    # Large value text
    + geom_text(aes(x="x", y="y+0.3", label="value"), data=df5,
                size=13, color="#1a1a1a", face="bold")
    # Label text
    + geom_text(aes(x="x", y="y-0.35", label="label"), data=df5,
                size=6.5, color="#555555")
    + xlim(0, 10)
    + ylim(-7.5, 0)
    + labs(
        title="The Appalachian Trail by the Numbers",
        subtitle="Key statistics from the Appalachian Trail Conservancy and partner organizations"
    )
    + theme_void()
    + theme(
        plot_margin=[15, 15, 10, 15],
        plot_background=element_rect(fill=light_bg, color=None),
        plot_title=element_text(size=16, face="bold", color="#1a1a1a",
                                hjust=0.5, margin=[0, 0, 5, 0]),
        plot_subtitle=element_text(size=9, color="#555555",
                                    hjust=0.5, margin=[0, 0, 15, 0])
    )
)

p5.to_png("chart5_stats.png", w=12, h=8, unit="in", dpi=200)

# Encode
png_data = Path("chart5_stats.png").read_bytes()
encoded = base64.b64encode(png_data).decode("utf-8")
data_uri = f"data:image/png;base64,{encoded}"

Path("chart5_b64.txt").write_text(data_uri, encoding="utf-8")
print("Chart 5 done")
print(f"Base64 length: {len(encoded)} chars")
