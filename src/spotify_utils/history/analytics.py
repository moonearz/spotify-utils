import json
import math
from collections import Counter, defaultdict
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


def filter_valid_plays(history, min_ms_played=10000):
    history = sorted(history, key=lambda record: record["ts"])
    return [
        record
        for record in history
        if record.get("master_metadata_track_name") is not None
        and record.get("master_metadata_album_artist_name") is not None
        and record.get("ms_played", 0) >= min_ms_played
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


def entropy(counts):
    total = sum(counts.values())

    if total == 0.0:
        return 0.0

    entropy = 0.0
    for value in counts.values():
        if value <= 0:
            continue

        prob = value / total
        entropy += -1 * prob * math.log2(prob)

    return entropy


# measured at the artist level
def diversity_index(history, metric):
    counts = artist_counts(history, metric)
    num_plays = total_listening(history, metric=ListeningMetric.PLAYS)

    if num_plays <= 1:
        return 0.0

    return entropy(counts) / math.log2(num_plays)


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

            if metric == ListeningMetric.PLAYS:
                window[track] += 1
            elif metric == ListeningMetric.TIME:
                ms_played = record.get("ms_played", 0)
                if ms_played <= 0:
                    global_index += 1
                    continue
                window[track] += ms_played

            counter += 1
            global_index += 1

        # compute diversity
        entrop = entropy(window)
        if counter == window_size:
            diversities.append(entrop / math.log2(counter))

    # compute obsessiveness
    if not diversities:
        return 0.0

    average_diversity = sum(diversities) / len(diversities)
    return 1 - average_diversity


def discovery_rate(history):
    seen_songs = set()
    seen_artists = set()

    monthly_stats = defaultdict(
        lambda: {
            "total_plays": 0,
            "new_songs": 0,
            "new_artists": 0,
        }
    )

    history = filter_valid_plays(history)

    for record in history:
        artist = record.get("master_metadata_album_artist_name")
        song = record.get("master_metadata_track_name")

        if artist is None or song is None:
            continue

        month = record["ts"][:7]
        stats = monthly_stats[month]

        stats["total_plays"] += 1
        track = normalize_track((song, artist))

        if track not in seen_songs:
            stats["new_songs"] += 1
            seen_songs.add(track)

        if artist not in seen_artists:
            stats["new_artists"] += 1
            seen_artists.add(artist)

    return [
        {
            "month": month,
            "total_plays": stats["total_plays"],
            "new_songs": stats["new_songs"],
            "new_artists": stats["new_artists"],
            "song_rate": stats["new_songs"] / stats["total_plays"],
            "artist_rate": stats["new_artists"] / stats["total_plays"],
        }
        for month, stats in sorted(monthly_stats.items())
    ]
