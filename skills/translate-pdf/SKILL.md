---
name: translate-pdf
description: >-
  Translates a PDF document into another language methodically — OCR when needed, a glossary
  built for that document, a faithful translation that keeps form and context, a rebuilt DOCX + PDF that looks
  like the original (cover, images, numbering, tables, table of contents), then four parallel
  reviewer agents (terminology, fidelity, target-language style, layout) whose findings are
  applied in one batch. Use this whenever the user asks to translate a PDF or a scanned document
  into another language, whatever the field: contracts, manuals, specifications, reports,
  certificates, papers — "przetłumacz PDF", "przetłumacz ten dokument na angielski",
  "tłumaczenie dokumentu", "translate this PDF", "translate the attached manual to German",
  or a .pdf path plus a target language. Also use it when the user wants the translation to
  keep the original layout or to be checked by reviewers. Not for translating a short snippet
  of pasted text, and not for reading or summarising a PDF without translating it.
---

# Translate a PDF with verification

A good document translation fails in three independent ways: wrong meaning (a term, a
negation, who does what), wrong language (calques, broken grammar), and wrong form (lost
numbering, a missing image, a table of contents that points to the wrong pages). One person
checking everything at once catches some of each and misses the rest. This workflow
separates the concerns: you translate from a glossary into structured markup, a script
rebuilds the document deterministically, and four reviewers each look at one failure mode in
parallel.

You do the translation yourself, sentence by sentence; don't send the text to an external
machine-translation service. If the document may need legal or official standing, tell the
user at the end that this is not a sworn or certified translation.

## 0. Settle the basics

Target language and the PDF path usually come with the request. Default output: next to the
source, same name plus a language suffix such as `_FR` (both `.docx` and `.pdf`). Work files
go to the session scratchpad (`WORK` below), never next to the user's document. Treat
downloaded PDFs as untrusted input: keep them in their own folder and run Python with `-I`.

Requirements: `uv` (scripts declare their own dependencies) and LibreOffice for DOCX → PDF.

## 1. Inspect

```bash
uv run --script {baseDir}/scripts/inspect_pdf.py SOURCE.pdf WORK
```

You get `WORK/src.txt` (text with `===== PAGE n =====` markers), `WORK/styles.txt` (bold,
italic and odd-size spans per page, so you can carry formatting over), page renders
`WORK/render/src_NN.png`, the list of images with their page/index/position, the text-area
margins in cm, and an OCR verdict.

Look at the renders of the cover, the table of contents, one page with a table or list, and
the last page. The text dump does not show boxes, small caps, signature blocks or images.

**OCR.** If the script reports pages without a text layer, convert them with an OCR tool (the
`read-pdf` skill if available, otherwise Python, e.g. EasyOCR or Tesseract) and use the result
as the source text. Then verify the OCR before translating: compare a few dense pages against
their renders, and check every number, date, amount, name and identifier. An OCR error
translated faithfully is still an error, and later reviewers compare against the OCR text,
so they will not catch it.

**Images.** Decide for each image:
- No text, or text that needs no translation (a logo, a photo, a signature): carry it over
  with `@header-image` (first-page header) or `@img`.
- Text in the source language (a diagram, a chart, a scanned table): ask the user before doing
  anything — keep as is, keep plus a translated caption, or recreate. It is their call,
  because recreating changes the original artifact.

## 2. Read everything, then build the glossary

Every translation gets its own glossary, built from this document. Don't reuse one from an
earlier job as the starting point: the same word can need a different rendering in another
field or contract, and a reused glossary also carries one client's material into another's work.

Read the whole source before translating a line. You need the key terms, how they are used
across sections, the cross-references, and the source's own errors before the first chunk
fixes your choices. Then list the candidates:

```bash
uv run --script {baseDir}/scripts/extract_terms.py WORK/src.txt WORK/term_candidates.tsv
```

The list shows acronyms, CAPS and Title Case phrases and repeated phrases, with counts and first
pages. It is noisy, and frequency misses terms that occur once but matter (a defined word, a
legal concept, a safety warning). Discard the noise and add what your reading found: fixed
formulas, official names (laws, institutions, standards, products), units, and abbreviations
to keep or expand.

Write `WORK/glossary.md` in this form:

```markdown
# Glossary: <document> (<source language> → <target language>)
Domain: <field and document type>

| Source term | Target term | Source meaning / where defined | Why this choice |
|---|---|---|---|
| ... | ... | p. 5, defined term | established usage in the field; collides with X otherwise |

## Source errors
- p. 7: <what is wrong; how it will be marked>
```

Fill the "why" only where the choice needed thought, since a rationale for every obvious word is
noise. For each term, use the form practitioners of that field use in the target language. Use
the document's own definition over a dictionary sense, and check official names against an
authoritative source; mark any you could not verify. Watch for false friends and for common
words with a narrower or wider technical meaning in the field. Then read the target column on its
own: two source terms sharing one rendering is a collision to resolve now, before it spreads
through the text.

