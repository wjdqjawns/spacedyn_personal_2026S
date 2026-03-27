from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np


@dataclass
class CloseApproach:
    sat_a: str
    sat_b: str
    distance_km: float


def pair_distance_km(state_a, state_b) -> float:
    return float(np.linalg.norm(state_a.r_teme_m - state_b.r_teme_m) / 1000.0)


def find_close_pairs_at_index(tracks, index: int, threshold_km: float) -> list[CloseApproach]:
    events: list[CloseApproach] = []

    for track_a, track_b in combinations(tracks, 2):
        state_a = track_a.states[index]
        state_b = track_b.states[index]
        d_km = pair_distance_km(state_a, state_b)

        if d_km <= threshold_km:
            events.append(
                CloseApproach(
                    sat_a=track_a.name,
                    sat_b=track_b.name,
                    distance_km=d_km,
                )
            )

    return events


def find_closest_pair_at_index(tracks, index: int) -> CloseApproach | None:
    best = None

    for track_a, track_b in combinations(tracks, 2):
        state_a = track_a.states[index]
        state_b = track_b.states[index]
        d_km = pair_distance_km(state_a, state_b)

        event = CloseApproach(
            sat_a=track_a.name,
            sat_b=track_b.name,
            distance_km=d_km,
        )

        if best is None or event.distance_km < best.distance_km:
            best = event

    return best