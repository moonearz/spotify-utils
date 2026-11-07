import json
from collections import Counter
from datetime import date

from spotify_utils.config import (
    DATA_DIR,
    DEFAULT_PAGE_SIZE,
)
from spotify_utils.settings import ListeningMetric
from spotify_utils.utils import normalize_track


def load_history(audio_only=True):
    history = []

    pattern = "*Audio*.json" if audio_only else "*.json"
    for file in sorted(DATA_DIR.glob(pattern)):
        with file.open(encoding="utf-8") as f:
            history.extend(json.load(f))

    return history


def filter_history(history, start_date=None, end_date=None):
    return [
        record
        for record in history
        if (
            (start_date is None or date.fromisoformat(record["ts"][:10]) >= start_date)
            and (end_date is None or date.fromisoformat(record["ts"][:10]) <= end_date)
        )
    ]


def artist_counts(history, metric):
    counter = Counter()

    for record in history:
        artist = record.get("master_metadata_album_artist_name")

        if artist is None:
            continue

        if metric == ListeningMetric.PLAYS:
            counter[artist] += 1

        elif metric == ListeningMetric.TIME:
            counter[artist] += record.get("ms_played", 0)

    return counter


def most_played_artists(history, metric):
    counts = artist_counts(history, metric)
    return counts.most_common()


def artist_distribution(
    history,
    metric,
    n=DEFAULT_PAGE_SIZE,
):
    if n < 1:
        raise ValueError("n must be > 0")

    counts = artist_counts(history, metric)

    top = dict(counts.most_common(n))
    remaining = counts.total() - sum(top.values())
    if remaining > 0:
        top["Other"] = remaining

    return top


def song_skip_stats(history):
    counts = Counter()
    skips = Counter()
    display_names = {}

    for record in history:
        track = (
            record.get("master_metadata_track_name"),
            record.get("master_metadata_album_artist_name"),
        )
        if any(part is None for part in track):
            continue

        skipped = record.get("skipped")
        if skipped is None:
            continue

        normalized_track = normalize_track(track)
        counts[normalized_track] += 1
        display_names.setdefault(normalized_track, track)
        if skipped:
            skips[normalized_track] += 1

    return {
        normalized_track: {
            "plays": counts[normalized_track],
            "skips": skips[normalized_track],
            "skip_rate": skips[normalized_track] / counts[normalized_track],
            "display_name": display_names[normalized_track],
        }
        for normalized_track in counts
    }


def most_skipped_songs(history):
    stats = song_skip_stats(history)

    return sorted(
        stats.items(),
        key=lambda item: item[1]["skip_rate"],
        reverse=True,
    )
