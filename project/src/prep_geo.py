"""Turn the DataMeet India boundary into a compact, render-ready outline.

Source: https://github.com/datameet/maps  Country/india-composite.geojson
        (c) DataMeet India community, CC BY 4.0

This file is used rather than the more common Natural Earth country layer
because Natural Earth draws Jammu & Kashmir on de-facto control lines.  The
DataMeet composite follows India's official boundary, which is the correct
depiction for this subject.

Run once; the result is committed as assets/geo/india_outline.json so a rebuild
needs no network.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "assets", "geo", "india_outline.json")

# Douglas-Peucker tolerance in degrees.  ~0.02 keeps the coastline and the
# northern boundary honest while cutting 250k points down to a few thousand.
TOL_MAIN = 0.018
TOL_ISLE = 0.030
MIN_AREA = 0.010  # drop specks too small to read at 1080px wide


def main(src: str) -> None:
    from shapely.geometry import shape
    from shapely.ops import unary_union

    geom = unary_union([shape(f["geometry"]) for f in json.load(open(src))["features"]])
    polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    polys.sort(key=lambda p: p.area, reverse=True)

    rings = []
    for i, p in enumerate(polys):
        if p.area < MIN_AREA:
            continue
        s = p.simplify(TOL_MAIN if i == 0 else TOL_ISLE, preserve_topology=True)
        if s.is_empty:
            continue
        rings.append([[round(x, 4), round(y, 4)] for x, y in s.exterior.coords])

    lons = [c[0] for r in rings for c in r]
    lats = [c[1] for r in rings for c in r]
    data = dict(
        source="DataMeet India community - india-composite.geojson (CC BY 4.0)",
        source_url="https://github.com/datameet/maps/blob/master/Country/india-composite.geojson",
        note="Official boundary depiction. Simplified for rendering; not for navigation.",
        bounds=dict(lon=[min(lons), max(lons)], lat=[min(lats), max(lats)]),
        rings=rings,
    )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f)
    pts = sum(len(r) for r in rings)
    print(f"{len(rings)} rings, {pts} points -> {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")
    print("bounds", data["bounds"])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/dm_india-composite.geojson")
