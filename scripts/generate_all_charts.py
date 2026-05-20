#!/usr/bin/env python3
"""
Generate four publication-quality charts for a magazine feature on personal AI agents.
Output: 1400x900 px minimum, 150+ dpi, matplotlib with professional styling.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Global style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 16,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#CCCCCC",
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
})

WIDTH, HEIGHT = 1600, 1100
DPI = 150


# ══════════════════════════════════════════════════════════════════════════════
# Chart 1: Enterprise AI Agent Adoption Curve
# ══════════════════════════════════════════════════════════════════════════════
def chart_enterprise_adoption():
    fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)

    categories = ["Early 2025", "Q2 2025", "Q3 2025", "Early 2026", "End 2026\n(proj.)"]
    values     = [5, 11, 42, 72, 40]
    label_text = ["<5%", "11%", "42%", "72%", "40%"]

    x = np.arange(len(categories))
    color = "#00897B"

    # Area fill under line
    ax.fill_between(x, 0, values, color=color, alpha=0.15)

    # Line with markers
    ax.plot(x, values, color=color, linewidth=2.5, marker="o", markersize=8,
            markeredgecolor="white", markeredgewidth=1.5, zorder=5)

    # Data labels ABOVE each point (offset upward so they don't touch)
    for i, (v, lbl) in enumerate(zip(values, label_text)):
        ax.annotate(
            lbl,
            (x[i], v),
            textcoords="offset points",
            xytext=(0, 14),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="#004D40",
        )

    # Axes
    ax.set_xlim(-0.4, len(categories) - 0.6)
    ax.set_ylim(0, 85)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=0, ha="center")
    ax.set_ylabel("Percentage of Organizations (%)", fontsize=12)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))

    # Gridlines — Y-axis only, light grey dashed
    ax.yaxis.grid(True, linestyle="--", linewidth=0.6, color="#E0E0E0", zorder=0)
    ax.set_axisbelow(True)

    # Titles
    ax.set_title("Enterprise AI Agent Adoption", fontsize=16, fontweight="bold", pad=8)
    ax.text(0.5, 0.98, "Percentage of organizations with deployed AI agents",
            transform=ax.transAxes, ha="center", va="top", fontsize=11,
            color="#666666")

    # Source note
    ax.text(1.0, -0.02,
            "Sources: Gartner, KPMG AI Pulse Survey, Zapier State of Agentic AI 2026",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
            color="#999999", style="italic")
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig("chart_enterprise_adoption.png", dpi=DPI,
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("✓ chart_enterprise_adoption.png")


# ══════════════════════════════════════════════════════════════════════════════
# Chart 2: Time Savings from AI Agents
# ══════════════════════════════════════════════════════════════════════════════
def chart_time_savings():
    fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)

    tasks = [
        "Trip Planning",
        "Budget Optimization",
        "SaaS Comparative\nAnalysis",
        "Learning\nRecommendations",
        "B2B Vendor\nSourcing",
    ]
    pct_saved    = [76, 71, 68, 64, 55]
    agent_min    = [9.2, 6.1, 8.7, 5.3, 10.0]
    manual_min   = [38.5, 21.3, 27.0, 14.6, 22.4]
    avg_ref      = 66.8

    # Gradient: longest bar = #00695C (darkest) → shortest = #80CBC4 (lightest)
    colors = ["#00695C", "#00897B", "#26A69A", "#4DB6AC", "#80CBC4"]

    y = np.arange(len(tasks))
    bar_height = 0.55

    bars = ax.barh(y, pct_saved, height=bar_height, color=colors, zorder=3)

    # Percentage labels INSIDE bars at the end
    for i, (bar, pct) in enumerate(zip(bars, pct_saved)):
        # Dark enough for white text? Threshold ~55
        text_color = "white" if pct >= 60 else "#1a1a1a"
        ax.text(
            pct - 2.5, bar.get_y() + bar.get_height() / 2,
            f"{pct}%",
            ha="right", va="center", fontsize=11, fontweight="bold",
            color=text_color,
        )

    # Parenthetical labels to the RIGHT of each bar
    for i, (pct, a_min, m_min) in enumerate(zip(pct_saved, agent_min, manual_min)):
        ax.text(
            pct + 0.8, y[i],
            f"({a_min} / {m_min} min)",
            ha="left", va="center", fontsize=8.5,
            color="#555555",
        )

    # Vertical reference line at average
    ax.axvline(x=avg_ref, color="#E65100", linestyle="--", linewidth=1.2, zorder=4)
    ax.text(avg_ref + 0.5, len(tasks) - 0.3, f"Average: {avg_ref}%",
            fontsize=9, color="#E65100", fontweight="bold", va="bottom")

    # Axes
    ax.set_xlim(0, 105)
    ax.set_ylim(-0.6, len(tasks) - 0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(tasks, fontsize=10)
    ax.set_xlabel("Time Saved (%)", fontsize=12)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))

    # Gridlines
    ax.xaxis.grid(True, linestyle="--", linewidth=0.6, color="#E0E0E0", zorder=0)
    ax.set_axisbelow(True)

    # Titles
    ax.set_title("Time Savings Using AI Agents", fontsize=16, fontweight="bold", pad=8)
    ax.text(0.5, 0.98, "Agent task vs. manual task completion time",
            transform=ax.transAxes, ha="center", va="top", fontsize=11,
            color="#666666")

    # Source
    ax.text(1.0, -0.02,
            "First Page Sage, Agentic AI Statistics 2026 (N=8,128)",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
            color="#999999", style="italic")

    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig("chart_time_savings.png", dpi=DPI,
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("✓ chart_time_savings.png")


# ══════════════════════════════════════════════════════════════════════════════
# Chart 3: Psychological Impact of AI Use Modes
# ══════════════════════════════════════════════════════════════════════════════
def chart_psychological_impact():
    fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)

    cat_keys   = ["Self-Efficacy", "Psychological Ownership", "Work Meaningfulness"]
    cat_labels = ["Self-Efficacy", "Psychological\nOwnership", "Work\nMeaningfulness"]
    groups = ["No AI", "Active Collaboration", "Passive AI"]
    colors = ["#2E7D32", "#1565C0", "#E65100"]

    # Data: means
    means = {
        "Self-Efficacy":            [5.63, 5.43, 5.16],
        "Psychological Ownership":  [5.34, 5.26, 4.35],
        "Work Meaningfulness":      [5.54, 5.46, 4.94],
    }
    # Standard errors
    ses = {
        "Self-Efficacy":            [0.14, 0.12, 0.13],
        "Psychological Ownership":  [0.09, 0.08, 0.13],
        "Work Meaningfulness":      [0.12, 0.14, 0.16],
    }

    n_cats = len(cat_keys)
    n_groups = len(groups)
    bar_width = 0.22
    gap = 0.04  # gap between groups of bars

    # Positions for each group of bars
    x = np.arange(n_cats)
    offsets = np.linspace(-(bar_width + gap / 2), (bar_width + gap / 2), n_groups)

    for g_idx in range(n_groups):
        vals = [means[ck][g_idx] for ck in cat_keys]
        errs = [ses[ck][g_idx] for ck in cat_keys]
        x_pos = x + offsets[g_idx]

        bars = ax.bar(x_pos, vals, width=bar_width, color=colors[g_idx],
                      label=groups[g_idx], zorder=3)

        # Error bars (black, cap width 5)
        ax.errorbar(x_pos, vals, yerr=errs, fmt="none", ecolor="black",
                    capsize=5, capthick=1.0, elinewidth=1.0, zorder=4)

        # Value labels on top of each bar (offset above error bar cap)
        for xi, vi, ei in zip(x_pos, vals, errs):
            ax.text(xi, vi + ei + 0.08, f"{vi:.2f}",
                    ha="center", va="bottom", fontsize=9,
                    fontweight="bold", color="#333333")

    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels, fontsize=10)

    # Y-axis
    ax.set_ylim(1, 7.3)
    ax.set_ylabel("Mean Rating (1–7 Scale)", fontsize=12)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))

    # Grid
    ax.yaxis.grid(True, linestyle="--", linewidth=0.6, color="#E0E0E0", zorder=0)
    ax.set_axisbelow(True)

    # Legend ABOVE chart
    legend = ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.14),
        ncol=3,
        frameon=False,
        fontsize=11,
        handlelength=1.2,
        handletextpad=0.5,
        columnspacing=1.5,
    )

    # Titles
    ax.set_title("Psychological Impact of AI Use Modes", fontsize=16,
                 fontweight="bold", pad=8)
    ax.text(0.5, 1.02, "Passive AI use erodes self-efficacy, ownership, and meaningfulness",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=11,
            color="#666666")

    # Source
    ax.text(1.0, -0.02,
            "Lee et al., Nature Scientific Reports, March 2026 (N=539)",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
            color="#999999", style="italic")

    fig.tight_layout(rect=[0, 0.04, 1, 0.88])
    fig.savefig("chart_psychological_impact.png", dpi=DPI,
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("✓ chart_psychological_impact.png")


# ══════════════════════════════════════════════════════════════════════════════
# Chart 4: AI Agent Adoption by Industry
# ══════════════════════════════════════════════════════════════════════════════
def chart_industry_adoption():
    fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)

    industries = [
        "Technology /\nSoftware",
        "Financial\nServices",
        "Manufacturing",
        "Healthcare",
        "Telecom",
        "Retail /\neCommerce",
        "Energy",
        "Government",
        "Education",
    ]
    pcts = [86.5, 78.5, 68, 65, 62, 56.5, 50, 45, 37.5]

    # Varying opacity: top bar full, bottom ~0.4
    n = len(industries)
    base_color = np.array([25, 118, 210]) / 255.0  # #1976D2
    opacities = np.linspace(1.0, 0.4, n)

    y = np.arange(n)
    bar_height = 0.55

    for i, (pct, alpha) in enumerate(zip(pcts, opacities)):
        color = (base_color[0], base_color[1], base_color[2], alpha)
        ax.barh(y[i], pct, height=bar_height, color=color, zorder=3)

    # Percentage labels at the END of each bar (right-aligned, outside)
    for i, pct in enumerate(pcts):
        ax.text(pct + 1.2, y[i], f"{pct}%",
                ha="left", va="center", fontsize=11, fontweight="bold",
                color="#1a1a1a")

    # Vertical reference line at 50%
    ax.axvline(x=50, color="#666666", linestyle="--", linewidth=1.0, zorder=4)
    # Label above the line
    ax.text(50 + 0.5, n - 0.5, "50%",
            fontsize=9, color="#666666", fontweight="bold", va="bottom")

    # Axes
    ax.set_xlim(0, 105)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(industries, fontsize=10)
    ax.set_xlabel("Adoption Rate (%)", fontsize=12)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))

    # Gridlines
    ax.xaxis.grid(True, linestyle="--", linewidth=0.6, color="#E0E0E0", zorder=0)
    ax.set_axisbelow(True)

    # Titles
    ax.set_title("AI Agent Adoption by Industry, 2026", fontsize=16,
                 fontweight="bold", pad=8)
    ax.text(0.5, 0.98, "Percentage of organizations with active AI agents in production",
            transform=ax.transAxes, ha="center", va="top", fontsize=11,
            color="#666666")

    # Source
    ax.text(1.0, -0.02,
            "Compiled from Gartner, IDC, Paul Okhrem (CC BY 4.0)",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
            color="#999999", style="italic")

    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig("chart_industry_adoption.png", dpi=DPI,
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("✓ chart_industry_adoption.png")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    chart_enterprise_adoption()
    chart_time_savings()
    chart_psychological_impact()
    chart_industry_adoption()
    print("\nAll four charts generated successfully.")
