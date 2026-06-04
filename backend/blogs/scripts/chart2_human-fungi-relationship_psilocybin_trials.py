#!/usr/bin/env python3
"""
Grouped bar chart: Psilocybin for Treatment-Resistant Depression
Phase 3 Trial Results — COMPASS Pathways COMP005 & COMP006

Data source: COMPASS Pathways press release, February 17, 2026
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# ── Figure setup ──────────────────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150), dpi=150)

# ── Data ──────────────────────────────────────────────────────────────────────
trials = ["COMP005", "COMP006"]

# MADRS mean change from baseline (more negative = greater improvement)
active  = [-13.2, -15.8]   # 25 mg psilocybin
control = [-9.6,  -12.0]   # placebo (COMP005) / 1 mg (COMP006)

# Approximate 95% CI half-widths (illustrative)
ci_half = 2.0

# ── Positions ─────────────────────────────────────────────────────────────────
n_trials = len(trials)
bar_width = 0.32
gap = 0.04  # gap between groups

x = np.arange(n_trials)  # [0, 1]

# Offset each bar within the group
offset = bar_width / 2 + gap / 2
x_active  = x - offset
x_control = x + offset

# ── Colorblind-safe palette (Set2) ────────────────────────────────────────────
colors = {
    "active":  "#66c2a5",   # Set2 green
    "control": "#fc8d62",   # Set2 orange
}

# ── Bars ──────────────────────────────────────────────────────────────────────
bars_active = ax.bar(
    x_active, active, width=bar_width,
    color=colors["active"], edgecolor="white", linewidth=0.5,
    label="COMP360 25 mg psilocybin",
)

bars_control = ax.bar(
    x_control, control, width=bar_width,
    color=colors["control"], edgecolor="white", linewidth=0.5,
    label="Control (placebo / 1 mg)",
)

# ── Error bars ────────────────────────────────────────────────────────────────
ax.errorbar(
    x_active, active, yerr=ci_half,
    fmt="none", ecolor="grey", capsize=4, capthick=1.2, elinewidth=1.2,
)
ax.errorbar(
    x_control, control, yerr=ci_half,
    fmt="none", ecolor="grey", capsize=4, capthick=1.2, elinewidth=1.2,
)

# ── p-value annotations ───────────────────────────────────────────────────────
for i in range(n_trials):
    y_max = max(active[i], control[i])
    top = y_max + ci_half + 0.5   # just above the upper error bar
    ax.annotate(
        "p < 0.001",
        xy=(x[i], top),
        ha="center", va="bottom",
        fontsize=10, fontweight="bold",
        color="#333333",
    )

# ── Axis labels & title ───────────────────────────────────────────────────────
ax.set_ylabel(
    "Mean Change in MADRS Score from Baseline",
    fontsize=12, fontweight="semibold",
)
ax.set_xlabel("Trial", fontsize=12, fontweight="semibold")

ax.set_title(
    "Psilocybin for Treatment-Resistant Depression: Phase 3 Trial Results",
    fontsize=14, fontweight="bold", pad=16,
)

ax.set_xticks(x)
ax.set_xticklabels(trials, fontsize=11, fontweight="semibold")

# ── Y-axis: more negative = greater improvement → -20 at bottom, 0 at top ────
ax.set_ylim(-20, 1)
ax.set_yticks(np.arange(-20, 1, 5))
ax.yaxis.set_major_formatter(plt.FormatStrFormatter("%d"))

# ── Legend above chart ────────────────────────────────────────────────────────
ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, 1.02),
    ncol=2,
    fontsize=10,
    frameon=False,
)

# ── Source line ───────────────────────────────────────────────────────────────
fig.text(
    0.5, -0.02,
    "Source: COMPASS Pathways press release, February 17, 2026",
    ha="center", va="top",
    fontsize=8, color="#666666",
    transform=fig.transFigure,
)

# ── Layout & export ───────────────────────────────────────────────────────────
fig.tight_layout(rect=[0, 0.03, 1, 0.95])

out_path = "/home/pi/Documents/code/quortol/backend/blogs/images/human-fungi-relationship_psilocybin_trials.png"
fig.savefig(out_path, dpi=150)
plt.close(fig)

print(f"Chart saved → {out_path}")
