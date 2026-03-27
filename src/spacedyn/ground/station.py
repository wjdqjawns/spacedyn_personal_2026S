from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GroundStation:
    name: str
    lat_deg: float
    lon_deg: float
    alt_m: float = 0.0
    min_elevation_deg: float = 10.0