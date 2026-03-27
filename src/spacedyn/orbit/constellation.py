from __future__ import annotations

from dataclasses import dataclass

from spacedyn.orbit.sgp4_propagator import SGP4Propagator
from spacedyn.orbit.tle import TLERecord


@dataclass
class SatelliteTrack:
    name: str
    states: list


class ConstellationPropagator:
    def __init__(self, tle_records: list[TLERecord]) -> None:
        self.tle_records = tle_records
        self.propagators = [SGP4Propagator(tle) for tle in tle_records]

    def propagate_times(self, times) -> list[SatelliteTrack]:
        tracks: list[SatelliteTrack] = []

        for tle, propagator in zip(self.tle_records, self.propagators):
            states = [propagator.propagate(t) for t in times]
            tracks.append(SatelliteTrack(name=tle.name, states=states))

        return tracks