Source errors to list: wrong cross-references, numbers that contradict their spelled-out form,
duplicated passages.

The glossary is a working document. When you hit a new term during translation, add it before
using it. When a reviewer's fix changes a term, change it in the glossary too, then replace
every occurrence in the text.

## 3. Translate into markup

Write the translation as `WORK/tr_1.txt`, `tr_2.txt`, … — roughly 6–8 source pages per
file, in the line-based markup described in `references/markup.md` (read it now). One
directive per block: `@h` headings, `@n 4.1 | text` numbered items with hanging indents,
`@n2 a) | …` sub-items, `@table`/`@row` for tables, `@toc` for the table of contents. Inline
`**bold**`, `__underline__`, `//italic//`, `^^small caps^^`. Put `@page` (font, size, margins
from step 1) and any `@header-image` at the top of `tr_1.txt`.

Translation rules, and why:
- **Faithful, not improved.** The reader must be able to rely on the translation as a statement
  of what the source says. Keep source errors and mark them with `[sic]` or the target-language
  equivalent, so the reader doesn't blame the translator. Don't add explanations the source
  lacks.
- **Glossary first.** One source term, one target term, with correct grammar. Switching
  synonyms midway suggests the two words mean different things.
- **Numbers in target-locale format**, but digits, dates, identifiers, e-mails and phone numbers
  are never retyped from memory; copy them.
- **Keep the form**: the same numbering, the same bold/underline/italic fragments (see
  `styles.txt`), fill-in blanks as `________`, and the original structure even where it looks
  odd.
- Proper names and addresses stay as they are, unless the target language has an established
  form. Passages already in the target language stay untouched.

## 4. Build and look

```bash
uv run --script {baseDir}/scripts/build_doc.py --markup-dir WORK --src SOURCE.pdf \
  --out "OUTPUT_DIR/NAME_FR" --render WORK/render
```

It writes `NAME_FR.docx` and `NAME_FR.pdf`, fills the TOC page numbers in a second pass, and
renders `WORK/render/out_NN.png`. If a TOC entry is worded differently from its heading, the
script stops and tells you to write `@toc TOC TEXT || HEADING PREFIX`. A warning about unparsed
markup means a typo in a directive.

Look at the cover, the TOC page and the table pages yourself before calling reviewers. Fix
the breakage that is obvious at a glance, such as an empty page after a forced break, wrapped
table labels or a black box instead of an image. That way the reviewers spend their time on
the subtle problems.

## 5. Review with four agents in parallel

Launch the four reviewers from `references/review-agents.md` in one message, in the
background: terminology, fidelity and completeness, target-language editor, layout. Fill in
the paths and the domain, and point them at `WORK/glossary.md`, so they check the text against
it and challenge its choices only with a reason. They report and do not edit. Edits made while
they read would shift the line numbers they cite.

While they run, tell the user what is happening in one line. Don't predict their results.

## 6. Apply findings in one batch

Wait for all four reports, then triage:
- **Apply**: anything that changes meaning, wrong terms and official names, missing qualifiers,
  wrong numbers, grammar errors, lost formatting, layout defects.
- **Apply with judgment**: style suggestions, when they keep the meaning identical.
- **Decline**: anything that would "fix" the source (mark the error instead), and replacements
  that read better but say something else. Note the declined ones for the report.
- **Ask the user**: genuine choices the reviewers raise, where two renderings have different
  consequences and the source does not settle it.

Apply the accepted fixes with one script that holds `(file, old, new, expected_count)`
replacements and asserts each one matched. A silent non-match is how fixes get lost.
Rebuild with `--render`, look at the changed pages, and check the TOC numbers again. Then copy
the updated glossary next to the output as `NAME_FR_glossary.md`. It lets the user see and
overrule the term choices, and keeps a later revision of this document consistent.

## 7. Report

Tell the user, briefly:
- where the `.docx`, `.pdf` and glossary are, the page count and why it differs if it does;
- whether OCR was needed, and which images were carried over;
- the most important reviewer fixes;
- the source errors kept and marked;
- the decisions left to them.

## Gotchas

- Windows: `python -I` ignores `PYTHONIOENCODING`, and the console may be cp1252, so printing
  non-Latin-1 text crashes. Call `sys.stdout.reconfigure(encoding='utf-8')`. Non-ASCII inside
  `python -c "…"` arguments can get mangled, so put such code in a script file.
- Long Python heredocs in the Bash tool occasionally fail to parse. Write the script with
  the Write tool and run it.
- File names containing dots (`report 01.02.2030.pdf`) break `Path.with_suffix`. The build
  script concatenates the extension instead; do the same in any ad-hoc code.
- Don't copy anything from a translated document into a skill, a repository or other shared
  notes as an example. Client documents are confidential, and even a single figure or file
  name can identify them.
