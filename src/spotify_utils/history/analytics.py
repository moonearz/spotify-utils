import json
from collections import Counter
from datetime import date

from spotify_utils.config import (
    DATA_DIR,
    DEFAULT_NUM_RESULTS,
    MIN_NUM_TRACKS,
)
from spotify_utils.history.config import ListeningMetric


def load_history(audio_only=True):
    history = []

    pattern = "*Audio*.json" if audio_only else "*.json"
    for file in sorted(DATA_DIR.glob(pattern)):
        with file.open(encoding="utf-8") as f:
            history.extend(json.load(f))

    return history


def filter_history(history, start_date):
    if start_date is None:
        return history

    return [
        record
        for record in history
        if date.fromisoformat(record["ts"][:10]) >= start_date
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


def most_played_artists(history, metric, n=DEFAULT_NUM_RESULTS):
    counts = artist_counts(history, metric)
    return counts.most_common(n)


def artist_distribution(
    history,
    metric,
    n=DEFAULT_NUM_RESULTS,
):
    if n < 1:
        raise ValueError("n must be > 0")

    counts = artist_counts(history, metric)

    top = dict(counts.most_common(n))
    remaining = counts.total() - sum(top.values())
    if remaining > 0:
        top["Other"] = remaining

    return top


def normalize_track(track):
    title, artist = track
    return (
        title.strip().casefold(),
        artist.strip().casefold(),
    )


def most_skipped_songs(history, n=DEFAULT_NUM_RESULTS):
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

        normalized_track = normalize_track(track)
        counts[normalized_track] += 1
        display_names.setdefault(normalized_track, track)
        if record.get("skipped"):
            skips[normalized_track] += 1

    ratios = {
        display_names[track]: skips[track] / counts[track]
        for track in counts
        if counts[track] >= MIN_NUM_TRACKS
    }

    return sorted(
        ratios.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:n]
