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
---

# HERE Routing API v8

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

## Decision tree

Pick the right path based on what the user needs:

```
User request
  ├─ "How far is A to B?" or "drive time A → B"
  │   → Quick route: single curl call (Step 2a)
  │
  ├─ "Fetch route for my map" or "generate polyline"
  │   → Full pipeline: fetch + process script (Steps 2b + 3)
  │
  ├─ "Fetch all routes for this trip"
  │   → Batch pipeline: define routes array + batch fetch (Steps 2c + 3)
  │
  └─ User gives place names, not coordinates
      → Geocode first (Step 1), then pick a path above
```

---

## Step 0 — API key

1. Check environment: `echo $HERE_API_KEY` (Unix/macOS) or `echo $env:HERE_API_KEY` (PowerShell)
2. If not set, ask the user: *"Do you have a HERE API key? Free tier at developer.here.com — 1,000 req/day, no credit card."*

Never hardcode the key into project files.

---

## Step 1 — Geocode (only if user gives place names)

Convert place names or addresses to coordinates before routing.

```bash
curl -s "https://geocode.search.hereapi.com/v1/geocode?q=Munich%2C+Germany&apikey=$HERE_API_KEY" \
  | jq '.items[0].position'
```

Returns `{ "lat": 48.1351, "lng": 11.582 }`.

For Node.js:
```js
async function geocode(query, apiKey) {
  const resp = await fetch(`https://geocode.search.hereapi.com/v1/geocode?q=${encodeURIComponent(query)}&apikey=${apiKey}`);
  const data = await resp.json();
  if (!data.items?.length) throw new Error(`No results for: ${query}`);
  const { lat, lng } = data.items[0].position;
  return [lat, lng];
}
```

---

## Step 2 — Fetch the route

### 2a. Quick single route (just distance + time)

```bash
curl -s "https://router.hereapi.com/v8/routes?\
transportMode=car&\
origin=48.135,11.582&\
destination=47.368,8.539&\
return=summary&\
apikey=$HERE_API_KEY" | jq '.routes[0].sections[] | {length: .summary.length, duration: .summary.duration}'
```

Read `length` (meters) and `duration` (seconds) from the response. Done — no processing needed.
Uses `jq` for JSON parsing; if unavailable, pipe to `python -m json.tool` or read the raw JSON.

### 2b. Full route with coordinates

Add `polyline` to `return` to get route geometry:

```bash
curl -s "https://router.hereapi.com/v8/routes?\
transportMode=car&\
origin=48.135,11.582&\
destination=47.368,8.539&\
return=summary,polyline&\
apikey=$HERE_API_KEY" -o route_raw.json
```

Then process with the bundled script (Step 3).

### 2c. Batch — multiple routes

Define routes as an array, then fetch sequentially with retry and delay:

```js
import { writeFileSync } from 'fs';
import { processRoute, toMarkdownTable } from './process-route.mjs';

const API_KEY = process.env.HERE_API_KEY;

const routeDefs = [
  { id: 'leg1', name: 'Munich → Innsbruck',              day: 1, points: [[48.135, 11.582], [47.260, 11.394]] },
  { id: 'leg2', name: 'Innsbruck → Bolzano → Verona',    day: 2, points: [[47.260, 11.394], [46.498, 11.355], [45.438, 10.992]] },
  { id: 'leg3', name: 'Verona → Venice',                  day: 3, points: [[45.438, 10.992], [45.440, 12.316]] },
];

// Build HERE API URL from a route definition
function buildUrl(r) {
  const [o, d] = [r.points[0], r.points.at(-1)];
  const params = new URLSearchParams({
    transportMode: 'car',
    origin: `${o[0]},${o[1]}`, destination: `${d[0]},${d[1]}`,
    return: 'summary,polyline', apikey: API_KEY,
  });
  r.points.slice(1, -1).forEach(([lat, lng]) => params.append('via', `${lat},${lng}`));
  // Optional: params.set('departureTime', '2026-07-15T08:00:00');
  // Optional: params.set('avoid[features]', 'tollRoad');
  return `https://router.hereapi.com/v8/routes?${params}`;
}

