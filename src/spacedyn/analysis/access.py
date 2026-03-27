from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from spacedyn.env.geodesy import geodetic_to_ecef
from spacedyn.ground.station import GroundStation

@dataclass
class AccessResult:
    visible: bool
    elevation_deg: float
    range_m: float

def ecef_to_enu_matrix(lat_deg: float, lon_deg: float) -> np.ndarray:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)

    s_lat = math.sin(lat)
    c_lat = math.cos(lat)
    s_lon = math.sin(lon)
    c_lon = math.cos(lon)

    return np.array([
        [-s_lon,           c_lon,          0.0],
        [-s_lat * c_lon,  -s_lat * s_lon,  c_lat],
        [ c_lat * c_lon,   c_lat * s_lon,  s_lat],
    ])

def compute_access(gs: GroundStation, sat_r_ecef_m: np.ndarray) -> AccessResult:
    gs_r_ecef_m = geodetic_to_ecef(gs.lat_deg, gs.lon_deg, gs.alt_m)

    rho_ecef_m = sat_r_ecef_m - gs_r_ecef_m
    range_m = float(np.linalg.norm(rho_ecef_m))

    rot = ecef_to_enu_matrix(gs.lat_deg, gs.lon_deg)
    rho_enu_m = rot @ rho_ecef_m

    east, north, up = rho_enu_m
    horiz = math.sqrt(east * east + north * north)
    elevation_deg = math.degrees(math.atan2(up, horiz))

    visible = elevation_deg >= gs.min_elevation_deg
    return AccessResult(
        visible=visible,
        elevation_deg=elevation_deg,
        range_m=range_m,
    )