from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class ListeningMetric(StrEnum):
    PLAYS = "plays"
    TIME = "time"


@dataclass
class HistoryOptions:
    start_date: date | None = None
    metrics: set[ListeningMetric] = field(
        default_factory=lambda: {ListeningMetric.PLAYS}
    )
