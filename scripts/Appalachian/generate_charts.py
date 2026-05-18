import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch
import numpy as np
from PIL import Image
import os

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 16,
    'axes.labelsize': 12,
    'figure.dpi': 200,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.3,
})

root = r'C:\Users\abhij\Code\quortol'

# ──────────────────────────────────────────────
# CHART 1: Elevation Profile
# ──────────────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(12, 7))

states = ['GA', 'TN/NC', 'VA', 'WV', 'MD', 'PA', 'NJ', 'NY', 'CT', 'MA', 'VT', 'NH', 'ME']
climb = [20407, 113904, 136323, 2455, 7296, 29960, 7697, 22569, 12317, 18758, 34532, 53182, 67280]
descent = [20396, 114476, 138409, 3299, 6358, 30857, 7600, 22567, 10941, 18209, 36459, 50615, 65000]

y = np.arange(len(states))
bar_height = 0.6

bars_climb = ax1.barh(y, climb, bar_height, color='#2D6A4F', label='Climb (ft)')
bars_desc = ax1.barh(y, [-d for d in descent], bar_height, color='#8B6F47', label='Descent (ft)')

ax1.set_yticks(y)
ax1.set_yticklabels(states, fontsize=9)
ax1.set_xlabel('Elevation (ft)')
ax1.set_title('The Spine of the East: Elevation Gain and Loss by State', fontsize=15, fontweight='bold', pad=25)
ax1.text(0.5, 1.01, 'Cumulative climb: 526,664 ft \u2014 equivalent to climbing Everest nearly 18 times',
         transform=ax1.transAxes, ha='center', fontsize=10, color='#555555')

ax1.axvline(0, color='black', linewidth=0.8)
ax1.set_xlim(-150000, 150000)

def fmt_k(x, p):
    val = int(abs(x) / 1000)
    return f'{val}k'
ax1.xaxis.set_major_formatter(plt.FuncFormatter(fmt_k))
ax1.xaxis.set_major_locator(ticker.MultipleLocator(20000))

for i in range(len(states)):
    c = climb[i]
    d = descent[i]
    ax1.text(c - 800, i, f'{c/1000:.1f}k', ha='right', va='center', fontsize=7, color='white')
    ax1.text(-d + 800, i, f'{d/1000:.1f}k', ha='left', va='center', fontsize=7, color='white')

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.invert_yaxis()
fig1.tight_layout()
fig1.savefig(os.path.join(root, 'chart1_elevation.png'), dpi=200)
plt.close(fig1)

# ──────────────────────────────────────────────
# CHART 3: Mount Washington Weather
# ──────────────────────────────────────────────
fig3, ax3_left = plt.subplots(figsize=(10, 5.5))

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
snow = [41.6, 43.3, 46.2, 33.1, 12.9, 1.3, 0.0, 0.1, 1.2, 19.0, 35.6, 47.7]
avg_temp = [5.8, 5.9, 12.9, 23.7, 36.3, 45.5, 49.9, 48.7, 43.1, 31.3, 20.8, 11.8]

x = np.arange(len(months))
bar_width = 0.6

ax3_left.bar(x, snow, bar_width, color='#4A6FA5', label='Snowfall (inches)')
ax3_left.set_xlabel('Month')
ax3_left.set_ylabel('Snowfall (inches)', color='#4A6FA5')
ax3_left.tick_params(axis='y', labelcolor='#4A6FA5')
ax3_left.set_xticks(x)
ax3_left.set_xticklabels(months, rotation=45, ha='right')
ax3_left.set_ylim(0, 60)

ax3_right = ax3_left.twinx()
ax3_right.plot(x, avg_temp, color='#C0392B', marker='o', linewidth=2, markersize=5, label='Avg Temperature (°F)')
ax3_right.set_ylabel('Avg Temperature (°F)', color='#C0392B')
ax3_right.tick_params(axis='y', labelcolor='#C0392B')
ax3_right.set_ylim(-10, 60)

ax3_left.axhline(y=32, color='gray', linestyle='--', linewidth=0.8)
ax3_left.text(x[-1], 33, 'Freezing', fontsize=8, color='gray', ha='right')

ax3_left.set_title('Mount Washington: The Worst Weather on Earth', fontsize=14, fontweight='bold', pad=20)
ax3_left.text(0.5, 1.02,
    'Average annual temperature: 28.0\u00b0F | Average annual snowfall: 281.8 in | Highest recorded wind gust: 231 mph',
    transform=ax3_left.transAxes, ha='center', fontsize=9, color='#555555')

