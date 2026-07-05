---
name: adobe-firefly
description: >
  Drive Adobe Firefly's web app (firefly.adobe.com) through Chrome browser
  automation to generate images from a text prompt — no API. Pick a model,
  set aspect ratio / resolution or quality / reference images, generate, then
  download the result via Firefly's own Download button. Use when the user asks
  to "generate an image with Firefly", "make a picture in Adobe Firefly",
  "use Firefly to create an image", or mentions "firefly". Scope is IMAGE
  generation only (not video, audio, or the edit/upscale tools). Requires an
  Adobe account the user logs into manually, and the claude-in-chrome tools.
---

# Adobe Firefly — image generation via the web app

Firefly is Adobe's generative studio. This skill covers **image generation
only** (Image → Generate image). It generates through the browser UI, so it
spends the user's generative credits and needs a logged-in Adobe account.

**Localization:** Firefly's UI language follows the browser locale, so button
labels change per user (e.g. a Polish browser shows "Generuj" instead of
"Generate"). This skill uses **English labels**; match controls by their role,
position, and icon, and confirm with a screenshot rather than trusting an exact
string. A short EN⇄PL label map is at the bottom for Polish-locale sessions.

## Golden rules

- **Never log in or type credentials.** If logged out, hand control to the user
  (step 0).
- **Never buy credits / click "Buy more" / "Buy now", accept terms, or dismiss
  content-policy notices** on the user's behalf.
- **Read the credit cost aloud before every generation.** The Generate button
  shows "Uses N credits" for partner models (varies by model *and* by
  quality/resolution: verified Gemini 3.1 = 20; GPT Image 2 = 10 at Medium, 60
  at High). **Adobe/Firefly models show "Unlimited access" instead — no credit
  cost on this plan**, so they're the free choice for iterating.
- **Ask before downloading** (state that it saves a PNG to Downloads), per the
  file-download policy — even though saving is the goal.
- **Read model settings live.** The available aspect ratios, the
  resolution-vs-quality control, extra toggles, and reference-image support all
  **depend on the selected model** — re-read the panel after any model change.

## Setup

Load the Chrome tools in one `ToolSearch` call, get tab context, create a new
tab, navigate to `https://firefly.adobe.com/generate/image` (the image-generate
view — it loads even when logged out, so you can inspect models before sign-in).

A cookie banner may appear on first load — click **"Decline"** (the
privacy-preserving choice), not "Enable all".

## 0. Verify login state (BEFORE generating)

Take a screenshot and check the **top-right corner**:

- **"Sign in" button present → NOT logged in.** Stop. Ask the user to log in
  manually in this Chrome tab (Adobe / Google / SSO), wait for confirmation,
  then re-screenshot and re-check. Do not drive the login yourself.
- **Account avatar + a generative-credits counter (and a "Buy more" button)
  present → logged in.** Proceed.

The left settings panel renders even when logged out, so seeing the Model panel
does **not** prove you're signed in — the avatar/credits check is what confirms
it. If mid-session a generation bounces to a sign-in page, the session expired —
repeat this step.

## 1. Choose the model

Click the **Model** dropdown (top of the left "General settings" panel). Two
groups (snapshot captured 2026-07 — read the live list, it drifts):

- **Adobe models** — *Commercially safe* (Adobe IP-indemnified): **Firefly
  Image 5**, **Firefly Image 4 Ultra**, **Firefly Image 4**, **Firefly
  Image 3**. A 👑 crown marks premium.
- **Partner models** — third-party, NOT covered by Adobe's IP guarantee:
  **GPT Image 2 / 1.5 / 1**, **Gemini 3.1 (Nano Banana 2)**, **Gemini 3 (Nano
  Banana Pro)**, **Gemini 2.5 (Nano Banana)**, **FLUX.2 [pro]**, **FLUX.1
  Kontext [max] / [pro]**, **FLUX1.1 [pro] Ultra Raw / Ultra / [pro]**,
  **Runway Gen-4 Image**.

Present the live list to the user grouped as above and ask which to pick. Click
the chosen entry; a ✓ marks the active model.

**The two families behave very differently — not just look:**

| | Adobe (Firefly Image 3/4/5) | Partner (GPT / Gemini / FLUX / Runway) |
|---|---|---|
| Cost | **Unlimited** (no credits) | Credits per generation (10–60+) |
| Output | **Grid of 4 variations** | Single image (Gemini, GPT) |
| Settings panel | Rich (content type, visual intensity, composition + style references, effects) | Minimal (aspect + resolution *or* quality) |
| Commercial use | IP-indemnified | Not covered by Adobe's guarantee |

So the choice drives the *whole* rest of the flow. Flag the tradeoff: Adobe
models are free + commercially safe + richer; partner models cost credits and
aren't IP-indemnified but give a specific look.

