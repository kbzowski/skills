# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf>=1.24"]
# ///
"""First look at a PDF before translating it.

    uv run --script inspect_pdf.py SOURCE.pdf WORKDIR

Writes WORKDIR/src.txt (text with ===== PAGE n ===== markers), WORKDIR/styles.txt (bold/italic
spans and font sizes per page, so formatting can be carried over), WORKDIR/render/src_NN.png
(70 dpi page images) and prints a summary: text layer per page, images, layout geometry, and
whether OCR is needed.
"""
import sys
from collections import Counter
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding='utf-8')  # Windows consoles default to cp1252 and choke on non-Latin-1 text
src, work = Path(sys.argv[1]), Path(sys.argv[2])
(work / 'render').mkdir(parents=True, exist_ok=True)
d = pymupdf.open(src)
print(f'{src.name}: {d.page_count} pages, size {d[0].rect.width:.0f}x{d[0].rect.height:.0f} pt, '
      f'producer={d.metadata.get("producer")!r}')

scanned, x0s, x1s, y0s, y1s, fonts, sizes = [], [], [], [], [], Counter(), Counter()
with open(work / 'src.txt', 'w', encoding='utf-8') as txt, open(work / 'styles.txt', 'w', encoding='utf-8') as sty:
    for i, p in enumerate(d):
        n = i + 1
        text = p.get_text()
        txt.write(f'\n===== PAGE {n} =====\n{text}')
        imgs = p.get_images()
        area = p.rect.width * p.rect.height
        big = any(r.width * r.height > 0.5 * area for im in imgs for r in p.get_image_rects(im[0]))
        if len(text.strip()) < 50 and (big or imgs):
            scanned.append(n)
        for j, im in enumerate(imgs):
            for r in p.get_image_rects(im[0]):
                print(f'  page {n}: image index={j} xref={im[0]} {im[2]}x{im[3]}px at '
                      f'x={r.x0:.0f}-{r.x1:.0f} y={r.y0:.0f}-{r.y1:.0f} pt')
        for b in p.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                for s in ln['spans']:
                    if not s['text'].strip():
                        continue
                    x0s.append(s['bbox'][0]); x1s.append(s['bbox'][2]); y0s.append(s['bbox'][1]); y1s.append(s['bbox'][3])
                    fonts[s['font']] += len(s['text']); sizes[round(s['size'], 1)] += len(s['text'])
                    bold, ital = 'Bold' in s['font'] or s['flags'] & 16, 'Italic' in s['font'] or s['flags'] & 2
                    if bold or ital or abs(s['size'] - 12) > 0.6:
                        sty.write(f'p{n} x={s["bbox"][0]:.0f} {"B" if bold else ""}{"I" if ital else ""} '
                                  f'{s["size"]:.1f}pt: {s["text"].strip()[:90]}\n')
        p.get_pixmap(dpi=70).save(work / 'render' / f'src_{n:02d}.png')

def q(v, f):  # robust edge: ignore stray header/footer outliers
    v = sorted(v); return v[int(len(v) * f)] if v else 0
W, H = d[0].rect.width, d[0].rect.height
print(f'text area (pt): x {q(x0s, .02):.0f}-{q(x1s, .98):.0f}, y {q(y0s, .02):.0f}-{q(y1s, .98):.0f}  '
      f'-> margins cm: left {q(x0s, .02) / 28.35:.1f}, right {(W - q(x1s, .98)) / 28.35:.1f}, '
      f'top {q(y0s, .02) / 28.35:.1f}, bottom {(H - q(y1s, .98)) / 28.35:.1f}')
print('fonts:', ', '.join(f'{f.split("+")[-1]}' for f, _ in fonts.most_common(4)))
print('sizes:', ', '.join(f'{s}pt' for s, _ in sizes.most_common(4)))
if scanned:
    print(f'OCR NEEDED on pages {scanned} (little or no text layer). Run the read-pdf skill with --full-ocr.')
else:
    print('text layer OK on all pages; no OCR needed')
print(f'wrote {work / "src.txt"}, {work / "styles.txt"}, {work / "render"}/src_NN.png')
