"""
overview.py — high-level breakdown of all games
Outputs: win/loss/draw by color, by time class, rated vs unrated
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

USERNAME = "ygwr"
DATA_FILE = Path("data/games.json")
OUTPUT_DIR = Path("analysis/output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_games():
    with open(DATA_FILE) as f:
        games = json.load(f)

    rows = []
    for g in games:
        my_color = "white" if g["white"]["username"].lower() == USERNAME else "black"
        my_data = g[my_color]
        opponent_data = g["black" if my_color == "white" else "white"]

        result = my_data["result"]
        # Normalize results to win/loss/draw
        if result == "win":
            outcome = "win"
        elif result in ("checkmated", "resigned", "timeout", "abandoned", "lose"):
            outcome = "loss"
        else:
            outcome = "draw"

        rows.append({
            "color": my_color,
            "outcome": outcome,
            "raw_result": result,
            "my_rating": my_data.get("rating", 0),
            "opponent": opponent_data["username"],
            "opponent_rating": opponent_data.get("rating", 0),
            "time_class": g.get("time_class", "unknown"),
            "rated": g.get("rated", False),
            "end_time": g.get("end_time", 0),
        })

    return pd.DataFrame(rows)


def plot_overview(df):
    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor("#1a1a2e")
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    colors = {"win": "#4ade80", "loss": "#f87171", "draw": "#94a3b8"}

    # 1. Overall outcomes (pie)
    ax1 = fig.add_subplot(gs[0, 0])
    counts = df["outcome"].value_counts()
    ax1.pie(
        counts,
        labels=counts.index,
        colors=[colors[k] for k in counts.index],
        autopct="%1.0f%%",
        textprops={"color": "white", "fontsize": 11},
        wedgeprops={"linewidth": 0.5, "edgecolor": "#1a1a2e"},
    )
    ax1.set_title("Overall Results", color="white", pad=12)

    # 2. Outcomes by color (grouped bar)
    ax2 = fig.add_subplot(gs[0, 1])
    color_outcome = df.groupby(["color", "outcome"]).size().unstack(fill_value=0)
    x = range(len(color_outcome))
    width = 0.25
    for i, outcome in enumerate(["win", "loss", "draw"]):
        if outcome in color_outcome.columns:
            bars = ax2.bar(
                [p + i * width for p in x],
                color_outcome[outcome],
                width,
                label=outcome,
                color=colors[outcome],
            )
    ax2.set_xticks([p + width for p in x])
    ax2.set_xticklabels(color_outcome.index, color="white")
    ax2.set_title("Results by Color", color="white")
    ax2.legend(facecolor="#2d2d4e", labelcolor="white", fontsize=9)
    ax2.set_facecolor("#2d2d4e")
    ax2.tick_params(colors="white")

    # 3. Rated vs unrated (pie)
    ax3 = fig.add_subplot(gs[0, 2])
    rated_counts = df["rated"].map({True: "Rated", False: "Unrated"}).value_counts()
    ax3.pie(
        rated_counts,
        labels=rated_counts.index,
        colors=["#818cf8", "#94a3b8"],
        autopct="%1.0f%%",
        textprops={"color": "white", "fontsize": 11},
        wedgeprops={"linewidth": 0.5, "edgecolor": "#1a1a2e"},
    )
    ax3.set_title("Rated vs Unrated", color="white", pad=12)

    # 4. Outcomes by time class (grouped bar)
    ax4 = fig.add_subplot(gs[1, 0:2])
    tc_outcome = df.groupby(["time_class", "outcome"]).size().unstack(fill_value=0)
    x = range(len(tc_outcome))
    width = 0.25
    for i, outcome in enumerate(["win", "loss", "draw"]):
        if outcome in tc_outcome.columns:
            ax4.bar(
                [p + i * width for p in x],
                tc_outcome[outcome],
                width,
                label=outcome,
                color=colors[outcome],
            )
    ax4.set_xticks([p + width for p in x])
    ax4.set_xticklabels(tc_outcome.index, color="white")
    ax4.set_title("Results by Time Class", color="white")
    ax4.legend(facecolor="#2d2d4e", labelcolor="white", fontsize=9)
    ax4.set_facecolor("#2d2d4e")
    ax4.tick_params(colors="white")

    # 5. Games vs top opponents (horizontal bar)
    ax5 = fig.add_subplot(gs[1, 2])
    top_opponents = df["opponent"].value_counts().head(5)
    ax5.barh(top_opponents.index, top_opponents.values, color="#818cf8")
    ax5.set_title("Top Opponents", color="white")
    ax5.set_facecolor("#2d2d4e")
    ax5.tick_params(colors="white")
    ax5.invert_yaxis()

    fig.suptitle(f"Chess Analysis — {USERNAME}", color="white", fontsize=16, y=0.98)

    output_path = OUTPUT_DIR / "overview.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved >> {output_path}")
    plt.close()


def print_summary(df):
    total = len(df)
    wins = (df["outcome"] == "win").sum()
    losses = (df["outcome"] == "loss").sum()
    draws = (df["outcome"] == "draw").sum()

    print(f"\n{'='*40}")
    print(f"  {USERNAME} — Game Summary")
    print(f"{'='*40}")
    print(f"  Total games : {total}")
    print(f"  Wins        : {wins} ({wins/total*100:.0f}%)")
    print(f"  Losses      : {losses} ({losses/total*100:.0f}%)")
    print(f"  Draws       : {draws} ({draws/total*100:.0f}%)")
    print(f"\n  By time class:")
    for tc, group in df.groupby("time_class"):
        w = (group["outcome"] == "win").sum()
        l = (group["outcome"] == "loss").sum()
        d = (group["outcome"] == "draw").sum()
        print(f"    {tc:10} {len(group):3} games — {w}W {l}L {d}D")
    print(f"\n  Rated: {df['rated'].sum()} | Unrated: {(~df['rated']).sum()}")
    print(f"{'='*40}\n")


if __name__ == "__main__":
    df = load_games()
    print_summary(df)
    plot_overview(df)
