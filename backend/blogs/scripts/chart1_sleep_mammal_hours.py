#!/usr/bin/env python3
"""
Chart: Total Daily Sleep Time Across Species
Output: ../images/sleep_mammal_hours.png  (1200 × 720 px, 150 DPI)

Horizontal bar chart of total daily sleep hours across mammal species,
color-coded by diet category with a colorblind-safe palette.

Data: Siegel (2005) Nature; McNamara et al. (2008) Phylogeny of Sleep Database
"""

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ============================================================================
# 1. DATA
# ============================================================================
df = pd.DataFrame({
    "species": [
        "Big brown bat", "Armadillo", "Opossum", "Cat", "Fox",
        "Chimpanzee", "Human", "Guinea pig", "Rat", "Pig",
        "Sheep", "Cow", "Horse", "Donkey", "Elephant",
        "Giraffe", "Dolphin", "Frigatebird", "Platypus",
    ],
    "sleep_hours": [
        19.9, 20.0, 19.4, 12.5, 9.8,
        9.7, 7.0, 9.4, 12.6, 8.4,
        4.0, 3.9, 2.9, 3.0, 3.5,
        4.5, 5.4, 0.7, 14.0,
    ],
    "diet": [
        "Insectivore", "Insectivore", "Omnivore", "Carnivore", "Carnivore",
        "Omnivore", "Omnivore", "Herbivore", "Omnivore", "Omnivore",
        "Herbivore", "Herbivore", "Herbivore", "Herbivore", "Herbivore",
        "Herbivore", "Carnivore", "Piscivore", "Carnivore",
    ],
})

# ============================================================================
# 2. ORDERING — shortest sleep at TOP of chart
# ============================================================================
species_order = df.sort_values("sleep_hours")["species"].tolist()
# Ascending order: [Frigatebird, Horse, Donkey, … , Armadillo]
# Reverse so that 1st level = longest sleep (bottom), last level = shortest (top)
df["species"] = pd.Categorical(
    df["species"],
    categories=species_order[::-1],
    ordered=True,
)

# ============================================================================
# 3. COLORBLIND-SAFE PALETTE  (Okabe-Ito / Wong 2011)
# ============================================================================
diet_colors = {
    "Herbivore":   "#CC79A7",   # pink
    "Carnivore":   "#009E73",   # bluish green
    "Omnivore":    "#56B4E9",   # sky blue
    "Insectivore": "#E69F00",   # orange
    "Piscivore":   "#0072B2",   # dark blue
}

# ============================================================================
# 4. ANNOTATION DATA  (average mammal line label)
# ============================================================================
vline_label = pd.DataFrame({
    "species":     ["Frigatebird"],            # top of chart, plenty of room
    "sleep_hours": [12.3],                    # just right of the 11.7 line
    "label":       ["Average mammal: 11.7 h"],
})

# ============================================================================
# 5. BUILD THE PLOT
# ============================================================================
p = (
    ggplot(df, aes(x="sleep_hours", y="species", fill="diet"))
    + geom_bar(stat="identity", width=0.7)
    + scale_fill_manual(values=diet_colors, name="Diet")

    # ---- Average mammal reference line + label ----
    + geom_vline(xintercept=11.7, linetype="dashed", color="#555555", size=0.7)
    + geom_text(
        aes(x="sleep_hours", y="species", label="label"),
        data=vline_label,
        color="#555555", size=9, hjust=0, family="sans",
    )

    # ---- Labels ----
    + labs(
        title="Total Daily Sleep Time Across Species",
        subtitle="Hours of sleep per 24-hour period",
        x="Hours per day",
        y="",
        caption=(
            "Source: Siegel (2005) Nature; "
            "McNamara et al. (2008) Phylogeny of Sleep Database\n"
            "* Dolphin: unihemispheric sleep; "
            "approx. half of typical bihemispheric measurement"
        ),
    )

    # ---- Scales ----
    + scale_x_continuous(
        breaks=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        limits=(0, 22),
    )

    # ---- Theme ----
    + theme_minimal()
    + theme(
        # Italic species names on y-axis
        axis_text_y       = element_text(face="italic", size=11),
        axis_text_x       = element_text(size=10),
        axis_title_x      = element_text(size=12, margin=[8, 0, 0, 0]),
        # Title block
        plot_title        = element_text(size=18, face="bold"),
        plot_subtitle     = element_text(size=13, color="#555555"),
        plot_caption      = element_text(
            size=8, color="#888888", margin=[10, 0, 0, 0]
        ),
        # Only horizontal gridlines
        panel_grid_major_x = element_blank(),
        panel_grid_minor_x = element_blank(),
        panel_grid_major_y = element_line(color="#e0e0e0", size=0.4),
        panel_grid_minor_y = element_blank(),
        # Legend
        legend_position   = "right",
        legend_title      = element_text(size=11, face="bold"),
        legend_text       = element_text(size=10),
        # Margins (top, right, bottom, left)
        plot_margin       = [15, 20, 10, 15],
    )
)

# ============================================================================
# 6. SAVE PNG  — 1200 × 720 px @ 150 DPI  →  8 × 4.8 in
# ============================================================================
output_path = (
    "/home/pi/Documents/code/quortol/backend/blogs/images/"
    "sleep_mammal_hours.png"
)
ggsave(p, output_path, w=8, h=4.8, unit="in", dpi=150)

print(f"✓ Chart saved to {output_path}")
print(f"  Dimensions: 1200 × 720 px  @  150 DPI")
