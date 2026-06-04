#!/usr/bin/env python3
"""
Chart 2: Major vs. Minor chord ratio comparison.

Two-panel visualization showing sine-wave alignment for:
  - Major triad  (4:5:6  →  400 / 500 / 600 Hz)
  - Minor triad  (10:12:15  →  500 / 600 / 750 Hz)

Vertical dashed lines mark LCM-period boundaries where all three waves
return to the same phase (pattern repeats).  The major triad has more
frequent alignment → perceived as consonant / stable.

Output: 1200 × 720 px PNG, 150 DPI
"""

from pathlib import Path

import numpy as np
import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------
script_path = Path(__file__).resolve()
images_dir = script_path.parent.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_png = images_dir / "hidden-math-in-what-you-hear_chord_ratios.png"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
DURATION = 0.02           # seconds — ~8–10 cycles of the root
SR = 50_000               # sample rate (Hz) — smooth curves
t = np.arange(0, DURATION, 1 / SR)

# Colorblind-safe palette (Tableau 10 — three distinguishable hues)
COLOR_ROOT  = "#E15759"   # reddish
COLOR_THIRD = "#4E79A7"   # blue
COLOR_FIFTH = "#59A14F"   # green

# ---------------------------------------------------------------------------
# Build dataset for both chords
# ---------------------------------------------------------------------------
chord_defs = [
    {
        "label":     "Major Chord (4:5:6)",
        "freqs":     [400, 500, 600],
        "root_hz":   400,
        "note_labs": ["Root (400 Hz, 4\u00d7)",
                       "Major Third (500 Hz, 5\u00d7)",
                       "Perfect Fifth (600 Hz, 6\u00d7)"],
        "lcm":       0.01,            # 1 / gcd(400, 500, 600)
        "annotation":
            "Frequent alignment \u2014 consonant, stable",
    },
    {
        "label":     "Minor Chord (10:12:15)",
        "freqs":     [500, 600, 750],
        "root_hz":   500,
        "note_labs": ["Root (500 Hz, 10\u00d7)",
                       "Minor Third (600 Hz, 12\u00d7)",
                       "Perfect Fifth (750 Hz, 15\u00d7)"],
        "lcm":       0.02,            # 1 / gcd(500, 600, 750)
        "annotation":
            "Sparser alignment \u2014 more complex, searching",
    },
]

wave_rows = []
align_rows = []
annot_rows = []

for cd in chord_defs:
    root = cd["root_hz"]
    # colours per note role (not per chord)
    note_colors = [COLOR_ROOT, COLOR_THIRD, COLOR_FIFTH]

    # ── Sine waves ───────────────────────────────────────────────────────
    for freq, nlab, col in zip(cd["freqs"], cd["note_labs"], note_colors):
        wave_rows.append(pd.DataFrame({
            "cycles":     t * root,          # x-axis in root cycles
            "amplitude":  np.sin(2 * np.pi * freq * t),
            "note":       nlab,
            "chord":      cd["label"],
        }))

    # ── Alignment lines (LCM-period boundaries) ─────────────────────────
    align_times = np.arange(0, DURATION + cd["lcm"] * 0.5, cd["lcm"])
    for at in align_times:
        align_rows.append(pd.DataFrame({
            "xintercept": [at * root],
            "chord":      [cd["label"]],
        }))

    # ── Annotation text (centred below the waves) ──────────────────────
    x_mid = DURATION * root / 2
    annot_rows.append(pd.DataFrame({
        "chord":      [cd["label"]],
        "cycles":     [x_mid],
        "amplitude":  [-1.6],
        "label":      [cd["annotation"]],
    }))

df_wave  = pd.concat(wave_rows,  ignore_index=True)
df_align = pd.concat(align_rows, ignore_index=True)
df_annot = pd.concat(annot_rows, ignore_index=True)

