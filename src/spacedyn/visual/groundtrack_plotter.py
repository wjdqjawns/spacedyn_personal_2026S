from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _break_dateline(lon_deg: np.ndarray, lat_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lon_plot = lon_deg.astype(float).copy()
    lat_plot = lat_deg.astype(float).copy()

    dlon = np.abs(np.diff(lon_plot))
    jump_idx = np.where(dlon > 180.0)[0]

    for idx in jump_idx:
        lon_plot[idx + 1] = np.nan
        lat_plot[idx + 1] = np.nan

    return lon_plot, lat_plot


def plot_ground_track_basic(states, output_path: Path) -> None:
    lon = np.array([s.lon_deg for s in states], dtype=float)
    lat = np.array([s.lat_deg for s in states], dtype=float)

    lon_plot, lat_plot = _break_dateline(lon, lat)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(lon_plot, lat_plot, linewidth=1.2)
    ax.scatter(lon[0], lat[0], marker="o", s=30, label="start")
    ax.scatter(lon[-1], lat[-1], marker="^", s=30, label="end")

    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Ground track")
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_ground_track_cartopy(states, output_path: Path) -> None:
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
    except ImportError as exc:
        raise RuntimeError(
            "Cartopy is not installed. Run: pip install cartopy"
        ) from exc

    lon = np.array([s.lon_deg for s in states], dtype=float)
    lat = np.array([s.lat_deg for s in states], dtype=float)
    lon_plot, lat_plot = _break_dateline(lon, lat)

    fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_global()
    ax.coastlines(linewidth=0.7)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)
    ax.add_feature(cfeature.LAND, alpha=0.2)
    ax.add_feature(cfeature.OCEAN, alpha=0.15)

    gl = ax.gridlines(draw_labels=True, linewidth=0.4, alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False

    ax.plot(
        lon_plot,
        lat_plot,
        transform=ccrs.PlateCarree(),
        linewidth=1.3,
        label="ground track",
    )
    ax.scatter(
        lon[0],
        lat[0],
        transform=ccrs.PlateCarree(),
        marker="o",
        s=30,
        label="start",
    )
    ax.scatter(
        lon[-1],
        lat[-1],
        transform=ccrs.PlateCarree(),
        marker="^",
        s=30,
        label="end",
    )

    ax.set_title("Ground track (Cartopy)")
    ax.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)