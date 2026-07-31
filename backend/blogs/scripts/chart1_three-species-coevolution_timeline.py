#!/usr/bin/env python3
"""
Three-Species Coevolution Timeline
===================================
Horizontal timeline chart showing domestication milestones of dogs, cats,
and humans, using lets-plot.

Output: 1200x720 px PNG at 150 DPI
"""

import pandas as pd
from pathlib import Path
from lets_plot import *

LetsPlot.setup_html()

# ── Data ──────────────────────────────────────────────────────────────────────
events = [
    # (species, event_label, years_ago)
    # --- Dog events ---
    ("Dog",   "Wolf-dog genetic divergence",         33000),
    ("Dog",   "First dog remains (Bonn-Oberkassel)", 17500),
    ("Dog",   "Dog burials with humans",             14000),
    ("Dog",   "Dog reaches Japan",                   9000),
    ("Dog",   "Dogs in Americas",                    3500),
    # --- Cat events ---
    ("Cat",   "Cat domestication (Fertile Crescent)", 10000),
    ("Cat",   "Cat buried with human (Cyprus)",       9500),
    ("Cat",   "Cat remains in Bulgaria",              6400),
    ("Cat",   "Egyptian cat maritime dispersal",      2000),
    ("Cat",   "Tabby coat pattern emerges",           1000),
    # --- Human self-domestication events ---
    ("Human", "Homo sapiens appears",                300000),
    ("Human", "Facial shortening begins",            200000),
    ("Human", "Behavioral modernity",                100000),
    ("Human", "Agricultural revolution",              12000),
]

df = pd.DataFrame(events, columns=["species", "event", "years_ago"])

# Order species on y-axis (top to bottom: Human, Dog, Cat)
species_order = ["Human", "Dog", "Cat"]
df["species"] = pd.Categorical(df["species"], categories=species_order, ordered=True)

# Numeric y coordinates (0 = top, 1 = middle, 2 = bottom)
df["y"] = df["species"].cat.codes.astype(float)

# Sort for consistent ordering
df = df.sort_values(["species", "years_ago"], ascending=[True, False]).reset_index(drop=True)

# ── Timeline base segments (horizontal line for each species) ─────────────────
timeline_segments = pd.DataFrame({
    "species": species_order,
    "x_start": [0, 0, 0],
    "x_end":   [300000, 33000, 10000],
    "y":       [0.0, 1.0, 2.0],
})

# ── Explicit label positions (pre-computed, no nudge needed) ──────────────────
# Each label offset alternates above/below the species line
label_y_offsets = {
    ("Dog",   "Wolf-dog genetic divergence"):         -0.35,
    ("Dog",   "First dog remains (Bonn-Oberkassel)"):  0.35,
    ("Dog",   "Dog burials with humans"):              -0.35,
    ("Dog",   "Dog reaches Japan"):                    0.35,
    ("Dog",   "Dogs in Americas"):                     -0.35,
    ("Cat",   "Cat domestication (Fertile Crescent)"): -0.35,
    ("Cat",   "Cat buried with human (Cyprus)"):        0.35,
    ("Cat",   "Cat remains in Bulgaria"):               -0.35,
    ("Cat",   "Egyptian cat maritime dispersal"):        0.35,
    ("Cat",   "Tabby coat pattern emerges"):            -0.35,
    ("Human", "Homo sapiens appears"):                  -0.35,
    ("Human", "Facial shortening begins"):               0.35,
    ("Human", "Behavioral modernity"):                  -0.35,
    ("Human", "Agricultural revolution"):                0.35,
}

df["label_y"] = df.apply(
    lambda r: r["y"] + label_y_offsets[(r["species"], r["event"])], axis=1
)

# ── Colour palette (colorblind-safe) ─────────────────────────────────────────
palette = {
    "Dog":   "#0077BB",   # blue
    "Cat":   "#EE7733",   # orange
    "Human": "#009988",   # teal
}

# ── Build chart ──────────────────────────────────────────────────────────────
p = (
    ggplot()
    # --- Horizontal timeline lines ---
    + geom_segment(
        aes(x="x_start", xend="x_end", y="y", yend="y", color="species"),
        data=timeline_segments,
        size=2.0, alpha=0.25,
    )
    # --- Event markers (diamond) ---
    + geom_point(
        aes(x="years_ago", y="y", color="species"),
        data=df,
        shape=18,
        size=5.5,
    )
    # --- Event labels at pre-computed y positions ---
    + geom_text(
        aes(x="years_ago", y="label_y", label="event"),
        data=df,
        hjust=0,
        vjust="middle",
        size=8.5,
        family="sans",
        color="#222222",
    )
    # --- X-axis (years before present) ---
    + scale_x_continuous(
        breaks=[0, 50000, 100000, 150000, 200000, 250000, 300000],
        labels=["0", "50k", "100k", "150k", "200k", "250k", "300k"],
        limits=[0, 450000],
    )
    # --- Y-axis (species labels) ---
    + scale_y_continuous(
        breaks=[0, 1, 2],
        labels=["Human", "Dog", "Cat"],
        limits=[-1.0, 3.0],
    )
    # --- Color scale (species -> hex) ---
    + scale_color_manual(values=palette, name=" ")
    # --- Labels & titles ---
    + labs(
        title="Three-Species Coevolution Timeline",
        subtitle="Domestication milestones of dogs, cats, and humans",
        x="Years before present",
        y="",
        caption="Data from primary academic sources (Science, Nature, PNAS, etc.)",
    )
    # --- Theme ---
    + theme_minimal()
    + theme(
        plot_title         = element_text(size=18, face="bold", hjust=0),
        plot_subtitle      = element_text(size=12, color="#666666",
                                          hjust=0, margin=[0, 0, 15, 0]),
        plot_caption       = element_text(size=8.5, color="#999999", hjust=1),
        axis_title_x       = element_text(size=11),
        axis_text_x        = element_text(size=10),
        axis_text_y        = element_text(size=13, face="bold"),
        legend_position    = "none",
        panel_grid_major_x = element_line(color="#E8E8E8", size=0.4),
        panel_grid_minor_x = element_blank(),
        panel_grid_major_y = element_blank(),
        panel_grid_minor_y = element_blank(),
        panel_background   = element_blank(),
        plot_margin        = [10, 25, 10, 10],
    )
)

# ── Save ─────────────────────────────────────────────────────────────────────
script_path = Path(__file__).resolve()
img_dir = script_path.parent.parent / "images"
img_dir.mkdir(parents=True, exist_ok=True)

png_path = img_dir / "three-species-coevolution_timeline.png"
p.to_png(str(png_path), w=8, h=4.8, unit="in", dpi=150, scale=1.0)

print(f"Chart saved to: {png_path.resolve()}")
print(f"Dimensions: 1200 x 720 px at 150 DPI")
print("Done.")
