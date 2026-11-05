from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from spotify_utils.config import DEFAULT_NUM_RESULTS


class ListeningMetric(StrEnum):
    PLAYS = "plays"
    TIME = "time"


@dataclass
class HistoryOptions:
    start_date: date | None = None
    metrics: set[ListeningMetric] = field(
        default_factory=lambda: {ListeningMetric.TIME}
    )
    num_results: int = DEFAULT_NUM_RESULTS
