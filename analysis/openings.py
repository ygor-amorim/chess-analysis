"""
openings.py — opening repertoire analysis
Extracts ECO codes + names from PGN headers, shows win rate per opening family
"""

import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

USERNAME = "ygwr"
DATA_FILE = Path("data/games.json")
OUTPUT_DIR = Path("analysis/output")
OUTPUT_DIR.mkdir(exist_ok=True)

ECO_CATEGORIES = {
    "A": "Flank (A)",
    "B": "Semi-Open (B)",
    "C": "Open (C)",
    "D": "Closed/Semi (D)",
    "E": "Indian (E)",
}


def parse_pgn_header(pgn, tag):
    m = re.search(rf'\[{tag} "([^"]+)"\]', pgn)
    return m.group(1) if m else None


def extract_opening_family(eco_url):
    """Reduce 'English-Opening-Kings-English-Nimzowitsch-Variation-3.Nd4' to 'English Opening'."""
    if not eco_url:
        return "Unknown"
    path = eco_url.split("/")[-1].replace("-", " ")
    # Take only the first two words as the family name (e.g. "English Opening", "Kings Indian")
    words = path.split()
    # If second word is "Opening", "Defense", "Game", "System", etc. keep both
    family_markers = {"Opening", "Defense", "Game", "Gambit", "System", "Attack", "Variation"}
    if len(words) >= 2 and words[1] in family_markers:
        return f"{words[0]} {words[1]}"
    elif len(words) >= 3 and words[2] in family_markers:
        return f"{words[0]} {words[1]} {words[2]}"
    return words[0] if words else "Unknown"


def load_games():
    with open(DATA_FILE) as f:
        games = json.load(f)

    rows = []
    for g in games:
        my_color = "white" if g["white"]["username"].lower() == USERNAME else "black"
        my_data = g[my_color]

        result = my_data["result"]
        if result == "win":
            outcome = "win"
        elif result in ("checkmated", "resigned", "timeout", "abandoned", "lose"):
            outcome = "loss"
        else:
            outcome = "draw"

        pgn = g.get("pgn", "")
        eco = parse_pgn_header(pgn, "ECO")
        eco_url = parse_pgn_header(pgn, "ECOUrl")
        opening_family = extract_opening_family(eco_url)
        eco_category = ECO_CATEGORIES.get(eco[0] if eco else "?", "Other") if eco else "Other"

        rows.append({
            "color": my_color,
            "outcome": outcome,
            "eco": eco,
            "opening_family": opening_family,
            "eco_category": eco_category,
            "rated": g.get("rated", False),
            "time_class": g.get("time_class", "unknown"),
        })

    return pd.DataFrame(rows)


