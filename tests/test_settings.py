from datetime import date

from spotify_utils.config import DEFAULT_PAGE_SIZE
from spotify_utils.settings import ListeningMetric, UtilOptions


def test_default_settings():
    options = UtilOptions()

    assert options.start_date is None
    assert options.end_date is None
    assert options.page_size == DEFAULT_PAGE_SIZE
    assert options.metrics == {ListeningMetric.TIME}


def test_settings_can_be_updated():
    options = UtilOptions()

    options.start_date = date(2025, 1, 1)
    options.end_date = date(2025, 12, 31)
    options.page_size = 20
    options.metrics = {ListeningMetric.PLAYS}

    assert options.start_date == date(2025, 1, 1)
    assert options.end_date == date(2025, 12, 31)
    assert options.page_size == 20
    assert options.metrics == {ListeningMetric.PLAYS}


def test_multiple_metrics():
    options = UtilOptions()

    options.metrics = {
        ListeningMetric.PLAYS,
        ListeningMetric.TIME,
    }

    assert len(options.metrics) == 2
    assert ListeningMetric.PLAYS in options.metrics
    assert ListeningMetric.TIME in options.metrics


def test_settings_independent_instances():
    first = UtilOptions()
    second = UtilOptions()

    first.metrics.add(ListeningMetric.PLAYS)
    first.start_date = date(2025, 1, 1)
    first.page_size = 25

    assert second.metrics == {ListeningMetric.TIME}
    assert second.start_date is None
    assert second.page_size == DEFAULT_PAGE_SIZE


def test_date_range_can_be_set():
    options = UtilOptions(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
    )

    assert options.start_date <= options.end_date


def test_open_ended_date_ranges():
    start_only = UtilOptions(start_date=date(2025, 1, 1))
    end_only = UtilOptions(end_date=date(2025, 12, 31))

    assert start_only.end_date is None
    assert end_only.start_date is None
