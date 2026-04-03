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

#### Agent 1: Reference Verifier

```
Prompt: Verify the following references from a scientific paper. For each reference:
1. Search for the paper by title, authors, and/or DOI using WebSearch
2. If DOI is provided, fetch https://doi.org/{DOI} with WebFetch to confirm it resolves
3. Check if the paper exists on Google Scholar, Semantic Scholar, or publisher sites
4. Check if the paper appears in Retraction Watch database
   (search: site:retractionwatch.com "[author name]" OR "[paper title fragment]")
5. Check DOI/ISBN format validity

For each reference, report ONE of:
- ✅ CONFIRMED — found matching paper (include actual URL)
- ❌ NOT FOUND — no evidence this paper exists (describe what was searched)
- ⚠️ MISMATCH — paper exists but title/authors/year differ (show diff)
- 🔴 RETRACTED — paper found in Retraction Watch or marked as retracted
- ⏭️ SKIPPED — insufficient information to verify (explain why)

Also report:
- Self-citation count and percentage of total references
- Reference age distribution: median year, newest, oldest
- Any DOIs/ISBNs with invalid format
- Any citation URLs containing UTM/tracking parameters
- Any citation artifacts (oaicite, turn0search0, contentReference, grok_card)

References to verify:
[paste extracted reference list here]
```

#### Agent 2: Claims Verifier

```
Prompt: You are a scientific claims verification agent. Your job is to verify factual
claims from a research paper using ONLY peer-reviewed, high-quality scholarly sources.

SOURCE QUALITY RULES:
Verify claims ONLY against high-quality, peer-reviewed scholarly sources. For each source
you cite, assess its credibility by the journal it was published in.

Preferred sources (in order of reliability):
1. Articles in journals indexed in Scopus, Web of Science, or PubMed — check the journal's
   impact factor, SJR rank, or CiteScore when possible. Higher-ranked journals = stronger evidence.
2. Systematic reviews, meta-analyses, and Cochrane reviews — strongest evidence for empirical claims.
3. Official institutional data (WHO, CDC, Eurostat, World Bank, NIST, national statistics offices,
   IEEE standards, RFC documents) — for statistics, standards, and definitions.
4. Conference proceedings from top-tier venues (NeurIPS, ICML, ACL, CHI, SIGMOD, etc. — check
   acceptance rate or known reputation).

Handling preprints (arXiv, bioRxiv, medRxiv, SSRN):
- Preprints are NOT automatically bad. Many are later published in top journals.
- ALWAYS search for a published version first. If a peer-reviewed version exists, cite that instead.
- If only the preprint exists, you MAY use it but clearly mark it: "preprint, not yet peer-reviewed".
- A claim supported ONLY by preprints is weaker — report as ⚠️ WEAKLY SUPPORTED, not ✅ SUPPORTED.

DO NOT use as verification sources:
- Blogs, news articles, opinion pieces, social media
- Wikipedia (useful for leads, but never cite it as evidence)
- Articles from journals with no indexing, no impact factor, or known predatory indicators
  (check against Beall's list patterns: no editorial board, fake metrics, pay-to-publish with
  no review, suspiciously fast acceptance)
- Self-published reports without institutional backing

If you cannot verify a claim from acceptable sources, report it as UNVERIFIABLE.

CLAIM SELECTION — from the candidate claims below, autonomously select which to verify.
Use your judgment to prioritize the most impactful claims. You MUST verify at least 15.
Priority order:
1. Quantitative claims in abstract and conclusions (these shape the paper's narrative)
2. Foundational assumptions the entire study rests on
3. Claims presented without citation (author assertions taken as fact)
4. Prevalence/incidence statistics and epidemiological numbers
5. Methodological claims ("X is the gold standard", "Y is widely used")
6. Historical facts and attributions

For each verified claim, report:
- ✅ SUPPORTED — corroborated by peer-reviewed source in indexed journal
- 🟡 WEAKLY SUPPORTED — only supported by preprints or low-impact sources
- ❌ CONTRADICTED — contradicted by peer-reviewed evidence
- ⚠️ UNVERIFIABLE — no acceptable scholarly evidence found either way
- 🔄 OUTDATED — was true but superseded by newer findings

For each result, cite: author, year, journal name, DOI/PMID, and note the journal's
quality indicator (impact factor, SJR quartile, or indexing status) when available.
Do not cite sources you have not actually found and verified via search.

Candidate claims from the paper:
[paste all extracted factual claims here — the agent will select ≥15 to verify]
```

