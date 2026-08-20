---
name: fact-check-local
description: >-
  Verifies a report or document claim-by-claim against a LOCAL source corpus (papers,
  books, transcripts, data files on disk) so that verification converges and produces
  an auditable, evidence-backed verdict for every claim. Use this whenever the user
  asks to verify, fact-check, audit, or "check again" a report/synthesis/summary
  against its sources, complains that repeated reviews keep finding new errors, or
  asks how confident they can be in a document's claims. Also use when the user asks
  for "weryfikacja raportu" or wants a claim registry / traceability for a document.
  Do NOT use for fact-checking against the web (different problem - source
  credibility, not vouching).
---

# Fact-check a document against a local corpus

## Why this process exists

Unstructured "read it and find errors" review does not converge: each pass samples a
different subset of the document, verdicts are judgments rather than tests, and fixes
introduce new errors nobody re-checks. The result is that every review finds "new"
errors and trust erodes. This skill replaces that with a finite, enumerable list of
typed tests with a hard stop condition. Verification is done when every claim has an
evidence-backed verdict and the residual-error estimate is below threshold — never
when "this pass found nothing".

## Two ground rules before starting

**Findings first, fixes on request.** Verification produces verdicts and a findings
list — it does not edit the document. The user asked whether the document is right,
not for a different document; an unrequested edit also invalidates the frozen-version
audit trail. Apply fixes (diff-scoped, per Phase 5) only when the user asks for them.

**Scale the effort to the document.** The full apparatus below exists for large
syntheses (dozens of sources, hundreds of claims) where ad hoc review demonstrably
fails. For a small document (roughly < 200 lines / < 50 claims): one extraction agent,
one verifier-A agent, one adversarial verifier-B agent, same evidence and stop rules.
The invariants that never shrink are: the registry, evidence-mandatory verdicts, the
mechanical checks, and the stop criteria. What scales is only the number of agents.

## When NOT to use this skill

- Fact-checking against the web — that is a source-credibility problem, not a
  vouching problem, and the local-corpus stop criteria do not apply.
- Copy-editing, style review, or "is this argument sound?" — this skill tests claims
  against sources, it does not judge quality of reasoning.
- A document whose sources are not on disk: every claim lands on T6/UNVERIFIABLE and
  the process produces no signal.

## Artifacts produced (all in the project directory)

| File | Contents |
|---|---|
| `<REPORT>_FROZEN_<date>.md` | Frozen copy of the document under verification + SHA256 |
| `REJESTR_TWIERDZEN.md` (claim registry) | One row per atomic claim: ID, line, claim, attributed source, test type |
| `WERDYKTY_R<n>.md` (verdict tables) | Per-claim verdict + pasted evidence — the audit trail |
| `mechanical_checks.py` + `checks_config.json` | Project-specific mechanical tests, run after every edit |
| `WYNIK_RUNDY_<n>.md` (round result) | Findings, residual estimate, stop-criteria status |

## Workflow

### Phase 0 — Freeze and set materiality (before reading anything)

1. Copy the document to a dated frozen file; record its SHA256. All verdicts refer to
   this immutable version.
2. Write down severity classes BEFORE starting, so scope can't creep between rounds:
   - CRITICAL: claim contradicts source, wrong number, wrong attribution.
   - MAJOR: claim unsupported by its attributed source, overreach.
   - MINOR: imprecision that doesn't change conclusions. Below MINOR: don't log.

### Phase 1 — Claim registry (inventory, not judgment)

Extract EVERY atomic verifiable claim into a registry table. Atomic claim = every
number with a unit, every "source X states Y" attribution, every negative claim
("no source provides…"), every arithmetic relation, every count, every bibliography
entry. One sentence often contains several claims — split them.

- Delegate extraction to Sonnet agents, ~150–200 document lines per agent (detection
  quality collapses above ~400 lines per sitting). Prefix IDs per chunk (C1-, C2-)
  to avoid collisions.
- **Completeness is tested mechanically, not judged**: regex-sweep the document for
  every number+unit token and citation pattern; every hit must appear in the registry.
  Until the sweep is clean, Phase 1 is not done. (`mechanical_checks.py` does this.)

Each claim gets exactly one test type:

| Type | Test | Who runs it |
|---|---|---|
| T1 vouching | find the exact passage in the local source; paste quote + file:line | verifier agents |
| T2 arithmetic | recompute every sum/product/percentage in a script, never mentally | script |
| T3 cross-reference | same value quoted in ≥2 places of the document must be identical | script |
| T4 negative claim | "no source states X" → grep the whole corpus for X; grep output is the evidence | verifier agents + script |
| T5 bibliography | author/year/journal/DOI/counts vs the actual source file front matter | verifier agents + script |
| T6 out-of-corpus | source not on disk → verdict NIEWERYFIKOWALNE/UNVERIFIABLE, never fake a verdict | mechanical |

