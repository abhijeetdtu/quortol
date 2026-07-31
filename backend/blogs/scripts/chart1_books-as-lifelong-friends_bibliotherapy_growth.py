#!/usr/bin/env python3
"""Chart: The Growth of Bibliotherapy Research — cumulative with annotations.

Clean cumulative line chart with per-period new-publication annotations and
a secondary visual (bar) for new publications, using colorblind-safe palette.

Output: 1200×720 PNG at 150 DPI.
"""

from pathlib import Path

import pandas as pd
from lets_plot import *

LetsPlot.setup_html()

# ── Data ─────────────────────────────────────────────────────────────────
df = pd.DataFrame({
    'year':       [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2024],
    'period':     [
        '1942–1950', '1951–1960', '1961–1970', '1971–1980',
        '1981–1990', '1991–2000', '2001–2010', '2011–2020', '2021–2024',
    ],
    'cumulative': [5, 12, 28, 55, 95, 178, 420, 1250, 1703],
    'new_pubs':   [5, 7, 16, 27, 40, 83, 242, 830, 453],
})

# ── Prepare annotation labels ────────────────────────────────────────────
df['new_label'] = '+' + df['new_pubs'].astype(str) + ' new'

# ── Colorblind-safe palette ──────────────────────────────────────────────
BLUE        = '#2166AC'
ORANGE      = '#E69F00'
DARK_ORANGE = '#D55E00'

# ── Build the plot ───────────────────────────────────────────────────────
p = (
    ggplot(df, aes(x='year'))
    # Subtle background bars for new publications per period
    + geom_bar(
        aes(y='new_pubs'),
        fill=ORANGE, alpha=0.28, width=7, stat='identity',
    )
    # Cumulative line
    + geom_line(
        aes(y='cumulative'),
        color=BLUE, size=1.8,
    )
    # Cumulative points
    + geom_point(
        aes(y='cumulative'),
        color=BLUE, size=4.5, stroke=0,
    )
    # Value labels at each cumulative point
    + geom_text(
        aes(y='cumulative', label='cumulative'),
        color=BLUE, size=8.5, fontface='bold',
        vjust=-1.6, hjust=0.5,
    )
    # Annotation: "+N new" labels for the three most recent periods
    + geom_text(
        aes(y='cumulative', label='new_label'),
        data=df[df['year'] >= 2000],
        color=DARK_ORANGE, size=8, fontface='italic',
        vjust=2.8, hjust=0.5,
    )
    # X-axis: period labels instead of year numbers
    + scale_x_continuous(
        breaks=df['year'].tolist(),
        labels=df['period'].tolist(),
        expand=[0.01, 0.02],
    )
    # Y-axis: leave headroom for labels above top point
    + scale_y_continuous(
        name='Cumulative Publications',
        limits=[0, df['cumulative'].max() * 1.18],
        expand=[0, 0],
    )
    # Labels and titles
    + labs(
        title='The Growth of Bibliotherapy Research',
        subtitle='Cumulative publications indexed in Scopus, 1942–2024',
        caption='Sources: Joseph & Jose (2024), Library Hi Tech; TCI-Thaijo (2024)',
    )
    + xlab('')
    # Magazine-style theme
    + theme_minimal()
    + theme(
        plot_title         =element_text(size=22, face='bold'),
        plot_subtitle      =element_text(size=14, color='#555555'),
        plot_caption       =element_text(size=9, color='#888888', hjust=0),
        axis_text_x        =element_text(angle=30, hjust=1, size=11),
        axis_text_y        =element_text(size=11),
        axis_title_y       =element_text(size=13),
        plot_margin        =[20, 30, 20, 20],
        panel_grid_major_x =element_blank(),
        panel_grid_minor_x =element_blank(),
        panel_grid_major_y =element_line(color='#EEEEEE', size=0.4),
        panel_grid_minor_y =element_blank(),
        legend_position    ='none',
        axis_ticks         =element_blank(),
        axis_line          =element_blank(),
    )
)

# ── Save ─────────────────────────────────────────────────────────────────
output_dir = Path('/home/pi/Documents/code/quortol/backend/blogs/images')
output_dir.mkdir(parents=True, exist_ok=True)

output_path = (
    output_dir / 'books-as-lifelong-friends_bibliotherapy_growth.png'
)

ggsave(p, str(output_path), w=1200, h=720, unit='px', dpi=150)

print(f'✓ Chart saved → {output_path}')
print(f'  Dimensions: 1200 × 720 px @ 150 DPI')
