/**
 * NestJS Circular Dependency Analyzer using nestjs-spelunker
 *
 * This script bootstraps the NestJS application context (without listening),
 * uses nestjs-spelunker to explore the real runtime DI graph, detects
 * circular dependency cycles, and outputs results as JSON and/or Mermaid.
 *
 * Usage:
 *   <pmx> ts-node scripts/spelunker-analyze.ts [--json] [--mermaid] [--debug]
 *
 * Prerequisites:
 *   npm install nestjs-spelunker --save-dev
 *
 * The script must be run from the project root. It imports AppModule from
 * src/app.module (configurable via APP_MODULE_PATH env var).
 */

import { NestFactory } from '@nestjs/core';
import { SpelunkerModule } from 'nestjs-spelunker';
import * as path from 'path';

// ── Configuration ──────────────────────────────────────────────────────

const APP_MODULE_PATH = process.env.APP_MODULE_PATH || './src/app.module';
const outputJson = process.argv.includes('--json');
const outputMermaid = process.argv.includes('--mermaid');
const debugMode = process.argv.includes('--debug');

// ── Types ──────────────────────────────────────────────────────────────

interface ModuleNode {
  name: string;
  imports: string[];
  providers: string[];
  controllers: string[];
  exports: string[];
}

interface Cycle {
  modules: string[];
  length: number;
  chain: string;
}

interface AnalysisResult {
  summary: {
    totalModules: number;
    totalCycles: number;
    modulesInCycles: string[];
  };
  modules: ModuleNode[];
  adjacency: Record<string, string[]>;
  cycles: Cycle[];
  mermaid?: string;
  debug?: any[];
}

// ── Cycle Detection (DFS with back-edge tracking) ──────────────────────

function detectCycles(adjacency: Record<string, string[]>): Cycle[] {
  const cycles: Cycle[] = [];
  const visited = new Set<string>();
  const recStack: string[] = [];
  const recSet = new Set<string>();

  function dfs(node: string): void {
    visited.add(node);
    recStack.push(node);
    recSet.add(node);

    for (const neighbor of adjacency[node] || []) {
      if (!visited.has(neighbor)) {
        dfs(neighbor);
      } else if (recSet.has(neighbor)) {
        const cycleStart = recStack.indexOf(neighbor);
        const cycleModules = recStack.slice(cycleStart);
        cycles.push({
          modules: [...cycleModules],
          length: cycleModules.length,
          chain: [...cycleModules, neighbor].join(' → '),
        });
      }
    }

    recStack.pop();
    recSet.delete(node);
  }

  for (const node of Object.keys(adjacency)) {
    if (!visited.has(node)) {
      dfs(node);
    }
  }

  // Deduplicate — normalize by rotating smallest element to front
  const unique = new Map<string, Cycle>();
  for (const cycle of cycles) {
    const minIdx = cycle.modules.indexOf(
      cycle.modules.reduce((a, b) => (a < b ? a : b)),
    );
    const normalized = [
      ...cycle.modules.slice(minIdx),
      ...cycle.modules.slice(0, minIdx),
    ];
    const key = normalized.join('|');
    if (!unique.has(key)) {
      unique.set(key, {
        modules: normalized,
        length: normalized.length,
        chain: [...normalized, normalized[0]].join(' → '),
      });
    }
  }

  return Array.from(unique.values());
}

// ── Mermaid Generation ─────────────────────────────────────────────────

function generateMermaid(
  adjacency: Record<string, string[]>,
  cycles: Cycle[],
): string {
  const lines: string[] = ['graph LR'];

  // Collect cycle edges
  const cycleEdges = new Set<string>();
  for (const cycle of cycles) {
    for (let i = 0; i < cycle.modules.length; i++) {
      const src = cycle.modules[i];
      const dst = cycle.modules[(i + 1) % cycle.modules.length];
      cycleEdges.add(`${src}|${dst}`);
    }
  }

  let edgeIndex = 0;
  const cycleEdgeIndices: number[] = [];
  const rendered = new Set<string>();

  for (const [src, targets] of Object.entries(adjacency).sort()) {
    for (const dst of [...targets].sort()) {
      const edgeKey = `${src}->${dst}`;
      if (rendered.has(edgeKey)) continue;
      rendered.add(edgeKey);

      const shortSrc = src.replace(/Module$/, '');
      const shortDst = dst.replace(/Module$/, '');
      lines.push(`  ${shortSrc}[${src}] --> ${shortDst}[${dst}]`);

      if (cycleEdges.has(`${src}|${dst}`)) {
        cycleEdgeIndices.push(edgeIndex);
      }
      edgeIndex++;
    }
  }

  if (cycleEdgeIndices.length > 0) {
    lines.push(
      `  linkStyle ${cycleEdgeIndices.join(',')} stroke:red,stroke-width:2px`,
    );
  }

  return lines.join('\n');
}

