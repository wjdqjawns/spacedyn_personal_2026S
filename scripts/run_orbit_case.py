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
from spacedyn.ground.station import GroundStation
from spacedyn.io.result_writer import write_orbit_csv
from spacedyn.io.tle_reader import read_tle_file
from spacedyn.orbit.sgp4_propagator import SGP4Propagator
from spacedyn.sim.scenario import OrbitScenario
from spacedyn.visual.animation import save_groundtrack_gif
from spacedyn.visual.groundtrack_plotter import plot_ground_track_cartopy, plot_ground_track_basic
from spacedyn.visual.orbit_viewer import plot_orbit_3d
from spacedyn.visual.orbit_animation import save_orbit_3d_gif
from spacedyn.analysis.access import compute_access
from spacedyn.analysis.coverage import compute_footprint_circle
from spacedyn.analysis.passes import extract_passes_for_network

def load_scenario(config_path: Path) -> OrbitScenario:
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    return OrbitScenario(
        run_name=cfg["run_name"],
        tle_file=cfg["tle_file"],
        start_utc=parse_utc_iso8601(cfg["start_utc"]),
        duration_sec=float(cfg["duration_sec"]),
        step_sec=float(cfg["step_sec"]),
        save_csv=bool(cfg.get("save_csv", True)),
        save_plots=bool(cfg.get("save_plots", True)),
    )


def build_ground_stations() -> list[GroundStation]:
    return [
        GroundStation(
            name="Seoul",
            lat_deg=37.5665,
            lon_deg=126.9780,
            alt_m=50.0,
            min_elevation_deg=10.0,
        ),
        GroundStation(
            name="Daejeon",
            lat_deg=36.3504,
            lon_deg=127.3845,
            alt_m=70.0,
            min_elevation_deg=10.0,
        ),
    ]

def save_pass_report(pass_events, output_path: Path) -> None:
    import csv

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ground_station",
            "aos_utc",
            "los_utc",
            "duration_sec",
            "max_elevation_deg",
            "tca_utc",
        ])

        for p in pass_events:
            writer.writerow([
                p.ground_station,
                p.aos_utc.isoformat(),
                p.los_utc.isoformat(),
                f"{p.duration_sec:.1f}",
                f"{p.max_elevation_deg:.2f}",
                p.tca_utc.isoformat(),
            ])

def save_access_report(states, ground_stations: list[GroundStation], output_path: Path) -> None:
    import csv

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["utc", "ground_station", "visible", "elevation_deg", "range_km"])

        for s in states:
            for gs in ground_stations:
                access = compute_access(gs, s.r_ecef_m)
                writer.writerow([
                    s.utc.isoformat(),
                    gs.name,
                    int(access.visible),
                    f"{access.elevation_deg:.3f}",
                    f"{access.range_m / 1000.0:.3f}",
                ])

def main() -> None:
    parser = argparse.ArgumentParser(description="Run TLE + SGP4 orbit propagation case")
    parser.add_argument("--config", type=str, default="config/orbit/tle_case.yaml")
    parser.add_argument("--map-backend", type=str, default="basic", choices=["basic", "cartopy"])
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    scenario = load_scenario(config_path)
    tle_path = (ROOT / scenario.tle_file).resolve()

    tle = read_tle_file(tle_path)
    propagator = SGP4Propagator(tle)

    times = datetime_range(scenario.start_utc, scenario.duration_sec, scenario.step_sec)
    states = [propagator.propagate(t) for t in times]    
    ground_stations = build_ground_stations()
    pass_events = extract_passes_for_network(states, ground_stations)

    out_dir = ROOT / "experiments" / "runs" / scenario.run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    if scenario.save_csv:
        write_orbit_csv(out_dir / "orbit_log.csv", states)
        save_access_report(states, ground_stations, out_dir / "access_report.csv")
        save_pass_report(pass_events, out_dir / "pass_report.csv")

    if scenario.save_plots:
        texture_path = ROOT / "assets" / "earth" / "world_map.jpg"
        plot_orbit_3d(states, out_dir / "orbit_3d.png", texture_path=texture_path)

        save_orbit_3d_gif(
            states,
            out_dir / "orbit_3d.gif",
            texture_path=texture_path,
            stride=5,
            fps=10,
        )
        
        if args.map_backend == "cartopy":
            plot_ground_track_cartopy(states, out_dir / "ground_track.png")
        else:
            plot_ground_track_basic(states, out_dir / "ground_track.png")

        save_groundtrack_gif(
            states,
            out_dir / "ground_track.gif",
            ground_stations=ground_stations,
            stride=5,
            fps=10,
        )

    print(f"Run complete: {scenario.run_name}")
    print(f"TLE: {tle.name}")
    print(f"Samples: {len(states)}")
    print(f"Output directory: {out_dir}")
    print()

    if pass_events:
        print("Detected passes:")
        for p in pass_events:
            print(
                f"[{p.ground_station}] "
                f"AOS={p.aos_utc.isoformat()}  "
                f"LOS={p.los_utc.isoformat()}  "
                f"Dur={p.duration_sec:.1f}s  "
                f"MaxEl={p.max_elevation_deg:.1f}deg  "
                f"TCA={p.tca_utc.isoformat()}"
            )
    else:
        print("No visible passes found.")

if __name__ == "__main__":
    main()