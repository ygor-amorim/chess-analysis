# Session Log — chess-analysis

Older sessions in `SESSION_ARCHIVE.md`.

---

## Session 2 — 2026-03-28

### What We Did
- Built `analysis/openings.py` — parses ECO codes and opening names from PGN headers, calculates win rate per opening family, generates 3-panel dark chart
- Built `analysis/rating.py` — rating progression over time for rapid + blitz, with W/L/D markers, min/current/peak bar chart, and opponent rating scatter
- Git repo initialized + first commit (`078313f`)

### Files Created/Modified
- `analysis/openings.py` — new: ECO-based opening repertoire analysis
- `analysis/rating.py` — new: rated game progression chart
- `analysis/output/openings.png` — new: chart output
- `analysis/output/rating.png` — new: chart output

### Key Decisions
| Decision | Reason |
|----------|--------|
| ECO code from PGN headers (not move parsing) | chess.com embeds ECO + ECOUrl in every game's PGN — no need to parse moves |
| Group by opening family (first 2 words) | Too many unique variants with 1 game each; family grouping gives meaningful sample sizes |
| Commit output PNGs | Charts should be visible on GitHub without re-running scripts |

### Key Findings (Session 2)
- English Opening dominates: 28/46 games (61%) — playing a lot of 1.c4 or facing it
- Rapid rating: started 162, peaked 355, currently 229 (+67 overall)
- Blitz: only 2 rated games, went 310 → 181 (-129)
- Queens Pawn Opening: 2/2 wins (100% — small sample but promising)

---

## Session 3 — 2026-03-28

### What We Did
- Created GitHub repo and pushed: https://github.com/ygor-amorim/chess-analysis
- Updated `analysis/openings.py`: ECO category panel now uses rated games only; `print_summary` shows two tables (all games + rated-only)

### Files Created/Modified
- `analysis/openings.py` — rated/unrated split in summary + chart panel
- `analysis/output/openings.png` — regenerated with updated ECO panel

### Key Decisions
| Decision | Reason |
|----------|--------|
| ECO category panel = rated only | Unrated coach games inflate totals and obscure competitive performance |
| Keep top chart as all-games | Still useful to see full opening exposure including practice |

### Key Findings (Session 3)
- Rated openings: English Opening 38% win rate (8 games), Flank (A) = 64% of rated games
- Semi-Open (B) rated win rate: 25% — worth improving

---

## Session 4 — 2026-03-28

### What We Did
- Built `analysis/game_length.py` — move count distribution by outcome and time class, box plots, loss reasons breakdown
- Added `README.md` with chart previews and key findings for GitHub
- Manual game analysis: ygwr vs Maria-BOT (1-0, 37 moves, Dutch Defense A84)

### Files Created/Modified
- `analysis/game_length.py` — new: move count analysis
- `analysis/output/game_length.png` — new: chart output
- `README.md` — new: GitHub landing page with all 4 chart previews

### Key Decisions
| Decision | Reason |
|----------|--------|
| Box plots over histograms for spread panel | Small dataset (46 games) makes histograms sparse; box plots show distribution better |

### Key Findings (Session 4)
- Resigned losses avg 22 moves, checkmates avg 29 — but coach practice (unrated) skews this heavily
- Draws are almost entirely stalemates (6/8), all vs Coach-Mae at 47–81 moves — endgame training pattern
- Short resigned losses are coaching sessions, not competitive collapses
- Manual game: beat Maria-BOT (1000) with English → Dutch, b-pawn promotion at move 22, Qbg8# at move 37
- Chasemaster20 (2-move resign) confirmed as a bot opponent, not a real player

### Next Session
- [ ] Re-fetch when chess.com archive updates (new games from 2026-03-28 not yet in API)
- [ ] Filter bot opponents from competitive analysis (Chasemaster20, Maria-BOT, Coach-*)
- [ ] `analysis/opponents.py` — breakdown by opponent type (human vs bot vs coach)
