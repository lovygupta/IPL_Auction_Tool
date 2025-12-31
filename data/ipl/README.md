# IPL Dataset

This folder contains datasets related to the **Indian Premier League (IPL)** used for
player performance analysis, valuation modeling, and auction price prediction.

---

## Contents

This folder may include the following files (availability may vary by season):

- `matches.csv` — match-level details (season, teams, venue, result)
- `players.csv` — player metadata (role, batting/bowling style, nationality)
- `ball_by_ball.csv` — delivery-level data for each match
- `batting.csv` — aggregated batting statistics
- `bowling.csv` — aggregated bowling statistics
- `auctions.csv` — IPL auction data (base price, sold price, team)

---

## Intended Use

These datasets are intended for:
- Player valuation and base value modeling
- Auction price prediction
- Role-based and position-relative analysis
- Team composition and optimization studies
- Historical performance analysis

---

## Notes

- Data is compiled from public sources
- Player names may need normalization across files
- Missing values may exist for certain seasons or players
- All monetary values (if present) are in INR unless stated otherwise

---

## Example Usage

```python
import pandas as pd

batting = pd.read_csv("data/ipl/batting.csv")
bowling = pd.read_csv("data/ipl/bowling.csv")