## 2. Set the options (they depend on the model)

After selecting the model the panel shows only that model's controls. Read each
dropdown live. Verified examples of how much they differ:

| Control | Gemini 3.1 | GPT Image 2 | Firefly Image 4 |
|---|---|---|---|
| **Aspect ratio** | Automatic + ~13 ratios | Automatic + ratios | ratios (e.g. 4:3) |
| **Resolution** | 512 / 1K / 2K / 4K | — | — |
| **Quality** | — | Low / Medium / High | — |
| **Content type** (Photo/Art/Auto) | — | — | **yes** |
| **Visual intensity** slider | — | — | **yes** |
| **Composition** + **Style** references | — | — | **yes (2 slots)** |
| **Effects** preset browser | — | — | **yes** |
| **Use Google search** toggle | yes | no | no |
| **Reference images** | single "0/6" slot | single "0/6" slot | via Composition/Style |
| **Cost** | 20 credits | 10 (Med) / 60 (High) | **Unlimited** |

So partner models expose **Resolution** *or* **Quality** and a single reference
slot; **Firefly models drop those for a much richer panel** (content type,
visual-intensity slider, separate Composition + Style reference slots, and an
Effects preset browser with tag filters). Offer the user **only the live
options** for the
current model, never a value it doesn't list. Reasonable defaults if the user
doesn't care: Aspect ratio *Automatic*, and the mid option of whatever
resolution/quality control is shown (e.g. 1K, or Medium).

**Reference images** are model-dependent and have their own upload quirk — see
the dedicated section after step 6.

## 3. Refine the prompt (always offer)

Before generating, **always propose an improved prompt**: take the user's idea
and offer a tightened version (subject, composition, lighting, style, mood,
lens/medium as relevant) plus a one-line note on what you changed. Let the user
accept, edit, or keep their original. Keep it short — don't lecture.

## 4. Generate

1. Click the **Prompt** field at the bottom (placeholder "Describe the image
   you want to generate").
2. Type the final prompt.
3. The **Generate** button (bottom-right) enables once the prompt is non-empty;
   next to it a **"Uses N credits"** readout shows the cost. Read it to the
   user, then click Generate.
4. Wait and poll with short waits + screenshots. Speed varies by model:
   **Gemini ≈ 15 s, GPT Image 2 ≈ 25–35 s, Firefly ≈ 10–20 s.** **Result count
   is model-dependent (verified): Gemini and GPT Image 2 return a single image;
   Firefly Image 4 returns a grid of 4 variations.** If a credits / paywall /
   content-policy notice appears instead, report it verbatim and stop — don't
   dismiss or purchase.

## 5. Save the image (verified flow)

Firefly auto-saves to Adobe cloud; to get a local file, **hover the result** to
reveal its controls, then use one of two download entry points:

- the header button (top-right, above the images): **"Download"** for a single
  result, or **"Download all"** when the result is a grid (saves every tile), or
- the **download-arrow icon** on an individual tile (top-right of the tile, next
  to the blue **Ps** = open-in-Photoshop icon) — saves just that one variation.

For a grid (Firefly models), confirm with the user whether they want one tile or
all four, then use the per-tile icon or "Download all" accordingly.

Clicking **Download triggers an immediate download** — no format/size dialog. A
"Downloading…" toast appears and the file saves to the Chrome download folder
(Windows default: `~/Downloads`) as a **PNG** named
`Firefly_<first ~90 chars of the prompt> <id>.png`.

- **Click exactly once** — each click downloads another copy; the same prompt
  produces the same base filename (the `<id>` is derived from the prompt, not
  unique per model/image), so extra clicks just make Chrome append `(1)`, `(2)`.
- **Ask the user's permission first** (state it saves a PNG to Downloads), click
  once, then confirm the saved path by listing the newest file in `~/Downloads`.

Other hover controls, for reference: **Edit** dropdown (top-left), thumbs
up/down, share, favorite (star), and the header **"…" menu** + chevron. If a
download ever opens an OS "Save as" dialog the extension can't reach, ask the
user to confirm it manually.

## 6. Iterate (optional)

To improve a result: adjust the prompt (step 3) or options (step 2) and
re-generate, or feed a prior output back in as a reference image (below).
Editing an existing image (inpaint, remove object, expand, upscale) is the
**Edit** tab — out of this skill's scope; say so.

## Reference images (model-dependent, has an upload quirk)

Reference images let you steer a generation with an existing picture. **The
slots differ by model family:**

- **Partner models (Gemini / GPT / FLUX):** one **"Reference images (0/6)"**
  section — up to 6 images, blended for general guidance. Its hidden input is
  `multiple:false`, so **inject one image at a time** (the counter climbs
  0/6 → 1/6 → …); each adds a prompt-bar chip (e.g. "Object reference image").
- **Firefly (Adobe) models:** two *separate* slots under the panel —
  **Composition** (structure/layout) and **Style** (look/aesthetic). Each slot
  offers **Add image** (upload from the computer), **Browse gallery** (Adobe
  presets), and — once an image is added — an **Intensity** slider controlling
  how strongly it applies. An active reference shows a thumbnail (with ✕) and a
  chip in the prompt bar (e.g. "Composition reference ✕") plus a **Clear**
  button. Use Composition to copy a layout, Style to copy an aesthetic.

**Upload quirk — the file inputs are hidden inside shadow DOM** (Firefly is
built with Spectrum Web Components). Consequences:

- `find` / `read_page` return no file-input `ref`, so the ref-based
  `file_upload` / `upload_image` tools **cannot target these inputs**.
- Clicking **"Add image"** opens a native OS file picker the extension can't
  drive (and it can block the session) — avoid clicking it blind.

Working approaches, in order of preference:

1. **Reuse an on-page image (verified on Firefly *and* GPT/Gemini):** the
   generated results live at same-origin `firefly.adobe.com/*.png`. Inject one
   straight into a slot's hidden input via `javascript_tool` — walk shadow roots
   to collect `input[type=file]`, `fetch` the image → `File` → `DataTransfer` →
   set `input.files` → dispatch a bubbling `change` event. The thumbnail + chip
   confirm success. **Slot order matches panel order**: on Firefly, index 0 =
   Composition, 1 = Style; on partner models there's a single input (the 0/6
   slot).
