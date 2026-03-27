from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class OrbitScenario:
    run_name: str
    tle_file: str
    start_utc: datetime
    duration_sec: float
    step_sec: float
    save_csv: bool = True
    save_plots: bool = True
