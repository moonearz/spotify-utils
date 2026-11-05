import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def load_history(audio_only=True):
    history = []

    pattern = "*Audio*.json" if audio_only else "*.json"
    for file in sorted(DATA_DIR.glob(pattern)):
        with file.open(encoding="utf-8") as f:
            history.extend(json.load(f))

    return history


def most_played_artists(history, n=20):
    counts = Counter()

    for record in history:
        artist = record.get("master_metadata_album_artist_name")

        if artist is not None:
            counts[artist] += 1

    return counts.most_common(n)


def artist_distribution(
    history,
    n=50,
):
    if n < 1:
        raise ValueError("n must be > 0")
    counts = Counter()

    for record in history:
        artist = record.get("master_metadata_album_artist_name")

        if artist is not None:
            counts[artist] += 1

    top = dict(counts.most_common(n))
    remaining = counts.total() - sum(count for _, count in top.items())
    if remaining > 0:
        top["Other"] = remaining

    return top
