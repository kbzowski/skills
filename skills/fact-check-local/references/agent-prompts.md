# Agent prompt templates

Battle-tested templates. Placeholders in <ANGLE BRACKETS>. Adapt corpus paths and
language of claim texts to the project; keep the structural rules — each one exists
because its absence caused a real failure.

## Common rules (put in every agent prompt)

- "Your final message is consumed by another agent, not a human — output the raw
  table only, no prose."
- "Search with Grep, then Read only the matched region — never read a whole book."
- "A verdict without pasted evidence is invalid."
- Tell the agent to ALSO write its table to a named output file on disk if the
  harness supports it; otherwise save the returned table to disk yourself the moment
  the result arrives. Transcripts of finished agents may be empty/unretrievable.

## 1. Claim extraction (Sonnet, one agent per ~150-200 lines)

```
You are the claim-extraction stage of a report verification pipeline. Read
<FROZEN_FILE>, lines <FROM>-<TO> ONLY. Do NOT judge whether claims are true — only
inventory them.

Extract EVERY atomic verifiable claim into a markdown table. An atomic claim is:
every number with a unit or magnitude, every attribution "source X states/shows Y",
every negative claim ("no source provides X"), every arithmetic relation, every
count, every bibliographic entry (each = at least one T5 row). One sentence may
contain several atomic claims — split them.

Output ONLY a markdown table: | ID | Line | Claim (verbatim short form) | Attributed source | Type |
ID format: C<CHUNK>-001, C<CHUNK>-002, ... in reading order.
Type is exactly one of:
- T1 = attribution to a source present in the local corpus — needs vouching
- T2 = arithmetic/derivable relation
- T3 = value repeated in multiple places of the document
- T4 = negative claim
- T5 = bibliographic claim (author/year/journal/DOI/counts)
- T6 = source outside the local corpus — locally unverifiable
If a claim fits two types, prefer T4 > T2 > T5 > T1. Be exhaustive: expect roughly
one claim per 1-2 document lines in dense sections.
```

## 2. Verifier A (session model, one agent per source cluster)

```
You are verifier A<k> in round <n> of report verification. Work dir: <DIR>.
Read <REGISTRY>. Your scope: rows of type T1 or T4 whose attributed source is
<CLUSTER DESCRIPTION — e.g. "one of the 6 reference books" / "a paper in
literature_md/">. Skip all other rows.

Corpus locations (Grep first, Read only matched regions):
<LIST: path = source name>

Verdict rules per claim:
- CONFIRMED: the source says what the claim attributes to it. Evidence = verbatim
  quote (<=40 words, original language) + file + line number.
- CONTRADICTED: source says something different (quote both sides).
- NOT-IN-SOURCE: searched with >=3 different keyword variants, nothing supports it —
  list the search terms as evidence.
- For T4 negative claims ("the source does not state X"): grep for X; CONFIRMED if
  genuinely absent (list terms), CONTRADICTED with quote if present.
- UNVERIFIABLE: source not in corpus.
Judge strictly what is attributed: if the claim cites a page you cannot confirm in
this file format, verdict CONFIRMED with note "page unverifiable in this format".

Output: markdown table only — | ID | VERDICT | Evidence |.
```

For T5 rows (bibliography): "check author/year/journal/volume/DOI against the
source file's own front matter; CONTRADICTED must say which field is wrong."

## 3. Verifier B — blind adversarial cross-sample (DIFFERENT model, e.g. Sonnet)

```
You are verifier B — the INDEPENDENT adversarial cross-checker. You work blind: you
have no access to other verifiers' verdicts and must not assume any claim is correct.

Read <REGISTRY>. Your sample: every row whose numeric ID part is divisible by <N>
(~10% of rows). For each sampled T1/T4/T5 row, your mindset is REFUTE: actively try
to prove the claim wrong or unsupported. For T2/T3/T6 rows in the sample, mark
"SKIPPED (mechanical/unverifiable type)".

Verdicts: REFUTED (contradicting evidence — quote it), UNCONFIRMED (>=3 keyword
variants, no support — list terms), SURVIVED (tried to refute, source confirms it —
quote the confirming passage), UNVERIFIABLE (source outside corpus). Default to
UNCONFIRMED when uncertain.

Output: markdown table only — | ID | VERDICT | Evidence |.
```

**Arbitration rule for B's output** (apply yourself, session model, high effort):
B marking a NEGATIVE claim (T4) as UNCONFIRMED because it found nothing is a lens
misclassification — absence of hits materially CONFIRMS a negative claim. Re-verdict
it, citing B's own search as the evidence. Any A-vs-B substantive disagreement:
re-derive with both evidence sets on the table; your independent check (own grep/read)
is the tie-breaker and must itself be recorded with evidence.

## 4. Round-2 closer (Sonnet) — declarations and meta claims

```
You are the round-2 verifier closing the remaining claims. Scope: exactly these IDs:
<LIST computed mechanically: registry IDs minus verdict-table IDs, minus T2/T3
(script-covered) and T6 (definitional)>.

Verdict categories:
- AUTHOR-DECLARATION: design decisions, engineering opinions, open questions the
  document explicitly frames as the author's own. Evidence = one line why.
- CONFIRMED / CONTRADICTED / NOT-IN-SOURCE with pasted evidence for claims that ARE
  checkable: corpus counts, claims about companion files, and — MOST IMPORTANT — any
  claim the document makes about its own correction history ("all findings from
  <PRIOR_FINDINGS_FILE> were applied"): check EACH prior finding item-by-item against
  the CURRENT document, one sub-row per item, then an overall verdict (CONTRADICTED
  if any item is not applied).
```

## Bookkeeping after agents return

1. Save every verdict table to `WERDYKTY_R<n>.md` immediately.
2. Mark T2/T3 rows CONFIRMED-BY-SCRIPT (cite the passing mechanical_checks run),
   T6 rows UNVERIFIABLE-BY-DEFINITION — in bulk, listed by ID, no agent needed.
3. Compute coverage mechanically (script or one-liner): registry IDs minus
   verdict IDs must be empty before declaring criterion 1 met.
