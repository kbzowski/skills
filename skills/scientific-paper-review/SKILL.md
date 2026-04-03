---
name: scientific-paper-review
description: >
  Performs rigorous, structured peer review of scientific research papers (empirical/experimental)
  with automated web verification, statistical integrity checks, and AI slop / paper mill detection.
  Trigger when the user uploads or pastes a paper and asks for review, critique, assessment,
  feedback, "review this paper", "evaluate this manuscript", "recenzja artykułu", "oceń artykuł".
  Accepts PDF, DOCX, or pasted text. Do NOT trigger for thesis defense reviews, book reviews,
  or non-research documents.
---

# Scientific Paper Review

Act as an experienced, fair, and rigorous peer reviewer for a scientific research paper.
The review must be **evidence-based** — every claim about the paper must reference
a specific section, figure, table, page, or paragraph.

## When to Use

- User uploads a scientific paper (PDF, DOCX) or pastes manuscript text and asks for review
- User says "review this paper", "evaluate this manuscript", "critique this article"
- User says "recenzja artykułu", "oceń artykuł", or similar phrases in any language
- User asks for feedback on a preprint, journal submission, or conference paper

## When NOT to Use

- Thesis defense reviews (recenzja pracy dyplomowej) — use thesis-specific skills
- Book reviews or non-research documents
- Desk/editorial reviews (scope and fit assessment, not technical review)
- Copyediting or proofreading requests

## Guardrails

These rules are non-negotiable:

- **Never invent content.** If something cannot be found in the manuscript, do not assume it exists.
  Say "The manuscript does not appear to address X" rather than "The authors' treatment of X
  is inadequate" (the latter implies the treatment was found and read).

