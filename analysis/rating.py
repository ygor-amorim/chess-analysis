"""
rating.py — rating progression over time
Shows rapid + blitz rating trajectory across rated games
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime

USERNAME = "ygwr"
DATA_FILE = Path("data/games.json")
OUTPUT_DIR = Path("analysis/output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_rated_games():
    with open(DATA_FILE) as f:
        games = json.load(f)

    rows = []
    for g in games:
        if not g.get("rated"):
            continue

        my_color = "white" if g["white"]["username"].lower() == USERNAME else "black"
        my_data = g[my_color]
        opponent_data = g["black" if my_color == "white" else "white"]

        result = my_data["result"]
        if result == "win":
            outcome = "win"
        elif result in ("checkmated", "resigned", "timeout", "abandoned", "lose"):
            outcome = "loss"
        else:
            outcome = "draw"

        end_time = g.get("end_time", 0)
        rows.append({
            "datetime": datetime.fromtimestamp(end_time) if end_time else None,
            "time_class": g.get("time_class", "unknown"),
            "rating": my_data.get("rating", 0),
            "opponent_rating": opponent_data.get("rating", 0),
            "outcome": outcome,
            "color": my_color,
        })

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["datetime"]).sort_values("datetime")
    return df


def plot_rating(df):
    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor("#1a1a2e")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.5, wspace=0.35)

    outcome_markers = {"win": ("^", "#4ade80"), "loss": ("v", "#f87171"), "draw": ("o", "#94a3b8")}
    tc_colors = {"rapid": "#818cf8", "blitz": "#fb923c"}

    # --- 1. Rating progression over time (line + scatter per time class) ---
    ax1 = fig.add_subplot(gs[0, :])

    for tc in ["rapid", "blitz"]:
        tc_df = df[df["time_class"] == tc].copy()
        if tc_df.empty:
            continue

        color = tc_colors.get(tc, "#94a3b8")
        ax1.plot(tc_df["datetime"], tc_df["rating"], color=color, linewidth=1.5,
                 alpha=0.6, label=f"{tc} (line)")

        for outcome, (marker, mcolor) in outcome_markers.items():
            sub = tc_df[tc_df["outcome"] == outcome]
            if not sub.empty:
                ax1.scatter(sub["datetime"], sub["rating"], marker=marker,
                            color=mcolor, s=70, zorder=5,
                            label=f"{tc} {outcome}" if outcome == "win" else None)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax1.set_title("Rating Progression (Rated Games)", color="white", pad=10)
    ax1.set_ylabel("Rating", color="white")
    ax1.set_facecolor("#2d2d4e")
    ax1.tick_params(colors="white")

    # Custom legend
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_elements = [
        Line2D([0], [0], color=tc_colors["rapid"], linewidth=2, label="Rapid"),
        Line2D([0], [0], color=tc_colors["blitz"], linewidth=2, label="Blitz"),
        Line2D([0], [0], marker="^", color="#4ade80", linewidth=0, markersize=8, label="Win"),
        Line2D([0], [0], marker="v", color="#f87171", linewidth=0, markersize=8, label="Loss"),
        Line2D([0], [0], marker="o", color="#94a3b8", linewidth=0, markersize=8, label="Draw"),
    ]
    ax1.legend(handles=legend_elements, facecolor="#2d2d4e", labelcolor="white", fontsize=9)

    # --- 2. Rating high/low/current per time class ---
    ax2 = fig.add_subplot(gs[1, 0])

    stats = df.groupby("time_class")["rating"].agg(["min", "max", "last"]).reset_index()
    x = range(len(stats))
    width = 0.25

    bars_min = ax2.bar([p - width for p in x], stats["min"], width, color="#f87171", label="Min")
    bars_cur = ax2.bar(list(x), stats["last"], width, color="#818cf8", label="Current")
    bars_max = ax2.bar([p + width for p in x], stats["max"], width, color="#4ade80", label="Peak")

    ax2.set_xticks(list(x))
    ax2.set_xticklabels(stats["time_class"], color="white")
    ax2.set_title("Rating: Min / Current / Peak", color="white")
    ax2.legend(facecolor="#2d2d4e", labelcolor="white", fontsize=9)
    ax2.set_facecolor("#2d2d4e")
    ax2.tick_params(colors="white")

    # Add value labels
    for bars in [bars_min, bars_cur, bars_max]:
        for bar in bars:
            h = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2, h + 3, str(int(h)),
                     ha="center", va="bottom", color="white", fontsize=8)

    # --- 3. Opponent rating distribution (scatter: my rating vs opponent rating) ---
    ax3 = fig.add_subplot(gs[1, 1])

    for outcome, (marker, mcolor) in outcome_markers.items():
        sub = df[df["outcome"] == outcome]
        if not sub.empty:
            ax3.scatter(sub["opponent_rating"], sub["rating"], marker=marker,
                        color=mcolor, s=60, label=outcome, alpha=0.85)

    # Diagonal line (equal rating)
    all_ratings = pd.concat([df["rating"], df["opponent_rating"]])
    mn, mx = all_ratings.min() - 20, all_ratings.max() + 20
    ax3.plot([mn, mx], [mn, mx], color="#475569", linewidth=1, linestyle="--", alpha=0.5)

    ax3.set_xlabel("Opponent Rating", color="white")
    ax3.set_ylabel("My Rating", color="white")
    ax3.set_title("My Rating vs Opponent (rated games)", color="white")
    ax3.legend(facecolor="#2d2d4e", labelcolor="white", fontsize=9)
    ax3.set_facecolor("#2d2d4e")
    ax3.tick_params(colors="white")

    fig.suptitle(f"Rating Progression — {USERNAME}", color="white", fontsize=16, y=0.98)

    output_path = OUTPUT_DIR / "rating.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved >> {output_path}")
    plt.close()


def print_summary(df):
    print(f"\n{'='*45}")
    print(f"  {USERNAME} -- Rating Summary")
    print(f"{'='*45}")
    print(f"  Total rated games: {len(df)}")
    print()

    for tc, group in df.groupby("time_class"):
        group = group.sort_values("datetime")
        first = group.iloc[0]["rating"]
        last = group.iloc[-1]["rating"]
        peak = group["rating"].max()
        low = group["rating"].min()
        delta = last - first
        sign = "+" if delta >= 0 else ""
        w = (group["outcome"] == "win").sum()
        l = (group["outcome"] == "loss").sum()
        d = (group["outcome"] == "draw").sum()
        print(f"  {tc.upper()}")
        print(f"    Games : {len(group)}  ({w}W {l}L {d}D)")
        print(f"    Start : {int(first)}  Current: {int(last)}  ({sign}{int(delta)})")
        print(f"    Peak  : {int(peak)}  Low: {int(low)}")
        print()

    print(f"{'='*45}\n")


if __name__ == "__main__":
    df = load_rated_games()
    print_summary(df)
    plot_rating(df)
