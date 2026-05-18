import base64
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Chart 1: AT Elevation Profile — "The Spine of the East"
# ---------------------------------------------------------------------------
df1 = pd.DataFrame({
    "state": ["Georgia", "TN/NC", "Virginia", "West Virginia", "Maryland",
              "Pennsylvania", "New Jersey", "New York", "Connecticut",
              "Massachusetts", "Vermont", "New Hampshire", "Maine"],
    "climb":    [20407, 113904, 136323, 2455, 7296, 29960, 7697, 22569, 12317, 18758, 34532, 53182, 67280],
    "descent":  [-20396, -114476, -138409, -3299, -6358, -30857, -7600, -22567, -10941, -18209, -36459, -50615, -65000]
})

# Order: Georgia first (top), Maine last (bottom)
df1["state"] = pd.Categorical(df1["state"], categories=df1["state"].tolist(), ordered=True)

# Melt for grouped bars
df1_melt = df1.melt(id_vars=["state"], value_vars=["climb", "descent"],
                    var_name="direction", value_name="feet")

climb_color = "#2D6A4F"
descent_color = "#8B6F47"

p1 = (
    ggplot(df1_melt, aes(y="state", x="feet", fill="direction"))
    + geom_bar(stat="identity", width=0.7, alpha=0.9)
    + scale_fill_manual(values={"climb": climb_color, "descent": descent_color},
                        labels={"climb": "Climb (ft)", "descent": "Descent (ft)"})
    + geom_vline(xintercept=0, color="#333333", size=0.7)
)

# Add climb labels (right side of bars)
df1_climb = df1_melt[df1_melt["direction"] == "climb"].copy()
df1_climb["label"] = (df1_climb["feet"] / 1000).round(1).astype(str) + "k"
p1 = p1 + geom_text(aes(x="feet", label="label"), data=df1_climb,
                     hjust=-0.1, size=8, color="#2D6A4F")

# Add descent labels (left side of bars)
df1_desc = df1_melt[df1_melt["direction"] == "descent"].copy()
df1_desc["label"] = (df1_desc["feet"].abs() / 1000).round(1).astype(str) + "k"
p1 = p1 + geom_text(aes(x="feet", label="label"), data=df1_desc,
                     hjust=1.1, size=8, color="#8B6F47")

p1 = p1 + labs(
    title="The Spine of the East: Elevation Gain and Loss by State",
    subtitle="Cumulative climb: 526,664 ft \u2014 equivalent to climbing Everest nearly 18 times",
    x="Feet",
    y=None,
    fill=None
) + theme_minimal() + theme(
    axis_text_y=element_text(size=10, hjust=1, face="bold"),
    axis_text_x=element_text(size=8),
    axis_title_x=element_text(size=9),
    plot_title=element_text(size=14, face="bold", color="#1a1a1a"),
    plot_subtitle=element_text(size=9, color="#555555"),
    legend_position="top",
    legend_direction="horizontal",
    legend_text=element_text(size=9),
    panel_grid_major_x=element_line(color="#e0e0e0", size=0.3),
    panel_grid_major_y=element_blank(),
    panel_grid_minor_x=element_blank(),
    plot_margin=[20, 50, 10, 10]
) + scale_x_continuous(labels=lambda x: f"{abs(x/1000):.0f}k",
                       expand=[0.05, 0.15])

p1.to_png("chart1_elevation.png", w=12, h=8.4, unit="in", dpi=200)

# Encode
png_data = Path("chart1_elevation.png").read_bytes()
encoded = base64.b64encode(png_data).decode("utf-8")
data_uri = f"data:image/png;base64,{encoded}"

Path("chart1_b64.txt").write_text(data_uri, encoding="utf-8")
print("Chart 1 done")
print(f"Base64 length: {len(encoded)} chars")
