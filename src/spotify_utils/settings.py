from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from spotify_utils.config import DEFAULT_PAGE_SIZE


class ListeningMetric(StrEnum):
    PLAYS = "plays"
    TIME = "time"


@dataclass
class UtilOptions:
    start_date: date | None = None
    end_date: date | None = None
    page_size: int = DEFAULT_PAGE_SIZE
    metrics: set[ListeningMetric] = field(
        default_factory=lambda: {ListeningMetric.TIME}
    )