// ── Main ───────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  // Dynamically resolve the AppModule
  const modulePath = path.resolve(process.cwd(), APP_MODULE_PATH);
  let AppModule: any;

  try {
    const imported = await import(modulePath);
    AppModule = imported.AppModule || imported.default;
    if (!AppModule) {
      console.error(
        `Could not find AppModule export in ${modulePath}. ` +
          `Make sure it exports "AppModule" or a default export.`,
      );
      process.exit(1);
    }
  } catch (err) {
    console.error(`Failed to import AppModule from ${modulePath}:`, err);
    process.exit(1);
  }

  // Bootstrap the application context (no HTTP listener)
  const app = await NestFactory.createApplicationContext(AppModule, {
    logger: false,
  });

  // ── Explore ──────────────────────────────────────────────────────────

  const tree = SpelunkerModule.explore(app);

  // Build structured module list
  const modules: ModuleNode[] = tree.map((m: any) => ({
    name: m.name,
    imports: m.imports || [],
    providers: (m.providers || []).map((p: any) =>
      typeof p === 'string' ? p : p.name || String(p),
    ),
    controllers: (m.controllers || []).map((c: any) =>
      typeof c === 'string' ? c : c.name || String(c),
    ),
    exports: m.exports || [],
  }));

  // Build adjacency list from imports
  const adjacency: Record<string, string[]> = {};
  for (const mod of modules) {
    adjacency[mod.name] = [...mod.imports];
  }

  // ── Graph edges (spelunker native) ───────────────────────────────────

  const root = SpelunkerModule.graph(tree);
  const edges = SpelunkerModule.findGraphEdges(root);

  // Enrich adjacency from graph edges (catches dynamic module deps)
  const adjacencySets: Record<string, Set<string>> = {};
  for (const [name, deps] of Object.entries(adjacency)) {
    adjacencySets[name] = new Set(deps);
  }
  for (const edge of edges) {
    const fromName = edge.from.module.name;
    const toName = edge.to.module.name;
    if (!adjacencySets[fromName]) adjacencySets[fromName] = new Set();
    if (!adjacency[fromName]) adjacency[fromName] = [];
    if (!adjacencySets[fromName].has(toName)) {
      adjacencySets[fromName].add(toName);
      adjacency[fromName].push(toName);
    }
  }

  // ── Detect cycles ───────────────────────────────────────────────────

  const cycles = detectCycles(adjacency);

  // Collect all modules that participate in cycles
  const modulesInCycles = new Set<string>();
  for (const cycle of cycles) {
    for (const m of cycle.modules) {
      modulesInCycles.add(m);
    }
  }

  // ── Debug output ────────────────────────────────────────────────────

  let debugOutput: any[] | undefined;
  if (debugMode) {
    debugOutput = SpelunkerModule.debug(app);
  }

  // ── Build result ────────────────────────────────────────────────────

  const mermaid = generateMermaid(adjacency, cycles);

  const result: AnalysisResult = {
    summary: {
      totalModules: modules.length,
      totalCycles: cycles.length,
      modulesInCycles: Array.from(modulesInCycles),
    },
    modules,
    adjacency,
    cycles,
    ...(outputMermaid || !outputJson ? { mermaid } : {}),
    ...(debugMode ? { debug: debugOutput } : {}),
  };

  // ── Output ──────────────────────────────────────────────────────────

  if (outputJson) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log('=== NestJS Dependency Analysis (nestjs-spelunker) ===');
    console.log(`Modules found: ${modules.length}`);
    console.log();

    if (cycles.length === 0) {
      console.log('✅ No circular dependencies detected!');
    } else {
      console.log(`⚠️  Found ${cycles.length} circular dependency cycle(s):`);
      console.log();
      cycles.forEach((cycle, i) => {
        console.log(`  Cycle ${i + 1} (${cycle.length} modules):`);
        console.log(`    ${cycle.chain}`);
        console.log();
      });
    }

    console.log('=== Module Dependency Map ===');
    for (const [name, deps] of Object.entries(adjacency).sort()) {
      if (deps.length > 0) {
        console.log(`  ${name} → ${deps.join(', ')}`);
      } else {
        console.log(`  ${name} (no imports)`);
      }
    }

    if (outputMermaid) {
      console.log();
      console.log('=== Mermaid Diagram ===');
      console.log('```mermaid');
      console.log(mermaid);
      console.log('```');
    }
  }

  await app.close();
}

main().catch((err) => {
  console.error('Analysis failed:', err);
  process.exit(1);
});
