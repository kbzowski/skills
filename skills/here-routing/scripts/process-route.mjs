/**
 * HERE route processor: decode flexpolyline, simplify, output clean JSON.
 *
 * Usage:
 *   node process-route.mjs <input.json> <output.json> [--id day01] [--day 1] [--name "A → B"] [--tolerance 0.0008] [--strategy fastest]
 *
 * Input:  raw HERE Routing API v8 response (JSON)
 * Output: processed route JSON with simplified coords and segment metadata
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { decode } from '@here/flexpolyline';

// --- Douglas-Peucker line simplification ---

function perpendicularDist(point, lineStart, lineEnd) {
  const [px, py] = point;
  const [ax, ay] = lineStart;
  const [bx, by] = lineEnd;
  const dx = bx - ax, dy = by - ay;
  const mag = Math.sqrt(dx * dx + dy * dy);
  if (mag === 0) return Math.hypot(px - ax, py - ay);
  return Math.abs((py - ay) * dx - (px - ax) * dy) / mag;
}

function simplify(points, tolerance = 0.0008) {
  if (points.length <= 2) return points;
  let maxDist = 0, maxIdx = 0;
  for (let i = 1; i < points.length - 1; i++) {
    const d = perpendicularDist(points[i], points[0], points[points.length - 1]);
    if (d > maxDist) { maxDist = d; maxIdx = i; }
  }
  if (maxDist > tolerance) {
    return [
      ...simplify(points.slice(0, maxIdx + 1), tolerance).slice(0, -1),
      ...simplify(points.slice(maxIdx), tolerance),
    ];
  }
  return [points[0], points[points.length - 1]];
}

// --- Route selection ---

function pickRoute(apiResponse, strategy = 'fastest') {
  const routes = apiResponse.routes;
  if (!routes?.length) throw new Error('No routes in API response');
  if (routes.length === 1) return routes[0];
  const key = strategy === 'shortest' ? 'length' : 'duration';
  return routes.reduce((best, r) => {
    const total = r.sections.reduce((s, sec) => s + sec.summary[key], 0);
    const bestTotal = best.sections.reduce((s, sec) => s + sec.summary[key], 0);
    return total < bestTotal ? r : best;
  });
}

// --- Processing ---

export function processRoute(apiResponse, { id, day = null, name, tolerance = 0.0008, strategy = 'fastest' }) {
  const route = pickRoute(apiResponse, strategy);
  const sections = route.sections;
  const waypoints = name.split(' → ');

  const sectionCoords = sections.map(s => {
    const raw = decode(s.polyline).polyline.map(p => [p[0], p[1]]);
    const simplified = simplify(raw, tolerance);
    return simplified.map(([lat, lng]) => [
      Math.round(lat * 1000) / 1000,
      Math.round(lng * 1000) / 1000,
    ]);
  });

  const coords = sectionCoords.reduce((acc, seg, i) =>
    i === 0 ? seg : [...acc, ...seg.slice(1)], []);

  const totalKm = Math.round(sections.reduce((s, sec) => s + sec.summary.length, 0) / 1000);
  const totalMin = Math.round(sections.reduce((s, sec) => s + sec.summary.duration, 0) / 60);

  const segments = sections.map((s, i) => ({
    from:      waypoints[i]     ?? `Point ${i}`,
    to:        waypoints[i + 1] ?? `Point ${i + 1}`,
    km:        Math.round(s.summary.length / 1000),
    min:       Math.round(s.summary.duration / 60),
    transport: s.transport?.mode ?? 'car',
  }));

  return { id, day, name, km: totalKm, min: totalMin, coords, segments };
}

// --- Formatting ---

export function formatDuration(min) {
  const h = Math.floor(min / 60), m = min % 60;
  return h === 0 ? `${m} min` : `${h}h${m > 0 ? String(m).padStart(2, '0') : ''}`;
}

export function toMarkdownTable(routes) {
  const rows = routes.flatMap(r =>
    r.segments.length > 1
      ? r.segments.map(s => `| ${s.from} → ${s.to} | ${s.km} km | ~${formatDuration(s.min)} |`)
      : [`| ${r.name} | ${r.km} km | ~${formatDuration(r.min)} |`]
  );
  const total = routes.reduce((s, r) => s + r.km, 0);
  return [
    '| Route | Distance | Drive time |',
    '|-------|----------|------------|',
    ...rows,
    `| **TOTAL** | **~${total} km** | |`,
  ].join('\n');
}

// --- CLI (only runs when executed directly, not when imported) ---

function parseArgs(args) {
  const opts = { tolerance: 0.0008, strategy: 'fastest' };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--id')        opts.id = args[++i];
    if (args[i] === '--day')       opts.day = parseInt(args[++i], 10);
    if (args[i] === '--name')      opts.name = args[++i];
    if (args[i] === '--tolerance') opts.tolerance = parseFloat(args[++i]);
    if (args[i] === '--strategy')  opts.strategy = args[++i];
  }
  return opts;
}

const isDirectRun = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];

if (isDirectRun) {
  const [,, inputFile, outputFile, ...rest] = process.argv;

  if (!inputFile || !outputFile) {
    console.error('Usage: node process-route.mjs <input.json> <output.json> [--id X] [--day N] [--name "A → B"]');
    process.exit(1);
  }

  const opts = parseArgs(rest);
  const raw = JSON.parse(readFileSync(inputFile, 'utf-8'));
  const result = processRoute(raw, {
    id:        opts.id ?? 'route',
    day:       opts.day ?? null,
    name:      opts.name ?? 'Route',
    tolerance: opts.tolerance,
    strategy:  opts.strategy,
  });

  writeFileSync(outputFile, JSON.stringify(result, null, 2));
  console.log(`${result.id}: ${result.coords.length} pts, ${result.km} km, ${formatDuration(result.min)}`);
  result.segments.forEach(s => {
    console.log(`  ${s.from} → ${s.to}: ${s.km} km, ${formatDuration(s.min)} [${s.transport}]`);
  });
}
