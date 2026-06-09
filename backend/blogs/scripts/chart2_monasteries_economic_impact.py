"""
Horizontal bar chart: Annual economic impact of major monastic & pilgrimage sites.

Data sources:
  - Santiago de Compostela: WUR study (2017) — https://edepot.wur.nl/442744
  - Torreciudad Sanctuary: Huesca Chamber of Commerce (2024)
    https://exaudi.org/the-torreciudad-sanctuary-generates-an-annual-economic-impact-of-97-million-euros-in-the-province-of-huesca-and-aragon/
  - Kylemore Abbey: Fitzpatrick Associates (2024)
    https://www.travelandtourworld.com/news/article/kylemore-abbey-impact-on-galway-mayo-region-economic-boost-and-sustainable-growth-in-ireland/
  - Medjugorje: Regional economic analysis (2024)
    https://tragento.com/en/analysis-of-pilgrimage-tourism-in-Southeast-Europe/
  - English Cathedrals (42 sites): English Cathedrals study (2019)
    https://www.englishcathedrals.co.uk/wp-content/uploads/2021/08/Economic-Social-Impacts-of-Englands-Cathedrals-2019.pdf
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

# ── Data ──────────────────────────────────────────────────────────────────────
sites = [
    "English Cathedrals\n(42 sites, England, UK)",
    "Santiago de Compostela\n(Camino, Galicia, Spain)",
    "Torreciudad Sanctuary\n(Huesca, Spain)",
    "Kylemore Abbey\n(Galway, Ireland)",
    "Medjugorje\n(Bosnia-Herzegovina)",
]

values = [235, 100, 97, 91.5, 90]

# ── Colour palette (colorblind-safe) ─────────────────────────────────────────
# Warm orange for single sites, neutral grey for the composite entry.
SINGLE_SITE_COLOUR = "#E8843B"
COMPOSITE_COLOUR = "#888888"

bar_colours = []
for v in values:
    if v == 235:  # English Cathedrals is the composite
        bar_colours.append(COMPOSITE_COLOUR)
    else:
        bar_colours.append(SINGLE_SITE_COLOUR)

# ── Output directories ───────────────────────────────────────────────────────
script_dir = Path(__file__).parent
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_png = images_dir / "monasteries_economic_impact.png"

# ── Figure setup ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(1200 / 150, 720 / 150))  # 1200x720 px at 150 DPI
fig.set_dpi(150)

# ── Horizontal bars (sorted descending → top row = largest) ─────────────────
bars = ax.barh(
    range(len(sites)),
    values,
    height=0.55,
    color=bar_colours,
    edgecolor="none",
    zorder=3,
)

# ── Y-axis ───────────────────────────────────────────────────────────────────
ax.set_yticks(range(len(sites)))
ax.set_yticklabels(sites, fontsize=9, fontfamily="sans-serif")
ax.invert_yaxis()  # largest bar at top

# ── X-axis ───────────────────────────────────────────────────────────────────
ax.set_xlim(0, 270)
ax.set_xlabel("€ millions", fontsize=10, fontfamily="sans-serif")
ax.xaxis.set_major_locator(mticker.MultipleLocator(50))
ax.xaxis.set_minor_locator(mticker.MultipleLocator(10))
ax.grid(axis="x", which="major", color="#cccccc", linewidth=0.5, zorder=0)
ax.grid(axis="x", which="minor", color="#e6e6e6", linewidth=0.3, zorder=0)
ax.tick_params(axis="x", labelsize=8)

# Remove y-axis gridlines
ax.grid(axis="y", which="both", visible=False)

# ── Data labels ──────────────────────────────────────────────────────────────
for i, (v, bar) in enumerate(zip(values, bars)):
    ax.text(
        v + 3,
        i,
        f"€{v:g}M" if v == int(v) else f"€{v}M",
        va="center",
        fontsize=9,
        fontfamily="sans-serif",
        color="#333333",
    )

# ── Titles & subtitle ────────────────────────────────────────────────────────
ax.set_title(
    "Annual Economic Impact of Major Monastic & Pilgrimage Sites",
    fontsize=14,
    fontweight="bold",
    fontfamily="sans-serif",
    pad=12,
    loc="left",
)

ax.text(
    x=0,
    y=1.02,
    s="Direct, indirect, and induced contributions to local economies",
    transform=ax.transAxes,
    fontsize=9,
    fontfamily="sans-serif",
    color="#555555",
    va="bottom",
    ha="left",
)

# ── Source line ──────────────────────────────────────────────────────────────
ax.text(
    x=0,
    y=-0.12,
    s="Sources: Regional economic impact studies (2010–2024)",
    transform=ax.transAxes,
    fontsize=7,
    fontfamily="sans-serif",
    color="#888888",
    va="top",
    ha="left",
)

# ── Spines ───────────────────────────────────────────────────────────────────
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color("#cccccc")
ax.spines["bottom"].set_linewidth(0.5)

# ── Layout & export ──────────────────────────────────────────────────────────
fig.tight_layout()

fig.savefig(
    output_png,
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
    edgecolor="none",
    pad_inches=0.15,
)

plt.close(fig)

print(f"Chart saved to: {output_png.resolve()}")
