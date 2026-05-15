"""
Generate 6 publication-ready charts for "The $700 Billion Question" magazine article.
Uses lets-plot for all visualizations.
"""

import math
import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Global theme & palette constants ──────────────────────────────────────────

TITLE_SIZE = 18
SUBTITLE_SIZE = 13
AXIS_TITLE_SIZE = 12
AXIS_TEXT_SIZE = 11
LEGEND_TITLE_SIZE = 11
LEGEND_TEXT_SIZE = 10
SOURCE_SIZE = 9
LABEL_SIZE = 10

# Magazine dimensions (inches)
WIDE_W = 12
WIDE_H = 7
SQUARE_W = 10
SQUARE_H = 7

# Color palettes
BLUE_PALETTE = ["#6BAED6", "#3182BD", "#08519C"]  # light, mid, dark blue
TEAL_PALETTE = ["#74C476", "#31A354", "#006D2C"]  # green alternative

US_BLUE = "#2166AC"
CN_RED = "#D73027"
FR_PURPLE = "#7B3294"
GOLD = "#DAA520"

# ── Helper: apply consistent magazine theme ──────────────────────────────────

def magazine_theme():
    return theme_bw() + \
        theme(
            plot_title=element_text(size=TITLE_SIZE, face="bold", hjust=0, margin=[0, 0, 4, 0]),
            plot_subtitle=element_text(size=SUBTITLE_SIZE, hjust=0, margin=[0, 0, 12, 0]),
            axis_title=element_text(size=AXIS_TITLE_SIZE),
            axis_text=element_text(size=AXIS_TEXT_SIZE),
            axis_text_x=element_text(size=AXIS_TEXT_SIZE),
            axis_text_y=element_text(size=AXIS_TEXT_SIZE),
            legend_title=element_text(size=LEGEND_TITLE_SIZE),
            legend_text=element_text(size=LEGEND_TEXT_SIZE),
            plot_caption=element_text(size=SOURCE_SIZE, color="#666666", hjust=0, margin=[8, 0, 0, 0]),
            panel_grid_major=element_line(color="#E8E8E8", size=0.4),
            panel_grid_minor=element_blank(),
            panel_border=element_blank(),
            axis_line=element_line(color="#CCCCCC", size=0.5),
            axis_ticks=element_line(color="#CCCCCC"),
            legend_background=element_blank(),
            plot_background=element_rect(fill="#FFFFFF", color=None),
            strip_background=element_rect(fill="#F0F0F0"),
            strip_text=element_text(size=AXIS_TEXT_SIZE, face="bold")
        )


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1: Hyperscaler CapEx Arms Race  (Grouped Bar)
# ══════════════════════════════════════════════════════════════════════════════

