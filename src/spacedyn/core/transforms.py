from __future__ import annotations

from datetime import datetime, timezone
import math
import numpy as np
from sgp4.api import jday


def datetime_to_jd_fr(dt: datetime) -> tuple[float, float]:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    jd, fr = jday(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second + dt.microsecond * 1e-6,
    )
    return jd, fr


def gmst_rad(dt: datetime) -> float:
    """
    Approximate Greenwich Mean Sidereal Time in radians.
    Good enough for orbit visualization / basic ground track.
    """
    jd, fr = datetime_to_jd_fr(dt)
    jd_total = jd + fr
    t_ut1 = (jd_total - 2451545.0) / 36525.0

    gmst_deg = (
        280.46061837
        + 360.98564736629 * (jd_total - 2451545.0)
        + 0.000387933 * t_ut1**2
        - (t_ut1**3) / 38710000.0
    )

    gmst_deg = gmst_deg % 360.0
    return math.radians(gmst_deg)


def rot_z(theta_rad: float) -> np.ndarray:
    c = math.cos(theta_rad)
    s = math.sin(theta_rad)
    return np.array([
        [ c, s, 0.0],
        [-s, c, 0.0],
        [0.0, 0.0, 1.0],
    ])


def teme_to_ecef(r_teme_m: np.ndarray, dt: datetime) -> np.ndarray:
    """
    Simple TEME -> ECEF approximation using GMST-only z-rotation.
    This is fine for MVP visualization, but later you may want a more rigorous conversion.
    """
    theta = gmst_rad(dt)
    r_ecef_m = rot_z(theta) @ r_teme_m
    return r_ecef_m