# Custom Add-on Authoring

## Overview

TanStack CLI add-ons are reusable integration packages. They bundle code, dependencies,
and configuration that get applied to a TanStack project via `tanstack add`.

## Workflow

### 1. Start from a working project

Create a project with the base setup you want your add-on to extend:
```bash
<runner> @tanstack/cli create my-addon-dev -y
```

Add your integration code to `src/integrations/` and any routes to `src/routes/`.

### 2. Initialize the add-on

```bash
<runner> @tanstack/cli add-on init
```

This creates `.add-on/info.json` with metadata fields:
- `type` — add-on type
- `phase` — when it runs during setup
- `modes` — supported modes (start, router-only)
- `priority` — execution order (lower = earlier)
- `dependencies` — required add-ons
- `conflicts` — incompatible add-ons

### 3. Edit info.json

Configure the metadata to match your add-on's requirements.

**Priority ranges:**
| Range | Category | Examples |
|-------|----------|---------|
| 0-10 | Toolchains | ESLint, Biome |
| 20-30 | Core libraries | TanStack Query |
| 30-50 | UI foundations | Tailwind CSS |
| 100-150 | Feature add-ons | Clerk, Drizzle, Sentry |
| 170-200 | Deployment | Vercel, Netlify, AWS |

### 4. Compile

```bash
<runner> @tanstack/cli add-on compile
```

Run after every change to metadata or template files.

### 5. Development mode

```bash
<runner> @tanstack/cli add-on dev
```

Watches for changes and recompiles automatically.

### 6. Test locally

In one terminal, serve the compiled add-on:
```bash
npx serve .add-on -l 9080
```

In another, create a test project using it:
```bash
<runner> @tanstack/cli create test-app --add-ons http://localhost:9080/info.json
```

### 7. Distribute

Publish the contents of `.add-on/` to a stable URL. Users can then:
```bash
<runner> @tanstack/cli add https://your-url.com/info.json
```

## Add-on directory structure

```
.add-on/
├── info.json       # Metadata (required)
├── package.json    # Dependencies to merge (optional)
└── assets/         # Files to copy into the project
    ├── src/
    │   ├── integrations/
    │   └── routes/
    └── ...
```

## Template syntax

Add-on templates use EJS for dynamic content. Available variables:
- `projectName` — the project name
- `typescript` — whether TypeScript is enabled
- `tailwind` — whether Tailwind CSS is present
- `selectedAddOns` — list of all selected add-ons
