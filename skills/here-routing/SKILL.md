---
name: here-routing
description: |
  Fetch real driving routes, distances, and travel times using HERE Maps Routing API v8.
  Produces clean JSON with coordinates for map display (Leaflet, Mapbox, Google Maps)
  and Markdown distance tables for trip planning.
  Supports geocoding, traffic-aware ETAs, avoidance options, and alternative routes.

  Trigger on: "driving route", "travel time", "road distance", "how far by car",
  "fetch route", "polyline", "HERE API", "avoid tolls", "departure time",
  "route between X and Y", or any request for real road geometry.
metadata:
  {
    "openclaw":
      {
        "emoji": "🛣️",
        "requires": { "bins": ["uv"], "env": ["HERE_API_KEY"] },
        "primaryEnv": "HERE_API_KEY"
      }
  }
---

# HERE Routing API v8

One bundled script does everything: geocode → fetch → decode polyline → simplify → output JSON / Markdown.

```bash
uv run {baseDir}/scripts/route.py --help
```

`uv` reads PEP 723 inline metadata at the top of the script and installs deps (`requests`, `flexpolyline`) into a hermetic per-script venv on first run. 

## When to use

- User needs **real road distance or drive time** between locations (not straight-line)
- User wants **route coordinates** for map display
- User needs to **compare route options** (fastest vs shortest, toll-free, ferry-free)
- User is **planning a multi-stop road trip** and needs segment-by-segment data

## When NOT to use

- Walking or transit directions within a city — use Google Maps or similar
- Distances under 1 km — not worth an API call
- User already has route data and just needs to display it — skip to map rendering
- Flight distances — HERE routes ground transport only

---

## Step 0 — API key

The script reads `HERE_API_KEY` from the environment automatically. Override with `--api-key` if needed.

If unset, ask the user: *"Do you have a HERE API key? Free tier at developer.here.com — 1,000 req/day, no credit card."*

Never hardcode the key into project files.

---

## Step 1 — Geocode (only if user gives place names)

```bash
uv run {baseDir}/scripts/route.py --geocode "Munich, Germany"
# -> 48.1372,11.5755
```

Capture both endpoints, then feed the coords into Step 2.

---

## Step 2 — Fetch a route

### Quick: distance + time only

```bash
uv run {baseDir}/scripts/route.py \
  --origin 48.135,11.582 \
  --destination 47.368,8.539 \
  --summary-only
```

Prints a small JSON object with `km` and `min` — no polyline work, no file written.

### Full route with coordinates (single)

```bash
uv run {baseDir}/scripts/route.py \
  --origin 48.135,11.582 \
  --destination 47.368,8.539 \
  --name "Munich -> Zurich" \
  --id leg1 --day 1 \
  --output route.json
```

### Multi-stop with via points

```bash
uv run {baseDir}/scripts/route.py \
  --origin 47.260,11.394 \
  --via 46.498,11.355 \
  --destination 45.438,10.992 \
  --name "Innsbruck -> Bolzano -> Verona" \
  --output route.json
```

`--via` is repeatable. The `--name` segments (split on `->`) are used to label `from`/`to` in the output `segments` array.

### Batch — multiple routes in one go

Write a JSON file describing each leg:

```json
[
  { "id": "leg1", "day": 1, "name": "Munich -> Innsbruck",
    "points": [[48.135, 11.582], [47.260, 11.394]] },
  { "id": "leg2", "day": 2, "name": "Innsbruck -> Bolzano -> Verona",
    "points": [[47.260, 11.394], [46.498, 11.355], [45.438, 10.992]] },
  { "id": "leg3", "day": 3, "name": "Verona -> Venice",
    "points": [[45.438, 10.992], [45.440, 12.316]] }
]
```

Then:

```bash
uv run {baseDir}/scripts/route.py \
  --batch routes_in.json \
  --output routes.json \
  --markdown routes_table.md
```

Per-route overrides supported in the batch file: `transportMode`, `departureTime`, `avoid`, `alternatives`. The script:

- Fetches sequentially with a 300ms polite delay (free-tier friendly)
- Retries 429 / 5xx up to 2 times with exponential backoff
- Logs and continues on per-leg failure (does not abort the batch)

### Common flags

| Flag | Values | Effect |
|---|---|---|
| `--transport-mode` | `car`, `pedestrian`, `bicycle`, `truck` | Routing profile |
| `--departure-time` | ISO 8601, e.g. `2026-07-15T08:30:00` | Traffic-aware ETA |
| `--alternatives` | `1`–`3` | Request alternative routes (hint, not guaranteed) |
| `--avoid` | `tollRoad`, `ferry`, `motorway`, `dirtRoad`, `tunnel` | Comma-separated |
| `--strategy` | `fastest` *(default)*, `shortest` | Used when alternatives are returned |
| `--tolerance` | float in degrees | Douglas-Peucker simplification (default `0.0008` ≈ 80 m) |
| `--summary-only` | flag | Skip polyline decoding for cheap "how far" answers |

---

## Output format

```json
{
  "id": "leg2",
  "day": 2,
  "name": "Innsbruck -> Bolzano -> Verona",
  "km": 248,
  "min": 185,
  "coords": [[47.260, 11.394], [47.119, 11.387], ...],
  "segments": [
    { "from": "Innsbruck", "to": "Bolzano", "km": 116, "min":  83, "transport": "car" },
    { "from": "Bolzano",   "to": "Verona",  "km": 132, "min": 102, "transport": "car" }
  ]
}
```

Map library usage:
- **Leaflet**: `L.polyline(route.coords).addTo(map)`
- **Mapbox**: swap each coord to `[lng, lat]`
- **Google Maps**: convert to `{ lat, lng }` objects

Style ferry segments differently using the `transport` field (e.g. dashed blue line).

### Markdown distance table

`--markdown out.md` (batch mode) writes:

```
| Route | Distance | Drive time |
|-------|----------|------------|
| Munich → Innsbruck | 187 km | ~1h54 |
| Innsbruck → Bolzano | 116 km | ~1h23 |
| Bolzano → Verona | 132 km | ~1h42 |
| Verona → Venice | 120 km | ~1h18 |
| **TOTAL** | **~555 km** | |
```

### Tolerance guide

| Tolerance | Resolution | Best for |
|-----------|-----------|----------|
| `0.0002°` | ~20 m | Street-level detail, larger files |
| `0.0008°` | ~80 m | Trip overview maps *(default)* |
| `0.002°`  | ~200 m | Thumbnails, minimal payload |

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `No route found` | Cannot route by car (island, ped zone) | Adjust via points or use `--transport-mode pedestrian` |
| `401 Unauthorized` | Bad or missing API key | Verify `$HERE_API_KEY` with `--geocode "Berlin"` |
| `429 Too Many Requests` | Daily limit hit (1,000/day) | Wait until midnight UTC, or use cached response |
| Route too blocky | Tolerance too high | Reduce to `--tolerance 0.0004` or `0.0002` |
| JSON too large | Tolerance too low / too many routes | Increase to `--tolerance 0.002` |
| Unexpected ferry section | HERE auto-inserts ferries on water crossings | Normal — check `transport` field per segment |
