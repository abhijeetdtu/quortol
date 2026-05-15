"""
Regenerate 3 charts with ONLY verified, sourced data.
Overwrites existing files at:
  - figures/netflix_pricing_arc.png
  - figures/content_spend_comparison.png
  - figures/piracy_trends.png

Style: DPI 150, consistent magazine style
  - White bg, Netflix red #E50914 accent, dark gray #333333 text, light gray #f5f5f5
"""

import warnings
warnings.filterwarnings("ignore")

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

# ── Global Style ──────────────────────────────────────────────
NETFLIX_RED   = "#E50914"
DARK_TEXT     = "#333333"
MED_GRAY      = "#888888"
LIGHT_GRAY    = "#f5f5f5"
WHITE         = "#FFFFFF"
DPI           = 150

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.facecolor": WHITE,
    "figure.facecolor": WHITE,
    "axes.edgecolor": "#dddddd",
    "axes.grid": True,
    "grid.color": "#eeeeee",
    "grid.linewidth": 0.4,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "xtick.color": DARK_TEXT,
    "ytick.color": DARK_TEXT,
})

Path("figures").mkdir(exist_ok=True)


# ════════════════════════════════════════════════════════════════
# CHART 1: Pricing Arc
# ════════════════════════════════════════════════════════════════
def chart_1_pricing_arc():
    print("Generating Chart 1: Pricing Arc...")

    years = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
             2020, 2021, 2022, 2023, 2024, 2025, 2026]
    prices = [7.99, 7.99, 7.99, 8.99, 9.99, 9.99, 10.99, 10.99, 12.99,
              13.99, 13.99, 15.49, 15.49, 15.49, 17.99, 19.99]

    fig, ax = plt.subplots(figsize=(1200/DPI, 900/DPI))
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    # ── Area fill (light red, opacity 0.2) ──
    ax.fill_between(years, prices, alpha=0.2, color=NETFLIX_RED, linewidth=0)

    # ── Line ──
    ax.plot(years, prices, color=NETFLIX_RED, linewidth=2.5, zorder=4)

    # ── Points ──
    ax.scatter(years, prices, color=NETFLIX_RED, s=40, zorder=5, edgecolors=WHITE, linewidth=0.5)

    # ── Annotations at key events ──
    annotations = [
        (2011, 7.99,  "$7.99\nStreaming plan\nlaunched"),
        (2019, 12.99, "$12.99\nAll tiers\nincreased"),
        (2022, 15.49, "$15.49\nBasic plan\ndiscontinued"),
        (2026, 19.99, "$19.99\nMarch 2026\nincrease"),
    ]

    for year, price, label in annotations:
        # Determine offset direction: 2011 goes left, others alternate
        if year == 2011:
            ha = "left"
            x_off = 0.3
        elif year == 2026:
            ha = "right"
            x_off = -0.3
        else:
            ha = "center"
            x_off = 0

        ax.annotate(
            label,
            xy=(year, price),
            xytext=(x_off, 18),
            textcoords="offset points",
            ha=ha, va="bottom",
            fontsize=8.5, color=DARK_TEXT,
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=MED_GRAY, lw=1.0),
            bbox=dict(boxstyle="round,pad=0.3", facecolor=WHITE,
                      edgecolor="#dddddd", alpha=0.9)
        )

    # ── Axis labels ──
    ax.set_ylabel("Monthly Price (USD)", fontsize=12, color=DARK_TEXT, labelpad=10)

    # ── X-axis: every year, rotated ──
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right", fontsize=9)

    # ── Y-axis ──
    ax.set_ylim(0, 24)
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.set_yticklabels(["$0", "$5", "$10", "$15", "$20"])

    # ── Title / Subtitle ──
    ax.set_title("", fontsize=22, fontweight="bold", color=DARK_TEXT, pad=5, loc="center")
    fig.text(0.5, 0.97, "The Price of Watching: Netflix Standard Plan, 2011–2026",
             ha="center", va="top", fontsize=20, fontweight="bold", color=DARK_TEXT)
    fig.text(0.5, 0.925, "From $7.99 to $19.99 — a 150% increase",
             ha="center", va="top", fontsize=12, color=MED_GRAY)

    # ── Source ──
    fig.text(0.5, 0.01,
             "Source: Netflix pricing history (Keeping Up With Inflation, PriceTimeline)",
             ha="center", va="bottom", fontsize=8.5, color=MED_GRAY, style="italic")

    # ── Final adjustments ──
    ax.set_xlim(2010, 2027)
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    plt.subplots_adjust(top=0.88, bottom=0.10, left=0.10, right=0.95)
    plt.savefig("figures/netflix_pricing_arc.png", dpi=DPI,
                bbox_inches="tight", facecolor=WHITE, edgecolor="none")
    plt.close()
    print("  -> Saved figures/netflix_pricing_arc.png")


