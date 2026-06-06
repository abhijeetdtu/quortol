"""
Horizontal bar chart: Effect Sizes from Randomized Trials of Stoic Training
===========================================================================
Cohen's d values from three published RCTs of Stoic-informed interventions.

Sources:
  - King (2024) PhD thesis, Royal Holloway, University of London
  - Brown et al. (2022) BMC Medical Education
  - MacLellan & Derakshan (2021) Cognitive Therapy and Research

Output: 1200 × 720 px PNG at 150 DPI
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Data ──────────────────────────────────────────────────────────────────
data = [
    # (study_label, outcome, d)
    ("Brown et al. (2022)",   "Empathy ↑",                 0.99),
    ("King (2024)",           "Depression ↓",              0.80),
    ("King (2024)",           "Experiential avoidance ↓",  0.75),
    ("MacLellan & Derakshan (2021)", "Rumination ↓",       0.69),
    ("King (2024)",           "Anxiety ↓ (follow-up)",     0.65),
    ("Brown et al. (2022)",   "Stoic ideation ↑",          0.64),
    ("MacLellan & Derakshan (2021)", "Self-efficacy ↑",    0.56),
    ("Brown et al. (2022)",   "Resilience ↑",              0.50),
]

# Sort by d descending (largest at top)
data.sort(key=lambda row: row[2], reverse=True)

# Build display labels
y_labels = [f"{study}" for study, _, _ in data]
outcomes = [outcome for _, outcome, _ in data]
d_vals = [d for _, _, d in data]

# ── Figure setup ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)
fig.patch.set_facecolor("#FAFAFA")
ax.set_facecolor("#FFFFFF")

n = len(data)
y_pos = np.arange(n)

# ── Okabe-Ito colourblind-safe palette ───────────────────────────────────
okabe_ito = {
    "orange":    "#E69F00",
    "sky_blue":  "#56B4E9",
    "bluish_green": "#009E73",
    "yellow":    "#F0E442",
    "blue":      "#0072B2",
    "vermilion": "#D55E00",
    "purple":    "#CC79A7",
    "black":     "#000000",
}

# One colour per study; map each unique study to a palette colour
unique_studies = []
study_colour_map = {}
palette_cycle = [
    okabe_ito["blue"],
    okabe_ito["vermilion"],
    okabe_ito["bluish_green"],
    okabe_ito["purple"],
    okabe_ito["orange"],
    okabe_ito["sky_blue"],
]
for study, _, _ in data:
    if study not in study_colour_map:
        study_colour_map[study] = palette_cycle[len(unique_studies) % len(palette_cycle)]
        unique_studies.append(study)

bar_colours = [study_colour_map[study] for study, _, _ in data]

# ── Horizontal bars ───────────────────────────────────────────────────────
bars = ax.barh(y_pos, d_vals, height=0.55, color=bar_colours, edgecolor="white", linewidth=0.6)

# ── Reference lines ───────────────────────────────────────────────────────
# Medium effect: d = 0.5
ax.axvline(x=0.5, color="#888888", linestyle="--", linewidth=0.9, alpha=0.75)
ax.text(0.5, n - 0.15, "Medium  (d = 0.5)", color="#888888", fontsize=7.5,
        ha="center", va="bottom", style="italic", alpha=0.85)

# Large effect: d = 0.8
ax.axvline(x=0.8, color="#555555", linestyle="--", linewidth=0.9, alpha=0.75)
ax.text(0.8, n - 0.15, "Large  (d = 0.8)", color="#555555", fontsize=7.5,
        ha="center", va="bottom", style="italic", alpha=0.85)

# ── Labels ────────────────────────────────────────────────────────────────
# Study labels on the left (y-axis)
ax.set_yticks(y_pos)
ax.set_yticklabels(y_labels, fontsize=8.5, ha="right")

# Outcome labels positioned inside each bar (right-aligned within bar)
for i, (bar, outcome, d) in enumerate(zip(bars, outcomes, d_vals)):
    # Outcome text inside bar, right-aligned with padding
    label_x = d * 0.70
    if d < 0.15:
        # If bar is too short, place label outside to the right
        label_x = d + 0.04
        ax.text(label_x, y_pos[i], outcome, fontsize=7.5, color="#333333",
                va="center", ha="left")
    else:
        ax.text(label_x, y_pos[i], outcome, fontsize=7.5, color="white",
                va="center", ha="right", fontweight="bold")

    # d value at end of bar
    ax.text(d + 0.025, y_pos[i], f"d = {d:.2f}", fontsize=8, color="#222222",
            va="center", ha="left")

# ── Axes styling ──────────────────────────────────────────────────────────
ax.set_xlim(0, max(d_vals) + 0.25)
ax.set_xlabel("Cohen's d", fontsize=10, color="#444444")
ax.tick_params(axis="x", colors="#444444", labelsize=8.5)
ax.tick_params(axis="y", colors="#444444", labelsize=8.5)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#DDDDDD")
ax.spines["bottom"].set_color("#DDDDDD")
ax.grid(axis="x", color="#EEEEEE", linewidth=0.6)
ax.set_axisbelow(True)

# ── Legend (study colours) ────────────────────────────────────────────────
legend_patches = []
for study_name, colour in study_colour_map.items():
    legend_patches.append(mpatches.Patch(color=colour, label=study_name))

legend = ax.legend(handles=legend_patches, loc="lower right", fontsize=7.5,
                   framealpha=0.9, edgecolor="#DDDDDD", title="Study",
                   title_fontsize=8)

# ── Titles ────────────────────────────────────────────────────────────────
ax.set_title(
    "Effect Sizes from Randomized Trials of Stoic Training",
    fontsize=15, fontweight="bold", color="#1A1A1A", pad=12, loc="left"
)
ax.text(
    0, 1.035,
    "Cohen's d — Clinical significance thresholds shown",
    transform=ax.transAxes, fontsize=9.5, color="#666666",
    va="bottom", ha="left"
)

# ── Source line ───────────────────────────────────────────────────────────
fig.text(
    0.5, -0.025,
    "Sources: King (2024); Brown et al. (2022); MacLellan & Derakshan (2021)",
    fontsize=7.5, color="#888888", ha="center", va="top",
    transform=ax.transAxes
)

# ── Adjust layout ─────────────────────────────────────────────────────────
plt.subplots_adjust(left=0.28, right=0.88, top=0.88, bottom=0.12)

# ── Save ──────────────────────────────────────────────────────────────────
output_path = "/home/pi/Documents/code/quortol/backend/blogs/images/stoicism-science_effect_sizes.png"
fig.savefig(output_path, dpi=150, facecolor=fig.get_facecolor())
plt.close(fig)
print(f"Chart saved → {output_path}")
