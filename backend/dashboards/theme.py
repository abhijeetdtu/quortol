"""Shared chart theme for Data Storytelling dashboards — minimal, quiet styling."""

PRUSSIAN_BLUE = '#001427'
DEEP_TEAL = '#708D81'
JASMINE = '#F4D58D'
BRICK_EMBER = '#BF0603'
BLOOD_RED = '#8D0801'

CHART_COLORWAY = [
    PRUSSIAN_BLUE,
    DEEP_TEAL,
    JASMINE,
    BRICK_EMBER,
    BLOOD_RED,
]

DASH_STYLES = ['solid', 'dash', 'dot', 'dashdot', 'longdash']

DISPLAY_FONT = "'Fraunces', Georgia, 'Times New Roman', serif"
BODY_FONT = "'Source Sans 3', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"


def apply_chart_theme(fig, *, title, xaxis_title=None, yaxis_title=None, height=420):
    """Apply clean, low-noise chart theme. No template, no border, no ticks."""
    fig.update_layout(
        title=title,
        colorway=CHART_COLORWAY,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'color': PRUSSIAN_BLUE, 'family': BODY_FONT, 'size': 12},
        title_font={'family': DISPLAY_FONT, 'size': 18},
        height=height,
        margin={'l': 50, 'r': 20, 't': 50, 'b': 50},
        hovermode='x unified',
        hoverlabel={
            'font': {'family': BODY_FONT, 'size': 11},
            'namelength': -1,
        },
    )
    fig.update_xaxes(
        showgrid=False,
        showline=False,
        showticklabels=True,
        tickfont={'size': 11},
        title_font={'size': 12},
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='#EDF0F2',
        gridwidth=1,
        showline=False,
        showticklabels=True,
        tickfont={'size': 11},
        title_font={'size': 12},
    )
    if xaxis_title:
        fig.update_xaxes(title_text=xaxis_title)
    if yaxis_title:
        fig.update_yaxes(title_text=yaxis_title)
    return fig
