from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_orbit_3d(states, output_path: Path, texture_path: Path | None = None) -> None:
    xyz_km = np.array([s.r_teme_m for s in states], dtype=float) / 1000.0

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    # orbit
    ax.plot(
        xyz_km[:, 0],
        xyz_km[:, 1],
        xyz_km[:, 2],
        linewidth=2.0,
        label="orbit",
    )
    ax.scatter(*xyz_km[0], s=40, label="start")
    ax.scatter(*xyz_km[-1], s=40, marker="^", label="end")

    # earth sphere
    R = 6378.137
    n_lon = 180
    n_lat = 90

    lon = np.linspace(0.0, 2.0 * np.pi, n_lon)
    colat = np.linspace(0.0, np.pi, n_lat)

    lon_grid, colat_grid = np.meshgrid(lon, colat)

    x = R * np.cos(lon_grid) * np.sin(colat_grid)
    y = R * np.sin(lon_grid) * np.sin(colat_grid)
    z = R * np.cos(colat_grid)

    if texture_path is not None and texture_path.exists():
        img = plt.imread(texture_path)

        if img.dtype != np.float32 and img.dtype != np.float64:
            img = img.astype(np.float32) / 255.0

        img_h, img_w = img.shape[:2]

        # map sphere grid -> image pixel indices
        # lon: 0..2pi  -> x index: 0..img_w-1
        # colat: 0..pi -> y index: 0..img_h-1
        x_idx = ((lon_grid / (2.0 * np.pi)) * (img_w - 1)).astype(int)
        y_idx = ((colat_grid / np.pi) * (img_h - 1)).astype(int)

        facecolors = img[y_idx, x_idx]

        ax.plot_surface(
            x,
            y,
            z,
            facecolors=facecolors,
            rstride=1,
            cstride=1,
            linewidth=0,
            antialiased=False,
            shade=False,
        )
    else:
        ax.plot_surface(
            x,
            y,
            z,
            alpha=0.6,
            linewidth=0,
        )

    max_range = np.max(np.abs(xyz_km)) * 1.2
    ax.set_xlim(-max_range, max_range)
    ax.set_ylim(-max_range, max_range)
    ax.set_zlim(-max_range, max_range)

    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.set_zlabel("Z [km]")
    ax.set_title("3D Orbit with Earth Texture")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)