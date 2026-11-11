import json
import math
from collections import Counter
from datetime import date

from spotify_utils.config import (
    DATA_DIR,
    DEFAULT_PAGE_SIZE,
    DEFAULT_WINDOW_SIZE,
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


def total_listening(history, metric):
    total = 0
    for record in history:
        artist = record.get("master_metadata_album_artist_name")

        if artist is None:
            continue

        if metric == ListeningMetric.PLAYS:
            total += 1

        elif metric == ListeningMetric.TIME:
            total += record.get("ms_played", 0)

    return total


# measured at the artist level
def diversity_index(history, metric):
    counts = artist_counts(history, metric)
    metric_total = sum(metric_value for metric_value in counts.values())

    entropy = 0
    for metric_value in counts.values():
        prob = metric_value / metric_total
        entropy += -1 * prob * math.log2(prob)

    return entropy / math.log2(metric_total)


# measured at the song level
def obsessiveness_index(history, metric, window_size=DEFAULT_WINDOW_SIZE):
    global_index = 0
    num_records = len(history)
    # diversity per window
    diversities = []

    # iterate through records
    while global_index < num_records:
        # make window
        counter = 0
        window = Counter()
        while counter < window_size and global_index < num_records:
            record = history[global_index]
            track = (
                record.get("master_metadata_track_name"),
                record.get("master_metadata_album_artist_name"),
            )
            if any(part is None for part in track):
                global_index += 1
                continue

            counter += 1
            global_index += 1

            if metric == ListeningMetric.PLAYS:
                window[track] += 1
            elif metric == ListeningMetric.TIME:
                window[track] += record.get("ms_played", 0)

        # compute diversity
        entropy = 0
        metric_total = sum(value for value in window.values())
        for value in window.values():
            prob = value / metric_total
            entropy += -1 * prob * math.log2(prob)

        diversities.append(entropy / math.log2(metric_total))

    # compute obsessiveness
    average_diversity = sum(diversities) / len(diversities)
    return 1 - average_diversity
