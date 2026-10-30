# Reviewer prompts

Launch all four in **one message** (parallel, background) once the first build exists. Each
gets the same files and a different perspective, so their findings rarely overlap and none
of them is anchored on the others. They must not edit files: you apply the fixes yourself,
in one batch, so line numbers in the four reports stay valid until all have reported.

Fill in `{SRC_TXT}`, `{TR_FILES}` (e.g. `WORK/tr_1.txt … tr_4.txt`), `{SRC_LANG}`,
`{TGT_LANG}`, `{DOMAIN}` (the document's field and type), `{DECISIONS}` (the glossary choices
you made deliberately), `{RENDER_DIR}`, `{SRC_PDF}`, `{OUT_PDF}`. Write the prompts in the
language the user writes in, and ask for the reply in it.

Common preamble for 1–3:

> Files (UTF-8): source text extracted from the PDF, with `===== PAGE n =====` markers
> (justified text sometimes comes out one word per line): {SRC_TXT}. Translation, in order:
> {TR_FILES}. Translation lines start with layout directives (`@p`, `@n LABEL | text`, `@h`,
> `@toc`, `@table`/`@row` …) and inline markup `**bold**`, `__underline__`, `//italic//`,
> `^^small caps^^`; ignore the markup and judge the text. `[sic]` markers (or their
> target-language equivalent) flag source errors kept deliberately; do not "fix" those.
> Do NOT edit any files. Report only concrete findings as
> `file:line — current fragment — problem — proposed replacement`, ranked by severity
> (meaning-changing first). No praise, no summary of what is fine.

## 1. Terminology (domain expert)

> You are a {SRC_LANG}→{TGT_LANG} translator specialising in {DOMAIN}. Check whether terms are
> the established {TGT_LANG} equivalents in that field's practice, whether key terms are used
> consistently and with correct grammar, whether one term collides with another, and whether
> official names (laws, institutions, standards, products) are exact. Deliberate
> choices — challenge only if clearly wrong, with the reason: {DECISIONS}. Say which official
> names you could not verify. Max ~30 findings; skip pure style.

## 2. Fidelity and completeness

> Compare source and translation sentence by sentence. Check exhaustively: (1) omissions and
> additions — every clause, list item, parenthetical and qualifier; (2) every number, amount,
> percentage, date, unit, cross-reference, name, address, identifier, e-mail and phone number
> matches the source (target-locale number formatting is intended); (3) meaning shifts —
> obligation vs permission, negations, who does what to whom, scope of exceptions; (4) other
> obvious source inconsistencies that deserve a `[sic]` marker and do not have one (wrong
> cross-references, numbers contradicting their spelled-out form, duplicated passages), and
> markers that are unnecessary.

## 3. Target-language editor

> You are a {TGT_LANG} editor for {DOMAIN} texts. Judge only the {TGT_LANG}: grammar, syntax,
> agreement, punctuation; calques that read unnaturally in such a document (propose the
> idiomatic equivalent without changing the meaning); consistency of recurring formulas and
> reference styles; typos, quotation marks, dashes, spaces. Do not change the terminology
> listed here: {DECISIONS}. Max ~40.

## 4. Layout

> Compare the visual layout of the original PDF and its translation rebuilt as a new
> document. Page renders (70 dpi): original `{RENDER_DIR}/src_NN.png`, translation
> `{RENDER_DIR}/out_NN.png`; full PDFs if you need more resolution: {SRC_PDF} and {OUT_PDF}.
> Read the PNGs with the Read tool. The translation may be longer, so pagination need not
> match page for page. Judge whether it looks like the same document: cover, images, heading
> styles, numbered items and hanging indents, sub-lists, bullets, table of contents (check
> each TOC page number against where the heading really is in the translation), small caps,
> tables, fill-in blanks, bold/underline/italic fragments that the original has and the
> translation lost (or gained), spacing, margins, line spacing, font.
> Report: `translation page — element — what differs or is broken — suggested fix (in
> indentation / spacing / bold / table widths terms)`, ranked by visibility. Max ~20.
