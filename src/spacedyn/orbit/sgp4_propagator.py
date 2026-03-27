from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
from sgp4.api import Satrec

from spacedyn.core.transforms import datetime_to_jd_fr, teme_to_ecef
from spacedyn.env.geodesy import ecef_to_geodetic
from spacedyn.orbit.orbit_state import OrbitState
from spacedyn.orbit.tle import TLERecord


class SGP4Propagator:
    def __init__(self, tle: TLERecord) -> None:
        self.tle = tle
        self.sat = Satrec.twoline2rv(tle.line1, tle.line2)

    def propagate(self, utc: datetime) -> OrbitState:
        if utc.tzinfo is None:
            utc = utc.replace(tzinfo=timezone.utc)
        else:
            utc = utc.astimezone(timezone.utc)

        jd, fr = datetime_to_jd_fr(utc)
        error_code, r_km, v_kmps = self.sat.sgp4(jd, fr)

        if error_code != 0:
            raise RuntimeError(f"SGP4 propagation failed with code {error_code}")

        r_teme_m = np.array(r_km, dtype=float) * 1000.0
        v_teme_mps = np.array(v_kmps, dtype=float) * 1000.0

        r_ecef_m = teme_to_ecef(r_teme_m, utc)

        lat_deg, lon_deg, alt_m = ecef_to_geodetic(r_ecef_m)

        return OrbitState(
            utc=utc,
            r_teme_m=r_teme_m,
            v_teme_mps=v_teme_mps,
            r_ecef_m=r_ecef_m,
            lat_deg=lat_deg,
            lon_deg=lon_deg,
            alt_m=alt_m,
        )