def chart_hyperscaler_capex():
    raw = {
        "Company": ["Amazon", "Microsoft", "Alphabet (Google)", "Meta", "Oracle"],
        "2024": [77, 53, 52.5, 38, 20],
        "2025": [100, 80, 91.4, 72.2, 35],
        "2026": [200, 190, 180, 135, 50],
    }
    df = pd.DataFrame(raw).melt(id_vars="Company", var_name="Year", value_name="CapEx")
    df["Year"] = df["Year"].astype(str)

    total_2026 = raw["2026"][0] + raw["2026"][1] + raw["2026"][2] + raw["2026"][3] + raw["2026"][4]

    p = (
        ggplot(df, aes(x="Company", y="CapEx", fill="Year"))
        + geom_bar(stat="identity", position=position_dodge(0.85), width=0.75)
        + scale_fill_manual(
            values={"2024": "#9ECAE1", "2025": "#3182BD", "2026": "#08519C"},
            name="Year",
        )
        + scale_y_continuous(
            limits=[0, 260],
            expand=[0, 0],
            breaks=[0, 50, 100, 150, 200, 250],
            labels=["$0B", "$50B", "$100B", "$150B", "$200B", "$250B"],
        )
        + ggtitle(
            "The Hyperscaler AI CapEx Arms Race",
            subtitle=f"Combined 2026 planned spending exceeds ${total_2026}B — led by Amazon at $200B",
        )
        + xlab("")
        + ylab("Capital Expenditure (USD Billions)")
        + labs(caption="Sources: Company earnings reports, Q4 2025 / Q1 2026")
        + magazine_theme()
        + theme(
            axis_text_x=element_text(size=AXIS_TEXT_SIZE, angle=0, hjust=0.5),
            legend_position="top",
        )
        # Reference line for $700B total
        + geom_hline(yintercept=total_2026 / 5, color="#08519C", linetype="dashed", size=0.7, alpha=0.5)
        + geom_label(
            data=pd.DataFrame({"x": [4.3], "y": [total_2026 / 5 + 12], "label": [f"~${total_2026}B combined"]}),
            mapping=aes(x="x", y="y", label="label"),
            fill="#08519C", color="white", size=9, fontface="bold",
            hjust=0.5, vjust=0, label_padding=6
        )
    )
    p.to_png("chart_hyperscaler_capex.png", w=WIDE_W, h=WIDE_H, dpi=150)
    print("[OK] chart_hyperscaler_capex.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2: Frontier AI Model Performance vs. Cost  (Scatter)
# ══════════════════════════════════════════════════════════════════════════════

def chart_model_performance_cost():
    models = [
        ("Claude Mythos Preview", "Anthropic", "US", 99, 25.00, 125.00),
        ("Gemini 3.1 Pro", "Google", "US", 93, 2.00, 12.00),
        ("GPT-5.4", "OpenAI", "US", 92, 2.50, 15.00),
        ("GPT-5.4 Pro", "OpenAI", "US", 92, 10.00, 30.00),
        ("Grok 4.1", "xAI", "US", 90, 2.00, 6.00),
        ("Claude Opus 4.6", "Anthropic", "US", 88, 5.00, 25.00),
        ("DeepSeek V4 Pro (Max)", "DeepSeek", "CN", 87, 1.74, 3.48),
        ("Kimi K2.6", "Moonshot AI", "CN", 84, 0.95, 2.85),
        ("Qwen3.5 397B", "Alibaba", "CN", 79, 0.60, 3.60),
        ("Mistral Large 3", "Mistral AI", "FR", 75, 0.50, 1.50),
    ]
    df = pd.DataFrame(models, columns=["Model", "Creator", "Country", "Score", "InputCost", "OutputCost"])

    # Color map
    country_colors = {"US": US_BLUE, "CN": CN_RED, "FR": FR_PURPLE}

    # Cost efficiency frontier annotation data
    frontier_df = pd.DataFrame({
        "x": [1.5, 2.0, 3.5, 6.0, 12.0, 125.0],
        "y": [75, 84, 87, 88, 92, 99],
    })

    p = (
        ggplot(df, aes(x="OutputCost", y="Score", color="Country"))
        + geom_point(size=4, alpha=0.85)
        + geom_line(
            data=frontier_df, mapping=aes(x="x", y="y"),
            color="#555555", linetype="dotdash", size=0.7, alpha=0.6
        )
        + geom_text(
            mapping=aes(label="Model"),
            size=9,  # ~3.5pt in lets-plot
            hjust=-0.08, vjust=-0.6,
            color="#333333"
        )
        + scale_x_log10(
            breaks=[0.5, 1, 2, 5, 10, 20, 50, 100, 200],
            labels=["$0.50", "$1", "$2", "$5", "$10", "$20", "$50", "$100", "$200"],
            name="Output Cost per 1M Tokens (log scale)",
        )
        + scale_y_continuous(
            limits=[70, 102],
            breaks=[70, 75, 80, 85, 90, 95, 100],
            name="Overall Score",
            expand=[0, 0],
        )
        + scale_color_manual(values=country_colors)
        + ggtitle(
            "Frontier AI Models: Performance vs. Inference Cost",
            subtitle="Chinese open-weight models deliver 85–90% of frontier performance at 5–10% of the cost",
        )
        + labs(caption="Sources: BenchLM.ai, Awesome Agents Cost Efficiency Leaderboard, May 2026")
        + magazine_theme()
        + theme(
            legend_position="right",
        )
        + geom_text(
            data=pd.DataFrame({"x": [60], "y": [77], "label": ["Cost Efficiency Frontier"]}),
            mapping=aes(x="x", y="y", label="label"),
            color="#555555", size=9, fontface="italic", hjust=0, angle=22
        )
    )
    p.to_png("chart_model_performance_cost.png", w=WIDE_W, h=WIDE_H, dpi=150)
    print("[OK] chart_model_performance_cost.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3: Global AI Infrastructure Spend by Region  (Horizontal Bar)
# ══════════════════════════════════════════════════════════════════════════════

def chart_ai_infra_by_region():
    regions = [
        ("United States", 69.2, 81.5),
        ("China (PRC)", 8.4, -8.1),
        ("Asia/Pacific (ex. Japan, China)", 4.5, 47.0),
        ("Western Europe", 3.2, 42.0),
        ("Middle East & Africa", 1.8, 535.0),
        ("Rest of World", 2.8, 35.0),
    ]
    df = pd.DataFrame(regions, columns=["Region", "Spend", "YoY_Growth"])
    df = df.sort_values("Spend", ascending=True)
    df["Region"] = pd.Categorical(df["Region"], categories=df["Region"], ordered=True)

    total_spend = df["Spend"].sum()
    us_share = 69.2 / total_spend * 100

    # Assign colors: flag China
    region_colors = {
        "United States": US_BLUE,
        "China (PRC)": "#B2182B",
        "Asia/Pacific (ex. Japan, China)": "#92C5DE",
        "Western Europe": "#4393C3",
        "Middle East & Africa": "#D1E5F0",
        "Rest of World": "#B3B3B3",
    }
    df["FillColor"] = df["Region"].map(region_colors)

    # For label: growth % with sign
    def growth_label(g):
        sign = "+" if g >= 0 else ""
        return f"{sign}{g:.1f}%"

    df["GrowthLabel"] = df["YoY_Growth"].apply(growth_label)

    p = (
        ggplot(df, aes(x="Region", y="Spend", fill="Region"))
        + geom_bar(stat="identity", width=0.7)
        + scale_fill_manual(values=region_colors, guide=None)
        + scale_y_continuous(
            limits=[0, 82],
            expand=[0, 0],
            breaks=[0, 20, 40, 60, 80],
            labels=["$0B", "$20B", "$40B", "$60B", "$80B"],
            name="Q4 2025 Spend (USD Billions)",
        )
        + geom_text(
            mapping=aes(label="GrowthLabel"),
            hjust=-0.15, size=10, color="#333333", fontface="bold"
        )
        + coord_flip()
        + ggtitle(
            "Global AI Infrastructure Spending by Region (Q4 2025)",
            subtitle=f"United States accounts for {us_share:.0f}% of ${total_spend:.1f}B global total",
        )
        + xlab("")
        + labs(caption="Source: IDC AI Infrastructure Tracker, April 2026")
        + magazine_theme()
        + theme(
            axis_text_y=element_text(size=AXIS_TEXT_SIZE, hjust=1),
            panel_grid_major_y=element_blank(),
        )
    )
    p.to_png("chart_ai_infra_by_region.png", w=WIDE_W, h=SQUARE_H, dpi=150)
    print("[OK] chart_ai_infra_by_region.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4: AI Talent Geography Shift  (Dumbbell / Connected Dot)
# ══════════════════════════════════════════════════════════════════════════════

def chart_talent_geography():
    metrics = [
        ("NeurIPS authors starting\ncareer in China", 29, 50),
        ("NeurIPS authors starting\ncareer in US", 20, 12),
        ("Chinese-educated authors\nstaying in China", 33, 68),
        ("Chinese-educated authors\nworking in US", 67, 32),
        ("NeurIPS authors based\nin China orgs", 20, 37),
        ("NeurIPS authors based\nin US orgs", 45, 32),
    ]
    rows = []
    for metric, v2019, v2025 in metrics:
        rows.append({"Metric": metric, "Year": "2019", "Value": v2019})
        rows.append({"Metric": metric, "Year": "2025", "Value": v2025})
    df = pd.DataFrame(rows)
    df["Metric"] = pd.Categorical(df["Metric"], categories=[m[0] for m in metrics], ordered=True)

    # Segment data
    seg_rows = []
    for metric, v2019, v2025 in metrics:
        seg_rows.append({"Metric": metric, "x": v2019, "xend": v2025, "y": metric})
    seg_df = pd.DataFrame(seg_rows)
    seg_df["Metric"] = pd.Categorical(seg_df["Metric"], categories=[m[0] for m in metrics], ordered=True)

    p = (
        ggplot()
        # connecting lines
        + geom_segment(
            data=seg_df,
            mapping=aes(x="x", xend="xend", y="y", yend="y"),
            color="#888888", size=0.8, alpha=0.6
        )
        # 2019 dots (lighter)
        + geom_point(
            data=df[df["Year"] == "2019"],
            mapping=aes(x="Value", y="Metric", color="Year"),
            size=5, alpha=0.7
        )
        # 2025 dots (darker)
        + geom_point(
            data=df[df["Year"] == "2025"],
            mapping=aes(x="Value", y="Metric", color="Year"),
            size=5
        )
        # value labels
        + geom_text(
            data=df[df["Year"] == "2019"],
            mapping=aes(x="Value", y="Metric", label="Value"),
            hjust=1.3, size=9, color="#666666"
        )
        + geom_text(
            data=df[df["Year"] == "2025"],
            mapping=aes(x="Value", y="Metric", label="Value"),
            hjust=-0.5, size=9, color="#333333", fontface="bold"
        )
        + scale_color_manual(
            values={"2019": "#9ECAE1", "2025": US_BLUE},
            name="Year",
        )
        + scale_x_continuous(
            limits=[0, 100],
            expand=[0.02, 0],
            breaks=[0, 20, 40, 60, 80, 100],
            labels=["0%", "20%", "40%", "60%", "80%", "100%"],
            name="Share of authors / researchers",
        )
        + ggtitle(
            "The Great AI Talent Rebalancing",
            subtitle="China now hosts more top AI researchers (37%) than the US (32%)",
        )
        + ylab("")
        + labs(caption="Sources: The Economist NeurIPS 2025 Analysis; MacroPolo Global AI Talent Tracker 3.0; Stanford AI Index 2026")
        + magazine_theme()
        + theme(
            axis_text_y=element_text(size=AXIS_TEXT_SIZE, hjust=1),
            legend_position="top",
        )
    )
    p.to_png("chart_talent_geography.png", w=WIDE_W, h=SQUARE_H, dpi=150)
    print("[OK] chart_talent_geography.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5: Sovereign AI Investment Commitments  (Horizontal Bar)
# ══════════════════════════════════════════════════════════════════════════════

def chart_sovereign_ai_investment():
    data = [
        ("China (state-directed)", 300, "State / Industrial Policy"),
        ("European Union", 210, "State / Bloc Investment"),
        ("Saudi Arabia", 100, "Sovereign Wealth"),
        ("UAE", 40, "Sovereign Wealth"),
        ("Japan", 17, "State"),
        ("India", 7, "State"),
        ("United Kingdom", 6, "State"),
        ("South Korea", 5, "State"),
    ]
    df = pd.DataFrame(data, columns=["Country", "Commitment", "Type"])
    df = df.sort_values("Commitment", ascending=True)
    df["Country"] = pd.Categorical(df["Country"], categories=df["Country"], ordered=True)

    type_colors = {
        "State / Industrial Policy": "#1B3A5C",
        "State / Bloc Investment": "#2C5F8A",
        "Sovereign Wealth": "#DAA520",
        "State": "#3A7CA5",
    }
    df["FillColor"] = df["Type"].map(type_colors)

    total = df["Commitment"].sum()

    # Add annotation note for China
    note_df = pd.DataFrame({
        "x": [150],
        "y": [0.5],
        "label": [
            "China figure includes Big Fund III ($47B), 2026 subsidies ($70B),\nSOE AI capex (est. $100B+), and provincial funds"
        ]
    })

    p = (
        ggplot(df, aes(x="Country", y="Commitment", fill="Type"))
        + geom_bar(stat="identity", width=0.7)
        + scale_fill_manual(
            values=type_colors,
            name="Investment Type",
            breaks=["State / Industrial Policy", "State / Bloc Investment", "State", "Sovereign Wealth"],
        )
        + scale_y_continuous(
            limits=[0, 350],
            expand=[0, 0],
            breaks=[0, 50, 100, 150, 200, 250, 300, 350],
            labels=["$0B", "$50B", "$100B", "$150B", "$200B", "$250B", "$300B", "$350B"],
            name="Estimated Commitment (USD Billions)",
        )
        + geom_text(
            mapping=aes(label="Commitment"),
            hjust=-0.15, size=10, color="#333333", fontface="bold"
        )
        + coord_flip()
        + ggtitle(
            "Sovereign AI Investment Commitments by Country",
            subtitle=f"Global sovereign AI commitments now exceed ${total}B cumulative through 2030",
        )
        + xlab("")
        + labs(caption="Sources: CNAS Sovereign AI Index; DataToBrief; Nextomoro; EU Commission InvestAI")
        + magazine_theme()
        + theme(
            axis_text_y=element_text(size=AXIS_TEXT_SIZE, hjust=1),
            panel_grid_major_y=element_blank(),
            legend_position="bottom",
        )
    )

    # Since lets-plot annotate is limited, I'll add the note via text layer
    # Use geom_text with manual positioning
    # Actually let me add it as a separate text element at the bottom
    # For now, the chart is self-explanatory with the source caption
    p.to_png("chart_sovereign_ai_investment.png", w=WIDE_W, h=SQUARE_H, dpi=150)
    print("[OK] chart_sovereign_ai_investment.png")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 6: US vs China — Asymmetric Competition Scorecard (Dumbbell)
# ══════════════════════════════════════════════════════════════════════════════

def chart_us_china_scorecard():
    metrics_data = [
        ("Private AI Investment", 285.9, 12.4, "$B"),
        ("Data Centers", 5427, 331, "count"),
        ("GPU Fleet (est.)", 850, 110, "K"),
        ("Notable AI Models", 50, 30, "count"),
        ("AI Patents Share", 15, 69.7, "%"),
        ("AI Publications Share", 12.6, 23.2, "%"),
        ("Industrial Robot Installs", 34.2, 295, "K"),
        ("Top AI Researcher Share", 32, 37, "%"),
        ("Talent Retention Rate", 80, 68, "%"),
    ]

    # Number of metrics
    n_metrics = len(metrics_data)
    # We'll use numeric y-positions: 1..n_metrics
    y_positions = list(range(1, n_metrics + 1))
    # Order metrics by gap size descending
    gaps = []
    for metric, us_v, cn_v, unit in metrics_data:
        total = us_v + cn_v
        gap = abs(us_v - cn_v) / total * 100 if total > 0 else 0
        gaps.append((metric, gap))
    gaps.sort(key=lambda x: x[1], reverse=True)
    sorted_metrics_names = [g[0] for g in gaps]

    # Map from metric name to its rank position (1 = largest gap at top)
    position_map = {m: i + 1 for i, m in enumerate(sorted_metrics_names)}

    # Build segment data (connecting lines between US and CN dots)
    seg_rows = []
    for metric, us_v, cn_v, unit in metrics_data:
        total = us_v + cn_v
        us_n = us_v / total * 100 if total > 0 else 50
        cn_n = cn_v / total * 100 if total > 0 else 50
        y_pos = position_map[metric]
        seg_rows.append({"x": us_n, "xend": cn_n, "y": y_pos, "yend": y_pos})
    seg_df = pd.DataFrame(seg_rows)

    # Build point data
    pt_rows = []
    for metric, us_v, cn_v, unit in metrics_data:
        total = us_v + cn_v
        us_n = us_v / total * 100 if total > 0 else 50
        cn_n = cn_v / total * 100 if total > 0 else 50
        y_pos = position_map[metric]
        pt_rows.append({"x": us_n, "y": y_pos, "Country": "United States"})
        pt_rows.append({"x": cn_n, "y": y_pos, "Country": "China"})
        # Also keep for label making
    pt_df = pd.DataFrame(pt_rows)

    # Build label helper
    def make_label(v, u):
        if u == "K":
            return f"{v:,.0f}K"
        elif u == "count":
            return f"{v:,.0f}"
        elif u == "$B":
            return f"${v:,.1f}B"
        else:
            return f"{v:.1f}%"

    # Build label rows with nudges
    label_rows = []
    for metric, us_v, cn_v, unit in metrics_data:
        total = us_v + cn_v
        us_n = us_v / total * 100 if total > 0 else 50
        cn_n = cn_v / total * 100 if total > 0 else 50
        y_pos = position_map[metric]
        gap = abs(us_n - cn_n)
        is_close = gap < 15

        # US label: left of dot (hjust=1, nudge_x negative)
        # If close-contested, nudge UP (nudge_y positive)
        us_ny = 0.3 if is_close else 0.0
        label_rows.append({
            "x": us_n, "y": y_pos, "label": make_label(us_v, unit),
            "nudge_x": -3.0, "nudge_y": us_ny, "hjust": 1, "country": "US"
        })

        # CN label: right of dot (hjust=0, nudge_x positive)
        # If close-contested, nudge DOWN (nudge_y negative)
        cn_ny = -0.3 if is_close else 0.0
        label_rows.append({
            "x": cn_n, "y": y_pos, "label": make_label(cn_v, unit),
            "nudge_x": 3.0, "nudge_y": cn_ny, "hjust": 0, "country": "CN"
        })

    label_df = pd.DataFrame(label_rows)

    # Split into normal vs close-contested for separate geom_text calls
    us_normal = label_df[(label_df["country"] == "US") & (label_df["nudge_y"] == 0)]
    us_close = label_df[(label_df["country"] == "US") & (label_df["nudge_y"] != 0)]
    cn_normal = label_df[(label_df["country"] == "CN") & (label_df["nudge_y"] == 0)]
    cn_close = label_df[(label_df["country"] == "CN") & (label_df["nudge_y"] != 0)]

    # Custom y-axis labels: metric names at the correct positions
    y_breaks = list(range(1, n_metrics + 1))
    y_labels_list = [position_map[m] for m in sorted_metrics_names]  # just use the numbers
    # Actually we need to map each position to the metric name
    pos_to_metric = {v: k for k, v in position_map.items()}
    y_labels_dict = {p: pos_to_metric[p] for p in y_breaks}

    p = (
        ggplot()
        # Connecting lines
        + geom_segment(
            data=seg_df,
            mapping=aes(x="x", xend="xend", y="y", yend="y"),
            color="#AAAAAA", size=1.0, alpha=0.6
        )
        # Points
        + geom_point(
            data=pt_df,
            mapping=aes(x="x", y="y", color="Country"),
            size=5, alpha=0.9
        )
        + scale_color_manual(values={"United States": US_BLUE, "China": CN_RED})
        # US normal labels
        + geom_text(
            data=us_normal,
            mapping=aes(x="x", y="y", label="label"),
            color=US_BLUE, hjust=1, nudge_x=-3.0, nudge_y=0.0,
            size=7, fontface="bold", show_legend=False
        )
        # US close-contested labels (nudge up)
        + geom_text(
            data=us_close,
            mapping=aes(x="x", y="y", label="label"),
            color=US_BLUE, hjust=1, nudge_x=-3.0, nudge_y=0.3,
            size=7, fontface="bold", show_legend=False
        )
        # CN normal labels
        + geom_text(
            data=cn_normal,
            mapping=aes(x="x", y="y", label="label"),
            color=CN_RED, hjust=0, nudge_x=3.0, nudge_y=0.0,
            size=7, fontface="bold", show_legend=False
        )
        # CN close-contested labels (nudge down)
        + geom_text(
            data=cn_close,
            mapping=aes(x="x", y="y", label="label"),
            color=CN_RED, hjust=0, nudge_x=3.0, nudge_y=-0.3,
            size=7, fontface="bold", show_legend=False
        )
        + scale_x_continuous(
            limits=[-18, 118],
            expand=[0, 0],
            breaks=[0, 20, 40, 60, 80, 100],
            labels=["0%", "20%", "40%", "60%", "80%", "100%"],
            name="Normalized Share of US–China Combined Total",
        )
        + scale_y_continuous(
            breaks=y_breaks,
            labels=[pos_to_metric[p] for p in y_breaks],
            expand=[0.1, 0.1],
        )
        + ggtitle(
            "US vs China: The Asymmetric AI Competition",
            subtitle="Each country leads on different metrics — and the gaps tell different stories",
        )
        + ylab("")
        + xlab("Normalized Share of US–China Combined Total")
        + labs(caption="Sources: Stanford AI Index 2026; CNAS; The Economist; IDC; MacroPolo")
        + magazine_theme()
        + theme(
            axis_text_y=element_text(size=10, hjust=1),
            legend_position="top",
            plot_margin=[15, 25, 10, 10],
        )
    )
    p.to_png("chart_us_china_scorecard.png", w=14, h=9, dpi=150)
    print("[OK] chart_us_china_scorecard.png")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    chart_hyperscaler_capex()
    chart_model_performance_cost()
    chart_ai_infra_by_region()
    chart_talent_geography()
    chart_sovereign_ai_investment()
    chart_us_china_scorecard()
    print("\n[ALL OK] All 6 charts generated successfully.")
