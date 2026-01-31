import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

print("="*80)
print("IPL BALL-BY-BALL DATA PROCESSING (2020-2025)")
print("="*80)

# Setup paths - script directory as base
SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / 'deliveries_updated_ipl_upto_2025.csv'
OUTPUT_FILE = SCRIPT_DIR / 'ball_by_ball_ipl_2020_2024.csv'
REPORT_FILE = SCRIPT_DIR / 'data_quality_report.txt'

# Read the dataset
print("\n[1/6] Reading dataset...")
print(f"   Input file: {INPUT_FILE}")
df = pd.read_csv(INPUT_FILE)
print(f"   Original dataset: {df.shape[0]:,} rows, {df.shape[1]} columns")

# Extract year from date
print("\n[2/6] Filtering data for 2020-2025...")
df['date'] = pd.to_datetime(df['date'])
df['season'] = df['date'].dt.year

# Filter for 2020-2025
df_filtered = df[(df['season'] >= 2020) & (df['season'] <= 2025)].copy()
print(f"   After filtering: {df_filtered.shape[0]:,} rows")
print(f"   Seasons: {sorted(df_filtered['season'].unique())}")

# Remove super overs - both by over number AND innings number
# Super overs can be coded as innings 3, 4, 5, 6 OR as over >= 20
before_super_over = len(df_filtered)
df_filtered = df_filtered[(df_filtered['over'] < 20) & (df_filtered['inning'] <= 2)].copy()
print(f"   Removed {before_super_over - len(df_filtered)} super over balls (over >= 20 or innings > 2)")

# Rename columns to match requirements
print("\n[3/6] Creating required columns...")
df_filtered = df_filtered.rename(columns={
    'matchId': 'match_id',
    'inning': 'innings',
    'batsman_runs': 'runs_off_bat'
})

# Calculate total runs on this ball (batsman runs + extras)
df_filtered['runs'] = df_filtered['runs_off_bat'] + df_filtered['extras']

# Create wicket indicator (1 if dismissal, 0 otherwise)
df_filtered['wicket'] = df_filtered['dismissal_kind'].notna().astype(int)

# Create boundary_type
def get_boundary_type(runs_off_bat):
    if runs_off_bat == 6:
        return 'six'
    elif runs_off_bat == 4:
        return 'four'
    else:
        return 'none'

df_filtered['boundary_type'] = df_filtered['runs_off_bat'].apply(get_boundary_type)

# Create phase (powerplay: 1-6, middle: 7-15, death: 16-20)
def get_phase(over):
    if over < 6:
        return 'powerplay'
    elif over < 15:
        return 'middle'
    else:
        return 'death'

df_filtered['phase'] = df_filtered['over'].apply(get_phase)

# Sort by match, innings, over, ball for proper cumulative calculations
df_filtered = df_filtered.sort_values(['match_id', 'innings', 'over', 'ball']).reset_index(drop=True)

# Calculate current_score and current_wickets (cumulative within each innings)
print("\n[4/6] Calculating cumulative scores and wickets...")
df_filtered['current_score'] = df_filtered.groupby(['match_id', 'innings'])['runs'].cumsum()
df_filtered['current_wickets'] = df_filtered.groupby(['match_id', 'innings'])['wicket'].cumsum()

# Calculate balls_remaining (120 balls in T20, minus current ball number)
# Ball number within innings = (over * 6) + ball
df_filtered['ball_number'] = (df_filtered['over'] * 6) + df_filtered['ball']
df_filtered['balls_remaining'] = 120 - df_filtered['ball_number']

# Calculate final scores for each innings
print("\n[5/6] Calculating final scores and match winners...")
final_scores = df_filtered.groupby(['match_id', 'innings'])['current_score'].max().reset_index()
final_scores_pivot = final_scores.pivot(index='match_id', columns='innings', values='current_score')
final_scores_pivot.columns = ['final_score_innings1', 'final_score_innings2']
final_scores_pivot = final_scores_pivot.reset_index()

# Merge final scores back to main dataframe
df_filtered = df_filtered.merge(final_scores_pivot, on='match_id', how='left')

# Determine match winner
def get_match_winner(row):
    if pd.isna(row['final_score_innings1']) or pd.isna(row['final_score_innings2']):
        return None
    
    if row['final_score_innings1'] > row['final_score_innings2']:
        # Innings 1 team won (batting first team)
        return row['batting_team'] if row['innings'] == 1 else row['bowling_team']
    else:
        # Innings 2 team won (chasing team)
        return row['bowling_team'] if row['innings'] == 1 else row['batting_team']

df_filtered['match_winner'] = df_filtered.apply(get_match_winner, axis=1)

# Flag unusual matches (score > 250 or < 100)
df_filtered['is_high_score'] = ((df_filtered['final_score_innings1'] > 250) | 
                                  (df_filtered['final_score_innings2'] > 250)).astype(int)
df_filtered['is_low_score'] = ((df_filtered['final_score_innings1'] < 100) | 
                                 (df_filtered['final_score_innings2'] < 100)).astype(int)

# Select and reorder columns for final output
output_columns = [
    'match_id', 'innings', 'over', 'ball', 'batsman', 'bowler', 'non_striker',
    'runs', 'wicket', 'boundary_type', 'current_score', 'current_wickets',
    'balls_remaining', 'phase', 'match_winner', 'final_score_innings1', 
    'final_score_innings2', 'batting_team', 'bowling_team', 'season', 'date',
    'is_high_score', 'is_low_score', 'dismissal_kind', 'player_dismissed'
]

df_output = df_filtered[output_columns].copy()

# Save the processed dataset
df_output.to_csv(OUTPUT_FILE, index=False)
print(f"\n✓ Saved processed dataset to: {OUTPUT_FILE}")
print(f"  Final dataset: {df_output.shape[0]:,} rows, {df_output.shape[1]} columns")

print("\n" + "="*80)
print("PROCESSING COMPLETE!")
print("="*80)
print(f"\nOutput files:")
print(f"  1. {OUTPUT_FILE}")
print(f"\nQuality report:")
print(f"  - Open WALKTHROUGH.html in your browser for detailed quality metrics")
print(f"\nNext steps:")
print(f"  - Review WALKTHROUGH.html for complete analysis")
print(f"  - Use the CSV for modeling and analysis")
print(f"  - Check flagged unusual matches if needed")
