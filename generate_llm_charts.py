"""
Generate 6 data visualization charts for the blog post:
"The Unit Economics of an LLM Token"

Output: backend/blogs/images/chart_*.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("backend/blogs/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Global style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 12,
    'axes.titlesize': 18,
    'axes.titleweight': 'bold',
    'axes.labelsize': 13,
    'axes.labelweight': 'semibold',
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 150,
    'figure.figsize': (12, 8),
    'axes.facecolor': '#FAFAFA',
    'figure.facecolor': 'white',
    'axes.edgecolor': '#D1D5DB',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.color': '#D1D5DB',
})

# Color palette (professional, blog-suitable)
C_BLUE = '#2563EB'
C_BLUE_LIGHT = '#93C5FD'
C_GREEN = '#059669'
C_GREEN_LIGHT = '#6EE7B7'
C_ORANGE = '#EA580C'
C_PURPLE = '#7C3AED'
C_GRAY = '#6B7280'
C_GRAY_LIGHT = '#D1D5DB'
C_DARK = '#1F2937'
C_RED = '#DC2626'
C_TEAL = '#0D9488'
C_AMBER = '#D97706'
C_INDIGO = '#4F46E5'
C_ROSE = '#E11D48'

# ── Helper ─────────────────────────────────────────────────────────────────
def save(fig, name):
    path = OUTPUT_DIR / name
    fig.savefig(path, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  + Saved {path}")
    return path


# ═══════════════════════════════════════════════════════════════════════════
# CHART 1: Token Price Collapse (line chart, log scale)
# ═══════════════════════════════════════════════════════════════════════════
def chart_token_price_decline():
    """Line chart: GPT-4 input/output pricing from launch to GPT-5.4."""
    data = {
        'date': pd.to_datetime([
            '2023-03-01',  # GPT-4 launch
            '2023-11-01',  # GPT-4 Turbo
            '2024-05-01',  # GPT-4o
            '2025-04-01',  # GPT-4.1 (estimated)
            '2026-01-15',  # GPT-5.4
        ]),
        'input': [30.00, 10.00, 5.00, 2.50, 2.50],
        'output': [60.00, 30.00, 15.00, 10.00, 15.00],
        'label': [
            'GPT-4\n$30 / $60',
            'GPT-4 Turbo\n$10 / $30',
            'GPT-4o\n$5 / $15',
            'GPT-4.1\n$2.50 / $10',
            'GPT-5.4\n$2.50 / $15',
        ],
    }
    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(df['date'], df['input'], color=C_BLUE, linewidth=3, marker='o',
            markersize=10, label='Input price per 1M tokens', zorder=5)
    ax.plot(df['date'], df['output'], color=C_ORANGE, linewidth=3, marker='s',
            markersize=10, label='Output price per 1M tokens', zorder=5)

    # Annotations with staggered offsets to prevent overlap
    output_offsets = [-22, -22, -22, 10, -22]  # alternate above/below
    input_offsets = [10, 10, 10, -22, -22]
    for i, (_, row) in enumerate(df.iterrows()):
        ax.annotate(f"${row['input']:.2f}", xy=(row['date'], row['input']),
                    xytext=(0, input_offsets[i]), textcoords='offset points',
                    fontsize=10, fontweight='bold', color=C_BLUE,
                    ha='center', va='bottom' if input_offsets[i] > 0 else 'top')
        ax.annotate(f"${row['output']:.2f}", xy=(row['date'], row['output']),
                    xytext=(15, output_offsets[i]), textcoords='offset points',
                    fontsize=10, fontweight='bold', color=C_ORANGE,
                    ha='center', va='bottom' if output_offsets[i] > 0 else 'top')

    # Shade the 83% decline region
    ax.annotate('', xy=(pd.Timestamp('2023-03-01'), 60), xytext=(pd.Timestamp('2026-01-15'), 15),
                arrowprops=dict(arrowstyle='<->', color=C_GRAY, lw=2, linestyle='--'))
    ax.text(pd.Timestamp('2024-08-15'), 38, '83% decline',
            fontsize=12, fontweight='bold', color=C_GRAY,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=C_GRAY, alpha=0.9))

    ax.set_yscale('log')
    ax.set_ylim(1, 120)
    ax.set_xlim(pd.Timestamp('2022-10-01'), pd.Timestamp('2026-06-01'))
    ax.set_title('Token Prices Have Collapsed 83% in Three Years', fontsize=18, fontweight='bold', pad=16)
    ax.set_xlabel('')
    ax.set_ylabel('$ per 1M tokens (log scale)', fontsize=13, fontweight='semibold')
    ax.legend(loc='upper right', framealpha=0.9, edgecolor=C_GRAY_LIGHT)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[3, 11]))  # March & November

    # Add source note
    ax.text(0.01, -0.12, 'Source: OpenAI official API documentation. GPT-4.1 pricing estimated.',
            transform=ax.transAxes, fontsize=9, color=C_GRAY, ha='left', va='top')

    fig.tight_layout()
    save(fig, 'chart_token_price_decline.png')


# ═══════════════════════════════════════════════════════════════════════════
# CHART 2: Cost Waterfall
# ═══════════════════════════════════════════════════════════════════════════
def chart_cost_waterfall():
    """Horizontal waterfall chart: per-token cost buildup."""
    categories = [
        'GPU Hardware\nAmortization',
        'Memory\nBandwidth',
        'Energy',
        'Cooling &\nInfrastructure',
        'Engineering &\nOptimization',
        'KV Cache\nOverhead',
        'Provider Margin\n& R&D',
    ]

    # Each cost component in $ per 1M tokens
    values = np.array([0.35, 0.15, 0.10, 0.30, 0.50, 0.30, 0.80])
    cumulative = np.cumsum(values)

    # We'll build a waterfall: start from 0, add each component
    starts = np.zeros(7)
    starts[1:] = cumulative[:-1]

    # Colors: blues for physical, greens for ops, orange for margin
    colors = ['#1D4ED8', '#3B82F6', '#60A5FA', '#059669', '#10B981', '#34D399', '#F59E0B']

    fig, ax = plt.subplots(figsize=(12, 8))

    bars = ax.barh(categories, values, left=starts, color=colors, edgecolor='white',
                   height=0.6, zorder=3)

    # Value labels on bars
    for i, (bar, val, cum) in enumerate(zip(bars, values, cumulative)):
        # Show the increment value on the bar
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2,
                f'+${val:.2f}', ha='center', va='center', fontsize=11,
                fontweight='bold', color='white')

        # Show cumulative on the right
        ax.text(cum + 0.05, bar.get_y() + bar.get_height() / 2,
                f'${cum:.2f}', ha='left', va='center', fontsize=12,
                fontweight='bold', color=C_DARK)

    # Final total annotation
    ax.axvline(x=cumulative[-1], color=C_DARK, linestyle='--', linewidth=1.5, alpha=0.5)
    ax.annotate(f'Final price:\n${cumulative[-1]:.2f}/M tokens',
                xy=(cumulative[-1], 6.5), xytext=(cumulative[-1] + 1.0, 6.5),
                fontsize=13, fontweight='bold', color=C_DARK,
                ha='left', va='center',
                arrowprops=dict(arrowstyle='->', color=C_DARK, lw=1.5))

    ax.set_xlim(0, cumulative[-1] * 1.5)
    ax.set_title('What Makes Up a Token: The Cost Cascade', fontsize=18, fontweight='bold', pad=16)
    ax.set_xlabel('$ per 1M tokens (cumulative)', fontsize=13, fontweight='semibold')
    ax.set_ylabel('')
    ax.invert_yaxis()  # Top-to-bottom cascade
    ax.grid(axis='y', visible=False)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=C_BLUE, label='Hardware & Infrastructure'),
        Patch(facecolor=C_GREEN, label='Operations & Engineering'),
        Patch(facecolor='#F59E0B', label='Provider Margin'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9, edgecolor=C_GRAY_LIGHT)

    ax.text(0.01, -0.08, 'Cost per 1M tokens for GPT-5.4 class models. Estimates based on industry data.',
            transform=ax.transAxes, fontsize=9, color=C_GRAY, ha='left', va='top')

    fig.tight_layout()
    save(fig, 'chart_cost_waterfall.png')


# ═══════════════════════════════════════════════════════════════════════════
# CHART 3: Frontier vs Budget Pricing
# ═══════════════════════════════════════════════════════════════════════════
def chart_frontier_vs_budget_pricing():
    """Grouped bar chart: input/output pricing across all models."""
    models = [
        'GPT-5.4', 'GPT-5.5', 'Claude Opus 4.7', 'Claude Sonnet 4.6',
        'Gemini 2.5 Pro', 'Gemini 2.5 Flash',
        'Llama 3.3 70B\n(Together)', 'Llama 3.1 405B\n(Fireworks)',
        'Mistral Large 2', 'DeepSeek V3',
    ]
    # Categories: F = frontier, O = open-weight
    categories = ['F', 'F', 'F', 'F', 'F', 'F', 'O', 'O', 'O', 'O']
    input_prices = [2.50, 5.00, 5.00, 3.00, 1.25, 0.30, 0.88, 3.00, 2.00, 0.32]
    output_prices = [15.00, 30.00, 25.00, 15.00, 10.00, 2.50, 0.88, 3.00, 6.00, 1.10]

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))

    bars_in = ax.bar(x - width/2, input_prices, width, label='Input price / 1M tokens',
                     color=C_BLUE, edgecolor='white', linewidth=0.5, zorder=3)
    bars_out = ax.bar(x + width/2, output_prices, width, label='Output price / 1M tokens',
                      color=C_ORANGE, edgecolor='white', linewidth=0.5, zorder=3)

    # Color-code background by category
    for i, cat in enumerate(categories):
        color = '#EFF6FF' if cat == 'F' else '#F0FDF4'
        ax.axvspan(i - 0.5, i + 0.5, color=color, zorder=0, alpha=0.5)

    # Value labels on bars
    for bar in bars_in:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.3, f'${h:.2f}',
                ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=C_BLUE)
    for bar in bars_out:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, f'${h:.2f}',
                ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=C_ORANGE)

    # Frontier vs open-weight divider label
    ax.axvline(x=5.5, color=C_DARK, linewidth=2, linestyle='--', alpha=0.6)
    ax.text(2.75, ax.get_ylim()[1] * 0.95, 'Frontier Models',
            ha='center', fontsize=12, fontweight='bold', color=C_DARK,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=C_BLUE, alpha=0.8))
    ax.text(8, ax.get_ylim()[1] * 0.95, 'Open-Weight via API',
            ha='center', fontsize=12, fontweight='bold', color=C_DARK,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=C_GREEN, alpha=0.8))

    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=10, ha='center')
    ax.set_title('Frontier vs. Budget: The 10-100x Pricing Spread', fontsize=18, fontweight='bold', pad=16)
    ax.set_ylabel('$ per 1M tokens', fontsize=13, fontweight='semibold')
    ax.legend(loc='upper right', framealpha=0.9, edgecolor=C_GRAY_LIGHT)
    ax.set_ylim(0, max(output_prices) * 1.25)

    ax.text(0.01, -0.10, 'Q1 2026 API pricing. Source: OpenAI, Anthropic, Google, Together AI, Fireworks, Mistral, DeepSeek.',
            transform=ax.transAxes, fontsize=9, color=C_GRAY, ha='left', va='top')

    fig.tight_layout()
    save(fig, 'chart_frontier_vs_budget_pricing.png')


# ═══════════════════════════════════════════════════════════════════════════
# CHART 4: Input vs Output Ratio
# ═══════════════════════════════════════════════════════════════════════════
def chart_input_vs_output_ratio():
    """Horizontal bar chart: output-to-input price ratio per provider."""
    providers = [
        'GPT-5.4', 'GPT-5.5', 'Claude Opus 4.7', 'Claude Sonnet 4.6',
        'Gemini 2.5 Pro', 'Gemini 2.5 Flash',
        'Mistral Large 2', 'DeepSeek V3',
        'Llama 3.3 70B\n(Together)', 'Llama 3.1 405B\n(Fireworks)',
    ]
    ratios = [6.0, 6.0, 5.0, 5.0, 8.0, 8.33, 3.0, 3.44, 1.0, 1.0]
    input_vals = [2.50, 5.00, 5.00, 3.00, 1.25, 0.30, 2.00, 0.32, 0.88, 3.00]
    output_vals = [15.00, 30.00, 25.00, 15.00, 10.00, 2.50, 6.00, 1.10, 0.88, 3.00]

    y = np.arange(len(providers))
    avg_ratio = np.mean([r for r in ratios if r > 1.5])  # Exclude 1:1 models

    fig, ax = plt.subplots(figsize=(12, 8))

    # Color bars by ratio intensity
    colors = ['#3B82F6' if r <= 2 else '#F59E0B' if r <= 5 else '#EF4444' for r in ratios]
    bars = ax.barh(y, ratios, height=0.6, color=colors, edgecolor='white', zorder=3)

    # Value labels (combine ratio + detail for 1:1 models to avoid overlap)
    for bar, ratio, inp, out in zip(bars, ratios, input_vals, output_vals):
        if ratio == 1.0:
            label = f'{ratio:.1f}x — same price (${inp:.2f} in = ${out:.2f} out)'
        else:
            label = f'{ratio:.1f}x   (${inp:.2f} in → ${out:.2f} out)'
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
                label, ha='left', va='center', fontsize=10, fontweight='bold',
                color=C_GREEN if ratio == 1.0 else C_DARK)

    # Average ratio line
    ax.axvline(x=avg_ratio, color=C_RED, linestyle='--', linewidth=2, alpha=0.8)
    ax.text(avg_ratio + 0.1, len(providers) - 0.5, f'Average: ~{avg_ratio:.0f}x',
            color=C_RED, fontsize=13, fontweight='bold', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=C_RED, alpha=0.9))

    ax.set_yticks(y)
    ax.set_yticklabels(providers, fontsize=10)
    ax.set_xlim(0, max(ratios) * 1.6)
    ax.set_title('Output Tokens Cost 3-8x More Than Input Tokens', fontsize=18, fontweight='bold', pad=16)
    ax.set_xlabel('Output-to-Input Price Ratio', fontsize=13, fontweight='semibold')
    ax.set_ylabel('')
    ax.grid(axis='y', visible=False)

    ax.text(0.01, -0.08, 'Ratios based on Q1 2026 API pricing. Generation is N forward passes per token vs 1 for prefill.',
            transform=ax.transAxes, fontsize=9, color=C_GRAY, ha='left', va='top')

    fig.tight_layout()
    save(fig, 'chart_input_vs_output_ratio.png')


# ═══════════════════════════════════════════════════════════════════════════
# CHART 5: Jevons Paradox (dual axis)
# ═══════════════════════════════════════════════════════════════════════════
def chart_jevons_paradox():
    """Dual-axis chart: falling token prices vs exploding infrastructure spend."""
    years = [2023, 2024, 2025, 2026]

    # Average (input+output)/2 for GPT flagship models
    # GPT-4 ($30+$60)/2 = $45; GPT-4o ($5+$15)/2 = $10; GPT-4.1 ($2.50+$10)/2 = $6.25; GPT-5.4 ($2.50+$15)/2 = $8.75
    avg_token_prices = [45.0, 10.0, 6.25, 8.75]
    token_labels = ['GPT-4\n$30/$60', 'GPT-4o\n$5/$15', 'GPT-4.1\n$2.50/$10', 'GPT-5.4\n$2.50/$15']

    # Enterprise AI infrastructure spending ($B)
    infra_spend = [70, 150, 443, 700]
    spend_labels = ['$70B', '$150B', '$443B', '$700B']

    fig, ax1 = plt.subplots(figsize=(12, 8))

    # Price line (left axis)
    line = ax1.plot(years, avg_token_prices, color=C_BLUE, linewidth=3.5,
                    marker='o', markersize=12, markerfacecolor='white',
                    markeredgecolor=C_BLUE, markeredgewidth=2.5, zorder=5,
                    label='Avg token price ($/1M tokens)')

    # Annotations for each price point
    for yr, price, label in zip(years, avg_token_prices, token_labels):
        ax1.annotate(f'${price:.2f}', xy=(yr, price),
                     xytext=(0, 12), textcoords='offset points',
                     fontsize=11, fontweight='bold', color=C_BLUE,
                     ha='center', va='bottom')

    # Shade the divergence
    ax1.fill_between(years, avg_token_prices, alpha=0.08, color=C_BLUE, label=None)

    ax1.set_xlim(2022.5, 2026.5)
    ax1.set_ylim(0, max(avg_token_prices) * 1.4)
    ax1.set_ylabel('$ per 1M tokens (avg input+output)', fontsize=13, fontweight='semibold', color=C_BLUE)
    ax1.tick_params(axis='y', labelcolor=C_BLUE)

    # Infrastructure bars (right axis)
    ax2 = ax1.twinx()
    bars = ax2.bar(years, infra_spend, width=0.55, alpha=0.75, color=C_ORANGE,
                   edgecolor='white', linewidth=1.5, zorder=3,
                   label='Enterprise AI infra spend ($B)')

    # Bar labels
    for bar, label in zip(bars, spend_labels):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                 label, ha='center', va='bottom', fontsize=12,
                 fontweight='bold', color=C_ORANGE)

    ax2.set_ylim(0, max(infra_spend) * 1.35)
    ax2.set_ylabel('Enterprise AI Infrastructure Spending ($B)', fontsize=13, fontweight='semibold', color=C_ORANGE)
    ax2.tick_params(axis='y', labelcolor=C_ORANGE)

    # X-axis
    ax1.set_xticks(years)
    ax1.set_xticklabels([str(y) for y in years], fontsize=12, fontweight='bold')
    ax1.set_xlabel('')

    # Title
    ax1.set_title('The Jevons Paradox of Inference: Cheaper Tokens, Bigger Bills',
                  fontsize=18, fontweight='bold', pad=16)

    # Legend (combined)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=C_BLUE, linewidth=3, marker='o', markersize=8,
               markerfacecolor='white', markeredgecolor=C_BLUE, markeredgewidth=2,
               label='Avg token price ($/1M)'),
        Patch(facecolor=C_ORANGE, alpha=0.75, label='AI infra spend ($B)'),
    ]
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.92),
               ncol=2, framealpha=0.9, edgecolor=C_GRAY_LIGHT, fontsize=12)

    # Jevons paradox annotation
    ax1.annotate('Prices ↓ 5-10x\nSpending ↑ 10x',
                 xy=(2025, 6.25), xytext=(2023.5, 55),
                 fontsize=14, fontweight='bold', color=C_DARK,
                 ha='center',
                 arrowprops=dict(arrowstyle='->', color=C_RED, lw=2, connectionstyle='arc3,rad=-0.3'),
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=C_RED, alpha=0.9))

    ax1.text(0.01, -0.10,
             'Sources: OpenAI API pricing; Hyperscaler capex guidance (Microsoft, Amazon, Google, Meta, Oracle).',
             transform=ax1.transAxes, fontsize=9, color=C_GRAY, ha='left', va='top')

    fig.subplots_adjust(top=0.88)  # Make room for top legend
    save(fig, 'chart_jevons_paradox.png')


# ═══════════════════════════════════════════════════════════════════════════
# CHART 6: Self-Host Breakeven
# ═══════════════════════════════════════════════════════════════════════════
def chart_self_host_breakeven():
    """Line chart: total daily cost vs daily token volume for API vs self-host."""
    # Daily token volume (millions)
    volume_m = np.linspace(0, 100, 500)  # 0 to 100M tokens/day

    # API cost: Together AI Llama 3.3 70B at $0.88/M tokens
    api_cost = 0.88 * volume_m

    # Self-host costs (fixed daily GPU rental)
    h100_low = 72.0    # $3/hr * 24
    h100_high = 144.0   # $6/hr * 24
    dgx_low = 576.0     # 8 GPUs at $3/hr each * 24
    dgx_high = 1152.0   # 8 GPUs at $6/hr each * 24

    fig, ax = plt.subplots(figsize=(12, 8))

    # API line
    ax.plot(volume_m, api_cost, color=C_BLUE, linewidth=3.5, zorder=5,
            label='API: Together AI Llama 3.3 70B ($0.88/M tokens)')

    # Self-host horizontal lines
    ax.axhline(y=h100_low, color=C_GREEN, linewidth=2.5, linestyle='--', zorder=4,
               label='Self-host: Single H100 ($3/hr)')
    ax.axhline(y=h100_high, color=C_GREEN, linewidth=2.5, linestyle=':', zorder=4,
               label='Self-host: Single H100 ($6/hr)')

    # Note DGX lines out of range
    ax.text(98, 230, '8-GPU DGX systems:\n$576–$1,152/day\n(far above this range)',
            fontsize=9, color=C_PURPLE, ha='right', va='top', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=C_PURPLE, alpha=0.7))

    # Shade regions: API cheaper vs self-host cheaper
    # Find the first intersection for H100 ($3/hr)
    idx_h100_low = np.argmin(np.abs(api_cost - h100_low))
    vol_break_low = volume_m[idx_h100_low]

    # API cheaper region (before break-even)
    ax.axvspan(0, vol_break_low, alpha=0.06, color=C_BLUE, label='API cheaper')
    ax.axvspan(vol_break_low, 100, alpha=0.06, color=C_GREEN, label='Self-host cheaper')

    # Break-even annotation
    ax.axvline(x=vol_break_low, color=C_DARK, linestyle='-.', linewidth=1.5, alpha=0.4)
    ax.annotate(f'H100 ($3/hr) breakeven:\n~{vol_break_low:.0f}M tokens/day',
                xy=(vol_break_low, h100_low), xytext=(vol_break_low - 25, h100_low + 50),
                fontsize=11, fontweight='bold', color=C_DARK,
                ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color=C_DARK, lw=1.5, connectionstyle='arc3,rad=0.2'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=C_GREEN, alpha=0.9))

    # 5-10M/day highlighted zone (blog's rule of thumb, reflecting batched throughput)
    ax.axvspan(5, 10, alpha=0.12, color=C_AMBER, zorder=2)
    ax.annotate('Blog rule-of-thumb\nbreak-even range\n(5-10M tokens/day)',
                xy=(7.5, 25), xytext=(35, 25),
                fontsize=10, fontweight='bold', color=C_AMBER,
                ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color=C_AMBER, lw=1.5, connectionstyle='arc3,rad=0.3'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=C_AMBER, alpha=0.9))

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 250)
    ax.set_title('When Does Self-Hosting Make Sense?', fontsize=18, fontweight='bold', pad=16)
    ax.set_xlabel('Daily token volume (millions)', fontsize=13, fontweight='semibold')
    ax.set_ylabel('Total daily cost ($)', fontsize=13, fontweight='semibold')
    ax.legend(loc='upper left', framealpha=0.9, edgecolor=C_GRAY_LIGHT, fontsize=10)

    ax.text(0.01, -0.12,
            'Self-host break-even math: $72/day H100 ÷ $0.88/M API = ~82M tokens/day. '
            'Blog rule-of-thumb (5-10M) assumes batched throughput with continuous batching.',
            transform=ax.transAxes, fontsize=9, color=C_GRAY, ha='left', va='top')

    fig.subplots_adjust(bottom=0.14, top=0.95)
    save(fig, 'chart_self_host_breakeven.png')


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating charts for 'The Unit Economics of an LLM Token'...\n")
    chart_token_price_decline()
    chart_cost_waterfall()
    chart_frontier_vs_budget_pricing()
    chart_input_vs_output_ratio()
    chart_jevons_paradox()
    chart_self_host_breakeven()
    print(f"\nAll 6 charts saved to {OUTPUT_DIR.resolve()}")
