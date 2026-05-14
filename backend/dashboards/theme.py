"""Shared chart theme for Data Storytelling dashboards."""

# SCSS HEX
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

DISPLAY_FONT = "'Fraunces', Georgia, 'Times New Roman', serif"
BODY_FONT = "'Source Sans 3', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"


def apply_chart_theme(fig, *, title, xaxis_title=None, yaxis_title=None, height=420):
    """Apply the shared dashboard chart styling to a Plotly figure."""
    fig.update_layout(
        title=title,
        template='plotly_white',
        colorway=CHART_COLORWAY,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'color': PRUSSIAN_BLUE, 'family': BODY_FONT},
        title_font={'family': DISPLAY_FONT, 'size': 24},
        xaxis={'gridcolor': '#E8ECEF'},
        yaxis={'gridcolor': '#E8ECEF'},
        height=height
    )
    if xaxis_title:
        fig.update_xaxes(title_text=xaxis_title)
    if yaxis_title:
        fig.update_yaxes(title_text=yaxis_title)
    return fig
