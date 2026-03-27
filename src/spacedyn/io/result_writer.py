from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from spacedyn.orbit.orbit_state import OrbitState


FIELDNAMES = [
    "utc",
    "x_teme_m",
    "y_teme_m",
    "z_teme_m",
    "vx_teme_mps",
    "vy_teme_mps",
    "vz_teme_mps",
    "x_ecef_m",
    "y_ecef_m",
    "z_ecef_m",
    "vx_ecef_mps",
    "vy_ecef_mps",
    "vz_ecef_mps",
    "lat_deg",
    "lon_deg",
    "alt_m",
]


def write_orbit_csv(path: str | Path, states: Iterable[OrbitState]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for s in states:
            writer.writerow(
                {
                    "utc": s.utc.isoformat(),
                    "x_teme_m": s.r_teme_m[0],
                    "y_teme_m": s.r_teme_m[1],
                    "z_teme_m": s.r_teme_m[2],
                    # "vx_teme_mps": s.v_teme_mps[0],
                    # "vy_teme_mps": s.v_teme_mps[1],
                    # "vz_teme_mps": s.v_teme_mps[2],
                    "x_ecef_m": s.r_ecef_m[0],
                    "y_ecef_m": s.r_ecef_m[1],
                    "z_ecef_m": s.r_ecef_m[2],
                    # "vx_ecef_mps": s.v_ecef_mps[0],
                    # "vy_ecef_mps": s.v_ecef_mps[1],
                    # "vz_ecef_mps": s.v_ecef_mps[2],
                    "lat_deg": s.lat_deg,
                    "lon_deg": s.lon_deg,
                    "alt_m": s.alt_m,
                }
            )