# ---------------------------------------------------------------------------
# Manual colour scale (shared hue-per-role across both chords)
# ---------------------------------------------------------------------------
color_scale = {
    "Root (400 Hz, 4\u00d7)":       COLOR_ROOT,
    "Major Third (500 Hz, 5\u00d7)": COLOR_THIRD,
    "Perfect Fifth (600 Hz, 6\u00d7)": COLOR_FIFTH,
    "Root (500 Hz, 10\u00d7)":       COLOR_ROOT,
    "Minor Third (600 Hz, 12\u00d7)": COLOR_THIRD,
    "Perfect Fifth (750 Hz, 15\u00d7)": COLOR_FIFTH,
}

# ---------------------------------------------------------------------------
# Build plot
# ---------------------------------------------------------------------------
p = (
    ggplot()
    # Sine waves
    + geom_line(
        aes(x="cycles", y="amplitude", color="note"),
        data=df_wave, size=0.65,
    )
    # Alignment lines
    + geom_vline(
        aes(xintercept="xintercept"),
        data=df_align,
        linetype="dashed",
        color="#777777",
        alpha=0.45,
        size=0.5,
    )
    # Annotation labels below each panel
    + geom_text(
        aes(x="cycles", y="amplitude", label="label"),
        data=df_annot,
        size=3.5,               # ≈ 10 pt
        color="#333333",
        fontface="italic",
        va="top",               # text grows downward from y
    )
    # Facet into two columns
    + facet_wrap(facets="chord", ncol=2, scales="free_x")
    # Colour
    + scale_color_manual(values=color_scale, name="Note")
    # Titles & labels
    + labs(
        title    = "Major vs. Minor: The Ratio Difference",
        subtitle = ("Major chord 4:5:6 (left) offers more frequent wave "
                     "alignment than minor chord 10:12:15 (right)"),
        x        = "Time (cycles)",
        y        = "Amplitude",
        caption  = "Data: Overtone series ratios from Roberts (2018), Holy Cross",
    )
    # Make room for annotation text below the waves
    + coord_cartesian(ylim=[-1.85, 1.25])
    # Clean theme
    + theme_minimal()
    + theme(
        # Titles
        plot_title      = element_text(size=14, hjust=0.5, face="bold",
                                       color="#1a1a1a"),
        plot_subtitle   = element_text(size=9.5, hjust=0.5,
                                       color="#555555"),
        # Axis labels
        axis_title_x    = element_text(size=10, color="#333333"),
        axis_title_y    = element_text(size=10, color="#333333"),
        axis_text_x     = element_text(size=8,  color="#444444"),
        axis_text_y     = element_text(size=8,  color="#444444"),
        # Strip / facet labels
        strip_text      = element_text(size=11, face="bold",
                                       color="#222222"),
        strip_background = element_rect(fill="#F0F0F0", color=None),
        # Caption
        plot_caption    = element_text(size=8, color="#888888",
                                       hjust=0, face="italic"),
        # Legend
        legend_position = "bottom",
        legend_title    = element_text(size=9, color="#333333"),
        legend_text     = element_text(size=8, color="#555555"),
        # Grid: faint horizontal only
        panel_grid_major_x = element_blank(),
        panel_grid_major_y = element_line(color="#EEEEEE", size=0.3),
        panel_grid_minor   = element_blank(),
        # Axes lines
        axis_line       = element_line(color="#CCCCCC"),
        axis_ticks      = element_line(color="#CCCCCC"),
        # Backgrounds: white
        panel_background = element_rect(fill="#FAFAFA", color=None),
        plot_background  = element_rect(fill="white",   color=None),
        # Margins (top, right, bottom, left)
        plot_margin     = [10, 25, 5, 15],
    )
)

# ---------------------------------------------------------------------------
# Save — 1200 × 720 px at 150 DPI → 8 × 4.8 inches
# ---------------------------------------------------------------------------
ggsave(p, str(output_png), w=8, h=4.8, unit="in", dpi=150)

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
if output_png.exists():
    size_kb = output_png.stat().st_size / 1024
    print(f"Saved: {output_png}")
    print(f"  Dimensions: 1200 × 720 px @ 150 DPI")
    print(f"  File size:  {size_kb:.1f} KB")
else:
    print(f"ERROR: file was not created at {output_png}")
