from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter


def _load_texture(texture_path: Path) -> np.ndarray | None:
    if texture_path is None or not texture_path.exists():
        return None

    img = plt.imread(texture_path)

    if img.dtype != np.float32 and img.dtype != np.float64:
        img = img.astype(np.float32) / 255.0

    if img.shape[-1] == 4:
        img = img[..., :3]

    return img


def _make_earth_surface(radius_km: float, n_lon: int = 180, n_lat: int = 90):
    lon = np.linspace(0.0, 2.0 * np.pi, n_lon)
    colat = np.linspace(0.0, np.pi, n_lat)

    lon_grid, colat_grid = np.meshgrid(lon, colat)

    x = radius_km * np.cos(lon_grid) * np.sin(colat_grid)
    y = radius_km * np.sin(lon_grid) * np.sin(colat_grid)
    z = radius_km * np.cos(colat_grid)

    return x, y, z, lon_grid, colat_grid


def _make_facecolors(img: np.ndarray, lon_grid: np.ndarray, colat_grid: np.ndarray) -> np.ndarray:
    img_h, img_w = img.shape[:2]

    x_idx = ((lon_grid / (2.0 * np.pi)) * (img_w - 1)).astype(int)
    y_idx = ((colat_grid / np.pi) * (img_h - 1)).astype(int)

    return img[y_idx, x_idx]


def save_orbit_3d_gif(
    states,
    output_path: Path,
    texture_path: Path | None = None,
    stride: int = 5,
    fps: int = 10,
) -> None:
    states_anim = states[::stride]
    xyz_km_all = np.array([s.r_teme_m for s in states], dtype=float) / 1000.0

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    radius_km = 6378.137
    x_e, y_e, z_e, lon_grid, colat_grid = _make_earth_surface(radius_km)
    texture = _load_texture(texture_path)

    if texture is not None:
        facecolors = _make_facecolors(texture, lon_grid, colat_grid)
        ax.plot_surface(
            x_e,
            y_e,
            z_e,
            facecolors=facecolors,
            rstride=1,
            cstride=1,
            linewidth=0,
            antialiased=False,
            shade=False,
            alpha=1.0,
        )
    else:
        ax.plot_surface(
            x_e,
            y_e,
            z_e,
            linewidth=0,
            alpha=0.6,
        )

    orbit_line, = ax.plot([], [], [], linewidth=2.0, label="orbit")
    sat_point, = ax.plot([], [], [], marker="o", markersize=6, linestyle="None", label="satellite")
    start_point, = ax.plot([], [], [], marker="o", markersize=6, linestyle="None", label="start")

    max_range = np.max(np.abs(xyz_km_all)) * 1.2
    ax.set_xlim(-max_range, max_range)
    ax.set_ylim(-max_range, max_range)
    ax.set_zlim(-max_range, max_range)
    ax.set_box_aspect((1, 1, 1))

    ax.set_xlabel("X TEME [km]")
    ax.set_ylabel("Y TEME [km]")
    ax.set_zlabel("Z TEME [km]")
    ax.set_title("3D Orbit Animation")
    ax.legend(loc="upper right")

    def update(frame_idx: int):
        curr_xyz = np.array([s.r_teme_m for s in states_anim[: frame_idx + 1]], dtype=float) / 1000.0
        curr = curr_xyz[-1]
        start = curr_xyz[0]

        orbit_line.set_data(curr_xyz[:, 0], curr_xyz[:, 1])
        orbit_line.set_3d_properties(curr_xyz[:, 2])

        sat_point.set_data([curr[0]], [curr[1]])
        sat_point.set_3d_properties([curr[2]])

        start_point.set_data([start[0]], [start[1]])
        start_point.set_3d_properties([start[2]])

        ax.view_init(elev=25, azim=0.3 * frame_idx)
        return orbit_line, sat_point, start_point

    anim = FuncAnimation(fig, update, frames=len(states_anim), interval=100, blit=False)
    writer = PillowWriter(fps=fps)
    anim.save(output_path, writer=writer)
    plt.close(fig)