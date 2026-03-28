"""
fetch.py — pulls all games from chess.com and saves to data/games.json
Usage: python fetch.py
"""

import requests
import json
import time
from pathlib import Path

USERNAME = "ygwr"
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_archives():
    url = f"https://api.chess.com/pub/player/{USERNAME}/games/archives"
    res = requests.get(url, headers={"User-Agent": "chess-analysis/1.0"})
    res.raise_for_status()
    return res.json()["archives"]


def get_games_for_month(archive_url):
    res = requests.get(archive_url, headers={"User-Agent": "chess-analysis/1.0"})
    res.raise_for_status()
    return res.json()["games"]


def fetch_all():
    print(f"Fetching archives for {USERNAME}...")
    archives = get_archives()
    print(f"Found {len(archives)} months: {[a.split('/')[-2] + '/' + a.split('/')[-1] for a in archives]}")

    all_games = []
    for archive_url in archives:
        month = archive_url.split("/")[-2] + "/" + archive_url.split("/")[-1]
        games = get_games_for_month(archive_url)
        print(f"  {month}: {len(games)} games")
        all_games.extend(games)
        time.sleep(0.5)  # be polite to the API

    output = DATA_DIR / "games.json"
    with open(output, "w") as f:
        json.dump(all_games, f, indent=2)

    print(f"\nSaved {len(all_games)} total games to {output}")
    return all_games


if __name__ == "__main__":
    fetch_all()