Tie-breaker when a claim fits several types: T4 > T2 > T5 > T1.

### Phase 2 — Mechanical tests (write once, run after every edit)

Copy `scripts/mechanical_checks.py` from this skill into the project, create
`checks_config.json` with the project's arithmetic relations, key cross-referenced
values, bibliography count expectations, and negative-claim grep terms. Run it now
and after EVERY subsequent edit of the document. This permanently eliminates the
whole class of arithmetic/count/cross-ref errors — they get caught by code, not eyes.

### Phase 3 — Independent double verification

Read `references/agent-prompts.md` for the exact agent prompt templates (they encode
hard-won pitfalls — use them, don't improvise). Key rules:

- **Verifier A** (session model, i.e. the strongest available): all T1/T4/T5 claims,
  split into agents by source cluster (books / papers part 1 / papers part 2).
  Verdicts: CONFIRMED / CONTRADICTED / NOT-IN-SOURCE / UNVERIFIABLE.
- **Verifier B** (deliberately a DIFFERENT model, e.g. Sonnet): blind adversarial
  cross-sample — every Nth registry row (N chosen for a ~10% sample), mindset REFUTE.
  Model diversity is not a cost optimization: two runs of the same model share blind
  spots, which silently inflates the capture-recapture estimate below.
  Pass the model via the Agent tool's `model` parameter. If no model override is
  available in your harness, still run B — blind, adversarial, with no access to A's
  verdicts — and record in the round result that A and B shared a model, so the
  capture-recapture estimate must be read as optimistic.
- **A verdict without pasted evidence is not a verdict.** Evidence = verbatim quote
  (≤40 words) + file:line, or the grep terms used for absence claims. This is what
  makes a second check re-derive the same verdict instead of issuing a new opinion.
- **Persist immediately**: each agent writes its verdict table straight to a
  `WERDYKTY_*` file on disk (or you save it the moment its result arrives). Agent
  transcripts are not reliably retrievable afterwards — losing the tables destroys
  the audit trail.
- **Arbitration**: disagreements between A and B go to the session model at high
  effort, with both pieces of evidence on the table. Known lens error to watch for:
  an adversarial verifier marks a NEGATIVE claim "unconfirmed" because it found
  nothing — finding nothing is exactly what CONFIRMS a negative claim.

### Phase 4 — Capture–recapture residual estimate

From the A/B overlap sample: A found n1 errors (MAJOR+), B found n2, m in common.
Chapman estimator: N̂ = (n1+1)(n2+1)/(m+1) − 1. Estimated undetected = N̂ − found.
Report the estimate with the honest caveat that small counts mean wide intervals —
it says "no signal anything remains", not "mathematically zero".

### Phase 5 — Diff-scoped fixes and stop criteria

- Fix ONLY registry findings; every fix references a claim ID. Update the registry
  row when the fixed text changes a value the completeness sweep tracks.
- Re-verify ONLY the diff (edited fragments + their T3 cross-references) plus a full
  `mechanical_checks.py` run. New issues found outside the diff go into the registry
  as new rows for the next round — they do not block closing this one (unbounded
  re-review scope is the main reason review loops never end).

Verification is DONE when all of these hold:
1. 100% of registry rows have an evidence-backed verdict (UNVERIFIABLE counts, listed explicitly).
2. All CRITICAL/MAJOR findings fixed and their diffs re-verified.
3. All mechanical tests pass.
4. Capture–recapture estimate of undetected CRITICAL/MAJOR ≤ 1.
5. The document itself flags its unverifiable claims (confidence section).

The closing statement is quantified: "N claims verified with evidence, M unverifiable
locally, estimated residual ≤ 1" — never "the report was checked".

## Model assignment

| Task | Model | Why |
|---|---|---|
| Claim extraction, diff re-verification | Sonnet | bulk mechanical work; completeness is guarded by the regex sweep, not the model |
| T2/T3/T5-counts/T4-greps | Python script | deterministic — a model only adds noise |
| T1 vouching, T4 judgment (verifier A) | session model | the hardest judgment: overreach vs coverage |
| Independent verifier B | different model than A | error decorrelation for capture–recapture |
| Arbitration of conflicts | session model, high effort | few cases, highest stakes |

## Follow-up rounds

Later rounds close whatever round 1 left open: author-declaration/meta claims get a
cheap classification pass (verdict DEKLARACJA AUTORSKA / AUTHOR-DECLARATION for
explicitly-framed design decisions and opinions — unverifiable by nature), and any
claim the document makes about its own history ("all prior corrections were applied")
gets audited item-by-item against the prior findings file. Compute the not-yet-verdicted
ID list mechanically (registry IDs minus verdict-table IDs), never by rereading.