# ════════════════════════════════════════════════════════════════
# CHART 2: Content Spend Comparison
# ════════════════════════════════════════════════════════════════
def chart_2_content_spend():
    print("Generating Chart 2: Content Spend Comparison...")

    companies = ["Netflix\n(cash content)", "Amazon\n(video+music)", "Disney\n(total prog. & prod.)"]
    y2024 = [16.6, 20.4, 27.2]
    y2025 = [18.0, 22.4, 25.0]
    y2026 = [19.8, 24.0, 24.0]

    # Professional palette (blue / teal / slate — not red)
    colors_2024 = "#94a3b8"   # slate-400
    colors_2025 = "#64748b"   # slate-500
    colors_2026 = "#334155"   # slate-700

    x = np.arange(len(companies))
    bar_width = 0.25
    offset = 0.3

    fig, ax = plt.subplots(figsize=(1400/DPI, 900/DPI))
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    # ── Bars ──
    bars_2024 = ax.bar(x - offset, y2024, bar_width, label="2024",
                       color=colors_2024, edgecolor=WHITE, linewidth=0.5, zorder=3)
    bars_2025 = ax.bar(x, y2025, bar_width, label="2025",
                       color=colors_2025, edgecolor=WHITE, linewidth=0.5, zorder=3)
    bars_2026 = ax.bar(x + offset, y2026, bar_width, label="2026",
                       color=colors_2026, edgecolor=WHITE, linewidth=0.5, zorder=3)

    # ── Value labels on bars ──
    for bars, vals in [(bars_2024, y2024), (bars_2025, y2025), (bars_2026, y2026)]:
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f"${val:.1f}B", ha="center", va="bottom", fontsize=8.5,
                    color=DARK_TEXT, fontweight="bold")

    # ── Axis labels ──
    ax.set_ylabel("Content Spend ($ Billions)", fontsize=12, color=DARK_TEXT, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(companies, fontsize=10, color=DARK_TEXT)

    # ── Y-axis ──
    ax.set_ylim(0, 32)
    ax.set_yticks([0, 5, 10, 15, 20, 25, 30])
    ax.set_yticklabels(["$0", "$5B", "$10B", "$15B", "$20B", "$25B", "$30B"])

    ax.grid(True, alpha=0.3, axis="y")
    ax.set_axisbelow(True)

    # ── Title / Subtitle ──
    fig.text(0.5, 0.96, "The Content Arms Race",
             ha="center", va="top", fontsize=20, fontweight="bold", color=DARK_TEXT)
    fig.text(0.5, 0.92,
             "Major studio content spending, 2024–2026 (varying definitions — see notes)",
             ha="center", va="top", fontsize=11, color=MED_GRAY)

    # ── Legend ──
    legend = ax.legend(loc="upper left", frameon=True, fancybox=True,
                       facecolor=WHITE, edgecolor="#dddddd", fontsize=10,
                       title="Year", title_fontsize=10)
    legend.get_frame().set_linewidth(0.5)

    # ── Source ──
    fig.text(0.5, 0.03,
             "Source: Netflix shareholder letters; Amazon 10-K SEC filings (video+music combined); "
             "Disney annual reports (total programming & production costs incl. sports)",
             ha="center", va="bottom", fontsize=7.5, color=MED_GRAY, style="italic")

    # ── Important note about incomparability ──
    fig.text(0.5, 0.06,
             "Note: Definitions of content spend vary by company (see sources). "
             "Netflix = cash content spend. Amazon = video+music expense. Disney = total programming & production costs incl. sports.",
             ha="center", va="bottom", fontsize=8, color="#c0392b",
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#fef0f0",
                       edgecolor="#e0b3b3", linewidth=0.8))

    plt.subplots_adjust(top=0.88, bottom=0.18, left=0.10, right=0.95)
    plt.savefig("figures/content_spend_comparison.png", dpi=DPI,
                bbox_inches="tight", facecolor=WHITE, edgecolor="none")
    plt.close()
    print("  -> Saved figures/content_spend_comparison.png")


