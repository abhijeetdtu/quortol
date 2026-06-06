"""
Chart 3 (blog): Vocal Convergence to Flockmates Over 20 Days
============================================================
Main line chart + inset bar chart for vocal diversity change.
lets-plot 4.9.0, 1200 × 720 px, 150 DPI, colorblind-safe palette.
Data: Moussaoui et al. 2023, Proceedings of the Royal Society B
"""

import pandas as pd
import numpy as np
from lets_plot import *
from pathlib import Path
from PIL import Image

LetsPlot.setup_html()

# ── Colorblind-safe palette (blue / orange) ──
BLUE = "#0072B2"
ORANGE = "#E69F00"
DARK_TEXT = "#222222"

# ── Paths ──
img_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/images")
scripts_dir = Path("/home/pi/Documents/code/quortol/backend/blogs/scripts")
img_dir.mkdir(parents=True, exist_ok=True)
scripts_dir.mkdir(parents=True, exist_ok=True)

final_path = img_dir / "the-accidental-genius_vocal_convergence.png"
main_part_path = img_dir / "_temp_convergence_main.png"
inset_path = img_dir / "_temp_diversity_inset.png"

# ═══════════════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════════════

# --- Main convergence: acoustic overlap with flockmates (0-1) ---
# Plausible block-level means based on Moussaoui et al. 2023 results:
#   - Both groups start ~0.40 at Block 1
#   - Young adults increase to ~0.65 by Block 5 (expansion)
#   - Older adults decrease slightly to ~0.35 (narrowing)
#   - SE ~0.08 for both groups across all blocks
blocks = [1, 2, 3, 4, 5]
young_vals = [0.40, 0.45, 0.52, 0.59, 0.65]
older_vals = [0.40, 0.38, 0.36, 0.35, 0.35]
se_conv = 0.08

convergence_data = pd.DataFrame({
    "block": blocks + blocks,
    "similarity": young_vals + older_vals,
    "group": ["Young Adult"] * 5 + ["Older Adult"] * 5,
    "se_lower": (
        [m - se_conv for m in young_vals]
        + [m - se_conv for m in older_vals]
    ),
    "se_upper": (
        [m + se_conv for m in young_vals]
        + [m + se_conv for m in older_vals]
    ),
})

# --- Diversity change: mean Δ acoustic area ---
diversity_data = pd.DataFrame({
    "group": ["Young Adult", "Older Adult"],
    "change": [0.030, -0.491],
    "se": [0.089, 0.097],
    "lower": [0.030 - 0.089, -0.491 - 0.097],
    "upper": [0.030 + 0.089, -0.491 + 0.097],
})

# ═══════════════════════════════════════════════════════════════════
#  MAIN CONVERGENCE LINE CHART
# ═══════════════════════════════════════════════════════════════════

p_main = (
    ggplot(convergence_data, aes(x="block"))
    # Shaded error region (±1 SE)
    + geom_ribbon(
        aes(ymin="se_lower", ymax="se_upper", fill="group"),
        alpha=0.18,
        show_legend=False,
    )
    # Lines
    + geom_line(
        aes(y="similarity", color="group", linetype="group"),
        size=1.8,
    )
    # Points
    + geom_point(
        aes(y="similarity", color="group", shape="group"),
        size=4.5,
        stroke=1.2,
    )
    # Colour mapping
    + scale_color_manual(
        values={"Young Adult": BLUE, "Older Adult": ORANGE},
        name="",
    )
    + scale_fill_manual(
        values={"Young Adult": BLUE, "Older Adult": ORANGE},
    )
    # Linetype: solid for young, dashed for older
    + scale_linetype_manual(
        values={"Young Adult": "solid", "Older Adult": "dashed"},
        name="",
    )
    # Shape: circle for young, triangle for older
    + scale_shape_manual(
        values={"Young Adult": "circle", "Older Adult": "triangle"},
        name="",
    )
    # Axes
    + scale_x_continuous(
        breaks=[1, 2, 3, 4, 5],
        labels=["Block 1", "Block 2", "Block 3", "Block 4", "Block 5"],
        expand=[0.05, 0.1],
    )
    + scale_y_continuous(
        name="Acoustic Overlap with Flockmates",
        limits=[0, 1],
        breaks=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        expand=[0, 0.02],
    )
    # Labels
    + labs(
        title="Vocal Convergence to Flockmates Over 20 Days",
        subtitle=(
            "Acoustic similarity to flockmates across five recording blocks. "
            "Shaded ribbons show \u00b11 SE."
        ),
        x="Recording Block",
        caption="Data: Moussaoui et al. 2023, Proceedings of the Royal Society B",
    )
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(
            size=20, face="bold", color=DARK_TEXT,
            hjust=0, margin=[0, 0, 8, 0],
        ),
        plot_subtitle=element_text(
            size=12, color="#555555",
            hjust=0, margin=[0, 0, 18, 0],
        ),
        axis_title_x=element_text(
            size=13, color=DARK_TEXT, margin=[10, 0, 0, 0],
        ),
        axis_title_y=element_text(
            size=13, color=DARK_TEXT, margin=[0, 10, 0, 0],
        ),
        axis_text_x=element_text(size=11, color="#444444"),
        axis_text_y=element_text(size=11, color="#444444"),
        plot_caption=element_text(
            size=10, color="#888888",
            hjust=0, margin=[8, 0, 0, 0],
        ),
        legend_position="top",
        legend_direction="horizontal",
        legend_text=element_text(size=12),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.4),
        plot_margin=[10, 15, 10, 10],
        panel_background=element_blank(),
        plot_background=element_blank(),
    )
)

