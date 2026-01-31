import pandas as pd
import numpy as np
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR.parent / "task 1.1" / "ball_by_ball_ipl_2020_2024.csv"
OUTPUT_DIR = SCRIPT_DIR

def load_data():
    """Load ball-by-ball data from Task 1.1"""
    print(f"Loading data from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} deliveries from {df['match_id'].nunique()} matches")
    return df

def calculate_league_average_score(df):
    """Calculate league average score per innings for competitive total threshold"""
    innings_scores = df.groupby(['match_id', 'innings'])['current_score'].max()
    return innings_scores.mean()

def aggregate_batting_stats(df):
    """
    Aggregate batting statistics for all players who faced at least 1 ball.
    No minimum threshold - include everyone for downstream WPA analysis.
    """
    print("\n=== Aggregating Batting Statistics ===")
    
    # Calculate league average for competitive total
    league_avg_score = calculate_league_average_score(df)
    print(f"League average score: {league_avg_score:.1f}")
    
    # Add helper columns
    df['is_dot_ball'] = (df['runs'] == 0) & (df['wicket'] == 0)
    df['is_four'] = df['boundary_type'] == 'four'
    df['is_six'] = df['boundary_type'] == 'six'
    df['is_boundary'] = df['boundary_type'].isin(['four', 'six'])
    
    # Determine if team won
    df['team_won'] = df['batting_team'] == df['match_winner']
    
    # Determine close matches (margin < 15 runs)
    match_info = df[['match_id', 'final_score_innings1', 'final_score_innings2']].drop_duplicates('match_id')
    match_info['margin'] = abs(match_info['final_score_innings1'] - match_info['final_score_innings2'])
    close_match_ids = match_info[match_info['margin'] < 15]['match_id'].values
    df['is_close_match'] = df['match_id'].isin(close_match_ids)
    
    # Determine competitive total (team score > league average)
    innings_max_scores = df.groupby(['match_id', 'innings'])['current_score'].transform('max')
    df['is_competitive_total'] = innings_max_scores > league_avg_score
    
    # Calculate bowler economy for quality bowling analysis
    bowler_stats = df.groupby('bowler').agg({'runs': 'sum', 'batsman': 'count'}).rename(columns={'batsman': 'balls'})
    bowler_stats['economy'] = bowler_stats['runs'] / (bowler_stats['balls'] / 6)
    bowler_stats.loc[bowler_stats['balls'] < 6, 'economy'] = np.nan
    df['bowler_economy'] = df['bowler'].map(bowler_stats['economy'])
    df['is_quality_bowling'] = df['bowler_economy'] < 7
    df['is_weak_bowling'] = df['bowler_economy'] > 10
    
    batting_stats = []
    
    for batsman in df['batsman'].unique():
        player_df = df[df['batsman'] == batsman].copy()
        
        stats = {'batsman': batsman}
        
        # === OVERALL STATISTICS ===
        stats['total_runs'] = player_df['runs'].sum()
        stats['total_balls'] = len(player_df)
        stats['total_innings'] = player_df.groupby('match_id')['innings'].nunique().sum()
        stats['overall_sr'] = (stats['total_runs'] / stats['total_balls'] * 100) if stats['total_balls'] > 0 else 0
        stats['total_fours'] = player_df['is_four'].sum()
        stats['total_sixes'] = player_df['is_six'].sum()
        stats['dot_ball_pct'] = (player_df['is_dot_ball'].sum() / stats['total_balls'] * 100) if stats['total_balls'] > 0 else 0
        
        # === BY INNINGS ===
        for inn in [1, 2]:
            inn_df = player_df[player_df['innings'] == inn]
            prefix = f'inn{inn}_'
            stats[f'{prefix}runs'] = inn_df['runs'].sum()
            stats[f'{prefix}balls'] = len(inn_df)
            stats[f'{prefix}sr'] = (stats[f'{prefix}runs'] / stats[f'{prefix}balls'] * 100) if stats[f'{prefix}balls'] > 0 else 0
            stats[f'{prefix}fours'] = inn_df['is_four'].sum()
            stats[f'{prefix}sixes'] = inn_df['is_six'].sum()
        
        # === BY PHASE ===
        for phase in ['powerplay', 'middle', 'death']:
            phase_df = player_df[player_df['phase'] == phase]
            stats[f'{phase}_runs'] = phase_df['runs'].sum()
            stats[f'{phase}_balls'] = len(phase_df)
            stats[f'{phase}_sr'] = (stats[f'{phase}_runs'] / stats[f'{phase}_balls'] * 100) if stats[f'{phase}_balls'] > 0 else 0
            stats[f'{phase}_fours'] = phase_df['is_four'].sum()
            stats[f'{phase}_sixes'] = phase_df['is_six'].sum()
            stats[f'{phase}_boundaries'] = phase_df['is_boundary'].sum()
        
        # === BY MATCH CONTEXT ===
        stats['runs_in_wins'] = player_df[player_df['team_won']]['runs'].sum()
        stats['runs_in_losses'] = player_df[~player_df['team_won']]['runs'].sum()
        stats['runs_in_close_matches'] = player_df[player_df['is_close_match']]['runs'].sum()
        stats['runs_competitive_total'] = player_df[player_df['is_competitive_total']]['runs'].sum()
        
        # === BY INNINGS × PHASE (18 combinations) ===
        for inn in [1, 2]:
            for phase in ['powerplay', 'middle', 'death']:
                combo_df = player_df[(player_df['innings'] == inn) & (player_df['phase'] == phase)]
                prefix = f'inn{inn}_{phase}_'
                stats[f'{prefix}runs'] = combo_df['runs'].sum()
                stats[f'{prefix}balls'] = len(combo_df)
                stats[f'{prefix}sr'] = (stats[f'{prefix}runs'] / stats[f'{prefix}balls'] * 100) if stats[f'{prefix}balls'] > 0 else 0
                stats[f'{prefix}boundaries'] = combo_df['is_boundary'].sum()
        
        # === ADDITIONAL METRICS ===
        stats['runs_vs_quality_bowling'] = player_df[player_df['is_quality_bowling']]['runs'].sum()
        stats['runs_vs_weak_bowling'] = player_df[player_df['is_weak_bowling']]['runs'].sum()
        
        batting_stats.append(stats)
    
    batting_df = pd.DataFrame(batting_stats)
    batting_df = batting_df.sort_values('total_runs', ascending=False).reset_index(drop=True)
    
    print(f"Aggregated stats for {len(batting_df)} batsmen")
    print(f"Total runs aggregated: {batting_df['total_runs'].sum():,}")
    
    return batting_df

