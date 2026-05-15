"""
Southern Cone Feature Article — 5 Magazine-Quality Redesigned Charts
Uses lets-plot 4.9.0, outputs 1200x800 PNGs to figures/
SINGLE dataframe per ggplot — no inherit_aes=False, no separate data frames.
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from lets_plot import *

warnings.filterwarnings("ignore")
LetsPlot.setup_html()

# -- Color Palette (South American) ------------------------------
TEAL       = "#008080"
TEAL_DARK  = "#005C5C"
TEAL_LIGHT = "#40B4B4"
ORANGE     = "#D85C27"
ORANGE_LIGHT = "#FF8C00"
GOLD       = "#E8A820"
GREEN_DARK   = "#1B5E20"
GREEN_MED    = "#2E7D32"
GREEN_LIGHT  = "#66BB6A"
GREEN_PALE   = "#A5D6A7"
SOFT_BLUE    = "#4A90A4"
SOFT_BLUE_LIGHT = "#7BB8CC"
CHARCOAL     = "#2C2C2C"
CREAM        = "#FDF8F0"
RUST         = "#A04020"
GOLD_YELLOW  = "#D4A843"
LIGHT_GRAY   = "#B0B0B0"
PALE_GRAY    = "#D8D8D8"

FIGURES = Path("figures")
FIGURES.mkdir(parents=True, exist_ok=True)

MAGAZINE_THEME = theme(
    plot_background   = element_rect(fill="#FFFFFF"),
    panel_background  = element_rect(fill="#FFFFFF"),
    panel_grid_major  = element_line(color="#E8E8E8", size=0.35),
    panel_grid_minor  = element_blank(),
    axis_line         = element_line(color="#D0D0D0", size=0.5),
    axis_ticks        = element_line(color="#D0D0D0"),
    axis_text         = element_text(size=10, family="Arial", color="#444444"),
    axis_title        = element_text(size=12, family="Arial", color="#222222", face="bold"),
    plot_title        = element_text(size=20, family="Arial", color="#111111", face="bold"),
    plot_subtitle     = element_text(size=13, family="Arial", color="#555555"),
    legend_title      = element_text(size=10, family="Arial", color="#333333"),
    legend_text       = element_text(size=9, family="Arial", color="#444444"),
    plot_caption      = element_text(size=8.5, family="Arial", color="#999999", hjust=0),
    plot_margin       = [12, 20, 8, 12],
    axis_ticks_length = 4,
)


def save_chart(plot, filename):
    ggsave(plot, filename, path=str(FIGURES), w=12, h=8, dpi=100)
    path = FIGURES / filename
    size_kb = path.stat().st_size / 1024
    print(f"  [OK] {filename}  ({size_kb:.0f} KB)")
    return path


# ===============================================================
# CHART 1: Argentina Inflation (Embedded annotations, no separate data)
# ===============================================================

def chart_1_inflation():
    print("\n-- Chart 1: Argentina Inflation --")

    raw = [
        ("2023-12", 211.4), ("2024-01", 254.2), ("2024-02", 276.2),
        ("2024-03", 287.9), ("2024-04", 289.4), ("2024-05", 276.4),
        ("2024-06", 271.5), ("2024-07", 263.4), ("2024-08", 236.7),
        ("2024-09", 209.0), ("2024-10", 193.0), ("2024-11", 166.0),
        ("2024-12", 117.8), ("2025-01", 84.5),  ("2025-02", 66.9),
        ("2025-03", 55.9),  ("2025-04", 47.3),  ("2025-05", 43.5),
        ("2025-06", 39.4),  ("2025-07", 36.6),  ("2025-08", 33.6),
        ("2025-09", 31.8),  ("2025-10", 31.3),  ("2025-11", 31.4),
        ("2025-12", 31.5),  ("2026-01", None),   ("2026-02", 33.2),
        ("2026-03", 32.6),
    ]

    df = pd.DataFrame(raw, columns=["date_str", "inflation"])
    df["date"] = pd.to_datetime(df["date_str"] + "-01")
    df_plot = df.dropna(subset=["inflation"]).copy()

    df_plot["milei_label"] = None
    df_plot["milei_x"] = pd.NaT
    df_plot["milei_y"] = np.nan
    df_plot["peak_label"] = None
    df_plot["peak_x"] = pd.NaT
    df_plot["peak_y"] = np.nan

    milei_idx = df_plot[df_plot["date_str"] == "2023-12"].index[0]
    df_plot.loc[milei_idx, "milei_label"] = "Milei takes office\nDec 2023"
    df_plot.loc[milei_idx, "milei_x"] = pd.Timestamp("2023-12-01")
    df_plot.loc[milei_idx, "milei_y"] = 255.0

    peak_idx = df_plot[df_plot["date_str"] == "2024-04"].index[0]
    df_plot.loc[peak_idx, "peak_label"] = "Peak: 289.4%\nApr 2024"
    df_plot.loc[peak_idx, "peak_x"] = pd.Timestamp("2024-04-01")
    df_plot.loc[peak_idx, "peak_y"] = 289.4

    last_date = df_plot["date"].max()

    p = (
        ggplot(df_plot, aes(x="date", y="inflation"))
        + geom_area(fill=TEAL, alpha=0.10)
        + geom_line(color=TEAL_DARK, size=1.6)
        + geom_point(color=TEAL_DARK, size=2.5)
        + geom_hline(yintercept=0, color=CHARCOAL, size=0.5, linetype="dashed", alpha=0.35)
        + geom_vline(
            xintercept=pd.Timestamp("2023-12-01"),
            color=ORANGE_LIGHT, size=0.8, linetype="dashed", alpha=0.5
        )
        + geom_vline(
            xintercept=last_date,
            color=ORANGE_LIGHT, size=0.8, linetype="dashed", alpha=0.5
        )
        + geom_label(
            data=df_plot[df_plot["milei_label"].notna()],
            mapping=aes(x="milei_x", y="milei_y", label="milei_label"),
            fill="#FFFFFF", color=CHARCOAL, size=3.2, family="Arial",
            fontface="bold", hjust=1, vjust=0,
            box_just=1, alpha=0.85,
            label_padding=5.5, label_r=3, label_format="raw",
        )
        + geom_label(
            data=df_plot[df_plot["peak_label"].notna()],
            mapping=aes(x="peak_x", y="peak_y", label="peak_label"),
            fill=ORANGE_LIGHT, color=CHARCOAL, size=3.2, family="Arial",
            fontface="bold", hjust=0.5, vjust=-0.5,
            alpha=0.9, label_padding=5.5, label_r=3, label_format="raw",
        )
        + scale_x_datetime(
            name="",
            format="%b\n%Y",
            expand=[0.02, 0.02],
        )
        + scale_y_continuous(
            name="Inflation Rate (CPI YoY %)",
            breaks=[0, 50, 100, 150, 200, 250],
            labels=["0%", "50%", "100%", "150%", "200%", "250%"],
            expand=[0, 0.08],
        )
        + ggtitle(
            label="Argentina's Disinflation: From 289% to 33%",
            subtitle="Monthly CPI Year-over-Year under Javier Milei's administration",
        )
        + xlab("")
        + labs(caption="Quortol | Source: INDEC / Trading Economics")
        + MAGAZINE_THEME
        + theme(
            axis_text_x=element_text(size=8.5, color="#555555"),
        )
    )

    return save_chart(p, "argentina_inflation.png")


# ===============================================================
# CHART 2: GDP per Capita Dumbbell (Single df with geom_linerange)
# ===============================================================

def chart_2_gdp_per_capita():
    print("\n-- Chart 2: GDP per Capita Dumbbell --")

    df = pd.DataFrame([
        ("Uruguay",   17278, 27608, "+60%"),
        ("Chile",     14791, 17735, "+20%"),
        ("Argentina", 10056, 14355, "+43%"),
        ("Paraguay",   5551,  7692, "+39%"),
    ], columns=["country", "gdp_2019", "gdp_2026", "growth_label"])

    df = df.sort_values("gdp_2026", ascending=True).reset_index(drop=True)

    p = (
        ggplot(df, aes(x="country"))
        + geom_linerange(aes(ymin="gdp_2019", ymax="gdp_2026"), color=PALE_GRAY, size=2.5)
        + geom_point(aes(y="gdp_2019"), color=SOFT_BLUE_LIGHT, size=4, alpha=0.6)
        + geom_point(aes(y="gdp_2026"), color=TEAL_DARK, size=6)
        + geom_text(
            aes(y="gdp_2026", label="growth_label"),
            hjust=-0.3, size=3.8, family="Arial", color=CHARCOAL, fontface="bold",
        )
        + scale_y_continuous(
            name="GDP per Capita (Nominal USD)",
            breaks=[0, 5000, 10000, 15000, 20000, 25000, 30000],
            labels=["$0", "$5,000", "$10,000", "$15,000", "$20,000", "$25,000", "$30,000"],
            expand=[0, 0.25],
        )
        + coord_flip()
        + ggtitle(
            label="Southern Cone GDP per Capita: 2019 vs 2026",
            subtitle="Uruguay leads; Argentina posts strongest recovery (+43%); Paraguay steady (+39%)",
        )
        + xlab("")
        + labs(caption="Quortol | Sources: IMF, INDEC, Central Bank of Chile, BCP Paraguay")
        + MAGAZINE_THEME
        + theme(
            axis_text_y=element_text(size=12, face="bold", color="#222222"),
            axis_text_x=element_text(size=9),
        )
    )

    return save_chart(p, "southern_cone_gdp_per_capita.png")


# ===============================================================
# CHART 3: Vaca Muerta Oil Production + Energy Trade Surplus
# ===============================================================

def chart_3_vaca_muerta():
    print("\n-- Chart 3: Vaca Muerta + Energy Surplus --")

    df = pd.DataFrame([
        (2019, 200, 25.0, -2.1),
        (2020, 185, 28.0, -1.5),
        (2021, 210, 35.0, 1.2),
        (2022, 230, 42.0, 3.5),
        (2023, 240, 48.0, 4.8),
        (2024, 256, 54.9, 5.7),
        (2025, 270, 58.0, 7.815),
    ], columns=["year", "total_production", "vm_share_pct", "energy_surplus_bn"])

    df["vm_production"] = df["total_production"] * df["vm_share_pct"] / 100.0
    df["conventional"] = df["total_production"] - df["vm_production"]

    df_melt = df.melt(
        id_vars=["year"],
        value_vars=["conventional", "vm_production"],
        var_name="source", value_name="production",
    )
    source_labels = {"conventional": "Conventional", "vm_production": "Vaca Muerta"}
    df_melt["source_label"] = df_melt["source"].map(source_labels)

    surplus_min, surplus_max = -2.1, 7.815
    surplus_scale = {
        y: (v - surplus_min) / (surplus_max - surplus_min) * 300
        for y, v in zip(df["year"], df["energy_surplus_bn"])
    }
    df_melt["surplus_scaled"] = df_melt["year"].map(surplus_scale)
    df_melt["surplus_label"] = df_melt["year"].map(
        dict(zip(df["year"], df["energy_surplus_bn"]))
    )
    df_melt["vm_pct_label"] = df_melt["year"].map(
        dict(zip(df["year"], df["vm_share_pct"]))
    )

    p = (
        ggplot(df_melt, aes(x="year", y="production", fill="source_label"))
        + geom_bar(stat="identity", width=0.7, alpha=0.9)
        + geom_line(
            data=df_melt[df_melt["source"] == "conventional"],
            mapping=aes(y="surplus_scaled"),
            color=ORANGE, size=1.8,
        )
        + geom_point(
            data=df_melt[df_melt["source"] == "conventional"],
            mapping=aes(y="surplus_scaled"),
            color=ORANGE, size=4, fill="#FFFFFF", stroke=1.5,
        )
        + geom_text(
            data=df_melt[df_melt["source"] == "conventional"],
            mapping=aes(y="surplus_scaled", label="surplus_label"),
            size=3.6, family="Arial", color=ORANGE, fontface="bold",
            nudge_y=16, label_format="raw",
        )
        + geom_text(
            data=df_melt[df_melt["source"] == "vm_production"],
            mapping=aes(y="production", label="vm_pct_label"),
            size=3.8, family="Arial", color="#FFFFFF", fontface="bold",
            nudge_y=8, label_format="raw",
        )
        + scale_fill_manual(
            name="",
            values={"Conventional": TEAL_LIGHT, "Vaca Muerta": TEAL_DARK},
        )
        + scale_x_continuous(
            name="",
            breaks=[2019, 2020, 2021, 2022, 2023, 2024, 2025],
            expand=[0.08, 0.08],
        )
        + scale_y_continuous(
            name="Total Oil Production (million bbl)",
            breaks=[0, 50, 100, 150, 200, 250, 300],
            labels=["0", "50", "100", "150", "200", "250", "300"],
            expand=[0, 0.08],
        )
        + ggtitle(
            label="Argentina's Oil Boom Fuels Energy Trade Surplus",
            subtitle="Vaca Muerta now 58% of production; energy surplus hits record $7.8B (2025)",
        )
        + xlab("")
        + labs(
            caption="Quortol | Source: Argentine Energy Secretariat / IPS",
            fill="Production Source",
        )
        + MAGAZINE_THEME
        + theme(
            legend_position="top",
            legend_justification="left",
            axis_text_x=element_text(size=11, face="bold"),
        )
    )

    return save_chart(p, "vaca_muerta_production.png")


# ===============================================================
# CHART 4: Uruguay Beef Exports — Destination Shift (Stacked Area + Revenue)
# ===============================================================

def chart_4_uruguay_beef():
    print("\n-- Chart 4: Uruguay Beef Destination Shift --")

    df_wide = pd.DataFrame([
        (2020, 58, 15, 12, 15, 1.8),
        (2021, 67, 12, 10, 11, 2.1),
        (2022, 66, 12,  9, 13, 2.3),
        (2023, 58, 16, 11, 15, 2.1),
        (2024, 42, 25, 15, 18, 2.5),
        (2025, 36, 33, 18, 13, 2.7),
    ], columns=["year", "china_pct", "us_pct", "eu_pct", "other_pct", "total_revenue_bn"])

    df_melt = df_wide.melt(
        id_vars=["year", "total_revenue_bn"],
        value_vars=["china_pct", "us_pct", "eu_pct", "other_pct"],
        var_name="destination", value_name="pct_share",
    )
    dest_labels = {"china_pct": "China", "us_pct": "US", "eu_pct": "EU", "other_pct": "Other"}
    df_melt["destination"] = df_melt["destination"].map(dest_labels)

    dest_order = ["China", "US", "EU", "Other"]
    df_melt["destination"] = pd.Categorical(
        df_melt["destination"], categories=dest_order, ordered=True
    )

    rev_min, rev_max = 1.8, 2.7
    rev_scale = {
        y: (v - rev_min) / (rev_max - rev_min) * 100
        for y, v in zip(df_wide["year"], df_wide["total_revenue_bn"])
    }
    df_melt["rev_scaled"] = df_melt["year"].map(rev_scale)
    df_melt["rev_label"] = df_melt["total_revenue_bn"]

    p = (
        ggplot(df_melt, aes(x="year", y="pct_share", fill="destination"))
        + geom_area(alpha=0.85, position="stack")
        + geom_smooth(
            data=df_melt[df_melt["destination"] == "China"],
            mapping=aes(y="rev_scaled"),
            method="loess", se=False, span=0.35, color=CHARCOAL, size=1.3,
        )
        + geom_point(
            data=df_melt[df_melt["destination"] == "China"],
            mapping=aes(y="rev_scaled"),
            color=CHARCOAL, size=3, fill="#FFFFFF", stroke=1.2,
        )
        + geom_text(
            data=df_melt[df_melt["destination"] == "China"],
            mapping=aes(y="rev_scaled", label="rev_label"),
            size=3.0, family="Arial", color=CHARCOAL, fontface="bold",
            nudge_y=-6, label_format="raw",
        )
        + scale_fill_manual(
            name="Export Destination",
            values={"China": RUST, "US": SOFT_BLUE, "EU": GOLD_YELLOW, "Other": LIGHT_GRAY},
        )
        + scale_x_continuous(
            name="",
            breaks=[2020, 2021, 2022, 2023, 2024, 2025],
            expand=[0.03, 0.03],
        )
        + scale_y_continuous(
            name="Share of Beef Export Value",
            breaks=[0, 25, 50, 75, 100],
            labels=["0%", "25%", "50%", "75%", "100%"],
            expand=[0, 0.02],
        )
        + ggtitle(
            label="Uruguay's Beef Export Shift: China Declines, US Rises",
            subtitle="China's share dropped from 67% to 36%; US grew from 15% to 33% (2020-2025)",
        )
        + xlab("")
        + labs(
            caption="Quortol | Source: INAC | Total Revenue shown as line (USD bn)",
            fill="Destination",
        )
        + MAGAZINE_THEME
        + theme(
            legend_position="top",
            legend_justification="left",
            axis_text_x=element_text(size=11, face="bold"),
        )
    )

    return save_chart(p, "uruguay_beef_exports.png")


# ===============================================================
# CHART 5: GDP Growth Rates — All 4 Southern Cone Countries
# ===============================================================

def chart_5_gdp_growth():
    print("\n-- Chart 5: GDP Growth Rates Comparison --")

    df = pd.DataFrame([
        (2019, -2.0, 0.6, 0.2, -0.4),
        (2020, -9.9, -6.1, -7.4, -0.8),
        (2021, 10.4, 11.3, 5.6, 4.0),
        (2022,  5.3, 2.1, 4.7, 0.2),
        (2023, -1.6, 0.2, 0.4, 4.7),
        (2024, -1.3, 2.6, 3.1, 4.2),
        (2025,  4.3, 2.6, 2.3, 4.5),
        (2026,  3.8, 2.2, 2.2, 4.0),
    ], columns=["year", "Argentina", "Chile", "Uruguay", "Paraguay"])

    df_melt = df.melt(
        id_vars=["year"],
        var_name="country", value_name="growth_rate",
    )

    country_colors = {
        "Argentina": SOFT_BLUE,
        "Chile":     ORANGE,
        "Uruguay":   TEAL,
        "Paraguay":  GREEN_MED,
    }

    p = (
        ggplot(df_melt, aes(x="year", y="growth_rate", color="country"))
        + geom_hline(yintercept=0, color=CHARCOAL, size=0.5, linetype="dashed", alpha=0.35)
        + geom_smooth(method="loess", se=False, span=0.35, size=1.3)
        + geom_point(size=2.5)
        + scale_color_manual(
            name="",
            values=country_colors,
        )
        + scale_x_continuous(
            name="",
            breaks=[2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
            expand=[0.03, 0.03],
        )
        + scale_y_continuous(
            name="Real GDP Growth Rate (%)",
            breaks=[-10, -5, 0, 5, 10],
            labels=["-10%", "-5%", "0%", "+5%", "+10%"],
            expand=[0, 0.08],
        )
        + ggtitle(
            label="Southern Cone GDP Growth: Divergent Paths (2019-2026)",
            subtitle="Paraguay shows remarkable stability; Argentina's dramatic swings; Chile and Uruguay recover steadily",
        )
        + xlab("")
        + labs(caption="Quortol | Sources: IMF WEO, INDEC, Central Bank of Chile, BCU, BCP")
        + MAGAZINE_THEME
        + theme(
            legend_position="top",
            legend_justification="left",
            axis_text_x=element_text(size=10, face="bold"),
        )
    )

    return save_chart(p, "southern_cone_gdp_growth.png")


# ===============================================================
# MAIN
# ===============================================================

if __name__ == "__main__":
    print("Generating Southern Cone feature charts...")

    paths = [
        chart_1_inflation(),
        chart_2_gdp_per_capita(),
        chart_3_vaca_muerta(),
        chart_4_uruguay_beef(),
        chart_5_gdp_growth(),
    ]

    print("\n-- Verification --")
    all_ok = True
    for p in paths:
        if p.exists():
            kb = p.stat().st_size / 1024
            print(f"  [OK] {p.name}  ({kb:.0f} KB)")
        else:
            print(f"  [FAIL] {p.name}  MISSING")
            all_ok = False

    if all_ok:
        print("\n[ALL OK] All 5 charts created successfully in figures/")
    else:
        print("\n[WARN]  Some charts are missing!")
