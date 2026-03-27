from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d


def plot_subsatellite_voronoi(tracks, index: int, output_path: Path) -> None:
    points = []
    names = []

    for track in tracks:
        s = track.states[index]
        points.append([s.lon_deg, s.lat_deg])
        names.append(track.name)

    points = np.array(points, dtype=float)

    fig, ax = plt.subplots(figsize=(12, 6))

    if len(points) >= 3:
        vor = Voronoi(points)
        voronoi_plot_2d(
            vor,
            ax=ax,
            show_vertices=False,
            line_colors="gray",
            line_width=1.0,
            line_alpha=0.7,
            point_size=0,
        )

    ax.scatter(points[:, 0], points[:, 1], s=30, color="red")

    for i, name in enumerate(names):
        ax.text(points[i, 0] + 2.0, points[i, 1] + 2.0, name, fontsize=8)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Sub-satellite Voronoi Diagram")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)