#### Agent 3: Journal & Venue Checker

```
Prompt: Evaluate the legitimacy of this journal/conference:
Journal name: [name]
Publisher: [if known]
ISSN: [if available]

Check:
1. Search for the journal on Scimago Journal Rank (scimagojr.com)
2. Search Beall's List of predatory journals/publishers (beallslist.net)
3. Check if the journal is indexed in PubMed, Scopus, or Web of Science
4. Look for the journal on DOAJ (doaj.org) if open access
5. Check publisher reputation

Report:
- Journal found in legitimate indexes? Which ones?
- Any predatory indicators? (Beall's list, no indexing, suspicious publisher)
- Impact factor or SJR rank if available
- Overall assessment: LEGITIMATE / SUSPICIOUS / PREDATORY / UNKNOWN
```

#### Agent 4: Author & Affiliation Checker

```
Prompt: Verify these authors and their affiliations:
[paste author list with affiliations]

For each author:
1. Search for their profile on Google Scholar, ORCID, or institutional pages
2. Verify the stated affiliation matches their known affiliation
3. Check if they have prior publications in this field
4. Verify ORCID ID if provided (fetch https://orcid.org/[ID])
5. Note their h-index or publication count if available

Report:
- Author found with matching affiliation? Yes/No/Partial match
- Prior publications in this field? Estimated count
- ORCID verified? (if provided)
- Any red flags? (no online presence, affiliation mismatch, paper mill indicators)
```

#### Agent 5: Statistical Integrity Checker

```
Prompt: Check the statistical integrity of the following reported statistics from a
scientific paper. See the detailed guide below for each test.

PART A — Statcheck (p-value recalculation):
For each statistic reported in APA format, recalculate the p-value and compare:
[paste extracted statistics: e.g., "t(34) = 2.10, p = .02"]

PART B — GRIM Test (mean consistency):
For each reported mean of integer-scale data, check if it's mathematically possible:
[paste: mean, sample size, number of decimal places, scale type]

PART C — Impossible statistics scan:
Check for: percentages not summing to 100, CI not containing point estimate,
df inconsistent with sample size, correlations outside [-1, 1], negative F or χ²,
sample sizes changing between analyses without explanation.

PART D — P-value clustering:
Count all reported p-values. Report how many fall in each range:
.001-.01, .01-.03, .03-.04, .04-.049, .05-.10, >.10
Flag if suspicious clustering just below .05.

Report findings per test with PASS / FLAG / FAIL for each.
```

**Before launching Agent 5:** Read [references/statistical_checks.md](references/statistical_checks.md)
and embed the test methodology (formulas, examples, thresholds) directly into the agent prompt.
The subagent has no filesystem access — all instructions must be in the prompt itself.

#### Agent 6: Code-Paper Alignment (conditional)

Launch ONLY if the manuscript contains a link to a code repository (GitHub, GitLab, etc.).

```
Prompt: Check alignment between this paper and its code repository.
Paper claims: [paste methodology summary — algorithms, architectures, parameters]
Repository URL: [URL]

Check:
1. Does the repository exist and is it accessible?
2. Does the README describe the same method as the paper?
3. Do file/directory names suggest the described architecture/method is implemented?
4. Are key hyperparameters mentioned in the paper findable in config files or code?
5. Is there a requirements.txt/environment.yml specifying dependencies and versions?
6. Does the repo have a license?
7. When was the last commit? (abandoned repo?)

Report:
- Repository accessible? Yes/No
- Method alignment: CONSISTENT / PARTIAL / INCONSISTENT / CANNOT DETERMINE
- Specific discrepancies found (if any)
- Reproducibility readiness: HIGH / MEDIUM / LOW
```

### Step 3: AI Slop & Paper Mill Scan

While agents work, scan the manuscript for AI-generated content and paper mill indicators.
See [references/ai_slop_heuristics.md](references/ai_slop_heuristics.md) for the full detection guide
and [references/tortured_phrases.md](references/tortured_phrases.md) for paper mill phrase detection.

Perform the scan silently. Do not report individual heuristic matches — only the
aggregate assessment goes into the Verification Report.

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
