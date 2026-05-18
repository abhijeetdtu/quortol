import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os

root = r'C:\Users\abhij\Code\quortol'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 9,
    'axes.titlesize': 13,
    'axes.labelsize': 10,
    'figure.dpi': 200,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.5,
})

# ============================================================
# CHART 1: Elevation Profile
# ============================================================
states = ['GA', 'TN/NC', 'VA', 'WV', 'MD', 'PA', 'NJ', 'NY', 'CT', 'MA', 'VT', 'NH', 'ME']
climb = [20407, 113904, 136323, 2455, 7296, 29960, 7697, 22569, 12317, 18758, 34532, 53182, 67280]
descent = [20396, 114476, 138409, 3299, 6358, 30857, 7600, 22567, 10941, 18209, 36459, 50615, 65000]

fig, ax = plt.subplots(figsize=(14, 9))
ax.barh(range(len(states)), climb, color='#2D6A4F', height=0.6, label='Climb')
ax.barh(range(len(states)), [-d for d in descent], color='#8B6F47', height=0.6, label='Descent')
ax.set_yticks(range(len(states)))
ax.set_yticklabels(states, fontsize=10)
ax.set_ylim(-0.5, len(states) - 0.5)
ax.margins(y=0.1)
ax.set_xlim(-155000, 155000)
for i in range(len(states)):
    ax.text(climb[i] + 2000, i, f'{climb[i]/1000:.1f}k',
            va='center', fontsize=5.5, color='#2D6A4F')
    ax.text(-descent[i] - 2000, i, f'{descent[i]/1000:.1f}k',
            va='center', ha='right', fontsize=5.5, color='#8B6F47')
ax.set_title('The Spine of the East: Elevation Gain and Loss by State', fontsize=15, fontweight='bold', pad=15)
fig.text(0.5, 0.96, 'Cumulative climb: 526,664 ft \u2014 equivalent to climbing Everest nearly 18 times',
         ha='center', fontsize=9, color='#555555')
ax.axvline(x=0, color='#333333', linewidth=0.8)
ax.legend(loc='lower right', fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel('Feet')
plt.tight_layout()
plt.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.05)
fig.savefig(os.path.join(root, 'chart1_elevation.png'), dpi=200, bbox_inches='tight', pad_inches=0.5)
plt.close()
print("Chart 1 done")

# ============================================================
# CHART 3: Mount Washington Weather
# ============================================================
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
temps = [5.8, 5.9, 12.9, 23.7, 36.3, 45.5, 49.9, 48.7, 43.1, 31.3, 20.8, 11.8]
snow = [41.6, 43.3, 46.2, 33.1, 12.9, 1.3, 0.0, 0.1, 1.2, 19.0, 35.6, 47.7]

