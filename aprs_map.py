#!/usr/bin/env python3
"""
basic demo of reading APRS packets and plotting on a map.

Python >= 3.9

example supposing you have APRS packets from aprs.fi in aprs_raw.txt,
and wish to plot over continential USA:

    python aprs_map.py aprs_raw.txt -b 20 50 -130 -65 -t 25
"""

import argparse
from pathlib import Path

import numpy as np
from matplotlib.pyplot import figure, show
import cartopy
import cartopy.feature as cpf

from aprspy import APRS
import aprspy.exceptions


def read(
    file: Path, bounds: tuple[float, float, float, float], trim: int = 0
) -> list[tuple[float, float]]:
    file = Path(file).expanduser()

    latb = bounds[:2]
    lonb = bounds[2:]

    latlon = []
    with file.open("r") as f:
        for line in f:
            if not line:
                continue
            try:
                packet = APRS.parse(line[trim:])
            except aprspy.exceptions.ParseError:
                # print(line)
                continue
            except aprspy.exceptions.UnsupportedError:
                continue

            if not hasattr(packet, "latitude"):
                continue
            if packet.latitude > latb[1] or packet.latitude < latb[0]:
                continue
            if packet.longitude > lonb[1] or packet.longitude < lonb[0]:
                continue

            latlon.append((packet.latitude, packet.longitude))

    return latlon


def map_plot(latlon: list[tuple[float, float]]):

    ll = np.array(latlon)

    proj = cartopy.crs.PlateCarree()

    ax = figure().gca(projection=proj)
    ax.add_feature(cpf.LAND)
    ax.add_feature(cpf.OCEAN)
    ax.add_feature(cpf.COASTLINE)
    ax.add_feature(cpf.BORDERS, linestyle=":")
    ax.add_feature(cpf.LAKES, alpha=0.5)

    state_prov = cpf.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="110m",
        edgecolor="gray",
        facecolor="none",
    )
    ax.add_feature(state_prov)

    ax.scatter(ll[:, 1], ll[:, 0], transform=proj)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="APRS map plotter")
    p.add_argument("file", help="APRS raw package file")
    p.add_argument(
        "-b",
        "--latlon_bounds",
        help="latitude bounds [min,max]",
        nargs=4,
        default=[-90, 90, -180, 180],
        type=float,
    )
    p.add_argument("-t", "--trim", help="discard first N characters per line", type=int, default=0)
    P = p.parse_args()

    latlon = read(P.file, P.latlon_bounds, P.trim)

    map_plot(latlon)

    show()
