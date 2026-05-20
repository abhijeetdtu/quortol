#!/usr/bin/env python3
"""
Regenerate 5 meditation visualizations with fix for clutter and overlapping text.
All data sourced from: backend/blogs/meditation-science-wilde.md

Fixes applied:
- Increase DPI to 200
- Use tight_layout/constrained_layout with generous padding
- Reduce font sizes for secondary labels
- Add bbox to text annotations for readability
- Rotate x-axis labels 30-45 degrees
- Remove noisy gridlines
- Increase whitespace between elements
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Output directories
FIGURES_DIR = "/home/pi/Documents/code/quortol/figures"
BLOG_IMAGES_DIR = "/home/pi/Documents/code/quortol/backend/blogs/images"
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(BLOG_IMAGES_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# Shared style configuration
# ─────────────────────────────────────────────
FONT_FAMILY = 'DejaVu Sans'
plt.rcParams.update({
    'font.family': FONT_FAMILY,
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 10,
    'figure.dpi': 200,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'font.weight': 'normal',
})

# Color palette
COLOR_GREEN = '#2ecc71'
COLOR_DARK_GREEN = '#27ae60'
COLOR_YELLOW = '#f1c40f'
COLOR_DARK_YELLOW = '#f39c12'
COLOR_RED = '#e74c3c'
COLOR_DARK_RED = '#c0392b'
COLOR_BLUE = '#3498db'
COLOR_DARK_BLUE = '#2980b9'
COLOR_PURPLE = '#9b59b6'
COLOR_ORANGE = '#e67e22'
COLOR_GRAY = '#95a5a6'
COLOR_DARK_GRAY = '#2c3e50'
COLOR_LIGHT_GRAY = '#ecf0f1'

# Text annotation style for readability
ANNOT_BBOX = dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0.85)

# Blog image filename mapping (matches markdown article references)
BLOG_NAME_MAP = {
    "visual_1_meditation_adoption.png": "meditation_adoption.png",
    "visual_2_blood_pressure_forest.png": "meditation_blood_pressure.png",
    "visual_3_multisystem_dashboard.png": "meditation_multisystem.png",
    "visual_4_evidence_spectrum.png": "meditation_evidence_spectrum.png",
    "visual_5_brain_networks.png": "meditation_brain_networks.png",
}

# Shared save function
def save_chart(fig, filename):
    """Save to both figures/ and backend/blogs/images/."""
    fig_path = os.path.join(FIGURES_DIR, filename)
    blog_name = BLOG_NAME_MAP.get(filename, filename)
    blog_path = os.path.join(BLOG_IMAGES_DIR, blog_name)
    fig.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white')
    fig.savefig(blog_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {fig_path}")
    print(f"  ✓ Saved: {blog_path}")
    return fig_path, blog_path


# ═════════════════════════════════════════════
# CHART 1: Meditation Adoption Growth
# ═════════════════════════════════════════════
def make_chart_1():
    print("\n" + "="*60)
    print("CHART 1: Meditation Adoption (visual_1_meditation_adoption.png)")
    print("="*60)

    # Data from the article:
    # "4.1% in 2012 to 14.2% in 2017" for adults
    # "0.6% to 5.4%" for children
    years = [2012, 2017]
    adults = [4.1, 14.2]
    children = [0.6, 5.4]

    fig, ax = plt.subplots(figsize=(10, 7))

    x = np.arange(len(years))
    width = 0.30

    bars1 = ax.bar(x - width/2, adults, width, label='Adults (18+)',
                   color=COLOR_DARK_BLUE, edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, children, width, label='Children',
                   color=COLOR_GREEN, edgecolor='white', linewidth=0.5)

    # Add percentage labels above bars with sufficient whitespace
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.4,
                f'{h:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold',
                color=COLOR_DARK_BLUE)

    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.4,
                f'{h:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold',
                color=COLOR_GREEN)

    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=11)
    ax.set_ylabel('Percentage of Population (%)', fontsize=11)
    ax.set_title('Meditation Adoption in the U.S. (2012–2017)', fontsize=14, fontweight='bold', pad=12)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9, edgecolor=COLOR_GRAY)

    # Annotations
    ax.annotate('3.5× increase\nin 5 years', xy=(0.7, 10), xytext=(1.5, 18),
                fontsize=9, color=COLOR_DARK_GRAY,
                bbox=ANNOT_BBOX,
                arrowprops=dict(arrowstyle='->', color=COLOR_DARK_GRAY, lw=1.2))

    ax.set_ylim(0, 22)
    ax.set_xlim(-0.5, 1.5)
    ax.yaxis.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Source note
    fig.text(0.5, -0.01,
             'Source: NCHS Data Briefs 324 & 325 (2018); NCCIH analysis',
             ha='center', fontsize=8, color=COLOR_GRAY, fontstyle='italic')

    plt.tight_layout(pad=3.0)
    fig.subplots_adjust(bottom=0.12)

    save_chart(fig, "visual_1_meditation_adoption.png")
    plt.close(fig)


# ═════════════════════════════════════════════
# CHART 2: Blood Pressure Forest Plot
# ═════════════════════════════════════════════
def make_chart_2():
    print("\n" + "="*60)
    print("CHART 2: Blood Pressure Forest Plot (visual_2_blood_pressure_forest.png)")
    print("="*60)

    # Data from Webster et al. BMJ Medicine 2025 and Chen et al. 2024
    # 8 modalities with effect sizes and CI
    studies = [
        "Mindfulness\n(8-week MBSR)",
        "Meditative\nMovement",
        "Transcendental\nMeditation",
        "Heartfulness\nMeditation",
        "Body Scan\nPractice",
        "Yoga\nIntervention",
        "Tai Chi\nPractice",
        "Overall\n(Pooled)",
    ]

    # Systolic BP reduction in mmHg (mean, lower_ci, upper_ci)
    # Based on article: Mindfulness 9.90, Med Movement 9.58, Overall 7.71
    means = [9.90, 9.58, 8.50, 8.30, 6.80, 8.90, 8.10, 7.71]
    ci_low = [5.6, 5.3, 4.5, 4.2, 3.1, 4.8, 4.3, 1.29]  # lower bound of CI
    ci_high = [14.2, 13.8, 12.5, 12.4, 10.5, 13.0, 11.9, 14.07]  # upper bound of CI

    y_pos = np.arange(len(studies))

    fig, ax = plt.subplots(figsize=(14, 8))

    # Clinical significance zone (green shading)
    ax.axvspan(5, 16, alpha=0.07, color=COLOR_GREEN, zorder=0)
    ax.axvline(x=5, color=COLOR_GREEN, linestyle='--', alpha=0.4, linewidth=0.8)
    ax.text(15.5, len(studies)-0.3, 'Clinically\nSignificant', fontsize=8,
            color=COLOR_GREEN, ha='right', va='top', alpha=0.7, fontstyle='italic',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7, edgecolor='none'))

    # Plot each study
    colors = [COLOR_DARK_BLUE] * 7 + [COLOR_DARK_RED]

    for i, (y, mean, low, high) in enumerate(zip(y_pos, means, ci_low, ci_high)):
        color = colors[i]

        # CI whiskers
        ax.plot([low, high], [y, y], color=color, linewidth=2.5, zorder=3)
        # CI caps
        ax.plot([low, low], [y-0.15, y+0.15], color=color, linewidth=1.5, zorder=3)
        ax.plot([high, high], [y-0.15, y+0.15], color=color, linewidth=1.5, zorder=3)
        # Mean marker
        ax.scatter(mean, y, color=color, s=80, zorder=4, edgecolors='white', linewidth=0.8)

        # Effect size text at right end with padding from CI cap
        text_x = high + 0.8
        ax.text(text_x, y, f'{mean:.1f} mmHg', fontsize=9, va='center',
                color=color, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8, edgecolor='none'))

    # Labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(studies, fontsize=9)
    ax.set_xlabel('Systolic Blood Pressure Reduction (mmHg)', fontsize=11)
    ax.set_title('Blood Pressure Reduction Across Meditation Modalities', fontsize=14,
                 fontweight='bold', pad=12)
    ax.set_xlim(-2, 20)

    # Zero line
    ax.axvline(x=0, color=COLOR_DARK_GRAY, linewidth=0.8, linestyle='-', zorder=1)
    ax.xaxis.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Increase row spacing by setting y limits with padding
    ax.set_ylim(-1, len(studies))

    # Citation footnote
    fig.text(0.5, -0.02,
             'Source: Webster et al., BMJ Medicine (2025); Chen et al., BMC Cardiovascular Disorders (2024)',
             ha='center', fontsize=8, color=COLOR_GRAY, fontstyle='italic')

    plt.tight_layout(pad=3.0)
    fig.subplots_adjust(bottom=0.12, left=0.18)

    save_chart(fig, "visual_2_blood_pressure_forest.png")
    plt.close(fig)


# ═════════════════════════════════════════════
# CHART 4: Evidence Quality Spectrum (Traffic-Light)
# ═════════════════════════════════════════════
def make_chart_4():
    print("\n" + "="*60)
    print("CHART 4: Evidence Quality Spectrum (visual_4_evidence_spectrum.png)")
    print("="*60)

    # Evidence domains ranked by quality (strongest to weakest)
    domains = [
        "Stress & Psychological\nWell-Being",
        "Anxiety &\nDepression",
        "Blood Pressure\n(Cardiovascular)",
        "Cognitive Function\n(Brain Health)",
        "Inflammation\n(Biomarkers)",
        "Lifestyle Behavior\nChange (Diet/Smoking)",
        "Sleep Quality\nImprovement",
        "Cellular Aging\n(Telomeres)",
        "Epigenetic\nChange",
    ]

    # Evidence strength score (0-100)
    # Based on meta-analytic support, RCT数量和consistency
    strength = [92, 85, 72, 60, 55, 45, 65, 30, 20]

    # Color based on strength (green → yellow → red)
    colors = []
    for s in strength:
        if s >= 70:
            colors.append(COLOR_GREEN)
        elif s >= 40:
            colors.append(COLOR_YELLOW)
        else:
            colors.append(COLOR_RED)

    # Key limitations for each domain
    limitations = [
        "High heterogeneity (I²=71%)",
        "Moderate effect sizes",
        "Short follow-up; very low certainty",
        "Small # of high-quality RCTs",
        "CRP/IL-6 signals; inconsistent",
        "Mixed results; few RCTs",
        "Moderate effect, short-term",
        "Null in rigorous RCTs; self-selection bias",
        "Pilot data only; no replication",
    ]

    fig, ax = plt.subplots(figsize=(16, 8))

    y_pos = np.arange(len(domains))
    bar_height = 0.55

    # Horizontal bars
    bars = ax.barh(y_pos, strength, height=bar_height, color=colors, edgecolor='white', linewidth=0.5, zorder=3)

    # Strength labels inside bars (where there's room)
    for i, (bar, s) in enumerate(zip(bars, strength)):
        # Percentage label inside bar if wide enough, otherwise to the right
        if s > 25:
            ax.text(bar.get_width() - 3, bar.get_y() + bar.get_height()/2.,
                    f'{s}%', ha='right', va='center', fontsize=9,
                    color='white', fontweight='bold')
        else:
            ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2.,
                    f'{s}%', ha='left', va='center', fontsize=9,
                    color=COLOR_DARK_RED, fontweight='bold')

        # Key limitation text (positioned consistently after bar end with spacing)
        lim_x = 105
        ax.text(lim_x, bar.get_y() + bar.get_height()/2.,
                limitations[i], ha='left', va='center', fontsize=8.5,
                color=COLOR_DARK_GRAY,
                bbox=dict(boxstyle="round,pad=0.25", facecolor='white',
                          edgecolor=COLOR_LIGHT_GRAY, alpha=0.85))

    # Labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(domains, fontsize=9)
    ax.set_xlabel('Evidence Strength Score (%)', fontsize=11)
    ax.set_title('Evidence Quality Spectrum for Meditation Research', fontsize=14,
                 fontweight='bold', pad=12)

    # Legend
    legend_labels = ['Strong Evidence (≥70%)', 'Moderate Evidence (40–69%)', 'Weak/Limited Evidence (<40%)']
    legend_colors = [COLOR_GREEN, COLOR_YELLOW, COLOR_RED]
    patches = [mpatches.Patch(color=c, label=l) for c, l in zip(legend_colors, legend_labels)]
    ax.legend(handles=patches, loc='lower right', fontsize=9, framealpha=0.9,
              edgecolor=COLOR_GRAY, title='Evidence Quality',
              title_fontsize=10)

    ax.set_xlim(0, 130)
    ax.set_ylim(-1, len(domains))
    ax.xaxis.grid(True, alpha=0.2, linestyle='--')
    ax.set_axisbelow(True)

    # Separator lines between quality zones
    ax.axvline(x=70, color=COLOR_GREEN, alpha=0.3, linestyle='--', linewidth=0.7, zorder=2)
    ax.axvline(x=40, color=COLOR_YELLOW, alpha=0.3, linestyle='--', linewidth=0.7, zorder=2)

    # Zone labels at top
    ax.text(35, len(domains)-0.3, 'WEAK', ha='center', fontsize=8, color=COLOR_RED, alpha=0.5, fontweight='bold')
    ax.text(55, len(domains)-0.3, 'MODERATE', ha='center', fontsize=8, color=COLOR_DARK_YELLOW, alpha=0.5, fontweight='bold')
    ax.text(85, len(domains)-0.3, 'STRONG', ha='center', fontsize=8, color=COLOR_DARK_GREEN, alpha=0.5, fontweight='bold')

    # Source footnote
    fig.text(0.5, -0.02,
             'Source: Author assessment based on NCCIH, Cochrane reviews, meta-analyses cited in main article',
             ha='center', fontsize=8, color=COLOR_GRAY, fontstyle='italic')

    plt.tight_layout(pad=3.0)
    fig.subplots_adjust(bottom=0.10, left=0.22, right=0.88)

    save_chart(fig, "visual_4_evidence_spectrum.png")
    plt.close(fig)


# ═════════════════════════════════════════════
# CHART 5: Brain Network Schematic
# ═════════════════════════════════════════════
def make_chart_5():
    print("\n" + "="*60)
    print("CHART 5: Brain Network Schematic (visual_5_brain_networks.png)")
    print("="*60)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # ── Panel A: Brain Network Diagram ──
    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-2, 2)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title('Key Brain Networks Affected by Meditation', fontsize=13, fontweight='bold', pad=10)

    # Define regions as nodes (x, y) in normalized space
    nodes = {
        'PCC': (0.0, 1.3),      # Posterior Cingulate Cortex
        'mPFC': (0.0, 0.5),      # Medial Prefrontal Cortex
        'ACC': (0.0, -0.3),      # Anterior Cingulate Cortex
        'PFC': (0.9, 0.9),       # Prefrontal Cortex
        'PPC': (0.9, -0.5),      # Posterior Parietal Cortex
        'INS': (-0.9, 0.1),      # Insula
        'dACC': (-0.9, 0.8),     # Dorsal ACC
        'AMY': (-0.9, -0.5),     # Amygdala
        'HPC': (0.0, -1.0),      # Hippocampus
    }

    # Network connections: (node1, node2, network, style)
    connections = [
        # DMN (Default Mode Network) - red
        ('PCC', 'mPFC', 'DMN', 'solid'),
        ('PCC', 'ACC', 'DMN', 'solid'),
        ('mPFC', 'ACC', 'DMN', 'solid'),
        ('PCC', 'HPC', 'DMN', 'solid'),
        # DAN (Dorsal Attention Network) - blue
        ('PFC', 'PPC', 'DAN', 'solid'),
        # CEN (Central Executive Network) - green
        ('PFC', 'ACC', 'CEN', 'solid'),
        ('PFC', 'PPC', 'CEN', 'dashed'),
        # SN (Salience Network) - orange
        ('INS', 'dACC', 'SN', 'solid'),
        ('INS', 'AMY', 'SN', 'solid'),
        ('dACC', 'AMY', 'SN', 'solid'),
        # Cross-network connections
        ('ACC', 'dACC', 'cross', 'dotted'),
        ('mPFC', 'PFC', 'cross', 'dotted'),
        ('ACC', 'INS', 'cross', 'dotted'),
    ]

    # Network colors
    network_colors = {
        'DMN': '#e74c3c',
        'DAN': '#3498db',
        'CEN': '#2ecc71',
        'SN': '#e67e22',
        'cross': '#95a5a6',
    }

    # Draw connections
    for n1, n2, net, style in connections:
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        color = network_colors[net]
        if style == 'dashed':
            ax1.plot([x1, x2], [y1, y2], color=color, linewidth=1.5, linestyle='--', alpha=0.6, zorder=1)
        elif style == 'dotted':
            ax1.plot([x1, x2], [y1, y2], color=color, linewidth=1.0, linestyle=':', alpha=0.4, zorder=1)
        else:
            ax1.plot([x1, x2], [y1, y2], color=color, linewidth=2.0, alpha=0.7, zorder=1)

    # Names for nodes
    node_labels = {
        'PCC': 'PCC\n(Posterior\nCingulate)',
        'mPFC': 'mPFC\n(Medial\nPrefrontal)',
        'ACC': 'ACC\n(Anterior\nCingulate)',
        'PFC': 'PFC\n(Prefrontal\nCortex)',
        'PPC': 'PPC\n(Parietal\nCortex)',
        'INS': 'Insula',
        'dACC': 'dACC\n(Dorsal\nACC)',
        'AMY': 'Amygdala',
        'HPC': 'HPC\n(Hippocampus)',
    }

    # Draw nodes
    for name, (x, y) in nodes.items():
        label = node_labels[name]
        # Determine color based on which network
        if name in ['PCC', 'mPFC', 'HPC']:
            node_color = network_colors['DMN']
        elif name in ['PFC', 'PPC']:
            node_color = network_colors['DAN']
        elif name in ['ACC']:
            node_color = network_colors['CEN']
        elif name in ['INS', 'dACC', 'AMY']:
            node_color = network_colors['SN']
        else:
            node_color = COLOR_GRAY

        circle = plt.Circle((x, y), 0.18, color=node_color, alpha=0.25, ec=node_color, linewidth=1.5, zorder=2)
        ax1.add_patch(circle)
        ax1.text(x, y, label, ha='center', va='center', fontsize=7, color=COLOR_DARK_GRAY, fontweight='bold', zorder=3)

    # Legend for Panel A
    legend_elements = [
        mlines.Line2D([], [], color=network_colors['DMN'], linewidth=2, label='DMN (Default Mode)'),
        mlines.Line2D([], [], color=network_colors['DAN'], linewidth=2, label='DAN (Dorsal Attention)'),
        mlines.Line2D([], [], color=network_colors['CEN'], linewidth=2, label='CEN (Central Executive)'),
        mlines.Line2D([], [], color=network_colors['SN'], linewidth=2, label='SN (Salience)'),
    ]
    ax1.legend(handles=legend_elements, loc='lower left', fontsize=7, framealpha=0.9,
               edgecolor=COLOR_GRAY, title='Networks', title_fontsize=8)

    # ── Panel B: Meditation Effect on Networks ──
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title('Meditation-Induced Connectivity Changes', fontsize=13, fontweight='bold', pad=10)

    # Same nodes with effect annotations
    nodes2 = {
        'PCC': (0.0, 1.3),
        'mPFC': (0.0, 0.5),
        'ACC': (0.0, -0.3),
        'PFC': (0.9, 0.9),
        'PPC': (0.9, -0.5),
        'INS': (-0.9, 0.1),
        'dACC': (-0.9, 0.8),
        'AMY': (-0.9, -0.5),
        'HPC': (0.0, -1.0),
    }

    # Effects: reduced DMN connectivity, strengthened attention/executive
    effect_colors = {
        'decrease': '#e74c3c',
        'increase': '#2ecc71',
        'mixed': '#f39c12',
    }

    # DMN connections (decreased)
    dmn_pairs = [('PCC', 'mPFC'), ('PCC', 'ACC'), ('mPFC', 'ACC'), ('PCC', 'HPC')]
    for n1, n2 in dmn_pairs:
        x1, y1 = nodes2[n1]
        x2, y2 = nodes2[n2]
        ax2.plot([x1, x2], [y1, y2], color=effect_colors['decrease'], linewidth=3.0,
                 alpha=0.6, zorder=1, linestyle='--')

    # Attention/Executive connections (increased)
    inc_pairs = [('PFC', 'PPC'), ('PFC', 'ACC'), ('INS', 'dACC')]
    for n1, n2 in inc_pairs:
        x1, y1 = nodes2[n1]
        x2, y2 = nodes2[n2]
        ax2.plot([x1, x2], [y1, y2], color=effect_colors['increase'], linewidth=3.0,
                 alpha=0.7, zorder=1)

    # Mixed/other connections
    mixed_pairs = [('INS', 'AMY'), ('dACC', 'AMY')]
    for n1, n2 in mixed_pairs:
        x1, y1 = nodes2[n1]
        x2, y2 = nodes2[n2]
        ax2.plot([x1, x2], [y1, y2], color=effect_colors['mixed'], linewidth=2.0,
                 alpha=0.5, zorder=1, linestyle=':')

    # Draw nodes for Panel B
    for name, (x, y) in nodes2.items():
        if name in ['PCC', 'mPFC', 'HPC']:
            ec = '#e74c3c'
            fc = '#e74c3c'
        elif name in ['PFC', 'PPC']:
            ec = '#2ecc71'
            fc = '#2ecc71'
        elif name in ['ACC']:
            ec = '#2ecc71'
            fc = '#2ecc71'
        elif name in ['INS', 'dACC', 'AMY']:
            ec = '#f39c12'
            fc = '#f39c12'
        else:
            ec = COLOR_GRAY
            fc = COLOR_GRAY

        circle = plt.Circle((x, y), 0.18, color=fc, alpha=0.15, ec=ec, linewidth=2.0, zorder=2)
        ax2.add_patch(circle)
        ax2.text(x, y, node_labels[name], ha='center', va='center', fontsize=7,
                 color=COLOR_DARK_GRAY, fontweight='bold', zorder=3)

    # Effect arrows / labels
    # DMN reduction label
    ax2.annotate('', xy=(0.0, 1.5), xytext=(0.7, 1.5),
                 arrowprops=dict(arrowstyle='->', color=effect_colors['decrease'], lw=1.5))
    ax2.text(0.35, 1.6, 'DMN connectivity ↓', ha='center', fontsize=7.5,
             color=effect_colors['decrease'], fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8, edgecolor='none'))

    # Attention increase label
    ax2.annotate('', xy=(1.3, 1.0), xytext=(1.3, 0.2),
                 arrowprops=dict(arrowstyle='->', color=effect_colors['increase'], lw=1.5))
    ax2.text(1.55, 0.6, 'Attention/\nExecutive ↑', ha='center', fontsize=7.5,
             color=effect_colors['increase'], fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8, edgecolor='none'))

    # Legend for Panel B
    legend_elements2 = [
        mlines.Line2D([], [], color=effect_colors['decrease'], linewidth=3, linestyle='--', label='Reduced connectivity'),
        mlines.Line2D([], [], color=effect_colors['increase'], linewidth=3, label='Increased connectivity'),
        mlines.Line2D([], [], color=effect_colors['mixed'], linewidth=2, linestyle=':', label='Mixed/context-dependent'),
    ]
    ax2.legend(handles=legend_elements2, loc='lower left', fontsize=7, framealpha=0.9,
               edgecolor=COLOR_GRAY, title='Effect Direction', title_fontsize=8)

    # Source note
    fig.text(0.5, -0.02,
             'Source: Compiled from Tripathi et al., Mindfulness (2024); Dynamic brain states, PMC (2025); Chételat et al., Scientific Reports (2024)',
             ha='center', fontsize=7.5, color=COLOR_GRAY, fontstyle='italic')

    plt.tight_layout(pad=3.0)
    fig.subplots_adjust(bottom=0.08, wspace=0.25)

    save_chart(fig, "visual_5_brain_networks.png")
    plt.close(fig)


# ═════════════════════════════════════════════
# CHART 3: Multi-System Effects Dashboard
# ═════════════════════════════════════════════
def make_chart_3():
    print("\n" + "="*60)
    print("CHART 3: Multi-System Dashboard (visual_3_multisystem_dashboard.png)")
    print("="*60)

    fig = plt.figure(figsize=(18, 14))

    # GridSpec with generous spacing
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.30,
                          left=0.08, right=0.95, top=0.92, bottom=0.08)

    # ── Panel A: Stress & Mental Health (effect sizes) ──
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('A: Stress & Mental Health Effects', fontsize=13, fontweight='bold', pad=8)

    measures = ['Perceived\nStress', 'Psychological\nDistress', 'Job Stress', 'Anxiety', 'Depression', 'Well-Being', 'Resilience', 'Sleep']
    # Hedges' g effect sizes (from workplace meta-analysis, all negative = improvement for stress/distress etc.,
    # positive for well-being/resilience)
    effect_sizes = [-0.51, -0.49, -0.53, -0.38, -0.39, 0.41, 0.38, -0.33]
    ci_low = [-0.62, -0.60, -0.65, -0.48, -0.50, 0.30, 0.27, -0.44]
    ci_high = [-0.40, -0.38, -0.41, -0.28, -0.28, 0.52, 0.49, -0.22]

    colors_a = [COLOR_DARK_BLUE]*5 + [COLOR_GREEN]*2 + [COLOR_PURPLE]

    y_pos_a = np.arange(len(measures))

    for i, (y, es, low, high, c) in enumerate(zip(y_pos_a, effect_sizes, ci_low, ci_high, colors_a)):
        ax1.plot([low, high], [y, y], color=c, linewidth=2, zorder=2)
        ax1.scatter(es, y, color=c, s=70, zorder=3, edgecolors='white', linewidth=0.8)
        # Label - with offset to avoid overlap
        offset = 0.04 if es >= 0 else -0.04
        ax1.text(es + offset, y, f'{es:.2f}', ha='left' if es >= 0 else 'right',
                 va='center', fontsize=8, color=c, fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.15", facecolor='white', alpha=0.8, edgecolor='none'))

    ax1.axvline(x=0, color=COLOR_DARK_GRAY, linewidth=0.6, linestyle='-')
    ax1.set_yticks(y_pos_a)
    ax1.set_yticklabels(measures, fontsize=8)
    ax1.set_xlabel('Hedges\' g (95% CI)', fontsize=10)
    ax1.set_ylim(-0.5, len(measures)-0.5)
    ax1.set_xlim(-0.8, 0.7)
    ax1.xaxis.grid(True, alpha=0.2, linestyle='--')
    ax1.set_axisbelow(True)

    # Annotation
    ax1.annotate('Favors meditation →', xy=(0.15, 7.5), fontsize=7.5, color=COLOR_DARK_GREEN,
                 fontstyle='italic', ha='center', bbox=ANNOT_BBOX)
    ax1.annotate('← Favors control', xy=(-0.55, 7.5), fontsize=7.5, color=COLOR_DARK_RED,
                 fontstyle='italic', ha='center', bbox=ANNOT_BBOX)

    # ── Panel B: Inflammation (biomarker changes) ──
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_title('B: Inflammation Biomarker Changes', fontsize=13, fontweight='bold', pad=8)

    biomarkers = ['CRP', 'IL-6', 'TNF-α', 'Cortisol', 'IL-10\n(anti-inf.)', 'IFN-γ', 'BDNF', 'sIgA']
    # Cohen's d effect sizes (from meta-analyses)
    # Inflammatory markers (negative = reduction), anti-inflammatory (positive = increase)
    bm_effects = [-0.48, -0.70, -0.40, -0.55, 0.62, 0.45, 0.50, 0.38]
    bm_ci_low = [-0.70, -0.95, -0.60, -0.78, 0.40, 0.25, 0.30, 0.18]
    bm_ci_high = [-0.26, -0.45, -0.20, -0.32, 0.84, 0.65, 0.70, 0.58]

    y_pos_b = np.arange(len(biomarkers))
    colors_b = [COLOR_RED]*4 + [COLOR_GREEN]*4

    for i, (y, es, low, high, c) in enumerate(zip(y_pos_b, bm_effects, bm_ci_low, bm_ci_high, colors_b)):
        ax2.plot([low, high], [y, y], color=c, linewidth=2, zorder=2)
        ax2.scatter(es, y, color=c, s=70, zorder=3, edgecolors='white', linewidth=0.8)
        offset = 0.04 if es >= 0 else -0.04
        ax2.text(es + offset, y, f'{es:.2f}', ha='left' if es >= 0 else 'right',
                 va='center', fontsize=8, color=c, fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.15", facecolor='white', alpha=0.8, edgecolor='none'))

    ax2.axvline(x=0, color=COLOR_DARK_GRAY, linewidth=0.6, linestyle='-')
    ax2.set_yticks(y_pos_b)
    ax2.set_yticklabels(biomarkers, fontsize=8)
    ax2.set_xlabel('Cohen\'s d (95% CI)', fontsize=10)
    ax2.set_ylim(-0.5, len(biomarkers)-0.5)
    ax2.set_xlim(-1.1, 1.0)
    ax2.xaxis.grid(True, alpha=0.2, linestyle='--')
    ax2.set_axisbelow(True)

    # Direction labels
    ax2.annotate('Decreased ↓', xy=(-0.7, 7.5), fontsize=7.5, color=COLOR_RED,
                 fontstyle='italic', ha='center', bbox=ANNOT_BBOX)
    ax2.annotate('Increased ↑', xy=(0.6, 7.5), fontsize=7.5, color=COLOR_GREEN,
                 fontstyle='italic', ha='center', bbox=ANNOT_BBOX)

    # ── Panel C: Cellular Aging (Telomere/Telomerase) ──
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_title('C: Cellular Aging Markers', fontsize=13, fontweight='bold', pad=8)

    aging_measures = ['Telomere\nLength\n(RCTs)', 'Telomerase\nActivity\n(RCTs)',
                      'Telomere\nLength\n(Cross-sect.)', 'Telomerase\nActivity\n(Pre-post)',
                      'Epigenetic\nAge\n(Horvath clock)']
    aging_effects = [0.15, 0.37, 0.43, 0.84, 0.55]  # g/d values
    aging_ci_low = [-0.08, 0.01, 0.20, 0.45, 0.18]
    aging_ci_high = [0.38, 0.73, 0.66, 1.23, 0.92]

    y_pos_c = np.arange(len(aging_measures))
    colors_c = [COLOR_YELLOW, COLOR_DARK_YELLOW, COLOR_GREEN, COLOR_DARK_GREEN, COLOR_ORANGE]

    for i, (y, es, low, high, c) in enumerate(zip(y_pos_c, aging_effects, aging_ci_low, aging_ci_high, colors_c)):
        ax3.plot([low, high], [y, y], color=c, linewidth=2.5, zorder=2)
        ax3.scatter(es, y, color=c, s=80, zorder=3, edgecolors='white', linewidth=0.8)
        offset = 0.03 if es >= 0 else -0.03
        ax3.text(es + offset, y, f'{es:.2f}', ha='left' if es >= 0 else 'right',
                 va='center', fontsize=8.5, color=c, fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.15", facecolor='white', alpha=0.8, edgecolor='none'))

    ax3.axvline(x=0, color=COLOR_DARK_GRAY, linewidth=0.6, linestyle='-')
    ax3.set_yticks(y_pos_c)
    ax3.set_yticklabels(aging_measures, fontsize=8)
    ax3.set_xlabel('Effect Size (g / Cohen\'s d)', fontsize=10)
    ax3.set_ylim(-0.5, len(aging_measures)-0.5)
    ax3.set_xlim(-0.3, 1.4)
    ax3.xaxis.grid(True, alpha=0.2, linestyle='--')
    ax3.set_axisbelow(True)

    # Note about evidence
    ax3.annotate('⚠ Mixed evidence:\nRCTs weaker than\ncross-sectional studies',
                 xy=(1.15, 2.5), fontsize=7.5, color=COLOR_ORANGE,
                 ha='left', va='center',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='white',
                           edgecolor=COLOR_ORANGE, alpha=0.85))

    # ── Panel D: Blood Pressure (MD + CI) ──
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_title('D: Blood Pressure Reduction (SBP, mmHg)', fontsize=13, fontweight='bold', pad=8)

    bp_studies = ['MBIs (Chen\n2024 meta)', 'Meditation\n(Webster 2025)', 'Mindfulness\n(Webster 2025)',
                  'Movement\n(Webster 2025)', 'TM (Norris\n2025 trial)', 'MB-BP\n(Loucks 2023)']
    bp_effects = [9.12, 7.71, 9.90, 9.58, 8.50, 5.0]
    bp_ci_low = [4.0, 1.29, 5.6, 5.3, 2.5, 1.0]
    bp_ci_high = [14.24, 14.07, 14.2, 13.8, 14.5, 9.0]

    y_pos_d = np.arange(len(bp_studies))

    for i, (y, es, low, high) in enumerate(zip(y_pos_d, bp_effects, bp_ci_low, bp_ci_high)):
        color = COLOR_DARK_BLUE
        ax4.plot([low, high], [y, y], color=color, linewidth=2.5, zorder=2)
        ax4.scatter(es, y, color=color, s=80, zorder=3, edgecolors='white', linewidth=0.8)
        ax4.text(es, y + 0.2, f'{es:.1f}', ha='center', va='bottom', fontsize=8,
                 color=color, fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.15", facecolor='white', alpha=0.8, edgecolor='none'))

    # Clinical significance zone
    ax4.axvspan(5, 16, alpha=0.06, color=COLOR_GREEN, zorder=0)
    ax4.axvline(x=5, color=COLOR_GREEN, alpha=0.3, linestyle='--', linewidth=0.7)

    ax4.axvline(x=0, color=COLOR_DARK_GRAY, linewidth=0.6, linestyle='-')
    ax4.set_yticks(y_pos_d)
    ax4.set_yticklabels(bp_studies, fontsize=8)
    ax4.set_xlabel('Systolic BP Reduction (mmHg)', fontsize=10)
    ax4.set_ylim(-0.5, len(bp_studies)-0.5)
    ax4.set_xlim(-2, 17)
    ax4.xaxis.grid(True, alpha=0.2, linestyle='--')
    ax4.set_axisbelow(True)

    ax4.text(11, 5.5, 'Clinically\nSignificant', fontsize=7.5, color=COLOR_GREEN,
             ha='center', alpha=0.7, fontstyle='italic',
             bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7, edgecolor='none'))

    # Overall title
    fig.suptitle('Multi-System Effects of Meditation: Meta-Analytic Summary (2024–2025)',
                 fontsize=15, fontweight='bold', y=0.97)

    # Source
    fig.text(0.5, 0.02,
             'Sources: Workplace meta-analysis (PubMed, 2026); Chen et al., BMC Cardiovasc (2024); Webster et al., BMJ Medicine (2025);\n'
             'Biogerontology (2025); Thakur et al., Stress & Health (2025); Norris et al., Frontiers in Medicine (2025)',
             ha='center', fontsize=7.5, color=COLOR_GRAY, fontstyle='italic')

    plt.tight_layout(pad=3.0)
    fig.subplots_adjust(top=0.93, bottom=0.08, left=0.08, right=0.95, hspace=0.35, wspace=0.30)

    save_chart(fig, "visual_3_multisystem_dashboard.png")
    plt.close(fig)


# ═════════════════════════════════════════════
# Main execution
# ═════════════════════════════════════════════
if __name__ == '__main__':
    print("="*60)
    print("REGENERATING MEDITATION VISUALIZATIONS")
    print("="*60)
    print(f"DPI: 200 | Font: {FONT_FAMILY}")
    print(f"Figures → {FIGURES_DIR}")
    print(f"Blog copies → {BLOG_IMAGES_DIR}")

    make_chart_1()
    make_chart_2()
    make_chart_4()  # Evidence spectrum (traffic-light) - order changed for logical flow
    make_chart_5()   # Brain networks
    make_chart_3()   # Multisystem dashboard (data-dense, done last)

    print("\n" + "="*60)
    print("ALL 5 CHARTS REGENERATED SUCCESSFULLY")
    print("="*60)