def aggregate_bowling_stats(df):
    """
    Aggregate bowling statistics for all players who bowled at least 1 ball.
    No minimum threshold - include everyone for downstream WPA analysis.
    """
    print("\n=== Aggregating Bowling Statistics ===")
    
    # Add helper columns
    df['is_dot_ball'] = (df['runs'] == 0) & (df['wicket'] == 0)
    df['team_won'] = df['bowling_team'] == df['match_winner']
    
    # Determine close matches
    match_info = df[['match_id', 'final_score_innings1', 'final_score_innings2']].drop_duplicates('match_id')
    match_info['margin'] = abs(match_info['final_score_innings1'] - match_info['final_score_innings2'])
    close_match_ids = match_info[match_info['margin'] < 15]['match_id'].values
    df['is_close_match'] = df['match_id'].isin(close_match_ids)
    
    bowling_stats = []
    
    for bowler in df['bowler'].unique():
        player_df = df[df['bowler'] == bowler].copy()
        
        stats = {'bowler': bowler}
        
        # === OVERALL STATISTICS ===
        stats['total_balls'] = len(player_df)
        stats['total_overs'] = stats['total_balls'] / 6
        stats['total_runs'] = player_df['runs'].sum()
        stats['total_wickets'] = player_df['wicket'].sum()
        stats['overall_economy'] = (stats['total_runs'] / stats['total_overs']) if stats['total_overs'] > 0 else 0
        stats['dot_ball_pct'] = (player_df['is_dot_ball'].sum() / stats['total_balls'] * 100) if stats['total_balls'] > 0 else 0
        
        # === BY INNINGS ===
        for inn in [1, 2]:
            inn_df = player_df[player_df['innings'] == inn]
            prefix = f'inn{inn}_'
            stats[f'{prefix}balls'] = len(inn_df)
            stats[f'{prefix}overs'] = stats[f'{prefix}balls'] / 6
            stats[f'{prefix}runs'] = inn_df['runs'].sum()
            stats[f'{prefix}wickets'] = inn_df['wicket'].sum()
            stats[f'{prefix}economy'] = (stats[f'{prefix}runs'] / stats[f'{prefix}overs']) if stats[f'{prefix}overs'] > 0 else 0
        
        # === BY PHASE ===
        for phase in ['powerplay', 'middle', 'death']:
            phase_df = player_df[player_df['phase'] == phase]
            stats[f'{phase}_balls'] = len(phase_df)
            stats[f'{phase}_overs'] = stats[f'{phase}_balls'] / 6
            stats[f'{phase}_runs'] = phase_df['runs'].sum()
            stats[f'{phase}_wickets'] = phase_df['wicket'].sum()
            stats[f'{phase}_economy'] = (stats[f'{phase}_runs'] / stats[f'{phase}_overs']) if stats[f'{phase}_overs'] > 0 else 0
            stats[f'{phase}_dot_ball_pct'] = (phase_df['is_dot_ball'].sum() / stats[f'{phase}_balls'] * 100) if stats[f'{phase}_balls'] > 0 else 0
        
        # === BY MATCH CONTEXT ===
        stats['wickets_in_wins'] = player_df[player_df['team_won']]['wicket'].sum()
        stats['wickets_in_losses'] = player_df[~player_df['team_won']]['wicket'].sum()
        stats['wickets_in_close_matches'] = player_df[player_df['is_close_match']]['wicket'].sum()
        stats['runs_in_close_matches'] = player_df[player_df['is_close_match']]['runs'].sum()
        
        # === BY INNINGS × PHASE (18 combinations) ===
        for inn in [1, 2]:
            for phase in ['powerplay', 'middle', 'death']:
                combo_df = player_df[(player_df['innings'] == inn) & (player_df['phase'] == phase)]
                prefix = f'inn{inn}_{phase}_'
                stats[f'{prefix}balls'] = len(combo_df)
                stats[f'{prefix}overs'] = stats[f'{prefix}balls'] / 6
                stats[f'{prefix}runs'] = combo_df['runs'].sum()
                stats[f'{prefix}wickets'] = combo_df['wicket'].sum()
                stats[f'{prefix}economy'] = (stats[f'{prefix}runs'] / stats[f'{prefix}overs']) if stats[f'{prefix}overs'] > 0 else 0
        
        bowling_stats.append(stats)
    
    bowling_df = pd.DataFrame(bowling_stats)
    bowling_df = bowling_df.sort_values('total_wickets', ascending=False).reset_index(drop=True)
    
    print(f"Aggregated stats for {len(bowling_df)} bowlers")
    print(f"Total wickets aggregated: {int(bowling_df['total_wickets'].sum())}")
    
    return bowling_df