def plot_openings(df):
    fig = plt.figure(figsize=(16, 11))
    fig.patch.set_facecolor("#1a1a2e")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.5, wspace=0.35)

    colors = {"win": "#4ade80", "loss": "#f87171", "draw": "#94a3b8"}

    # --- 1. Top opening families (horizontal stacked bar) ---
    ax1 = fig.add_subplot(gs[0, :])  # full top row

    family_counts = df.groupby(["opening_family", "outcome"]).size().unstack(fill_value=0)
    # Ensure all columns exist
    for col in ["win", "loss", "draw"]:
        if col not in family_counts.columns:
            family_counts[col] = 0
    family_counts["total"] = family_counts.sum(axis=1)
    family_counts = family_counts.sort_values("total", ascending=True)

    y = range(len(family_counts))
    lefts = [0] * len(family_counts)
    for outcome in ["win", "loss", "draw"]:
        vals = family_counts[outcome].values
        bars = ax1.barh(list(y), vals, left=lefts, color=colors[outcome], label=outcome, height=0.6)
        lefts = [l + v for l, v in zip(lefts, vals)]

    ax1.set_yticks(list(y))
    ax1.set_yticklabels(family_counts.index, color="white", fontsize=9)
    ax1.set_title("Openings by Frequency — All Games (stacked W/L/D)", color="white", pad=10)
    ax1.legend(facecolor="#2d2d4e", labelcolor="white", fontsize=9, loc="lower right")
    ax1.set_facecolor("#2d2d4e")
    ax1.tick_params(colors="white")
    ax1.set_xlabel("Games", color="white")

    # --- 2. ECO category breakdown (rated only) ---
    ax2 = fig.add_subplot(gs[1, 0])

    rated_df = df[df["rated"]]
    cat_outcome = rated_df.groupby(["eco_category", "outcome"]).size().unstack(fill_value=0)
    for col in ["win", "loss", "draw"]:
        if col not in cat_outcome.columns:
            cat_outcome[col] = 0

    x = range(len(cat_outcome))
    width = 0.25
    for i, outcome in enumerate(["win", "loss", "draw"]):
        ax2.bar(
            [p + i * width for p in x],
            cat_outcome[outcome],
            width,
            label=outcome,
            color=colors[outcome],
        )
    ax2.set_xticks([p + width for p in x])
    ax2.set_xticklabels(cat_outcome.index, color="white", fontsize=8, rotation=15, ha="right")
    ax2.set_title("ECO Category — Rated Only", color="white")
    ax2.legend(facecolor="#2d2d4e", labelcolor="white", fontsize=8)
    ax2.set_facecolor("#2d2d4e")
    ax2.tick_params(colors="white")

    note = "A=Flank  B=Semi-Open  C=Open  D=Closed"
    ax2.set_xlabel(note, color="#94a3b8", fontsize=7)

    # --- 3. White vs Black opening mix ---
    ax3 = fig.add_subplot(gs[1, 1])

    white_games = df[df["color"] == "white"]
    black_games = df[df["color"] == "black"]

    white_wins = (white_games["outcome"] == "win").sum()
    black_wins = (black_games["outcome"] == "win").sum()

    white_top = white_games["opening_family"].value_counts().head(5)
    black_top = black_games["opening_family"].value_counts().head(5)

    # Two side-by-side mini horizontal bars
    bar_colors_wb = ["#f8fafc", "#1e1b4b"]  # white pieces = light, black pieces = dark accent

    y_w = range(len(white_top))
    y_b = range(len(black_top))

    ax3.barh(
        [y + 0.2 for y in y_w],
        white_top.values,
        height=0.35,
        color="#e2e8f0",
        label=f"White ({white_wins}W/{len(white_games)-white_wins}L)",
    )
    ax3.barh(
        [y - 0.2 for y in y_b],
        black_top.values,
        height=0.35,
        color="#818cf8",
        label=f"Black ({black_wins}W/{len(black_games)-black_wins}L)",
    )

    all_labels = list(white_top.index)
    # Fill gaps if lists differ in length
    max_len = max(len(white_top), len(black_top))
    ax3.set_yticks(range(max_len))
    ax3.set_yticklabels(all_labels[:max_len], color="white", fontsize=8)
    ax3.set_title("Top Openings: White vs Black", color="white")
    ax3.legend(facecolor="#2d2d4e", labelcolor="white", fontsize=8)
    ax3.set_facecolor("#2d2d4e")
    ax3.tick_params(colors="white")
    ax3.invert_yaxis()

    fig.suptitle(f"Opening Repertoire — {USERNAME}", color="white", fontsize=16, y=0.98)

    output_path = OUTPUT_DIR / "openings.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved >> {output_path}")
    plt.close()


def _print_family_table(subset):
    family_stats = subset.groupby("opening_family").agg(
        games=("outcome", "count"),
        wins=("outcome", lambda x: (x == "win").sum()),
        losses=("outcome", lambda x: (x == "loss").sum()),
        draws=("outcome", lambda x: (x == "draw").sum()),
    ).sort_values("games", ascending=False)

    print(f"  {'Opening':<35} {'G':>3} {'W':>3} {'L':>3} {'D':>3} {'Win%':>5}")
    print(f"  {'-'*55}")
    for name, row in family_stats.iterrows():
        pct = row.wins / row.games * 100 if row.games > 0 else 0
        marker = " *" if row.games >= 3 else ""
        print(f"  {name:<35} {int(row.games):>3} {int(row.wins):>3} {int(row.losses):>3} {int(row.draws):>3} {pct:>4.0f}%{marker}")
    print(f"  * = 3+ games (statistically meaningful)")


def print_summary(df):
    print(f"\n{'='*50}")
    print(f"  {USERNAME} -- Opening Repertoire (all {len(df)} games)")
    print(f"{'='*50}\n")
    _print_family_table(df)

    rated = df[df["rated"]]
    print(f"\n{'='*50}")
    print(f"  Rated games only ({len(rated)} games)")
    print(f"{'='*50}\n")
    _print_family_table(rated)

    print(f"\n  ECO category breakdown (rated only):")
    for cat, group in rated.groupby("eco_category"):
        w = (group["outcome"] == "win").sum()
        total = len(group)
        print(f"    {cat:<20} {total:>3} games  {w/total*100:.0f}% win rate")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    df = load_games()
    print_summary(df)
    plot_openings(df)
