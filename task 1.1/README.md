# IPL Ball-by-Ball Data Processing Pipeline

## Overview
Production-ready pipeline to process IPL deliveries data and create comprehensive ball-by-ball match dataset for 2020-2025.

## Files in This Directory

### Input Data
- **deliveries_updated_ipl_upto_2025.csv** - Raw IPL ball-by-ball data (2008-2025)

### Processing Script
- **process_ipl_data.py** - Main data processing pipeline
  - Uses `pathlib` for portable file paths (no hardcoded paths)
  - Filters data for 2020-2025
  - Removes super overs
  - Creates 25 required columns
  - Generates quality validation report

### Output Files
- **ball_by_ball_ipl_2020_2024.csv** - Processed dataset (413 matches, 99,076 records, 25 columns)
- **WALKTHROUGH.html** - Beautiful walkthrough with quality validation report (open in browser)

## Usage

### Run the Pipeline
```bash
python process_ipl_data.py
```

The script will:
1. Read `deliveries_updated_ipl_upto_2025.csv` from the same directory
2. Process and transform the data
3. Output `ball_by_ball_ipl_2020_2024.csv` and `data_quality_report.txt`

### Key Features
- ✅ **Portable paths** - Uses pathlib, works on any system
- ✅ **No hardcoded paths** - Script directory is automatically detected
- ✅ **Production-ready** - Clean, maintainable code
- ✅ **Validated output** - All quality checks passed

## Output Schema (25 columns)

| Column | Description |
|--------|-------------|
| `match_id` | Unique match identifier |
| `innings` | Innings number (1 or 2) |
| `over` | Over number (0-19) |
| `ball` | Ball number within over (1+, can exceed 6 due to wides/no-balls) |
| `batsman` | Batsman on strike |
| `bowler` | Bowler |
| `non_striker` | Non-striker batsman |
| `runs` | Total runs scored on this ball |
| `wicket` | Wicket indicator (1/0) |
| `boundary_type` | 'four', 'six', or 'none' |
| `current_score` | Running score up to this ball |
| `current_wickets` | Running wickets up to this ball |
| `balls_remaining` | Balls remaining in innings |
| `phase` | 'powerplay', 'middle', or 'death' |
| `match_winner` | Team that won the match |
| `final_score_innings1` | Final score of first innings |
| `final_score_innings2` | Final score of second innings |
| `batting_team` | Team batting |
| `bowling_team` | Team bowling |
| `season` | Year of the match |
| `date` | Match date |
| `is_high_score` | Flag for scores >250 |
| `is_low_score` | Flag for scores <100 |
| `dismissal_kind` | Type of dismissal (if any) |
| `player_dismissed` | Player dismissed (if any) |

## Data Quality Metrics

- **Matches**: 413 (2020-2025)
- **Completeness**: 99.96%
- **Score validation**: 100% (0 mismatches)
- **Unusual matches flagged**: 9 high-scoring, 12 low-scoring

## Next Steps

Use this dataset for:
1. Win probability modeling
2. Player performance analysis
3. Match outcome prediction
4. Phase-wise analysis (powerplay/middle/death)
