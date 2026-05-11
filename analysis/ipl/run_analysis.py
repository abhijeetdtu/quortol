"""
IPL Data Analysis Runner

Quick script to run the full IPL analysis and generate all outputs.
"""

import pandas as pd
import numpy as np
import json
import datetime
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))
os.chdir(Path(__file__).parent)

from data_loader import IPLDataLoader
from metrics import (
    calculate_season_strike_rates,
    calculate_phase_scoring,
    calculate_six_rates,
    calculate_bowling_metrics,
    calculate_wicket_metrics,
    get_era_summary,
    compare_eras,
    perform_statistical_tests,
    calculate_projected_sixes,
    analyze_venue_impact
)
from visualization import (
    create_strike_rate_trend,
    create_sixes_growth_chart,
    create_phase_scoring_chart,
    create_bowling_metrics_chart,
    create_venue_impact_chart,
    create_statistical_tests_chart,
    create_q_value_chart,
    create_projection_chart
)

def main():
    print("=" * 80)
    print("IPL DATA-BACKED ANALYSIS")
    print("=" * 80)
    
    # Load data
    print("\n[1/9] Loading IPL data...")
    loader = IPLDataLoader()
    data = loader.load()
    clean_data = loader.clean()
    
    print(f"  Loaded {len(clean_data)} ball-by-ball records")
    print(f"  Seasons: {sorted(clean_data['season'].unique())}")
    print(f"  Total matches: {clean_data['match_id'].nunique()}")
    print(f"  Total sixes: {clean_data['is_six'].sum()}")
    
    # Section 1: Strike Rate
    print("\n[2/9] Analyzing strike rate trends...")
    season_sr = clean_data.groupby('season').agg({
        'batsman_runs': 'sum',
        'is_legal': 'sum'
    }).reset_index()
    season_sr['strike_rate'] = (season_sr['batsman_runs'] * 100) / (season_sr['is_legal'] + 0.001)
    
    early_sr = season_sr[(season_sr['season'] >= 2008) & (season_sr['season'] <= 2015)]['strike_rate'].mean()
    late_sr = season_sr[(season_sr['season'] >= 2016) & (season_sr['season'] <= 2024)]['strike_rate'].mean()
    sr_change = ((late_sr - early_sr) / early_sr) * 100
    
    print(f"  Early Era SR: {early_sr:.2f}")
    print(f"  Late Era SR: {late_sr:.2f}")
    print(f"  Change: {sr_change:.2f}% (Claim: +7.24%)")
    
    # Section 2: Sixes
    print("\n[3/9] Analyzing six-hitting trends...")
    season_sixes = clean_data.groupby('season').agg({
        'is_six': 'sum',
        'match_id': 'first'
    }).reset_index()
    season_matches = clean_data.groupby('season').nunique()['match_id'].reset_index()
    season_matches.rename(columns={'match_id': 'matches'}, inplace=True)
    season_sixes = season_sixes.merge(season_matches, on='season')
    season_sixes['sixes_per_match'] = season_sixes['is_six'] / (season_sixes['matches'] + 0.001)
    
    early_sixes = season_sixes[(season_sixes['season'] >= 2008) & (season_sixes['season'] <= 2015)]['sixes_per_match'].mean()
    late_sixes = season_sixes[(season_sixes['season'] >= 2016) & (season_sixes['season'] <= 2024)]['sixes_per_match'].mean()
    sixes_change = ((late_sixes - early_sixes) / early_sixes) * 100
    
    print(f"  Early Era sixes/match: {early_sixes:.2f}")
    print(f"  Late Era sixes/match: {late_sixes:.2f}")
    print(f"  Change: {sixes_change:.1f}% (Claim: +361%)")
    
    # Section 3: Phase scoring
    print("\n[4/9] Analyzing phase-wise scoring...")
    clean_data['phase'] = clean_data['over'].apply(
        lambda x: 'powerplay' if x <= 5 else ('middle' if x <= 13 else 'death')
    )
    phase_data = clean_data.groupby(['season', 'phase']).agg({
        'batsman_runs': 'sum',
        'is_legal': 'sum'
    }).reset_index()
    phase_data['runs_per_over'] = phase_data['batsman_runs'] / (phase_data['is_legal'] / 6 + 0.001)
    
    for phase in ['powerplay', 'middle', 'death']:
        phase_early = phase_data[(phase_data['phase'] == phase) & (phase_data['season'] <= 2015)]['runs_per_over'].mean()
        phase_late = phase_data[(phase_data['phase'] == phase) & (phase_data['season'] >= 2016)]['runs_per_over'].mean()
        change = ((phase_late - phase_early) / phase_early) * 100
        print(f"  {phase}: {phase_early:.2f} -> {phase_late:.2f} (+{change:.1f}%)")
    
    # Section 4: Bowling metrics
    print("\n[5/9] Analyzing bowling metrics...")
    bowling_data = clean_data.groupby('season').agg({
        'total_runs': 'sum',
        'is_legal': 'sum',
        'is_dot': 'sum'
    }).reset_index()
    bowling_data['economy_rate'] = bowling_data['total_runs'] / (bowling_data['is_legal'] / 6 + 0.001)
    bowling_data['dot_ball_ratio'] = bowling_data['is_dot'] / (bowling_data['is_legal'] + 0.001)
    
    early_econ = bowling_data[(bowling_data['season'] >= 2008) & (bowling_data['season'] <= 2015)]['economy_rate'].mean()
    late_econ = bowling_data[(bowling_data['season'] >= 2016) & (bowling_data['season'] <= 2024)]['economy_rate'].mean()
    econ_change = ((late_econ - early_econ) / early_econ) * 100
    
    early_dot = bowling_data[(bowling_data['season'] >= 2008) & (bowling_data['season'] <= 2015)]['dot_ball_ratio'].mean()
    late_dot = bowling_data[(bowling_data['season'] >= 2016) & (bowling_data['season'] <= 2024)]['dot_ball_ratio'].mean()
    dot_change = ((late_dot - early_dot) / early_dot) * 100
    
    print(f"  Economy: {early_econ:.2f}  ->  {late_econ:.2f} (+{econ_change:.1f}%) (Claim: +7.37%)")
    print(f"  Dot Ball: {early_dot*100:.2f}%  ->  {late_dot*100:.2f}% ({dot_change*100:.1f}%) (Claim: -2.59%)")
    
    # Section 5: Impact Player
    print("\n[6/9] Analyzing Impact Player Rule effect...")
    pre_impact = season_sixes[(season_sixes['season'] >= 2021) & (season_sixes['season'] <= 2022)]
    post_impact = season_sixes[(season_sixes['season'] >= 2023) & (season_sixes['season'] <= 2025)]
    pre_sixes = pre_impact['sixes_per_match'].mean()
    post_sixes = post_impact['sixes_per_match'].mean()
    impact_change = post_sixes - pre_sixes
    
    print(f"  Pre-Impact: {pre_sixes:.2f} sixes/match")
    print(f"  Post-Impact: {post_sixes:.2f} sixes/match")
    print(f"  Change: +{impact_change:.2f} (Claim: +1.4)")
    
    # Section 6: Venue impact
    print("\n[7/9] Analyzing venue impact...")
    venue_data = clean_data.groupby('venue').agg({
        'is_six': 'sum',
        'match_id': 'first'
    }).reset_index()
    venue_matches = clean_data.groupby('venue').nunique()['match_id'].reset_index()
    venue_matches.rename(columns={'match_id': 'matches'}, inplace=True)
    venue_data = venue_data.merge(venue_matches, on='venue')
    venue_data['sixes_per_match'] = venue_data['is_six'] / (venue_data['matches'] + 0.001)
    venue_data = venue_data.sort_values('sixes_per_match', ascending=False)
    
    print("  Top venues by sixes/match:")
    for i, row in venue_data.head(5).iterrows():
        print(f"    {row['venue']}: {row['sixes_per_match']:.2f}")
    
    # Section 7: Statistical tests
    print("\n[8/9] Running statistical hypothesis tests...")
    test_results = perform_statistical_tests(clean_data)
    
    passed = sum(1 for t in test_results.values() if t['significant'])
    print(f"  Tests passed (p<0.05): {passed}/{len(test_results)}")
    for metric, results in test_results.items():
        sig = '[OK]' if results['significant'] else '[X]'
        print(f"    {sig} {metric}: p={results['p_value']:.4f}")
    
    # Section 8: Projections
    print("\n[9/9] Generating 2028 projections...")
    current_sixes = season_sixes[season_sixes['season'] == 2025]['sixes_per_match'].values[0]
    projections = calculate_projected_sixes(
        current_sixes_per_match=current_sixes,
        annual_growth_rates=[0.03, 0.06, 0.09],
        years_to_project=3
    )
    
    print("  Projection scenarios:")
    for scenario, data in projections.items():
        name = 'Conservative' if '3' in scenario else ('Moderate' if '6' in scenario else 'Acceleration')
        print(f"    {name}: {data['final_sixes_per_match']:.1f} sixes/match")
    
    # Generate figures
    print("\n" + "=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    
    create_strike_rate_trend(season_sr, output_path='figures/strike_rate_trend.png')
    create_sixes_growth_chart(season_sixes, output_path='figures/sixes_growth.png')
    create_phase_scoring_chart(phase_data, output_path='figures/phase_scoring.png')
    create_bowling_metrics_chart(bowling_data, output_path='figures/bowling_metrics.png')
    create_venue_impact_chart(venue_data, output_path='figures/venue_impact.png')
    create_statistical_tests_chart(test_results, output_path='figures/statistical_tests.png')
    create_q_value_chart(test_results, corrected=True, output_path='figures/q_values.png')
    create_projection_chart(projections, output_path='figures/projections.png')
    
    print("\nAll figures saved to figures/ directory")
    
    # Save summary
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    
    summary = {
        'analysis_date': datetime.datetime.now().isoformat(),
        'data_summary': {
            'total_records': len(clean_data),
            'total_matches': clean_data['match_id'].nunique(),
            'total_sixes': clean_data['is_six'].sum(),
            'seasons_covered': list(range(2008, 2026))
        },
        'era_comparison': {
            'early_sr': round(early_sr, 2),
            'late_sr': round(late_sr, 2),
            'sr_change': round(sr_change, 2),
            'early_sixes': round(early_sixes, 2),
            'late_sixes': round(late_sixes, 2),
            'sixes_change': round(sixes_change, 1),
            'early_economy': round(early_econ, 2),
            'late_economy': round(late_econ, 2),
            'economy_change': round(econ_change, 2),
            'early_dot': round(early_dot * 100, 2),
            'late_dot': round(late_dot * 100, 2),
            'dot_change': round(dot_change, 1)
        },
        'impact_player_effect': {
            'pre_impact_sixes': round(pre_sixes, 2),
            'post_impact_sixes': round(post_sixes, 2),
            'change': round(impact_change, 2)
        },
        'statistical_tests': {
            'tests_passed': passed,
            'tests_total': len(test_results)
        },
        'projections': projections
    }
    
    output_path = Path('results/summary.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"Summary saved to: {output_path}")
    
    # Final validation
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    validations = [
        ('Strike Rate Change', sr_change, 7.24, 1),
        ('Sixes Growth', sixes_change, 361, 1),
        ('Economy Rate', econ_change, 7.37, 1),
        ('Dot Ball Ratio', abs(dot_change), 2.59, 1),
        ('Impact Player', impact_change, 1.4, 0.2),
        ('Stats Passed', passed, 7, 1)
    ]
    
    for name, found, claim, tolerance in validations:
        diff = abs(found - claim)
        status = '[OK]' if diff <= tolerance else '[X]'
        print(f"  {status} {name}: Found {found:.1f}, Claim {claim}, Diff {diff:.1f}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)


if __name__ == '__main__':
    main()
