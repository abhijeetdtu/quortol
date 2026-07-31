import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

films = [
    (1938, "Sevasadanam"),
    (1959, "Heera Moti"),
    (1966, "Gaban"),
    (1977, "Shatranj ke Khiladi"),
    (1977, "Oka Oori Katha"),
    (1979, "Saanch Ko Aanch Nahin"),
]

years = [f[0] for f in films]
titles = [f[1] for f in films]

colors = ["#4C72B0" if t != "Gaban" else "#E07B39" for t in titles]

fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)

bars = ax.barh(range(len(years)), years, color=colors, edgecolor="white", linewidth=0.5)

ax.set_yticks(range(len(titles)))
ax.set_yticklabels(titles, fontsize=11, fontfamily="serif")
ax.invert_yaxis()

ax.set_xlabel("Release Year", fontsize=12, fontweight="bold")
ax.set_title("Film Adaptations of Premchand's Novels", fontsize=16, fontweight="bold", pad=15)

ax.set_xlim(1935, 1985)
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))

for bar, year in zip(bars, years):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            str(year), va="center", fontsize=10, fontweight="bold")

ax.text(0.98, 0.02, "Source: Wikipedia, Premchand; Wikipedia, Gaban (film)",
        transform=ax.transAxes, fontsize=8, va="bottom", ha="right",
        color="#666666", style="italic")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.grid(axis="x", alpha=0.3, linestyle="-")
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("/home/pi/Documents/code/quortol/backend/blogs/images/gaban-influence-hindi-literature_film_adaptations.png",
            dpi=150, bbox_inches="tight", facecolor="white")
print("Chart 3 saved successfully")