def generate_summary_statistics(df, batting_df, bowling_df):
    """Generate summary statistics document"""
    print("\n=== Generating Summary Statistics ===")
    
    summary = []
    summary.append("# Task 1.2: Player Performance Aggregation - Summary Statistics\n")
    summary.append(f"**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    summary.append("---\n\n")
    
    # Dataset overview
    summary.append("## Dataset Overview\n")
    summary.append(f"- **Seasons**: 2020-2024\n")
    summary.append(f"- **Total Matches**: {df['match_id'].nunique()}\n")
    summary.append(f"- **Total Deliveries**: {len(df):,}\n\n")
    
    # Player counts
    summary.append("## Player Counts\n")
    summary.append(f"- **Batsmen**: {len(batting_df)} (all who faced >=1 ball)\n")
    summary.append(f"- **Bowlers**: {len(bowling_df)} (all who bowled >=1 ball)\n\n")
    
    # Innings distribution
    summary.append("## Innings Distribution (Batsmen)\n")
    innings_dist = batting_df['total_innings'].value_counts().sort_index()
    summary.append(f"- **1-5 innings**: {(batting_df['total_innings'] <= 5).sum()} players\n")
    summary.append(f"- **6-10 innings**: {((batting_df['total_innings'] > 5) & (batting_df['total_innings'] <= 10)).sum()} players\n")
    summary.append(f"- **11-20 innings**: {((batting_df['total_innings'] > 10) & (batting_df['total_innings'] <= 20)).sum()} players\n")
    summary.append(f"- **20+ innings**: {(batting_df['total_innings'] > 20).sum()} players\n\n")
    
    # Overs distribution
    summary.append("## Overs Distribution (Bowlers)\n")
    summary.append(f"- **<5 overs**: {(bowling_df['total_overs'] < 5).sum()} players\n")
    summary.append(f"- **5-20 overs**: {((bowling_df['total_overs'] >= 5) & (bowling_df['total_overs'] < 20)).sum()} players\n")
    summary.append(f"- **20-50 overs**: {((bowling_df['total_overs'] >= 20) & (bowling_df['total_overs'] < 50)).sum()} players\n")
    summary.append(f"- **50+ overs**: {(bowling_df['total_overs'] >= 50).sum()} players\n\n")
    
    # League averages by phase
    summary.append("## League Averages by Phase\n\n")
    summary.append("### Batting\n")
    for phase in ['powerplay', 'middle', 'death']:
        # Weighted average SR by balls faced (league-wide)
        total_runs = batting_df[f'{phase}_runs'].sum()
        total_balls = batting_df[f'{phase}_balls'].sum()
        weighted_sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
        summary.append(f"- **{phase.capitalize()}**: League SR = {weighted_sr:.1f}\n")
    
    summary.append("\n### Bowling\n")
    for phase in ['powerplay', 'middle', 'death']:
        # Weighted average economy by overs bowled (league-wide)
        total_runs = bowling_df[f'{phase}_runs'].sum()
        total_overs = bowling_df[f'{phase}_overs'].sum()
        weighted_economy = (total_runs / total_overs) if total_overs > 0 else 0
        summary.append(f"- **{phase.capitalize()}**: League Economy = {weighted_economy:.2f}\n")
    
    # League averages by innings
    summary.append("\n## League Averages by Innings\n\n")
    summary.append("### Batting\n")
    for inn in [1, 2]:
        # Weighted average SR (league-wide)
        total_runs = batting_df[f'inn{inn}_runs'].sum()
        total_balls = batting_df[f'inn{inn}_balls'].sum()
        weighted_sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
        summary.append(f"- **Innings {inn}**: League SR = {weighted_sr:.1f}\n")
    
    summary.append("\n### Bowling\n")
    for inn in [1, 2]:
        # Weighted average economy (league-wide)
        total_runs = bowling_df[f'inn{inn}_runs'].sum()
        total_overs = bowling_df[f'inn{inn}_overs'].sum()
        weighted_economy = (total_runs / total_overs) if total_overs > 0 else 0
        summary.append(f"- **Innings {inn}**: League Economy = {weighted_economy:.2f}\n")
    
    # Top performers
    summary.append("\n## Top Performers (Overall)\n\n")
    summary.append("### Top 5 Run Scorers\n")
    for idx, row in batting_df.head(5).iterrows():
        summary.append(f"{idx+1}. **{row['batsman']}**: {int(row['total_runs'])} runs @ SR {row['overall_sr']:.1f}\n")
    
    summary.append("\n### Top 5 Wicket Takers\n")
    for idx, row in bowling_df.head(5).iterrows():
        summary.append(f"{idx+1}. **{row['bowler']}**: {int(row['total_wickets'])} wickets @ Econ {row['overall_economy']:.2f}\n")
    
    summary_text = ''.join(summary)
    
    output_file = OUTPUT_DIR / "summary_statistics.md"
    with open(output_file, 'w') as f:
        f.write(summary_text)
    
    print(f"Summary statistics saved to: {output_file}")
    return summary_text

def main():
    """Main execution function"""
    print("=" * 60)
    print("Task 1.2: Player Performance Aggregation")
    print("=" * 60)
    
    # Load data
    df = load_data()
    
    # Aggregate batting stats
    batting_df = aggregate_batting_stats(df)
    batting_output = OUTPUT_DIR / "player_batting_stats_2020_2024.csv"
    batting_df.to_csv(batting_output, index=False)
    print(f"Batting stats saved to: {batting_output}")
    
    # Aggregate bowling stats
    bowling_df = aggregate_bowling_stats(df)
    bowling_output = OUTPUT_DIR / "player_bowling_stats_2020_2024.csv"
    bowling_df.to_csv(bowling_output, index=False)
    print(f"Bowling stats saved to: {bowling_output}")
    
    # Generate summary
    summary = generate_summary_statistics(df, batting_df, bowling_df)
    
    print("\n" + "=" * 60)
    print("Task 1.2 Complete!")
    print("=" * 60)
    print(f"\nOutputs created:")
    print(f"  1. {batting_output.name} ({len(batting_df)} players)")
    print(f"  2. {bowling_output.name} ({len(bowling_df)} players)")
    print(f"  3. summary_statistics.md")

if __name__ == "__main__":
    main()
