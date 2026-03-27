from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import yaml

from spacedyn.core.time import datetime_range, parse_utc_iso8601
from spacedyn.io.tle_reader import read_tle_catalog
from spacedyn.orbit.constellation import ConstellationPropagator
from spacedyn.visual.constellation_viewer import (
    plot_constellation_3d,
    plot_constellation_groundtrack,
)
from spacedyn.visual.constellation_animation import save_constellation_groundtrack_gif
from spacedyn.visual.voronoi_plotter import plot_subsatellite_voronoi

def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multi-satellite TLE propagation")
    parser.add_argument("--config", type=str, default="config/orbit/tle_case.yaml")
    parser.add_argument("--map-backend", type=str, default="basic", choices=["basic", "cartopy"])
    args = parser.parse_args()

    cfg = load_config((ROOT / args.config).resolve())

    run_name = cfg.get("run_name", "multi_sat_demo")
    tle_file = cfg["tle_file"]
    start_utc = parse_utc_iso8601(cfg["start_utc"])
    duration_sec = float(cfg["duration_sec"])
    step_sec = float(cfg["step_sec"])

    tle_path = (ROOT / tle_file).resolve()
    tle_records = read_tle_catalog(tle_path)

    times = datetime_range(start_utc, duration_sec, step_sec)

    constellation = ConstellationPropagator(tle_records)
    tracks = constellation.propagate_times(times)

    out_dir = ROOT / "experiments" / "runs" / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    texture_path = ROOT / "assets" / "earth" / "world_map.jpg"
    plot_constellation_3d(tracks, out_dir / "constellation_3d.png", texture_path=texture_path)
    plot_constellation_groundtrack(
        tracks,
        out_dir / "constellation_groundtrack.png",
        use_cartopy=(args.map_backend == "cartopy"),
    )

    save_constellation_groundtrack_gif(
        tracks,
        out_dir / "constellation_groundtrack.gif",
        stride=5,
        fps=10,
        proximity_threshold_km=1000.0,
    )

    mid_index = len(tracks[0].states) // 2
    plot_subsatellite_voronoi(
        tracks,
        index=mid_index,
        output_path=out_dir / "constellation_voronoi.png",
    )

    print(f"Run complete: {run_name}")
    print(f"TLE catalog: {tle_path}")
    print(f"Satellites: {len(tle_records)}")
    for tle in tle_records:
        print(f"  - {tle.name}")
    print(f"Samples per satellite: {len(times)}")
    print(f"Output directory: {out_dir}")


if __name__ == "__main__":
    main()