import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

novels = [
    (1907, "Kishna (lost)"),
    (1916, "Seva Sadan"),
    (1919, "Bazaar-e-Husn"),
    (1922, "Premashram"),
    (1924, "Rangbhoomi"),
    (1925, "Nirmala"),
    (1926, "Pratigya"),
    (1927, "Kaayakalp"),
    (1931, "Gaban"),
    (1932, "Karmabhoomi"),
    (1936, "Godan"),
]

years = [n[0] for n in novels]
titles = [n[1] for n in novels]

colors = ["#4C72B0" if t != "Gaban" else "#E07B39" for t in titles]

fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)

bars = ax.barh(range(len(years)), years, color=colors, edgecolor="white", linewidth=0.5)

ax.set_yticks(range(len(titles)))
ax.set_yticklabels(titles, fontsize=11, fontfamily="serif")
ax.invert_yaxis()

ax.set_xlabel("Publication Year", fontsize=12, fontweight="bold")
ax.set_title("Premchand's Major Novels: 1907-1936", fontsize=16, fontweight="bold", pad=15)

ax.set_xlim(1905, 1940)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))

for bar, year in zip(bars, years):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            str(year), va="center", fontsize=10, fontweight="bold")

ax.axvline(x=1931, color="#E07B39", linestyle="--", linewidth=1.5, alpha=0.7)
ax.text(1931.5, len(titles) - 0.5, "Gaban published", fontsize=9, color="#E07B39",
        fontstyle="italic", va="top")

ax.text(0.98, 0.02, "Source: Wikipedia, Premchand", transform=ax.transAxes,
        fontsize=8, va="bottom", ha="right", color="#666666", style="italic")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.grid(axis="x", alpha=0.3, linestyle="-")
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("/home/pi/Documents/code/quortol/backend/blogs/images/gaban-influence-hindi-literature_novels_timeline.png",
            dpi=150, bbox_inches="tight", facecolor="white")
print("Chart 1 saved successfully")
