from __future__ import annotations

from pathlib import Path

from spacedyn.orbit.tle import TLERecord

class TLEFormatError(ValueError):
    pass

def read_tle_file(path: str | Path) -> TLERecord:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"TLE file not found: {path}")

    raw_lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in raw_lines if line and not line.startswith("#")]

    if len(lines) < 2:
        raise TLEFormatError("TLE file must contain at least line1 and line2")

    if lines[0].startswith("1 ") and lines[1].startswith("2 "):
        name = path.stem
        line1, line2 = lines[0], lines[1]
    elif len(lines) >= 3 and lines[1].startswith("1 ") and lines[2].startswith("2 "):
        name = lines[0]
        line1, line2 = lines[1], lines[2]
    else:
        raise TLEFormatError("Could not detect valid TLE line ordering")

    return TLERecord(name=name, line1=line1, line2=line2)

def read_tle_catalog(path: str | Path) -> list[TLERecord]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"TLE file not found: {path}")

    raw_lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in raw_lines if line and not line.startswith("#")]

    if len(lines) < 3:
        raise TLEFormatError("TLE catalog must contain at least one full TLE (3 lines)")

    records: list[TLERecord] = []

    i = 0
    while i < len(lines):
        # case 1: name + line1 + line2
        if (
            i + 2 < len(lines)
            and not lines[i].startswith("1 ")
            and lines[i + 1].startswith("1 ")
            and lines[i + 2].startswith("2 ")
        ):
            name = lines[i]
            line1 = lines[i + 1]
            line2 = lines[i + 2]
            i += 3

        # case 2: line1 + line2 (no name)
        elif (
            i + 1 < len(lines)
            and lines[i].startswith("1 ")
            and lines[i + 1].startswith("2 ")
        ):
            name = f"SAT_{len(records)}"
            line1 = lines[i]
            line2 = lines[i + 1]
            i += 2

        else:
            raise TLEFormatError(f"Invalid TLE format near line {i}: {lines[i]}")

        records.append(TLERecord(name=name, line1=line1, line2=line2))

    return records