2. **Upload a computer file:** base64-encode the file (keep it small), then in
   `javascript_tool` decode → `Uint8Array` → `Blob` → `File` and inject exactly
   as above. Only files the session can read; large images bloat the payload, so
   downscale first.
3. **Fallback:** ask the user to drag the file onto the dashed dropzone, or click
   "Add image" and pick it themselves, then continue.

After the reference is registered (thumbnail + prompt-bar chip visible),
generate as normal (step 4). For Firefly this is free, so iterate on the
Intensity slider freely.

## EN ⇄ PL label map (Polish-locale sessions)

| English | Polish |
|---|---|
| Image / Generate image | Obraz / Generuj obraz |
| General settings | Ustawienia ogólne |
| Model / Adobe models / Partner models | Model / Modele Adobe / Modele partnerskie |
| Commercially safe | Bezpieczne komercyjnie |
| Aspect ratio | Proporcje |
| Resolution / Quality (Low/Medium/High) | Rozdzielczość / Jakość (Niska/Średnia/Wysoka) |
| Reference images | Obrazy referencyjne |
| Content type (Photo / Art / Auto) | Typ zawartości (Zdjęcie / Grafika / Automatyczne) |
| Visual intensity / Intensity | Intensywność wizualna / Intensywność |
| Composition / Style / Effects | Kompozycja / Styl / Efekty |
| Reference materials | Materiały referencyjne |
| Add image / Browse gallery / Clear | Dodaj obraz / Przeglądaj galerię / Wyczyść |
| Use Google search | Użyj wyszukiwania Google |
| Prompt / Generate / Uses N credits | Polecenie / Generuj / Wykorzystuje N kredytów |
| Unlimited access | Nieograniczony dostęp |
| Download / Download all / Downloading… | Pobierz / Pobierz wszystko / Pobieranie… |
| Sign in / Buy more / Pricing / Decline | Zaloguj się / Kup więcej / Cennik / Nie włączaj |
| Automatic / Square / Landscape / Portrait | Automatyczne / Kwadrat / Poziomo / Pionowo |

## Pitfalls

- **Logged-out illusion**: the generate UI renders without a session; only the
  avatar/credits check proves you're signed in.
- **Stale model list**: Adobe adds/removes models often — always read the live
  dropdown, don't trust the snapshot names above.
- **Options reset per model**: switching the model swaps Resolution↔Quality and
  changes available ratios/toggles. Re-read the panel after any model change.
- **Cost varies a lot**: same model, higher quality can be several× the credits
  (GPT Image 2: 10→60 from Medium→High). Always read "Uses N credits" first.
- **Double-download**: one click per copy; don't click Download twice.
- **Firefly ≠ partner models**: Adobe/Firefly models are unlimited, return a
  4-grid, and have a much richer panel (content type, intensity, composition +
  style references, effects); partner models cost credits, return one image, and
  have a minimal panel. Don't assume one model's flow applies to another.
- **Shadow DOM**: Firefly's controls live in Spectrum Web Components, so
  `find`/`read_page` miss file inputs and many elements. Prefer coordinate
  clicks (via screenshots) for interaction and `javascript_tool` with shadow-root
  walking for DOM work (e.g. reference-image upload).
- **Commercial use**: only Adobe (Firefly) models carry Adobe's IP indemnity —
  warn the user before using a partner model for commercial work.
