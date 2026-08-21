---
name: read-pdf
description: >-
  Converts a PDF into clean, agent-readable Markdown using docling with GPU-accelerated
  EasyOCR (tables, headings and optional figure extraction preserved). Use this whenever a
  PDF has to be read, summarized, quoted, searched, fact-checked, or fed into any further
  processing — including scanned or photographed documents, papers, invoices, contracts,
  reports and manuals — and whenever the user says "przeczytaj PDF", "wyciągnij tekst z PDF",
  "PDF na markdown", "zeskanowany PDF", "OCR", "wyciągnij rysunki/wykresy z PDF",
  "read this pdf", "extract text from pdf", "pdf to markdown", or drops a .pdf path into the
  conversation. Prefer this over reading the PDF directly: raw PDF reads lose table structure,
  mangle multi-column layouts and return nothing at all for scans. Not for generating or
  editing PDFs.
---

# PDF → Markdown for further processing

A PDF read straight into context arrives as flat text: columns interleave, tables collapse
into word soup, and a scanned page yields nothing. Everything downstream — the summary, the
quote, the fact-check — inherits those errors silently. This skill converts once, to a
Markdown file on disk, so the rest of the work happens on structured text you can grep,
cite by line, and re-read without re-parsing.

## Run it

```bash
uv run --script {baseDir}/scripts/pdf_to_md.py INPUT.pdf            # text only
uv run --script {baseDir}/scripts/pdf_to_md.py INPUT.pdf --images   # + extracted figures
```

Without `--images` you get a single `INPUT.md` next to the source, figures reduced to
`<!-- image -->` placeholders. With `--images` the run produces many files, so it gets its
own directory: `INPUT/INPUT.md` plus `INPUT/INPUT_artifacts/` holding the figures that the Markdown links to by relative path. `-o` overrides either — a path ending in
`.md` is taken as the output file, anything else as the output directory.

The script is self-contained (PEP 723 inline dependencies), so `uv` builds its environment on
first use. **That first run downloads a CUDA torch wheel plus the docling layout/TableFormer
and EasyOCR models — several GB, and minutes.** Run it in the background or with a generous
timeout; a two-minute timeout will look like a failure when it is just a download. Later runs
start in seconds and convert a page or two per second on the GPU.

## Choosing the flags

The default (hybrid OCR, `pl`+`en`, tables reconstructed, no image files) is right for most
documents. Change it when the document tells you to:

| Situation | Flag | Why |
|---|---|---|
| Scan or phone photo; default run produced little/garbled text | `--full-ocr` | Forces OCR on every page instead of trusting the PDF text layer |
| Digital-born PDF with a solid text layer (LaTeX/Word export) | `--no-ocr` | Skips OCR entirely — several times faster, no OCR transcription errors |
| The figures/charts/micrographs matter, not just the prose | `--images` | Writes them as PNG so they can be looked at or passed on |
| Figures need to be legible at high zoom | `--image-scale 3` | 1.0 ≈ 72 DPI; 2.0 is the default |
| A whole page must be reproducible as an image | `--page-images` | Adds `page_NNN.png` per page (implies `--images`) |
| Document is not Polish/English | `--lang de fr …` | EasyOCR codes; stay within one script family (Latin, Cyrillic, …) per run |
| Only part of a long document matters | `--pages 12-30` | Avoids minutes of work on pages nobody will read |
| No GPU on this machine | `--device cpu` | Explicit opt-in to the slow path |
| Unsure whether this box has a GPU | `--device auto` | Uses CUDA if present, CPU otherwise, without the hard fail |
| A `--device cpu` run is slow and the box has many cores | `--threads 16` | Raises docling's worker count (default 8) |

The script refuses to start if `--device cuda` is asked for and CUDA is unavailable. That is
deliberate: CPU OCR is roughly an order of magnitude slower, and a silent fallback reads as a
hang. If it fires, either accept `--device cpu` or fix the torch install (see below).

## After the conversion — verify before you trust it

Conversion is lossy in ways that are cheap to spot and expensive to miss. Before using the
Markdown as ground truth, read the first page or two of it and check:

- **Is it roughly the expected length?** A near-empty file from a 40-page PDF means the text
  layer was absent and layout detection found nothing → rerun with `--full-ocr`.
- **Do tables look like tables?** Docling emits real Markdown tables. A table that came out as
  a run-on paragraph did not get reconstructed; the numbers in it are unreliable, so quote the
  source page instead of the Markdown, or rerun with `--images --page-images` and read the page.
- **Is the OCR text plausible?** OCR errors cluster in numbers and units (`l` vs `1`, `O` vs
  `0`, decimal separators). If a downstream task depends on exact figures from a scan, verify
  them against the page rather than the transcription.

Say which of these you checked when reporting back — "converted, 38 pages, tables intact,
12 figures in X_artifacts/" is a useful handoff; "done" is not.

## Feeding it onward

The output is one Markdown file, so normal tooling applies: `grep` for terms, read line ranges
rather than the whole file for long documents, and cite as `INPUT.md:123`. Keep the Markdown
around — a second conversion of the same PDF costs minutes and produces the same bytes.

For a batch, loop in the shell rather than converting one PDF per agent invocation; the models
still reload per process, but you avoid paying for an agent turn each time.

## When something breaks

- **`CUDA not available`, and the run installed nothing** — uv reused a cached script
  environment that still holds a CPU torch wheel; an already-installed `torch` of any flavour
  satisfies the requirement, so changing the index alone does not force a reinstall. Delete the
  cached envs and re-run: `rm -rf "$(uv cache dir)/environments-v2/pdf-to-md-"*`
- **`CUDA not available` on a fresh environment** — the `[[tool.uv.index]]` block at the top of
  `{baseDir}/scripts/pdf_to_md.py` pins torch to the `cu130` PyTorch index; edit that URL if this
  machine's driver needs a different CUDA build. Keep the file's **LF line endings** — a CRLF
  rewrite of the metadata block is easy to introduce and hard to notice.
- **`Unsupported EasyOCR language code`** — the `--lang` value is not an EasyOCR code, or mixes
  incompatible script families in one run. Convert once per script family.
- **Out-of-memory on the GPU** — narrow the work with `--pages`, drop `--image-scale`, or fall
  back to `--device cpu` for that document.
- **Encrypted / password-protected PDF** — docling cannot open it. Say so; do not guess at
  passwords.
