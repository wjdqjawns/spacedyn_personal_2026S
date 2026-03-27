from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from spacedyn.analysis.access import compute_access
from spacedyn.ground.station import GroundStation


@dataclass
class PassEvent:
    ground_station: str
    aos_utc: datetime
    los_utc: datetime
    duration_sec: float
    max_elevation_deg: float
    tca_utc: datetime


def extract_passes(states, ground_station: GroundStation) -> list[PassEvent]:
    passes: list[PassEvent] = []

    in_pass = False
    aos_idx = None
    max_el = -1.0e9
    tca_idx = None

    for i, s in enumerate(states):
        access = compute_access(ground_station, s.r_ecef_m)
        visible = access.visible
        el = access.elevation_deg

        if visible and not in_pass:
            in_pass = True
            aos_idx = i
            max_el = el
            tca_idx = i

        elif visible and in_pass:
            if el > max_el:
                max_el = el
                tca_idx = i

        elif (not visible) and in_pass:
            los_idx = i

            aos_state = states[aos_idx]
            los_state = states[los_idx]
            tca_state = states[tca_idx]

            duration_sec = (los_state.utc - aos_state.utc).total_seconds()

            passes.append(
                PassEvent(
                    ground_station=ground_station.name,
                    aos_utc=aos_state.utc,
                    los_utc=los_state.utc,
                    duration_sec=duration_sec,
                    max_elevation_deg=max_el,
                    tca_utc=tca_state.utc,
                )
            )

            in_pass = False
            aos_idx = None
            max_el = -1.0e9
            tca_idx = None

    if in_pass and aos_idx is not None and tca_idx is not None:
        aos_state = states[aos_idx]
        los_state = states[-1]
        tca_state = states[tca_idx]

        duration_sec = (los_state.utc - aos_state.utc).total_seconds()

        passes.append(
            PassEvent(
                ground_station=ground_station.name,
                aos_utc=aos_state.utc,
                los_utc=los_state.utc,
                duration_sec=duration_sec,
                max_elevation_deg=max_el,
                tca_utc=tca_state.utc,
            )
        )

    return passes


def extract_passes_for_network(states, ground_stations: Iterable[GroundStation]) -> list[PassEvent]:
    all_passes: list[PassEvent] = []

    for gs in ground_stations:
        all_passes.extend(extract_passes(states, gs))

    all_passes.sort(key=lambda p: p.aos_utc)
    return all_passes