annotations = ['Record low: -47\u00b0F', 'Wind gust: 231 mph', 'Wind chill: -108\u00b0F (2023)']
for i, ann in enumerate(annotations):
    ax3_left.text(0.95, 0.95 - i * 0.08, ann, transform=ax3_left.transAxes, ha='right', va='top', fontsize=8,
                  bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

fig3.tight_layout()
fig3.savefig(os.path.join(root, 'chart3_mt_washington.png'), dpi=200)
plt.close(fig3)

# ──────────────────────────────────────────────
# CHART 4: Thru-Hiker Funnel
# ──────────────────────────────────────────────
fig4, ax4 = plt.subplots(figsize=(8, 5))

stages = ['Register intent', 'Start at Springer', 'Reach Harpers Ferry', 'Reach Katahdin']
counts = [3000, 2500, 1250, 800]
colors = ['#D4933A', '#A87B3A', '#6A5A3A', '#2C3E50']

max_count = 3000
y4 = np.arange(len(stages))
bar_height = 0.6

for i in range(len(stages)):
    left_offset = (max_count - counts[i]) / 2
    ax4.barh(i, counts[i], bar_height, left=left_offset, color=colors[i])

ax4.set_xlim(0, 3300)
ax4.set_ylim(-1, len(stages))

for i in range(len(stages)):
    stage = stages[i]
    count = counts[i]
    pct = count / 3000 * 100
    ax4.text(count + 40, i, f'{count:,} ({pct:.0f}%)', va='center', fontsize=10, fontweight='bold')
    text_color = 'white' if i >= 2 else 'black'
    ax4.text(max_count / 2, i, stage, ha='center', va='center', fontsize=9, color=text_color)

ax4.invert_yaxis()
ax4.axis('off')

fig4.suptitle('One in Four: The AT Thru-Hiker Funnel', fontsize=14, fontweight='bold', y=1.02)
fig4.text(0.5, 0.92, 'Of ~3,000 who register each year, roughly 25-33% complete the full 2,197.9 miles',
          ha='center', fontsize=9, color='#555555')

fig4.tight_layout()
fig4.savefig(os.path.join(root, 'chart4_funnel.png'), dpi=200)
plt.close(fig4)

# ──────────────────────────────────────────────
# CHART 5: Statistics Dashboard
# ──────────────────────────────────────────────
fig5, axes = plt.subplots(3, 4, figsize=(14, 9))

stats = [
    ("2,197.9", "TOTAL MILES"),
    ("464,500 ft", "ELEVATION GAIN\n(\u224816\u00d7 EVEREST)"),
    ("14", "STATES\nTRAVERSED"),
    ("5 MILLION", "STEPS TO\nCOMPLETE"),
    ("16.9 MILLION", "ANNUAL\nRECREATION VISITS"),
    ("~3,000", "ANNUAL THRU-HIKE\nATTEMPTS"),
    ("25-33%", "COMPLETION\nRATE"),
    ("176,504", "VOLUNTEER HOURS\nPER YEAR"),
    ("250+", "THREE-SIDED\nSHELTERS"),
    ("30", "TRAIL-MAINTAINING\nCLUBS"),
    ("30.4 lbs", "AVERAGE STARTING\nPACK WEIGHT"),
    ("152 days", "AVERAGE THRU-HIKE\nDURATION"),
]

for idx, (big_num, label) in enumerate(stats):
    row = idx // 4
    col = idx % 4
    ax = axes[row, col]
    ax.set_facecolor('#F5F9F5')
    ax.axis('off')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#2D6A4F')
        spine.set_linewidth(1.5)

    ax.text(0.5, 0.6, big_num, transform=ax.transAxes, ha='center', va='center',
            fontsize=24, fontweight='bold', color='#2D6A4F')
    ax.text(0.5, 0.25, label, transform=ax.transAxes, ha='center', va='center',
            fontsize=9, color='#555555')

fig5.suptitle("The Appalachian Trail by the Numbers", fontsize=18, fontweight='bold', y=0.98)
fig5.text(0.5, 0.93, "Key statistics that define the world's longest hiking-only footpath",
          ha='center', fontsize=11, color='#555555')

plt.subplots_adjust(hspace=0.3, wspace=0.2, top=0.88)
plt.tight_layout(rect=[0, 0, 1, 0.92])
fig5.savefig(os.path.join(root, 'chart5_stats.png'), dpi=200)
plt.close(fig5)

# ──────────────────────────────────────────────
# VERIFICATION
# ──────────────────────────────────────────────
for f in ['chart1_elevation.png', 'chart3_mt_washington.png', 'chart4_funnel.png', 'chart5_stats.png']:
    path = os.path.join(root, f)
    img = Image.open(path)
    arr = np.array(img)
    print(f'{f}: size={img.size}, file={os.path.getsize(path)} bytes, pixel range {arr.min()}-{arr.max()}')
    assert arr.max() != arr.min(), f"BLANK: {f}"
print("ALL CHARTS VERIFIED WITH CONTENT")
