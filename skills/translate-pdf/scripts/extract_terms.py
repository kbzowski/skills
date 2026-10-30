# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""List term candidates from a source text, so the glossary starts from the document itself.

    uv run --script extract_terms.py WORK/src.txt WORK/term_candidates.tsv [--min-count 3]
    uv run --script extract_terms.py --self-test

src.txt has ===== PAGE n ===== markers (written by inspect_pdf.py). Output columns: kind, count,
first page, term. Kinds: acronym, CAPS phrase, Title phrase, repeated phrase. Candidates only:
frequency finds recurring terms, while rare-but-critical ones still come from reading the text.

shortcut: tokenizes on word characters, so unsegmented scripts (Chinese, Japanese, Thai) yield
little; for those, build the glossary from reading alone.
"""
import argparse
import re
from collections import Counter


def is_caps(t):
    return t.isupper() and len(t) >= 2


def is_title(t):
    return t[0].isupper() and t[1:].islower() and len(t) >= 2


def candidates(text, min_count=3):
    counts, first, kind = Counter(), {}, {}

    def add(term, k, page):
        counts[term] += 1
        first.setdefault(term, page)
        kind.setdefault(term, k)

    for page_no, body in re.findall(r'===== PAGE (\d+) =====\n(.*?)(?=\n===== PAGE|\Z)', text, re.S):
        # split at sentence punctuation so runs and phrases never span two sentences
        for chunk in re.split(r'[.;:!?()\[\]“”„"]+\s', re.sub(r'\s+', ' ', body)):
            toks = re.findall(r"[^\W\d_][\w'’-]*", chunk)
            for pred, name in ((is_caps, 'CAPS phrase'), (is_title, 'Title phrase')):
                i = 1 if pred is is_title else 0  # a sentence's first word is capitalised anyway
                while i < len(toks):
                    j = i
                    while j < len(toks) and pred(toks[j]):
                        j += 1
                    if j - i >= 2:
                        add(' '.join(toks[i:j]), name, int(page_no))
                    elif j - i == 1 and pred is is_caps:
                        add(toks[i], 'acronym', int(page_no))
                    i = max(j, i + 1)
            for n in (2, 3, 4):  # short edge words are usually function words, in any language
                for i in range(len(toks) - n + 1):
                    gram = toks[i:i + n]
                    if all(t.islower() for t in gram) and len(gram[0]) > 3 and len(gram[-1]) > 3:
                        add(' '.join(gram), 'repeated phrase', int(page_no))
    rows = [(kind[t], c, first[t], t) for t, c in counts.items()
            if c >= (1 if kind[t] != 'repeated phrase' else min_count)]
    # drop a phrase contained in a longer one that occurs just as often
    long = [r for r in rows if r[0] == 'repeated phrase']
    rows = [r for r in rows if not (r[0] == 'repeated phrase' and any(
        o[3] != r[3] and f' {r[3]} ' in f' {o[3]} ' and o[1] == r[1] for o in long))]
    return sorted(rows, key=lambda r: (r[0], -r[1], r[3]))


def self_test():
    src = ('===== PAGE 1 =====\nThe Service Provider shall send the monthly usage report to ACME. '
           'The monthly usage report is due. The monthly usage report is final.\n'
           '===== PAGE 2 =====\nThe FINAL ACCEPTANCE follows. The Service Provider signs.\n')
    rows = {r[3]: r for r in candidates(src)}
    assert rows['monthly usage report'][:3] == ('repeated phrase', 3, 1), rows
    assert 'monthly usage' not in rows and 'usage report' not in rows, 'subsumed phrases must go'
    assert rows['FINAL ACCEPTANCE'][0] == 'CAPS phrase' and rows['FINAL ACCEPTANCE'][2] == 2
    assert rows['ACME'][0] == 'acronym'
    assert rows['Service Provider'][:2] == ('Title phrase', 2)
    print('self-test ok')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?')
    ap.add_argument('out', nargs='?')
    ap.add_argument('--min-count', type=int, default=3)
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.src and a.out):
        ap.error('src and out are required')
    with open(a.src, encoding='utf-8') as f:
        rows = candidates(f.read(), a.min_count)
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write('kind\tcount\tfirst_page\tterm\n')
        f.writelines(f'{k}\t{c}\t{p}\t{t}\n' for k, c, p, t in rows)
    print(f'{len(rows)} candidates -> {a.out}')


if __name__ == '__main__':
    main()
