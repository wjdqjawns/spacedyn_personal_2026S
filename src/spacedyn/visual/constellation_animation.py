from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from spacedyn.analysis.proximity import find_close_pairs_at_index, find_closest_pair_at_index


def _break_dateline(lon_deg: np.ndarray, lat_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lon_plot = lon_deg.astype(float).copy()
    lat_plot = lat_deg.astype(float).copy()

    dlon = np.abs(np.diff(lon_plot))
    jump_idx = np.where(dlon > 180.0)[0]

    for idx in jump_idx:
        lon_plot[idx + 1] = np.nan
        lat_plot[idx + 1] = np.nan

    return lon_plot, lat_plot


def save_constellation_groundtrack_gif(
    tracks,
    output_path: Path,
    stride: int = 5,
    fps: int = 10,
    proximity_threshold_km: float = 300.0,
) -> None:
    n_frames = len(tracks[0].states[::stride])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Constellation Ground Track Animation")
    ax.grid(True, alpha=0.3)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    track_lines = []
    sat_points = []

    for i, track in enumerate(tracks):
        lon_all = np.array([s.lon_deg for s in track.states], dtype=float)
        lat_all = np.array([s.lat_deg for s in track.states], dtype=float)
        lon_plot, lat_plot = _break_dateline(lon_all, lat_all)

        ax.plot(lon_plot, lat_plot, linewidth=0.8, alpha=0.2, color=colors[i % len(colors)])
        line, = ax.plot([], [], linewidth=1.5, color=colors[i % len(colors)], label=track.name)
        point, = ax.plot([], [], marker="o", markersize=6, linestyle="None", color=colors[i % len(colors)])
        track_lines.append(line)
        sat_points.append(point)

    proximity_lines = []
    status_text = ax.text(0.02, 0.02, "", transform=ax.transAxes, ha="left", va="bottom")

    ax.legend(loc="upper right", fontsize=8)

    def update(frame_idx: int):
        nonlocal proximity_lines

        for line in proximity_lines:
            line.remove()
        proximity_lines = []

        idx = frame_idx * stride

        for i, track in enumerate(tracks):
            hist_states = track.states[: idx + 1]
            lon_hist = np.array([s.lon_deg for s in hist_states], dtype=float)
            lat_hist = np.array([s.lat_deg for s in hist_states], dtype=float)
            lon_hist_plot, lat_hist_plot = _break_dateline(lon_hist, lat_hist)

            curr = track.states[idx]

            track_lines[i].set_data(lon_hist_plot, lat_hist_plot)
            sat_points[i].set_data([curr.lon_deg], [curr.lat_deg])

        close_pairs = find_close_pairs_at_index(tracks, idx, proximity_threshold_km)
        closest = find_closest_pair_at_index(tracks, idx)

        highlighted = set()

        for event in close_pairs:
            track_a = next(t for t in tracks if t.name == event.sat_a)
            track_b = next(t for t in tracks if t.name == event.sat_b)

            sa = track_a.states[idx]
            sb = track_b.states[idx]

            line, = ax.plot(
                [sa.lon_deg, sb.lon_deg],
                [sa.lat_deg, sb.lat_deg],
                linewidth=2.0,
                color="red",
                alpha=0.9,
            )
            proximity_lines.append(line)
            highlighted.add(event.sat_a)
            highlighted.add(event.sat_b)

        for i, track in enumerate(tracks):
            if track.name in highlighted:
                sat_points[i].set_color("red")
                sat_points[i].set_markersize(8)
            else:
                sat_points[i].set_markersize(6)

        utc_now = tracks[0].states[idx].utc.isoformat()
        closest_str = (
            f"{closest.sat_a} - {closest.sat_b}: {closest.distance_km:.1f} km"
            if closest is not None else "N/A"
        )

        status_text.set_text(
            f"UTC: {utc_now}\n"
            f"Closest pair: {closest_str}\n"
            f"Pairs < {proximity_threshold_km:.1f} km: {len(close_pairs)}"
        )

        return track_lines + sat_points + proximity_lines + [status_text]

    anim = FuncAnimation(fig, update, frames=n_frames, interval=100, blit=False)
    anim.save(output_path, writer=PillowWriter(fps=fps))
    plt.close(fig)