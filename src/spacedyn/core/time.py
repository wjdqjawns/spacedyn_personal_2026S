from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, List


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_utc_iso8601(text: str) -> datetime:
    dt = datetime.fromisoformat(text)
    return ensure_utc(dt)


def datetime_range(start: datetime, duration_sec: float, step_sec: float) -> List[datetime]:
    if step_sec <= 0:
        raise ValueError("step_sec must be > 0")
    if duration_sec < 0:
        raise ValueError("duration_sec must be >= 0")

    start = ensure_utc(start)
    count = int(duration_sec // step_sec) + 1
    return [start + timedelta(seconds=i * step_sec) for i in range(count)]
