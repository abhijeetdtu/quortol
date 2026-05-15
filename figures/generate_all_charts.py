"""
Generate all 5 charts for "The Netflix Paradox" magazine feature.
Uses lets-plot for charts 1, 3, 4 and matplotlib for charts 2 & 5.
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path

# lets-plot imports (primary visualization library)
from lets_plot import *
LetsPlot.setup_html()

# matplotlib imports are done locally in chart_2 and chart_5 functions
# to avoid interfering with lets-plot's rendering pipeline

# ============================================================
# GLOBAL STYLE SETTINGS
# ============================================================
NETFLIX_RED = "#E50914"
DARK_TEXT = "#333333"
MED_GRAY = "#888888"
LIGHT_GRAY = "#f5f5f5"
WHITE = "#FFFFFF"
GREEN_UP = "#2e7d32"
RED_DOWN = "#c62828"

WIDTH = 1200
DPI = 150

Path("figures").mkdir(exist_ok=True)

# Magazine theme for lets-plot
magazine_theme = (
    theme_minimal() +
    theme(
        plot_title=element_text(size=22, face="bold", color=DARK_TEXT, hjust=0.5, margin=[0, 0, 8, 0]),
        plot_subtitle=element_text(size=13, color=MED_GRAY, hjust=0.5, margin=[0, 0, 10, 0]),
        axis_title=element_text(size=12, color=DARK_TEXT),
        axis_text=element_text(size=10, color=DARK_TEXT),
        axis_ticks=element_line(color="#dddddd"),
        axis_line=element_line(color="#dddddd"),
        panel_grid_major=element_line(color="#eeeeee", size=0.4),
        panel_grid_minor=element_blank(),
        panel_background=element_rect(fill=WHITE, color=None),
        plot_background=element_rect(fill=WHITE, color=None),
        legend_position="right",
        legend_title=element_text(size=11, color=DARK_TEXT, face="bold"),
        legend_text=element_text(size=10, color=DARK_TEXT),
        plot_caption=element_text(size=9, color=MED_GRAY, hjust=0, margin=[10, 0, 0, 0]),
        strip_background=element_rect(fill=LIGHT_GRAY),
        strip_text=element_text(size=10, color=DARK_TEXT, face="bold"),
    )
)


# ============================================================
# CHART 1: The Pricing Arc
# ============================================================
def chart_1_pricing_arc():
    print("Generating Chart 1: The Pricing Arc...")

    df = pd.DataFrame({
        "year": [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                 2020, 2021, 2022, 2023, 2024, 2025, 2026],
        "nominal": [7.99, 7.99, 7.99, 8.99, 9.99, 9.99, 10.99, 10.99, 12.99,
                    13.99, 13.99, 15.49, 15.49, 15.49, 17.99, 19.99],
        "cpi_adjusted": [11.20, 10.90, 10.70, 11.80, 13.00, 12.80, 13.80, 13.50, 15.60,
                         16.50, 15.80, 16.20, 15.60, 15.20, 17.20, 19.99]
    })

    # Area fill data
    df_fill = df[["year", "nominal"]].copy()
    df_fill["ymax"] = df_fill["nominal"]

    # Melt for two lines with series column
    df_long = df.melt(id_vars=["year"], value_vars=["nominal", "cpi_adjusted"],
                      var_name="series", value_name="price")

    df_nominal = df_long[df_long["series"] == "nominal"].copy()
    df_cpi = df_long[df_long["series"] == "cpi_adjusted"].copy()

    # Annotations
    annotations = pd.DataFrame({
        "year": [2011, 2019, 2022, 2026],
        "price": [7.99, 12.99, 15.49, 19.99],
        "label": [
            "$7.99\nLaunch",
            "$12.99",
            "$15.49",
            "$19.99\nCurrent"
        ]
    })

    p = (
        # Use area fill with a ribbon approach: ggplot(base_data, aes(...))
        ggplot(df_fill, aes(x="year"))
        # Area fill
        + geom_area(aes(y="ymax"), fill=NETFLIX_RED, alpha=0.08)
        # Nominal line
        + geom_line(aes(y="price"), data=df_nominal, color=NETFLIX_RED, size=1.6)
        # CPI line
        + geom_line(aes(y="price"), data=df_cpi, color="#555555", size=1.2, linetype="dashed")
        # Nominal points
        + geom_point(aes(y="price"), data=df_nominal, color=NETFLIX_RED, size=2.5)
        # CPI points
        + geom_point(aes(y="price"), data=df_cpi, color="#555555", size=2)
        # Annotations
        + geom_label(
            aes(x="year", y="price", label="label"),
            data=annotations,
            fill=WHITE, color=DARK_TEXT,
            label_size=0.3, size=9, alpha=0.9, label_padding=0.3, tooltips="none"
        )
        # Scales
        + scale_x_continuous(breaks=list(range(2011, 2027)))
        + scale_y_continuous(limits=[0, 24], breaks=[0, 5, 10, 15, 20])
        # Labels
        + labs(
            title="The Price of Watching: Netflix Standard Plan, 2011\u20132026",
            subtitle="From $7.99 to $19.99 \u2014 a 150% increase, far outpacing inflation",
            x="",
            y="Monthly Price (USD)",
            caption="Source: Netflix pricing history, Bureau of Labor Statistics CPI; CPI-adjusted to March 2026 dollars"
        )
        # Theme
        + magazine_theme
        + theme(
            plot_margin=[20, 25, 30, 25],
            legend_position="top",
            axis_text_x=element_text(angle=45, hjust=1, size=9),
        )
    )

    ggsave(p, "netflix_pricing_arc.png", path="figures", w=WIDTH / DPI, h=9, dpi=DPI)
    print("  -> Saved figures/netflix_pricing_arc.png")


# ============================================================
# CHART 2: The Content Treadmill (matplotlib for dual axis)
# ============================================================
def chart_2_content_spend():
    print("Generating Chart 2: The Content Treadmill...")

    # Local matplotlib imports (avoid interfering with lets-plot)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.lines import Line2D

    platforms = ["Netflix", "Amazon\n(video+music)", "Disney\n(total content)", "Apple TV+\n(est.)"]
    y2024 = [16.5, 20.4, 22.0, 6.5]
    y2025 = [18.0, 22.4, 23.0, 7.0]
    y2026_forecast = [19.8, 24.0, 24.0, 7.5]

    totals = [85.0, 96.0, 101.0]
    years_total = [2024, 2025, 2026]

    fig, ax1 = plt.subplots(figsize=(12, 8.5))
    fig.patch.set_facecolor(WHITE)
    ax1.set_facecolor(WHITE)

    x = np.arange(len(platforms))
    bar_width = 0.25
    gap = 0.05

    # Bars for each year
    bars_2024 = ax1.bar(x - bar_width - gap / 2, y2024, bar_width, label="2024",
                        color="#c9c9c9", edgecolor=WHITE, linewidth=0.5)
    bars_2025 = ax1.bar(x, y2025, bar_width, label="2025",
                        color="#888888", edgecolor=WHITE, linewidth=0.5)
    bars_2026 = ax1.bar(x + bar_width + gap / 2, y2026_forecast, bar_width, label="2026 Forecast",
                        color=NETFLIX_RED, edgecolor=WHITE, linewidth=0.5, alpha=0.85)

    # Value labels on bars
    for bars, vals in [(bars_2024, y2024), (bars_2025, y2025), (bars_2026, y2026_forecast)]:
        for bar, val in zip(bars, vals):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                     "${:.1f}B".format(val), ha="center", va="bottom", fontsize=7.5,
                     color=DARK_TEXT, fontweight="bold")

    # Secondary axis - "All Streamers Combined" line
    ax2 = ax1.twinx()
    ax2.plot(years_total, totals, color="#1a237e", linewidth=2.5,
             marker="s", markersize=8, markerfacecolor="#1a237e",
             markeredgecolor=WHITE, markeredgewidth=1.5,
             label="All Streamers Combined", zorder=5)

    # Add data labels for the line
    for yr, tot in zip(years_total, totals):
        ax2.annotate("${}B".format(tot), (yr, tot), textcoords="offset points",
                     xytext=(0, 14), ha="center", fontsize=9, color="#1a237e",
                     fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.2", facecolor=WHITE,
                               edgecolor="#cccccc", alpha=0.8))

    # Axis labels
    ax1.set_ylabel("Content Spend by Platform ($ Billions)", fontsize=12, color=DARK_TEXT, labelpad=10)
    ax2.set_ylabel("Total Industry Spend ($ Billions)", fontsize=12, color="#1a237e", labelpad=10)

    ax1.set_xticks(x)
    ax1.set_xticklabels(platforms, fontsize=10, color=DARK_TEXT)
    ax1.set_xlim(-0.6, len(platforms) - 0.4)

    # Set y limits
    ax1.set_ylim(0, 30)
    ax2.set_ylim(60, 115)

    # Grid
    ax1.yaxis.grid(True, alpha=0.3, color="#dddddd", linewidth=0.5)
    ax1.set_axisbelow(True)

    # Remove top/bottom spines
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax1.spines["left"].set_color("#dddddd")
    ax1.spines["bottom"].set_color("#dddddd")
    ax2.spines["right"].set_color("#1a237e")

    # Title / Subtitle
    ax1.set_title("The Content Arms Race", fontsize=22, fontweight="bold",
                  color=DARK_TEXT, pad=10, loc="center")
    ax1.text(0.5, 0.97,
             "Streaming platforms will spend $101 billion on programming in 2026",
             transform=ax1.transAxes, ha="center", fontsize=13,
             color=MED_GRAY)

    # Legend: combine both axes
    legend_elements = [
        mpatches.Patch(facecolor="#c9c9c9", edgecolor=WHITE, label="2024"),
        mpatches.Patch(facecolor="#888888", edgecolor=WHITE, label="2025"),
        mpatches.Patch(facecolor=NETFLIX_RED, edgecolor=WHITE, label="2026 Forecast", alpha=0.85),
        Line2D([0], [0], color="#1a237e", linewidth=2.5,
               marker="s", markersize=8, markerfacecolor="#1a237e",
               markeredgecolor=WHITE, label="All Streamers Combined")
    ]

    ax1.legend(handles=legend_elements, loc="upper left",
               frameon=True, fancybox=True, facecolor=WHITE,
               edgecolor="#dddddd", fontsize=9.5, title=None)

    # Source
    ax1.text(0, -0.12,
             "Source: Netflix shareholder letters, Amazon 10-K SEC filings, Disney fiscal reporting, Ampere Analysis",
             transform=ax1.transAxes, fontsize=8.5, color=MED_GRAY)

    plt.tight_layout()
    plt.savefig("figures/content_spend_comparison.png", dpi=DPI,
                bbox_inches="tight", facecolor=WHITE, edgecolor="none")
    plt.close()
    print("  -> Saved figures/content_spend_comparison.png")


# ============================================================
# CHART 3: The Piracy Return
# ============================================================
def chart_3_piracy():
    print("Generating Chart 3: The Piracy Return...")

    df = pd.DataFrame({
        "year": [2020, 2021, 2022, 2023, 2024],
        "visits": [104, 130, 190, 229, 216]
    })

    # Trend line
    z = np.polyfit(df["year"], df["visits"], 1)
    p_trend = np.poly1d(z)
    df["trend"] = p_trend(df["year"])

    annotations = pd.DataFrame({
        "year": [2023, 2024],
        "visits": [229, 216],
        "label": ["Peak: 229B visits in 2023", "2024: 216B visits (-5.7%)"]
    })

    p = (
        ggplot()
        # Bars with gradient -- aes() FIRST as positional arg
        + geom_bar(
            aes(x="year", y="visits", fill="year"),
            data=df,
            stat="identity",
            width=0.6,
            alpha=0.85
        )
        # Trend line
        + geom_line(
            aes(x="year", y="trend"),
            data=df,
            color="#555555",
            size=1.2,
            linetype="dashed"
        )
        # Data labels on bars
        + geom_text(
            aes(x="year", y="visits", label="visits"),
            data=df,
            vjust=-0.5,
            size=11,
            color=DARK_TEXT,
            fontface="bold"
        )
        # Annotations
        + geom_label(
            aes(x="year", y="visits", label="label"),
            data=annotations,
            vjust=1.2,
            fill="#fefefe",
            color=DARK_TEXT,
            label_size=0.3,
            size=9,
            alpha=0.95,
            label_padding=0.4,
            tooltips="none"
        )
        # Color fill for bars: gradient from light to dark red
        + scale_fill_gradient(low="#ff8a80", high=NETFLIX_RED)
        # Labels
        + labs(
            title="The Piracy Resurgence",
            subtitle="Global piracy site visits more than doubled between 2020 and 2024",
            x="",
            y="Global Piracy Visits (Billions)",
            caption="Source: MUSO 2024 Global Piracy Trends Report"
        )
        # Theme
        + magazine_theme
        + theme(
            plot_margin=[20, 25, 30, 25],
            legend_position="none",
            axis_text_x=element_text(size=11),
        )
        + scale_x_continuous(breaks=[2020, 2021, 2022, 2023, 2024])
        + scale_y_continuous(limits=[0, 270], breaks=[0, 50, 100, 150, 200, 250])
    )

    ggsave(p, "piracy_trends.png", path="figures", w=WIDTH / DPI, h=8, dpi=DPI)
    print("  -> Saved figures/piracy_trends.png")


# ============================================================
# CHART 4: The Re-Bundling (Horizontal Bar Chart)
# ============================================================
def chart_4_bundling():
    print("Generating Chart 4: The Great Re-Bundling...")

    df = pd.DataFrame({
        "bundle": [
            "Disney+/Hulu/Max Bundle",
            "Comcast StreamSaver",
            "Verizon +play",
            "Amazon Prime Channels",
            "Other Bundles",
            "Total Bundle Subscribers"
        ],
        "subs_2024": [8, 3, 5, 18, 16, 50],
        "subs_2025": [15, 7, 9, 22, 18, 71],
        "growth": [87, 133, 80, 22, 12, 40],
        "is_total": [False, False, False, False, False, True]
    })

    # Reverse order for horizontal bar (bottom of chart = first in data)
    df = df.iloc[::-1].reset_index(drop=True)
    df["y_pos"] = range(len(df))

    # Build a color mapping column for 2025 bars
    # Map growth rate to green intensity hex colors
    def growth_to_color(growth_val, is_total):
        if is_total:
            return DARK_TEXT
        intensity = min(growth_val / 150, 1.0)
        r = int(165 - (165 - 27) * intensity)
        g = int(214 - (214 - 94) * intensity)
        b = int(167 - (167 - 32) * intensity)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    df["fill_color"] = [growth_to_color(row["growth"], row["is_total"])
                        for _, row in df.iterrows()]

    # To avoid fill=List (which breaks lets-plot rendering), create separate
    # dataframes per color group and overlay them
    bar_colors = df["fill_color"].unique()

    # Build chart with ggplot(df, aes(x="y_pos")) as base
    p = (
        ggplot(df, aes(x="y_pos"))
        # 2024 bars (lighter, behind)
        + geom_bar(aes(y="subs_2024"), stat="identity", fill="#cccccc", width=0.4, alpha=0.6)
        # 2025 bars (colored by growth) - use fill mapped to a categorical var, then manual scale
        + geom_bar(aes(y="subs_2025", fill="fill_color"), stat="identity", width=0.4, alpha=0.9)
        # Data labels for 2025 values
        + geom_text(
            aes(y="subs_2025", label="subs_2025"),
            hjust=-0.1, size=9.5, color=DARK_TEXT, fontface="bold"
        )
        # Growth rate labels (on the 2024 bar)
        + geom_text(
            aes(y="subs_2024", label="growth"),
            hjust=1.1, size=8, color=WHITE, fontface="bold", vjust=0.5
        )
        # Manual fill scale - but hide legend since it's not meaningful
        + scale_fill_identity(guide="none")
        # Flip coordinates
        + coord_flip()
        # Labels
        + labs(
            title="The Great Re-Bundling",
            subtitle="Bundle subscribers grew 40% in 2025, now 27% of all streaming subscriptions",
            x="",
            y="Subscribers (Millions)",
            caption="Source: Antenna State of Subscriptions Q1 2026; Parks Associates"
        )
        # Scale
        + scale_x_continuous(
            breaks=list(range(len(df))),
            labels=df["bundle"].tolist()
        )
        + scale_y_continuous(limits=[0, 90], breaks=[0, 20, 40, 60, 80])
        # Theme
        + magazine_theme
        + theme(
            plot_margin=[20, 40, 30, 25],
            legend_position="none",
            axis_text_y=element_text(size=10, color=DARK_TEXT, face="bold"),
        )
    )

    ggsave(p, "bundling_growth.png", path="figures", w=WIDTH / DPI, h=8, dpi=DPI)
    print("  -> Saved figures/bundling_growth.png")


# ============================================================
# CHART 5: Netflix Financial Profile - KPI Dashboard (matplotlib)
# ============================================================
def chart_5_financial_kpi():
    print("Generating Chart 5: Netflix Financial Profile...")

    # Local matplotlib imports (avoid interfering with lets-plot)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # KPI Data
    kpis = [
        {"metric": "Revenue", "value": "$12.25B", "period": "Q1 2026", "change": "+16.2%", "dir": "up"},
        {"metric": "Operating Margin", "value": "32.3%", "period": "Q1 2026", "change": "+0.6pp", "dir": "up"},
        {"metric": "Net Income", "value": "$5.28B", "period": "Q1 2026", "change": "+82.8%", "dir": "up"},
        {"metric": "Free Cash Flow", "value": "$5.1B", "period": "Q1 2026", "change": "+89.7%", "dir": "up"},
        {"metric": "Global Subscribers", "value": "325M+", "period": "Q1 2026", "change": "+14.8%", "dir": "up"},
        {"metric": "Ad Revenue (FY 2025)", "value": "$1.5B", "period": "FY 2025", "change": "+150%", "dir": "up"},
        {"metric": "Ad Revenue (Proj. 2026)", "value": "$3.0B", "period": "FY 2026 est", "change": "+100%", "dir": "up"},
        {"metric": "Monthly Churn", "value": "~2%", "period": "2025 avg", "change": "Best in industry", "dir": "up"},
    ]

    n_cards = len(kpis)
    n_cols = 4
    n_rows = (n_cards + n_cols - 1) // n_cols

    fig = plt.figure(figsize=(12, 10))
    fig.patch.set_facecolor(WHITE)

    # Title area
    ax_title = fig.add_axes([0, 0.94, 1, 0.06])
    ax_title.set_facecolor(WHITE)
    ax_title.set_xlim(0, 1)
    ax_title.set_ylim(0, 1)
    ax_title.text(0.5, 0.85, "Netflix by the Numbers, Early 2026",
                  ha="center", va="center", fontsize=24, fontweight="bold", color=DARK_TEXT)
    ax_title.text(0.5, 0.15, "A cash-generating machine with unmatched pricing power",
                  ha="center", va="center", fontsize=13, color=MED_GRAY)
    ax_title.axis("off")

    # Create card grid
    card_width = 0.22
    card_height = 0.17
    x_start = 0.04
    y_start = 0.90
    x_spacing = 0.26
    y_spacing = 0.19

    for i, kpi in enumerate(kpis):
        col = i % n_cols
        row = i // n_cols

        x = x_start + col * x_spacing
        y = y_start - (row + 1) * y_spacing

        ax_card = fig.add_axes([x, y, card_width, card_height])
        ax_card.set_facecolor(LIGHT_GRAY)
        ax_card.set_xlim(0, 1)
        ax_card.set_ylim(0, 1)
        ax_card.axis("off")

        # Card border
        for spine in ax_card.spines.values():
            spine.set_visible(True)
            spine.set_color("#dddddd")
            spine.set_linewidth(1)

        # Metric name at top
        ax_card.text(0.5, 0.88, kpi["metric"], ha="center", va="top",
                     fontsize=10, color=MED_GRAY, fontweight="semibold",
                     transform=ax_card.transAxes)

        # Big value in center
        ax_card.text(0.5, 0.52, kpi["value"], ha="center", va="center",
                     fontsize=18, fontweight="bold", color=DARK_TEXT,
                     transform=ax_card.transAxes)

        # Change indicator
        if kpi["dir"] == "up":
            arrow = "\u25B2"  # up triangle
            change_color = GREEN_UP
        else:
            arrow = "\u25BC"  # down triangle
            change_color = RED_DOWN

        if kpi["metric"] == "Monthly Churn":
            change_text = "{} {}".format(arrow, kpi["change"])
        else:
            change_text = "{} {} YoY".format(arrow, kpi["change"])

        ax_card.text(0.5, 0.15, change_text, ha="center", va="bottom",
                     fontsize=10, color=change_color, fontweight="bold",
                     transform=ax_card.transAxes)

        # Period label (small)
        ax_card.text(0.5, 0.02, kpi["period"], ha="center", va="bottom",
                     fontsize=7.5, color=MED_GRAY,
                     transform=ax_card.transAxes)

    # Source line
    ax_source = fig.add_axes([0.04, 0.01, 0.92, 0.02])
    ax_source.set_facecolor(WHITE)
    ax_source.text(0, 0.5,
                   "Source: Netflix Q1 2026 Shareholder Letter (April 16, 2026); SEC Filings; Antenna",
                   fontsize=8.5, color=MED_GRAY, va="center")
    ax_source.axis("off")

    plt.savefig("figures/netflix_financial_profile.png", dpi=DPI,
                bbox_inches="tight", facecolor=WHITE, edgecolor="none")
    plt.close()
    print("  -> Saved figures/netflix_financial_profile.png")


# ============================================================
# RUN ALL
# ============================================================
if __name__ == "__main__":
    chart_1_pricing_arc()
    chart_2_content_spend()
    chart_3_piracy()
    chart_4_bundling()
    chart_5_financial_kpi()
    print("\nAll 5 charts generated successfully!")
