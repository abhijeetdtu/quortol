import base64
import pandas as pd
from lets_plot import *
from pathlib import Path

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Chart 2: Fatalities by Cause — "The Grim Arithmetic"
# ---------------------------------------------------------------------------
df2 = pd.DataFrame({
    "cause": ["Accidents (falls, vehicle,\ntrespasser)", "Overexertion\n(heart attack, heat\nstroke, dehydration)",
              "Medical conditions", "Wildlife", "Weather-related"],
    "percentage": [60, 20, 10, 5, 5]
})

df2["cause"] = pd.Categorical(df2["cause"], categories=df2["cause"].tolist(), ordered=True)

p2 = (
    ggplot(df2, aes(y="cause", x="percentage"))
    + geom_bar(stat="identity", width=0.65, fill="#4A4A4A", alpha=0.88)
    + geom_text(aes(label="percentage"), hjust=-0.3, size=9, color="#333333")
    + labs(
        title="Causes of Death on the Appalachian Trail",
        subtitle="Approximately 200 fatalities since 1930 \u2014 accidents account for 60%",
        x="Percentage of Fatalities (%)"
    )
    + theme_minimal()
    + theme(
        axis_text_y=element_text(size=9, hjust=1),
        axis_text_x=element_text(size=8),
        axis_title_x=element_text(size=9),
        axis_title_y=element_blank(),
        plot_title=element_text(size=14, face="bold", color="#1a1a1a"),
        plot_subtitle=element_text(size=9, color="#555555"),
        panel_grid_major_x=element_line(color="#e0e0e0", size=0.3),
        panel_grid_major_y=element_blank(),
        panel_grid_minor_x=element_blank(),
        plot_margin=[20, 50, 10, 10]
    )
)

p2.to_png("chart2_fatalities.png", w=10, h=5.5, unit="in", dpi=200)

# Encode
png_data = Path("chart2_fatalities.png").read_bytes()
encoded = base64.b64encode(png_data).decode("utf-8")
data_uri = f"data:image/png;base64,{encoded}"

Path("chart2_b64.txt").write_text(data_uri, encoding="utf-8")
print("Chart 2 done")
print(f"Base64 length: {len(encoded)} chars")
