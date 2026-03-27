from __future__ import annotations

import numpy as np
import math

# WGS-84
A_WGS84_M = 6378137.0
F_WGS84 = 1.0 / 298.257223563
B_WGS84_M = A_WGS84_M * (1.0 - F_WGS84)
E2 = 1.0 - (B_WGS84_M ** 2) / (A_WGS84_M ** 2)
EP2 = (A_WGS84_M ** 2) / (B_WGS84_M ** 2) - 1.0


def wrap_longitude_deg(lon_deg: float) -> float:
    lon = (lon_deg + 180.0) % 360.0 - 180.0
    return lon


def ecef_to_geodetic(r_ecef_m: np.ndarray) -> tuple[float, float, float]:
    x, y, z = r_ecef_m.astype(float)
    p = np.hypot(x, y)

    if p < 1e-9:
        lat = np.pi / 2.0 if z >= 0.0 else -np.pi / 2.0
        lon = 0.0
        alt = abs(z) - B_WGS84_M
        return np.degrees(lat), np.degrees(lon), alt

    lon = np.arctan2(y, x)
    theta = np.arctan2(z * A_WGS84_M, p * B_WGS84_M)
    st = np.sin(theta)
    ct = np.cos(theta)

    lat = np.arctan2(z + EP2 * B_WGS84_M * st**3, p - E2 * A_WGS84_M * ct**3)
    sin_lat = np.sin(lat)
    N = A_WGS84_M / np.sqrt(1.0 - E2 * sin_lat**2)
    alt = p / np.cos(lat) - N

    return float(np.degrees(lat)), float(wrap_longitude_deg(np.degrees(lon))), float(alt)

def geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> np.ndarray:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)

    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    sin_lon = math.sin(lon)
    cos_lon = math.cos(lon)

    N = A_WGS84_M / math.sqrt(1.0 - E2 * sin_lat * sin_lat)

    x = (N + alt_m) * cos_lat * cos_lon
    y = (N + alt_m) * cos_lat * sin_lon
    z = (N * (1.0 - E2) + alt_m) * sin_lat
    return np.array([x, y, z], dtype=float)