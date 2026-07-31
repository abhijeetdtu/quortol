import matplotlib.pyplot as plt

ratings = ["5 stars", "4 stars", "3 stars", "2 stars", "1 star"]
counts = [3778, 1453, 407, 116, 59]
percentages = [65, 25, 7, 2, 1]

colors = ["#55A868", "#4C72B0", "#DDCC77", "#E07B39", "#C44E52"]

fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)

bars = ax.bar(ratings, counts, color=colors, edgecolor="white", linewidth=0.5)

ax.set_ylabel("Number of Ratings", fontsize=12, fontweight="bold")
ax.set_xlabel("Rating", fontsize=12, fontweight="bold")
ax.set_title("Goodreads Rating Distribution: Gaban by Munshi Premchand", fontsize=16, fontweight="bold", pad=15)

for bar, count, pct in zip(bars, counts, percentages):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
            f"{count}\n({pct}%)", ha="center", va="bottom", fontsize=10,
            fontweight="bold")

ax.text(0.98, 0.95, "Average: 4.33/5  |  Total: 5,813 ratings",
        transform=ax.transAxes, fontsize=11, va="top", ha="right",
        fontweight="bold", color="#333333",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#F0F0F0", edgecolor="#CCCCCC"))

ax.text(0.98, 0.02, "Source: Goodreads, 'Gaban by Munshi Premchand'",
        transform=ax.transAxes, fontsize=8, va="bottom", ha="right",
        color="#666666", style="italic")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.grid(axis="y", alpha=0.3, linestyle="-")
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("/home/pi/Documents/code/quortol/backend/blogs/images/gaban-influence-hindi-literature_goodreads_rating.png",
            dpi=150, bbox_inches="tight", facecolor="white")
print("Chart 4 saved successfully")
