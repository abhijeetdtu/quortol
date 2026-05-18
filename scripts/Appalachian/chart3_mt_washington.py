import base64
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Chart 3: Mount Washington Weather Extremes
# ---------------------------------------------------------------------------
df3 = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "avg_temp_f": [5.8, 5.9, 12.9, 23.7, 36.3, 45.5, 49.9, 48.7, 43.1, 31.3, 20.8, 11.8],
    "snow_inches": [41.6, 43.3, 46.2, 33.1, 12.9, 1.3, 0.0, 0.1, 1.2, 19.0, 35.6, 47.7]
})

df3["month"] = pd.Categorical(df3["month"], categories=df3["month"].tolist(), ordered=True)

p3 = (
    ggplot(df3, aes(x="month"))
    # Snowfall bars
    + geom_bar(aes(y="snow_inches", fill="Snowfall (in)"),
               stat="identity", width=0.65, alpha=0.85)
    # Temperature line
    + geom_line(aes(y="avg_temp_f", color="Avg Temp (\u00b0F)", group=1),
                size=1.5)
    + geom_point(aes(y="avg_temp_f", color="Avg Temp (\u00b0F)"),
                 size=3)
    # Manual scales with names for legend
    + scale_fill_manual(values={"Snowfall (in)": "#4A7FB5"},
                        name="")
    + scale_color_manual(values={"Avg Temp (\u00b0F)": "#C0392B"},
                         name="")
    # Labels
    + labs(
        title="Mount Washington: The Worst Weather on Earth",
        subtitle="Average annual temperature: 28.0\u00b0F | Average annual snowfall: 281.8 inches | Highest recorded wind gust: 231 mph",
        x=None,
        y="Inches / \u00b0F"
    )
    + theme_minimal()
    + theme(
        axis_text_x=element_text(size=9, hjust=0.5),
        axis_text_y=element_text(size=8),
        axis_title_y=element_text(size=9),
        axis_title_x=element_blank(),
        plot_title=element_text(size=14, face="bold", color="#1a1a1a"),
        plot_subtitle=element_text(size=8.5, color="#555555"),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=8.5),
        panel_grid_major=element_line(color="#e0e0e0", size=0.3),
        panel_grid_minor=element_blank(),
        plot_margin=[20, 20, 10, 10]
    )
)

# Annotations for records
# We'll add text annotations directly
record_data = pd.DataFrame({
    "label": [
        "Record low:\n-47\u00b0F",
        "Record wind:\n231 mph",
        "Record wind chill:\n-108\u00b0F"
    ],
    "x": ["Feb", "Apr", "Jan"],
    "y": [43, 50, 55]
})

p3 = p3 + geom_text(aes(x="x", y="y", label="label"), data=record_data,
                     size=6.5, color="#555555", hjust=0.5, vjust=0)

p3.to_png("chart3_mt_washington.png", w=11, h=6.5, unit="in", dpi=200)

# Encode
png_data = Path("chart3_mt_washington.png").read_bytes()
encoded = base64.b64encode(png_data).decode("utf-8")
data_uri = f"data:image/png;base64,{encoded}"

Path("chart3_b64.txt").write_text(data_uri, encoding="utf-8")
print("Chart 3 done")
print(f"Base64 length: {len(encoded)} chars")