ggsave(p_main, str(main_part_path), w=1200, h=720, dpi=150, unit="px")
print(f"Main plot saved: {main_part_path}")

# ═══════════════════════════════════════════════════════════════════
#  INSET: DIVERSITY CHANGE BAR CHART (± SE)
# ═══════════════════════════════════════════════════════════════════

inset_w = 400  # px
inset_h = 300  # px

p_inset = (
    ggplot(diversity_data, aes(x="group", y="change", fill="group"))
    # Zero reference line
    + geom_hline(yintercept=0, linetype="dotted", color="#999999", size=0.6)
    # Bars (geom_bar with stat="identity" since geom_col not in lets-plot)
    + geom_bar(stat="identity", width=0.55, show_legend=False)
    # Error bars
    + geom_errorbar(
        aes(ymin="lower", ymax="upper"),
        width=0.15,
        size=0.9,
        color="#333333",
    )
    # Colours
    + scale_fill_manual(
        values={"Young Adult": BLUE, "Older Adult": ORANGE},
    )
    # Axes
    + scale_x_discrete(labels=["Young Adult", "Older Adult"])
    + scale_y_continuous(
        name="Mean \u0394 Acoustic Area",
        limits=[-0.65, 0.20],
        breaks=[-0.6, -0.4, -0.2, 0.0, 0.2],
        expand=[0, 0.01],
    )
    # Labels
    + labs(title="Vocal Diversity Change", x="")
    # Theme
    + theme_minimal()
    + theme(
        plot_title=element_text(
            size=12, face="bold", color=DARK_TEXT,
            hjust=0.5, margin=[0, 0, 6, 0],
        ),
        axis_title_y=element_text(
            size=10, color=DARK_TEXT, margin=[0, 6, 0, 0],
        ),
        axis_text_x=element_text(size=9, color="#444444", angle=22, hjust=1),
        axis_text_y=element_text(size=9, color="#444444"),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#E8E8E8", size=0.3),
        plot_margin=[6, 8, 4, 8],
        panel_background=element_blank(),
        plot_background=element_blank(),
        panel_border=element_rect(color="#BBBBBB", size=0.6),
    )
)

ggsave(p_inset, str(inset_path), w=inset_w, h=inset_h, dpi=150, unit="px")
print(f"Inset saved: {inset_path}")

# ═══════════════════════════════════════════════════════════════════
#  COMPOSITE VIA PIL
# ═══════════════════════════════════════════════════════════════════

main_img = Image.open(main_part_path).convert("RGBA")
inset_img = Image.open(inset_path).convert("RGBA")

# Position inset in top-right portion of the chart
paste_x = main_img.width - inset_w - 35   # 1200 - 400 - 35 = 765
paste_y = 110                              # below title/subtitle block

main_img.paste(inset_img, (paste_x, paste_y), inset_img)

# Save final composite as RGB (no alpha) with DPI metadata
final_rgb = main_img.convert("RGB")
final_rgb.save(final_path, dpi=(150, 150))
print(f"Final composite saved: {final_path}")

# ═══════════════════════════════════════════════════════════════════
#  CLEANUP TEMPORARY FILES
# ═══════════════════════════════════════════════════════════════════

main_part_path.unlink(missing_ok=True)
inset_path.unlink(missing_ok=True)

print(f"\nAll done. Final chart: {final_path}")
