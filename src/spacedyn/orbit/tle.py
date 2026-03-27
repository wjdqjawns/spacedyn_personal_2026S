from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TLERecord:
    name: str
    line1: str
    line2: str
