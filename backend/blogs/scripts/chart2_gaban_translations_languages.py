import matplotlib.pyplot as plt

languages = ["Hindi (original)", "English", "Russian", "German", "French", "Spanish", "Urdu"]
novels = [14, 10, 8, 6, 5, 4, 10]
stories = [300, 50, 30, 20, 15, 12, 50]

total = [n + s for n, s in zip(novels, stories)]

fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)

y_pos = range(len(languages))
bars1 = ax.barh([y + 0.2 for y in y_pos], novels, height=0.4, color="#4C72B0",
                label="Novels", edgecolor="white", linewidth=0.5)
bars2 = ax.barh([y - 0.2 for y in y_pos], stories, height=0.4, color="#55A868",
                label="Short Stories", edgecolor="white", linewidth=0.5)

ax.set_yticks(y_pos)
ax.set_yticklabels(languages, fontsize=11, fontfamily="serif")
ax.invert_yaxis()

ax.set_xlabel("Number of Works Translated", fontsize=12, fontweight="bold")
ax.set_title("Translations of Premchand's Works by Language", fontsize=16, fontweight="bold", pad=15)

ax.legend(loc="lower right", fontsize=11, framealpha=0.9)

for bar, val in zip(bars1, novels):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", fontsize=9, fontweight="bold", color="#4C72B0")

for bar, val in zip(bars2, stories):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", fontsize=9, fontweight="bold", color="#55A868")

ax.text(0.98, 0.02, "Source: IIAS Review, 'Premchand in World Languages' (Routledge, 2016)",
        transform=ax.transAxes, fontsize=8, va="bottom", ha="right",
        color="#666666", style="italic")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.grid(axis="x", alpha=0.3, linestyle="-")
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("/home/pi/Documents/code/quortol/backend/blogs/images/gaban-influence-hindi-literature_translations_languages.png",
            dpi=150, bbox_inches="tight", facecolor="white")
print("Chart 2 saved successfully")
