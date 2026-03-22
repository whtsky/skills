#!/usr/bin/env python3
"""
Parse GPX file and extract key waypoints for weather analysis.
Outputs JSON with sampled points including lat, lon, elevation.

Usage:
    python3 parse_gpx.py <gpx_file> [--sample-interval-m 200] [--max-points 10]

If GPX lacks elevation data, outputs points without elevation
(caller should use Open-Meteo Elevation API to fill in).
"""

import argparse
import json
import math
import sys
import xml.etree.ElementTree as ET

GPX_NS = {"gpx": "http://www.topografix.com/GPX/1/1"}


def haversine(lat1, lon1, lat2, lon2):
    """Distance in meters between two GPS coordinates."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_gpx(filepath):
    """Parse GPX file, return list of (lat, lon, ele_or_None)."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    points = []

    # Try GPX 1.1 namespace first, then no namespace
    for ns_prefix in [GPX_NS, {"gpx": ""}]:
        for tag in ["gpx:trkpt", "gpx:rtept", "gpx:wpt"]:
            for pt in root.findall(f".//{tag}", ns_prefix):
                lat = float(pt.get("lat"))
                lon = float(pt.get("lon"))
                ele_el = pt.find("gpx:ele", ns_prefix)
                ele = float(ele_el.text) if ele_el is not None else None
                points.append({"lat": lat, "lon": lon, "ele": ele})
        if points:
            break

    # Fallback: no namespace
    if not points:
        for tag in ["trkpt", "rtept", "wpt"]:
            for pt in root.iter(tag):
                lat = float(pt.get("lat"))
                lon = float(pt.get("lon"))
                ele_el = pt.find("ele")
                ele = float(ele_el.text) if ele_el is not None else None
                points.append({"lat": lat, "lon": lon, "ele": ele})

    return points


def sample_by_elevation(points, interval_m=200, max_points=10):
    """
    Sample key points along the route based on elevation changes.
    Always includes: start, end, highest point, lowest point.
    Then samples at elevation intervals.
    """
    if not points:
        return []

    has_elevation = points[0]["ele"] is not None

    if not has_elevation:
        # Without elevation, sample evenly by distance
        return sample_by_distance(points, max_points)

    # Find key points
    start = points[0]
    end = points[-1]
    highest = max(points, key=lambda p: p["ele"])
    lowest = min(points, key=lambda p: p["ele"])

    # Sample at elevation intervals
    sampled = [start]
    last_ele = start["ele"]

    for p in points[1:-1]:
        if abs(p["ele"] - last_ele) >= interval_m:
            sampled.append(p)
            last_ele = p["ele"]

    sampled.append(end)

    # Ensure highest and lowest are included
    for special in [highest, lowest]:
        if not any(
            abs(s["lat"] - special["lat"]) < 0.0001 and abs(s["lon"] - special["lon"]) < 0.0001
            for s in sampled
        ):
            sampled.append(special)

    # Sort by track order (approximate by finding closest original index)
    def track_index(sp):
        for i, p in enumerate(points):
            if abs(p["lat"] - sp["lat"]) < 0.0001 and abs(p["lon"] - sp["lon"]) < 0.0001:
                return i
        return 0

    sampled.sort(key=track_index)

    # Trim to max_points
    if len(sampled) > max_points:
        # Always keep start, end, highest
        must_keep = {0, len(sampled) - 1}
        for i, s in enumerate(sampled):
            if s is highest:
                must_keep.add(i)
        # Evenly sample the rest
        remaining = max_points - len(must_keep)
        other_indices = [i for i in range(len(sampled)) if i not in must_keep]
        step = max(1, len(other_indices) // remaining)
        keep = must_keep | set(other_indices[::step][:remaining])
        sampled = [s for i, s in enumerate(sampled) if i in keep]

    # Add cumulative distance
    cum_dist = 0
    result = []
    for i, s in enumerate(sampled):
        if i > 0:
            prev = sampled[i - 1]
            cum_dist += haversine(prev["lat"], prev["lon"], s["lat"], s["lon"])
        result.append({**s, "distance_km": round(cum_dist / 1000, 1)})

    return result


def sample_by_distance(points, max_points=10):
    """Evenly sample points by track distance when no elevation available."""
    if len(points) <= max_points:
        return points

    # Calculate total distance
    distances = [0]
    for i in range(1, len(points)):
        d = haversine(points[i - 1]["lat"], points[i - 1]["lon"], points[i]["lat"], points[i]["lon"])
        distances.append(distances[-1] + d)

    total = distances[-1]
    interval = total / (max_points - 1)

    sampled = [points[0]]
    next_target = interval
    for i in range(1, len(points)):
        if distances[i] >= next_target:
            sampled.append(points[i])
            next_target += interval
    if len(sampled) < max_points:
        sampled.append(points[-1])

    # Add cumulative distance
    result = []
    for i, s in enumerate(sampled):
        result.append({**s, "distance_km": round(distances[points.index(s) if s in points else 0] / 1000, 1)})

    return result


def main():
    parser = argparse.ArgumentParser(description="Parse GPX and extract key waypoints")
    parser.add_argument("gpx_file", help="Path to GPX file")
    parser.add_argument("--sample-interval-m", type=int, default=200, help="Elevation change interval for sampling (meters)")
    parser.add_argument("--max-points", type=int, default=10, help="Maximum number of waypoints to output")
    args = parser.parse_args()

    points = parse_gpx(args.gpx_file)
    if not points:
        print(json.dumps({"error": "No track points found in GPX file"}))
        sys.exit(1)

    has_elevation = points[0]["ele"] is not None
    sampled = sample_by_elevation(points, args.sample_interval_m, args.max_points)

    output = {
        "total_points": len(points),
        "has_elevation": has_elevation,
        "needs_elevation_lookup": not has_elevation,
        "sampled_waypoints": sampled,
        "route_summary": {
            "start": {"lat": points[0]["lat"], "lon": points[0]["lon"]},
            "end": {"lat": points[-1]["lat"], "lon": points[-1]["lon"]},
        },
    }

    if has_elevation:
        elevations = [p["ele"] for p in points if p["ele"] is not None]
        output["route_summary"]["min_elevation_m"] = min(elevations)
        output["route_summary"]["max_elevation_m"] = max(elevations)
        output["route_summary"]["elevation_gain_m"] = sum(
            max(0, points[i]["ele"] - points[i - 1]["ele"]) for i in range(1, len(points)) if points[i]["ele"] is not None and points[i - 1]["ele"] is not None
        )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
