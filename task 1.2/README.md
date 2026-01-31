# Task 1.2: Player Performance Aggregation

## Overview
Comprehensive player-level batting and bowling statistics aggregated from IPL 2020-2024 ball-by-ball data (Task 1.1).

## Output Files

### 1. player_batting_stats_2020_2024.csv
**351 players, 66 columns**

Batting statistics for all players who faced at least 1 ball across 5 seasons (2020-2024).

**Column Categories**:
- **Overall**: `total_runs`, `total_balls`, `total_innings`, `overall_sr`, `total_fours`, `total_sixes`, `dot_ball_pct`
- **By Innings** (1st/2nd): `inn1_runs`, `inn1_balls`, `inn1_sr`, `inn1_fours`, `inn1_sixes`, `inn2_*`
- **By Phase** (powerplay/middle/death): `powerplay_runs`, `powerplay_balls`, `powerplay_sr`, `powerplay_fours`, `powerplay_sixes`, `powerplay_boundaries`, `middle_*`, `death_*`
- **By Context**: `runs_in_wins`, `runs_in_losses`, `runs_in_close_matches`, `runs_competitive_total`
- **By Innings × Phase** (18 combinations): `inn1_powerplay_runs`, `inn1_powerplay_balls`, `inn1_powerplay_sr`, `inn1_powerplay_boundaries`, etc.
- **Additional**: `runs_vs_quality_bowling`, `runs_vs_weak_bowling`

### 2. player_bowling_stats_2020_2024.csv
**263 players, 69 columns**

Bowling statistics for all players who bowled at least 1 ball across 5 seasons (2020-2024).

**Column Categories**:
- **Overall**: `total_balls`, `total_overs`, `total_runs`, `total_wickets`, `overall_economy`, `dot_ball_pct`
- **By Innings** (1st/2nd): `inn1_balls`, `inn1_overs`, `inn1_runs`, `inn1_wickets`, `inn1_economy`, `inn2_*`
- **By Phase** (powerplay/middle/death): `powerplay_balls`, `powerplay_overs`, `powerplay_runs`, `powerplay_wickets`, `powerplay_economy`, `powerplay_dot_ball_pct`, `middle_*`, `death_*`
- **By Context**: `wickets_in_wins`, `wickets_in_losses`, `wickets_in_close_matches`, `runs_in_close_matches`
- **By Innings × Phase** (18 combinations): `inn1_powerplay_balls`, `inn1_powerplay_overs`, `inn1_powerplay_runs`, `inn1_powerplay_wickets`, `inn1_powerplay_economy`, etc.

### 3. summary_statistics.md
League-wide statistics and top performers.

## Key Statistics

### Player Distribution
- **Batsmen**: 351 total
  - 1-5 innings: 147 players
  - 6-10 innings: 55 players
  - 11-20 innings: 55 players
  - 20+ innings: 94 players

- **Bowlers**: 263 total
  - <5 overs: 46 players
  - 5-20 overs: 67 players
  - 20-50 overs: 56 players
  - 50+ overs: 94 players

### League Averages (Batting)
- **Powerplay**: League SR 137.2
- **Middle**: League SR 133.9
- **Death**: League SR 163.8

### League Averages (Bowling)
- **Powerplay**: League Economy 8.23
- **Middle**: League Economy 8.03
- **Death**: League Economy 9.83

**Note**: League averages use **weighted calculations** (total runs / total balls for SR, total runs / total overs for economy) to accurately reflect league-wide IPL performance.

## Design Decisions

### No Role Classification
- **Rationale**: Role classification (batsman vs bowler vs all-rounder) is deferred to downstream WPA modeling
- **Benefit**: Preserves all data without arbitrary thresholds
- **Example**: Bhuvneshwar Kumar appears in both files if he batted and bowled

### No Minimum Thresholds
- **Rationale**: Include all players regardless of sample size for maximum flexibility
- **Benefit**: Downstream models can apply their own filtering based on needs
- **Note**: `total_innings` and `total_overs` columns allow easy filtering

### Heuristics Used
- **Close Match**: Decided by <15 runs margin
- **Quality Bowling**: Economy <7
- **Weak Bowling**: Economy >10
- **Competitive Total**: Team score > league average (170.8)

## Usage

### Load Data
```python
import pandas as pd

# Load batting stats
batting_df = pd.read_csv('player_batting_stats_2020_2024.csv')

# Load bowling stats
bowling_df = pd.read_csv('player_bowling_stats_2020_2024.csv')
```

### Filter by Sample Size
```python
# Get batsmen with at least 10 innings
regular_batsmen = batting_df[batting_df['total_innings'] >= 10]

# Get bowlers with at least 20 overs
regular_bowlers = bowling_df[bowling_df['total_overs'] >= 20]
```

### Analyze Phase Performance
```python
# Compare powerplay vs death SR for top batsmen
top_batsmen = batting_df.nlargest(20, 'total_runs')
print(top_batsmen[['batsman', 'powerplay_sr', 'death_sr']])

# Compare powerplay vs death economy for top bowlers
top_bowlers = bowling_df.nlargest(20, 'total_wickets')
print(top_bowlers[['bowler', 'powerplay_economy', 'death_economy']])
```

## Next Steps (Phase 2)

These statistics will feed into:
1. **Win Probability Model** (Task 2.1-2.2): Calculate WPA for each ball
2. **Coefficient Derivation** (Task 2.3-2.5): Derive boundary bonuses, SR premiums, and situational coefficients from WPA
3. **Player Valuation**: Use WPA-weighted performance for auction value modeling

## Known Issues

### Player Name Inconsistency
The source data (Task 1.1) contains inconsistent player name formatting:
- Some players have full names with spaces: "Shubman Gill", "V Kohli"
- Some players have initials without spaces: "SA Yadav" (Suryakumar Yadav), "SV Samson" (Sanju Samson)

**Impact**: This is preserved in the aggregated stats as we use exact names from source data.

**Recommendation**: Handle name standardization in a future data cleaning task before modeling.

**Examples**:
- "SA Yadav" = Suryakumar Yadav (Mumbai Indians)
- "SV Samson" = Sanju Samson (Rajasthan Royals)
- "RD Gaikwad" = Ruturaj Gaikwad (Chennai Super Kings)

## Data Quality

- **Completeness**: 100% of players who batted/bowled are included
- **Validation**: Total runs aggregated matches source data
- **Consistency**: All calculations use consistent phase definitions (PP: 1-6, Middle: 7-15, Death: 16-20)

## Files Generated
```
task 1.2/
├── aggregate_player_stats.py       # Main aggregation script
├── player_batting_stats_2020_2024.csv  # 351 players × 66 columns
├── player_bowling_stats_2020_2024.csv  # 263 players × 69 columns
├── summary_statistics.md           # League averages and top performers
└── README.md                       # This file
```

## Script Execution
```bash
cd "c:\Users\91620\Desktop\ipl model\task 1.2"
python aggregate_player_stats.py
```

**Runtime**: ~2-3 minutes for full aggregation
