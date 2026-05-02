#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31",
#   "flexpolyline>=0.1.0",
# ]
# ///
"""
HERE Routing API v8 — fetch + process in one step.

Single route:
    uv run route.py --origin 48.135,11.582 --destination 47.368,8.539 \\
        --name "Munich -> Zurich" --output route.json

With via points:
    uv run route.py --origin 47.260,11.394 --via 46.498,11.355 \\
        --destination 45.438,10.992 --name "Innsbruck -> Bolzano -> Verona" \\
        --output route.json

Batch (input file = JSON array of {id, name, day?, points: [[lat,lng],...]}):
    uv run route.py --batch routes_in.json --output routes.json [--markdown table.md]

Geocode helper:
    uv run route.py --geocode "Munich, Germany"

API key: --api-key, or env var HERE_API_KEY.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus, urlencode

import requests
from flexpolyline import decode

# Windows consoles default to cp1252 and choke on non-ASCII (e.g. "→") in print().
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try: _s.reconfigure(encoding="utf-8")
        except Exception: pass

GEOCODE_URL = "https://geocode.search.hereapi.com/v1/geocode"
ROUTING_URL = "https://router.hereapi.com/v8/routes"


# ---------- geometry ----------

def _perp_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    mag = (dx * dx + dy * dy) ** 0.5
    if mag == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    return abs((py - ay) * dx - (px - ax) * dy) / mag


def simplify(points, tolerance=0.0008):
    """Douglas-Peucker line simplification."""
    if len(points) <= 2:
        return points
    max_dist, max_idx = 0.0, 0
    for i in range(1, len(points) - 1):
        d = _perp_dist(points[i], points[0], points[-1])
        if d > max_dist:
            max_dist, max_idx = d, i
    if max_dist > tolerance:
        left = simplify(points[: max_idx + 1], tolerance)
        right = simplify(points[max_idx:], tolerance)
        return left[:-1] + right
    return [points[0], points[-1]]


# ---------- HERE API ----------

def fetch(url, retries=2):
    for attempt in range(retries + 1):
        resp = requests.get(url, timeout=60)
        if resp.ok:
            return resp.json()
        transient = resp.status_code == 429 or resp.status_code >= 500
        if attempt < retries and transient:
            print(f"  Retry {attempt + 1}/{retries} (HTTP {resp.status_code})", file=sys.stderr)
            time.sleep(0.5 * (attempt + 1))
            continue
        raise RuntimeError(f"HERE API {resp.status_code}: {resp.text}")


def build_url(points, *, api_key, mode="car", departure=None, avoid=None,
              alternatives=None, fields="summary,polyline"):
    if len(points) < 2:
        raise ValueError("Need at least origin and destination")
    o, d = points[0], points[-1]
    params = [
        ("transportMode", mode),
        ("origin", f"{o[0]},{o[1]}"),
        ("destination", f"{d[0]},{d[1]}"),
        ("return", fields),
        ("apikey", api_key),
    ]
    params += [("via", f"{lat},{lng}") for lat, lng in points[1:-1]]
    if departure:    params.append(("departureTime", departure))
    if avoid:        params.append(("avoid[features]", avoid))
    if alternatives: params.append(("alternatives", str(alternatives)))
    return f"{ROUTING_URL}?{urlencode(params)}"


def geocode(query, api_key):
    url = f"{GEOCODE_URL}?q={quote_plus(query)}&apikey={api_key}"
    items = (requests.get(url, timeout=30).json() or {}).get("items") or []
    if not items:
        raise RuntimeError(f"No geocode results for: {query}")
    pos = items[0]["position"]
    return pos["lat"], pos["lng"]


# ---------- processing ----------

def _pick_route(routes, strategy):
    if not routes:
        raise ValueError("No routes in API response")
    if len(routes) == 1:
        return routes[0]
    key = "length" if strategy == "shortest" else "duration"
    return min(routes, key=lambda r: sum(s["summary"][key] for s in r["sections"]))


def process(api_response, *, id, name, day=None, tolerance=0.0008, strategy="fastest"):
    sections = _pick_route(api_response.get("routes") or [], strategy)["sections"]
    waypoints = [w.strip() for w in name.replace("→", "->").split("->")]

    coords: list[list[float]] = []
    for i, s in enumerate(sections):
        raw = [(p[0], p[1]) for p in decode(s["polyline"])]
        thinned = [[round(lat, 3), round(lng, 3)] for lat, lng in simplify(raw, tolerance)]
        coords.extend(thinned if i == 0 else thinned[1:])  # drop joint duplicate

    segments = [
        {
            "from": waypoints[i] if i < len(waypoints) else f"Point {i}",
            "to":   waypoints[i + 1] if i + 1 < len(waypoints) else f"Point {i + 1}",
            "km":   round(s["summary"]["length"] / 1000),
            "min":  round(s["summary"]["duration"] / 60),
            "transport": (s.get("transport") or {}).get("mode", "car"),
        }
        for i, s in enumerate(sections)
    ]

    return {
        "id": id, "day": day, "name": name,
        "km": sum(seg["km"] for seg in segments),
        "min": sum(seg["min"] for seg in segments),
        "coords": coords,
        "segments": segments,
    }


def summarize(api_response, *, id, name, day=None):
    sections = api_response["routes"][0]["sections"]
    return {
        "id": id, "day": day, "name": name,
        "km": round(sum(s["summary"]["length"] for s in sections) / 1000),
        "min": round(sum(s["summary"]["duration"] for s in sections) / 60),
    }


# ---------- formatting ----------

def fmt_duration(minutes):
    h, m = divmod(minutes, 60)
    if h == 0:
        return f"{m} min"
    return f"{h}h{str(m).zfill(2) if m else ''}"


def to_markdown(routes):
    rows = []
    for r in routes:
        segs = r.get("segments")
        if segs:
            rows += [f"| {s['from']} → {s['to']} | {s['km']} km | ~{fmt_duration(s['min'])} |" for s in segs]
        else:
            name = r["name"].replace("->", "→")
            rows.append(f"| {name} | {r['km']} km | ~{fmt_duration(r['min'])} |")
    total = sum(r["km"] for r in routes)
    return "\n".join([
        "| Route | Distance | Drive time |",
        "|-------|----------|------------|",
        *rows,
        f"| **TOTAL** | **~{total} km** | |",
    ])


# ---------- CLI ----------

def parse_point(s):
    try:
        lat, lng = s.split(",")
        return float(lat), float(lng)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"expected LAT,LNG, got: {s!r}") from e


def load_specs(args):
    """Normalize CLI args into a list of {id, name, day, points, ...overrides}."""
    if args.batch:
        return json.loads(Path(args.batch).read_text(encoding="utf-8"))
    if not (args.origin and args.destination):
        raise SystemExit("error: --origin and --destination are required (or use --batch / --geocode)")
    return [{
        "id": args.id, "name": args.name, "day": args.day,
        "points": [args.origin, *args.via, args.destination],
    }]


def run_one(spec, args, api_key):
    points = [tuple(p) for p in spec["points"]]
    fields = "summary" if args.summary_only else "summary,polyline"
    url = build_url(
        points, api_key=api_key,
        mode=spec.get("transportMode", args.transport_mode),
        departure=spec.get("departureTime", args.departure_time),
        avoid=spec.get("avoid", args.avoid),
        alternatives=spec.get("alternatives", args.alternatives),
        fields=fields,
    )
    raw = fetch(url)
    common = dict(id=spec.get("id", "route"), name=spec["name"], day=spec.get("day"))
    if args.summary_only:
        return summarize(raw, **common)
    return process(raw, **common, tolerance=args.tolerance, strategy=args.strategy)


def main():
    p = argparse.ArgumentParser(description="HERE Routing v8 — fetch + process")
    p.add_argument("--api-key", help="HERE API key (overrides $HERE_API_KEY)")
    p.add_argument("--output", "-o", help="Output JSON file")
    p.add_argument("--markdown", help="Also write a Markdown distance table")
    p.add_argument("--geocode", help="Geocode a place name and exit")
    p.add_argument("--batch", help="Path to JSON array of route definitions")
    p.add_argument("--origin", type=parse_point, help="LAT,LNG")
    p.add_argument("--destination", type=parse_point, help="LAT,LNG")
    p.add_argument("--via", type=parse_point, action="append", default=[], help="LAT,LNG (repeatable)")
    p.add_argument("--id", default="route")
    p.add_argument("--day", type=int)
    p.add_argument("--name", default="Route")
    p.add_argument("--transport-mode", default="car",
                   choices=["car", "pedestrian", "bicycle", "truck"])
    p.add_argument("--departure-time", help="ISO 8601, e.g. 2026-07-15T08:30:00")
    p.add_argument("--avoid", help="Comma-separated: tollRoad,ferry,motorway,dirtRoad,tunnel")
    p.add_argument("--alternatives", type=int)
    p.add_argument("--tolerance", type=float, default=0.0008,
                   help="Douglas-Peucker tolerance in degrees (default 0.0008 ≈ 80 m)")
    p.add_argument("--strategy", default="fastest", choices=["fastest", "shortest"])
    p.add_argument("--summary-only", action="store_true",
                   help="Skip polyline; return km/min only")
    args = p.parse_args()

    api_key = args.api_key or os.environ.get("HERE_API_KEY")
    if not api_key:
        sys.exit("Error: no API key. Set HERE_API_KEY or pass --api-key.")

    if args.geocode:
        lat, lng = geocode(args.geocode, api_key)
        print(f"{lat},{lng}")
        return

    specs = load_specs(args)
    results: list[dict] = []
    for i, spec in enumerate(specs):
        print(f"Fetching: {spec['name']}", file=sys.stderr)
        try:
            r = run_one(spec, args, api_key)
        except Exception as e:
            print(f"  FAIL: {e}", file=sys.stderr)
            continue
        results.append(r)
        print(f"  OK: {r['km']} km, {r['min']} min", file=sys.stderr)
        if i + 1 < len(specs):
            time.sleep(0.3)  # polite delay for free tier

    payload = results if args.batch else (results[0] if results else None)
    out_json = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(out_json, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(out_json)

    if args.markdown:
        Path(args.markdown).write_text(to_markdown(results), encoding="utf-8")
        print(f"Wrote {args.markdown}")


if __name__ == "__main__":
    main()
