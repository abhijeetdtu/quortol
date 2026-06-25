"""
Chart 2: "Divinity: Original Sin 2 — Nine Years of Concurrent Players on Steam"
Area chart showing monthly average concurrent players from Sep 2017 through May 2026.
lets-plot 4.9.0, 1200x720 px, 150 DPI, Okabe-Ito colorblind-safe palette.
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path
from datetime import datetime

LetsPlot.setup_html()

# --- Data ---
csv_lines = """Month,Avg Players
Sep 2017,26288
Oct 2017,28002
Nov 2017,17969
Dec 2017,17247
Jan 2018,17693
Feb 2018,15504
Mar 2018,15706
Apr 2018,13665
May 2018,12331
Jun 2018,12167
Jul 2018,15160
Aug 2018,13963
Sep 2018,12529
Oct 2018,11339
Nov 2018,9385
Dec 2018,7747
Jan 2019,7507
Feb 2019,6191
Mar 2019,6943
Apr 2019,5676
May 2019,5347
Jun 2019,6479
Jul 2019,6759
Aug 2019,7037
Sep 2019,6666
Oct 2019,5381
Nov 2019,4706
Dec 2019,5121
Jan 2020,5284
Feb 2020,6154
Mar 2020,8323
Apr 2020,8969
May 2020,7089
Jun 2020,8037
Jul 2020,9841
Aug 2020,10875
Sep 2020,12058
Oct 2020,10828
Nov 2020,10842
Dec 2020,8957
Jan 2021,8647
Feb 2021,8103
Mar 2021,6734
Apr 2021,5571
May 2021,4933
Jun 2021,5111
Jul 2021,5374
Aug 2021,4873
Sep 2021,4545
Oct 2021,4437
Nov 2021,4164
Dec 2021,4340
Jan 2022,4448
Feb 2022,4081
Mar 2022,3550
Apr 2022,2982
May 2022,2760
Jun 2022,2781
Jul 2022,3038
Aug 2022,2667
Sep 2022,2534
Oct 2022,2424
Nov 2022,3060
Dec 2022,7993
Jan 2023,8686
Feb 2023,7146
Mar 2023,7927
Apr 2023,7927
May 2023,6536
Jun 2023,5963
Jul 2023,9192
Aug 2023,8228
Sep 2023,7085
Oct 2023,4838
Nov 2023,4100
Dec 2023,4872
Jan 2024,6125
Feb 2024,5345
Mar 2024,4887
Apr 2024,3785
May 2024,4254
Jun 2024,3596
Jul 2024,4491
Aug 2024,3786
Sep 2024,4649
Oct 2024,3479
Nov 2024,3344
Dec 2024,5047
Jan 2025,5529
Feb 2025,4913
Mar 2025,4431
Apr 2025,3582
May 2025,3199
Jun 2025,4154
Jul 2025,4088
Aug 2025,3574
Sep 2025,2942
Oct 2025,3768
Nov 2025,3221
Dec 2025,8699
Jan 2026,12852
Feb 2026,9241
Mar 2026,5544
Apr 2026,5117
May 2026,4864"""

rows = []
for i, line in enumerate(csv_lines.strip().split("\n")):
    if i == 0:
        continue  # skip header
    month_str, avg_str = line.rsplit(",", 1)
    rows.append({"month_str": month_str.strip(), "avg_players": int(avg_str.strip())})

data = pd.DataFrame(rows)

# Parse month strings to datetime
month_abbr = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

def to_date(s):
    parts = s.split()
    return datetime(int(parts[1]), month_abbr[parts[0]], 1)

data["date"] = data["month_str"].apply(to_date)

# --- Annotation data ---
# Each row: point to annotate + label text
# Positions are calculated manually so labels don't overlap
annotations = pd.DataFrame(
    [
        {
            "date": to_date("Sep 2017"),
            "avg_players": 26288,
            "label": "93,350 all-time peak at launch",
            "label_x": to_date("Jan 2018"),  # shifted right
            "label_y": 32000,
        },
        {
            "date": to_date("Aug 2023"),
            "avg_players": 8228,
            "label": "Baldur's Gate 3 launch\nhalo effect",
            "label_x": to_date("Apr 2023"),  # shifted left
            "label_y": 14500,
        },
        {
            "date": to_date("Dec 2025"),
            "avg_players": 8699,
            "label": "Divinity sequel announcement\nat TGA",
            "label_x": to_date("Oct 2025"),  # shifted left
            "label_y": 15500,
        },
        {
            "date": to_date("Jan 2026"),
            "avg_players": 12852,
            "label": "Best sales month since 2017",
            "label_x": to_date("Mar 2026"),  # shifted right
            "label_y": 18000,
        },
    ]
)

# ---- Build chart ----
p = (
    ggplot()
    # Shaded area
    + geom_area(
        data=data,
        mapping=aes(x="date", y="avg_players"),
        fill="#0072B2",  # Okabe-Ito blue
        alpha=0.20,
    )
    # Line
    + geom_line(
        data=data,
        mapping=aes(x="date", y="avg_players"),
        color="#0072B2",
        size=0.7,
    )
    # Points
    + geom_point(
        data=data,
        mapping=aes(x="date", y="avg_players"),
        color="#0072B2",
        size=1.2,
    )
    # Connector segments from label to data point
    + geom_segment(
        data=annotations,
        mapping=aes(x="label_x", y="label_y", xend="date", yend="avg_players"),
        color="#555555",
        size=0.5,
        linetype="solid",
    )
    # Annotation labels
    + geom_label(
        data=annotations,
        mapping=aes(x="label_x", y="label_y", label="label"),
        size=9.5,
        color="#222222",
        fill="#FFFFFF",
        alpha=0.92,
        label_padding=0.35,
        label_r=3,
        label_size=0.4,
        hjust=0.5,
        vjust=0.5,
    )
    # Scales
    + scale_x_datetime(
        break_width="1 year",
        format="%Y",
        expand=[0.02, 0],
    )
    + scale_y_continuous(
        expand=[0.01, 0],
        limits=[0, 36000],
        breaks=[0, 5000, 10000, 15000, 20000, 25000, 30000, 35000],
        labels=["0", "5K", "10K", "15K", "20K", "25K", "30K", "35K"],
    )
    # Labels and title
    + labs(
        title="Divinity: Original Sin 2 — Nine Years of Concurrent Players on Steam",
        subtitle=(
            "Monthly average concurrent players from September 2017 through May 2026. "
            "A Definitive Edition launch, the BG3 halo effect, and a sequel "
            "announcement each drove notable resurgences."
        ),
        x="",
        y="Average Concurrent Players",
        caption="Source: SteamCharts.com",
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(size=18, face="bold", hjust=0, margin=[0, 0, 6, 0]),
        plot_subtitle=element_text(size=11.5, color="#555555", hjust=0, margin=[0, 0, 16, 0]),
        axis_title_y=element_text(size=12, margin=[0, 8, 0, 0]),
        axis_title_x=element_blank(),
        axis_text_x=element_text(size=10, angle=0, hjust=0.5),
        axis_text_y=element_text(size=10),
        plot_caption=element_text(size=9, color="#888888", hjust=1, margin=[10, 0, 0, 0]),
        legend_position="none",
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.35),
        plot_margin=[20, 24, 10, 12],
        axis_ticks_x=element_line(color="#CCCCCC", size=0.3),
        axis_ticks_length_x=6,
    )
)

# --- Save ---
output_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "divinity-original-sin-2-blueprint_concurrent_players.png"

ggsave(p, str(output_path), w=1200, h=720, dpi=150, unit="px")
print(f"Chart saved to: {output_path}")
