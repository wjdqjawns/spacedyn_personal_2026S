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


def plot_constellation_3d(tracks, output_path: Path, texture_path: Path | None = None) -> None:
    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111, projection="3d")

    # Earth
    R = 6378.137
    lon = np.linspace(0.0, 2.0 * np.pi, 180)
    colat = np.linspace(0.0, np.pi, 90)
    lon_grid, colat_grid = np.meshgrid(lon, colat)

    x = R * np.cos(lon_grid) * np.sin(colat_grid)
    y = R * np.sin(lon_grid) * np.sin(colat_grid)
    z = R * np.cos(colat_grid)

    if texture_path is not None and texture_path.exists():
        img = plt.imread(texture_path)
        if img.dtype != np.float32 and img.dtype != np.float64:
            img = img.astype(np.float32) / 255.0
        if img.shape[-1] == 4:
            img = img[..., :3]

        img_h, img_w = img.shape[:2]
        x_idx = ((lon_grid / (2.0 * np.pi)) * (img_w - 1)).astype(int)
        y_idx = ((colat_grid / np.pi) * (img_h - 1)).astype(int)
        facecolors = img[y_idx, x_idx]

        ax.plot_surface(
            x, y, z,
            facecolors=facecolors,
            rstride=1,
            cstride=1,
            linewidth=0,
            antialiased=False,
            shade=False,
            alpha=1.0,
        )
    else:
        ax.plot_surface(x, y, z, linewidth=0, alpha=0.25)

    max_abs = R

    for track in tracks:
        xyz_km = np.array([s.r_teme_m for s in track.states], dtype=float) / 1000.0
        ax.plot(xyz_km[:, 0], xyz_km[:, 1], xyz_km[:, 2], linewidth=1.2, label=track.name)
        ax.scatter(xyz_km[0, 0], xyz_km[0, 1], xyz_km[0, 2], s=18)
        max_abs = max(max_abs, float(np.max(np.abs(xyz_km))))

    lim = max_abs * 1.15
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1))

    ax.set_xlabel("X TEME [km]")
    ax.set_ylabel("Y TEME [km]")
    ax.set_zlabel("Z TEME [km]")
    ax.set_title("Multi-satellite 3D Orbit")
    ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_constellation_groundtrack(tracks, output_path: Path, use_cartopy: bool = False) -> None:
    if use_cartopy:
        try:
            import cartopy.crs as ccrs
            import cartopy.feature as cfeature
        except ImportError as exc:
            raise RuntimeError("Cartopy is not installed. Run: pip install cartopy") from exc

        fig = plt.figure(figsize=(14, 7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_global()
        ax.coastlines(linewidth=0.7)
        ax.add_feature(cfeature.BORDERS, linewidth=0.4)

        gl = ax.gridlines(draw_labels=True, linewidth=0.4, alpha=0.5)
        gl.top_labels = False
        gl.right_labels = False

        for track in tracks:
            lon = np.array([s.lon_deg for s in track.states], dtype=float)
            lat = np.array([s.lat_deg for s in track.states], dtype=float)
            lon_plot, lat_plot = _break_dateline(lon, lat)

            ax.plot(
                lon_plot,
                lat_plot,
                transform=ccrs.PlateCarree(),
                linewidth=1.2,
                label=track.name,
            )
            ax.scatter(lon[0], lat[0], transform=ccrs.PlateCarree(), s=15)

        ax.set_title("Multi-satellite Ground Track")
        ax.legend(loc="upper right", fontsize=8)
        plt.tight_layout()
        plt.savefig(output_path, dpi=180)
        plt.close(fig)
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    for track in tracks:
        lon = np.array([s.lon_deg for s in track.states], dtype=float)
        lat = np.array([s.lat_deg for s in track.states], dtype=float)
        lon_plot, lat_plot = _break_dateline(lon, lat)

        ax.plot(lon_plot, lat_plot, linewidth=1.2, label=track.name)
        ax.scatter(lon[0], lat[0], s=15)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Multi-satellite Ground Track")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)