fig, ax1 = plt.subplots(figsize=(12, 6))
x = range(12)
ax1.bar(x, snow, width=0.5, color='#4A6FA5', alpha=0.7, label='Snowfall (in)')
ax2 = ax1.twinx()
ax2.plot(x, temps, 'o-', color='#C0392B', linewidth=2, markersize=5, label='Avg Temp (\u00b0F)')
ax1.set_xticks(x)
ax1.set_xticklabels(months, fontsize=9)
plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
ax1.set_ylabel('Snowfall (inches)', fontsize=10)
ax2.set_ylabel('Avg Temperature (\u00b0F)', fontsize=10)
ax1.axhline(y=32, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax1.text(0.5, 34, 'Freezing', fontsize=7, color='gray')
props = dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#cccccc')
textstr = '\n'.join((
    'Record low: -47\u00b0F',
    'Wind gust: 231 mph',
    'Wind chill: -108\u00b0F (2023)'))
ax1.text(0.15, 0.85, textstr, transform=ax1.transAxes, fontsize=8,
         verticalalignment='top', bbox=props)
ax1.set_title('Mount Washington: The Worst Weather on Earth', fontsize=14, fontweight='bold', pad=15)
fig.text(0.5, 0.93, 'Average annual temp: 28.0\u00b0F | Avg annual snowfall: 281.8 in | Highest wind gust: 231 mph',
         ha='center', fontsize=8.5, color='#555555')
fig.tight_layout(rect=[0, 0, 1, 0.92])
plt.subplots_adjust(top=0.88)
fig.savefig(os.path.join(root, 'chart3_mt_washington.png'), dpi=200, bbox_inches='tight', pad_inches=0.5)
plt.close()
print("Chart 3 done")

# ============================================================
# CHART 4: Thru-Hiker Funnel
# ============================================================
stages = ['Register intent', 'Start at Springer', 'Reach Harpers Ferry', 'Reach Katahdin']
counts = [3000, 2500, 1250, 800]
pcts = ['(100%)', '(83%)', '(42%)', '(27%)']
colors = ['#D4933A', '#C17D3A', '#4A6FA5', '#2C3E50']

fig, ax = plt.subplots(figsize=(10, 6))
max_w = max(counts)
for i, (stage, count, pct, color) in enumerate(zip(stages, counts, pcts, colors)):
    left = (max_w - count) / 2
    ax.barh(i, count, left=left, height=0.5, color=color, edgecolor='white', linewidth=0.5)
    ax.text(max_w/2, i, stage, ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    ax.text(max_w + 50, i, f'{count:,} {pct}', va='center', fontsize=9, fontweight='bold', color='#333333')
ax.set_xlim(0, max_w + 800)
ax.set_ylim(-0.6, len(stages) - 0.4)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('One in Four: The AT Thru-Hiker Funnel', fontsize=14, fontweight='bold', pad=15)
fig.text(0.5, 0.92, 'Of ~3,000 who register each year, roughly 25-33% complete the full 2,197.9 miles',
         ha='center', fontsize=8.5, color='#555555')
plt.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig(os.path.join(root, 'chart4_funnel.png'), dpi=200, bbox_inches='tight', pad_inches=0.5)
plt.close()
print("Chart 4 done")

# ============================================================
# CHART 5: Statistics Dashboard
# ============================================================
data = [
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
    ("30.4 lbs", "AVG STARTING\nPACK WEIGHT"),
    ("152 days", "AVG THRU-HIKE\nDURATION"),
]

fig, axes = plt.subplots(3, 4, figsize=(16, 10))
axes = axes.flatten()
big_num_color = '#1B4332'
bg_color = '#F0F7F0'
border_color = '#2D6A4F'
for i, (big_num, label) in enumerate(data):
    ax = axes[i]
    ax.set_facecolor(bg_color)
    ax.text(0.5, 0.65, big_num, transform=ax.transAxes, ha='center', va='center',
            fontsize=22, fontweight='bold', color=big_num_color)
    ax.text(0.5, 0.25, label, transform=ax.transAxes, ha='center', va='center',
            fontsize=8.5, color='#555555')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(border_color)
        spine.set_linewidth(2)
fig.suptitle('The Appalachian Trail by the Numbers', fontsize=18, fontweight='bold', y=0.97)
fig.text(0.5, 0.92, 'Key statistics that define the world\'s longest hiking-only footpath',
         ha='center', fontsize=10, color='#555555')
plt.tight_layout(rect=[0, 0, 1, 0.91])
plt.subplots_adjust(hspace=0.35, wspace=0.25)
fig.savefig(os.path.join(root, 'chart5_stats.png'), dpi=200, bbox_inches='tight', pad_inches=0.5)
plt.close()
print("Chart 5 done")

# ============================================================
# VERIFICATION
# ============================================================
print("\n=== VERIFICATION ===")
for f in ['chart1_elevation.png', 'chart3_mt_washington.png', 'chart4_funnel.png', 'chart5_stats.png']:
    path = os.path.join(root, f)
    img = Image.open(path)
    arr = np.array(img)
    size_kb = os.path.getsize(path) / 1024
    print(f'{f}: {img.size} = {size_kb:.0f} KB, pixel range {arr.min()}-{arr.max()}')
    assert arr.max() > arr.min(), f"BLANK: {f}"

img5 = Image.open(r'C:\Users\abhij\Code\quortol\chart5_stats.png')
arr5 = np.array(img5)
non_white = np.sum(np.any(arr5[:,:,:3] < 240, axis=2))
total = arr5.shape[0] * arr5.shape[1]
pct = non_white / total * 100
print(f'Chart5 ink density: {pct:.1f}%')
if pct < 3:
    print('WARNING: Chart 5 may still be too sparse')
else:
    print('Chart 5 ink density looks good')

print('ALL CHARTS VERIFIED')
