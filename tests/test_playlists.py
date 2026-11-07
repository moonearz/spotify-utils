import pytest

from spotify_utils.playlists import filter_playlist_by_skip_rate


def make_entry(title, artist):
    return {
        "item": {
            "name": title,
            "artists": [{"name": artist}],
            "type": "track",
            "uri": f"spotify:track:{title}",
        }
    }


@pytest.fixture
def tracks():
    return [
        make_entry("Address Unknown", "The Ink Spots"),
        make_entry("You Broke My Heart", "Drake"),
        make_entry("Top Dog", "Magdalena Bay"),
        make_entry("Unknown Song", "Unknown Artist"),
    ]


@pytest.fixture
def skip_stats():
    return {
        ("address unknown", "the ink spots"): {
            "plays": 20,
            "skip_rate": 0.10,
        },
        ("you broke my heart", "drake"): {
            "plays": 20,
            "skip_rate": 0.80,
        },
        ("top dog", "magdalena bay"): {
            "plays": 2,
            "skip_rate": 0.0,
        },
    }


def test_filter_playlist_by_skip_rate(tracks, skip_stats):
    kept, removed = filter_playlist_by_skip_rate(
        tracks,
        skip_stats,
        threshold=0.30,
        min_plays=5,
    )

    assert [entry["item"]["name"] for entry in kept] == ["Address Unknown"]
    assert len(removed) == 3


def test_filter_playlist_no_minimum_plays(tracks, skip_stats):
    kept, removed = filter_playlist_by_skip_rate(
        tracks,
        skip_stats,
        threshold=0.30,
        min_plays=0,
    )

    assert [entry["item"]["name"] for entry in kept] == [
        "Address Unknown",
        "Top Dog",
    ]
    assert len(removed) == 2


def test_filter_playlist_threshold_boundary(tracks, skip_stats):
    skip_stats[("address unknown", "the ink spots")]["skip_rate"] = 0.30

    kept, removed = filter_playlist_by_skip_rate(
        tracks,
        skip_stats,
        threshold=0.30,
        min_plays=5,
    )

    assert "Address Unknown" not in [entry["item"]["name"] for entry in kept]


def test_filter_playlist_normalization(skip_stats):
    tracks = [make_entry("  ADDRESS UNKNOWN  ", "THE INK SPOTS")]

    kept, removed = filter_playlist_by_skip_rate(
        tracks,
        skip_stats,
        threshold=0.30,
        min_plays=5,
    )

    assert len(kept) == 1
    assert removed == []
