from __future__ import annotations

import math
import numpy as np


EARTH_RADIUS_M = 6378137.0


def footprint_central_angle_rad(alt_m: float) -> float:
    """
    Geometric horizon half-angle on spherical Earth.
    """
    return math.acos(EARTH_RADIUS_M / (EARTH_RADIUS_M + alt_m))


def destination_point(lat_deg: float, lon_deg: float, bearing_deg: float, angular_distance_rad: float) -> tuple[float, float]:
    lat1 = math.radians(lat_deg)
    lon1 = math.radians(lon_deg)
    brng = math.radians(bearing_deg)
    d = angular_distance_rad

    sin_lat1 = math.sin(lat1)
    cos_lat1 = math.cos(lat1)
    sin_d = math.sin(d)
    cos_d = math.cos(d)

    lat2 = math.asin(sin_lat1 * cos_d + cos_lat1 * sin_d * math.cos(brng))
    lon2 = lon1 + math.atan2(
        math.sin(brng) * sin_d * cos_lat1,
        cos_d - sin_lat1 * math.sin(lat2),
    )

    lat2_deg = math.degrees(lat2)
    lon2_deg = math.degrees(lon2)
    lon2_deg = ((lon2_deg + 180.0) % 360.0) - 180.0
    return lat2_deg, lon2_deg


def compute_footprint_circle(lat_deg: float, lon_deg: float, alt_m: float, n_points: int = 180) -> tuple[np.ndarray, np.ndarray]:
    psi = footprint_central_angle_rad(alt_m)

    lats = []
    lons = []

    for bearing_deg in np.linspace(0.0, 360.0, n_points, endpoint=False):
        lat_i, lon_i = destination_point(lat_deg, lon_deg, float(bearing_deg), psi)
        lats.append(lat_i)
        lons.append(lon_i)

    return np.array(lons, dtype=float), np.array(lats, dtype=float)