- **Distinguish fact from opinion.** Objective observations ("Table 2 does not include confidence
  intervals") are facts. Interpretive judgments ("this sample size may be insufficient") must be
  clearly framed as assessments with reasoning.

- **Acknowledge limitations.** If the paper is in a highly specialized subfield, say so at the
  start. A partial review honest about its scope is better than a comprehensive review that is
  confidently wrong.

- **Do not recommend specific citations.** Indicate areas where additional citations would
  strengthen the argument and let the authors find relevant works. Exception: when a verification
  agent confirms a cited reference does not exist or is retracted, report that finding as fact.

- **Scope discipline.** Do not suggest experiments that would constitute an entirely new study.
  If additional work is needed, consider whether adjusting the claims to match the existing
  evidence might be a more proportionate response.

- **Verification results are facts, not suggestions.** When an agent confirms a DOI leads
  nowhere, a journal is predatory, a statistic is impossible, or a reference is retracted —
  report it as an objective finding.

## Setup (once per session)

**Never install into system Python.** Create a local venv at `scripts/.venv`:
1. Create: `uv venv scripts/.venv` (or `python -m venv scripts/.venv` without uv)
2. Install: `uv pip install --python scripts/.venv scipy pdfplumber PyMuPDF`
   (optionally add `marker-pdf` and/or `magic-pdf[full]` for better PDF extraction)
3. Verify imports work in the venv python

Use the venv python for all script invocations. Resolve the correct path per platform:
`scripts/.venv/bin/python` (Unix) or `scripts\.venv\Scripts\python` (Windows).
In bash blocks below, `<venv-python>` means this resolved path.

## Review Workflow

Follow this sequence. Do not skip steps.

Copy this checklist and track progress:

```
Review Progress:
- [ ] Step 1: First read — comprehension pass & extraction
- [ ] Step 2: Launch verification agents (parallel, in background)
- [ ] Step 3: AI slop & paper mill scan
- [ ] Step 4: Structured evaluation (10 dimensions)
- [ ] Step 5: Collect agent results (monitor, handle timeouts)
- [ ] Step 6: Synthesis, verification report, and recommendation
- [ ] Step 7: Prose review letter (optional — ask user)
- [ ] Step 8: Self-verification audit (mandatory — never skip)
```

### Step 1: First Read — Comprehension Pass & Extraction

**If the manuscript is a PDF**, run extraction (auto-selects best available extractor):
```bash
<venv-python> scripts/pdf_extract.py manuscript.pdf --output-dir review_output
```
If `"llm_fallback_recommended": true`, all extractors scored poorly — read the PDF
directly using the Read tool (native LLM PDF reading) instead.
Flag images with `estimated_dpi < 150` for Figures evaluation.

Read the entire manuscript. Before writing anything, form answers to:
- What is the research question or hypothesis?
- What methods were used?
- What are the main findings?
- What do the authors claim these findings mean?

If any of these are unclear from the manuscript, that itself is a finding for the review.

**Extract the following for agents:**
- All cited references (authors, year, title if available, DOI if available)
- Key factual claims for verification (Agent 2 will autonomously select which to verify — extract all candidates)
- Journal/conference name where the paper is submitted or published
- Author names, affiliations, ORCID if provided
- All inline statistics in APA format: t(df)=X, F(df1,df2)=X, χ²(df)=X, r(df)=X, with p-values
- Reported means, SDs, and sample sizes for integer-scale data (Likert, counts)
- GitHub/repository links if present

**Detect study type** for domain-specific evaluation:
- Randomized Controlled Trial → apply CONSORT overlay
- Observational study → apply STROBE overlay
- Systematic review / meta-analysis → apply PRISMA overlay
- Machine learning / AI → apply TRIPOD+AI overlay
- Qualitative research → apply COREQ overlay
- Diagnostic accuracy study → apply STARD overlay
- Other / mixed → use general evaluation only

See [references/reporting_guidelines.md](references/reporting_guidelines.md) for domain-specific checklists.

### Step 2: Launch Verification Agents

**Before launching agents**, inform the user about expected duration and ask:
> "The paper has [X] references and [Y] claims to verify. Verification agents may run
> for several minutes (especially Agent 1 with many references). Should I monitor their
> progress and report back every 5 minutes, or just notify you when everything is done?"

Launch agents **in parallel** using the Agent tool with `run_in_background: true`.
Proceed to Steps 3–4 while agents work.

Read [references/agent_prompts.md](references/agent_prompts.md) for the full prompt
templates. Fill in the bracketed placeholders with data extracted in Step 1, then pass
each prompt to the Agent tool. The agents are:

- **Agent 1: Reference Verifier** — verifies each cited reference exists, checks for
  retractions, DOI validity, citation artifacts, and self-citation rate.
- **Agent 2: Claims Verifier** — autonomously selects ≥15 factual claims to verify
  against peer-reviewed sources. Reports SUPPORTED / WEAKLY SUPPORTED / CONTRADICTED /
  UNVERIFIABLE / OUTDATED.
- **Agent 3: Journal & Venue Checker** — checks journal legitimacy via Scimago, Beall's
  list, indexing databases, and DOAJ.
- **Agent 4: Author & Affiliation Checker** — verifies author profiles, affiliations,
  ORCID IDs, and publication history.
- **Agent 6: Code-Paper Alignment** (conditional) — launch ONLY if the manuscript
  contains a code repository link. Checks method alignment and reproducibility.

#### Statistical Integrity Checks (scripts, not agent)

Run these scripts directly instead of delegating to an agent — they are deterministic
and more accurate than LLM mental math.

**Statcheck** — extracts APA statistics, recalculates p-values, detects p-value clustering:
```bash
<venv-python> scripts/statcheck.py review_output/full_text.txt
```

**GRIM/GRIMMER** — mean/SD consistency for integer-scale data:
```bash
echo '[{"mean": 3.47, "n": 10, "decimals": 2, "sd": 1.2}]' | <venv-python> scripts/grim.py -
```

**Impossible statistics** — check manually per [references/statistical_checks.md](references/statistical_checks.md) (Test C).

Incorporate all script results into the Verification Report.

### Step 3: AI Slop & Paper Mill Scan

Run the automated phrase scanner while agents work:
```bash
<venv-python> scripts/scan_phrases.py review_output/full_text.txt
```
Detects: tortured phrases, LLM markers (3 tiers), citation artifacts, copula avoidance.
For structural signals requiring comprehension (paragraph uniformity, register shifts), evaluate per
[references/ai_slop_heuristics.md](references/ai_slop_heuristics.md).
Combine script + manual findings. Only aggregate goes into report.

### Step 4: Structured Evaluation

Evaluate each dimension below. For each, provide:
- A brief assessment (1–3 sentences)
- Specific evidence from the manuscript supporting the assessment
- Concrete suggestions for improvement (if applicable)

**Do not force criticism.** If a section is well-done, say so briefly and move on.
**Do not force praise.** If a section has serious problems, state them clearly.

#### Dimensions to evaluate:

1. **Title and Abstract** — accuracy, completeness, overclaiming
2. **Introduction and Literature Review** — research gap, motivation, hypotheses
3. **Methodology** — reproducibility, design appropriateness, sample, variables, ethics
4. **Results** — clarity, statistical appropriateness, selective reporting
5. **Discussion and Conclusions** — interpretation, limitations quality (not just presence),
   overclaiming, alternative explanations seriously engaged
6. **References and Citations** — currency, relevance, self-citation, completeness
7. **Writing Quality** — clarity, organization, flow (flag language only if it impedes comprehension)
8. **Figures and Tables** — see [references/figures_evaluation.md](references/figures_evaluation.md)
   for the full checklist. Evaluate: data integrity, visual honesty, statistical presentation,
   technical quality, and completeness.
9. **Ethics, Declarations & Open Science** — pass/fail checklist:
   - [ ] IRB/ethics approval with committee name and approval number
   - [ ] Informed consent described
   - [ ] Conflict of interest / competing interests disclosed
   - [ ] Funding sources disclosed with potential bias assessment
   - [ ] Data availability statement with repository and accession number
   - [ ] Code availability (for computational work)
   - [ ] Clinical trial registration number (for RCTs, must be pre-enrollment)
   - [ ] Author contributions (CRediT taxonomy or equivalent)
   - [ ] Animal ethics / ARRIVE compliance (if applicable)
10. **Reproducibility** — exact software versions (not just "R" but "R v4.3.1"),
    RRIDs for antibodies/cell lines/organisms, reagent catalog numbers,
    Docker/conda environment for computational work, sufficient methodological detail
    for independent replication

**Domain-specific overlay:** If a study type was detected in Step 1, apply the
corresponding reporting guideline checklist from
[references/reporting_guidelines.md](references/reporting_guidelines.md) as an additional
evaluation dimension.

For methodology specifically, flag lack of expertise to evaluate a specific method:
> "I note the authors use [method X]. I am not in a position to evaluate its appropriateness
> for this specific application — the editors may wish to seek a specialist reviewer for this aspect."

### Step 5: Collect Agent Results

Check if all verification agents have completed. If any agent is still running:

1. **If user requested monitoring:** Report progress every 5 minutes:
   > "Agent status: Reference Verifier ✅ done (12/15 refs verified), Claims Verifier ⏳ running,
   > Journal Checker ✅ done, Author Checker ✅ done, Statistical Integrity ✅ done."

2. **If an agent has been running for >10 minutes with no response:** It may be stalled.
   Inform the user and offer to proceed without that agent's results:
   > "Agent [name] has been running for [X] minutes without responding. This may indicate
   > it is stalled. I can: (a) wait longer, (b) proceed without its results and note this
   > gap in the Verification Report, or (c) relaunch with a smaller batch."

3. **For large reference lists (>30 references):** Consider splitting across multiple
   Reference Verifier agents (e.g., refs 1–15 and refs 16–30) to avoid timeout.

Aggregate all completed agent findings into the Verification Report section of the output.
If any agent failed or was skipped, note it explicitly in the report.

### Step 6: Synthesis and Integrity Risk Assessment

Combine evaluation (Step 4) with verification results (Step 5) and linguistic scan (Step 3).

#### Integrity Risk Scoring

Calculate the risk level based on all signals:

| Risk Level | Threshold | Action |
|------------|-----------|--------|
| **LOW** | 0–1 flags, all minor | Note in report, no special action |
| **MEDIUM** | 2–4 flags or 1 major flag | Dedicated warning section in report |
| **HIGH** | 5+ flags OR >30% refs not found OR >20% claims contradicted | **Flag prominently at top of report.** Recommend Reject with detailed evidence. Add escape hatch note. |

**Escape hatch for HIGH risk:** Always include this note when flagging HIGH:
> "⚠️ HIGH INTEGRITY RISK — This assessment is based on automated heuristics, statistical checks,
> and web verification. Some flags may have innocent explanations (e.g., very recent preprints not
> yet indexed, niche journals not in major databases, non-native English writing patterns resembling
> LLM output, legitimate rounding differences in statistics). The reviewer recommends manual
> verification of the flagged items before making a final decision."

Write the synthesis covering:

1. **Summary** (1 paragraph): What the paper does, its main contribution, and its overall quality.

2. **Key Strengths** (numbered list): Be specific.

3. **Major Concerns** (numbered list): Issues affecting validity, reliability, or
   interpretability. Each must: state the problem, point to the location, explain why
   it matters, suggest a path to resolution. Include verification failures and statistical
   integrity issues as major concerns when they affect the paper's credibility.

4. **Minor Concerns** (numbered list): Issues that would improve the paper but do not
   threaten its core contribution.

5. **Questions for Authors**: Specific questions where clarification would help.

6. **Overall Recommendation**: One of:
   - **Accept** — Ready for publication as-is or with trivial corrections.
   - **Minor Revision** — Sound but needs small improvements.
   - **Major Revision** — Has potential but significant issues must be addressed.
   - **Reject** — Fundamental flaws that cannot be resolved through revision.

   If Integrity Risk is HIGH, default recommendation is **Reject** unless the section-by-section
   evaluation independently found the work to be sound despite the flags.

## Output Format

See [references/output_template.md](references/output_template.md) for the full report template.

## Step 7: Prose Review (optional)

After generating the structured report, ask the user:

> "The structured report is ready. Would you also like a **prose-style review letter** —
> the kind you'd submit to a journal editor? It will be concise: brief summary of the work,
> key concerns with questions, and a recommendation. No lengthy paper description."

If the user agrees, generate a prose review following these rules:

**Structure:**
1. **Opening** (2–3 sentences) — what the paper does and its claimed contribution. No padding.
2. **Strengths** (1 short paragraph) — only the most important ones.
3. **Concerns and questions** (main body) — weave major/minor concerns and questions for
   authors into a natural narrative. Lead with the most critical issues. Each concern should
   be actionable.
4. **Recommendation** (1–2 sentences) — clear verdict with brief justification.

**Style rules:**
- Maximum ~500 words. Shorter is better.
- No section-by-section rehash — synthesize across dimensions.
- Write like an experienced reviewer: direct, professional, no filler.
- Do not repeat the paper's abstract back to the authors — they know what they wrote.

**Humanization:** Before outputting the prose review, check if the user has the `humanizer`
skill installed (search for SKILL.md in a `humanizer` skill directory). If available, invoke
it on the prose review to remove AI writing patterns and make the text sound naturally human.
If not available, manually avoid LLM-typical patterns: no "delve", "crucial", "it is worth
noting", no participle chains ("highlighting", "underscoring"), vary sentence length and
structure, use direct phrasing.

## Step 8: Self-Verification (mandatory)

This step is **non-negotiable**. Every review must be verified before presenting to the user.

After generating the structured report (and prose review if requested), launch a
self-verification agent. Read [references/self_verification.md](references/self_verification.md)
and embed the full auditor prompt into the Agent tool call, along with:
- The original manuscript text
- The complete review (structured report + prose review if generated)

The auditor checks 5 dimensions: **accuracy** (do review claims match the manuscript?),
**fairness** (are concerns proportionate and evidence-based?), **hallucination** (does the
review invent content not in the paper?), **question relevance** (are questions already
answered in the manuscript?), and **recommendation consistency** (does the verdict match
the findings?).

**After receiving the audit results:**

- **CLEAN**: present the review to the user.
- **NEEDS REVISION**: fix every flagged issue before presenting. Then re-run the audit.
  Do not present a review that failed verification.
- Questions flagged as "already answered": remove or rephrase.
- Concerns flagged as inaccurate: correct with right reference or remove entirely.

Inform the user that the review was self-verified:
> "This review has been verified against the original manuscript for accuracy, fairness,
> and hallucination. [X] corrections were made during verification."
> (or: "No corrections were needed.")

## Language

The review is always written in **English**, regardless of the language of the manuscript or
the conversation with the user.