# ════════════════════════════════════════════════════════════════
# CHART 3: Piracy Trends
# ════════════════════════════════════════════════════════════════
def chart_3_piracy():
    print("Generating Chart 3: Piracy Trends...")

    years = [2021, 2022, 2023, 2024]
    visits = [182, 215, 229, 216]

    fig, ax = plt.subplots(figsize=(1200/DPI, 900/DPI))
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    # ── Gradient bars: lighter to darker red ──
    # Normalise visits to [0, 1] for color mapping
    norm_visits = [(v - min(visits)) / (max(visits) - min(visits)) for v in visits]
    # Light red at low end, Netflix red at high end
    bar_colors = []
    for n in norm_visits:
        # Interpolate between light pink (#ffcdd2) and Netflix red (#E50914)
        r1, g1, b1 = 0xFF, 0xCD, 0xD2  # light pink
        r2, g2, b2 = 0xE5, 0x09, 0x14  # Netflix red
        r = int(r1 + (r2 - r1) * n)
        g = int(g1 + (g2 - g1) * n)
        b = int(b1 + (b2 - b1) * n)
        bar_colors.append(f"#{r:02x}{g:02x}{b:02x}")

    # ── Bars ──
    bars = ax.bar(years, visits, width=0.55, color=bar_colors, edgecolor=WHITE,
                  linewidth=0.5, zorder=3)

    # ── Dashed connection line between bar tops ──
    ax.plot(years, visits, color=DARK_TEXT, linewidth=1.8, linestyle="--",
            marker="o", markersize=8, markerfacecolor=NETFLIX_RED,
            markeredgecolor=WHITE, markeredgewidth=1.5, zorder=5)

    # ── Value labels on bars ──
    for bar, val in zip(bars, visits):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                f"{val}B", ha="center", va="bottom", fontsize=11,
                color=DARK_TEXT, fontweight="bold")

    # ── Annotations ──
    # "2023 peak: 229B visits"
    ax.annotate(
        "2023 peak: 229B visits",
        xy=(2023, 229), xytext=(2023.6, 242),
        ha="center", va="bottom",
        fontsize=9, color=DARK_TEXT, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=NETFLIX_RED, lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", facecolor=WHITE,
                  edgecolor=NETFLIX_RED, alpha=0.9)
    )

    # "2024: 216B visits (-5.7%)"
    ax.annotate(
        "2024: 216B visits\n(-5.7% from peak)",
        xy=(2024, 216), xytext=(2023.4, 196),
        ha="center", va="top",
        fontsize=9, color="#2e7d32", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", facecolor=WHITE,
                  edgecolor="#2e7d32", alpha=0.9)
    )

    # ── Axis Labels ──
    ax.set_ylabel("Global Piracy Visits (Billions)", fontsize=12, color=DARK_TEXT, labelpad=10)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], fontsize=10)

    # ── Y-axis ──
    ax.set_ylim(0, 260)
    ax.set_yticks([0, 50, 100, 150, 200, 250])

    ax.grid(True, alpha=0.3, axis="y")
    ax.set_axisbelow(True)

    # ── Title / Subtitle ──
    fig.text(0.5, 0.97, "The Piracy Resurgence",
             ha="center", va="top", fontsize=20, fontweight="bold", color=DARK_TEXT)
    fig.text(0.5, 0.93,
             "Global piracy site visits rose sharply 2021–2023 before declining in 2024",
             ha="center", va="top", fontsize=11, color=MED_GRAY)

    # ── Source ──
    fig.text(0.5, 0.02,
             "Source: MUSO Piracy by Industry reports (2022–2024); Piracy Monitor",
             ha="center", va="bottom", fontsize=8.5, color=MED_GRAY, style="italic")

    # ── Note about 2020 omission ──
    fig.text(0.5, 0.045,
             "Note: 2020 data (approx. 158B visits) omitted — available only via secondary sources, not MUSO directly.",
             ha="center", va="bottom", fontsize=7.5, color=MED_GRAY, style="italic")

    plt.subplots_adjust(top=0.88, bottom=0.12, left=0.10, right=0.95)
    plt.savefig("figures/piracy_trends.png", dpi=DPI,
                bbox_inches="tight", facecolor=WHITE, edgecolor="none")
    plt.close()
    print("  -> Saved figures/piracy_trends.png")


# ════════════════════════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    chart_1_pricing_arc()
    chart_2_content_spend()
    chart_3_piracy()

    print("\n✓ All 3 charts regenerated successfully.")
    for f in ["netflix_pricing_arc.png", "content_spend_comparison.png", "piracy_trends.png"]:
        p = Path("figures") / f
        if p.exists():
            size_kb = p.stat().st_size / 1024
            print(f"  {p} — {size_kb:.1f} KB")
