# Translation markup for `build_doc.py`

The translation lives in plain UTF-8 files `WORK/tr_1.txt`, `tr_2.txt`, … (concatenated in
name order). One line = one block. Splitting into several files keeps each Write small and
lets reviewers cite `file:line`. Blank lines and lines starting with `#` are ignored.

## Page setup (first file, once)

```
@page font="Times New Roman" size=12 top=3.0 bottom=2.8 left=2.0 right=1.9 ls=1.0 after=6 align=justify
@header-image page=1 index=0 width=2.75 align=right indent=0.8
```

- `@page` keys (all optional): `font`, `size` (pt), margins `top bottom left right` (cm),
  `width height` (cm, default A4), `ls` line spacing, `after` paragraph space-after (pt),
  `align` default paragraph alignment. Take the margins from `inspect_pdf.py` output.
- `@header-image`: an image from the source PDF placed in the **first page header only**
  (e.g. a logo on a cover). `page` is 1-based, `index` is the image index that
  `inspect_pdf.py` prints for that page. The area is re-rendered from the page at 300 dpi.

## Blocks

| Directive | Result |
|---|---|
| `@h TEXT` | Heading: bold + underlined, left, space before 18 / after 12, kept with next |
| `@hn TEXT` | Heading without underline |
| `@hc TEXT` | Centered bold underlined title |
| `@p TEXT` | Paragraph in the default alignment; `@pl` left, `@pc` center, `@pr` right |
| `@pi TEXT` / `@pi2` / `@pi3` | Paragraph indented 1.1 / 1.9 / 2.7 cm (continuation under a numbered item) |
| `@n LABEL \| TEXT` | Numbered item, hanging indent: label at 0, text at 1.1 cm (`4.1`, `-`, `1)`) |
| `@n2 LABEL \| TEXT` | Sub-item: label at 1.1, text at 1.9 cm (`a)`, `(i)`, `I.`) |
| `@n3 LABEL \| TEXT` | Label at 1.9, text at 2.7 cm |
| `@n4 LABEL \| TEXT` | Deep list: label at 3.4, text at 4.0 cm |
| `@bul TEXT` | Bullet `•` at 1.1, text at 1.9 cm |
| `@list LABEL \| TEXT` | Tight list (no space after), e.g. a list of appendices in small caps |
| `@gap` | Empty paragraph |
| `@break` | Page break |
| `@ls 1.3` | Line spacing for all following paragraphs (switch back with `@ls 1.0`) |
| `@cover size=14 gap=6 \| LINE \| LINE …` | Cover title block in a bordered box, `gap` empty lines above |
| `@img page=3 index=0 width=12 align=center` | Inline image re-rendered from the source page |
| `@toc TEXT` | TOC line with dot leader; page number filled in automatically |
| `@toc TEXT \|\| KEY` | Same, but search the PDF for `KEY` (use when the heading is worded differently than the TOC entry, or contains a different dash) |

The `|` separating label and text must have spaces around it (` | `).

## Tables

```
@table widths=2.8,3.4,1.0,3.0,1.3,4.5 borders=none underline=2,4,6 size=10 align=right
@row Name: | Jane Doe | Tel. | +00 000 000 000 | E-mail | jane@example.com
@endtable
```

Options: `widths` (cm, one per column; widths are written to the grid so LibreOffice honours
them), `borders` = `none` | `all` | `box`, `underline` = 1-based columns that get a bottom
rule (fill-in lines, signature lines), `size` (pt), `align` = table position
`left|center|right` (a 16 cm table aligned `right` starts at the 1.1 cm item indent),
`cellalign`, `after` (pt after each cell paragraph), `gapafter`, `cantsplit=yes|no`.

Typical uses: two-column definitions (`widths=3.8,13.3`, term in `**…**`), signature blocks
(`@row Signature: | Signature:` per line, `after=10`), contact rows.

## Inline

`**bold**`, `__underline__`, `//italic//`, `^^small caps^^` — toggles, may nest.
Three or more underscores (`________`) are kept literally as a fill-in blank.
Small caps only show on mixed-case text: write `^^Appendix^^`, not `^^APPENDIX^^`.

## Example

```
@page font="Times New Roman" size=12 top=3.0 bottom=2.8 left=2.0 right=1.9
@cover size=14 | USER MANUAL
@break
@hc CONTENTS
@toc 1 - INTRODUCTION
@toc 2 - SETUP || 2 - INSTALLATION
@h 1 - INTRODUCTION
@p A **device** means the unit described in this manual.
@h 2 - INSTALLATION
@n 2.1 | Place the device on a level surface and wait **10 minutes** before use.
@n2 a) | first item;
@pi A continuation paragraph under item 2.1.
```
