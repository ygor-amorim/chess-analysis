# CLAUDE.md - chess-analysis

## Project Overview

Chess game analysis tool for player **ygwr** (chess.com). Pulls game data via the chess.com public API, processes it with Python/pandas, and generates visualizations with matplotlib.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Data fetching | Python + requests |
| Analysis | Python + pandas |
| Visualization | matplotlib |
| Data storage | JSON (local, gitignored) |
| Future dashboard | Node.js + React (Phase 2) |

## Structure

```
chess-analysis/
├── fetch.py          # Pull all games from chess.com API → data/games.json
├── analysis/         # Analysis scripts (one per topic)
├── data/             # Raw + processed data (gitignored)
├── .venv/            # Python virtual environment (gitignored)
└── CLAUDE.md
```

## Running

```bash
# Activate virtual environment first (always)
.venv\Scripts\Activate.ps1

# Fetch all games
python fetch.py

# Run an analysis
python analysis/overview.py
```

## Data Source

chess.com public API — no auth required.
- Archives: `https://api.chess.com/pub/player/ygwr/games/archives`
- Monthly games: `https://api.chess.com/pub/player/ygwr/games/{year}/{month}`

## Session Start Protocol

1. Read this file
2. Read `SESSION_LOG.md`

## Analyses Planned

- [ ] Overview: win/loss/draw by color, by time class
- [ ] Openings: most played, win rate per opening
- [ ] Rating progression over time
- [ ] Game length (moves) distribution
- [ ] Opponent rating breakdown
- [ ] Blunder patterns (needs engine — Phase 2)
