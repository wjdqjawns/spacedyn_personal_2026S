from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np

@dataclass(slots=True)
class OrbitState:
    utc: datetime
    r_teme_m: np.ndarray
    v_teme_mps: np.ndarray
    r_ecef_m: np.ndarray
    lat_deg: float
    lon_deg: float
    alt_m: float
