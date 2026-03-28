"""
game_length.py — move count distribution analysis
Do shorter games correlate with losses? Are blunders ending games early?
"""

import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from pathlib import Path

USERNAME = "ygwr"
DATA_FILE = Path("data/games.json")
OUTPUT_DIR = Path("analysis/output")
OUTPUT_DIR.mkdir(exist_ok=True)


def count_moves(pgn):
    """Return the number of full moves in a PGN string."""
    move_numbers = re.findall(r"(\d+)\.", pgn)
    return int(move_numbers[-1]) if move_numbers else 0


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

        rows.append({
            "outcome": outcome,
            "raw_result": result,
            "moves": count_moves(g.get("pgn", "")),
            "time_class": g.get("time_class", "unknown"),
            "rated": g.get("rated", False),
            "color": my_color,
            "my_rating": my_data.get("rating", 0),
            "opponent": g["black" if my_color == "white" else "white"]["username"],
        })

    return pd.DataFrame(rows)


def plot_game_length(df):
    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor("#1a1a2e")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.5, wspace=0.35)

    colors = {"win": "#4ade80", "loss": "#f87171", "draw": "#94a3b8"}
    alpha = 0.75

    # --- 1. Overlapping histograms: move count by outcome ---
    ax1 = fig.add_subplot(gs[0, :])

    bins = range(0, df["moves"].max() + 5, 5)
    for outcome in ["loss", "win", "draw"]:
        sub = df[df["outcome"] == outcome]["moves"]
        ax1.hist(sub, bins=bins, alpha=alpha, color=colors[outcome],
                 label=f"{outcome} (n={len(sub)}, avg={sub.mean():.0f})", edgecolor="#1a1a2e")

    ax1.axvline(df[df["outcome"] == "win"]["moves"].mean(), color="#4ade80",
                linestyle="--", linewidth=1.2, alpha=0.7)
    ax1.axvline(df[df["outcome"] == "loss"]["moves"].mean(), color="#f87171",
                linestyle="--", linewidth=1.2, alpha=0.7)

    ax1.set_xlabel("Move count", color="white")
    ax1.set_ylabel("Games", color="white")
    ax1.set_title("Game Length Distribution by Outcome", color="white", pad=10)
    ax1.legend(facecolor="#2d2d4e", labelcolor="white", fontsize=9)
    ax1.set_facecolor("#2d2d4e")
    ax1.tick_params(colors="white")

    # --- 2. Box plots by outcome ---
    ax2 = fig.add_subplot(gs[1, 0])

    outcomes_ordered = ["win", "loss", "draw"]
    data_by_outcome = [df[df["outcome"] == o]["moves"].values for o in outcomes_ordered]

    bp = ax2.boxplot(data_by_outcome, patch_artist=True, medianprops={"color": "white", "linewidth": 2})
    for patch, outcome in zip(bp["boxes"], outcomes_ordered):
        patch.set_facecolor(colors[outcome])
        patch.set_alpha(0.8)
    for whisker in bp["whiskers"]:
        whisker.set_color("#94a3b8")
    for cap in bp["caps"]:
        cap.set_color("#94a3b8")
    for flier in bp["fliers"]:
        flier.set_markerfacecolor("#94a3b8")
        flier.set_markeredgecolor("#94a3b8")

    ax2.set_xticklabels(outcomes_ordered, color="white")
    ax2.set_ylabel("Moves", color="white")
    ax2.set_title("Move Count Spread by Outcome", color="white")
    ax2.set_facecolor("#2d2d4e")
    ax2.tick_params(colors="white")

    # --- 3. Move count by time class (box plots) ---
    ax3 = fig.add_subplot(gs[1, 1])

    time_classes = df["time_class"].unique()
    data_by_tc = [df[df["time_class"] == tc]["moves"].values for tc in time_classes]
    tc_colors_map = {"daily": "#818cf8", "rapid": "#fb923c", "blitz": "#34d399"}

    bp2 = ax3.boxplot(data_by_tc, patch_artist=True, medianprops={"color": "white", "linewidth": 2})
    for patch, tc in zip(bp2["boxes"], time_classes):
        patch.set_facecolor(tc_colors_map.get(tc, "#94a3b8"))
        patch.set_alpha(0.8)
    for whisker in bp2["whiskers"]:
        whisker.set_color("#94a3b8")
    for cap in bp2["caps"]:
        cap.set_color("#94a3b8")
    for flier in bp2["fliers"]:
        flier.set_markerfacecolor("#94a3b8")
        flier.set_markeredgecolor("#94a3b8")

    ax3.set_xticklabels(time_classes, color="white")
    ax3.set_ylabel("Moves", color="white")
    ax3.set_title("Move Count by Time Class", color="white")
    ax3.set_facecolor("#2d2d4e")
    ax3.tick_params(colors="white")

    fig.suptitle(f"Game Length Analysis — {USERNAME}", color="white", fontsize=16, y=0.98)

    output_path = OUTPUT_DIR / "game_length.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved >> {output_path}")
    plt.close()


def print_summary(df):
    print(f"\n{'='*50}")
    print(f"  {USERNAME} -- Game Length Summary")
    print(f"{'='*50}")

    print(f"\n  By outcome:")
    print(f"  {'Outcome':<8} {'N':>3} {'Min':>4} {'Avg':>5} {'Med':>5} {'Max':>4}")
    print(f"  {'-'*35}")
    for outcome in ["win", "loss", "draw"]:
        sub = df[df["outcome"] == outcome]["moves"]
        if not sub.empty:
            print(f"  {outcome:<8} {len(sub):>3} {sub.min():>4} {sub.mean():>5.1f} {sub.median():>5.1f} {sub.max():>4}")

    print(f"\n  By time class:")
    print(f"  {'Class':<8} {'N':>3} {'Avg':>5} {'Med':>5}")
    print(f"  {'-'*25}")
    for tc, group in df.groupby("time_class"):
        sub = group["moves"]
        print(f"  {tc:<8} {len(sub):>3} {sub.mean():>5.1f} {sub.median():>5.1f}")

    # Termination breakdown
    print(f"\n  Loss reasons:")
    losses = df[df["outcome"] == "loss"]
    for reason, count in losses["raw_result"].value_counts().items():
        avg_moves = losses[losses["raw_result"] == reason]["moves"].mean()
        print(f"    {reason:<12} {count:>2}x  avg {avg_moves:.0f} moves")

    print(f"{'='*50}\n")


if __name__ == "__main__":
    df = load_games()
    print_summary(df)
    plot_game_length(df)