// Fetch with retry (handles 429 rate limit and 5xx errors)
async function fetchWithRetry(url, retries = 2) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const resp = await fetch(url);
    if (resp.ok) return resp.json();
    if (attempt < retries && (resp.status === 429 || resp.status >= 500)) {
      console.warn(`  Retry ${attempt + 1}/${retries} (HTTP ${resp.status})`);
      await new Promise(r => setTimeout(r, 500 * (attempt + 1)));
      continue;
    }
    throw new Error(`HERE API ${resp.status}: ${await resp.text()}`);
  }
}

// Fetch all routes sequentially
const results = [];
for (const r of routeDefs) {
  console.log(`Fetching: ${r.name}`);
  try {
    const raw = await fetchWithRetry(buildUrl(r));
    const processed = processRoute(raw, { id: r.id, day: r.day, name: r.name });
    results.push(processed);
    console.log(`  OK: ${processed.km} km, ${processed.min} min`);
  } catch (err) {
    console.error(`  FAIL: ${err.message}`);  // log and continue
  }
  await new Promise(r => setTimeout(r, 300));  // polite delay
}

writeFileSync('routes.json', JSON.stringify(results, null, 2));
console.log('\n' + toMarkdownTable(results));
```

Key points:
- First and last `point` = origin/destination. Middle points = `via` waypoints.
- **300ms delay** between requests to respect the free tier rate limit.
- On failure, **log and continue** — do not abort the whole batch.
- Retry transient errors (429, 5xx) up to 2 times with exponential backoff.

### API parameters reference

| Parameter | Values | Effect |
|-----------|--------|--------|
| `transportMode` | `car`, `pedestrian`, `bicycle`, `truck` | Routing profile |
| `departureTime` | ISO 8601, e.g. `2026-07-15T08:30:00` | Traffic-aware ETA |
| `alternatives` | `1`–`3` | Return alternative routes (hint, not guaranteed) |
| `avoid[features]` | `tollRoad`, `ferry`, `motorway`, `dirtRoad`, `tunnel` | Comma-separated |

Build the URL:
```
https://router.hereapi.com/v8/routes
  ?transportMode=car
  &origin=LAT,LNG
  &destination=LAT,LNG
  &via=LAT,LNG                           ← repeat per waypoint
  &return=summary,polyline
  &departureTime=2026-07-15T08:30:00     ← optional
  &avoid[features]=tollRoad              ← optional
  &alternatives=2                        ← optional
  &apikey=$HERE_API_KEY
```

---

## Step 3 — Process the response

**Prerequisite:** `npm install @here/flexpolyline` (if not already in project)

Use the bundled script to decode, simplify, and format:

```bash
node <skill-dir>/scripts/process-route.mjs \
  route_raw.json route.json \
  --id leg1 --day 1 --name "Munich → Innsbruck"
```

Replace `<skill-dir>` with the actual path to this skill's directory.

Optional flags:
- `--tolerance 0.0004` — finer detail (default `0.0008`, ~80m)
- `--strategy shortest` — pick shortest instead of fastest alternative

The script:
1. Decodes HERE flexpolyline encoding into lat/lng arrays
2. Simplifies with Douglas-Peucker (removes redundant points, preserves shape)
3. Rounds to 3 decimals (~100m precision)
4. Merges multi-section routes into one coordinate array
5. Preserves per-section transport mode (`car`, `ferry`, etc.)
6. Picks the best alternative if multiple were returned

### Output format

```json
{
  "id": "leg2",
  "day": 2,
  "name": "Innsbruck → Bolzano → Verona",
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

Import `toMarkdownTable` from the script (or call it inline) to produce:

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
| `No route found` | Cannot route by car (island, ped zone) | Adjust via points or use `transportMode=ferry` |
| `401 Unauthorized` | Bad or missing API key | Verify `$HERE_API_KEY` with a geocode test call |
| `429 Too Many Requests` | Daily limit hit (1,000/day) | Wait until midnight UTC, or use cached response |
| Route too blocky | Tolerance too high | Reduce to `0.0004` or `0.0002` |
| JSON too large | Tolerance too low / too many routes | Increase to `0.002` |
| Unexpected ferry section | HERE auto-inserts ferries on water crossings | Normal — check `transport` field per segment |
