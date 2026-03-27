from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from spacedyn.analysis.access import compute_access
from spacedyn.analysis.coverage import compute_footprint_circle
from spacedyn.ground.station import GroundStation


def _break_dateline(lon_deg: np.ndarray, lat_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lon_plot = lon_deg.astype(float).copy()
    lat_plot = lat_deg.astype(float).copy()

    dlon = np.abs(np.diff(lon_plot))
    jump_idx = np.where(dlon > 180.0)[0]
    for idx in jump_idx:
        lon_plot[idx + 1] = np.nan
        lat_plot[idx + 1] = np.nan

    return lon_plot, lat_plot


def save_groundtrack_gif(states, output_path: Path, ground_stations: list[GroundStation], stride: int = 5, fps: int = 10) -> None:
    states_anim = states[::stride]
    lon_all = np.array([s.lon_deg for s in states], dtype=float)
    lat_all = np.array([s.lat_deg for s in states], dtype=float)
    lon_all_plot, lat_all_plot = _break_dateline(lon_all, lat_all)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Ground track animation")
    ax.grid(True, alpha=0.3)

    ax.plot(lon_all_plot, lat_all_plot, linewidth=1.0, alpha=0.35, label="full track")

    for gs in ground_stations:
        ax.scatter(gs.lon_deg, gs.lat_deg, marker="^", s=50, label=gs.name)

    sat_point, = ax.plot([], [], marker="o", markersize=7, linestyle="None")
    track_line, = ax.plot([], [], linewidth=1.5)
    footprint_line, = ax.plot([], [], linewidth=1.0, alpha=0.8)

    status_text = ax.text(
        0.02, 0.02, "", transform=ax.transAxes, ha="left", va="bottom"
    )

    ax.legend(loc="upper right")

    def update(frame_idx: int):
        current_states = states_anim[: frame_idx + 1]
        curr = current_states[-1]

        lon_hist = np.array([s.lon_deg for s in current_states], dtype=float)
        lat_hist = np.array([s.lat_deg for s in current_states], dtype=float)
        lon_hist_plot, lat_hist_plot = _break_dateline(lon_hist, lat_hist)

        sat_point.set_data([curr.lon_deg], [curr.lat_deg])
        track_line.set_data(lon_hist_plot, lat_hist_plot)

        visible_names = []
        for gs in ground_stations:
            access = compute_access(gs, curr.r_ecef_m)
            if access.visible:
                visible_names.append(f"{gs.name} ({access.elevation_deg:.1f} deg)")

        sat_point.set_color("red" if visible_names else "blue")
        track_line.set_color("red" if visible_names else "tab:blue")

        fp_lon, fp_lat = compute_footprint_circle(curr.lat_deg, curr.lon_deg, curr.alt_m, n_points=180)
        fp_lon_plot, fp_lat_plot = _break_dateline(fp_lon, fp_lat)
        footprint_line.set_data(fp_lon_plot, fp_lat_plot)
        footprint_line.set_color("green")

        visible_str = ", ".join(visible_names) if visible_names else "None"
        status_mode = "IN CONTACT" if visible_names else "NO CONTACT"

        status_text.set_text(
            f"UTC: {curr.utc.isoformat()}\n"
            f"Lat/Lon: {curr.lat_deg:.2f}, {curr.lon_deg:.2f}\n"
            f"Alt: {curr.alt_m / 1000.0:.1f} km\n"
            f"Status: {status_mode}\n"
            f"Visible GS: {visible_str}"
        )

        return sat_point, track_line, footprint_line, status_text

    anim = FuncAnimation(fig, update, frames=len(states_anim), interval=100, blit=False)
    writer = PillowWriter(fps=fps)
    anim.save(output_path, writer=writer)
    plt.close(fig)