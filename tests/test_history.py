from datetime import date

from spotify_utils.history.analytics import filter_history

HISTORY = [
    {"ts": "2025-01-01T12:00:00Z"},
    {"ts": "2025-06-15T12:00:00Z"},
    {"ts": "2025-12-31T12:00:00Z"},
    {"ts": "2026-01-01T12:00:00Z"},
]


def test_filter_history_no_dates():
    assert filter_history(HISTORY) == HISTORY


def test_filter_history_start_date():
    result = filter_history(HISTORY, start_date=date(2025, 6, 15))

    assert len(result) == 3
    assert result[0]["ts"] == "2025-06-15T12:00:00Z"


def test_filter_history_end_date():
    result = filter_history(HISTORY, end_date=date(2025, 6, 15))

    assert len(result) == 2
    assert result[-1]["ts"] == "2025-06-15T12:00:00Z"


def test_filter_history_date_range():
    result = filter_history(
        HISTORY,
        start_date=date(2025, 6, 15),
        end_date=date(2025, 12, 31),
    )

    assert len(result) == 2


def test_filter_history_empty_range():
    result = filter_history(
        HISTORY,
        start_date=date(2027, 1, 1),
    )

    assert result == []
